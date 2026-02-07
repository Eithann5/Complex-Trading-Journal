# Mission 007 — Positions page UI (table + drawer editing)

## Goal
Implement `/positions` page UI:
- Table of open positions
- Drawer to edit origin, tags, and notes
- Display linked triggers list

## Scope
Implement:
- Positions table (MUI Table)
- Row click opens drawer showing:
  - origin selector (manual / alert_based)
  - tags list (chips) + add/remove
  - notes text area + save
  - linked triggers list (symbol/type/time)
- Uses backend endpoints:
  - GET /api/positions/open
  - PATCH /api/positions/{position_id}
  - POST/DELETE tags

Do NOT implement:
- No IBKR snapshots display yet (unless backend includes them later)
- No analytics page

## Acceptance criteria
- Positions load
- Editing origin/notes persists
- Tags add/remove persists
- Linked triggers shown

## Deliverables
- Files changed/created
