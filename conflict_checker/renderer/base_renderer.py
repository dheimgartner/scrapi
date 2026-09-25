from abc import ABC, abstractmethod

from conflict_checker.renderer.report import Report
from conflict_checker.interface.search_result.base_search_result import BaseSearchResult
from conflict_checker.interface.inference_result.base_inference_result import BaseInferenceResult


class BaseRenderer(ABC):

    def __init__(self, report: Report) -> None:
        self._report = report
        self._document: str | None = None

    @abstractmethod
    def render(self) -> str:
        """Renders the report and returns it as a string.

        Implementations should walk `self._report`, call
        `render_search_result()` and `render_inference_result()`,
        assemble the final document, and return it.
        """

    @abstractmethod
    def render_search_result(self, result: BaseSearchResult) -> str:
        """Format a single search result in this renderer's output format."""

    @abstractmethod
    def render_inference_result(self, result: BaseInferenceResult) -> str:
        """Format a single inference result in this renderer's output format."""

    @abstractmethod
    def save(self, path: str) -> None:
        """Compile if necessary and write the result to disk."""

    @property
    def document(self) -> str | None:
        """The last rendered output, or None if render()/save() hasn't been called yet."""
        return self._document
