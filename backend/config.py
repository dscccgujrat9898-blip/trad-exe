from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    candidates = []

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / ".env")

    candidates.append(Path.cwd() / ".env")
    candidates.append(Path(__file__).resolve().parents[1] / ".env")

    for env_file in candidates:
        if env_file.exists():
            load_dotenv(env_file, override=True)
            break
    else:
        load_dotenv(override=True)


_load_env()

APP_NAME = os.getenv("APP_NAME", "Neo AI Report App")
DATA_MODE = os.getenv("DATA_MODE", "demo").lower()
UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN", "")
UPSTOX_BASE_URL = os.getenv("UPSTOX_BASE_URL", "https://api.upstox.com")
DEFAULT_SYMBOLS = [
    s.strip().upper()
    for s in os.getenv(
        "DEFAULT_SYMBOLS",
        "RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK,SBIN,ONGC,BHARTIARTL",
    ).split(",")
    if s.strip()
]
