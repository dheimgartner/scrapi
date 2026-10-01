from __future__ import annotations

from functools import singledispatchmethod
from pathlib import Path
from typing import TYPE_CHECKING

from scrapi.renderer.base import BaseRenderer
from scrapi.models.inference_result import SummaryInferenceResult

if TYPE_CHECKING:
    from scrapi.models.pipeline_result import PipelineResult
    from scrapi.models.inference_result import BaseInferenceResult


class MarkdownRenderer(BaseRenderer):

    def __init__(self, pipeline_result: PipelineResult) -> None:
        super().__init__(pipeline_result)

    @singledispatchmethod
    @staticmethod
    def format_result(result: BaseInferenceResult) -> str:
        return result.result

    @format_result.register
    @staticmethod
    def _(result: SummaryInferenceResult) -> str:
        return (
            f"{result.structured_output.result}\n\n"
            f"**Key passages:**\n\n{result.structured_output.paragraphs}"
        )

    def render(self) -> str:
        sections = ["# Scrapi report", "## Search results"]

        if len(self._pipeline_result) == 0:
            sections.append("_No results._")
        else:
            rows = ["| # | ID | Source |", "|---|---|---|"]
            for i, pair in enumerate(self._pipeline_result, start=1):
                result = pair.search
                source = ", ".join(f"{k}: {v}" for k, v in result.source.items())
                rows.append(f"| {i} | {result.id} | {source} |")
            sections.append("\n".join(rows))

        sections += ["## Summary", self.format_result(self._pipeline_result.summary)]

        self._document = "\n\n".join(sections).rstrip() + "\n"
        return self._document

    def save(self, path: str) -> None:
        if self._document is None:
            self.render()
        Path(path).write_text(self._document)
