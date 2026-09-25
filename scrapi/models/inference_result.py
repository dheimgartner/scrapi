from abc import ABC
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import uuid
from pydantic import BaseModel

from scrapi.storage.storable import DatabaseStorable
from scrapi.storage import table_path as tp
from scrapi.inference.schemas import SearchSchema, SummarySchema
from scrapi.renderer.markdown import (
    InferenceResultMarkdownMixin,
    SearchInferenceResultMarkdownMixin,
    SummaryInferenceResultMarkdownMixin,
)


CONFLICT_CHECKER_SEARCH_INFERENCE_RESULTS = tp.TablePath(
    "dwhdata.finma.ch",
    "gbi_reporting",
    "gbi",
    "conflict_checker_search_inference_results",
)

CONFLICT_CHECKER_SUMMARY_INFERENCE_RESULTS = tp.TablePath(
    "dwhdata.finma.ch",
    "gbi_reporting",
    "gbi",
    "conflict_checker_summary_inference_results",
)


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


@dataclass
class SearchInferenceResult(BaseInferenceResult, SearchInferenceResultMarkdownMixin, DatabaseStorable):
    structured_output: SearchSchema

    def get_table_path(self) -> tp.TablePath:
        return CONFLICT_CHECKER_SEARCH_INFERENCE_RESULTS

    def to_db_dict(self) -> dict:
        d = asdict(self)
        d["structured_output"] = json.dumps(d["structured_output"])
        return d


@dataclass
class SummaryInferenceResult(BaseInferenceResult, SummaryInferenceResultMarkdownMixin, DatabaseStorable):
    structured_output: SummarySchema

    def get_table_path(self) -> tp.TablePath:
        return CONFLICT_CHECKER_SUMMARY_INFERENCE_RESULTS

    def to_db_dict(self) -> dict:
        d = asdict(self)
        d["structured_output"] = json.dumps(d["structured_output"])
        return d
