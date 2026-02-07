# Mission 001 — Backend skeleton (FastAPI) + static file serving

## Read first
- Read `AGENTS.md` and follow it strictly.
- This mission must NOT implement Supabase or IBKR yet.

## Goal
Create the FastAPI backend skeleton and verify:
- `/api/health` works
- `/static` serves files from `../data`

## Scope
Implement:
- `backend/` project scaffolding (FastAPI)
- `GET /api/health`
- Mount static directory: repo-root `/data` served at `/static`
- Basic config via environment variables
- Basic CORS setup for local dev (frontend at localhost:3000)

Do NOT implement:
- No Supabase queries
- No IBKR integration
- No chart generation logic (only static serving)

## Files to create
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/api/health.py`
- `backend/app/api/__init__.py`
- `backend/app/services/__init__.py` (empty ok)
- `backend/app/schemas/__init__.py` (empty ok)

## Implementation notes
- Use FastAPI + uvicorn.
- Mount static route:
  - Backend working dir is `backend/`
  - Static dir should point to `../data`
- Add CORS middleware allowing `http://localhost:3000` for dev.
- Health endpoint returns JSON: `{ "ok": true }`.

## Acceptance criteria
1. Run backend:
   - `cd backend`
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload --port 8000`
2. Verify:
   - `GET http://localhost:8000/api/health` returns `{ "ok": true }`
3. Static serving test:
   - Create a test file: `data/test.txt` (at repo root)
   - `GET http://localhost:8000/static/test.txt` returns the file contents

## Deliverables
- List of created/modified files
- Commands to run locally
