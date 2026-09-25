from datetime import datetime
import logging
import os
from tempfile import NamedTemporaryFile
from typing import Any

from bs4 import BeautifulSoup
from ddgs import DDGS
from markitdown import MarkItDown
from tqdm import tqdm

import conflict_checker.scraping.base_scraper as bs
from conflict_checker.scraping.proxy.proxy_session import PROXY_SESSION
import conflict_checker.scraping.selenium.selenium_html_downloader as shd
from conflict_checker.interface.search_result.web_search_result import WebSearchResult


class YahooScraper(bs.BaseScraper):
    """Scrape Yahoo search results and convert them into articles.

    The scraper performs a Yahoo search through DDGS, downloads the HTML
    content of each search result, extracts the page content, and converts
    the result into a collection of ``StandardizedArticle`` objects.

    A shared proxy session is used for all search requests to ensure
    network traffic is routed through the corporate proxy and trusted
    certificates are applied consistently.

    The resulting articles contain both the original HTML and a Markdown
    representation of the page content suitable for downstream analysis.

    """

    def fetch_content(self, query: str, n: int) -> list[WebSearchResult]:
        """Searches Yahoo and returns the retrieved results as articles.

        This method performs the following steps:

        1. Executes a Yahoo search using DDGS.
        2. Retrieves up to ``n`` search results.
        3. Downloads the HTML content of each result page.
        4. Converts the downloaded content into Markdown.
        5. Creates and returns ``WebSearchResult`` objects containing
            the search result metadata and page content.

        All search requests are executed through the shared
        ``PROXY_SESSION`` to ensure access through the corporate proxy.

        Args:
            query (str): Search query to execute.
            n (int): Maximum number of search results to retrieve.

        Returns:
            list[WebSearchResult]: articles
                created from the retrieved search results.

        """
        with PROXY_SESSION as session:
            scraper = DDGS(
                proxy=session.proxy_url,
                verify=session.root_ca_path,
            )
            search_results = scraper.text(query, max_results=n, backend="yahoo")
            self._retrieve_and_add_page_content(search_results)

        articles = []
        for result in search_results:
            article = self._create_web_search_result(result)
            articles.append(article)

        return articles

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return YahooScraper._convert_html_to_markdown(raw_content, ("script", "style"))

    @staticmethod
    def _retrieve_and_add_page_content(search_results: list[dict]) -> None:
        """Fetches the HTML content for each search result and adds it to the results."""
        selenium = shd.SeleniumHTMLDownloader()

        for search_result in tqdm(search_results, desc="Download page content"):
            url = search_result["href"]

            try:
                search_result["raw_content"] = selenium.download_html(url)
            except Exception as e:
                logging.warning(e)
                search_result["raw_content"] = "Error"
                continue

    def _create_web_search_result(self, result: dict) -> WebSearchResult:
        return WebSearchResult(
            scraper_repr=repr(self),
            fetched_at=datetime.now(),
            source={"url": result["href"]},
            raw_content=result["raw_content"],
            ai_content=self.convert_to_ai_content(result["raw_content"])
        )

    @staticmethod
    def _convert_html_to_markdown(
        html: str,
        remove_tags: tuple[str, ...] = ("script", "style"),
    ) -> str:
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
