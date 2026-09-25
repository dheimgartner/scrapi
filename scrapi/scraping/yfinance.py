from datetime import datetime, timezone
import logging
from typing import Any

import yfinance as yf
from tqdm import tqdm

import scrapi.scraping.base as bs
import scrapi.scraping.selenium as shd
from scrapi.models.search_result import WebSearchResult, SuccessfulSearch, FailedSearch


class YFinanceScraper(bs.BaseScraper):
    """Fetch Yahoo Finance news for a ticker and convert articles to Markdown.

    The query is a ticker symbol (e.g. ``"UBS"``). Up to ``n`` news items are
    retrieved via the yfinance API, their article pages are downloaded with
    Selenium, and the HTML is converted to Markdown.
    """

    def fetch_content(self, query: str, n: int) -> list[WebSearchResult]:
        """Fetch up to ``n`` news articles for the given ticker symbol.

        Args:
            query: Ticker symbol (e.g. ``"UBS"``).
            n: Maximum number of news articles to retrieve.

        Returns:
            list[WebSearchResult]: Articles created from the news feed.
        """
        news_items = yf.Ticker(query).news[:n]
        self._retrieve_and_add_page_content(news_items)
        return [self._create_web_search_result(item, ticker=query) for item in news_items]

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return bs.BaseScraper.html_to_markdown(raw_content)

    @staticmethod
    def _retrieve_and_add_page_content(news_items: list[dict]) -> None:
        selenium = shd.SeleniumHTMLDownloader()
        for item in tqdm(news_items, desc="Downloading pages"):
            url = item["content"]["canonicalUrl"]["url"]
            try:
                item["raw_content"] = selenium.download_html(url)
                item["status"] = SuccessfulSearch(status=200)
            except Exception as e:
                logging.warning(e)
                item["raw_content"] = ""
                item["status"] = FailedSearch(status=0, message=str(e), error=e)

    @staticmethod
    def _create_web_search_result(item: dict, ticker: str) -> WebSearchResult:
        content = item["content"]
        pub_date = datetime.fromisoformat(content["pubDate"].replace("Z", "+00:00"))
        return WebSearchResult(
            scraper_repr=repr(YFinanceScraper),
            status=item["status"],
            fetched_at=pub_date.astimezone(timezone.utc).replace(tzinfo=None),
            source={
                "url": content["canonicalUrl"]["url"],
                "ticker": ticker,
                "title": content["title"],
                "publisher": content["provider"]["displayName"],
            },
            raw_content=item["raw_content"],
            ai_content=YFinanceScraper.convert_to_ai_content(item["raw_content"]),
        )
