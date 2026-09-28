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
class LLMConfig(BaseConfig):
    """Configuration for the LLM component."""
    pass


@dataclass
class ScraperConfig(BaseConfig):
    """Configuration for a single scraper, including its fetch call arguments.

    Attributes:
        fetch: Keyword arguments forwarded to ``scraper.fetch_content()``.
    """

    fetch: dict = field(default_factory=dict)


@dataclass
class SearchInferenceConfig:
    """Prompts for per-result structured extraction.

    Attributes:
        system_prompt: System-level instructions for the LLM.
        task_prompt: Human-level instructions for the extraction task.
    """

    system_prompt: str
    task_prompt: str


@dataclass
class SummaryInferenceConfig:
    """Prompts for final summary generation.

    Attributes:
        system_prompt: System-level instructions for the LLM.
        task_prompt: Human-level instructions for the summarisation task.
    """

    system_prompt: str
    task_prompt: str


@dataclass
class InferenceConfig:
    """Configuration for both inference stages.

    Attributes:
        search: Config for per-result search inference.
        summary: Config for final summary inference.
    """

    search: SearchInferenceConfig
    summary: SummaryInferenceConfig


@dataclass
class ScrapiConfig:
    """Top-level configuration for a scrapi run.

    Attributes:
        llm: Configuration for the LLM provider.
        inference: Configuration for both inference stages.
        scrapers: List of scraper configurations, each with its own fetch args.
    """

    llm: LLMConfig
    inference: InferenceConfig
    scrapers: list[ScraperConfig]
