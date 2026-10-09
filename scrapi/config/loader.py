import tomllib
from pathlib import Path

from scrapi.exceptions import ConfigLoadError
from scrapi.config.schemas import (
    ScrapiConfig,
    LLMConfig,
    RendererConfig,
    ScraperConfig,
    InferenceConfig,
    SearchInferenceConfig,
    SummaryInferenceConfig,
)


def parse_config(source: dict) -> ScrapiConfig:
    """Parses a config dict into a ScrapiConfig.

    Args:
        source: Config dict.

    Returns:
        A ScrapiConfig populated from the dict.
    """
    renderer_raw = source.get("renderer")
    renderer = (
        RendererConfig(
            provider=renderer_raw["provider"],
            output_path=renderer_raw.get("output_path"),
        )
        if renderer_raw is not None
        else None
    )

    return ScrapiConfig(
        llm=LLMConfig(
            provider=source["llm"]["provider"],
            config=source["llm"].get("config", {}),
        ),
        inference=InferenceConfig(
            search=SearchInferenceConfig(
                system_prompt=source["inference"]["search"]["system_prompt"],
                task_prompt=source["inference"]["search"]["task_prompt"],
            ),
            summary=SummaryInferenceConfig(
                system_prompt=source["inference"]["summary"]["system_prompt"],
                task_prompt=source["inference"]["summary"]["task_prompt"],
            ),
        ),
        scrapers=[
            ScraperConfig(
                provider=s["provider"],
                config=s.get("config", {}),
                fetch=s.get("fetch", {}),
            )
            for s in source["scrapers"]
        ],
        renderer=renderer,
    )


def load_toml_config(path: Path) -> ScrapiConfig:
    """Loads a scrapi config from a TOML file.

    Args:
        path: Path to the TOML config file to load.

    Returns:
        The parsed and validated scrapi configuration.

    Raises:
        ConfigLoadError: If the file's content is not valid TOML.
    """
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigLoadError(f"Failed to parse TOML config at {path}: {e}") from e

    return parse_config(data)
