from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from scrapi.llm.base import BaseLLM


class OllamaLLM(BaseLLM):
    """Ollama endpoint via its OpenAI-compatible API (/v1).

    Attributes:
        meta: Configuration used to build the underlying chat model,
            keyed by "base_url", "model".
    """

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11434/v1",
        model: str = "gemma3:4b",
    ) -> None:
        """Initialise the Ollama endpoint configuration.

        Args:
            base_url: Base URL of the Ollama server's OpenAI-compatible API.
            model: Name of the Ollama model to use.
        """
        self.meta = {
            "base_url": base_url,
            "model": model,
        }
        super().__init__()

    def _create_llm(self) -> BaseChatModel:
        return ChatOpenAI(
            model=self.meta["model"],
            base_url=self.meta["base_url"],
            api_key="ollama",
        )
