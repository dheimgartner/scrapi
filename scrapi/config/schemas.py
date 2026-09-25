from dataclasses import dataclass, field


@dataclass
class BaseConfig:
    """Base config shared by scraper/inference component configs.

    Attributes:
        provider: Name of the provider implementation to use (e.g. a
            key into a provider registry).
        config: Provider-specific configuration options.
    """

    provider: str
    config: dict = field(default_factory=dict)


@dataclass
class ScraperConfig(BaseConfig):
    """Configuration for the scraper component."""

    pass


@dataclass
class InferenceConfig(BaseConfig):
    """Configuration for the inference component."""

    pass


@dataclass
class OrchestratorConfig(BaseConfig):
    """Configuration for the orchestrator component.

    Attributes:
        provider: Unused for the orchestrator, which has no provider
            registry. Defaults to "_".
    """

    provider: str = "_"


@dataclass
class ConflictCheckConfig:
    """Top-level configuration for a conflict-check run.

    Attributes:
        scraper: Configuration for the scraper component.
        inference: Configuration for the inference component.
        orchestrator: Configuration for the orchestrator component.
    """

    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
