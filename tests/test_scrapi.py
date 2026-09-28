"""Minimal test suite for the scrapi package."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scrapi.config.loader import parse_config, load_yaml_config
from scrapi.config.schemas import ScrapiConfig
from scrapi.config.defaults import DEFAULT_CONFIG
from scrapi.exceptions import ConfigLoadError, InvalidConfigError
from scrapi.factory import make_orchestrator
from scrapi.models.search_result import (
    SearchStatus,
    SuccessfulSearch,
    FailedSearch,
    WebSearchResult,
)
from scrapi.models.inference_result import (
    SearchInferenceResult,
    SummaryInferenceResult,
)
from scrapi.inference.schemas import SearchSchema, SummarySchema
from scrapi.models.pipeline_result import PipelineResult, ResultPair
from scrapi.renderer.markdown import MarkdownRenderer
from scrapi.orchestrator import Orchestrator


_BASE_CONFIG = {
    "llm": {"provider": "ollama", "config": {}},
    "inference": {
        "search": {
            "system_prompt": "sys",
            "task_prompt": "task",
        },
        "summary": {
            "system_prompt": "sys",
            "task_prompt": "sum",
        },
    },
    "scrapers": [
        {"provider": "yahoo", "config": {}, "fetch": {"query": "q", "n": 2}},
    ],
}


# ---------------------------------------------------------------------------
# 1. parse_config with valid dict
# ---------------------------------------------------------------------------

def test_parse_config_valid():
    config = parse_config(_BASE_CONFIG)
    assert isinstance(config, ScrapiConfig)
    assert config.llm.provider == "ollama"
    assert config.inference.search.system_prompt == "sys"
    assert config.inference.summary.task_prompt == "sum"
    assert config.scrapers[0].provider == "yahoo"
    assert config.scrapers[0].fetch["n"] == 2


# ---------------------------------------------------------------------------
# 2. load_yaml_config raises ConfigLoadError for invalid YAML file
# ---------------------------------------------------------------------------

def test_load_yaml_config_invalid_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(": invalid: yaml: [unclosed")
        tmp_path = Path(f.name)

    with pytest.raises(ConfigLoadError):
        load_yaml_config(tmp_path)

    tmp_path.unlink(missing_ok=True)


def test_load_yaml_config_non_mapping():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("- just\n- a\n- list\n")
        tmp_path = Path(f.name)

    with pytest.raises(ConfigLoadError):
        load_yaml_config(tmp_path)

    tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# 3. make_orchestrator returns Orchestrator for valid config
# ---------------------------------------------------------------------------

def test_make_orchestrator_returns_orchestrator():
    config = parse_config(_BASE_CONFIG)

    mock_llm_instance = MagicMock()
    mock_llm_instance.llm = MagicMock()
    mock_scraper_instance = MagicMock()

    with patch("scrapi.config.registry.LLM_REGISTRY", {"ollama": lambda **kw: mock_llm_instance}), \
         patch("scrapi.config.registry.SCRAPER_REGISTRY", {"yahoo": lambda **kw: mock_scraper_instance}):
        orchestrator = make_orchestrator(config)

    assert isinstance(orchestrator, Orchestrator)


# ---------------------------------------------------------------------------
# 4. make_orchestrator raises InvalidConfigError for unknown provider
# ---------------------------------------------------------------------------

def test_make_orchestrator_unknown_scraper():
    config = parse_config({
        **_BASE_CONFIG,
        "scrapers": [{"provider": "unknown_scraper", "config": {}, "fetch": {}}],
    })

    with pytest.raises((InvalidConfigError, KeyError)):
        make_orchestrator(config)


# ---------------------------------------------------------------------------
# 5. WebSearchResult construction and render_as_markdown
# ---------------------------------------------------------------------------

def test_web_search_result_render_as_markdown():
    status = SuccessfulSearch(status=200)
    result = WebSearchResult(
        scraper_repr="YahooScraper",
        status=status,
        fetched_at=datetime(2025, 1, 1),
        source={"url": "https://example.com"},
        raw_content="<html>raw</html>",
        ai_content="Some article content",
    )
    md = result.render_as_markdown()
    assert md
    assert "https://example.com" in md
    assert "Some article content" in md


# ---------------------------------------------------------------------------
# 6. SearchStatus, SuccessfulSearch, FailedSearch
# ---------------------------------------------------------------------------

def test_search_status_classes():
    success = SuccessfulSearch(status=200)
    assert success.status == 200
    assert isinstance(success, SearchStatus)

    failed = FailedSearch(status=404, message="Not found")
    assert failed.status == 404
    assert failed.message == "Not found"
    assert isinstance(failed, SearchStatus)

    error = ValueError("oops")
    failed_with_error = FailedSearch(status=500, error=error)
    assert failed_with_error.error is error


# ---------------------------------------------------------------------------
# 7. Orchestrator.run with mocked scraper and inference objects
# ---------------------------------------------------------------------------

def test_orchestrator_run():
    status = SuccessfulSearch(status=200)
    fake_search_result = WebSearchResult(
        scraper_repr="MockScraper",
        status=status,
        fetched_at=datetime(2025, 1, 1),
        source={"url": "https://example.com"},
        raw_content="<html/>",
        ai_content="Article content",
    )

    fake_search_schema = SearchSchema(summary="short summary", result="finding")
    fake_search_inference = SearchInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="task",
        structured_output=fake_search_schema,
        result="finding",
    )

    fake_summary_schema = SummarySchema(
        summary="overall summary",
        paragraphs="key paragraphs here",
        result="Final verdict",
    )
    fake_summary_inference = SummaryInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="sum",
        structured_output=fake_summary_schema,
        result="Final verdict",
    )

    mock_scraper = MagicMock()
    mock_scraper.fetch_content.return_value = [fake_search_result]

    mock_search_inference = MagicMock()
    mock_search_inference.analyse.return_value = fake_search_inference

    mock_summary_inference = MagicMock()
    mock_summary_inference.analyse.return_value = fake_summary_inference

    orchestrator = Orchestrator(
        scrapers=[(mock_scraper, {"query": "test query", "n": 1})],
        search_inference=mock_search_inference,
        summary_inference=mock_summary_inference,
    )
    report = orchestrator.run()

    mock_scraper.fetch_content.assert_called_once_with(query="test query", n=1)
    assert isinstance(report, PipelineResult)
    assert len(report) == 1
    assert report.results[0].search is fake_search_result
    assert report.results[0].inference is fake_search_inference
    assert report.summary is fake_summary_inference


# ---------------------------------------------------------------------------
# 8. MarkdownRenderer produces string with expected section headers
# ---------------------------------------------------------------------------

def test_markdown_renderer():
    status = SuccessfulSearch(status=200)
    search_result = WebSearchResult(
        scraper_repr="MockScraper",
        status=status,
        fetched_at=datetime(2025, 1, 1),
        source={"url": "https://example.com"},
        raw_content="<html/>",
        ai_content="Article content",
    )

    search_schema = SearchSchema(summary="short summary", result="finding")
    inference_result = SearchInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="task",
        structured_output=search_schema,
        result="finding",
    )

    summary_schema = SummarySchema(
        summary="overall summary",
        paragraphs="key paragraphs here",
        result="Final verdict",
    )
    summary_result = SummaryInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="sum",
        structured_output=summary_schema,
        result="Final verdict",
    )

    pair = ResultPair(search=search_result, inference=inference_result)
    report = PipelineResult(results=[pair], summary=summary_result)

    renderer = MarkdownRenderer(pipeline_result=report)
    output = renderer.render()

    assert isinstance(output, str)
    assert "# Report" in output
    assert "## Summary" in output
    assert "## Results" in output
    assert "### Result 1" in output
    assert "#### Search result" in output
    assert "#### Inference result" in output
    assert "Final verdict" in output
