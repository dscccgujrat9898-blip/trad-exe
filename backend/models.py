from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class Quote(BaseModel):
    symbol: str
    price: float
    open: float
    high: float
    low: float
    prev_close: float
    change: float
    change_pct: float
    volume: int = 0


class Candle(BaseModel):
    ts: str
    open: float
    high: float
    low: float
    close: float
    volume: int = 0


class PerformanceSnapshot(BaseModel):
    daily_pct: float
    weekly_pct: float
    monthly_pct: float
    yearly_pct: float
    cagr_like_pct: float
    distance_from_52w_high_pct: float
    distance_from_52w_low_pct: float


class TrendReport(BaseModel):
    score: int
    bucket: Literal[
        "Strong Uptrend",
        "Uptrend",
        "Sideways",
        "Weak",
        "High Risk Momentum",
        "Potential Reversal",
    ]
    reasons: list[str]


class SeasonalityReport(BaseModel):
    best_months: list[str]
    weak_months: list[str]
    best_weekdays: list[str]
    weak_weekdays: list[str]
    monthly_matrix: dict[str, float]
    weekday_matrix: dict[str, float]


class OptionLeg(BaseModel):
    strike: float
    ce_ltp: float
    pe_ltp: float
    ce_oi: int
    pe_oi: int
    ce_iv: float
    pe_iv: float


class OptionsSummary(BaseModel):
    atm_strike: float
    pcr: float
    max_pain_estimate: float
    top_oi_strikes: list[float]
    legs: list[OptionLeg]


class CostEstimate(BaseModel):
    symbol: str
    side: Literal["BUY", "SELL"]
    product: Literal["CNC", "MIS", "NRML"]
    quantity: int
    price: float
    gross_value: float
    brokerage_estimate: float
    taxes_and_charges_estimate: float
    total_payable_estimate: float
    margin_required_estimate: float
    leverage_estimate: float
    stop_loss_price: float | None = None
    risk_amount: float | None = None


class FullReport(BaseModel):
    quote: Quote
    performance: PerformanceSnapshot
    trend: TrendReport
    seasonality: SeasonalityReport
    options: OptionsSummary | None = None
    investment_view: str
    intraday_view: str
    swing_view: str
    warnings: list[str] = Field(default_factory=list)
