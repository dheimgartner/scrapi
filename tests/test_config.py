"""Tests for config parsing and loading."""

import tempfile
from pathlib import Path

import pytest

from scrapi.config.loader import parse_config, load_toml_config
from scrapi.config.schemas import ScrapiConfig, RendererConfig
from scrapi.exceptions import ConfigLoadError


_BASE_CONFIG = {
    "llm": {"provider": "ollama", "config": {}},
    "inference": {
        "search": {"system_prompt": "sys", "task_prompt": "task"},
        "summary": {"system_prompt": "sys", "task_prompt": "sum"},
    },
    "scrapers": [
        {"provider": "dummy", "config": {}, "scrape": {"query": "q", "n": 2}},
    ],
}

_VALID_TOML = """\
[llm]
provider = "ollama"

[llm.config]

[inference.search]
system_prompt = "sys"
task_prompt = "task"

[inference.summary]
system_prompt = "sys"
task_prompt = "sum"

[[scrapers]]
provider = "dummy"
[scrapers.scrape]
query = "q"
n = 2
"""


def test_parse_config_valid():
    config = parse_config(_BASE_CONFIG)
    assert isinstance(config, ScrapiConfig)
    assert config.llm.provider == "ollama"
    assert config.inference.search.system_prompt == "sys"
    assert config.inference.summary.task_prompt == "sum"
    assert config.scrapers[0].provider == "dummy"
    assert config.scrapers[0].scrape["n"] == 2


def test_load_toml_config_from_file():
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
        f.write(_VALID_TOML.encode())
        tmp_path = Path(f.name)

    try:
        config = load_toml_config(tmp_path)
        assert isinstance(config, ScrapiConfig)
        assert config.llm.provider == "ollama"
        assert config.scrapers[0].provider == "dummy"
        assert config.scrapers[0].scrape["n"] == 2
    finally:
        tmp_path.unlink(missing_ok=True)


def test_parse_config_renderer():
    config = parse_config({
        **_BASE_CONFIG,
        "renderer": {"provider": "markdown", "report_path": "~/out.md"},
    })
    assert isinstance(config.renderer, RendererConfig)
    assert config.renderer.provider == "markdown"
    assert config.renderer.report_path == "~/out.md"


def test_parse_config_renderer_optional():
    config = parse_config(_BASE_CONFIG)
    assert config.renderer is None


def test_parse_config_renderer_no_report_path():
    config = parse_config({**_BASE_CONFIG, "renderer": {"provider": "markdown"}})
    assert config.renderer.report_path is None


def test_load_toml_config_invalid_toml():
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
        f.write(b"[invalid toml\nkey = ")
        tmp_path = Path(f.name)

    try:
        with pytest.raises(ConfigLoadError):
            load_toml_config(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
