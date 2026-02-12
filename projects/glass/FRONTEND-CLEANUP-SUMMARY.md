# GLASS Frontend Cleanup Summary

**Date:** 2026-02-12
**Commit:** b56cd04 (on main, pushed)
**Deployed:** glass-api + glass-web to Railway production

---

## Priority 1: Onboarding Search — FIXED ✅

### Root Cause
The `searchOperators()` method in `client.ts` called `GET /api/v1/operators?search=X`, but:
1. The `/operators` endpoint requires `fastify.authenticate` (auth)
2. It filters by `request.auth.operator_id` — only returns the user's own operator
3. There was NO `search` query parameter support at all
4. During onboarding, new users don't have auth tokens, so the call returns 401 or only "New Operator" placeholder records

### Fix Applied
- **API:** Added `GET /api/v1/operators/search?q=` — PUBLIC endpoint (no auth required)
  - Searches by name OR city (ILIKE)
  - Filters out "New Operator" placeholders and "PENDING-" auto-provisioned records
  - Returns only `{ id, name, city, state }` (minimal surface area for public endpoint)
  - Limited to 15 results, requires ≥2 characters
  - Registered BEFORE `/operators/:id` to avoid route collision in Fastify
- **Frontend (`client.ts`):** Updated `searchOperators()` to call `/operators/search?q=` instead of `/operators?search=`
- **Frontend (`Onboarding.tsx`):** Updated result types, added state display (e.g., "Boston, MA")
- **Lib (`onboarding.ts`):** Introduced `SearchOperator` type to handle partial operator data from search

### Verification
Database has 492 operators. Searching "cannabis healing" now returns:
- `cannabis-healing` (boston)
- `Cannabis Healing` (allston)
- `Coastal Healing` (barnstable)

Instead of just "New Operator / Unknown".

---

## Priority 2: Frontend Audit

### A) Routes & Features

| Route | Status | Notes |
|-------|--------|-------|
| `/` (root) | ✅ Works | Shows Landing (signed out) or MorningBrief (signed in) |
| `/onboarding` | ✅ Fixed | Search now works; protected route |
| `/login`, `/signup` | ✅ Works | Clerk integration with GLASS branding |
| `/market` | ✅ Works | Public page, CCC cross-reference data loads |
| `/newsletter` | ✅ Works | Public newsletter signup page |
| `/prices` | ✅ Works | Protected; PriceWire with viz components |
| `/threats` | ✅ Works | Protected; ThreatRadar with network viz |
| `/competitors` | ✅ Works | Protected; operator comparison |
| `/geography` | ✅ Works | Protected; terrain map + delivery zones |
| `/recommendations` | ✅ Works | Protected; recommendation cards |
| `/alerts` | ✅ Works | Protected; alert management |
| `/budtender` | ✅ Fixed | Public product page; form now has handler |
| `/cue` | ✅ Fixed | Public product page; form now has handler |
| `/delivery` | ✅ Fixed | Public product page; form now has handler |
| `/settings` | ⚠️ Mock data | Has hardcoded operator/watchlist data |

### B) UX Issues Found & Fixed

1. **Sidebar double-icon** — Tool items had emoji in labels (🤖, 📦, 🚗) PLUS Lucide icons. Fixed: removed emoji from labels.

2. **Market page newsletter form** — Had `YOUR_FORM_ID` placeholder in Beehiiv action URL. Fixed: replaced with link to `/newsletter` page.

3. **Product page forms caused page reload** — Budtender, Cue, Delivery forms had no `onSubmit` handler, causing full page reload on submit. Fixed: added `preventDefault()` + confirmation alert.

4. **Delivery fake metric** — "42 operators interested near you" was hardcoded/fabricated. Fixed: changed to "490+ operators tracked statewide" (real DB count).

5. **Unused imports** — `Minus`, `TrendingDown`, `TrendingUp` in Market.tsx. Cleaned up.

### C) Data Display

- ✅ Prices formatted correctly with `$XX.XX` format
- ✅ DataFreshness component showing on Market and MorningBrief pages
- ✅ ReportCard renders (skeleton → error → actual data)
- ✅ Empty states render when no operator selected
- ✅ MorningBrief shows "—" for missing data (no fabrication)
- ✅ Cross-reference table shows real CCC vs GLASS data

### D) Dark/Light Mode Consistency

- ✅ Dashboard pages (MorningBrief, PriceWire, Threats, etc.) — consistent dark mode (`bg-glass-black`)
- ✅ Public pages (Landing, Market, Budtender, Cue, Delivery, Newsletter) — consistent light mode (`bg-white`)
- ✅ Onboarding — light mode (white bg, matches Landing aesthetic)
- ✅ Auth pages (Login/Signup) — dark mode with GLASS branding

### E) Mobile Responsiveness

- ✅ Sidebar has mobile hamburger menu + overlay
- ✅ All grid layouts use responsive breakpoints (`sm:`, `lg:`, `xl:`)
- ✅ Forms are full-width on mobile
- ✅ Tables overflow gracefully on Market page
- ✅ Landing page hero text scales down properly

---

## Remaining Issues (Need Randy's Input)

1. **Settings page mock data** — `mockOperator` and `mockWatchlist` are hardcoded constants, not connected to any API. Should we wire this to the profile/watchlist API or leave as placeholder?

2. **Beehiiv newsletter integration** — The newsletter form on `/newsletter` page needs actual Beehiiv embed or API integration. Currently the forms are client-side only.

3. **Product page form submissions** — Budtender/Cue/Delivery waitlist forms currently just show `alert()`. Should these POST to an API endpoint or go to a third-party form service?

4. **CueSignup component** — Uses `setTimeout` to simulate submission. Same question as above.

5. **Landing page "50+ operators"** — The CTA says "Join 50+ Massachusetts operators using GLASS." This is a social proof number — is it accurate? DB has 492 tracked operators but that's not the same as users.

6. **Auto-invite email changes** — Pre-existing uncommitted changes to `scripts/auto-invite/` were included in this commit (branding updates, Resend key fallback, unsubscribe URL). These were not part of my changes.

---

## Files Changed

| File | Change |
|------|--------|
| `services/api/src/routes/operators.ts` | Added public `/operators/search` endpoint |
| `apps/web/src/api/client.ts` | Updated `searchOperators()` to use new endpoint |
| `apps/web/src/lib/onboarding.ts` | Added `SearchOperator` type |
| `apps/web/src/pages/Onboarding.tsx` | Updated types + state display |
| `apps/web/src/components/Sidebar.tsx` | Removed emoji from tool labels |
| `apps/web/src/pages/Market.tsx` | Fixed newsletter form, cleaned imports |
| `apps/web/src/pages/Budtender.tsx` | Added form submit handler |
| `apps/web/src/pages/Cue.tsx` | Added form submit handler |
| `apps/web/src/pages/Delivery.tsx` | Added form submit handler, fixed fake metric |
