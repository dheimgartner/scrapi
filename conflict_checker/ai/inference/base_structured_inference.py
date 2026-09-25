from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from conflict_checker.interface.inference_result.base_inference_result import BaseInferenceResult


class BaseStructuredInference(ABC):
    """Shared base for single-shot structured output calls.

    Subclasses implement `analyse()` with domain-specific signatures and
    call `call_structured()` to do the actual LLM invocation.

    Attributes:
        llm: Chat model used to perform the structured invocation.
        schema: Pydantic model class describing the expected output
            shape. Passed to `llm.with_structured_output()` so the
            model's response is parsed and validated into an instance
            of this schema.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        schema: type[BaseModel],
    ) -> None:
        self.llm = llm
        self.schema = schema

    def call_structured(self, messages: list[tuple[str, str]]) -> BaseModel:
        """Invoke the LLM and parse its response into `self.schema`.

        Args:
            messages: Chat messages as (role, content) tuples, e.g.
                [("system", "..."), ("human", "...")], passed directly to
                the underlying chat model.

        Returns:
            An instance of `self.schema` populated from the model's
            structured response.
        """
        return self.llm.with_structured_output(self.schema).invoke(messages)

    @abstractmethod
    def analyse(self, *args: Any, **kwargs: Any) -> BaseInferenceResult:
        """Run the domain-specific analysis and return its result.

        Subclasses define their own concrete signature (specific
        positional/keyword arguments) and are responsible for building
        the messages, calling `call_structured()`, and mapping the
        resulting schema instance into a `BaseInferenceResult`.

        Returns:
            A `BaseInferenceResult` (or subclass) instance representing the
            outcome of the analysis.
        """
        pass
