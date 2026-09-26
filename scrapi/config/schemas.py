from dataclasses import dataclass, field


@dataclass
class BaseConfig:
    """Base config for components resolved via a provider registry.

    Attributes:
        provider: Registry key identifying the implementation to use.
        config: Provider-specific keyword arguments.
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
class OrchestratorConfig:
    """Configuration for the orchestrator component.

    Attributes:
        config: Keyword arguments passed directly to Orchestrator.__init__.
    """

    config: dict = field(default_factory=dict)


@dataclass
class ScrapiConfig:
    """Top-level configuration for a scrapi run.

    Attributes:
        scraper: Configuration for the scraper component.
        inference: Configuration for the inference component.
        orchestrator: Configuration for the orchestrator component.
    """

    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
