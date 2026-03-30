from __future__ import annotations

import math
import random
from datetime import date, datetime, timedelta
from typing import Iterable

import httpx

from .config import DATA_MODE, UPSTOX_ACCESS_TOKEN, UPSTOX_BASE_URL
from .models import Candle, OptionLeg, OptionsSummary, Quote


class MarketDataError(Exception):
    pass


class MarketDataService:
    def __init__(self) -> None:
        self.client = httpx.Client(timeout=20.0)

    def get_quote(self, symbol: str) -> Quote:
        if DATA_MODE == "live" and UPSTOX_ACCESS_TOKEN:
            live_quote = self._get_upstox_quote(symbol)
            if live_quote:
                return live_quote
        return self._demo_quote(symbol)

    def get_history(self, symbol: str, years: int = 2) -> list[Candle]:
        if DATA_MODE == "live" and UPSTOX_ACCESS_TOKEN:
            live_candles = self._get_upstox_history(symbol)
            if live_candles:
                return live_candles
        return self._demo_history(symbol, years=years)

    def get_options_summary(self, symbol: str, spot_price: float) -> OptionsSummary:
        return self._demo_options_summary(symbol, spot_price)

    def _upstox_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}",
        }

    def _get_upstox_quote(self, symbol: str) -> Quote | None:
        # Instrument mapping is broker-specific; this starter expects the user to replace
        # symbol translation for their own account universe.
        instrument_key = f"NSE_EQ|{symbol}"
        url = f"{UPSTOX_BASE_URL}/v2/market-quote/quotes"
        try:
            response = self.client.get(url, headers=self._upstox_headers(), params={"instrument_key": instrument_key})
            response.raise_for_status()
            payload = response.json()
            data = (payload.get("data") or {}).get(instrument_key)
            if not data:
                return None
            last_price = float(data.get("last_price", 0))
            ohlc = data.get("ohlc") or {}
            prev_close = float(ohlc.get("close", last_price))
            change = last_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            volume = int(data.get("volume", 0) or 0)
            return Quote(
                symbol=symbol.upper(),
                price=last_price,
                open=float(ohlc.get("open", last_price)),
                high=float(ohlc.get("high", last_price)),
                low=float(ohlc.get("low", last_price)),
                prev_close=prev_close,
                change=change,
                change_pct=change_pct,
                volume=volume,
            )
        except Exception:
            return None

    def _get_upstox_history(self, symbol: str) -> list[Candle] | None:
        instrument_key = f"NSE_EQ|{symbol}"
        end_date = date.today().isoformat()
        start_date = (date.today() - timedelta(days=730)).isoformat()
        url = f"{UPSTOX_BASE_URL}/v3/historical-candle/{instrument_key}/days/1/{end_date}/{start_date}"
        try:
            response = self.client.get(url, headers=self._upstox_headers())
            response.raise_for_status()
            payload = response.json()
            candles = ((payload.get("data") or {}).get("candles") or [])
            parsed = []
            for item in candles:
                # expected [timestamp, open, high, low, close, volume, oi]
                parsed.append(
                    Candle(
                        ts=str(item[0]),
                        open=float(item[1]),
                        high=float(item[2]),
                        low=float(item[3]),
                        close=float(item[4]),
                        volume=int(item[5] or 0),
                    )
                )
            return parsed if parsed else None
        except Exception:
            return None

    def _demo_quote(self, symbol: str) -> Quote:
        base = self._symbol_seed_price(symbol)
        prev_close = round(base * random.uniform(0.985, 1.015), 2)
        price = round(prev_close * random.uniform(0.985, 1.02), 2)
        day_high = round(max(price, prev_close) * random.uniform(1.0, 1.015), 2)
        day_low = round(min(price, prev_close) * random.uniform(0.985, 1.0), 2)
        day_open = round(random.uniform(day_low, day_high), 2)
        change = round(price - prev_close, 2)
        pct = round((change / prev_close) * 100, 2)
        volume = int(abs(hash(symbol)) % 4_000_000 + 150_000)
        return Quote(
            symbol=symbol.upper(),
            price=price,
            open=day_open,
            high=day_high,
            low=day_low,
            prev_close=prev_close,
            change=change,
            change_pct=pct,
            volume=volume,
        )

    def _demo_history(self, symbol: str, years: int = 2) -> list[Candle]:
        seed = abs(hash(symbol)) % 10_000
        random.seed(seed)
        start = date.today() - timedelta(days=365 * years)
        price = self._symbol_seed_price(symbol)
        candles: list[Candle] = []
        current = start
        while current <= date.today():
            if current.weekday() >= 5:
                current += timedelta(days=1)
                continue
            month_bias = math.sin((current.month / 12) * 2 * math.pi) * 0.002
            weekday_bias = {0: 0.0010, 1: 0.0004, 2: -0.0002, 3: 0.0003, 4: -0.0006}.get(current.weekday(), 0)
            drift = 0.0005 + month_bias + weekday_bias
            shock = random.gauss(0, 0.015)
            ret = drift + shock
            open_p = price
            close_p = max(5.0, price * (1 + ret))
            high_p = max(open_p, close_p) * (1 + abs(random.gauss(0, 0.006)))
            low_p = min(open_p, close_p) * (1 - abs(random.gauss(0, 0.006)))
            vol = int(200_000 + abs(random.gauss(0, 1)) * 600_000)
            candles.append(
                Candle(
                    ts=datetime.combine(current, datetime.min.time()).isoformat(),
                    open=round(open_p, 2),
                    high=round(high_p, 2),
                    low=round(low_p, 2),
                    close=round(close_p, 2),
                    volume=vol,
                )
            )
            price = close_p
            current += timedelta(days=1)
        return candles

    def _demo_options_summary(self, symbol: str, spot_price: float) -> OptionsSummary:
        strike_step = 50 if spot_price < 3000 else 100
        atm = round(spot_price / strike_step) * strike_step
        legs: list[OptionLeg] = []
        total_put_oi = 0
        total_call_oi = 0
        oi_map = {}
        for offset in range(-3, 4):
            strike = atm + offset * strike_step
            distance = abs(strike - spot_price) / max(spot_price, 1)
            ce_ltp = max(2.0, round(max(spot_price - strike, 0) * 0.35 + max(1, 40 * (1 - distance)), 2))
            pe_ltp = max(2.0, round(max(strike - spot_price, 0) * 0.35 + max(1, 38 * (1 - distance)), 2))
            ce_oi = int(100_000 * (1.5 - min(distance * 8, 1.2)) + random.randint(0, 50_000))
            pe_oi = int(95_000 * (1.5 - min(distance * 8, 1.2)) + random.randint(0, 50_000))
            total_call_oi += ce_oi
            total_put_oi += pe_oi
            oi_map[strike] = ce_oi + pe_oi
            legs.append(
                OptionLeg(
                    strike=strike,
                    ce_ltp=ce_ltp,
                    pe_ltp=pe_ltp,
                    ce_oi=ce_oi,
                    pe_oi=pe_oi,
                    ce_iv=round(12 + distance * 120, 2),
                    pe_iv=round(13 + distance * 115, 2),
                )
            )
        sorted_oi = sorted(oi_map.items(), key=lambda x: x[1], reverse=True)
        pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi else 1.0
        return OptionsSummary(
            atm_strike=float(atm),
            pcr=pcr,
            max_pain_estimate=float(sorted_oi[0][0]) if sorted_oi else float(atm),
            top_oi_strikes=[float(x[0]) for x in sorted_oi[:3]],
            legs=legs,
        )

    @staticmethod
    def _symbol_seed_price(symbol: str) -> float:
        symbol = symbol.upper()
        anchors = {
            "RELIANCE": 2900,
            "TCS": 4200,
            "INFY": 1900,
            "HDFCBANK": 1700,
            "ICICIBANK": 1300,
            "SBIN": 820,
            "ONGC": 290,
            "BHARTIARTL": 1500,
            "NIFTY": 23000,
            "BANKNIFTY": 51000,
        }
        return float(anchors.get(symbol, 150 + (abs(hash(symbol)) % 3000)))
