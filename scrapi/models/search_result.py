from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapi.models.financial_snapshot import FinancialSnapshot


@dataclass(frozen=True)
class SearchStatus(ABC):
    """Base class for fetch status codes."""

    status: int
    message: str | None = None


@dataclass(frozen=True)
class SuccessfulSearch(SearchStatus):
    """Indicates a successful fetch (HTTP 200 or equivalent)."""


@dataclass(frozen=True)
class FailedSearch(SearchStatus):
    """Indicates a failed fetch.

    Attributes:
        error: The exception that caused the failure, if any.
    """

    error: Exception | None = None


@dataclass
class BaseSearchResult(ABC):
    """Every search engine must return an object of type BaseSearchResult.

    Attributes:
        id: Unique identifier for this search result (auto-generated if not provided).
        pipeline_id: Unique identifier for the pipeline run, linking search results, inference results, and summary result.
        scraper_repr: Corresponding search engine.
        status: The fetch status.
        fetched_at: Timestamp at which the result was fetched.
        source: Depending on the search engine: e.g., {"url": "..."} for a web search engine.
        raw_content: Return value of search engine's `fetch_result()` call.
        ai_content: Converted `raw_content` suitable for LLM consumption.
    """
    scraper_repr: str
    status: SearchStatus
    fetched_at: datetime
    source: dict[str, str]
    raw_content: Any
    ai_content: str
    id: str | None = None
    pipeline_id: str | None = None

    def __post_init__(self) -> None:
        if self.id is None:
            object.__setattr__(self, "id", uuid.uuid4().hex)


@dataclass
class WebSearchResult(BaseSearchResult):
    """Search result from a web-based scraper."""


@dataclass
class FileSearchResult(BaseSearchResult):
    """Search result from a local file scraper."""


@dataclass
class FinanceSearchResult(BaseSearchResult):
    """Search result from the finance scraper.

    Unlike other result types, ``raw_content`` is a ``FinancialSnapshot``
    instead of a raw string.
    """

    raw_content: FinancialSnapshot
