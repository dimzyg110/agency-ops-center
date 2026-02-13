# GLASS Logged-In Dashboard Review
**Date:** 2026-02-13 (UTC)  
**Reviewer:** OpenClaw subagent (`reviewer-logged-in`)  
**Target:** https://glassintel.xyz

---

## Test setup

### Auth attempts
1. Tried signup via `/signup` (Clerk embedded UI) with test email/password.
2. Tried signin via `/login` (Clerk embedded + hosted Clerk page).
3. In browser automation, Clerk flow did not complete reliably (signup stuck in disabled/spinner state; signin submit redirected to Google OAuth flow repeatedly).

### Fallback used
To still validate authenticated data behavior, I created a test account through API:
- `POST /api/v1/auth/signup`
- Test email: `test-loggedin-review-1770960977@roviq.ai`
- Created operator: `Review Test Operator` (`4ab8b348-ab61-461b-a255-582d8b4959e5`)

Then tested protected APIs with returned bearer token.

> **Important limitation:** I could not get a stable Clerk browser session in this environment, so true in-browser logged-in UI walkthrough of sidebar/page navigation is partially blocked. Findings below combine: (a) direct route behavior, (b) authenticated API responses, and (c) frontend source review.

---

## High-level findings (critical)

1. **Auth flow risk (P0):** Signup/signin is unreliable under automation (spinner freeze / OAuth redirect behavior). This may be anti-bot/Turnstile related, but it blocks QA and could block some real users.
2. **New-user data gap (P0):** New operators get empty `/prices`, `/recommendations`, `/alerts` because data is strictly scoped to `request.auth.operator_id`.
3. **Onboarding mismatch (P0):** Onboarding “claim operator” is stored in localStorage only; it does not remap the authenticated user’s backend operator context. This creates mismatch between what UI implies and what APIs return.
4. **Competitors endpoint bug (P0):** `/api/v1/viz/operator-compare` returns 500 (`cannot cast type record to text[]` / `malformed array literal`) with current query construction.
5. **Settings page is mock-only (P1):** `/settings` frontend is hardcoded demo data, not real account/operator data.

---

## Page-by-page review

## `/prices` — Price Wire

### What works
- Route exists and is protected.
- Unauthenticated visit correctly redirects to Clerk sign-in.
- API responds (no server crash): `GET /api/v1/prices`, `GET /api/v1/prices/movers`.

### What doesn’t work
- For newly created operator account, `prices` and `movers` are empty:
  - `{"data":[], ...}`
  - `{"movers":[]}`
- No automatic bootstrap data for new user experience.

### Data accuracy issues
- Backend intentionally scopes prices to authenticated operator ID only (not selected onboarding operator).
- If operator has no ingested menu/source rows, page is empty even though market has large dataset.

### UX suggestions
- Add “no data yet” onboarding state with clear action path:
  - claim existing operator + backend link,
  - or run initial import.
- Consider optional market-wide fallback view for first-session value.
- Surface “last successful scrape for your operator” directly on page.

---

## `/threats` — Threat Radar

### What works
- Route protection/redirect works.
- API returns valid threat records with severity and metadata.
- Threat feed summary is populated (critical/high/medium/low counts).

### What doesn’t work
- Threats are effectively **global** unless lat/lon filters are passed.
- Frontend hook currently calls without operator geo context by default, so personalization is weak.

### Data accuracy issues
- For new operator, threat data still shows all-segment/global threats, not clearly “your local threats”.

### UX suggestions
- Auto-pass operator location/radius to threats API.
- Label cards as “statewide” vs “within X miles of your store”.
- Show confidence/source freshness per threat.

---

## `/competitors` — Competitor analysis

### What works
- Page route is present and protected.
- Supporting viz endpoints like `/viz/market-share-flow`, `/viz/price-wars` return data.

### What doesn’t work
- **Primary compare API is broken:**
  - `/api/v1/viz/operator-compare?ids=...` returns 500.
  - Errors observed: `cannot cast type record to text[]`, `malformed array literal`.
- With current implementation, competitor comparison component is likely broken/empty.

### Data accuracy issues
- Because compare query fails, any displayed comparison metrics would be incomplete or absent.

### UX suggestions
- Fix SQL/query binding for `ids` array in `/viz/operator-compare` first.
- Add graceful fallback card (“comparison unavailable; retry”).
- Log structured error telemetry per user/session.

---

## `/recommendations`

### What works
- Route protection works.
- API responds without crash.

### What doesn’t work
- For test operator, recommendations are empty:
  - `{"data":[], ...}`
- No first-run generated recommendation set for new operator.

### Data accuracy issues
- Operator-scoped table means fresh signups see blank state until recommendation generation exists for that operator.
- Historical docs indicate recommendation framing may still conflict with report-card framing in some seeded contexts.

### UX suggestions
- Auto-generate starter recommendations after onboarding completion.
- Explicitly show why recommendations are empty (no data / no model run yet).
- Keep framing consistent with “margin opportunity” messaging.

---

## `/alerts`

### What works
- Route protection works.
- API endpoint responds cleanly.

### What doesn’t work
- For test operator, alerts are empty:
  - `{"data":[], ...}`
- Could not validate mark-read/dismiss UX on real alert objects due zero records.

### Data accuracy issues
- Operator-scoped alert model is correct technically, but zero bootstrap alerts produces dead page for new users.

### UX suggestions
- Seed onboarding alert examples or first-run informational alerts.
- Add “alert sources connected” checklist so users know how to get real alerts.

---

## `/settings`

### What works
- Route exists and renders.
- Local UI interactions (toggle/remove mock watchlist item) function client-side.

### What doesn’t work
- Page is currently hardcoded mock data (`mockOperator`, `mockWatchlist`) in frontend code.
- Not connected to real profile/watchlist/notification backend state.
- Email shown is static (`admin@greenleafma.com`) and not user-specific.

### Data accuracy issues
- Operator profile in settings can be materially wrong for signed-in user.
- Watchlist changes are local state only (not persisted to backend).

### UX suggestions
- Replace mock data with `useProfile`, `useWatchlists`, and notification preference APIs.
- Persist notification preferences and email list server-side.
- Add explicit save states/toasts and unsaved-change indicators.

---

## Navigation verification

### What works
- Direct unauthenticated access to protected routes (`/prices`, `/threats`, `/competitors`, `/recommendations`, `/alerts`, `/settings`) redirects to Clerk sign-in.
- Redirect includes return URL target.

### Could not fully verify
- In-app sidebar navigation while authenticated (blocked by Clerk session issue in this environment).

---

## Operator-specific correctness review

- Backend protected routes for prices/recommendations/alerts are tied to `request.auth.operator_id`.
- Onboarding’s selected operator is local-only and does **not** update backend operator ownership.
- Result: user can “select” an operator in onboarding but still receive empty operator-scoped datasets in several pages.

**Impact:** severe trust issue for first-time users (UI promises “we track your dispensary” but key pages remain empty).

---

## Email snapshot/doc review

## What I checked
- `outreach/emails-sent-log.json`
- `outreach/emails-batch-1-final.md`
- newsletter/report card public endpoints

## Findings
1. **Email delivery issue:** `emails-sent-log.json` shows sends failing with `403` (Resend domain not verified). So many “sent” entries were not actually delivered.
2. **Report-card email links:** sampled slugs from outreach docs (e.g., `canna-provisions-holyoke`, `elevated-roots`) resolve and generally align with current report card directionally (minor numeric drift expected as data updates).
3. **Newsletter snapshot mismatch:** newsletter/marketing copy includes static/demo claims (e.g., “500+ operators” / “70,000+ products”) that don’t match current live headline metrics seen elsewhere (`301 operators`, `110.3K products`, `134.2K observations`).

---

## Priority fixes

### P0
1. Stabilize Clerk login/signup completion (including captcha/Turnstile edge cases).
2. Fix onboarding-to-backend operator linkage.
3. Fix `/viz/operator-compare` SQL parameterization bug.
4. Improve first-run experience for empty operator-scoped pages.

### P1
5. Replace `/settings` mock data with real API-backed data.
6. Unify metric claims across newsletter/market/public pages.
7. Ensure recommendation language is consistent with report-card “opportunity” framing.

---

## Final verdict
The platform has strong underlying data and several healthy APIs, but the logged-in operator experience has major first-session and operator-context integrity gaps. In current state, a new signup can authenticate yet see mostly empty actionable pages, and competitors analysis has a backend error path that likely breaks the page.
