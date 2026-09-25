from datetime import datetime, timezone
from typing import Any

import yfinance as yf
from tqdm import tqdm

import scrapi.scraping.base as bs
from scrapi.models.search_result import WebSearchResult, SuccessfulSearch


class YFinanceScraper(bs.BaseScraper):
    """Fetch Yahoo Finance news for a ticker via the yfinance API.

    The query is a ticker symbol (e.g. ``"UBS"``). Up to ``n`` news items are
    retrieved and their API-provided title and summary are used directly as
    content — no HTML fetching required.
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
        return [
            self._create_web_search_result(item, ticker=query)
            for item in tqdm(news_items, desc="Processing news items")
        ]

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return raw_content

    @staticmethod
    def _create_web_search_result(item: dict, ticker: str) -> WebSearchResult:
        content = item["content"]
        pub_date = datetime.fromisoformat(content["pubDate"].replace("Z", "+00:00"))
        title = content["title"]
        summary = content.get("summary", "")
        text = f"# {title}\n\n{summary}" if summary else f"# {title}"
        return WebSearchResult(
            scraper_repr=repr(YFinanceScraper),
            status=SuccessfulSearch(status=200),
            fetched_at=pub_date.astimezone(timezone.utc).replace(tzinfo=None),
            source={
                "url": content["canonicalUrl"]["url"],
                "ticker": ticker,
                "title": title,
                "publisher": content["provider"]["displayName"],
            },
            raw_content=text,
            ai_content=text,
        )
