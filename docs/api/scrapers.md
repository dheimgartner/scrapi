# Scrapers

All scrapers inherit from `BaseScraper` and implement a `_scrape()` method that returns a list of `BaseSearchResult` objects. The public `scrape()` method wraps `_scrape()` and raises `NoResultsFoundError` on empty or failed results.

## BaseScraper

::: scrapi.scraping.base.BaseScraper
    options:
      members: [_scrape, scrape, convert_to_ai_content]

## YahooScraper

Searches the web via DDGS (DuckDuckGo Search), then downloads each page via Selenium and converts HTML to Markdown using MarkItDown.

::: scrapi.scraping.yahoo.YahooScraper
    options:
      members: [_scrape, convert_to_ai_content]

## FileScraper

Reads local files. PDFs are converted via PyMuPDF4LLM; other formats (Word, Excel, etc.) via MarkItDown.

::: scrapi.scraping.file.FileScraper
    options:
      members: [_scrape, convert_to_ai_content]

## FinanceScraper

Fetches financial data via [yfinance](https://github.com/ranaroussi/yfinance). Returns a `FinancialSnapshot` as `raw_content`.

::: scrapi.scraping.finance.FinanceScraper
    options:
      members: [_scrape, convert_to_ai_content]

## SQLScraper

Executes a SQL query via SQLAlchemy. Supports `${VAR}` placeholders in the connection string, resolved from environment variables.

::: scrapi.scraping.sql.SQLScraper
    options:
      members: [__init__, _scrape, convert_to_ai_content]

## DummyScraper

Generates synthetic results for testing and development.

::: scrapi.scraping.dummy.DummyScraper
    options:
      members: [_scrape, convert_to_ai_content]
