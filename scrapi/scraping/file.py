import glob
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pymupdf4llm
from markitdown import MarkItDown

import scrapi.scraping.base as bs
from scrapi.models.search_result import FailedSearch, FileSearchResult, SuccessfulSearch


class FileScraper(bs.BaseScraper):
    """Read local files and convert them to Markdown for LLM consumption.

    Each entry in ``query`` may be a literal path or a glob pattern; ``~`` is
    expanded. PDF files are processed via PyMuPDF for faithful table and math
    rendering; all other formats are handled by MarkItDown.
    """

    def _fetch_content(self, query: list[str]) -> list[FileSearchResult]:
        paths: list[str] = []
        for entry in query:
            expanded = Path(entry).expanduser()
            matches = glob.glob(str(expanded), recursive=True)
            if matches:
                paths.extend(sorted(matches))
            else:
                paths.append(str(expanded))

        results = []
        for path in paths:
            try:
                if Path(path).suffix.lower() == ".pdf":
                    raw = pymupdf4llm.to_markdown(path)
                else:
                    raw = MarkItDown().convert(path).text_content
                status = SuccessfulSearch(status=200)
            except Exception as e:
                logging.warning("FileScraper failed to read %s: %s", path, e)
                raw = ""
                status = FailedSearch(status=0, message=str(e), error=e)
            results.append(
                FileSearchResult(
                    scraper_repr=repr(self),
                    status=status,
                    fetched_at=datetime.now(),
                    source={"path": path},
                    raw_content=raw,
                    ai_content=self.convert_to_ai_content(raw),
                )
            )
        return results

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return raw_content
