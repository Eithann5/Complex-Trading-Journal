# AGENTS.md — Complex Trading Journal (Codex Rules)

## Golden rules (do not violate)
- Repo is a monorepo with two separate apps:
  - /backend = Python FastAPI
  - /frontend = Next.js + MUI Core (FREE, MIT)
- Frontend NEVER talks directly to Supabase or IBKR. Only to backend API.
- IBKR integration is READ-ONLY. Do not add order endpoints or trading actions.
- Alerts feed shows charts INLINE (no click-to-view).
- Alert trigger disappears from feed ONLY when linked to a position (not when viewed).
- Use UTC everywhere in DB/backend; UI may display local time.

## Alerts source table (Supabase)
Read from table: alerts_triggers
Columns used:
- id (trigger_id, UUID)  <-- primary key for trigger events
- alert_id
- symbol
- alert_type
- condition (JSON text)
- triggered_at (timestamptz UTC)
- price
- message
- snapshot (JSON text)

## New Supabase tables we will add
- position_journal
- positions_snapshot
- trigger_position_links
- position_tags

## Chart generation (static PNG)
- One chart per trigger event.
- Chart key: trigger_id (alerts_triggers.id)
- Path: data/charts/triggers/{symbol}/{trigger_id}_v1.png
- Never overwrite. If needed later: _v2, _v3, etc.
- Served by backend at /static/... (no external uploads for MVP)

## Backend API (must be stable)
- GET  /api/health
- GET  /api/alerts/feed        (returns UNLINKED triggers + chart_url)
- POST /api/triggers/{trigger_id}/link
- GET  /api/positions/open
- PATCH /api/positions/{position_id}
- POST /api/positions/{position_id}/tags
- DELETE /api/positions/{position_id}/tags/{tag_id}

## UI pages
- /alerts    (feed with search + polling every ~7 seconds)
- /positions (open positions + drawer editing)
