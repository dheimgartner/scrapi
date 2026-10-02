import logging
from datetime import datetime
from typing import Any

import pymupdf4llm

import scrapi.scraping.base as bs
from scrapi.models.search_result import FailedSearch, FileSearchResult, SuccessfulSearch


class FileScraper(bs.BaseScraper):
    """Read local files and convert them to Markdown for LLM consumption.

    Each path in ``query`` becomes one ``FileSearchResult``. Supports any
    format handled by PyMuPDF (PDF, DOCX, EPUB, …); tables and math are
    preserved as best-effort Markdown/Unicode text.
    """

    def _fetch_content(self, query: list[str]) -> list[FileSearchResult]:
        """Convert each file in ``query`` to a ``FileSearchResult``.

        Args:
            query: List of file paths to read.

        Returns:
            list[FileSearchResult]: One result per input path.
        """
        results = []
        for path in query:
            try:
                raw = pymupdf4llm.to_markdown(path)
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
