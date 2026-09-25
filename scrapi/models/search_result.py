from abc import ABC
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import uuid
from typing import Any

from scrapi.storage.storable import DatabaseStorable
from scrapi.storage import table_path as tp
from scrapi.renderer.markdown import SearchResultMarkdownMixin, WebSearchResultMarkdownMixin


@dataclass(frozen=True)
class SearchStatus(ABC):
    status: int
    message: str | None = None


@dataclass(frozen=True)
class SuccessfulSearch(SearchStatus): ...


@dataclass(frozen=True)
class FailedSearch(SearchStatus):
    error: Exception | None = None


CONFLICT_CHECKER_WEB_SEARCH_RESULTS = tp.TablePath(
    "dwhdata.finma.ch",
    "gbi_reporting",
    "gbi",
    "conflict_checker_web_search_results",
)


@dataclass
class BaseSearchResult(ABC, SearchResultMarkdownMixin):
    """Every search engine must return on object of type BaseSearchResult

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
class WebSearchResult(BaseSearchResult, WebSearchResultMarkdownMixin, DatabaseStorable):

    def get_table_path(self) -> tp.TablePath:
        return CONFLICT_CHECKER_WEB_SEARCH_RESULTS

    def to_db_dict(self) -> dict:
        d = asdict(self)
        d["status"] = repr(d["status"])
        d["source"] = json.dumps(d["source"])
        return d
