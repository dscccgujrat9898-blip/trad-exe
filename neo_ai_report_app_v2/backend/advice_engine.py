from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from .models import Candle, CostEstimate, FullReport, OptionsSummary, PerformanceSnapshot, Quote, SeasonalityReport, TrendReport


@dataclass
class AdviceEngine:
    def _df(self, candles: Sequence[Candle]) -> pd.DataFrame:
        df = pd.DataFrame([c.model_dump() for c in candles])
        df["ts"] = pd.to_datetime(df["ts"])
        df = df.sort_values("ts").reset_index(drop=True)
        return df

    def performance(self, candles: Sequence[Candle]) -> PerformanceSnapshot:
        df = self._df(candles)
        closes = df["close"].astype(float)
        last = closes.iloc[-1]

        def pct_from(days: int) -> float:
            if len(closes) <= days:
                base = closes.iloc[0]
            else:
                base = closes.iloc[-days - 1]
            return round((last / base - 1) * 100, 2) if base else 0.0

        rolling_252 = closes.tail(min(252, len(closes)))
        high_52 = rolling_252.max()
        low_52 = rolling_252.min()
        years = max(len(closes) / 252, 1e-6)
        cagr_like = ((last / closes.iloc[0]) ** (1 / years) - 1) * 100 if closes.iloc[0] else 0.0

        return PerformanceSnapshot(
            daily_pct=pct_from(1),
            weekly_pct=pct_from(5),
            monthly_pct=pct_from(21),
            yearly_pct=pct_from(252),
            cagr_like_pct=round(cagr_like, 2),
            distance_from_52w_high_pct=round((last / high_52 - 1) * 100, 2) if high_52 else 0.0,
            distance_from_52w_low_pct=round((last / low_52 - 1) * 100, 2) if low_52 else 0.0,
        )

    def trend(self, candles: Sequence[Candle], quote: Quote) -> TrendReport:
        df = self._df(candles)
        df["ema20"] = df["close"].ewm(span=20).mean()
        df["ema50"] = df["close"].ewm(span=50).mean()
        df["ret"] = df["close"].pct_change()
        df["vol_avg20"] = df["volume"].rolling(20).mean()
        latest = df.iloc[-1]
        score = 50
        reasons: list[str] = []

        if latest["close"] > latest["ema20"]:
            score += 10
            reasons.append("Price is above 20 EMA")
        else:
            score -= 10
            reasons.append("Price is below 20 EMA")

        if latest["close"] > latest["ema50"]:
            score += 15
            reasons.append("Price is above 50 EMA")
        else:
            score -= 15
            reasons.append("Price is below 50 EMA")

        recent_high = df["high"].tail(20).max()
        recent_low = df["low"].tail(20).min()
        if latest["close"] >= recent_high * 0.985:
            score += 10
            reasons.append("Price is near recent breakout zone")
        if latest["close"] <= recent_low * 1.015:
            score -= 8
            reasons.append("Price is near recent support/risk zone")

        if latest["volume"] > (latest["vol_avg20"] or 1) * 1.3:
            score += 8
            reasons.append("Volume is above 20-day average")

        volatility = df["ret"].tail(20).std() * np.sqrt(252) * 100
        if volatility > 45:
            score -= 8
            reasons.append("High volatility raises risk")
        elif volatility < 25:
            score += 5
            reasons.append("Moderate volatility is supportive")

        score = max(0, min(100, int(round(score))))

        if score >= 78:
            bucket = "Strong Uptrend"
        elif score >= 62:
            bucket = "Uptrend"
        elif score >= 48:
            bucket = "Sideways"
        elif score >= 35:
            bucket = "Weak"
        elif quote.change_pct > 2.5:
            bucket = "High Risk Momentum"
        else:
            bucket = "Potential Reversal"

        return TrendReport(score=score, bucket=bucket, reasons=reasons)

    def seasonality(self, candles: Sequence[Candle]) -> SeasonalityReport:
        df = self._df(candles)
        df["ret"] = df["close"].pct_change()
        df["month"] = df["ts"].dt.month_name().str[:3]
        df["weekday"] = df["ts"].dt.day_name().str[:3]

        monthly = (df.groupby("month")["ret"].mean() * 100).to_dict()
        weekday = (df.groupby("weekday")["ret"].mean() * 100).to_dict()

        month_rank = sorted(monthly.items(), key=lambda x: x[1], reverse=True)
        weekday_rank = sorted(weekday.items(), key=lambda x: x[1], reverse=True)

        return SeasonalityReport(
            best_months=[x[0] for x in month_rank[:3]],
            weak_months=[x[0] for x in month_rank[-3:]],
            best_weekdays=[x[0] for x in weekday_rank[:2]],
            weak_weekdays=[x[0] for x in weekday_rank[-2:]],
            monthly_matrix={k: round(v, 3) for k, v in monthly.items()},
            weekday_matrix={k: round(v, 3) for k, v in weekday.items()},
        )

    def views(self, performance: PerformanceSnapshot, trend: TrendReport, options: OptionsSummary | None) -> tuple[str, str, str, list[str]]:
        warnings: list[str] = []

        if trend.score >= 75 and performance.yearly_pct > 10:
            investment_view = "Structure looks strong for watchlist or staggered long-term accumulation. Prefer dips over chasing spikes."
        elif performance.yearly_pct < -10:
            investment_view = "Long-term structure is weak. Better for observation than fresh conviction-based investing."
        else:
            investment_view = "Neutral-to-selective investment posture. Use staggered entries and risk limits."

        if trend.bucket in {"Strong Uptrend", "Uptrend"} and performance.weekly_pct > 0:
            swing_view = "Momentum supports swing-trading setups if entries are near support or breakout confirmation."
        else:
            swing_view = "Swing setup is mixed. Wait for cleaner confirmation or stronger relative strength."

        if options:
            if options.pcr > 1.2:
                intraday_view = "Options positioning leans supportive, but confirm with price action before acting."
            elif options.pcr < 0.8:
                intraday_view = "Options positioning is cautious to bearish; avoid oversized long intraday positions."
            else:
                intraday_view = "Intraday bias is balanced; use key levels and strict stop-loss."
        else:
            intraday_view = "Intraday view depends on live price structure and volume confirmation."

        if abs(performance.daily_pct) > 4:
            warnings.append("Large one-day move can raise chase risk.")
        if trend.bucket == "High Risk Momentum":
            warnings.append("Momentum is strong but late entries can be risky.")
        if performance.distance_from_52w_high_pct > -2:
            warnings.append("The stock is close to its 52-week high zone; breakouts can fail without volume follow-through.")

        return investment_view, intraday_view, swing_view, warnings

    def quantity_cost(self, symbol: str, price: float, quantity: int, product: str, side: str, stop_loss_price: float | None = None) -> CostEstimate:
        gross = round(price * quantity, 2)
        brokerage = round(min(20.0, gross * 0.0003), 2) if product != "CNC" else 0.0
        charges = round(gross * 0.0012, 2)
        margin_pct = {
            "CNC": 1.0,
            "MIS": 0.2,
            "NRML": 0.35,
        }.get(product, 1.0)
        margin = round(gross * margin_pct, 2)
        leverage = round(gross / margin, 2) if margin else 1.0
        total_payable = round(margin + brokerage + charges, 2)
        risk_amount = None
        if stop_loss_price is not None:
            risk_amount = round(abs(price - stop_loss_price) * quantity, 2)

        return CostEstimate(
            symbol=symbol,
            side=side,
            product=product,
            quantity=quantity,
            price=price,
            gross_value=gross,
            brokerage_estimate=brokerage,
            taxes_and_charges_estimate=charges,
            total_payable_estimate=total_payable,
            margin_required_estimate=margin,
            leverage_estimate=leverage,
            stop_loss_price=stop_loss_price,
            risk_amount=risk_amount,
        )

    def full_report(self, quote: Quote, candles: Sequence[Candle], options: OptionsSummary | None) -> FullReport:
        perf = self.performance(candles)
        trend = self.trend(candles, quote)
        season = self.seasonality(candles)
        investment_view, intraday_view, swing_view, warnings = self.views(perf, trend, options)
        return FullReport(
            quote=quote,
            performance=perf,
            trend=trend,
            seasonality=season,
            options=options,
            investment_view=investment_view,
            intraday_view=intraday_view,
            swing_view=swing_view,
            warnings=warnings,
        )
