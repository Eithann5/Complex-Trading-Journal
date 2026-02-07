# Mission 004 — Chart generation + caching + chart_url in feed

## Read first
- Read `AGENTS.md` and follow it strictly.
- Charts are static PNG, served from backend /static.
- No external upload (no S3 / no Supabase Storage) for MVP.

## Goal
Add backend chart generation/caching so `GET /api/alerts/feed` returns a working `chart_url` per trigger.

## Scope
Implement:
- `chart_service.ensure_trigger_chart(trigger)`:
  - Computes file path:
    - `data/charts/triggers/{symbol}/{trigger_id}_v1.png`
  - If file exists: return URL
  - If missing: generate and save PNG, then return URL
- Update feed endpoint to set `chart_url`
- Ensure directories are created if missing
- Never overwrite existing files

Do NOT implement:
- No OHLC fetching from external providers yet (unless you already have it locally)
- If OHLC is not available, generate a placeholder chart:
  - Use matplotlib to draw a simple title + key values
  - Must still produce a valid PNG

## Files to create/modify
- `backend/app/services/chart_service.py`
- `backend/app/api/alerts_feed.py` (include chart_url)
- `backend/app/config.py` (chart base dir if needed)

## Static URL rules
- Backend already serves `../data` at `/static`
- Therefore chart URL should be:
  - `/static/charts/triggers/{symbol}/{trigger_id}_v1.png`

## Acceptance criteria
1. Call `GET /api/alerts/feed` and confirm each item includes `chart_url`
2. Open a returned `chart_url` in browser; it must show an image
3. Call feed twice; second time must NOT regenerate images (should reuse existing)

## Deliverables
- Files changed/created
- Notes on where images are stored
