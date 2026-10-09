from abc import ABC, abstractmethod
from typing import Any

from scrapi.exceptions import NoResultsFoundError
from scrapi.models.search_result import BaseSearchResult


class BaseScraper(ABC):
    """Abstract base class for content scrapers.

    All scraper implementations must provide a mechanism for retrieving
    content from a data source and converting it into a collection of
    ``BaseSearchResult`` objects.

    Implementations may obtain their content from search engines, web
    pages, APIs, document repositories, or other external systems, but
    should expose a consistent interface through ``fetch_content()``.
    """

    @abstractmethod
    def _fetch_content(self, *args, **kwargs) -> list[BaseSearchResult]:
        """Retrieve content.

        Implementations are responsible for executing the query against
        their respective data source, collecting the results, and
        returning them as search results. Each subclass defines its own
        parameter signature.

        Returns:
            list[BaseSearchResult]: Retrieved content represented as
                base search result.
        """
        pass

    def fetch_content(self, *args, **kwargs) -> list[BaseSearchResult]:
        """Retrieve content, raising ``NoResultsFoundError`` on failure.

        Wraps ``_fetch_content`` and raises if the result is empty or if
        the underlying implementation raises any exception.
        """
        try:
            results = self._fetch_content(*args, **kwargs)
        except Exception as e:
            raise NoResultsFoundError("No results found") from e
        if not results:
            raise NoResultsFoundError("No results found")
        return results

    @staticmethod
    @abstractmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        """Convert the raw content to content suitable for LLM consumption."""
        pass
