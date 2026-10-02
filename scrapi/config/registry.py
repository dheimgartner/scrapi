"""Registries mapping provider names to their concrete implementations.

Used by the config parsing/factory code to resolve a provider string
(e.g. from a YAML config) to the corresponding LLM or scraper class.
"""

from scrapi.llm.ollama import OllamaLLM
from scrapi.llm.openai import OpenaiLLM
from scrapi.scraping.dummy import DummyScraper
from scrapi.scraping.file import FileScraper
from scrapi.scraping.yahoo import YahooScraper

LLM_REGISTRY = {
    "ollama": OllamaLLM,
    "openai": OpenaiLLM,
}

SCRAPER_REGISTRY = {
    "dummy": DummyScraper,
    "file": FileScraper,
    "yahoo": YahooScraper,
}
