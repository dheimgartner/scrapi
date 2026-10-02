from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FinancialSnapshot:
    """Investor-relevant financial data for a single ticker fetched via yfinance.

    Attributes:
        ticker: Stock ticker symbol (e.g. "AAPL").
        fetched_at: Timestamp of the data fetch.
        name: Company name.
        sector: Business sector.
        industry: Industry classification.
        currency: Reporting currency.
        current_price: Latest traded price.
        previous_close: Previous session closing price.
        market_cap: Total market capitalisation.
        pe_ratio: Trailing price-to-earnings ratio.
        forward_pe: Forward price-to-earnings ratio.
        eps: Trailing twelve-month earnings per share.
        revenue: Trailing twelve-month total revenue.
        profit_margin: Net profit margin (0–1).
        dividend_yield: Annual dividend yield (0–1).
        beta: 5-year monthly beta vs. S&P 500.
        week_52_high: 52-week high price.
        week_52_low: 52-week low price.
        analyst_target_price: Median analyst 12-month price target.
        recommendation: Analyst consensus recommendation (e.g. "buy").
        info: Raw yfinance info dict for any fields not explicitly captured.
    """

    ticker: str
    fetched_at: datetime
    name: str | None = None
    sector: str | None = None
    industry: str | None = None
    currency: str | None = None
    current_price: float | None = None
    previous_close: float | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    forward_pe: float | None = None
    eps: float | None = None
    revenue: float | None = None
    profit_margin: float | None = None
    dividend_yield: float | None = None
    beta: float | None = None
    week_52_high: float | None = None
    week_52_low: float | None = None
    analyst_target_price: float | None = None
    recommendation: str | None = None
    info: dict = field(default_factory=dict)
