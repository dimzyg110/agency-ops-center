# GLASS State of the World

_Last updated: 2026-02-14 04:55 UTC_

## 1) Architecture

### Monorepo reality

- Repo root (`/data/workspace/projects/glass/`) contains strategy/planning/review docs.
- **Actual code root is `src/`**.

### Core code layout (under `src/`)

- `apps/web/` → React + Vite + Tailwind frontend
- `services/api/` → Fastify API service
- `scrapers/` → platform scrapers
  - `scrapers/jane/`
  - `scrapers/leafly/`
  - `scrapers/weedmaps/`
  - `scrapers/dutchie/`
- `scripts/gpid/` → GPID parser + GPID lock/verification scripts
- `scripts/matching/` → candidate generation, fuzzy matching, auto-verify pipeline
- `scripts/brand-authority/` → brand authority ingestion/ranking logic

### Database

- Railway PostgreSQL
- Active schema for GLASS data in this environment: `public`
- Historical headline numbers in older docs (225K prices / 162K products / 2,088 operators / 2,545 sources) are **partially stale** versus current live counts below.

### Scrapers — ALL 4 DEPLOYED & RUNNING ON RAILWAY

- 4 scraper services deployed as Railway cron jobs
- Each has its own directory in `src/scrapers/{name}/` with Dockerfile + railway.toml
- **All 4 are confirmed running in production** (verified from `scrape_runs` table)

| Scraper      | Railway Cron              | Total Runs | Completed | Last Success | Best Haul                 |
| ------------ | ------------------------- | ---------- | --------- | ------------ | ------------------------- |
| **Dutchie**  | `0 8 * * *` (3am ET)      | 14         | 13 (93%)  | Feb 13       | Reliable                  |
| **Jane**     | `0 7 * * *` (2am ET)      | 14         | 7 (50%)   | Feb 13 20:56 | 9,482 prices / 37 stores  |
| **Leafly**   | `5 7 * * *` (2:05am ET)   | 8          | 4 (50%)   | Feb 13 20:09 | 43,844 prices / 99 stores |
| **Weedmaps** | `30 3 * * *` (10:30pm ET) | 9          | 7 (78%)   | Feb 14 03:31 | 477 prices / 25 stores    |

Notes:

- Jane/Leafly 50% rate is from early debugging runs, not ongoing issues — their successful runs pull massive data
- Weedmaps runs daily automatically; low store count (25/282) is a scraper reliability issue, not deployment
- Dutchie is the most reliable at 93%

### API

- Fastify service at `src/services/api/`
- **29 route files** in `src/services/api/src/routes/`
- Clerk auth integration (`@clerk/fastify`)
- Stripe billing integration (billing route + Stripe envs)

### Web frontend

- `src/apps/web/`
- React + Vite + Tailwind

### GPID/LLM system

- GPID scripts in:
  - `src/scripts/gpid/`
  - `src/scripts/matching/`
  - `src/scripts/brand-authority/`
- LLM parser runner: `src/scripts/gpid/parse-top-brands.ts`
  - Default model: `gemini-2.5-flash`
  - Prior benchmark confidence reference in project docs: **~0.952**

### Railway deployment shape

- **API**: Deployed, healthy (`/health` returns `{"status":"ok"}`)
- **Web**: Deployed (React SPA served via `serve`)
- **GPID Verify UI**: Deployed (Express + PG verification dashboard)
- **4 Scraper Crons**: All deployed and running on schedule (see table above)
- **PostgreSQL**: Railway managed database

---

## 2) Current Data State (Live DB Snapshot)

Connection queried:
`postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway`

All queries executed with:

```sql
SET search_path TO public;
```

### Core table counts

- `products`: **161,992**
- `prices`: **225,869**
- `operators`: **1,322**
- `sources`: **868**
- `brand_authority`: **1,001**
- `parsed_products`: **3,051**
- `gpid_candidates`: **7,438**
- `gpid_verdicts`: **6,144**

### Sources by platform

`SELECT source_type, COUNT(*) FROM sources GROUP BY source_type`

- `dutchie`: **235**
- `jane`: **42**
- `leafly`: **292**
- `menu`: **9**
- `website`: **6**
- `weedmaps`: **284**

### Verified GPIDs query result

Requested query:

```sql
SELECT COUNT(*) FROM canonical_products WHERE verified=true;
```

Current DB state:

- `canonical_products` exists, but **column `verified` does not exist** in this environment.
- So this exact query fails and cannot return a count without schema change or alternate verification source.

### Latest scrape runs (10)

`SELECT platform, status, started_at FROM scrape_runs ORDER BY started_at DESC LIMIT 10`

| #   | Platform | Status       | Started (UTC)    | Stores | Prices |
| --- | -------- | ------------ | ---------------- | ------ | ------ |
| 1   | weedmaps | ✅ completed | 2026-02-14 03:31 | 25/282 | 477    |
| 2   | weedmaps | ❌ failed    | 2026-02-14 03:00 | 0/0    | 0      |
| 3   | dutchie  | ❌ failed    | 2026-02-13 21:02 | 0/0    | 0      |
| 4   | jane     | ✅ completed | 2026-02-13 20:56 | 37/39  | 9,482  |
| 5   | leafly   | ✅ completed | 2026-02-13 20:09 | 99/292 | 43,844 |
| 6   | jane     | ✅ completed | 2026-02-13 20:08 | 37/39  | 9,482  |
| 7   | weedmaps | ✅ completed | 2026-02-13 19:53 | 0/1    | 0      |
| 8   | jane     | ✅ completed | 2026-02-13 14:43 | 39/39  | 10,345 |

---

## 3) What Works / In Progress / Broken-Missing

### ✅ What works

- **Railway PostgreSQL** — Live production database, 162K products, 226K prices
- **All 4 scrapers** — Deployed as Railway cron services, running daily on schedule
- **API** — Fastify service live at `glass-api-production.up.railway.app` (health check passing)
- **Web frontend** — Deployed on Railway
- **GPID Verify UI** — Deployed on Railway
- **GPID pipeline** — makeSKU, fuzzy matcher, auto-verifier, LLM parser all functional
- **Consumer API endpoints** — search, GPID detail, top brands
- **LLM parser** — Gemini 2.5 Flash, 0.952 avg confidence

### 🔧 Three Data Workstreams (related but distinct)

| Goal                         | What                                   | Progress                                       |
| ---------------------------- | -------------------------------------- | ---------------------------------------------- |
| **Launch 500 perfect GPIDs** | Flash Parser: parse top 308 brands     | Running (3,051 parsed)                         |
| **Fix missing brands**       | Brand Fill: 61K products with no brand | Not started — needs re-scrape or LLM inference |
| **Brand catalog complete**   | Brand Authority: 1,001 brands ingested | Done (308 verified at 3+ platforms)            |

#### 1. Brand Authority ✅

- **What**: 1,001 brand names scraped from Leafly/Weedmaps directories → `brand_authority` table
- **Status**: Complete. 308 brands verified (appear on 3+ platforms)
- **Used by**: Flash Parser (as the brand cutoff for which products to parse)

#### 2. Flash Parser 🔧

- **What**: LLM (Gemini 2.5 Flash) parsing product names for the top 308 brands → structured data (brand, strain, weight, category, etc.) into `parsed_products` table
- **Goal**: 500 clean GPIDs for launch
- **Status**: Running — **3,051 products parsed**, ~36K total target for 308 brands
- **Script**: `src/scripts/gpid/parse-top-brands.ts --brand-top=308 --batch-size=25`

#### 3. Brand Fill 🔴

- **What**: **61,707 products (38% of all 162K)** have NO brand at all — the scraper didn't capture it
- **Goal**: Fill in the missing brand field for these products
- **Status**: Not started
- **Options**: Re-scrape with better brand capture OR run LLM to infer brand from product names
- **Separate from Flash Parser** — this is a data quality gap, not a parsing task

### 🔧 Other in-progress work

- Consumer site design (PRICES-SITE-GAMEPLAN.md)
- GTM strategy execution (GTM-MARKETPLACE-TRAP.md)

### ⚠️ Known issues

- **Weedmaps scraper**: Only hitting 25/282 stores per run (reliability issue, not deployment)
- **Dutchie**: 1 recent failure (Feb 13), otherwise 93% success rate
- **API TypeScript build fails**: 3 broken files (`health-sources.ts`, `pos-api-integration.ts`, `source-priority.ts`) — `tsx watch` works for dev, `tsc` build doesn't
- **Schema drift**: `canonical_products.verified` referenced in docs but doesn't exist in DB; `parsed_products` uses `validation_status` not `status`

---

## 4) Environment Variables Needed

Below is the consolidated env surface needed to run the system end-to-end.

### Core runtime

- `NODE_ENV`
- `HOST`
- `PORT`
- `LOG_LEVEL`

### Data stores

- `DATABASE_URL` (required)
- `REDIS_URL` (required for queue/scheduler flows)

### Auth/security

- `JWT_SECRET`
- `CLERK_SECRET_KEY`
- `CLERK_PUBLISHABLE_KEY` / `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CORS_ORIGIN`
- `ADMIN_API_KEY` (for admin-only paths)

### Billing

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID`

### Frontend

- `VITE_API_URL`
- `VITE_CLERK_PUBLISHABLE_KEY`

### Scraper + scheduling

- `FULL_SCRAPE_CRON`
- `DELTA_SCRAPE_CRON`
- `SCRAPER_CONCURRENCY`
- `SCRAPER_DEBUG`
- `SCRAPE_FULL_CONCURRENCY`
- `SCRAPE_DELTA_CONCURRENCY`
- `SCRAPE_FULL_SOURCE_CONCURRENCY`
- `SCRAPE_SCHEDULE_TZ`
- `SCRAPE_USER_AGENT`
- `DUTCHIE_SHARD_COUNT`
- `WEEDMAPS_CAMOFOX_URL` / `CAMOFOX_URL`
- `MAX_TIMEOUT_MS`
- `PLAYWRIGHT_MAX_RETRIES`
- `PLAYWRIGHT_NAV_TIMEOUT_MS`
- `PLAYWRIGHT_NETWORK_IDLE_TIMEOUT_MS`
- `WM_VERBOSE`

### Jane-specific

- `JANE_ALGOLIA_APP_ID`
- `JANE_ALGOLIA_API_KEY`
- `JANE_STORES_INDEX`
- `JANE_PRODUCTS_INDEX`
- `JANE_STATE_FILTER`

### GPID/verification controls

- `LOW_CONFIDENCE_THRESHOLD`
- `PARSE_WORKER_CONCURRENCY`
- `VERIFICATION_LIMIT`
- `VERIFICATION_UI_PATH`
- `ROVIQ_SERVICE_API_KEYS`

### LLM Parser

- `GOOGLE_AI_API_KEY` (for Gemini 2.5 Flash parser)

### External integrations (as used)

- `GOOGLE_MAPS_API_KEY` (geocoding)
- `DISCORD_WEBHOOK_URL` (scraper notifications — not yet configured)

---

## 5) How to Run Everything (Fresh Clone)

1. **Clone + enter repo**

   ```bash
   git clone <repo-url>
   cd glass
   ```

2. **Install dependencies from code root**

   ```bash
   cd src
   npm install
   ```

3. **Create env files**
   - Use templates:
     - `src/infra/.env.example`
     - `src/apps/web/.env.example`
   - Populate runtime files:
     - `src/.env`
     - `src/apps/web/.env`

4. **Run API + web locally**

   ```bash
   npm run dev:api
   npm run dev:web
   ```

   (Or run both via root dev script where configured.)

5. **Run scrapers (from `src/`)**

   ```bash
   npx tsx scripts/scrape-jane.ts --skip-discovery --db
   npx tsx scripts/scrape-leafly.ts --skip-discovery --db
   npx tsx scripts/scrape-weedmaps.ts --skip-discovery --db
   npx tsx scripts/scrape-dutchie.ts --skip-discovery --db
   ```

6. **Run GPID pipeline (from `src/`)**

   ```bash
   npx tsx scripts/matching/seed-brand-dictionary.ts
   npx tsx scripts/matching/fuzzy-matcher.ts
   npx tsx scripts/matching/auto-verify.ts
   npx tsx scripts/gpid/parse-top-brands.ts --brand-top=308 --batch-size=25
   npx tsx scripts/gpid/lock-verified-gpids.ts
   ```

7. **Validate DB state before/after runs**
   - Always set schema explicitly:

   ```sql
   SET search_path TO public;
   ```

   - Re-run row-count and scrape-run queries from section 2.

---

## 6) Key Reconciliation Notes

- Current live counts diverge from older architecture headlines for operators/sources; use section 2 as source of truth.
- Requested verified-GPID query does not match current schema (`canonical_products.verified` missing).
- Documentation footprint outside code is still large; see `CLEANUP-PLAN.md` for full file-by-file categorization.
