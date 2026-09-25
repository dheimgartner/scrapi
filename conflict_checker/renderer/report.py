from typing import NamedTuple

from conflict_checker.interface.search_result.base_search_result import BaseSearchResult
from conflict_checker.interface.inference_result.base_inference_result import BaseInferenceResult


class ResultPair(NamedTuple):
    """A single search result paired with its (optional) inference result."""
    search: BaseSearchResult
    inference: BaseInferenceResult | None


class Report:
    """Plain data holder for a conflict-check report.

    Renderer-agnostic: does not know about output formats and is never
    mutated by a renderer.
    """

    def __init__(
        self,
        results: list[ResultPair],
        summary: BaseInferenceResult,
    ) -> None:
        self.results = results
        self.summary = summary

    def __iter__(self):
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)
