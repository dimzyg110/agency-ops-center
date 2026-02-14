# GLASS State of the World

_Last updated: 2026-02-14 (UTC)_

## 1) Architecture

## Monorepo layout
- Repo root (`/data/workspace/projects/glass/`) contains strategy docs, reports, and planning artifacts.
- **Actual application code root is `src/`**.

Inside `src/`:
- `apps/web/` → React + Vite + Tailwind frontend
- `services/api/` → Fastify API service
- `scrapers/` → platform scraper implementations
  - `scrapers/jane/`
  - `scrapers/leafly/`
  - `scrapers/weedmaps/`
  - `scrapers/dutchie/`
- `scripts/gpid/` → GPID parsing + lock/QA tooling
- `scripts/matching/` → makeSKU + fuzzy matching + auto-verify tooling
- `scripts/brand-authority/` → brand authority discovery/ranking scripts

## Core platform components
- **Database:** Railway PostgreSQL, `public` schema
- **Scrapers:** Jane, Leafly, Weedmaps, Dutchie are present and operational (with Weedmaps reliability caveat)
- **API:** Fastify app at `src/services/api/`
  - 29 route files in `src/services/api/src/routes/`
  - Clerk auth integration (`@clerk/fastify`)
  - Stripe billing route (`routes/billing.ts`)
- **Web frontend:** `src/apps/web/` using React + Vite + Tailwind
- **LLM parser:** `src/scripts/gpid/parse-top-brands.ts`
  - Default model: `gemini-2.5-flash`
  - Acceptance threshold in parser logic: confidence `>= 0.8`
  - Prior benchmark target referenced in project docs: ~0.952 confidence
- **Railway services planned/deployed pattern:** API + Web + 4 scraper cron jobs

---

## 2) Current Data State (Railway Postgres)

Connection used:
`postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway`

All queries executed with:
`SET search_path TO public;`

## Table counts
- `products`: **161,991**
- `prices`: **225,868**
- `operators`: **1,322**
- `sources`: **868**
- `brand_authority`: **1,001**
- `parsed_products`: **2,111**
- `gpid_candidates`: **7,438**
- `gpid_verdicts`: **6,144**

## Sources by platform (`source_type`)
- `leafly`: **292**
- `weedmaps`: **284**
- `dutchie`: **235**
- `jane`: **42**
- `menu`: **9**
- `website`: **6**

## Verified GPIDs
Requested query was:
```sql
SELECT COUNT(*) FROM canonical_products WHERE verified=true;
```

Current schema note:
- `canonical_products` does **not** have a `verified` column in this environment.
- Closest current verification source appears to be `verified_gpids`.

Observed verification proxy counts:
- `verified_gpids`: **234**
- `verified_gpids WHERE verification_status='verified'`: **234**

## Latest scrape runs
`SELECT platform, status, started_at FROM scrape_runs ORDER BY started_at DESC LIMIT 10`

1. weedmaps | running   | 2026-02-14 03:31:39+00
2. weedmaps | failed    | 2026-02-14 03:00:29+00
3. weedmaps | running   | 2026-02-13 22:40:53+00
4. dutchie  | failed    | 2026-02-13 21:02:59+00
5. jane     | completed | 2026-02-13 20:56:29+00
6. leafly   | completed | 2026-02-13 20:09:33+00
7. jane     | completed | 2026-02-13 20:08:44+00
8. weedmaps | completed | 2026-02-13 19:53:23+00
9. leafly   | failed    | 2026-02-13 19:52:10+00
10. jane    | failed    | 2026-02-13 19:51:14+00

---

## 3) What Works

- 4 scraper stacks are implemented and running: Jane, Leafly, Weedmaps, Dutchie
  - Caveat: Weedmaps reliability remains materially worse than others
- GPID matching pipeline exists and is wired
  - makeSKU logic + fuzzy matcher + auto-verifier scripts
- LLM parser pipeline exists (`parse-top-brands.ts`) and is active with Gemini 2.5 Flash
- Brand authority subsystem exists and is populated (`brand_authority` table + scripts)
- Consumer API endpoints exist (`routes/consumer.ts`)
- Verification/match validation UI/API path exists (`routes/match-validation.ts`) and is deployed with Railway API

---

## 4) In Progress

- Flash parsing program for top brands (project target: 308 brands / 36,556 products)
- Consumer-site product direction + UX strategy (`PRICES-SITE-GAMEPLAN.md`)
- GTM and defensibility strategy (`GTM-MARKETPLACE-TRAP.md`)

---

## 5) Broken / Missing

- Weedmaps scraper instability on Railway cron (noted high fail rate in project ops docs)
- No fully launched public consumer-facing site yet
- Automated test coverage is effectively absent (`@glass/api` test script currently placeholder)
- OpenRouter-balance dependency blocks some script runs when balance is $0
- Root-level documentation sprawl (155 markdown files outside `src/`)

---

## 6) Environment Variables Needed

Below is the consolidated set observed in code and env templates.

## Core runtime / server
- `NODE_ENV`
- `HOST`
- `PORT`
- `LOG_LEVEL`

## Database / cache
- `DATABASE_URL` (required)
- `REDIS_URL` (if queue/worker paths are used)

## Auth / security
- `JWT_SECRET`
- `CLERK_SECRET_KEY`
- `CLERK_PUBLISHABLE_KEY` (or `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`)
- `CORS_ORIGIN`
- `ADMIN_API_KEY` (for protected health/metrics admin views)

## Billing
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID`

## Frontend
- `VITE_API_URL`
- `VITE_CLERK_PUBLISHABLE_KEY`

## LLM / parsing / integrations
- `GOOGLE_AI_API_KEY` (Gemini)
- `OPENAI_API_KEY` (from infra template)
- `FIRECRAWL_API_KEY`
- `FIRECRAWL_API_BASE`
- `FIRECRAWL_TIMEOUT_MS`
- `FIRECRAWL_MAX_RETRIES`

## Scraper-specific
- `SCRAPER_CONCURRENCY`
- `SCRAPER_DEBUG`
- `SCRAPE_USER_AGENT`
- `JANE_ALGOLIA_APP_ID`
- `JANE_ALGOLIA_API_KEY`
- `JANE_STORES_INDEX`
- `JANE_PRODUCTS_INDEX`
- `JANE_STATE_FILTER`
- `WEEDMAPS_CAMOFOX_URL` / `CAMOFOX_URL`
- `DUTCHIE_SHARD_COUNT`
- `MAX_TIMEOUT_MS`
- `PLAYWRIGHT_MAX_RETRIES`
- `PLAYWRIGHT_NAV_TIMEOUT_MS`
- `PLAYWRIGHT_NETWORK_IDLE_TIMEOUT_MS`
- `WM_VERBOSE`

## Scheduling / ops controls
- `FULL_SCRAPE_CRON`
- `DELTA_SCRAPE_CRON`
- `SCRAPE_FULL_CONCURRENCY`
- `SCRAPE_DELTA_CONCURRENCY`
- `SCRAPE_FULL_SOURCE_CONCURRENCY`
- `SCRAPE_SCHEDULE_TZ`
- `LOW_CONFIDENCE_THRESHOLD`
- `VERIFICATION_LIMIT`
- `PARSE_WORKER_CONCURRENCY`
- `VERIFICATION_UI_PATH`
- `ROVIQ_SERVICE_API_KEYS`

## Optional ecosystem integrations
- `BEEHIIV_API_KEY`
- `BEEHIIV_PUBLICATION_ID`
- `DISCORD_WEBHOOK_URL`
- `GOOGLE_MAPS_API_KEY`

---

## 7) How to Run Everything (Fresh Clone)

## 1) Clone
```bash
git clone <repo-url>
cd glass
```

## 2) Install dependencies
```bash
cd src
npm install
```

## 3) Set up environment
- Create and populate:
  - `src/.env` (API + scripts runtime)
  - `src/apps/web/.env` (frontend runtime)
- Use `src/infra/.env.example` and `src/apps/web/.env.example` as starting templates.

## 4) Run scrapers (examples)
From `src/`:
```bash
npx tsx scripts/scrape-jane.ts --skip-discovery --db
npx tsx scripts/scrape-leafly.ts --skip-discovery --db
npx tsx scripts/scrape-weedmaps.ts --skip-discovery --db
npx tsx scripts/scrape-dutchie.ts --skip-discovery --db
```

## 5) Run API
```bash
npm run dev:api
```

## 6) Run web app
```bash
npm run dev:web
```

## 7) Run GPID pipeline
From `src/`:
```bash
# Brand dictionary seeding
npx tsx scripts/matching/seed-brand-dictionary.ts

# Candidate matching
npx tsx scripts/matching/fuzzy-matcher.ts

# Auto verification pass
npx tsx scripts/matching/auto-verify.ts

# LLM parsing for top brands (Gemini default)
npx tsx scripts/gpid/parse-top-brands.ts --brand-top=308 --batch-size=25

# Lock verified GPIDs
npx tsx scripts/gpid/lock-verified-gpids.ts
```

---

## 8) Notes / Gaps to Resolve in Part 2

- Operator/source totals in current DB differ from earlier headline metrics (2,088 operators / 2,545 sources) and should be reconciled as environment/version drift.
- Verified GPID canonical query in prompt does not match current schema (`canonical_products.verified` missing).
- A single canonical env template for all services is still missing; current requirements are split across code + multiple env examples.
