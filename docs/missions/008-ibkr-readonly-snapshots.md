# Mission 008 — IBKR read-only integration + positions_snapshot + journal sync

## Read first
- Read `AGENTS.md` and follow it strictly.
- IBKR must remain read-only.

## Goal
Integrate IBKR CP Web API (via local gateway) in backend to:
- periodically fetch open positions
- store snapshots in Supabase (`positions_snapshot`)
- sync `position_journal` open positions using snapshots

## Scope
Implement:
1) Supabase table:
   - `positions_snapshot` (per PLAN.md)
2) Backend services:
   - `ibkr_service.py` to call CP Web API for positions
   - `snapshot_service.py` scheduler job every N minutes
3) Sync logic:
   - For each ticker in IB positions:
     - ensure an open `position_journal` exists
   - Optionally mark positions closed when they disappear (can be deferred)

Do NOT implement:
- No trading endpoints
- No order placement
- No WebSockets
- No historical PnL yet unless easy

## Acceptance criteria
- When gateway is running and authenticated:
  - backend fetches positions successfully
  - inserts snapshot rows
  - open positions appear in `GET /api/positions/open` with latest snapshot enrichment (optional)
- If IB gateway is down:
  - system still runs, and positions page can show last known info (optional)

## Deliverables
- Env var docs for gateway URL/port
- Files changed/created
- How to run snapshot job locally
