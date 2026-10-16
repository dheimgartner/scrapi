from datetime import datetime
from typing import Any

import scrapi.scraping.base as bs
from scrapi.models.search_result import WebSearchResult, SuccessfulSearch


class DummyScraper(bs.BaseScraper):
    """Returns synthetic search results without making any network requests.

    Useful for local development and testing the analysis pipeline without
    a live scraper.
    """

    def _scrape(self, query: str, n: int) -> list[WebSearchResult]:
        return [self._make_result(query, i) for i in range(1, n + 1)]

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return raw_content

    @staticmethod
    def _make_result(query: str, index: int) -> WebSearchResult:
        text = f"Dummy article {index} about '{query}'. No real content."
        return WebSearchResult(
            scraper_repr=repr(DummyScraper),
            status=SuccessfulSearch(status=200),
            fetched_at=datetime.now(),
            source={"url": f"https://dummy.example.com/{index}"},
            raw_content=text,
            ai_content=text,
        )
