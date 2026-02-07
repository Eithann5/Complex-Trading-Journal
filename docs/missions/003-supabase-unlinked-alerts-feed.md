# Mission 003 — Supabase: fetch unlinked triggers for Alerts Feed

## Read first
- Read `AGENTS.md` and follow it strictly.
- Alerts source table is `alerts_triggers`.
- Feed returns triggers that have NO rows in `trigger_position_links`.

## Goal
Implement backend Supabase service + API endpoint:
- `GET /api/alerts/feed`
that returns unlinked triggers from Supabase.

## Scope
Implement:
- Supabase client init (env vars)
- Query `alerts_triggers`
- Filter out triggers linked in `trigger_position_links`
- Support filters:
  - `limit` (default 20)
  - `cursor` (pagination)
  - `q` (search by symbol or alert_type)
  - `symbol`
  - `alert_type`
- Parse `condition` and `snapshot` JSON text into objects
- Return newest first by `triggered_at desc`, tie-break by `id desc`

Do NOT implement:
- No chart generation yet (chart_url can be null or placeholder)
- No linking endpoint yet
- No IBKR work

## Required env vars (backend/.env example)
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` (or anon key if enough for read)
- Optional: `SUPABASE_SCHEMA` if needed

## Files to create/modify
- `backend/app/config.py` (add supabase env vars)
- `backend/app/services/supabase_service.py`
- `backend/app/api/alerts_feed.py`
- `backend/app/schemas/alerts.py`
- `backend/app/main.py` (include router)

## API response shape (per item)
Return JSON array of:
- `trigger_id` (alerts_triggers.id)
- `alert_id`
- `symbol`
- `alert_type`
- `triggered_at_utc`
- `price`
- `message`
- `condition` (object)
- `snapshot` (object)
- `chart_url` (null for now)

## Pagination (cursor)
Implement cursor using `(triggered_at, id)`:
- Request provides `cursor` as `"2026-02-06T16:35:00Z|0a711bfa-..."`
- Next page returns items strictly older than that tuple:
  - `(triggered_at < cursor_time) OR (triggered_at = cursor_time AND id < cursor_id)`

## Acceptance criteria
1. With env vars set, run backend and call:
   - `GET http://localhost:8000/api/alerts/feed?limit=20`
2. Response:
   - sorted newest first
   - each item has parsed JSON objects for condition/snapshot
3. Search:
   - `q=CVCO` matches symbol
   - `q=sma_touch` matches alert_type
4. Filters:
   - `symbol=CVCO` filters correctly
   - `alert_type=sma_touch` filters correctly

## Deliverables
- List of files changed/created
- How to set env vars
- Example curl calls
