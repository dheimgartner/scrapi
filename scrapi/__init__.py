"""Web scraping and LLM analysis pipeline.

Typical usage::

    import scrapi

    config = scrapi.load_toml_config("config.toml")
    orchestrator = scrapi.make_orchestrator(config)
    result = orchestrator.run()
"""

from scrapi.config.loader import parse_config, load_toml_config
from scrapi.factory import make_orchestrator
from scrapi.config.defaults import DEFAULT_CONFIG
