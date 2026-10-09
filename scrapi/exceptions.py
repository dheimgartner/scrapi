class ScrapiError(Exception):
    """Base error for all scrapi exceptions."""


class InvalidConfigError(ScrapiError):
    """Raised when a config is invalid or fails to instantiate a provider."""

    def __init__(
        self, message: str, provider: str | None = None, cause: Exception | None = None
    ):
        self.provider = provider
        self.cause = cause
        super().__init__(message)


class ConfigLoadError(ScrapiError):
    """Raised when a config file cannot be read."""


class NoResultsFoundError(ScrapiError):
    """Raised when a scraper returns no results or errors during fetch."""


class RendererError(ScrapiError):
    """Raised when a renderer is used incorrectly or fails to produce output."""
