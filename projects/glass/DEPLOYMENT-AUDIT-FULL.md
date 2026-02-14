# GLASS Repo Audit — Part 2: Deployment, Branches, API Routes, Migrations

Audit target: `/data/workspace/projects/glass/src/`
Date: 2026-02-14 (UTC)

---

## Task 1) Services Build/Deploy Audit

### 1) `services/api/`

- **Build status:** ❌ **Does not currently build**
  - Ran: `npm run build` in `services/api`
  - TypeScript compile fails with 3 blocking errors:
    - `src/routes/health-sources.ts` (Drizzle `eq(..., null)` typing mismatch)
    - `src/routes/pos-api-integration.ts` (`{}` assigned to `string[]`)
    - `src/services/source-priority.ts` (same Drizzle `eq(..., null)` mismatch)
- **Dockerfile:** present (`services/api/Dockerfile`) and structurally valid multi-stage build.
  - But Docker build will also fail at `npx tsc -p tsconfig.json` until TS errors are fixed.
- **Env vars referenced in code:**
  - Core runtime: `PORT`, `HOST`, `NODE_ENV`, `LOG_LEVEL`
  - Auth/security: `JWT_SECRET`, `CLERK_SECRET_KEY`, `CLERK_PUBLISHABLE_KEY`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CORS_ORIGIN`, `ADMIN_API_KEY`
  - DB/integrations: `DATABASE_URL`, `ROVIQ_SERVICE_API_KEYS`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID`, `BEEHIIV_API_KEY`, `BEEHIIV_PUBLICATION_ID`
- **Railway deployment:** ✅ Yes (root `railway.toml` points to `services/api/Dockerfile`).

---

### 2) `apps/web/`

- **Build status (local workspace):** ❌ **Fails in current local state**
  - Ran: `npm run build` in `apps/web`
  - Error: `vite: not found` (local dependency resolution issue in current checkout)
- **Build status (Docker intent):** ⚠️ Likely buildable in container if install step succeeds
  - Dockerfile runs `npm install` then `npm run build`; this should provide vite binary in image.
- **Dockerfile:** present (`apps/web/Dockerfile`) and valid static build + `serve` runtime.
- **Env vars referenced:**
  - `VITE_API_URL`
  - `VITE_CLERK_PUBLISHABLE_KEY`
- **Railway deployment:** ✅ Yes (`apps/web/railway.toml` and root `railway-web.toml` both target web Dockerfile).

---

### 3) Scrapers: `scrapers/{dutchie,jane,leafly,weedmaps}/`

#### Common findings
- **Dockerfiles:** ✅ all 4 present and valid; each uses Playwright base, installs Node 22 + `tsx`, copies scraper code, runs `tsx <scraper>/index.ts`.
- **Entrypoints:** ✅ all 4 have `index.ts`.
- **TypeScript strict compile (local):** ❌ fails if you run `npx tsc --noEmit` at `scrapers/` due to missing `scripts-lib` TS module resolution and typing issues.
  - Important: scrapers are run with `tsx` at runtime, not precompiled by `tsc` in Docker.
- **Railway deployment:** ✅ all 4 have dedicated `railway.toml` with cron schedules.

#### `dutchie`
- **Build/run expectation:** ✅ Docker image likely buildable; runtime uses `tsx dutchie/index.ts`.
- **Env vars referenced:**
  - `DATABASE_URL`, `DISCORD_WEBHOOK_URL`, `MAX_TIMEOUT_MS`, `DUTCHIE_SHARD_COUNT`, `CAMOUFOX_BIN_PATH`, `NODE_ENV` (+ cache/home vars)
- **Railway:** ✅ yes (`scrapers/dutchie/railway.toml`)

#### `jane`
- **Build/run expectation:** ✅ Docker image likely buildable; runtime uses `tsx jane/index.ts`.
- **Env vars referenced:**
  - `DATABASE_URL`, `DISCORD_WEBHOOK_URL`, `MAX_TIMEOUT_MS`, `JANE_ALGOLIA_APP_ID`, `JANE_ALGOLIA_API_KEY`, `JANE_STORES_INDEX`, `JANE_PRODUCTS_INDEX`, `JANE_STATE_FILTER`, `CAMOUFOX_BIN_PATH`, `NODE_ENV`
- **Railway:** ✅ yes (`scrapers/jane/railway.toml`)

#### `leafly`
- **Build/run expectation:** ✅ Docker image likely buildable; runtime uses `tsx leafly/index.ts`.
- **Env vars referenced:**
  - `DATABASE_URL`, `DISCORD_WEBHOOK_URL`, `MAX_TIMEOUT_MS`, `CAMOUFOX_BIN_PATH`, `NODE_ENV`
- **Railway:** ✅ yes (`scrapers/leafly/railway.toml`)

#### `weedmaps`
- **Build/run expectation:** ✅ Docker image likely buildable; runtime uses `tsx weedmaps/index.ts`.
- **Env vars referenced:**
  - `DATABASE_URL`, `DISCORD_WEBHOOK_URL`, `MAX_TIMEOUT_MS`, `CAMOUFOX_BIN_PATH`, `NODE_ENV`
- **Railway:** ✅ yes (`scrapers/weedmaps/railway.toml`)

---

### 4) `services/gpid-verify/`

- **What it is:** A small Express + Postgres verification UI/API for human GPID verdicting.
  - Dockerfile copies `scripts/reports/verification-server.ts` and serves `verification-ui.html`.
  - Endpoints: `/api/candidates`, `/api/progress`, `/api/verdicts`, `/health`, `/`.
- **Build status:** ⚠️ **Docker packaging is present**, but it depends on root-level `package.json`/lock existing in build context and `tsx` execution via `npx` at runtime.
- **Env vars used by server code:**
  - Required: `DATABASE_URL`
  - Optional: `PORT` (default 3847), `VERIFICATION_LIMIT`, `VERIFICATION_UI_PATH`, `NODE_ENV`
- **Railway deployment:** ✅ yes (`services/gpid-verify/railway.toml`).

---

### 5) `services/intelligence/`

- **Build status (local workspace):** ❌ fails currently (`tsc: not found` in current local install state).
- **Code status:** ⚠️ **Dormant / likely not active deployment**
  - `CONTRIBUTING.md` labels it as CCC ingestion **"dormant"**.
  - Has source + package + tsconfig but **no Dockerfile** and **no Railway config** in this service directory.
- **Env vars referenced in source:**
  - `DATABASE_URL`, `REDIS_URL`, `CCC_APP_TOKEN`
- **Railway deployment:** ❌ no evidence in repo configs.

---

### 6) `services/scrape/`

- **Build status:** ❌ effectively non-buildable as a service in current repo shape.
  - Directory contains only `dist/` + `node_modules/`; no `package.json`, no `src/`, no Dockerfile.
- **Usage status:** ❌ **Dead code**
  - `CONTRIBUTING.md` explicitly: `services/scrape/ is DEAD CODE (replaced by scripts/)`.
- **Railway deployment:** ❌ no deployment config.

---

## Task 2) Stale Branches Audit (24 unmerged remote branches)

Command run:

```bash
cd /data/workspace/projects/glass/src && \
git branch -r --no-merged origin/main --format='%(refname:short) %(committerdate:short) %(subject)'
```

### Branch-by-branch review

| Branch | Summary of contents | Recommendation |
|---|---|---|
| `origin/codex/backend-skeleton` | API skeleton/auth/routes/plugin updates | **Review then delete** if superseded by current main/wartime |
| `origin/codex/phase3-pricewire` | dashboard/prices/watchlists fixes | **Review then delete** if superseded |
| `origin/codex/platform-infra` | infra docker/ci/observability files | **Keep pending infra PR** or merge; not auto-delete |
| `origin/codex/scrape-core` | old `services/scrape/src/*` work | **Delete** (targets dead `services/scrape`) |
| `origin/codex/threat-intel` | `services/intelligence/*` service work | **Archive/delete** unless intelligence is being revived |
| `origin/contracts/v1` | contracts/openapi/events updates | **Keep until contracts decisions finalized** |
| `origin/contracts/v2-audit-fixes` | contracts + web/api alignment fixes | **Review then merge/delete** |
| `origin/feat/llm-parser-poc` | experiment scripts/results only | **Delete after archiving report** |
| `origin/feat/testing-plan` | testing docs + starter tests | **Merge useful docs/tests or delete** |
| `origin/fix/camoufox-binary-path` | scraper package dep fix | **Likely merge/delete** (small hotfix branch) |
| `origin/fix/consolidate-public-schema` | GPID verification script/server tweaks | **Keep if gpid-verify is active; otherwise delete** |
| `origin/fix/jane-evaluate-fetch` | jane scraper behavior change | **Keep if not merged into scraper baseline; else delete** |
| `origin/fix/leafly-direct-http` | leafly scraper transport refactor | **Keep if current production behavior; else delete** |
| `origin/fix/weedmaps-dutchie-plain-firefox` | dutchie/weedmaps runtime changes | **Keep if in-use; else delete** |
| `origin/kimi/frontend-shell-v2` | major frontend shell commit | **Review then delete** if superseded by current web |
| `origin/kimi/frontend-stabilize` | frontend compile/auth/API stabilization | **Review then delete** if merged indirectly |
| `origin/kimi/phase3-morning-brief` | morning brief + pricewire pages | **Review then delete** if already on main |
| `origin/opus/backend-stabilize` | backend route/plugin/package fixes | **Review then delete** if superseded |
| `origin/opus/phase5-margin-engine` | margin engine + route/openapi updates | **Keep if strategic feature still pending** |
| `origin/wartime/phase0-quarantine` | migration 014 + report | **Keep (recent wartime stream)** |
| `origin/wartime/phase1-brand-authority` | brand authority scripts/reports | **Keep (recent wartime stream)** |
| `origin/wartime/phase3-gpid-lock` | GPID lock + QA scripts/reports | **Keep (recent wartime stream)** |
| `origin/wartime/phase4-consumer-api` | consumer API route + consumer-api service files | **Keep / high priority review** |
| `origin/wartime/sprint-review-fixes` | wartime fixups across scripts/reports | **Keep until wartime stack merged** |

### Cleanup strategy

- **Immediate delete candidates:** `codex/scrape-core`, `feat/llm-parser-poc` (after report archive), likely old `kimi/*` + `opus/*` once confirmed superseded.
- **Keep active pipeline branches:** `wartime/*`, `contracts/*`, `codex/platform-infra` until explicit PR decision.

---

## Task 3) API Route Audit (29 files)

All 29 files contain actual handlers and route registration code. Only one file has obvious partial TODO implementation (`pos-api-integration.ts`).

Legend:
- **Impl:** Full / Partial / Stub
- **Consumer needed (`glassintel.xyz/prices`):** Yes / Maybe / No

| Route file | Impl | Consumer needed? | Notes |
|---|---|---|---|
| `consumer.ts` | Full | **Yes (critical)** | Public consumer API |
| `products.ts` | Full | **Yes (critical)** | Core product catalog/matching access |
| `prices.ts` | Full | **Yes (critical)** | Core pricing endpoints; minor TODO note for geo/PostGIS |
| `operators.ts` | Full | **Yes (critical)** | Operator search/listing used by consumer flows |
| `sources.ts` | Full | **Yes (critical)** | Source metadata/provenance |
| `catalog.ts` | Full | Maybe | Service/catalog feed; possibly used by consumer backend pipelines |
| `public-report-card.ts` | Full | Maybe | Public-facing intelligence page support |
| `ccc.ts` | Full | Maybe | Public market intelligence content (not core price compare) |
| `waitlist.ts` | Full | No | Growth/onboarding infra |
| `newsletter.ts` | Full | No | Growth content feed/subscribe |
| `health-sources.ts` | Full | No | Operational/health endpoint |
| `auth.ts` | Full | No | Platform auth infra |
| `profile.ts` | Full | No | Authenticated user profile |
| `dashboard.ts` | Full | No | Operator dashboard/morning brief |
| `viz.ts` | Full | No | Advanced internal visualizations |
| `scores.ts` | Full | No | Scoring/leaderboard operator intelligence |
| `report-card.ts` | Full | No | Operator report card internals |
| `recommendations.ts` | Full | No | B2B recommendation workflows |
| `alerts.ts` | Full | No | B2B alerting workflows |
| `watchlists.ts` | Full | No | B2B watchlist workflows |
| `threats.ts` | Full | No | Threat radar (legacy/B2B) |
| `margin-rules.ts` | Full | No | Margin engine/B2B |
| `billing.ts` | Full | No | Stripe + billing |
| `ecosystem.ts` | Full | No | Event ingestion/query |
| `budtender-api.ts` | Full | No | Virtual budtender telemetry API |
| `admin-vb.ts` | Full | No | Admin virtual budtender endpoints |
| `exports.ts` | Full | No | Export jobs |
| `match-validation.ts` | Full | No | Human QA for matching |
| `pos-api-integration.ts` | **Partial** | No | Has multiple TODOs for live Dutchie/Jane/Clover calls + upsert validation |

**Conclusion:**
- No route files are empty stubs.
- `pos-api-integration.ts` is the only clearly partial implementation.
- Consumer-critical surface is concentrated in: `consumer.ts`, `products.ts`, `prices.ts`, `operators.ts`, `sources.ts`.

---

## Task 4) Migration State

### Files discovered

- `migrations/004_matching_engine.sql`
- `scripts/migrations/001-scraper-v2.sql`
- `scripts/migrations/002-price-idempotency.sql`
- `scripts/migrations/003-data-quality-infra.sql`
- `scripts/migrations/004-merge-duplicate-operators.sql`
- `scripts/migrations/005-performance-indexes.sql`
- `scripts/migrations/006-ecosystem-integration.sql`
- `scripts/migrations/007-billing.sql`
- `scripts/migrations/008-vb-tenants.sql`
- `scripts/migrations/009-demand-signals-upsert-safety.sql`
- `scripts/migrations/010-sources-url-unique.sql`
- `scripts/migrations/011-pos-connections.sql`
- `scripts/migrations/012-operator-matching.sql`
- `scripts/migrations/013-fuzzy-product-matches.sql`
- `scripts/migrations/014-wartime-quarantine.sql`
- plus helpers: `move-glass-to-public.sql`, `rehash-gpid.ts`

### Database query result

Query run (via `pg`):

```sql
SELECT * FROM glass.migration_log ORDER BY applied_at DESC LIMIT 20;
```

Result rows (latest first):

1. `012-operator-matching.sql` — applied 2026-02-13T16:51:02.171Z (`codex-scraper-phase2`)
2. `010-sources-url-unique.sql` — applied 2026-02-13T16:27:49.310Z (`fix/db-critical-phase1`)
3. `011-pos-connections.sql` — applied 2026-02-13T16:27:49.310Z (`fix/db-critical-phase1`)

### Migration-state conclusion

- **Migration log is sparse** versus migration files present in repo.
- As recorded in `glass.migration_log`, only **3 migrations** are applied.
- `013` and `014` exist in repo but are **not shown as applied** in this environment.
- There is a likely process gap between migration file creation and production application/audit logging.

---

## Deployment readiness summary

- **Deployable now (with caveats):** scrapers, gpid-verify (assuming env + context correctness).
- **Not deployable as-is:** `services/api` (TS compile blockers), `apps/web` (local dependency/build state broken), `services/scrape` (dead/non-service shape).
- **Dormant/not deployed:** `services/intelligence`.
- **Branch hygiene:** 24 unmerged branches; significant cleanup opportunity after wartime/contracts decisions.
- **DB migrations:** currently inconsistent between repo migrations and `glass.migration_log` applied state.
