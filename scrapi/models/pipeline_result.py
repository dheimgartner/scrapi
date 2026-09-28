from typing import NamedTuple

from scrapi.models.search_result import BaseSearchResult
from scrapi.models.inference_result import BaseInferenceResult


class ResultPair(NamedTuple):
    """A single search result paired with its (optional) inference result."""
    search: BaseSearchResult
    inference: BaseInferenceResult | None


class PipelineResult:
    """Plain data holder for a scrapi run's results.

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
