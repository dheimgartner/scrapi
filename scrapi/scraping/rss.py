from datetime import datetime
from typing import Any

import feedparser
from bs4 import BeautifulSoup

import scrapi.scraping.base as bs
from scrapi.models.search_result import WebSearchResult, SuccessfulSearch, FailedSearch


class RssScraper(bs.BaseScraper):
    """Fetch articles from an RSS feed.

    The query is an RSS feed URL. Up to ``n`` entries are returned using the
    title and summary provided by the feed — no additional HTTP requests are
    made to fetch full article pages.

    Example feed URLs:
        - Yahoo Finance ticker news:
          ``https://finance.yahoo.com/rss/2.0/headline?s=UBS&region=US&lang=en-US``
        - Reuters business news:
          ``https://feeds.reuters.com/reuters/businessNews``
    """

    def fetch_content(self, query: str, n: int) -> list[WebSearchResult]:
        """Parse an RSS feed and return up to ``n`` entries as search results.

        Args:
            query: URL of the RSS feed.
            n: Maximum number of feed entries to return.

        Returns:
            list[WebSearchResult]: Articles created from the feed entries.
        """
        feed = feedparser.parse(query)

        if feed.get("bozo") and not feed.entries:
            raise ValueError(f"Failed to parse RSS feed at {query!r}: {feed.bozo_exception}")

        return [
            self._create_web_search_result(entry, feed_url=query)
            for entry in feed.entries[:n]
        ]

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return raw_content

    @staticmethod
    def _create_web_search_result(entry: dict, feed_url: str) -> WebSearchResult:
        title = entry.get("title", "")
        summary = RssScraper._strip_html(entry.get("summary", ""))
        link = entry.get("link", "")

        published_parsed = entry.get("published_parsed")
        fetched_at = datetime(*published_parsed[:6]) if published_parsed else datetime.now()

        text = f"# {title}\n\n{summary}".strip() if summary else f"# {title}"

        return WebSearchResult(
            scraper_repr=repr(RssScraper),
            status=SuccessfulSearch(status=200),
            fetched_at=fetched_at,
            source={"url": link, "title": title, "feed": feed_url},
            raw_content=text,
            ai_content=text,
        )

    @staticmethod
    def _strip_html(text: str) -> str:
        return BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()
