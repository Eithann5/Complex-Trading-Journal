# Mission 008 — IBKR read-only integration + position snapshots

## Read first
- Read AGENTS.md and follow it strictly.
- IBKR integration is **READ-ONLY**.
- Do NOT place trades, submit orders, or modify the account in any way.
- This mission focuses on **positions visibility and journaling**, not automation.

---

## Goal
Integrate Interactive Brokers **Client Portal Web API (CP Web API)** into the backend in a safe,
read-only manner in order to:

- fetch current open positions from IBKR
- store periodic snapshots of those positions
- synchronize them with `position_journal`
- expose enriched open positions to the frontend

This mission assumes the Client Portal Gateway is already running and authenticated locally.

---

## Prerequisites (must already be true)
- Client Portal Gateway is running locally
- User is logged in via https://localhost:5000
- The following endpoint works in a browser:

```
GET https://localhost:5000/v1/api/portfolio/U18234408/positions/0
```

If this endpoint does not return JSON, STOP and fix authentication before coding.

---

## Environment variables

The backend must read these from environment variables:

- `IBKR_BASE_URL=https://localhost:5000`
- `IBKR_ACCOUNT_ID=U18234408`
- `IBKR_VERIFY_SSL=false`  
  (required for localhost self-signed certificate)
- `IBKR_SNAPSHOT_INTERVAL_SECONDS=300`

---

## IBKR endpoints (READ-ONLY)

### Authentication / health check (optional)
```
GET /v1/api/iserver/accounts
```

### Fetch positions (core)
```
GET /v1/api/portfolio/{IBKR_ACCOUNT_ID}/positions/{page}
```

---

## IBKR position response mapping

- `ticker` ← `contractDesc`
- `quantity` ← `position`
- `avg_cost` ← `avgCost` (fallback `avgPrice`)
- `market_price` ← `mktPrice`
- `unrealized_pnl` ← `unrealizedPnl`
- `currency` ← `currency`
- `raw` ← full JSON
- `snapshot_time_utc` ← now (UTC)

---

## Sync rules with position_journal

- Ensure one OPEN position per IBKR ticker
- Create missing positions automatically
- Do NOT auto-close missing tickers yet

---

## Backend services

Implement:
- `ibkr_service.py`
- `snapshot_service.py`

Add manual trigger:
```
POST /api/ibkr/snapshot/run
```

---

## Frontend exposure

`GET /api/positions/open` must return latest snapshot per ticker
(CURRENT price from `mktPrice`).

---

## Non-goals

- No trading
- No orders
- No automation
- No WebSockets

---

## Acceptance criteria

- Snapshot endpoint creates rows
- Positions API enriched with current price
- Backend survives gateway downtime

---

## Deliverables

- IBKR integration
- Snapshot storage
- Manual trigger endpoint
