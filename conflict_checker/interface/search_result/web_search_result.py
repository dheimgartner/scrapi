from dataclasses import asdict, dataclass
import json

from conflict_checker.interface.search_result.base_search_result import BaseSearchResult
import conflict_checker.interface.table_paths as tp
from conflict_checker.storage.database_storable import DatabaseStorable
from conflict_checker.renderer.markdown.mixins import WebSearchResultMarkdownMixin

@dataclass
class WebSearchResult(BaseSearchResult, WebSearchResultMarkdownMixin, DatabaseStorable):

    def get_table_path(self) -> tp.TablePath:
        return tp.CONFLICT_CHECKER_WEB_SEARCH_RESULTS

    def to_db_dict(self) -> dict:
        d = asdict(self)
        d["status"] = repr(d["status"])
        d["source"] = json.dumps(d["source"])
        return d