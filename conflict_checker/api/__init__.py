"""Public API surface for the conflict checker package.

Re-exports so callers can import them directly from
`conflict_checker.api` instead of their individual submodules.
"""

from conflict_checker.api.config.parse_config import parse_config
from conflict_checker.api.config.load_yaml_config import load_yaml_config
from conflict_checker.api.factory import make_conflict_checker
from conflict_checker.api.utils.save_result_to_md import save_result_to_md
from conflict_checker.scraping.proxy.proxy_session import PROXY_SESSION  # noqa: F401
from conflict_checker.api.config.default_config import DEFAULT_CONFIG
