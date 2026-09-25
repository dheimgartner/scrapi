from abc import ABC, abstractmethod
from typing import Any

from conflict_checker.interface.search_result.base_search_result import BaseSearchResult


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
    def fetch_content(self, query: str, n: int) -> list[BaseSearchResult]:
        """Retrieve content matching a query.

        Implementations are responsible for executing the query against
        their respective data source, collecting the results, and
        returning them as search results.

        Args:
            query (str): Query used to retrieve content.
            n (int): Maximum number of results to return.

        Returns:
            list[BaseSearchResult]: Retrieved content represented as
                base search result.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        """Convert the raw content to content suitable for LLM consumption."""
        pass
