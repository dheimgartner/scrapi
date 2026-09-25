import yaml
from pathlib import Path

from scrapi.exceptions import ConfigLoadError
from scrapi.config.schemas import ConflictCheckConfig, ScraperConfig, InferenceConfig, OrchestratorConfig


def parse_config(source: dict) -> ConflictCheckConfig:
    """Parses a config dict into a ConflictCheckConfig.

    Args:
        source: Config dict.

    Returns:
        A ConflictCheckConfig populated from the dict.
    """
    return ConflictCheckConfig(
        scraper=ScraperConfig(
            provider=source["scraper"]["provider"],
            config=source["scraper"].get("config", {}),
        ),
        inference=InferenceConfig(
            provider=source["inference"]["provider"],
            config=source["inference"].get("config", {}),
        ),
        orchestrator=OrchestratorConfig(
            config=source["orchestrator"].get("config", {}),
        ),
    )


def load_yaml_config(path: Path) -> ConflictCheckConfig:
    """Loads a conflict checker config from a YAML file.

    Args:
        path: Path to the YAML config file to load.

    Returns:
        The parsed and validated conflict checker configuration.

    Raises:
        ConfigLoadError: If the file's content is not valid YAML, or if
            the parsed YAML is not a mapping (dict).
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigLoadError(f"Failed to parse YAML config at {path}: {e}") from e

    if not isinstance(data, dict):
        raise ConfigLoadError(
            f"Config at {path} must be a YAML mapping, got {type(data).__name__}"
        )

    return parse_config(data)
