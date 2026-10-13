from typing import cast

from langchain_core.language_models import BaseChatModel

from scrapi.inference.inference import Inference
from scrapi.inference.schemas import SearchSchema
from scrapi.models.inference_result import SearchInferenceResult
from scrapi.models.search_result import BaseSearchResult


class SearchInference:
    """Extracts structured information from a single search result."""

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        task_prompt: str,
    ) -> None:
        self._inference = Inference(
            llm=llm,
            system_prompt=system_prompt,
            task_prompt=task_prompt,
            schema=SearchSchema,
        )

    def analyse(self, search_result: BaseSearchResult) -> SearchInferenceResult:
        content = f"search_id: {search_result.id}\n\narticle:\n\n{search_result.ai_content}"
        ir = self._inference.run(content)
        structured_output = cast(SearchSchema, ir.structured_output)
        return SearchInferenceResult(
            system_prompt=ir.system_prompt,
            task_prompt=ir.task_prompt,
            prompted_at=ir.prompted_at,
            structured_output=structured_output,
            result=structured_output.result,
        )
