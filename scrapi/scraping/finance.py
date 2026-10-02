import logging
from datetime import datetime
from typing import Any

import yfinance as yf

import scrapi.scraping.base as bs
from scrapi.models.financial_snapshot import FinancialSnapshot
from scrapi.models.search_result import FailedSearch, FinanceSearchResult, SuccessfulSearch


class FinanceScraper(bs.BaseScraper):
    """Fetch investor-relevant financial data for a list of ticker symbols via yfinance.

    Each ticker produces one ``FinanceSearchResult`` whose ``raw_content`` is a
    ``FinancialSnapshot`` and whose ``ai_content`` is a Markdown rendering of it.
    """

    def _fetch_content(self, query: list[str]) -> list[FinanceSearchResult]:
        """Fetch financial snapshots for each ticker in ``query``.

        Args:
            query: List of ticker symbols (e.g. ``["AAPL", "MSFT"]``).

        Returns:
            One ``FinanceSearchResult`` per ticker.
        """
        return [self._fetch_one(ticker) for ticker in query]

    def _fetch_one(self, ticker: str) -> FinanceSearchResult:
        try:
            info = yf.Ticker(ticker).info
            snapshot = FinancialSnapshot(
                ticker=ticker,
                fetched_at=datetime.now(),
                name=info.get("longName"),
                sector=info.get("sector"),
                industry=info.get("industry"),
                currency=info.get("currency"),
                current_price=info.get("currentPrice"),
                previous_close=info.get("previousClose"),
                market_cap=info.get("marketCap"),
                pe_ratio=info.get("trailingPE"),
                forward_pe=info.get("forwardPE"),
                eps=info.get("trailingEps"),
                revenue=info.get("totalRevenue"),
                profit_margin=info.get("profitMargins"),
                dividend_yield=info.get("dividendYield"),
                beta=info.get("beta"),
                week_52_high=info.get("fiftyTwoWeekHigh"),
                week_52_low=info.get("fiftyTwoWeekLow"),
                analyst_target_price=info.get("targetMeanPrice"),
                recommendation=info.get("recommendationKey"),
                info=info,
            )
            status = SuccessfulSearch(status=200)
        except Exception as e:
            logging.warning("FinanceScraper failed for %s: %s", ticker, e)
            snapshot = FinancialSnapshot(ticker=ticker, fetched_at=datetime.now())
            status = FailedSearch(status=0, message=str(e), error=e)

        return FinanceSearchResult(
            scraper_repr=repr(self),
            status=status,
            fetched_at=datetime.now(),
            source={"ticker": ticker},
            raw_content=snapshot,
            ai_content=self.convert_to_ai_content(snapshot),
        )

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        """Render a ``FinancialSnapshot`` as a Markdown string.

        Args:
            raw_content: A ``FinancialSnapshot`` instance.

        Returns:
            Markdown-formatted string suitable for LLM consumption.
        """
        s: FinancialSnapshot = raw_content

        def fmt_float(v: float | None, decimals: int = 2) -> str:
            return f"{v:.{decimals}f}" if v is not None else "n/a"

        def fmt_large(v: float | None) -> str:
            if v is None:
                return "n/a"
            if v >= 1e12:
                return f"{v / 1e12:.2f}T"
            if v >= 1e9:
                return f"{v / 1e9:.2f}B"
            if v >= 1e6:
                return f"{v / 1e6:.2f}M"
            return str(v)

        def fmt_pct(v: float | None) -> str:
            return f"{v * 100:.2f}%" if v is not None else "n/a"

        lines = [
            f"# {s.name or s.ticker} ({s.ticker})",
            "",
            f"**Sector:** {s.sector or 'n/a'}  ",
            f"**Industry:** {s.industry or 'n/a'}  ",
            f"**Currency:** {s.currency or 'n/a'}  ",
            f"**Fetched at:** {s.fetched_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Price",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Current price | {fmt_float(s.current_price)} |",
            f"| Previous close | {fmt_float(s.previous_close)} |",
            f"| 52-week high | {fmt_float(s.week_52_high)} |",
            f"| 52-week low | {fmt_float(s.week_52_low)} |",
            "",
            "## Valuation & Fundamentals",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Market cap | {fmt_large(s.market_cap)} |",
            f"| Trailing P/E | {fmt_float(s.pe_ratio)} |",
            f"| Forward P/E | {fmt_float(s.forward_pe)} |",
            f"| EPS (TTM) | {fmt_float(s.eps)} |",
            f"| Revenue (TTM) | {fmt_large(s.revenue)} |",
            f"| Profit margin | {fmt_pct(s.profit_margin)} |",
            "",
            "## Other",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Dividend yield | {fmt_pct(s.dividend_yield)} |",
            f"| Beta | {fmt_float(s.beta)} |",
            f"| Analyst target price | {fmt_float(s.analyst_target_price)} |",
            f"| Recommendation | {s.recommendation or 'n/a'} |",
        ]

        return "\n".join(lines)
