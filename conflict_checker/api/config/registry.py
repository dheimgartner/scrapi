"""Registries mapping provider names to their concrete implementations.

Used by the config parsing/factory code to resolve a provider string
(e.g. from a YAML config) to the corresponding LLM or scraper class.
"""

from conflict_checker.ai.llm.openai_llm import OpenaiLLM
from conflict_checker.scraping.yahoo_scraper import YahooScraper

LLM_REGISTRY = {
    "openai": OpenaiLLM,
}

SCRAPER_REGISTRY = {
    "yahoo": YahooScraper,
}
