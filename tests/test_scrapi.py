"""Minimal test suite for the scrapi package."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scrapi.config.loader import parse_config, load_yaml_config
from scrapi.config.schemas import ConflictCheckConfig
from scrapi.config.defaults import DEFAULT_CONFIG
from scrapi.exceptions import ConfigLoadError, InvalidConfigError
from scrapi.factory import make_conflict_checker
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
from scrapi.models.report import Report, ResultPair
from scrapi.renderer.markdown import MarkdownRenderer
from scrapi.orchestrator import Orchestrator


# ---------------------------------------------------------------------------
# 1. parse_config with valid dict
# ---------------------------------------------------------------------------

def test_parse_config_valid():
    source = {
        "scraper": {"provider": "yahoo", "config": {}},
        "inference": {"provider": "openai", "config": {}},
        "orchestrator": {"config": {"system_prompt": "sys", "task_prompt": "task",
                                    "summary_prompt": "sum", "query": "q", "n": 2}},
    }
    config = parse_config(source)
    assert isinstance(config, ConflictCheckConfig)
    assert config.scraper.provider == "yahoo"
    assert config.inference.provider == "openai"
    assert config.orchestrator.config["n"] == 2


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
# 3. make_conflict_checker returns Orchestrator for valid config
# ---------------------------------------------------------------------------

def test_make_conflict_checker_returns_orchestrator():
    config = parse_config({
        "scraper": {"provider": "yahoo", "config": {}},
        "inference": {"provider": "openai", "config": {}},
        "orchestrator": {
            "config": {
                "system_prompt": "sys",
                "task_prompt": "task",
                "summary_prompt": "sum",
                "query": "q",
                "n": 1,
                "save": False,
            }
        },
    })

    mock_llm_instance = MagicMock()
    mock_llm_instance.llm = MagicMock()
    mock_scraper_instance = MagicMock()

    with patch("scrapi.config.registry.LLM_REGISTRY", {"openai": lambda **kw: mock_llm_instance}), \
         patch("scrapi.config.registry.SCRAPER_REGISTRY", {"yahoo": lambda **kw: mock_scraper_instance}):
        orchestrator = make_conflict_checker(config)

    assert isinstance(orchestrator, Orchestrator)


# ---------------------------------------------------------------------------
# 4. make_conflict_checker raises InvalidConfigError for unknown provider
# ---------------------------------------------------------------------------

def test_make_conflict_checker_unknown_scraper():
    config = parse_config({
        "scraper": {"provider": "unknown_scraper", "config": {}},
        "inference": {"provider": "openai", "config": {}},
        "orchestrator": {
            "config": {
                "system_prompt": "sys",
                "task_prompt": "task",
                "summary_prompt": "sum",
                "query": "q",
                "n": 1,
            }
        },
    })

    with pytest.raises((InvalidConfigError, KeyError)):
        make_conflict_checker(config)


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
# 7. Orchestrator.conflict_check with mocked scraper and LLM
# ---------------------------------------------------------------------------

def test_orchestrator_conflict_check():
    status = SuccessfulSearch(status=200)
    fake_search_result = WebSearchResult(
        scraper_repr="MockScraper",
        status=status,
        fetched_at=datetime(2025, 1, 1),
        source={"url": "https://example.com"},
        raw_content="<html/>",
        ai_content="Article content",
    )

    fake_search_schema = SearchSchema(summary="short summary", result="conflict found")
    fake_search_inference = SearchInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="task",
        structured_output=fake_search_schema,
        result="conflict found",
    )

    fake_summary_schema = SummarySchema(
        summary="overall summary",
        paragraphs="key paragraphs here",
        result="Final verdict: no conflict",
    )
    fake_summary_inference = SummaryInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="sum",
        structured_output=fake_summary_schema,
        result="Final verdict: no conflict",
    )

    mock_scraper = MagicMock()
    mock_scraper.fetch_content.return_value = [fake_search_result]

    mock_llm = MagicMock()
    mock_llm.llm = MagicMock()

    with patch("scrapi.orchestrator.SearchInference") as MockSearchInf, \
         patch("scrapi.orchestrator.SummaryInference") as MockSummaryInf:

        mock_search_inf_instance = MagicMock()
        mock_search_inf_instance.analyse.return_value = fake_search_inference
        MockSearchInf.return_value = mock_search_inf_instance

        mock_summary_inf_instance = MagicMock()
        mock_summary_inf_instance.analyse.return_value = fake_summary_inference
        MockSummaryInf.return_value = mock_summary_inf_instance

        orchestrator = Orchestrator(
            system_prompt="sys",
            task_prompt="task",
            summary_prompt="sum",
            query="test query",
            n=1,
            llm=mock_llm,
            scraper=mock_scraper,
            save=False,
        )
        report = orchestrator.conflict_check()

    assert isinstance(report, Report)
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

    search_schema = SearchSchema(summary="short summary", result="conflict found")
    inference_result = SearchInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="task",
        structured_output=search_schema,
        result="conflict found",
    )

    summary_schema = SummarySchema(
        summary="overall summary",
        paragraphs="key paragraphs here",
        result="Final verdict: no conflict",
    )
    summary_result = SummaryInferenceResult(
        prompted_at=datetime(2025, 1, 1),
        system_prompt="sys",
        task_prompt="sum",
        structured_output=summary_schema,
        result="Final verdict: no conflict",
    )

    pair = ResultPair(search=search_result, inference=inference_result)
    report = Report(results=[pair], summary=summary_result)

    renderer = MarkdownRenderer(report)
    output = renderer.render()

    assert isinstance(output, str)
    assert "# Conflict check report" in output
    assert "## Summary" in output
    assert "## Results" in output
    assert "### Result 1" in output
    assert "#### Search result" in output
    assert "#### Inference result" in output
    assert "Final verdict: no conflict" in output
