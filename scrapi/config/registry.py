"""Registries mapping provider names to their concrete implementations.

Used by the config parsing/factory code to resolve a provider string
(e.g. from a YAML config) to the corresponding LLM or scraper class.
"""

from scrapi.llm.openai import OpenaiLLM
from scrapi.scraping.yahoo import YahooScraper
from scrapi.scraping.yfinance import YFinanceScraper

LLM_REGISTRY = {
    "openai": OpenaiLLM,
}

SCRAPER_REGISTRY = {
    "yahoo": YahooScraper,
    "yfinance": YFinanceScraper,
}
