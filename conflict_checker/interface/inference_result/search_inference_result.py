from dataclasses import asdict, dataclass
import json

from conflict_checker.interface.inference_result.base_inference_result import BaseInferenceResult
from conflict_checker.ai.inference.search_schema import SearchSchema
from conflict_checker.storage.database_storable import DatabaseStorable
from conflict_checker.renderer.markdown.mixins import SearchInferenceResultMarkdownMixin
import conflict_checker.interface.table_paths as tp


@dataclass
class SearchInferenceResult(BaseInferenceResult, SearchInferenceResultMarkdownMixin, DatabaseStorable):
    structured_output: SearchSchema

    def get_table_path(self) -> tp.TablePath:
        return tp.CONFLICT_CHECKER_SEARCH_INFERENCE_RESULTS

    def to_db_dict(self) -> dict:
        d = asdict(self)
        d["structured_output"] = json.dumps(d["structured_output"])
        return d