from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .advice_engine import AdviceEngine
from .config import APP_NAME, DEFAULT_SYMBOLS
from .market_data import MarketDataService

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

data_service = MarketDataService()
engine = AdviceEngine()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": APP_NAME, "symbols": DEFAULT_SYMBOLS})


@app.get("/api/watchlist")
def watchlist(symbols: str | None = None):
    symbol_list = [s.strip().upper() for s in (symbols.split(",") if symbols else DEFAULT_SYMBOLS) if s.strip()]
    rows = []
    for symbol in symbol_list:
        quote = data_service.get_quote(symbol)
        candles = data_service.get_history(symbol)
        perf = engine.performance(candles)
        trend = engine.trend(candles, quote)
        rows.append({
            "symbol": symbol,
            "price": quote.price,
            "change_pct": quote.change_pct,
            "weekly_pct": perf.weekly_pct,
            "monthly_pct": perf.monthly_pct,
            "yearly_pct": perf.yearly_pct,
            "trend_score": trend.score,
            "trend_bucket": trend.bucket,
        })
    rows.sort(key=lambda x: (x["trend_score"], x["weekly_pct"]), reverse=True)
    return {"items": rows}


@app.get("/api/quote/{symbol}")
def quote(symbol: str):
    return data_service.get_quote(symbol.upper())


@app.get("/api/report/{symbol}")
def report(symbol: str):
    symbol = symbol.upper()
    quote_data = data_service.get_quote(symbol)
    candles = data_service.get_history(symbol)
    if not candles:
        raise HTTPException(status_code=404, detail="No candle history available")
    options = data_service.get_options_summary(symbol, quote_data.price)
    return engine.full_report(quote_data, candles, options)


@app.get("/api/calc/{symbol}")
def calc(
    symbol: str,
    quantity: int = Query(1, ge=1),
    product: str = Query("MIS"),
    side: str = Query("BUY"),
    stop_loss_price: float | None = Query(None),
):
    quote_data = data_service.get_quote(symbol.upper())
    return engine.quantity_cost(symbol.upper(), quote_data.price, quantity, product.upper(), side.upper(), stop_loss_price)
