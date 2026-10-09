import os
import re
import urllib.parse
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine, text
from tabulate import tabulate

import scrapi.scraping.base as bs
from scrapi.models.search_result import SQLSearchResult, SuccessfulSearch


class SQLScraper(bs.BaseScraper):
    """Execute SQL queries and return result sets via SQLAlchemy.

    Each instance is bound to a single database via ``connection_string``.
    Passwords (or other secrets) can be injected using ``${ENV_VAR}``
    placeholders in the connection string, e.g.::

        postgresql://user:${DB_PASSWORD}@host/db

    The placeholder is resolved from the environment at instantiation time.

    Args:
        connection_string: SQLAlchemy connection URL. May contain
            ``${VAR}`` placeholders resolved from environment variables.
    """

    def __init__(self, connection_string: str) -> None:
        resolved = _resolve_env_vars(connection_string)
        self._engine = create_engine(resolved)

    def _fetch_content(
        self, query: str, rows_as_results: bool = False
    ) -> list[SQLSearchResult]:
        """Execute ``query`` and return the result set.

        Args:
            query: SQL query string to execute.
            rows_as_results: When ``True``, each row becomes an individual
                ``SQLSearchResult``. When ``False`` (default), the entire
                result set is a single result.

        Returns:
            One ``SQLSearchResult`` per row if ``rows_as_results`` is
            ``True``, otherwise a single ``SQLSearchResult`` with all rows.
        """
        with self._engine.connect() as conn:
            result = conn.execute(text(query))
            rows = [dict(row._mapping) for row in result]

        if not rows:
            return []

        if rows_as_results:
            return [
                self._make_result(query, [row], row_index=i)
                for i, row in enumerate(rows)
            ]
        return [self._make_result(query, rows)]

    def _make_result(
        self,
        query: str,
        rows: list[dict],
        row_index: int | None = None,
    ) -> SQLSearchResult:
        source: dict[str, str] = {"query": query}
        if row_index is not None:
            source["row"] = str(row_index)
        return SQLSearchResult(
            scraper_repr=repr(self),
            status=SuccessfulSearch(status=200),
            fetched_at=datetime.now(),
            source=source,
            raw_content=rows,
            ai_content=self.convert_to_ai_content(rows),
        )

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        """Render rows as a GitHub-flavoured Markdown table.

        Args:
            raw_content: A ``list[dict]`` where each dict is one row.

        Returns:
            Markdown table string, or ``"(no rows)"`` for an empty result.
        """
        return tabulate(raw_content, headers="keys", tablefmt="github")


def _resolve_env_vars(s: str) -> str:
    """Substitute ``${VAR}`` placeholders in ``s`` from the environment.

    Substituted values are URL-encoded so that special characters in
    passwords (e.g. ``@``, ``#``) do not break URL parsing.

    Raises:
        ValueError: If a referenced variable is not set.
    """
    def _sub(m: re.Match) -> str:
        var = m.group(1)
        val = os.environ.get(var)
        if val is None:
            raise ValueError(
                f"Environment variable '{var}' referenced in connection string is not set"
            )
        return urllib.parse.quote(val, safe="")

    return re.sub(r"\$\{([^}]+)\}", _sub, s)
