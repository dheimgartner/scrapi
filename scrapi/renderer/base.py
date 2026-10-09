from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapi.models.run_result import RunResult


class BaseRenderer(ABC):
    """Abstract base class for pipeline result renderers.

    Subclasses format a ``RunResult`` into a specific output format
    and expose ``render()`` and ``save()`` as the public interface.
    """

    def __init__(self, output_path: str | None = None) -> None:
        self.output_path = output_path
        self._document: str | None = None

    @abstractmethod
    def render(self, run_result: RunResult) -> str:
        """Render ``run_result`` and return it as a string."""

    @abstractmethod
    def save(self) -> None:
        """Write the rendered document to ``output_path``. Call ``render()`` first."""

    @property
    def document(self) -> str | None:
        """The last rendered output, or None if ``render()`` hasn't been called yet."""
        return self._document

