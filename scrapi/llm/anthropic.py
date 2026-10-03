import os

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

from scrapi.llm.base import BaseLLM


class AnthropicLLM(BaseLLM):
    """Anthropic Claude endpoint.

    Attributes:
        meta: Configuration used to build the underlying chat model,
            keyed by "model" and "api_key".
    """

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-6",
        api_key: str = None,
    ) -> None:
        """Initialise the Anthropic endpoint configuration.

        Args:
            model: Anthropic model identifier to use.
            api_key: API key for authentication. Falls back to the
                `ANTHROPIC_API_KEY` environment variable if not given.
        """
        self.meta = {
            "model": model,
            "api_key": api_key or os.getenv("ANTHROPIC_API_KEY"),
        }
        super().__init__()

    def _create_llm(self) -> BaseChatModel:
        return ChatAnthropic(
            model=self.meta["model"],
            api_key=self.meta["api_key"],
        )
