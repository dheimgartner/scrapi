from datetime import datetime

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from scrapi.models.inference_result import BaseInferenceResult
from scrapi.models.search_result import BaseSearchResult


class Inference:
    """Single-shot structured output call against an LLM."""

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        task_prompt: str,
        schema: type[BaseModel],
    ) -> None:
        self.llm = llm
        self.system_prompt = system_prompt
        self.task_prompt = task_prompt
        self.schema = schema

    def run(self, content: str | BaseSearchResult) -> BaseInferenceResult:
        """Invoke the LLM and return a structured inference result.

        Args:
            content: Either a plain string or a ``BaseSearchResult`` whose
                ``ai_content`` is used as the content message.
        """
        if not isinstance(content, str):
            content = content.ai_content
        messages = [
            ("system", self.system_prompt),
            ("human", self.task_prompt),
            ("human", content),
        ]
        structured_output = self.llm.with_structured_output(self.schema).invoke(messages)
        return BaseInferenceResult(
            system_prompt=self.system_prompt,
            task_prompt=self.task_prompt,
            prompted_at=datetime.now(),
            structured_output=structured_output,
        )
