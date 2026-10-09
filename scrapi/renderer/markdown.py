from __future__ import annotations

from functools import singledispatchmethod
from pathlib import Path
from typing import TYPE_CHECKING

from scrapi.exceptions import RendererError
from scrapi.renderer.base import BaseRenderer
from scrapi.models.inference_result import SummaryInferenceResult
from scrapi.models.run_result import RunResult

if TYPE_CHECKING:
    from scrapi.models.inference_result import BaseInferenceResult


class MarkdownRenderer(BaseRenderer):
    """Renders a ``RunResult`` as a Markdown report."""

    def __init__(self, output_path: str | None = None) -> None:
        super().__init__(output_path=output_path)

    @singledispatchmethod
    @staticmethod
    def to_markdown(result: BaseInferenceResult) -> str:
        """Convert an inference result or pipeline result to a Markdown string.

        Dispatches on the concrete type of ``result``; handles
        ``BaseInferenceResult``, ``SummaryInferenceResult``, and
        ``RunResult``.

        Args:
            result: The object to render.

        Returns:
            Markdown-formatted string.
        """
        return result.result

    @to_markdown.register
    @staticmethod
    def _(result: SummaryInferenceResult) -> str:
        return (
            f"{result.structured_output.result}\n\n"
            f"**Key passages:**\n\n{result.structured_output.paragraphs}"
        )

    @to_markdown.register
    @staticmethod
    def _(result: RunResult) -> str:
        if len(result) == 0:
            return "_No results._"
        rows = ["| # | ID | Scraper | Status | Fetched at | Source |", "|---|---|---|---|---|---|"]
        for i, pair in enumerate(result, start=1):
            sr = pair.search
            source = ", ".join(f"{k}: {v}" for k, v in sr.source.items())
            status = str(sr.status.status)
            if sr.status.message:
                status += f" {sr.status.message}"
            fetched_at = sr.fetched_at.strftime("%Y-%m-%d %H:%M:%S")
            rows.append(f"| {i} | {sr.id} | {sr.scraper_repr} | {status} | {fetched_at} | {source} |")
        return "\n".join(rows)

    def render(self, run_result: RunResult) -> str:
        """Render ``run_result`` as a Markdown report.

        Args:
            run_result: The completed pipeline result to render.

        Returns:
            Markdown string containing the full report.
        """
        sections = [
            "# Scrapi report",
            "## Search results",
            self.to_markdown(run_result),
            "## Summary",
            self.to_markdown(run_result.summary),
        ]
        self._document = "\n\n".join(sections).rstrip() + "\n"
        return self._document

    def save(self) -> None:
        """Write the rendered report to ``output_path``.

        Raises:
            RendererError: If ``render()`` has not been called yet.
        """
        if self._document is None:
            raise RendererError("call render() before save()")
        Path(self.output_path).write_text(self._document)
