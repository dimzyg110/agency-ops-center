# GLASS — Comprehensive Technical Review & Phase Plan

**Reviewer:** Senior Technical Architect (Opus 4)  
**Date:** 2026-02-12  
**Production URL:** glassintel.xyz (Railway)  
**DB:** PostgreSQL on Railway (`turntable.proxy.rlwy.net:18582/railway`)

---

## Table of Contents

1. [Current State Audit](#1-current-state-audit)
2. [Data Inventory](#2-data-inventory)
3. [What's Working vs Broken](#3-whats-working-vs-broken)
4. [Phase Plan](#4-phase-plan)
5. [Critical Path — This Week](#5-critical-path--this-week)

---

## 1. Current State Audit

### 1.1 Database Schema (26 tables)

**Core Business Tables:**

| Table | Rows | Purpose | Health |
|-------|------|---------|--------|
| `operators` | 473 | MA dispensary records | ⚠️ 464 "pending", only 9 "active" |
| `products` | 100,849 | Normalized product catalog | ✅ Well-populated, 7 categories |
| `prices` | 116,991 | Price observations | ⚠️ 99.9% from single day (Feb 12) |
| `sources` | 532 | Scrape source configs | ✅ 235 Dutchie + 282 Weedmaps + 15 other |
| `users` | 3 | Registered users | ⚠️ Only Randy + 2 Clerk placeholders |
| `threats` | 6 | Competitive threats | ⚠️ Seed data only |
| `recommendations` | 6 | AI pricing recs | ⚠️ Seed data only |
| `margin_rules` | 5 | Pricing guardrails | ⚠️ Seed data only |
| `watchlists` | 0 | Product watch alerts | ❌ Empty |
| `alerts` | 10 | User notifications | ⚠️ Seed data only |
| `waitlist` | 4 | Signup waitlist | ⚠️ All test entries |

**CCC State Data Tables:**

| Table | Rows | Purpose | Health |
|-------|------|---------|--------|
| `ccc_lab_tests` | 147,649 | THC/THCA test results | ✅ Imported, latest test: 2024-03-31 |
| `ccc_avg_prices` | 31,038 | Official state price data | ✅ 7 years, latest: 2025-12-21 |
| `ccc_plant_activity` | 46,863 | Plant growth/harvest data | ✅ Populated |
| `ccc_weekly_sales` | 376 | Weekly sales aggregates | ✅ Populated |
| `ccc_pending_applications` | 234 | License applications | ✅ Imported |
| `ccc_demographics` | 14 | Industry demographics | ✅ Small but present |
| `ccc_facility_sales` | 0 | Per-facility sales | ❌ NOT IMPORTED (CSV exists: 7.9MB) |
| `ccc_licenses` | 0 | License registry | ❌ NOT IMPORTED (CSV exists: 652KB) |
| `ccc_monthly_prices` | 0 | Monthly price summaries | ❌ NOT IMPORTED |

**Infrastructure Tables:**

| Table | Rows | Purpose | Health |
|-------|------|---------|--------|
| `scrape_runs` | 10 | Scrape execution logs | ✅ Working |
| `scrape_jobs` | 769 | Per-store scrape jobs | ✅ Working |
| `etl_runs` | 1 | ETL pipeline tracking | ✅ Working |
| `operator_scores` | 0 | Precomputed health scores | ❌ Table exists in schema but NOT in production DB |
| `daily_price_averages` | 47 | (VIEW) Daily aggregates | ✅ Working |
| `refresh_tokens` | 1 | JWT refresh tokens | ✅ Working |

**Missing from Production (defined in schema.ts but not deployed):**
- `operator_scores` table — does NOT exist in production DB
- No materialized views (`mv_operator_health`, `mv_thc_integrity`) — 0 matviews found
- No stored function `refresh_health_scores()` — only pgcrypto functions exist

### 1.2 API Architecture

**Framework:** Fastify with Clerk auth, JWT, CORS  
**Route prefix:** `/api/v1/`  
**21 route files registered:**

| Route File | Endpoints | Auth | Status |
|------------|-----------|------|--------|
| `auth.ts` | Login/signup/callback | Public | ✅ Working (Clerk) |
| `operators.ts` | Search, CRUD | Public (search) / Auth (CRUD) | ✅ Working |
| `prices.ts` | List, movers, categories | Auth required | ✅ Working with real data |
| `products.ts` | List, search | Auth required | ✅ Working |
| `dashboard.ts` | Morning Brief aggregate | Auth required | ✅ Working |
| `report-card.ts` | Operator report cards | Rate-limited (no auth!) | ✅ Working — impressive feature |
| `ccc.ts` | 7 CCC data endpoints | Public (rate-limited) | ✅ Working |
| `scores.ts` | Health scores, leaderboard | Mixed | ⚠️ Depends on missing `operator_scores` table and matviews |
| `viz.ts` | D3 visualization data | Auth required | ✅ Working |
| `threats.ts` | Threat feed/list | Auth required | ⚠️ Only 6 seed records |
| `recommendations.ts` | AI recs + generate | Auth required | ⚠️ Only 6 seed records |
| `margin-rules.ts` | CRUD + violations | Auth required | ⚠️ Only 5 seed records |
| `watchlists.ts` | CRUD | Auth required | ✅ Working (empty) |
| `alerts.ts` | List/manage | Auth required | ⚠️ Only 10 seed records |
| `sources.ts` | Scrape source mgmt | Auth required | ✅ Working |
| `exports.ts` | CSV export | Auth required | ✅ Working |
| `profile.ts` | User profile | Auth required | ✅ Working |
| `newsletter.ts` | Email subscribe | Public | ✅ Working |
| `waitlist.ts` | Waitlist signup | Public | ✅ Working (with XSS test entry!) |
| `scores.ts` | Health scores | Mixed auth | ❌ Broken — `operator_scores` table doesn't exist |

**Security:**
- ✅ Clerk JWT auth on protected routes
- ✅ CORS origin validation
- ✅ Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- ✅ Admin API key gating for admin endpoints
- ✅ Rate limiting on public endpoints
- ✅ `escapeLike()` for SQL injection prevention
- ⚠️ Waitlist has XSS test entry — suggests someone probed it
- ⚠️ Report card endpoint has NO auth — any operator_id gives full market intel

### 1.3 Frontend Architecture

**Stack:** React + Vite + Tailwind CSS + Clerk + TanStack Query + D3  
**17 page components:**

| Page | Route | Auth | Real Data | Status |
|------|-------|------|-----------|--------|
| `Landing.tsx` (19KB) | `/`, `/landing` | Public | N/A | ✅ Marketing page |
| `Market.tsx` (37KB) | `/market` | Public | Yes (CCC endpoints) | ✅ Largest page — market intelligence dashboard |
| `MorningBrief.tsx` (32KB) | `/` (signed in) | Auth | Yes (dashboard + report-card APIs) | ✅ Real data via hooks |
| `PriceWire.tsx` (22KB) | `/prices` | Auth | Yes (prices API) | ✅ Real data via hooks |
| `ThreatRadar.tsx` (10KB) | `/threats` | Auth | Yes (threats API) | ⚠️ Only 6 seed records shown |
| `Recommendations.tsx` (7KB) | `/recommendations` | Auth | Yes (recommendations API) | ⚠️ Only 6 seed records |
| `Alerts.tsx` (11KB) | `/alerts` | Auth | Yes (alerts API) | ⚠️ Only 10 seed records |
| `Onboarding.tsx` (20KB) | `/onboarding` | Auth | Yes (operator search) | ✅ 4-step flow working |
| `Newsletter.tsx` (15KB) | `/newsletter` | Public | Yes (newsletter API) | ✅ Working |
| `Settings.tsx` (9KB) | `/settings` | Auth | Mostly mock | ⚠️ Heavy placeholder references |
| `Competitors.tsx` (2.5KB) | `/competitors` | Auth | Minimal | ⚠️ Thin shell |
| `Geography.tsx` (2KB) | `/geography` | Auth | Minimal | ⚠️ Thin shell |
| `Budtender.tsx` (15KB) | `/budtender` | Public | Mock | ❌ Paused per exec summary |
| `Cue.tsx` (13KB) | `/cue` | Public | Mock | ❌ Future spoke |
| `Delivery.tsx` (5KB) | `/delivery` | Public | Mock | ❌ Future spoke |
| `Admin.tsx` (7KB) | `/admin` | Public (!) | Yes (admin APIs) | ⚠️ No auth gate! Uses API key query param |

**Data fetching:** TanStack Query hooks in `src/apps/web/src/api/hooks.ts` — 
well-structured with automatic refetch intervals (5-10 min).

### 1.4 Scraper Infrastructure

**Files:**
- `src/scripts/scrape-dutchie-ma.ts` (25KB) — Dutchie scraper with Camofox browser automation
- `src/scripts/scrape-weedmaps.ts` (21KB) — Weedmaps scraper with Camofox
- `src/scripts/daily-scrape.ts` (4KB) — Orchestrator (runs Dutchie then Weedmaps)
- `src/scripts/run-scrapers-sequential.ts` (2KB) — Alternative runner
- `src/scripts/lib/` — Shared utilities (brand filter, normalizer, browser pool, DB helpers, config)

**Slug sources:**
- `dutchie-slugs.json` (55KB) — 235+ Dutchie store slugs
- `weedmaps-slugs.json` (400KB) — 282+ Weedmaps store slugs

**Performance (Feb 12 — only scrape day with meaningful volume):**

| Platform | Stores Attempted | Succeeded | Failed | Success Rate | Products Found |
|----------|-----------------|-----------|--------|--------------|----------------|
| Dutchie | 235 | 195 | 40 | **83.0%** | 57,986 |
| Weedmaps | 173 | 10 | 163 | **5.8%** | 6,162 |

**Critical issue:** Weedmaps scraper has a **94.2% failure rate**. Only 10/173 stores succeeded. This means ~60% of operators (Weedmaps-only) have NO price data.

### 1.5 CCC Data Pipeline

**Available CSVs** in `src/data/ccc-raw/`:
- `testing-thc-thca.csv` (29.6MB) → ✅ Imported to `ccc_lab_tests` (147,649 rows)
- `facility-sales-stats.csv` (7.9MB) → ❌ NOT imported (`ccc_facility_sales` = 0 rows)
- `itd-retail-delivery-sales.csv` (7.9MB) → ❌ NOT imported
- `medical-facility-stats.csv` (4.9MB) → ❌ NOT imported
- `commence-ops.csv` (652KB) → ❌ NOT imported (`ccc_licenses` = 0 rows)
- `avg-monthly-price-oz.csv` (1.5KB) → ❌ NOT imported (`ccc_monthly_prices` = 0 rows)
- `adult-market-data-counties.csv` (1.6MB) → Partially imported (to `ccc_demographics`?)

**Import scripts:**
- `src/scripts/import-ccc-data.ts` (10KB) — General CCC importer
- `src/scripts/import/import-lab-tests.ts` — Lab test importer (recently bug-fixed per `LAB-IMPORT-FIX.md`)

---

## 2. Data Inventory

### 2.1 Scrape Data Timeline

| Date | Price Observations | Operators Scraped |
|------|-------------------|-------------------|
| 2026-02-12 | 116,874 | 293 |
| 2026-02-11 | 16 | 9 |
| 2026-02-10 | 19 | 10 |
| 2026-02-09 | 17 | 9 |
| 2026-02-08 | 16 | 8 |
| 2026-02-07 | 14 | 8 |
| 2026-02-06 | 20 | 9 |
| 2026-02-05 | 15 | 9 |

**Analysis:** There is virtually **no time-series data**. 99.9% of price observations are from a single Feb 12 bulk scrape. Pre-Feb 12, only 8-10 operators per day were being scraped (likely manual test runs). The daily scraper is not running as a cron.

### 2.2 Product Category Distribution

| Category | Products | % |
|----------|----------|---|
| flower | 45,492 | 45.1% |
| preroll | 22,441 | 22.2% |
| vape | 15,030 | 14.9% |
| edible | 12,854 | 12.7% |
| concentrate | 5,026 | 5.0% |
| tincture | 3 | <0.01% |
| topical | 3 | <0.01% |

### 2.3 Price Data Quality

| Metric | Value |
|--------|-------|
| Total prices | 116,991 |
| Zero prices | 0 ✅ |
| Negative prices | 0 ✅ |
| Over $500 | 0 ✅ |
| Average price | $29.79 |
| Min price | $0.22 |
| Max price | $500.00 |
| Distinct operators with prices | 301 / 472 total |
| Suspicious brands | 82 (0.08% of products) |

**Price quality is excellent** — no invalid prices. The brand quality issue (82 suspicious brands) is minor — the regex catches false positives like "Offbrand" (a real brand name) and "British Bake Off" (contains "off").

### 2.4 Operator Coverage

| Metric | Count |
|--------|-------|
| Total operators | 472 (excluding "New Operator") |
| Geocoded | 472/472 (100%) ✅ |
| With price data | 301 (63.8%) |
| Active last 24h | 295 |
| Active last 7d | 301 |
| No price data ever | 171 (36.2%) — mostly Weedmaps-only stores |
| Platform: Dutchie | 189 |
| Platform: Weedmaps | 273 |
| Platform: Unknown | 11 |

### 2.5 Data Gaps Summary

| Gap | Impact | Fix Effort |
|-----|--------|------------|
| Weedmaps scraper 94% failure rate | 171 operators have NO data | HIGH — need scraper rewrite |
| No daily scrape cron | No time-series accumulation | LOW — add Railway cron or systemd timer |
| `ccc_facility_sales` not imported | Missing facility-level revenue data | MEDIUM — write import script |
| `ccc_licenses` not imported | Missing license registry | MEDIUM — write import script |
| `ccc_monthly_prices` not imported | Missing official monthly prices | LOW — small CSV |
| `operator_scores` table missing | Health score endpoints broken | MEDIUM — run migration |
| No materialized views | Score computation slow/broken | MEDIUM — run migration 003 |
| Only 1 day of real price data | Can't compute trends, deltas, time-series | CRITICAL — needs daily scraping NOW |

---

## 3. What's Working vs Broken

### 3.1 ✅ Working Well

1. **Dutchie scraper** — 83% success rate, 57,986 products per run. Solid.
2. **Product normalization pipeline** — clean categories, good brand parsing (82 false positives out of 100K+ is fine).
3. **Price data quality** — zero invalid prices, good confidence scores.
4. **Operator geocoding** — 100% coverage (472/472).
5. **Report Card API** (`/api/v1/report-card/:operator_id`) — sophisticated multi-section analysis with real SQL. Best feature in the platform.
6. **Onboarding flow** — 4-step, operator search works, instant value.
7. **Clerk authentication** — properly integrated with JWT and JWKS verification.
8. **CCC data endpoints** — weekly sales, avg prices, pending applications, plant activity, cross-reference — all working.
9. **Market page** (`/market`) — largest frontend page, renders real CCC data publicly.
10. **Frontend data layer** — TanStack Query hooks with proper caching and refetch.
11. **Security posture** — headers, CORS, rate limiting, SQL injection protection.
12. **Margin Engine v1** — `engine/elasticity.ts`, `engine/generator.ts`, `engine/rules.ts` — code exists and is clean.

### 3.2 ⚠️ Partially Working

1. **Morning Brief** — fetches real data but limited by single-day dataset. No trends possible.
2. **Price Wire** — works with real API but "price movers" are meaningless with only 1 day of data.
3. **Threats** — only 6 seed records. No automated CCC threat detection pipeline.
4. **Recommendations** — only 6 seed records. Generator exists but not connected to cron.
5. **Alerts** — 10 seed records. No automated alert generation.
6. **Settings page** — heavy placeholder/mock content.
7. **Competitors/Geography pages** — thin shells, minimal content.

### 3.3 ❌ Broken / Non-functional

1. **Weedmaps scraper** — 5.8% success rate. Effectively non-functional.
2. **Daily scrape cron** — NOT running. No Railway cron, no Procfile, no railway.toml. The `daily-scrape.ts` script exists but is never automatically executed.
3. **Health scores** — `operator_scores` table doesn't exist in production. All `/operators/:id/health-score` and `/market/health-leaders` and `/admin/scores/recalculate` endpoints will error.
4. **Materialized views** — none exist. Score routes that fall back to `mv_operator_health` will 404/500.
5. **CCC facility sales import** — 0 rows despite 7.9MB CSV available.
6. **CCC licenses import** — 0 rows despite 652KB CSV available.
7. **CCC monthly prices import** — 0 rows.
8. **Budtender page** — paused/mock.
9. **Cue page** — mock/future.
10. **Delivery page** — mock/future.
11. **Admin page** — no auth gate (anyone can access `/admin`).

### 3.4 Scraper Reliability Assessment

**Dutchie (83% success, 195/235 stores):**
- Good baseline. The 40 failures likely include rate-limited stores, changed slugs, or stores that went offline.
- The `brand-filter.ts` library handles parsing garbage well.
- Uses Camofox anti-detection browser correctly.

**Weedmaps (5.8% success, 10/173 stores):**
- Nearly total failure. Likely causes:
  - Weedmaps may have changed their page structure/API
  - Anti-bot detection upgraded
  - Rate limiting
  - Category page structure differs from parser expectations
- This is the **#1 technical blocker** — 273 operators are Weedmaps-sourced.

### 3.5 Auth/Security Assessment

| Check | Status |
|-------|--------|
| Clerk JWT verification | ✅ Working |
| Admin API key gating | ✅ Working |
| CORS restriction | ✅ Configured |
| Security headers | ✅ All 5 headers set |
| Rate limiting | ✅ On public endpoints |
| SQL injection prevention | ✅ `escapeLike()` helper |
| Report card auth | ⚠️ NO AUTH — any UUID gets full market data |
| Admin page auth | ⚠️ NO AUTH on frontend route |
| XSS in waitlist | ⚠️ Stored `<script>alert(1)</script>@test.com` — needs sanitization |
| JWT_SECRET in prod | ✅ Required via env check |

---

## 4. Phase Plan

### Phase 2A: Data Quality + Scraper Stability

**Goal:** Make the data pipeline reliable enough to accumulate 7+ consecutive days of pricing data for all 300+ operators.

**Tasks:**

1. **Fix Weedmaps scraper** — Debug the 94% failure rate. Likely needs:
   - Snapshot comparison of working vs failing stores
   - Updated selector/API extraction logic
   - Better error handling and retry logic
   - May need to switch from page scraping to Weedmaps API if available
   - **File:** `src/scripts/scrape-weedmaps.ts` + `src/scripts/lib/weedmaps-parser.ts`
   - **Target:** >70% success rate (120+/173 stores)

2. **Deploy daily scrape cron** — Set up automated daily execution:
   - Add `railway.toml` or `Procfile` with cron schedule
   - Or: Railway cron job service pointing to `daily-scrape.ts`
   - Schedule: 4 AM ET daily (Dutchie), 5 AM ET (Weedmaps)
   - Add monitoring: alert on <60% success rate

3. **Import remaining CCC datasets:**
   - `ccc_facility_sales` from `facility-sales-stats.csv` (7.9MB) + `itd-retail-delivery-sales.csv` + `medical-facility-stats.csv`
   - `ccc_licenses` from `commence-ops.csv` (652KB)
   - `ccc_monthly_prices` from `avg-monthly-price-oz.csv` (1.5KB)
   - **Write import scripts** modeled on `import-lab-tests.ts`

4. **Run missing DB migrations:**
   - Create `operator_scores` table (exists in `schema.ts` but not in prod)
   - Create materialized views (`mv_operator_health`, `mv_thc_integrity`)
   - Create `refresh_health_scores()` stored function
   - **File:** `src/scripts/migrations/` — need new migration 006

5. **Brand data cleanup:**
   - Fix regex to exclude false positives ("Offbrand", "British Bake Off")
   - The 82 suspicious brands are actually mostly fine — `brand-filter.ts` works well
   - Low priority — current data is clean

6. **Activate operator statuses:**
   - 464/473 operators are "pending" status. Update all operators with price data to "active"
   - One-time SQL: `UPDATE operators SET status = 'active' WHERE id IN (SELECT DISTINCT operator_id FROM prices)`

7. **Sanitize waitlist inputs:**
   - Add XSS/HTML sanitization to waitlist and newsletter endpoints
   - Clean existing `<script>` entry

**Dependencies:** None (can start immediately)  
**Estimated effort:** 24-32 hours  
**Success criteria:**
- ✅ Weedmaps scraper >70% success rate
- ✅ 7 consecutive days of automated daily scrapes
- ✅ 350+ operators with price data (up from 301)
- ✅ All CCC CSVs imported (facility sales, licenses, monthly prices)
- ✅ `operator_scores` table + matviews exist and populated
- ✅ All operators with prices marked "active"

---

### Phase 2B: Price Wire + Morning Brief (Core Daily Value Prop)

**Goal:** Make the daily dashboard genuinely useful — real price trends, meaningful movers, actionable morning briefing.

**Tasks:**

1. **Price trend computation** — After 7+ days of data:
   - Build daily delta computation (`today_price - yesterday_price`)
   - Store in `daily_price_averages` view or new `price_trends` table
   - Power sparklines with REAL data (not fake)
   - **Files:** `src/services/api/src/routes/prices.ts`, `src/services/api/src/routes/dashboard.ts`

2. **Morning Brief enhancements:**
   - "Top 10 Price Movers" with actual 24h deltas
   - "Your store vs market" percentile per category (uses report-card data)
   - "New this week" — new products appearing in competitor menus
   - Data freshness indicator (hours since last scrape)
   - **File:** `src/services/api/src/routes/dashboard.ts`

3. **Price Wire improvements:**
   - Time-series chart per product (7-day, 30-day)
   - Category-level market avg trendlines
   - "Watch" button connected to watchlists API
   - CSV export working with real data
   - Filter by city/region
   - **Files:** `src/apps/web/src/pages/PriceWire.tsx`, `src/services/api/src/routes/prices.ts`

4. **Email Morning Brief (Cue Lite):**
   - Daily email at 6 AM with top 5 price movers in operator's city
   - Uses Resend API
   - Simple HTML template
   - This IS the first revenue product — operators get hooked on the email
   - **New file:** `src/services/api/src/jobs/morning-email.ts`

5. **Automated threat detection:**
   - Parse `ccc_pending_applications` for new entries near each operator
   - Generate threat records automatically when new applications filed within 5 miles
   - **File:** `src/services/api/src/jobs/threat-scanner.ts`

6. **Automated recommendation generation:**
   - Wire up `engine/generator.ts` to a daily cron
   - Generate recommendations for all active operators after price scrape
   - **File:** `src/services/api/src/jobs/generate-recs.ts`

**Dependencies:** Phase 2A complete (7+ days of data, all imports done)  
**Estimated effort:** 32-40 hours  
**Success criteria:**
- ✅ Morning Brief shows real 24h price movers
- ✅ Sparklines render real 7-day trends
- ✅ Email morning brief sends to test operators
- ✅ Automated threat + recommendation generation running daily
- ✅ 0 fake/mock data visible to users

---

### Phase 3: Margin Engine (AI Pricing Recommendations)

**Goal:** Deliver personalized, actionable pricing recommendations that operators can apply with one click.

**Tasks:**

1. **Connect elasticity model to real data:**
   - `engine/elasticity.ts` exists but needs 30+ days of price data
   - Until then, use rule-based recommendations (already in `engine/rules.ts`)
   - Cross-reference with CCC official prices for validation
   - **Files:** `src/services/api/src/engine/generator.ts`, `src/services/api/src/engine/elasticity.ts`

2. **Recommendation UI polish:**
   - "Apply" → creates a task/note (no POS integration yet)
   - "Dismiss with reason" → feeds back to model
   - Confidence score visualization
   - Expected impact visualization (revenue/margin delta)
   - **File:** `src/apps/web/src/pages/Recommendations.tsx`

3. **Report Card v2:**
   - Add THC integrity section (menu THC vs lab test THC)
   - Add historical grade tracking (grade trend over weeks)
   - PDF export for weekly review
   - **Files:** `src/services/api/src/routes/report-card.ts`, `src/services/api/src/routes/scores.ts`

4. **Margin rules UI:**
   - Let operators set min/max price guardrails per category
   - Alert when market moves push them outside their rules
   - **File:** `src/apps/web/src/pages/Settings.tsx` (replace mock content)

5. **Price simulation:**
   - "What if I drop flower by $3?" → projected impact
   - Uses elasticity curves from 30+ days of data
   - **New file:** `src/services/api/src/routes/simulate.ts`

**Dependencies:** Phase 2B complete (30+ days of data for meaningful elasticity)  
**Estimated effort:** 40-48 hours  
**Success criteria:**
- ✅ Operators receive 3+ recommendations per week
- ✅ "Apply/Dismiss" workflow functional
- ✅ Report Card includes THC integrity
- ✅ Price simulation endpoint working

---

### Phase 4: Outreach + Onboarding (First 20 Operators)

**Goal:** Get 20 MA cannabis operators actively using GLASS weekly.

**Tasks:**

1. **Outreach email sequence:**
   - Build list of 50 target operators from DB (prioritize operators with good data coverage)
   - Query: `SELECT o.name, o.city, o.email FROM operators o JOIN prices p ON p.operator_id = o.id GROUP BY o.id HAVING COUNT(*) > 50 ORDER BY COUNT(*) DESC LIMIT 50`
   - 3-email sequence: (1) "Your store vs market" teaser, (2) "Here's what your competitors changed", (3) "Claim your free dashboard"
   - Use Resend API
   - **New files:** `src/scripts/outreach/`

2. **GA4 analytics deployment:**
   - GA4 tag already in code (`G-HJ72X18ZDN`) with `usePageTracking()` hook
   - Verify it's firing in production
   - Set up conversion events: signup, onboarding complete, first login
   - **File:** `src/apps/web/src/App.tsx` (already has tracking)

3. **Onboarding polish:**
   - Ensure operator search returns relevant results fast
   - Add "Invite a colleague" CTA after onboarding
   - Auto-generate first report card on signup
   - **File:** `src/apps/web/src/pages/Onboarding.tsx`

4. **Landing page optimization:**
   - Add real market stats to landing page ("517 dispensaries tracked", "100K+ products")
   - Social proof section
   - "See your store" instant preview (public report card link)
   - **File:** `src/apps/web/src/pages/Landing.tsx`

5. **LinkedIn prospecting script:**
   - Already started: `src/scripts/linkedin-prospecting/`
   - Finalize outreach sequence and target list
   - Track responses in DB or spreadsheet

**Dependencies:** Phase 2B complete (real data to show in outreach emails)  
**Estimated effort:** 20-24 hours  
**Success criteria:**
- ✅ 50 outreach emails sent
- ✅ 20 operators with active accounts
- ✅ 5+ operators logging in weekly
- ✅ GA4 tracking confirmed working
- ✅ Conversion funnel measurable

---

### Phase 5: Revenue Spokes (Cue Integration, Newsletter Monetization)

**Goal:** Generate first revenue — $199/mo Cue subscriptions + newsletter sponsorships.

**Tasks:**

1. **Cue MVP (Budtender Incentive System):**
   - Brand creates incentive: "Sell 10 units of [product], earn $50"
   - Budtender view shows active incentives
   - Operator dashboard shows incentive performance
   - **This is brand-funded — operators pay $0**
   - Build: brand portal, budtender mobile view, incentive CRUD
   - **Files:** `src/apps/web/src/pages/Cue.tsx` (replace mock), new API routes

2. **Cue Starter subscription ($199/mo):**
   - Daily SMS/email price alerts (from Morning Brief data)
   - Weekly PDF report card
   - Monthly margin analysis
   - Stripe integration for payments
   - **New files:** `src/services/api/src/routes/billing.ts`, `src/services/api/src/jobs/weekly-pdf.ts`

3. **Newsletter launch ("The GLASS Weekly"):**
   - Weekly market digest email to all subscribers
   - Top price movers, CCC alerts, market trends
   - Beehiiv or Resend for delivery
   - Sponsorship slots: $200-500/week for brand mentions
   - **File:** `src/apps/web/src/pages/Newsletter.tsx` (already exists)

4. **Auto-invite system:**
   - Already started: `src/scripts/auto-invite/`
   - Automated drip sequence for new signups
   - Onboarding email + 3-day check-in + 7-day report card email

**Dependencies:** Phase 4 complete (20+ active operators), Phase 2B (reliable daily data)  
**Estimated effort:** 48-60 hours  
**Success criteria:**
- ✅ 3-5 operators on Cue Starter ($600-1,000 MRR)
- ✅ Newsletter sending weekly to 50+ subscribers
- ✅ First sponsorship revenue
- ✅ Stripe billing integrated
- ✅ PDF report card generating

---

### Phase 6: Scale (Full MA Coverage, Daily Reliability)

**Goal:** Cover the entire MA market with daily reliability. 150+ operators on free tier, 25+ paying.

**Tasks:**

1. **Full Weedmaps coverage:**
   - After Phase 2A fixes, expand to all 282 Weedmaps stores
   - Add Leafly, Jane, iHeartJane scrapers
   - Target: 450+/472 operators with daily data

2. **Scraper monitoring & alerting:**
   - Automated Slack/email alerts on scrape failures
   - Dashboard showing scrape health by platform
   - Auto-retry failed stores

3. **Performance optimization:**
   - Implement Redis caching for hot endpoints
   - Consider ClickHouse for time-series queries at scale
   - Optimize report-card queries (currently complex 20s-timeout SQL)

4. **Agency services (Roviq):**
   - Package GLASS data into client reports
   - Offer $3K "Growth Sprint" consulting packages
   - Use GLASS insights to justify ad spend recommendations

5. **AC Toll Processing integration:**
   - White-label manufacturing workflow
   - "Request Quote" from Margin Engine recommendations
   - Partnership agreements with manufacturers

6. **Delivered integration:**
   - Delivery toggle per zip code
   - License MD1303 integration
   - Revenue share model (15% GMV)

**Dependencies:** Phases 2-5 complete, 50+ active operators  
**Estimated effort:** 80-100 hours  
**Success criteria:**
- ✅ 450+ operators with daily price data
- ✅ 99%+ scraper uptime over 30 days
- ✅ 150+ free operators, 25+ paying
- ✅ $5,000+ MRR
- ✅ Newsletter with 200+ subscribers

---

## 5. Critical Path — This Week

### The 5 things that MUST happen this week:

#### 1. 🔴 Fix Weedmaps Scraper (Priority: CRITICAL)
**Why:** 273 operators (58% of the market) are Weedmaps-sourced. With 5.8% success rate, most of MA is invisible.  
**Action:** Debug `src/scripts/scrape-weedmaps.ts`. Run single-store test, compare DOM/API response to parser expectations. Fix extraction logic.  
**Effort:** 8-12 hours  
**Owner:** Backend developer  
**Success:** >70% Weedmaps success rate in a full run

#### 2. 🔴 Deploy Daily Scrape Cron (Priority: CRITICAL)
**Why:** Without daily scraping, there's no time-series data, no price movers, no trends, no Morning Brief value. Right now 99.9% of data is from ONE day.  
**Action:** Add Railway cron job or external scheduler (e.g., GitHub Actions) to run `daily-scrape.ts` at 4 AM ET daily.  
**Effort:** 2-3 hours  
**Owner:** DevOps  
**Success:** 3+ consecutive days of automated scrape runs visible in `scrape_runs` table

#### 3. 🟡 Run Missing Database Migrations (Priority: HIGH)
**Why:** `operator_scores` table doesn't exist, materialized views don't exist, `refresh_health_scores()` function doesn't exist. The health score feature — which is referenced throughout the frontend — is completely broken.  
**Action:** Write and run migration creating `operator_scores` table, materialized views, and refresh function. Then run initial score calculation.  
**Effort:** 4-6 hours  
**Owner:** Backend developer  
**SQL needed:**
```sql
-- From schema.ts definition
CREATE TABLE operator_scores (...);
CREATE MATERIALIZED VIEW mv_operator_health AS ...;
CREATE MATERIALIZED VIEW mv_thc_integrity AS ...;
CREATE FUNCTION refresh_health_scores() RETURNS void AS ...;
```

#### 4. 🟡 Import Remaining CCC Datasets (Priority: HIGH)
**Why:** `ccc_facility_sales` (0 rows), `ccc_licenses` (0 rows), `ccc_monthly_prices` (0 rows) — these power the cross-reference analysis and market context. CSVs already exist locally.  
**Action:** Write import scripts modeled on `import-lab-tests.ts`. Run imports.  
**Effort:** 4-6 hours  
**Owner:** Backend developer  
**Success:** All CCC tables populated, `/ccc/cross-reference` returns richer data

#### 5. 🟡 Update Operator Statuses + First Outreach Draft (Priority: HIGH)
**Why:** 464/473 operators are "pending" status even though 301 have price data. Need to activate them AND draft the first outreach email.  
**Action:**
- Run: `UPDATE operators SET status = 'active' WHERE id IN (SELECT DISTINCT operator_id FROM prices)`
- Draft 3-email outreach sequence
- Identify first 25 target operators (best data coverage, known owners)  
**Effort:** 3-4 hours  
**Owner:** COO + marketing  
**Success:** 301 operators marked active, outreach draft ready to review

---

## Appendix A: Full Endpoint Inventory

### Public Endpoints (no auth)
| Method | Path | Working |
|--------|------|---------|
| GET | `/health` | ✅ |
| GET | `/metrics` | ✅ (admin key) |
| POST | `/api/v1/auth/signup` | ✅ |
| POST | `/api/v1/auth/login` | ✅ |
| GET | `/api/v1/auth/callback` | ✅ |
| POST | `/api/v1/waitlist` | ✅ |
| POST | `/api/v1/newsletter/subscribe` | ✅ |
| GET | `/api/v1/operators/search` | ✅ |
| GET | `/api/v1/ccc/weekly-sales` | ✅ |
| GET | `/api/v1/ccc/avg-prices` | ✅ |
| GET | `/api/v1/ccc/pending-applications` | ✅ |
| GET | `/api/v1/ccc/demographics` | ✅ |
| GET | `/api/v1/ccc/cross-reference` | ✅ |
| GET | `/api/v1/ccc/data-freshness` | ✅ |
| GET | `/api/v1/ccc/plant-activity` | ✅ |
| GET | `/api/v1/ccc/plant-activity/summary` | ✅ |
| GET | `/api/v1/report-card/:operator_id` | ✅ (no auth!) |
| GET | `/api/v1/report-card/summary/:operator_id` | ✅ (no auth!) |
| GET | `/api/v1/market/health-leaders` | ❌ (`operator_scores` missing) |
| GET | `/api/v1/admin/data-quality` | ✅ (admin key) |
| GET | `/api/v1/admin/duplicate-products` | ✅ (admin key) |
| POST | `/api/v1/admin/scores/recalculate` | ❌ (matviews missing) |

### Authenticated Endpoints (Clerk JWT)
| Method | Path | Working |
|--------|------|---------|
| GET | `/api/v1/operators/me/scores` | ❌ (`operator_scores` missing) |
| GET | `/api/v1/operators/:id/health-score` | ❌ (matviews missing) |
| GET | `/api/v1/operators/:id/thc-integrity` | ⚠️ (falls back to live query) |
| GET | `/api/v1/prices` | ✅ |
| GET | `/api/v1/prices/movers` | ⚠️ (needs multi-day data) |
| GET | `/api/v1/prices/categories` | ✅ |
| GET | `/api/v1/products` | ✅ |
| GET/POST | `/api/v1/watchlists` | ✅ (empty) |
| GET | `/api/v1/threats` | ⚠️ (6 seed records) |
| GET | `/api/v1/threats/feed` | ⚠️ (6 seed records) |
| GET | `/api/v1/recommendations` | ⚠️ (6 seed records) |
| POST | `/api/v1/recommendations/generate` | ✅ |
| GET | `/api/v1/margin-rules` | ✅ |
| GET | `/api/v1/alerts` | ⚠️ (10 seed records) |
| GET | `/api/v1/dashboard` | ✅ |
| GET | `/api/v1/profile` | ✅ |
| GET | `/api/v1/exports/:type` | ✅ |
| GET | `/api/v1/viz/*` | ✅ |

---

## Appendix B: File Reference

```
src/
├── services/api/src/
│   ├── index.ts                    # Server bootstrap, route registration
│   ├── db/
│   │   ├── schema.ts              # Full Drizzle ORM schema (26 tables)
│   │   └── index.ts               # DB connection (postgres.js)
│   ├── routes/                     # 21 route files
│   │   ├── auth.ts                # Clerk auth flow
│   │   ├── operators.ts           # Operator CRUD + search
│   │   ├── prices.ts              # Price queries + movers
│   │   ├── products.ts            # Product catalog
│   │   ├── dashboard.ts           # Morning Brief aggregate
│   │   ├── report-card.ts         # Store report cards (700+ lines)
│   │   ├── scores.ts              # Health scores (broken - missing table)
│   │   ├── ccc.ts                 # CCC state data (7 endpoints)
│   │   ├── viz.ts                 # D3 visualization data
│   │   ├── threats.ts             # Threat radar
│   │   ├── recommendations.ts     # AI recommendations
│   │   ├── margin-rules.ts        # Pricing guardrails
│   │   ├── watchlists.ts          # Product watch alerts
│   │   ├── alerts.ts              # User notifications
│   │   ├── sources.ts             # Scrape source management
│   │   ├── exports.ts             # CSV exports
│   │   ├── profile.ts             # User profile
│   │   ├── newsletter.ts          # Newsletter subscribe
│   │   └── waitlist.ts            # Waitlist signup
│   ├── engine/                     # Margin Engine v1
│   │   ├── elasticity.ts          # Price elasticity estimation
│   │   ├── generator.ts           # Recommendation generation
│   │   └── rules.ts               # Rule violation evaluator
│   ├── plugins/
│   │   └── auth.ts                # Clerk JWT + JWKS verification
│   └── utils/
│       ├── rate-limit.ts          # Token bucket rate limiter
│       └── data-quality.ts        # Price limit helpers
│
├── apps/web/src/
│   ├── App.tsx                    # Router (17 routes)
│   ├── pages/                     # 17 page components
│   │   ├── Landing.tsx            # Public marketing page
│   │   ├── Market.tsx             # Public market data (37KB)
│   │   ├── MorningBrief.tsx       # Dashboard home (32KB)
│   │   ├── PriceWire.tsx          # Price intelligence (22KB)
│   │   ├── Onboarding.tsx         # 4-step onboarding (20KB)
│   │   ├── Newsletter.tsx         # Newsletter page (15KB)
│   │   ├── Budtender.tsx          # [PAUSED] Budtender view
│   │   ├── Cue.tsx                # [FUTURE] Brand incentives
│   │   ├── Delivery.tsx           # [FUTURE] Delivery toggle
│   │   ├── ThreatRadar.tsx        # Threat map
│   │   ├── Alerts.tsx             # Alert management
│   │   ├── Recommendations.tsx    # AI recommendations
│   │   ├── Settings.tsx           # User settings [MOCK]
│   │   ├── Competitors.tsx        # Competitor view [THIN]
│   │   ├── Geography.tsx          # Geo view [THIN]
│   │   └── Admin.tsx              # Admin dashboard [NO AUTH]
│   ├── api/
│   │   ├── client.ts              # API client wrapper
│   │   └── hooks.ts               # TanStack Query hooks (20+)
│   └── lib/
│       ├── onboarding.ts          # Onboarding state
│       └── waitlist.ts            # Waitlist helpers
│
├── scripts/
│   ├── daily-scrape.ts            # Daily scrape orchestrator [NOT CRONNED]
│   ├── scrape-dutchie-ma.ts       # Dutchie scraper (25KB)
│   ├── scrape-weedmaps.ts         # Weedmaps scraper (21KB) [5.8% SUCCESS]
│   ├── geocode-operators.ts       # Geocoding script
│   ├── import-ccc-data.ts         # CCC data importer
│   ├── import/
│   │   ├── import-lab-tests.ts    # Lab test importer (recently fixed)
│   │   └── lib/etl-base.ts        # ETL utilities
│   ├── lib/
│   │   ├── brand-filter.ts        # Brand name validation
│   │   ├── normalizer.ts          # Product normalization
│   │   ├── browser-pool.ts        # Camofox browser management
│   │   ├── db.ts                  # Direct DB helpers for scripts
│   │   ├── config.ts              # Shared configuration
│   │   └── types.ts               # Shared types
│   └── migrations/
│       ├── 001-scraper-v2.sql
│       ├── 002-price-idempotency.sql
│       ├── 003-data-quality-infra.sql
│       ├── 004-merge-duplicate-operators.sql
│       └── 005-performance-indexes.sql
│
└── data/ccc-raw/
    ├── testing-thc-thca.csv       # 29.6MB → imported ✅
    ├── facility-sales-stats.csv   # 7.9MB → NOT imported ❌
    ├── itd-retail-delivery-sales.csv # 7.9MB → NOT imported ❌
    ├── medical-facility-stats.csv # 4.9MB → NOT imported ❌
    ├── commence-ops.csv           # 652KB → NOT imported ❌
    ├── avg-monthly-price-oz.csv   # 1.5KB → NOT imported ❌
    └── adult-market-data-counties.csv # 1.6MB → partially imported
```

---

## Appendix C: Revenue Path Summary

| Week | Action | Milestone |
|------|--------|-----------|
| **Week 1** (Feb 12-18) | Fix Weedmaps scraper, deploy cron, run migrations, import CCC data | Data foundation solid |
| **Week 2** (Feb 19-25) | Accumulate 7 days data, build email morning brief, draft outreach | First automated emails |
| **Week 3** (Feb 26-Mar 4) | Send outreach to 25 operators, track signups, polish onboarding | 10+ signups |
| **Week 4** (Mar 5-11) | Demo to engaged operators, build Cue Starter billing | First conversations |
| **Week 5** (Mar 12-18) | Launch Cue Starter ($199/mo), launch newsletter | **First revenue** |
| **Week 6-8** | Expand to 50 operators, iterate on product | $1,000-2,000 MRR |

**The single most important metric right now:** Days of consecutive automated scrape data. Every day without scraping is a day the time-series moat isn't growing.

---

*Generated 2026-02-12. Based on production DB queries, full codebase review, and scrape run analysis.*
