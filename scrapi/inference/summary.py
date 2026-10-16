import json
from typing import cast

from langchain_core.language_models import BaseChatModel

from scrapi.inference.inference import Inference
from scrapi.inference.schemas import SummarySchema
from scrapi.models.inference_result import SearchInferenceResult, SummaryInferenceResult


class SummaryInference:
    """Summarises a set of search inference results into one summary."""

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
            schema=SummarySchema,
        )

    def run(self, search_inference_results: list[SearchInferenceResult]) -> SummaryInferenceResult:
        content = f"articles:\n\n{self._serialize(search_inference_results)}"
        ir = self._inference.run(content)
        structured_output = cast(SummarySchema, ir.structured_output)
        return SummaryInferenceResult(
            system_prompt=ir.system_prompt,
            task_prompt=ir.task_prompt,
            prompted_at=ir.prompted_at,
            structured_output=structured_output,
            result=structured_output.result,
            result_md=structured_output.result_md,
        )

    @staticmethod
    def _serialize(search_inference_results: list[SearchInferenceResult]) -> str:
        return json.dumps(
            [
                {"source": sir.id, **sir.structured_output.model_dump()}
                for sir in search_inference_results
            ],
            indent=2,
        )
