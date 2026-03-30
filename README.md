# Neo AI Report App - GitHub Upload Ready

Ye package GitHub par upload karke Windows `.exe` banane ke liye ready hai.

## Kya karna hai
1. Is folder ke saare files GitHub repo ke root me upload karo.
2. `.env.example` ko rename karke `.env` banao.
3. `.env` me apna Upstox token paste karo.
4. GitHub repo me **Actions** tab kholo.
5. **Build Windows EXE** workflow run karo.
6. Build complete hone ke baad artifact download karo.

## API key kahan se laani hai
Upstox Developer account me app/token generate karke **Access Token** lo.

Paste yahan karna hai:
- file: `.env`
- key: `UPSTOX_ACCESS_TOKEN=`

## `.env` example
```env
APP_NAME=Neo AI Report App
DATA_MODE=live
UPSTOX_ACCESS_TOKEN=PASTE_YOUR_UPSTOX_ACCESS_TOKEN_HERE
UPSTOX_BASE_URL=https://api.upstox.com
DEFAULT_SYMBOLS=RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK,SBIN,ONGC,BHARTIARTL
```

## Local run
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

## EXE build
Details: `EXE_BUILD.md`
