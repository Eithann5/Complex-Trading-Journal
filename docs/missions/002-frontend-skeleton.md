# Mission 002 — Frontend skeleton (Next.js) + MUI Core light theme

## Read first
- Read `AGENTS.md` and follow it strictly.
- Frontend must call backend only (no Supabase direct).

## Goal
Create Next.js frontend skeleton with:
- Light theme (MUI Core)
- Navbar with links to Alerts and Positions
- Placeholder pages that render without errors

## Scope
Implement:
- `frontend/` Next.js app
- MUI Core setup
- Light theme
- Routes/pages:
  - `/alerts`
  - `/positions`
- Simple top nav (AppBar) with 2 links

Do NOT implement:
- No real API calls yet
- No feed UI yet
- No tables yet

## Files to create (typical)
- `frontend/package.json`
- `frontend/next.config.js` (optional)
- `frontend/src/pages/_app.tsx`
- `frontend/src/pages/alerts.tsx`
- `frontend/src/pages/positions.tsx`
- `frontend/src/components/NavBar.tsx`
- `frontend/src/theme/theme.ts`

## Implementation notes
- Use MUI Core (free) only.
- Use Next.js pages router or app router — choose one and keep consistent.
- Provide a light theme in `src/theme/theme.ts` and wrap app with ThemeProvider.
- Ensure links work and pages render.

## Acceptance criteria
1. Run:
   - `cd frontend`
   - `npm install`
   - `npm run dev`
2. Verify:
   - Home can redirect or show nav
   - `/alerts` loads with placeholder text
   - `/positions` loads with placeholder text
   - Navbar appears on both pages

## Deliverables
- List of created/modified files
- Commands to run locally
