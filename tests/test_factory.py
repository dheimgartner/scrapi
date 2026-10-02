"""Tests for the make_orchestrator factory."""

from unittest.mock import patch

import pytest

from scrapi.config.loader import parse_config
from scrapi.exceptions import InvalidConfigError
from scrapi.factory import make_orchestrator
from scrapi.orchestrator import Orchestrator
from scrapi.scraping.dummy import DummyScraper


_BASE_CONFIG = {
    "llm": {"provider": "ollama", "config": {}},
    "inference": {
        "search": {"system_prompt": "sys", "task_prompt": "task"},
        "summary": {"system_prompt": "sys", "task_prompt": "sum"},
    },
    "scrapers": [
        {"provider": "dummy", "config": {}, "fetch": {"query": "q", "n": 2}},
    ],
}


def test_make_orchestrator_returns_orchestrator():
    config = parse_config(_BASE_CONFIG)

    mock_llm = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()
    mock_llm.llm = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()

    with (
        patch("scrapi.config.registry.LLM_REGISTRY", {"ollama": lambda **kw: mock_llm}),
        patch("scrapi.config.registry.SCRAPER_REGISTRY", {"dummy": lambda **kw: DummyScraper()}),
    ):
        orchestrator = make_orchestrator(config)

    assert isinstance(orchestrator, Orchestrator)


def test_make_orchestrator_unknown_scraper():
    config = parse_config({
        **_BASE_CONFIG,
        "scrapers": [{"provider": "unknown_scraper", "config": {}, "fetch": {}}],
    })

    with pytest.raises((InvalidConfigError, KeyError)):
        make_orchestrator(config)
