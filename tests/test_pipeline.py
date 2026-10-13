"""End-to-end pipeline tests: DummyScraper → Orchestrator → MarkdownRenderer."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from scrapi.inference.schemas import SearchSchema, SummarySchema
from scrapi.models.inference_result import SearchInferenceResult, SummaryInferenceResult
from scrapi.models.run_result import RunResult
from scrapi.orchestrator import Orchestrator
from scrapi.renderer.markdown import MarkdownRenderer
from scrapi.scraping.dummy import DummyScraper


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

    run_result = orchestrator.run()

    assert isinstance(run_result, RunResult)
    assert len(run_result) == n
    assert all(pair.search.ai_content.startswith("Dummy article") for pair in run_result.results)
    assert mock_search_inference.analyse.call_count == n
    mock_summary_inference.analyse.assert_called_once()
    assert orchestrator.result == "Final verdict"

    renderer = MarkdownRenderer()
    output = renderer.render(run_result)
    assert isinstance(output, str)
    assert "# Scrapi report" in output
    assert "## Search results" in output
    assert "dummy.example.com" in output
    assert "## Summary" in output
    assert "Final verdict" in output


def test_orchestrator_auto_saves_with_renderer():
    scraper = DummyScraper()

    mock_search_inference = MagicMock()
    mock_search_inference.analyse.side_effect = lambda _: _make_fake_search_inference()

    mock_summary_inference = MagicMock()
    mock_summary_inference.analyse.return_value = _make_fake_summary_inference()

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        output_path = f.name

    try:
        renderer = MarkdownRenderer(output_path=output_path)
        orchestrator = Orchestrator(
            scrapers=[(scraper, {"query": "test", "n": 1})],
            search_inference=mock_search_inference,
            summary_inference=mock_summary_inference,
            renderer=renderer,
        )
        orchestrator.run()

        saved = Path(output_path).read_text()
        assert "# Scrapi report" in saved
        assert "Final verdict" in saved
    finally:
        Path(output_path).unlink(missing_ok=True)
