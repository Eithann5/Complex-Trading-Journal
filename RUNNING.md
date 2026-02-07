# Running The Project

## Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Supabase project + credentials
- (Optional for Mission 008) IBKR Client Portal Gateway running locally and authenticated

## 1) Backend setup
```powershell
cd D:\Projects\Complex-Trading-Journal\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend\.env` (example values):
```env
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY
SUPABASE_SCHEMA=public

IBKR_BASE_URL=https://localhost:5000
IBKR_ACCOUNT_ID=U18234408
IBKR_VERIFY_SSL=false
IBKR_SNAPSHOT_INTERVAL_SECONDS=300
```

Run backend:
```powershell
cd D:\Projects\Complex-Trading-Journal\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

## 2) Frontend setup
```powershell
cd D:\Projects\Complex-Trading-Journal\frontend
npm install
```

Create `frontend\.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ALERTS_POLL_MS=7000
```

Run frontend:
```powershell
cd D:\Projects\Complex-Trading-Journal\frontend
npm run dev
```

## 3) IBKR API
https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#gw-step-one

cd D:\Projects\ibkr-api
bin\run.bat root\conf.yaml