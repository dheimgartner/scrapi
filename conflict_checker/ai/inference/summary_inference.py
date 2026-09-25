import json

from datetime import datetime
from langchain_core.language_models import BaseChatModel
from typing import cast

from conflict_checker.ai.inference.base_structured_inference import BaseStructuredInference
from conflict_checker.interface.inference_result.search_inference_result import SearchInferenceResult
from conflict_checker.interface.inference_result.summary_inference_result import (
    SummarySchema,
    SummaryInferenceResult,
)


class SummaryInference(BaseStructuredInference):
    """Summarises a set of search inference results into one summary.

    Attributes:
        system_prompt: System-level instructions sent to the LLM,
            establishing its role/behaviour for the summarisation task.
        task_prompt: Human-level instructions describing the specific
            summarisation task to perform.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        task_prompt: str,
    ) -> None:
        super().__init__(llm, schema=SummarySchema)
        self.system_prompt = system_prompt
        self.task_prompt = task_prompt

    def analyse(self, search_inference_results: list[SearchInferenceResult]) -> SummaryInferenceResult:
        """Summarise a collection of search inference results.

        Serialises the given search inference structured output field,
        sends them to the LLM alongside the system/task prompts, and
        returns a summary inference result.

        Args:
            search_inference_results: List of search inference results to summarise.
                Each result's id is recorded as a source, and
                its structured output is serialised into
                the prompt sent to the LLM.

        Returns:
            A `SummaryInferenceResult` whose `result` is a `SummarySchema` instance.
        """
        serialized = self._serialize_search_inference_results(search_inference_results)
        messages = [
            ("system", self.system_prompt),
            ("human", self.task_prompt),
            ("human", f"articles:\n\n{serialized}"),
        ]

        structured_output = cast(SummarySchema, self.call_structured(messages))
        return SummaryInferenceResult(
            system_prompt=self.system_prompt,
            task_prompt=self.task_prompt,
            prompted_at=datetime.now(),
            structured_output=structured_output,
            result=structured_output.result
        )

    @staticmethod
    def _serialize_search_inference_results(search_inference_results: list[SearchInferenceResult]) -> str:
        return json.dumps(
            [
                {"source": sir.id, **sir.structured_output.model_dump()}
                for sir in search_inference_results
            ],
            indent=2,
        )
