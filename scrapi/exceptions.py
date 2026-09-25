class ConflictCheckerError(Exception):
    """Base error for all conflict checker exceptions."""


class InvalidConfigError(ConflictCheckerError):
    """Raised when a config is invalid or fails to instantiate a provider."""

    def __init__(
        self, message: str, provider: str | None = None, cause: Exception | None = None
    ):
        self.provider = provider
        self.cause = cause
        super().__init__(message)


class ConfigLoadError(ConflictCheckerError):
    """Raised when a config file cannto be read."""
