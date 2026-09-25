import os

from langchain_openai import AzureChatOpenAI
from langchain_core.language_models import BaseChatModel

from scrapi.llm.base import BaseLLM


class OpenaiLLM(BaseLLM):
    """Azure OpenAI endpoint for conflict checks.

    Attributes:
        meta: Configuration used to build the underlying chat model,
            keyed by "azure_endpoint", "api_version", "model", "api_key".
    """

    def __init__(
        self,
        *,
        azure_endpoint: str = "https://openai-asb-gbo-dev-rg-01.openai.azure.com/",
        api_version: str = "2024-12-01-preview",
        api_key: str = None,
        model: str = "gpt-4.1",
    ) -> None:
        """Initialise the Azure OpenAI endpoint configuration.

        Args:
            azure_endpoint: Base URL of the Azure OpenAI resource.
            api_version: Azure OpenAI API version to target.
            api_key: API key for authentication. Falls back to the
                `AZURE_OPENAI_API_KEY` environment variable if not given.
            model: Name of the Azure deployment/model to use.
        """
        self.meta = {
            "azure_endpoint": azure_endpoint,
            "api_version": api_version,
            "model": model,
            "api_key": api_key or os.getenv("AZURE_OPENAI_API_KEY"),
        }
        super().__init__()

    def _create_llm(self) -> BaseChatModel:
        return AzureChatOpenAI(
            azure_deployment=self.meta["model"],
            api_version=self.meta["api_version"],
            azure_endpoint=self.meta["azure_endpoint"],
            api_key=self.meta["api_key"],
        )
