import os
from abc import ABC, abstractmethod
from tempfile import NamedTemporaryFile
from typing import Any

from bs4 import BeautifulSoup
from markitdown import MarkItDown

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
    def _fetch_content(self, query: str, n: int) -> list[BaseSearchResult]:
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

    def fetch_content(self, query: str, n: int) -> list[BaseSearchResult]:
        """Retrieve content, raising ``NoResultsFoundError`` on failure.

        Wraps ``_fetch_content`` and raises if the result is empty or if
        the underlying implementation raises any exception.
        """
        try:
            results = self._fetch_content(query, n)
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

    @staticmethod
    def html_to_markdown(
        html: str,
        remove_tags: tuple[str, ...] = ("script", "style"),
    ) -> str:
        """Convert an HTML string to Markdown.

        Strips the specified tags before conversion to reduce noise.

        Args:
            html: Raw HTML string.
            remove_tags: Tag names to strip before conversion.

        Returns:
            Markdown-formatted string.
        """
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(remove_tags):
            tag.decompose()

        with NamedTemporaryFile(
            mode="w",
            suffix=".html",
            encoding="utf-8",
            delete=False,
        ) as f:
            f.write(str(soup))
            filepath = f.name

        md = MarkItDown()
        markdown = md.convert(filepath).text_content
        os.remove(filepath)
        return markdown
