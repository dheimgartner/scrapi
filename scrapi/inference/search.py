from langchain_core.language_models import BaseChatModel
from datetime import datetime
from typing import cast

from scrapi.inference.base import BaseStructuredInference
from scrapi.inference.schemas import SearchSchema
from scrapi.models.inference_result import SearchInferenceResult
from scrapi.models.search_result import BaseSearchResult


class SearchInference(BaseStructuredInference):
    """Extracts structured information from a single search result.

    Attributes:
        system_prompt: System-level instructions sent to the LLM,
            establishing its role/behaviour for the extraction task.
        task_prompt: Human-level instructions describing the specific
            extraction task to perform.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        task_prompt: str,
    ) -> None:
        super().__init__(llm=llm, schema=SearchSchema)
        self.system_prompt = system_prompt
        self.task_prompt = task_prompt

    def analyse(self, search_result: BaseSearchResult) -> SearchInferenceResult:
        """Extract structured information from a single search result.

        Sends the search result's content to the LLM alongside the
        system/task prompts and returns a structured response.

        Args:
            search_result: The search result to analyse. Its `ai_content`
                is sent to the LLM to be analysed.

        Returns:
            A `SearchInferenceResult` whose `structured_output` is a `SearchSchema` instance.
        """
        messages = [
            ("system", self.system_prompt),
            ("human", self.task_prompt),
            (
                "human",
                f"search_id: {search_result.id}\n\narticle:\n\n{search_result.ai_content}",
            ),
        ]

        structured_output = cast(SearchSchema, self.call_structured(messages))
        return SearchInferenceResult(
            system_prompt=self.system_prompt,
            task_prompt=self.task_prompt,
            prompted_at=datetime.now(),
            structured_output=structured_output,
            result=structured_output.result
        )
