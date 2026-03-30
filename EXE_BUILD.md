# GitHub se EXE banane ke exact steps

## 1) GitHub repo banao
- GitHub open karo
- **New repository** par click karo
- koi bhi naam do
- **Create repository**

## 2) Files upload karo
- Is package ke andar jo files hain, sab repo ke root me upload karo
- Dhyan rahe `.github/workflows/build_windows_exe.yml` file bhi upload ho

## 3) API token paste karo
- `.env.example` ki copy banao
- uska naam `.env` rakho
- `UPSTOX_ACCESS_TOKEN=` ke aage apna token paste karo
- `DATA_MODE=live` hi rehne do

Example:
```env
APP_NAME=Neo AI Report App
DATA_MODE=live
UPSTOX_ACCESS_TOKEN=PASTE_YOUR_UPSTOX_ACCESS_TOKEN_HERE
UPSTOX_BASE_URL=https://api.upstox.com
DEFAULT_SYMBOLS=RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK,SBIN,ONGC,BHARTIARTL
```

## 4) EXE build karo
- GitHub repo me **Actions** tab kholo
- **Build Windows EXE** workflow select karo
- **Run workflow** dabao
- process complete hone do

## 5) EXE download karo
- same workflow run open karo
- neeche **Artifacts** section me jao
- `NeoAIReportApp-windows-exe` download karo
- zip ke andar `NeoAIReportApp.exe` milega

## Upstox token kahan se aayega
- Upstox Developer portal open karo
- apna developer app/token generate karo
- jo **Access Token** mile, use copy karo
- `.env` file me `UPSTOX_ACCESS_TOKEN=` ke aage paste karo

## Important
- `.env` ko public repo me commit mat karo
- `.env.example` repo me rehne do
- apna real token sirf local `.env` me rakho
