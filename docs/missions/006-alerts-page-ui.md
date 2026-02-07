# Mission 006 — Alerts page UI (feed + inline chart + polling + link drawer)

## Read first
- Read `AGENTS.md` and follow it strictly.
- Charts must be visible inline (no click).
- Poll backend every ~7 seconds while page active.

## Goal
Implement `/alerts` page UI that:
- Fetches from `GET /api/alerts/feed`
- Shows alert cards with inline chart
- Allows linking via drawer flow
- Polls periodically

## Scope
Implement:
- API client wrapper in frontend (`src/lib/api.ts`)
- Alerts page:
  - search box (q)
  - list of AlertCard components
  - polling interval ~7 seconds while active
- AlertCard:
  - symbol, alert_type chip, triggered_at, price, message
  - inline `<img>` from chart_url
- Link flow:
  - “Link” button opens a right drawer
  - Drawer loads open positions from `GET /api/positions/open`
  - User selects position + link_type
  - Calls `POST /api/triggers/{trigger_id}/link`
  - On success removes card from feed

Do NOT implement:
- No fancy styling beyond clean MUI
- No pagination UI yet (optional)
- No IBKR

## Acceptance criteria
- Alerts appear on page
- Chart images display without user clicks
- New alerts appear within polling interval
- Linking removes alert from feed immediately

## Deliverables
- Files changed/created
- How to set backend base URL (env var)
