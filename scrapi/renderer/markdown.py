from __future__ import annotations

from functools import singledispatch
from pathlib import Path
from typing import TYPE_CHECKING

from scrapi.renderer.base import BaseRenderer
from scrapi.models.search_result import BaseSearchResult, WebSearchResult
from scrapi.models.inference_result import (
    BaseInferenceResult,
    SearchInferenceResult,
    SummaryInferenceResult,
)

if TYPE_CHECKING:
    from scrapi.models.pipeline_result import PipelineResult


@singledispatch
def format_search_result(result: BaseSearchResult) -> str:
    return result.ai_content


@format_search_result.register
def _(result: WebSearchResult) -> str:
    url = result.source.get("url", "")
    return f"**Source:** {url}\n\n{result.ai_content}"


@singledispatch
def format_inference_result(result: BaseInferenceResult) -> str:
    return result.result


@format_inference_result.register
def _(result: SearchInferenceResult) -> str:
    return f"**Summary:** {result.structured_output.summary}\n\n**Result:** {result.structured_output.result}"


@format_inference_result.register
def _(result: SummaryInferenceResult) -> str:
    return (
        f"{result.structured_output.result}\n\n"
        f"**Key passages:**\n\n{result.structured_output.paragraphs}"
    )


class MarkdownRenderer(BaseRenderer):

    def __init__(self, pipeline_result: PipelineResult) -> None:
        super().__init__(pipeline_result)

    def render(self) -> str:
        sections = [
            "# Report",
            "## Summary",
            self.render_inference_result(self._pipeline_result.summary),
            "## Results",
        ]

        if len(self._pipeline_result) == 0:
            sections.append("_No results._")
        else:
            for i, pair in enumerate(self._pipeline_result, start=1):
                sections.append(f"### Result {i}")
                sections.append("#### Search result")
                sections.append(self.render_search_result(pair.search))
                sections.append("#### Inference result")
                sections.append(self.render_inference_result(pair.inference))

        self._document = "\n".join(sections).rstrip() + "\n"
        return self._document

    def render_search_result(self, result: BaseSearchResult) -> str:
        return format_search_result(result)

    def render_inference_result(self, result: BaseInferenceResult) -> str:
        return format_inference_result(result)

    def save(self, path: str) -> None:
        if self._document is None:
            self.render()
        Path(path).write_text(self._document)
