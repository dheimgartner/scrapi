import inspect
from typing import Any

from scrapi.exceptions import InvalidConfigError
import scrapi.config.schemas as schema
import scrapi.config.registry as registry
from scrapi.orchestrator import Orchestrator


def make_orchestrator(config: schema.ScrapiConfig) -> Orchestrator:
    """Creates an Orchestrator from a ScrapiConfig.

    Instantiates the scraper and LLM providers from their respective registries,
    then injects them into the orchestrator kwargs before building the Orchestrator.

    Args:
        config: Configuration containing scraper, inference, and orchestrator settings.

    Returns:
        A fully instantiated Orchestrator.
    """
    scraper = _base_factory(
        registry.SCRAPER_REGISTRY[config.scraper.provider], config.scraper
    )
    llm = _base_factory(
        registry.LLM_REGISTRY[config.inference.provider], config.inference
    )

    kwargs = {**config.orchestrator.config, "scraper": scraper, "llm": llm}
    try:
        return Orchestrator(**kwargs)
    except Exception as e:
        raise InvalidConfigError(f"Failed to instantiate Orchestrator: {e}", cause=e) from e


def _base_factory(cls: type, config: schema.BaseConfig) -> Any:
    kwargs = config.config
    sig = inspect.signature(cls.__init__)
    params = sig.parameters

    if not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
        _ensure_no_extra_params(params, kwargs, config.provider)
        _ensure_required_params(params, kwargs, config.provider)

    try:
        return cls(**kwargs)
    except Exception as e:
        raise InvalidConfigError(
            f"Failed to instantiate {config.provider!r}: {e}",
            provider=config.provider,
            cause=e,
        ) from e


def _ensure_no_extra_params(
    params: inspect.Parameter,
    kwargs: dict,
    provider: str,
) -> None:
    valid = set(params) - {"self"}
    if unknown := set(kwargs) - valid:
        raise InvalidConfigError(f"{provider!r} got unexpected arguments: {unknown}")


def _ensure_required_params(
    params: inspect.Parameter,
    kwargs: dict,
    provider: str,
) -> None:
    required = {
        name
        for name, p in params.items()
        if name != "self"
        and p.default is inspect.Parameter.empty
        and p.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    }
    if missing := required - set(kwargs):
        raise InvalidConfigError(f"{provider!r} missing required arguments: {missing}")
