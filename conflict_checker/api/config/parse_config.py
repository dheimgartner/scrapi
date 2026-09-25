import conflict_checker.api.config.schemas as schema


def parse_config(source: dict) -> schema.ConflictCheckConfig:
    """Parses a config dict into a ConflictCheckConfig.

    Args:
        source: Config dict.

    Returns:
        A ConflictCheckConfig populated from the dict.
    """
    return schema.ConflictCheckConfig(
        scraper=schema.ScraperConfig(
            provider=source["scraper"]["provider"],
            config=source["scraper"].get("config", {}),
        ),
        inference=schema.InferenceConfig(
            provider=source["inference"]["provider"],
            config=source["inference"].get("config", {}),
        ),
        orchestrator=schema.OrchestratorConfig(
            config=source["orchestrator"].get("config", {}),
        ),
    )
