from __future__ import annotations

from functools import singledispatchmethod
from pathlib import Path
from typing import TYPE_CHECKING

from scrapi.renderer.base import BaseRenderer
from scrapi.models.inference_result import SummaryInferenceResult
from scrapi.models.pipeline_result import PipelineResult

if TYPE_CHECKING:
    from scrapi.models.inference_result import BaseInferenceResult


class MarkdownRenderer(BaseRenderer):

    def __init__(self, pipeline_result: PipelineResult) -> None:
        super().__init__(pipeline_result)

    @singledispatchmethod
    @staticmethod
    def to_markdown(result: BaseInferenceResult) -> str:
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
    def _(result: PipelineResult) -> str:
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

    def render(self) -> str:
        sections = [
            "# Scrapi report",
            "## Search results",
            self.to_markdown(self._pipeline_result),
            "## Summary",
            self.to_markdown(self._pipeline_result.summary),
        ]
        self._document = "\n\n".join(sections).rstrip() + "\n"
        return self._document

    def save(self, path: str) -> None:
        if self._document is None:
            self.render()
        Path(path).write_text(self._document)
