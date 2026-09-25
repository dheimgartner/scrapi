from pathlib import Path

from conflict_checker.renderer.base_renderer import (
    BaseRenderer,
    Report
)
from conflict_checker.interface.search_result.base_search_result import BaseSearchResult
from conflict_checker.interface.inference_result.base_inference_result import BaseInferenceResult

class MarkdownRenderer(BaseRenderer):

    def __init__(self, report: Report) -> None:
        super().__init__(report)

    def render(self) -> str:
        sections = [
            "# Conflict check report",
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

        return "\n".join(sections).rstrip() + "\n"

    def render_search_result(self, result: BaseSearchResult) -> str:
        return result.ai_content

    def render_inference_result(self, result: BaseInferenceResult) -> str:
        return result.result

    def save(self, path: str) -> None:
        """Render (if not already done) and write the result to disk."""
        if self._document is None:
            self.render()
        Path(path).write_text(self._document)