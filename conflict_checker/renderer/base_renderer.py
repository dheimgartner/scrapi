from abc import ABC, abstractmethod
from typing import NamedTuple

from conflict_checker.interface.search_result.base_search_result import BaseSearchResult
from conflict_checker.interface.inference_result.base_inference_result import BaseInferenceResult


class ResultPair(NamedTuple):
    """A single search result paired with its (optional) inference result."""
    search: BaseSearchResult
    inference: BaseInferenceResult | None


class Report:
    """
    Plain data holder for a conflict-check report.

    Report itself is renderer-agnostic: it does not know about output
    formats and is never mutated by a renderer. Each BaseRenderer owns
    its own rendered output.
    """

    def __init__(self,
                 results: list[ResultPair],
                 summary: BaseInferenceResult) -> None:
        self.results = results
        self.summary = summary

    def __iter__(self):
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)


class BaseRenderer(ABC):

    def __init__(self, report: Report) -> None:
        self._report = report
        self._document: str | None = None

    @abstractmethod
    def render(self) -> str:
        """
        Renders the report and returns it in string format.

        Implementations should walk `self._report`, call
        `render_search_result()` resp. `render_inference_result()`,
        assemble the final document, and return it.
        """

    @abstractmethod
    def render_search_result(self, result: BaseSearchResult) -> str:
        """
        Format a single search result in this renderer's output format.
        """

    @abstractmethod
    def render_inference_result(self, result: BaseInferenceResult) -> str:
        """
        Format a single inference result in this renderer's output format.
        """

    @abstractmethod
    def save(self, path: str) -> None:
        """Compile if necessary and write the result to disk."""

    @property
    def document(self) -> str | None:
        """The last rendered output, or None if render()/save() hasn't
        been called yet."""
        return self._document