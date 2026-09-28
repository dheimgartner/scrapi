from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapi.models.pipeline_result import PipelineResult
    from scrapi.models.search_result import BaseSearchResult
    from scrapi.models.inference_result import BaseInferenceResult


class BaseRenderer(ABC):

    def __init__(self, pipeline_result: PipelineResult) -> None:
        self._pipeline_result = pipeline_result
        self._document: str | None = None

    @abstractmethod
    def render(self) -> str:
        """Renders the pipeline result and returns it as a string.

        Implementations should walk `self._pipeline_result`, call
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
