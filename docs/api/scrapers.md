# Scrapers

All scrapers inherit from `BaseScraper` and implement a `scrape()` method that yields `BaseSearchResult` objects.

## BaseScraper

::: scrapi.scraping.base.BaseScraper

## YahooScraper

Searches the web via DDGS (DuckDuckGo Search), then downloads each page via Selenium and converts HTML to Markdown using MarkItDown.

::: scrapi.scraping.yahoo.YahooScraper

## FileScraper

Reads local files. PDFs are converted via PyMuPDF4LLM; other formats (Word, Excel, etc.) via MarkItDown.

::: scrapi.scraping.file.FileScraper

## FinanceScraper

Fetches financial data via [yfinance](https://github.com/ranaroussi/yfinance). Returns a `FinancialSnapshot` as `raw_content`.

::: scrapi.scraping.finance.FinanceScraper

## SQLScraper

Executes a SQL query via SQLAlchemy. Supports `${VAR}` placeholders in the connection string, resolved from environment variables.

::: scrapi.scraping.sql.SQLScraper

## DummyScraper

Generates synthetic results for testing and development.

::: scrapi.scraping.dummy.DummyScraper
