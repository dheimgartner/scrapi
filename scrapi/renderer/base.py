from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapi.models.pipeline_result import PipelineResult


class BaseRenderer(ABC):
    """Abstract base class for pipeline result renderers.

    Subclasses format a ``PipelineResult`` into a specific output format
    and expose ``render()`` and ``save()`` as the public interface.
    """

    def __init__(self, output_path: str | None = None) -> None:
        self._output_path = output_path
        self._document: str | None = None

    @abstractmethod
    def render(self, pipeline_result: PipelineResult) -> str:
        """Render ``pipeline_result`` and return it as a string."""

    @abstractmethod
    def save(self, path: str) -> None:
        """Write the rendered document to disk. Call ``render()`` first."""

    @property
    def document(self) -> str | None:
        """The last rendered output, or None if ``render()`` hasn't been called yet."""
        return self._document

    @property
    def output_path(self) -> str | None:
        """Destination path for ``save()``, or None if not configured."""
        return self._output_path
