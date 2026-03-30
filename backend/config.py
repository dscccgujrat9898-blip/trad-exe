from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Neo AI Report App")
DATA_MODE = os.getenv("DATA_MODE", "live").lower()
UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN", "")
UPSTOX_BASE_URL = os.getenv("UPSTOX_BASE_URL", "https://api.upstox.com")
DEFAULT_SYMBOLS = [s.strip().upper() for s in os.getenv("DEFAULT_SYMBOLS", "RELIANCE,TCS,INFY").split(",") if s.strip()]
