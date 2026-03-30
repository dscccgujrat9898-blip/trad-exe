# Architecture

## Backend modules
- `backend/app.py`: FastAPI routes and HTML serving
- `backend/market_data.py`: market data adapter layer with demo fallback
- `backend/advice_engine.py`: analytics, trend score, seasonality, and cost estimation
- `backend/models.py`: Pydantic response models
- `backend/config.py`: environment settings

## API endpoints
- `GET /` dashboard
- `GET /api/watchlist` ranked watchlist
- `GET /api/quote/{symbol}` quote snapshot
- `GET /api/report/{symbol}` full AI-style report
- `GET /api/calc/{symbol}` quantity cost estimate

## Future endpoints to add
- `/api/option-chain/{symbol}` full strike grid
- `/api/margin/live/{symbol}` broker-based margin call
- `/api/backtest`
- `/api/alerts`
- `/api/export/pdf/{symbol}`

## Scoring logic
Trend score is rules-based and considers:
- close vs EMA20
- close vs EMA50
- breakout proximity
- volume vs 20-day average
- volatility penalty

Recommendation buckets:
- Strong Uptrend
- Uptrend
- Sideways
- Weak
- High Risk Momentum
- Potential Reversal
