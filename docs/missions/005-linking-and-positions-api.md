# Mission 005 — Linking endpoint + positions tables + positions API (without IBKR)

## Read first
- Read `AGENTS.md` and follow it strictly.
- Alerts disappear from feed ONLY when linked.

## Goal
Implement:
- Supabase tables for linking and journaling
- Endpoint to link a trigger to a position
- Positions API to manage origin/tags
This mission does NOT yet integrate IBKR snapshots.

## Scope
Implement:
1) SQL migrations (or Supabase SQL scripts) to create:
   - `position_journal`
   - `trigger_position_links`
   - `position_tags`
2) Backend endpoints:
   - `POST /api/triggers/{trigger_id}/link`
   - `GET /api/positions/open` (from `position_journal`)
   - `PATCH /api/positions/{position_id}` (origin/notes/open_time)
   - `POST /api/positions/{position_id}/tags`
   - `DELETE /api/positions/{position_id}/tags/{tag_id}`
3) Update `GET /api/alerts/feed` filtering logic so linked triggers are excluded

Do NOT implement:
- No IBKR yet
- No positions_snapshot yet

## SQL requirements
- Use UUID primary keys
- Use FK constraints:
  - trigger_position_links.trigger_id → alerts_triggers.id
  - trigger_position_links.position_id → position_journal.id
  - position_tags.position_id → position_journal.id

## Link endpoint behavior
`POST /api/triggers/{trigger_id}/link` body:
- `position_id` (uuid)
- `link_type` = `trigger|context|post_entry`

Effect:
- Insert row into `trigger_position_links`
- Return `{ ok: true }`

## Positions API behavior
- `GET /api/positions/open` returns positions where status = open
- Include tags list and linked triggers list

## Acceptance criteria
1. Create a position_journal row manually (SQL or endpoint if you add one)
2. Call link endpoint and link a trigger to that position
3. Verify:
   - Trigger no longer appears in `/api/alerts/feed`
   - Positions open endpoint includes that linked trigger
4. Tag endpoint:
   - Add a tag and see it returned

## Deliverables
- SQL file(s) under `backend/sql/` or `docs/sql/`
- Backend routes + services updated
- Example curl commands
