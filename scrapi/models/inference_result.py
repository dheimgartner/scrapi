from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
import uuid
from pydantic import BaseModel

if TYPE_CHECKING:
    from scrapi.inference.schemas import SearchSchema, SummarySchema


@dataclass
class BaseInferenceResult:
    prompted_at: datetime
    system_prompt: str
    task_prompt: str
    structured_output: BaseModel
    result: str | None = None
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
