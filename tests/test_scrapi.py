"""Test suite for the scrapi package — focused on high-level pipeline functionality."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scrapi.config.loader import parse_config, load_toml_config
from scrapi.config.schemas import ScrapiConfig
from scrapi.exceptions import ConfigLoadError, InvalidConfigError
from scrapi.factory import make_orchestrator
from scrapi.inference.schemas import SearchSchema, SummarySchema
from scrapi.models.inference_result import SearchInferenceResult, SummaryInferenceResult
from scrapi.models.pipeline_result import PipelineResult
from scrapi.orchestrator import Orchestrator
from scrapi.renderer.markdown import MarkdownRenderer
from scrapi.scraping.dummy import DummyScraper


_BASE_CONFIG = {
    "llm": {"provider": "ollama", "config": {}},
    "inference": {
        "search": {"system_prompt": "sys", "task_prompt": "task"},
        "summary": {"system_prompt": "sys", "task_prompt": "sum"},
    },
    "scrapers": [
        {"provider": "dummy", "config": {}, "fetch": {"query": "q", "n": 2}},
    ],
}

_VALID_TOML = """\
[llm]
provider = "ollama"

[llm.config]

[inference.search]
system_prompt = "sys"
task_prompt = "task"

[inference.summary]
system_prompt = "sys"
task_prompt = "sum"

[[scrapers]]
provider = "dummy"
[scrapers.fetch]
query = "q"
n = 2
"""


# ---------------------------------------------------------------------------
# Config parsing
# ---------------------------------------------------------------------------

def test_parse_config_valid():
    config = parse_config(_BASE_CONFIG)
    assert isinstance(config, ScrapiConfig)
    assert config.llm.provider == "ollama"
    assert config.inference.search.system_prompt == "sys"
    assert config.inference.summary.task_prompt == "sum"
    assert config.scrapers[0].provider == "dummy"
    assert config.scrapers[0].fetch["n"] == 2


# ---------------------------------------------------------------------------
# TOML file loading
# ---------------------------------------------------------------------------

def test_load_toml_config_from_file():
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
        f.write(_VALID_TOML.encode())
        tmp_path = Path(f.name)

    try:
        config = load_toml_config(tmp_path)
        assert isinstance(config, ScrapiConfig)
        assert config.llm.provider == "ollama"
        assert config.scrapers[0].provider == "dummy"
        assert config.scrapers[0].fetch["n"] == 2
    finally:
        tmp_path.unlink(missing_ok=True)


def test_load_toml_config_invalid_toml():
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
        f.write(b"[invalid toml\nkey = ")
        tmp_path = Path(f.name)

    try:
        with pytest.raises(ConfigLoadError):
            load_toml_config(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def test_make_orchestrator_returns_orchestrator():
    config = parse_config(_BASE_CONFIG)

    mock_llm = MagicMock()
    mock_llm.llm = MagicMock()

    with (
        __import__("unittest.mock", fromlist=["patch"]).patch(
            "scrapi.config.registry.LLM_REGISTRY", {"ollama": lambda **kw: mock_llm}
        ),
        __import__("unittest.mock", fromlist=["patch"]).patch(
            "scrapi.config.registry.SCRAPER_REGISTRY", {"dummy": lambda **kw: DummyScraper()}
        ),
    ):
        orchestrator = make_orchestrator(config)

    assert isinstance(orchestrator, Orchestrator)


def test_make_orchestrator_unknown_scraper():
    config = parse_config({
        **_BASE_CONFIG,
        "scrapers": [{"provider": "unknown_scraper", "config": {}, "fetch": {}}],
    })

    with pytest.raises((InvalidConfigError, KeyError)):
        make_orchestrator(config)


# ---------------------------------------------------------------------------
# Full pipeline: DummyScraper → Orchestrator → MarkdownRenderer
# ---------------------------------------------------------------------------

def _make_fake_search_inference() -> SearchInferenceResult:
    return SearchInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="task",
        structured_output=SearchSchema(summary="short summary", result="finding"),
        result="finding",
    )


def _make_fake_summary_inference() -> SummaryInferenceResult:
    return SummaryInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="sum",
        structured_output=SummarySchema(
            summary="overall summary",
            paragraphs="key paragraphs here",
            result="Final verdict",
        ),
        result="Final verdict",
    )


def test_pipeline_with_dummy_scraper():
    n = 3
    scraper = DummyScraper()

    mock_search_inference = MagicMock()
    mock_search_inference.analyse.side_effect = lambda _: _make_fake_search_inference()

    mock_summary_inference = MagicMock()
    mock_summary_inference.analyse.return_value = _make_fake_summary_inference()

    orchestrator = Orchestrator(
        scrapers=[(scraper, {"query": "test query", "n": n})],
        search_inference=mock_search_inference,
        summary_inference=mock_summary_inference,
    )

    assert orchestrator.result is None

    report = orchestrator.run()

    assert isinstance(report, PipelineResult)
    assert len(report) == n
    assert all(pair.search.ai_content.startswith("Dummy article") for pair in report.results)
    assert mock_search_inference.analyse.call_count == n
    mock_summary_inference.analyse.assert_called_once()
    assert orchestrator.result == "Final verdict"

    output = MarkdownRenderer(pipeline_result=report).render()
    assert isinstance(output, str)
    assert "# Scrapi report" in output
    assert "## Search results" in output
    assert "dummy.example.com" in output
    assert "## Summary" in output
    assert "Final verdict" in output
