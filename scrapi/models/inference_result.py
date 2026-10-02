from abc import ABC
from dataclasses import dataclass
from datetime import datetime
import uuid
from pydantic import BaseModel

from scrapi.inference.schemas import SearchSchema, SummarySchema


@dataclass
class BaseInferenceResult(ABC):
    """Every BaseSearchResult piped through an inference engine
    must yield an object of class BaseInferenceResult.

    Subclasses must declare the `structured_output` field.

    Attributes:
        id: Unique identifier for this inference result (auto-generated if not provided).
        pipeline_id: Unique identifier for the pipeline run, linking search results, inference results, and summary result.
        prompted_at: Timestamp at which the prompt was sent to the inference engine.
        system_prompt: System prompt supplied to the inference engine.
        task_prompt: Task-specific prompt supplied to the inference engine.
        structured_output: Structured output returned by the inference engine; shape is subclass-specific.
        result: Main field of `structured_output`.
    """
    prompted_at: datetime
    system_prompt: str
    task_prompt: str
    structured_output: BaseModel
    result: str
    id: str | None = None
    pipeline_id: str | None = None

    def __post_init__(self) -> None:
        if self.id is None:
            object.__setattr__(self, "id", uuid.uuid4().hex)


@dataclass
class SearchInferenceResult(BaseInferenceResult):
    """Inference result for a single search result analysis."""

    structured_output: SearchSchema


@dataclass
class SummaryInferenceResult(BaseInferenceResult):
    """Inference result for the final cross-source summary."""

    structured_output: SummarySchema
