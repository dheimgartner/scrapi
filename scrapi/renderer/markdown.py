from __future__ import annotations

import re
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

    def __init__(
        self,
        report_path: str | None = None,
        result_md_path: str | None = None,
    ) -> None:
        super().__init__(report_path=report_path, result_md_path=result_md_path)

    @singledispatchmethod
    @staticmethod
    def to_markdown(result: BaseInferenceResult) -> str:
        """Convert an inference result or run result to a Markdown string.

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
        sections = []
        for i, pair in enumerate(result, start=1):
            sr = pair.search
            status = str(sr.status.status)
            if sr.status.message:
                status += f" {sr.status.message}"
            fields = {
                "ID": sr.id,
                "Status": status,
                "Fetched at": sr.fetched_at.strftime("%Y-%m-%d %H:%M:%S"),
                **sr.source,
            }
            lines = [f"### {i}. {sr.scraper_repr}", ""]
            lines += [MarkdownRenderer._field(k, v) for k, v in fields.items()]
            sections.append("\n".join(lines).rstrip())
        return "\n\n".join(sections)

    @staticmethod
    def _field(key: str, value: object) -> str:
        """Format ``key``/``value`` as a Markdown list item.

        Single-line values are rendered inline; multi-line values are placed
        in a fenced code block nested under the item so their formatting is
        preserved.
        """
        value = str(value).strip("\n")
        if "\n" not in value:
            return f"- **{key}:** {value}"
        longest_run = max((len(run) for run in re.findall(r"`+", value)), default=0)
        fence = "`" * max(3, longest_run + 1)
        body = "\n".join(f"  {line}" if line else "" for line in value.split("\n"))
        return f"- **{key}:**\n\n  {fence}\n{body}\n  {fence}\n"

    def render(self, run_result: RunResult) -> str:
        """Render ``run_result`` as a Markdown report.

        Args:
            run_result: The completed run result to render.

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
        """Write the rendered report to ``report_path``.

        Raises:
            RendererError: If ``render()`` has not been called yet.
        """
        if self._document is None:
            raise RendererError("call render() before save()")
        Path(self.report_path).write_text(self._document)
