# Writing a Custom Scraper

`scrapi` is designed to be extended. If the built-in scrapers don't cover your data source, you can write your own in a few lines and slot it straight into the pipeline.

## Contract

Every scraper must subclass `BaseScraper` and implement two methods:

| Method | What it does |
|---|---|
| `_scrape(*args, **kwargs)` | Fetches content and returns a list of `BaseSearchResult` objects. You define the parameter signature. |
| `convert_to_ai_content(raw_content)` | Converts raw content to a plain string suitable for LLM consumption. |

The public `scrape()` method (inherited from `BaseScraper`) calls `_scrape()` and raises `NoResultsFoundError` if the result is empty or if an exception is raised — you do not need to implement it yourself.

## Minimal example

```python
from datetime import datetime
from typing import Any

from scrapi.scraping.base import BaseScraper
from scrapi.models.search_result import WebSearchResult, SuccessfulSearch, FailedSearch


class RSSFeedScraper(BaseScraper):
    """Fetches items from an RSS feed."""

    def __init__(self, feed_url: str) -> None:
        self.feed_url = feed_url

    def _scrape(self, n: int = 10) -> list[WebSearchResult]:
        import feedparser  # your own dependency

        feed = feedparser.parse(self.feed_url)
        results = []
        for entry in feed.entries[:n]:
            text = entry.get("summary", "")
            results.append(
                WebSearchResult(
                    scraper_repr=repr(self),
                    status=SuccessfulSearch(status=200),
                    fetched_at=datetime.now(),
                    source={"url": entry.get("link", "")},
                    raw_content=text,
                    ai_content=self.convert_to_ai_content(text),
                )
            )
        return results

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return raw_content
```

## Choosing a result type

Pick the `BaseSearchResult` subtype that best describes your source. Using the right type helps renderers and downstream code interpret the result correctly.

| Type | When to use |
|---|---|
| `WebSearchResult` | Web pages, APIs, feeds — any URL-backed source |
| `FileSearchResult` | Local files on disk |
| `FinanceSearchResult` | Financial/market data (`raw_content` should be a `FinancialSnapshot`) |
| `SQLSearchResult` | Database rows (`raw_content` should be a `list[dict]`) |
| `BaseSearchResult` | Subclass directly if none of the above fit |

## Handling errors

Set `status` to `FailedSearch` when a single item cannot be fetched, but still append the result so the pipeline sees all sources:

```python
try:
    text = fetch_content(url)
    status = SuccessfulSearch(status=200)
except Exception as e:
    text = ""
    status = FailedSearch(status=0, message=str(e), error=e)

results.append(WebSearchResult(..., status=status, raw_content=text, ai_content=text))
```

This lets the inference stage skip failed results gracefully rather than aborting the whole run.

## Using your scraper programmatically

```python
from scrapi import parse_config, make_orchestrator
from scrapi.scraping.base import BaseScraper  # or import your module

scraper = RSSFeedScraper(feed_url="https://feeds.example.com/news.rss")

# Use directly
results = scraper.scrape(n=5)

# Or wire into the orchestrator manually
from scrapi.orchestrator import Orchestrator
from scrapi.inference.search import SearchInference
from scrapi.inference.summary import SummaryInference

orchestrator = Orchestrator(
    scrapers=[(scraper, {"n": 5})],
    search_inference=search_inference,
    summary_inference=summary_inference,
)
result = orchestrator.run()
```

## Registering your scraper for TOML config

To use your scraper via `make_orchestrator` and a TOML config file, add it to `SCRAPER_REGISTRY` in `scrapi/config/registry.py`:

```python
from my_package.scrapers import RSSFeedScraper

SCRAPER_REGISTRY = {
    ...,
    "rss": RSSFeedScraper,
}
```

Then reference it in your config like any built-in scraper:

```toml
[[scrapers]]
provider = "rss"

[scrapers.config]
feed_url = "https://feeds.example.com/news.rss"

[scrapers.scrape]
n = 10
```

Keys under `[scrapers.config]` are forwarded to `__init__`; keys under `[scrapers.scrape]` are forwarded to `_scrape()`.
