import inspect
from typing import Any

from scrapi.exceptions import InvalidConfigError
import scrapi.config.schemas as schema
import scrapi.config.registry as registry
from scrapi.orchestrator import Orchestrator
from scrapi.inference.search import SearchInference
from scrapi.inference.summary import SummaryInference


def make_orchestrator(config: schema.ScrapiConfig) -> Orchestrator:
    """Creates an Orchestrator from a ScrapiConfig.

    Instantiates the LLM, both inference objects, and all scrapers from their
    respective registries, then wires them into the Orchestrator.

    Args:
        config: Configuration containing LLM, inference, and scraper settings.

    Returns:
        A fully instantiated Orchestrator.
    """
    llm = _base_factory(registry.LLM_REGISTRY[config.llm.provider], config.llm)

    search_inference = SearchInference(
        llm=llm.llm,
        system_prompt=config.inference.search.system_prompt,
        task_prompt=config.inference.search.task_prompt,
    )
    summary_inference = SummaryInference(
        llm=llm.llm,
        system_prompt=config.inference.summary.system_prompt,
        task_prompt=config.inference.summary.task_prompt,
    )

    scrapers = [
        (_base_factory(registry.SCRAPER_REGISTRY[sc.provider], sc), sc.scrape)
        for sc in config.scrapers
    ]

    renderer = None
    if config.renderer is not None:
        renderer_cls = registry.RENDERER_REGISTRY[config.renderer.provider]
        renderer = renderer_cls(
            output_path=config.renderer.output_path,
            result_md_path=config.renderer.result_md_path,
        )

    return Orchestrator(
        scrapers=scrapers,
        search_inference=search_inference,
        summary_inference=summary_inference,
        renderer=renderer,
    )


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
