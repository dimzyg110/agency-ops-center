# FLYWHEEL SYSTEM SUMMARY

Date: 2026-02-12

## Completed

### 1) Waitlist persistence + API wiring
- Implemented/verified waitlist route support (`POST /api/v1/waitlist` + `GET /api/v1/admin/waitlist/stats`) in API code.
- Added/used waitlist client methods in web app (`api.joinWaitlist`, `api.getWaitlistStats`).
- Added reusable web waitlist helper/hook:
  - `apps/web/src/lib/waitlist.ts`
  - UTM capture from URL (`window.location.search`)
  - shared submit state (`idle/loading/success/error`)
  - flywheel next-step mapping for cross-sell CTAs.

### 2) Database table created
Executed against Railway Postgres:
- `CREATE EXTENSION IF NOT EXISTS pgcrypto;`
- `CREATE TABLE IF NOT EXISTS waitlist (...)`
- `CREATE INDEX IF NOT EXISTS idx_waitlist_product ...`
- `CREATE INDEX IF NOT EXISTS idx_waitlist_email ...`

### 3) Product page forms now persist real signups
Updated:
- `apps/web/src/pages/Budtender.tsx`
- `apps/web/src/pages/Cue.tsx`
- `apps/web/src/pages/Delivery.tsx`

Changes:
- Replaced `alert()` flow with real waitlist API submission.
- Added loading/success/error states.
- Added retry handling for error state.
- Added checkmark-based success confirmation.
- Added flywheel cross-sell next step after successful signup.
- Submit source now set as `product_page`, with UTM propagation.

### 4) Dashboard flywheel CTAs
Updated:
- `apps/web/src/pages/MorningBrief.tsx`

Added contextual CTAs after Report Card:
- If no recent price movers: CTA to Cue (`/cue?source=dashboard_cta`)
- If operator has website in onboarding state: CTA to Budtender (`/budtender?source=dashboard_cta`)

### 5) Sidebar tool flywheel indicators
Updated:
- `apps/web/src/components/Sidebar.tsx`

Changes:
- Tools include Virtual Budtender, Cue, Delivery.
- Added subtle right-side badge per tool:
  - shows waitlist count when available
  - otherwise shows `Coming Soon`.

### 6) Market page conversion CTA
Updated:
- `apps/web/src/pages/Market.tsx`

Added post cross-reference conversion block:
- “Want these insights for YOUR store?”
- Links to `/onboarding?source=market_page`.

### 7) Landing page “Get Started Free” flow
Updated:
- `apps/web/src/pages/Landing.tsx`

Changes:
- Hero CTA now captures email.
- Creates waitlist signup with `product: 'glass'` and `source: 'landing_get_started'`.
- On success redirects directly to `/onboarding`.

### 8) Newsletter waitlist integration
Updated:
- `services/api/src/routes/newsletter.ts`

Behavior now:
- Newsletter subscribe flow writes to waitlist with `product: 'newsletter'`.
- Still performs Beehiiv subscription when configured.
- If Beehiiv is not configured, returns success for waitlist capture path.

## Additional files touched
- `apps/web/src/components/CueSignup.tsx` (now submits real waitlist signup)
- `apps/web/src/api/client.ts`

## Validation
- API build step succeeded (`services/api` TypeScript build).
- Full monorepo build failed at web step due missing local `vite` binary in environment (`sh: 1: vite: not found`).

## Notes
- Existing repo had pre-existing unrelated changes outside this feature in other sessions; this summary only describes flywheel/waitlist work listed above.
