from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
import uuid

from conflict_checker.renderer.markdown.mixins import InferenceResultMarkdownMixin


@dataclass
class BaseInferenceResult(ABC, InferenceResultMarkdownMixin):
    """Every BaseSearchResult piped through an inference engine
    must yield an object of class BaseInferenceResult

    Subclasses must declare the `structured_output` field.

    Attributes:
        id: Unique identifier for this inference result (auto-generated if not provided).
        pipeline_id: Unique identifier for the pipeline run, linking search results, inference results, and summary result.
        prompted_at: Timestamp at which the prompt was sent to the inference engine.
        system_prompt: System prompt supplied to the inference engine.
        task_prompt: Task-specific prompt supplied to the inference engine.
        structured_output: Dict structured output returned by the inference engine; shape is subclass-specific.
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