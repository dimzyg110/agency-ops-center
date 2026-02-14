# GLASS Repo Audit — Part 2: Codebase Health & Deployment

Audit target: `/data/workspace/projects/glass/src/`  
Audit time: 2026-02-14 UTC

---

## Task 1 — Service Build & Deployment Readiness

## 1) `services/api/`

**Dockerfile validity:** ⚠️ Mostly valid, but build currently fails at TypeScript stage.
- Dockerfile compiles with `npx tsc -p tsconfig.json` and runs `node dist/index.js`.
- Entry point in Dockerfile matches package scripts (`src/index.ts` → `dist/index.js`).

**Dependencies:** ✅ `services/api/package.json` exists and is populated.

**TypeScript compilation status (actual run):** ❌ Fails
- `src/routes/health-sources.ts`: Drizzle `eq(..., null)` type mismatch (`run_id` nullable comparisons)
- `src/routes/pos-api-integration.ts`: type mismatch at line ~411 (object vs string[])
- `src/services/source-priority.ts`: same nullable `run_id` typed comparison issue

**Entry point correctness:** ✅ `dist/index.js` is correct target for built output.

**Environment variables needed (from code):**
- Required in production: `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGIN`, `CLERK_SECRET_KEY`, `CLERK_PUBLISHABLE_KEY` (or `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`)
- Optional/feature flags: `PORT`, `HOST`, `LOG_LEVEL`, `ADMIN_API_KEY`, `BEEHIIV_API_KEY`, `BEEHIIV_PUBLICATION_ID`, `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID`, `STRIPE_WEBHOOK_SECRET`, `ROVIQ_SERVICE_API_KEYS`, `NODE_ENV`

**Railway deployment:** ✅ Yes
- Root `railway.toml` points at `services/api/Dockerfile`

---

## 2) `apps/web/`

**Dockerfile validity:** ✅ Structurally valid multi-stage Vite build Dockerfile.

**Dependencies:** ✅ `apps/web/package.json` exists.

**Build status (actual run):** ❌ Fails in current checkout
- `npm run build` -> `sh: 1: vite: not found`
- Indicates dependency installation/state issue in current workspace (`node_modules/.bin/vite` missing), not necessarily Dockerfile logic.

**Entry point correctness:** ✅ Build outputs `dist/`; runtime serves with `serve -s dist -l 3000`.

**Environment variables needed:**
- Build/runtime frontend vars: `VITE_API_URL`, `VITE_CLERK_PUBLISHABLE_KEY`

**Railway deployment:** ✅ Yes
- `railway-web.toml` and `apps/web/railway.toml` both define web deployment via `apps/web/Dockerfile`

---

## 3) Scrapers (`scrapers/{dutchie,jane,leafly,weedmaps}`)

Shared observations:
- Each scraper has its own Dockerfile and Railway cron config.
- All Dockerfiles install Node 22 + `tsx`, install `scrapers/package.json` deps, copy shared libs + scraper entrypoint.
- Entry commands are aligned with files (`tsx <scraper>/index.ts`).

### a) `scrapers/dutchie/`
- **Dockerfile:** ✅
- **Dependencies:** ✅ via `scrapers/package.json`
- **Entry point:** ✅ `tsx dutchie/index.ts`
- **Env vars used:** `DATABASE_URL`, `DISCORD_WEBHOOK_URL`, `HEADLESS`, `MAX_TIMEOUT_MS`, `DUTCHIE_SHARD_COUNT`, `CAMOUFOX_BIN_PATH` (plus cache vars)
- **Railway deployed:** ✅ `scrapers/dutchie/railway.toml` (cron)

### b) `scrapers/jane/`
- **Dockerfile:** ✅
- **Dependencies:** ✅
- **Entry point:** ✅ `tsx jane/index.ts`
- **Env vars used:** `DATABASE_URL`, `DISCORD_WEBHOOK_URL`, `HEADLESS`, `MAX_TIMEOUT_MS`, `JANE_ALGOLIA_APP_ID`, `JANE_ALGOLIA_API_KEY`, `JANE_PRODUCTS_INDEX`, `JANE_STORES_INDEX`, `JANE_STATE_FILTER`
- **Railway deployed:** ✅ `scrapers/jane/railway.toml` (cron)

### c) `scrapers/leafly/`
- **Dockerfile:** ✅
- **Dependencies:** ✅
- **Entry point:** ✅ `tsx leafly/index.ts`
- **Env vars used:** `DATABASE_URL`, `DISCORD_WEBHOOK_URL`, `HEADLESS`, `MAX_TIMEOUT_MS`
- **Railway deployed:** ✅ `scrapers/leafly/railway.toml` (cron)

### d) `scrapers/weedmaps/`
- **Dockerfile:** ✅
- **Dependencies:** ✅
- **Entry point:** ✅ `tsx weedmaps/index.ts`
- **Env vars used:** `DATABASE_URL`, `DISCORD_WEBHOOK_URL`, `HEADLESS`, `MAX_TIMEOUT_MS`, `WEEDMAPS_CAMOFOX_URL`
- **Railway deployed:** ✅ `scrapers/weedmaps/railway.toml` (cron)

---

## 4) `services/gpid-verify/`

**What it does:**
- Lightweight Express + Postgres verification UI/API for GPID candidate pair review.
- Serves HTML UI (`verification-ui.html`) and APIs:
  - `GET /api/candidates`
  - `GET /api/progress`
  - `POST /api/verdicts`
  - `GET /health`
- Ensures `gpid_candidates` and `gpid_verdicts` tables exist on startup.

**Dockerfile validity:** ⚠️ Works but brittle
- Copies root `package.json` + lockfile and `verification-server.ts`.
- Installs prod deps (`npm ci --omit=dev`) with fallback `npm install express pg`.
- Runs `npx tsx server.ts` at runtime (tsx is typically dev dependency); can rely on npx download behavior.

**Dependencies:** ⚠️ Indirect/fragile
- No service-local `package.json`; piggybacks root package.
- `tsx` is not explicitly installed in production image except via npx behavior.

**Entry point correctness:** ✅ `server.ts` exists and starts Express app.

**Environment variables needed:**
- Required: `DATABASE_URL`
- Optional: `PORT` (default 3847), `VERIFICATION_LIMIT` (default 200), `VERIFICATION_UI_PATH`, `NODE_ENV`

**Railway deployment:** ✅ Yes
- `services/gpid-verify/railway.toml` points to its Dockerfile.

---

## 5) `services/intelligence/`

**Status:** ⚠️ Likely dormant/not deployed
- Has full TS service structure and package.json.
- No Dockerfile.
- No Railway config for this service.
- Not referenced by active deployment manifests.

**Dependencies:** ✅ present (`package.json` + lockfile).

**Entry point:** ✅ `src/index.ts` (scripts include `build`, `dev`, `start`).

**Environment variables:**
- No direct `process.env.*` references detected in `src/` (uses dotenv/postgres/bullmq stack; likely expects DB/Redis config from internal modules but not explicitly wired in current grep).

**Railway deployment:** ❌ No direct deployment manifest found.

**Conclusion:** treat as **inactive/experimental** until explicitly wired to infra.

---

## 6) `services/scrape/`

**Status:** ❌ Dead code / not deployable as-is
- Directory contains only `dist/` and `node_modules/` artifacts.
- Missing source (`src/`), missing `package.json`, missing Dockerfile, missing Railway config.
- Repo CONTRIBUTING.md explicitly marks `services/scrape/` as dead code replaced by `scripts/`.

**Dependencies:** ❌ no canonical manifest in service folder.

**Entry point:** ⚠️ compiled artifact exists (`dist/index.js`) but no build/deploy contract.

**Environment variables (from dist scan):** references `DATABASE_URL`, `REDIS_URL`, `FIRECRAWL_*`, scrape scheduler/concurrency vars.

**Railway deployment:** ❌ No.

---

## Task 2 — Stale Branches Audit (24 unmerged remote branches)

Command used:
`git branch -r --no-merged origin/main --format='%(refname:short) %(committerdate:short) %(subject)'`

| Branch | Last commit (date + subject) | Superseded by merged work? | Recommendation |
|---|---|---|---|
| origin/codex/backend-skeleton | 2026-02-11 — fix: request.jwtUser → request.auth in watchlists (runtime crash) | Partially (older backend stabilization lane, overlaps with other backend fixes) | **Delete** unless you want archival reference |
| origin/codex/phase3-pricewire | 2026-02-11 — fix(phase3): reviewer feedback | Likely superseded by later API/web evolution | **Delete** |
| origin/codex/platform-infra | 2026-02-11 — CI node 20→22 | Likely partly superseded; infra lane not currently active in deployment manifests | **Delete** or cherry-pick specific infra commits then delete |
| origin/codex/scrape-core | 2026-02-11 — scrape-core critical fixes | Targets now-dead `services/scrape` lane | **Delete** |
| origin/codex/threat-intel | 2026-02-11 — intelligence fixes | Not deployed currently | **Keep only if intelligence revival planned**, else delete |
| origin/contracts/v1 | 2026-02-11 — contracts fixes | Contracts likely stale vs runtime | **Delete** |
| origin/contracts/v2-audit-fixes | 2026-02-11 — auth/logout security fix + mixed web files | Mixed lane likely superseded | **Delete** |
| origin/feat/llm-parser-poc | 2026-02-14 — LLM parser POC | New experimental work, not merged | **Keep (short-term)** |
| origin/feat/testing-plan | 2026-02-14 — GPID testing strategy/tests | New and potentially useful | **Keep** |
| origin/fix/camoufox-binary-path | 2026-02-13 — add fingerprint-generator dep | Narrow, still relevant to scraper hardening | **Keep until verified merged/cherry-picked** |
| origin/fix/consolidate-public-schema | 2026-02-14 — gpid verification perf precompute | Appears patch-equivalent to merged work (cherry showed `minus`) | **Delete** |
| origin/fix/jane-evaluate-fetch | 2026-02-13 — Jane CF clearance change | Recent scraper fix | **Keep** |
| origin/fix/leafly-direct-http | 2026-02-13 — Leafly direct HTTP | Recent scraper experiment/fix | **Keep** |
| origin/fix/weedmaps-dutchie-plain-firefox | 2026-02-13 — plain Firefox for WM/Dutchie | Recent scraper fix | **Keep** |
| origin/kimi/frontend-shell-v2 | 2026-02-11 — full web shell | Appears superseded (patch-equivalent seen) | **Delete** |
| origin/kimi/frontend-stabilize | 2026-02-11 — frontend stabilization | Appears superseded (patch-equivalent seen) | **Delete** |
| origin/kimi/phase3-morning-brief | 2026-02-11 — frontend review fixes | Possibly superseded by later web changes | **Delete** unless page-level diffs still desired |
| origin/opus/backend-stabilize | 2026-02-11 — backend stabilize fixes | Old stabilization lane likely superseded | **Delete** |
| origin/opus/phase5-margin-engine | 2026-02-11 — margin-engine route ordering/spec | Might still contain unmerged route/spec deltas | **Keep only if margin engine still roadmap**, else delete |
| origin/wartime/phase0-quarantine | 2026-02-14 — migration 014 quarantine | Active wartime stream | **Keep** |
| origin/wartime/phase1-brand-authority | 2026-02-14 — brand authority scripts/reports | Active wartime stream | **Keep** |
| origin/wartime/phase3-gpid-lock | 2026-02-14 — deterministic GPID lock/QA | Active wartime stream | **Keep** |
| origin/wartime/phase4-consumer-api | 2026-02-14 — consumer GPID endpoints | Active consumer pivot work | **Keep (high priority)** |
| origin/wartime/sprint-review-fixes | 2026-02-14 — sprint review fixes | Active wartime stream | **Keep** |

**Practical cleanup suggestion:**
- Immediate delete candidates: old codex/kimi/opus/contracts lanes from 2026-02-11 not in current active plan.
- Keep all `wartime/*` + recent scraper fixes + `feat/testing-plan` + `feat/llm-parser-poc` until merged/rebased decision.

---

## Task 3 — API Route Audit (29 files)

Legend:
- **Impl**: Implemented / Partial / Stub
- **DB fit**: Does route align with current DB objects present in Railway Postgres (`public` + `glass`)
- **Consumer need**: Yes / Maybe / No (for consumer-first `glassintel.xyz/prices` pivot)

| Route file | Impl | DB fit | Consumer need | Notes |
|---|---|---|---|---|
| admin-vb.ts | Implemented | Yes | No | Virtual Budtender tenant admin (B2B/internal) |
| alerts.ts | Implemented | Yes (`alerts`) | No | Operator alert inbox |
| auth.ts | Implemented | Yes (`users`, `refresh_tokens`) | Maybe | Needed if consumer product retains accounts |
| billing.ts | Implemented | Yes | No | Stripe/B2B subscription flows |
| budtender-api.ts | Implemented | Yes (`budtender_*`) | No | B2B telemetry ingestion |
| catalog.ts | Implemented | Yes | Maybe | Service feed; not core consumer prices UI |
| ccc.ts | Implemented | Yes (CCC tables present) | Maybe | Public state datasets can support consumer context |
| consumer.ts | Implemented | Yes (`verified_gpids`, `product_verified_gpids`, `prices`, etc.) | **Yes** | Consumer-critical |
| dashboard.ts | Implemented | Yes | No | Operator morning brief |
| ecosystem.ts | Implemented | Yes (`ecosystem_events`) | No | B2B ecosystem telemetry |
| exports.ts | **Partial** | Yes | No | `/exports/report` explicitly returns 501 stub |
| health-sources.ts | Implemented (but TS compile issue) | Yes | Maybe | Operational health endpoint; currently blocks build via TS issues |
| margin-rules.ts | Implemented | Yes (`margin_rules`) | No | B2B pricing ops |
| match-validation.ts | Implemented | Yes (`match_validation_samples`) | Maybe | Data quality for matching pipeline |
| newsletter.ts | Implemented | Yes (`waitlist`) | Maybe | Consumer growth capture |
| operators.ts | Implemented | Yes (`operators`) | **Yes** | Consumer-critical for operator search/listing |
| pos-api-integration.ts | **Partial** | Yes (`pos_connections`) | No | Has multiple TODO placeholders for real provider integrations |
| prices.ts | Implemented | Yes (`prices`, `products`, etc.) | **Yes** | Consumer-critical |
| products.ts | Implemented | Yes (`products`) | **Yes** | Consumer-critical |
| profile.ts | Implemented | Yes | No | Authenticated operator profile |
| public-report-card.ts | Implemented | Yes | Maybe | Public-facing but not core /prices surface |
| recommendations.ts | Implemented | Yes (`recommendations`) | No | B2B recommendation workflows |
| report-card.ts | Implemented | Yes | No | Deep operator intelligence report |
| scores.ts | Implemented | Yes (`operator_scores`) | Maybe | Could be exposed in consumer rankings |
| sources.ts | Implemented | Yes (`sources`) | **Yes** | Consumer-critical per prompt |
| threats.ts | Implemented | Yes (`threats`) | No | B2B threat/risk intelligence |
| viz.ts | Implemented | Mostly yes | No | Large B2B visualization suite |
| waitlist.ts | Implemented | Yes (`waitlist`) | Maybe | Consumer acquisition funnel |
| watchlists.ts | Implemented | Yes (`watchlists`) | No | B2B operator watchlists |

### Route-level conclusions

1. **Consumer-critical routes exist and are implemented:** `consumer.ts`, `products.ts`, `prices.ts`, `operators.ts`, `sources.ts`.
2. **Known partial/stub routes:**
   - `exports.ts` has explicit 501 for report endpoint.
   - `pos-api-integration.ts` contains TODO/mock placeholders for real Dutchie/Jane/Clover integrations.
3. **Build blocker in consumer-adjacent codebase:** API route TS errors currently prevent clean service build.
4. **Large B2B surface remains active in router registration (`src/index.ts`)** and increases maintenance/deploy risk during pivot.

---

## Task 4 — Migration State

## A) SQL files present

### `src/migrations/`
- `migrations/004_matching_engine.sql`

### `src/scripts/migrations/`
- `001-scraper-v2.sql`
- `002-price-idempotency.sql`
- `003-data-quality-infra.sql`
- `004-merge-duplicate-operators.sql`
- `005-performance-indexes.sql`
- `006-ecosystem-integration.sql`
- `007-billing.sql`
- `008-vb-tenants.sql`
- `009-demand-signals-upsert-safety.sql`
- `010-sources-url-unique.sql`
- `011-pos-connections.sql`
- `012-operator-matching.sql`
- `013-fuzzy-product-matches.sql`
- `014-wartime-quarantine.sql`
- `move-glass-to-public.sql`

## B) Migration log status (queried DB)

Query run:
`SELECT * FROM glass.migration_log ORDER BY applied_at DESC LIMIT 20;`

Returned rows:
1. `012-operator-matching.sql` — applied 2026-02-13
2. `010-sources-url-unique.sql` — applied 2026-02-13
3. `011-pos-connections.sql` — applied 2026-02-13

Only **3** migrations are recorded in migration log, while **15** SQL files exist under `scripts/migrations` (+1 under `migrations`).

## C) Schema vs code expectations

- API Drizzle schema defines 26 tables; these table names are present in `public` schema in Railway DB.
- DB additionally has newer wartime/matching tables (`verified_gpids`, `product_verified_gpids`, `gpid_*`, `canonical_products`, etc.) used by consumer/matching flows.
- `glass` schema currently appears to host migration metadata + some objects, while app runtime mostly targets `public` (many routes explicitly set `search_path public` or rely on default).

### Migration state conclusion

⚠️ **Migration tracking is incomplete/inconsistent** with filesystem migration inventory.  
The database schema mostly supports current route code, but migration history does not reflect full evolution, increasing operational risk for reproducible deploys and rollback safety.

---

## Deployment Readiness Summary

### High-risk blockers (must fix before clean deploy confidence)
1. **`services/api` TypeScript build fails** (multiple compile errors).
2. **`apps/web` local build fails** (`vite` binary missing in current dependency state).
3. **Migration bookkeeping mismatch** (3 logged vs many migration files).
4. **`services/gpid-verify` packaging is brittle** (root package piggyback + runtime `npx tsx`).

### Medium-risk
1. Large B2B route surface still registered during consumer pivot.
2. `pos-api-integration.ts` and part of `exports.ts` are partial/not production-complete.
3. `services/intelligence` and `services/scrape` are not deploy-clean and should be explicitly archived or revived.

### Recommended immediate actions
1. Fix API TS errors and enforce `npm run build` in CI gate.
2. Normalize web dependency install path (workspace lock strategy) and verify Docker/local parity.
3. Introduce canonical migration runner + enforce one migration log table and complete backfill of historical entries.
4. Extract/trim non-consumer routes behind feature flags or separate service boundary.
5. Convert `services/gpid-verify` to standalone package with pinned runtime deps.
