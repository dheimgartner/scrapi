from datetime import datetime
import logging
from typing import Any

from ddgs import DDGS
from tqdm import tqdm

import scrapi.scraping.base as bs
import scrapi.scraping.selenium as shd
from scrapi.models.search_result import WebSearchResult, SuccessfulSearch, FailedSearch


class YahooScraper(bs.BaseScraper):
    """Scrape Yahoo search results and convert them into articles.

    Performs a Yahoo search through DDGS, downloads the HTML content of
    each result page via Selenium, and converts it to Markdown.
    """

    def _fetch_content(self, query: str, n: int) -> list[WebSearchResult]:
        """Search Yahoo and return up to ``n`` results as articles.

        Args:
            query: Search query to execute.
            n: Maximum number of search results to retrieve.

        Returns:
            list[WebSearchResult]: Articles created from the search results.
        """
        scraper = DDGS()
        search_results = scraper.text(query, max_results=n, backend="yahoo")
        self._retrieve_and_add_page_content(search_results)
        return [self._create_web_search_result(r) for r in search_results]

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return bs.BaseScraper.html_to_markdown(raw_content)

    @staticmethod
    def _retrieve_and_add_page_content(search_results: list[dict]) -> None:
        selenium = shd.SeleniumHTMLDownloader()
        for result in tqdm(search_results, desc="Downloading pages"):
            try:
                result["raw_content"] = selenium.download_html(result["href"])
                result["status"] = SuccessfulSearch(status=200)
            except Exception as e:
                logging.warning(e)
                result["raw_content"] = ""
                result["status"] = FailedSearch(status=0, message=str(e), error=e)

    def _create_web_search_result(self, result: dict) -> WebSearchResult:
        return WebSearchResult(
            scraper_repr=repr(self),
            status=result["status"],
            fetched_at=datetime.now(),
            source={"url": result["href"]},
            raw_content=result["raw_content"],
            ai_content=self.convert_to_ai_content(result["raw_content"]),
        )
