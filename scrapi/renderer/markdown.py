from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from scrapi.renderer.base import BaseRenderer

if TYPE_CHECKING:
    from scrapi.models.report import PipelineResult
    from scrapi.models.search_result import BaseSearchResult
    from scrapi.models.inference_result import BaseInferenceResult


class MarkdownRenderable:
    def render_as_markdown(self) -> str:
        raise NotImplementedError


class SearchResultMarkdownMixin(MarkdownRenderable):
    def render_as_markdown(self) -> str:
        return self.ai_content


class WebSearchResultMarkdownMixin(SearchResultMarkdownMixin):
    def render_as_markdown(self) -> str:
        url = self.source.get("url", "")
        return f"**Source:** {url}\n\n{self.ai_content}"


class InferenceResultMarkdownMixin(MarkdownRenderable):
    def render_as_markdown(self) -> str:
        return self.result


class SearchInferenceResultMarkdownMixin(InferenceResultMarkdownMixin):
    def render_as_markdown(self) -> str:
        return f"**Summary:** {self.structured_output.summary}\n\n**Result:** {self.structured_output.result}"


class SummaryInferenceResultMarkdownMixin(InferenceResultMarkdownMixin):
    def render_as_markdown(self) -> str:
        return (
            f"{self.structured_output.result}\n\n"
            f"**Key passages:**\n\n{self.structured_output.paragraphs}"
        )


class MarkdownRenderer(BaseRenderer):

    def __init__(self, report: PipelineResult) -> None:
        super().__init__(report)

    def render(self) -> str:
        sections = [
            "# Report",
            "## Summary",
            self.render_inference_result(self._report.summary),
            "## Results"
        ]

        if len(self._report) == 0:
            sections.append("_No results._")
        else:
            for i, pair in enumerate(self._report, start=1):
                sections.append(f"### Result {i}")
                sections.append("#### Search result")
                sections.append(self.render_search_result(pair.search))
                sections.append("#### Inference result")
                sections.append(self.render_inference_result(pair.inference))

        self._document = "\n".join(sections).rstrip() + "\n"
        return self._document

    def render_search_result(self, result: BaseSearchResult) -> str:
        return result.render_as_markdown()

    def render_inference_result(self, result: BaseInferenceResult) -> str:
        return result.render_as_markdown()

    def save(self, path: str) -> None:
        """Render (if not already done) and write the result to disk."""
        if self._document is None:
            self.render()
        Path(path).write_text(self._document)
