# GLASS Infrastructure Audit — Part 3: API Service, Backend & Architecture

**Auditor:** Senior Backend Architect (AI)  
**Date:** 2026-02-13  
**Scope:** API service (Fastify), Intelligence service, ETL scripts, event contracts, infra, architecture alignment with Master Strategy  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [API Service Health](#2-api-service-health)
3. [Schema Mismatch Analysis](#3-schema-mismatch-analysis)
4. [Route-by-Route Audit](#4-route-by-route-audit)
5. [Dead vs Live Code Classification](#5-dead-vs-live-code-classification)
6. [Architecture Issues](#6-architecture-issues)
7. [Security Audit](#7-security-audit)
8. [Strategy Alignment & Gap Analysis](#8-strategy-alignment--gap-analysis)
9. [Deployment Audit](#9-deployment-audit)
10. [Prioritized Action List](#10-prioritized-action-list)
11. [Dead Code Cleanup List](#11-dead-code-cleanup-list)
12. [Architecture Recommendations](#12-architecture-recommendations)

---

## 1. Executive Summary

The GLASS API is a **well-structured Fastify application** with solid fundamentals: proper auth (Clerk + JWT), good route organization, pagination, rate limiting, and a comprehensive Drizzle ORM schema. However, it suffers from several **critical issues** that must be resolved before the consumer-first pivot:

**Critical Issues (3):**
- Missing `pos_connections` table in production DB (API will crash on POS routes)
- CCC routes reference tables (`ccc_weekly_sales`, `ccc_pending_applications`, `ccc_demographics`, `ccc_avg_prices`, `ccc_plant_activity`) that exist in DB but are NOT in the Drizzle schema — fragile raw SQL dependency
- `match-validation.ts` references `canonical_products` and `product_matches` tables not in Drizzle schema

**High Issues (8):**
- Intelligence service is DORMANT — requires Redis (BullMQ) not provisioned on Railway
- No test suite exists anywhere
- In-memory rate limiting resets on deploy (useless in production)
- `operators.license_number` is NOT UNIQUE in Drizzle schema but IS UNIQUE in `infra/schema.sql` — schema drift
- Several raw SQL queries reference table/column names without Drizzle type safety
- Event contracts (JSON schemas) are defined but never consumed — dead architecture
- No database connection pooling tuning for Railway's proxy
- Recommendation engine + elasticity model use observation count as "volume proxy" — misleading

**Medium Issues (12):**
- Duplicate `escapeLike` function defined in 3+ files
- `bullmq` and `ioredis` in API package.json but not used by the API service
- No OpenAPI spec auto-generation from Typebox schemas
- Report card builds use expensive multi-CTE queries without query plan optimization
- Health-sources route imports `Type` at bottom of file (works but non-standard)
- No graceful connection drain on SIGTERM
- Dockerfile COPY paths are wrong (assumes `/services/api/` not `/src/services/api/`)
- Drizzle config uses default export but file is `.ts` — may need `drizzle.config.mjs` for drizzle-kit
- `viz.ts` has 20+ endpoints — should be split into separate modules
- Auto-invite system uses raw `pg` client (`db.query`) not Drizzle ORM
- Pagination `sort_by` uses `sql.identifier()` which could allow column enumeration attacks
- No request timeout middleware

**Current State:** The API is **functional for B2B operator-facing features** but is **not ready for the consumer-first pivot**. It lacks all consumer-facing endpoints specified in the Master Strategy.

---

## 2. API Service Health

### 2.1 Boot Analysis

**Severity: Critical**  
**Description:** The server imports `@clerk/fastify` and `bullmq`/`ioredis` at startup. If Clerk keys are missing in dev, it warns but continues. However, the `clerkPlugin` registration will likely throw if `secretKey` is undefined.

**Impact:** In dev without Clerk keys, the server may crash on boot. The code attempts to handle this with `if (!CLERK_SECRET_KEY)` checks but still passes `undefined` to `clerkPlugin`.

**Fix:** Wrap clerkPlugin registration in a conditional:
```typescript
if (CLERK_SECRET_KEY && CLERK_PUBLISHABLE_KEY) {
  await fastify.register(clerkPlugin, { ... });
}
```
**Effort:** 0.5 hours

### 2.2 Duplicate Route Risk

**Severity: Medium**  
**Description:** No duplicate routes detected. The codebase is carefully organized — static routes like `/recommendations/generate` and `/margin-rules/violations` are registered before parametric `/:id` routes with explicit comments noting this requirement.

**Impact:** None currently. Well handled.

### 2.3 Health Check

**Severity: Low**  
**Description:** Health check at `/health` is well-implemented — returns basic `ok` for public, detailed status (DB check, uptime) for admin key holders. Prometheus-style `/metrics` endpoint exists but is basic (no histogram, no per-route metrics).

**Fix:** Add response time histograms and per-route request counts for production observability.
**Effort:** 4 hours

### 2.4 Error Handling

**Severity: Low**  
**Description:** Global error handler properly redacts error messages in production, handles validation errors with field-level details. Good.

**Fix:** Add structured error codes for all error responses (some routes return `{ error: 'string' }` instead of `{ error: { code, message } }`).
**Effort:** 2 hours

---

## 3. Schema Mismatch Analysis

### 3.1 Tables in DB but NOT in Drizzle Schema

**Severity: Critical**  
**Description:** The following tables exist in the production database but have NO Drizzle ORM definition in `schema.ts`:

| Table | Used in Routes? | Risk |
|-------|----------------|------|
| `auto_invite_log` | No (script-only) | Low |
| `brand_dictionary` | No | Low |
| `canonical_products` | Yes (`match-validation.ts`) | **Critical** |
| `ccc_avg_prices` | Yes (`ccc.ts`) | **Critical** |
| `ccc_demographics` | Yes (`ccc.ts`) | **Critical** |
| `ccc_ingest_runs` | No (intelligence service) | Low |
| `ccc_pending_applications` | Yes (`ccc.ts`, `report-card.ts`) | **Critical** |
| `ccc_plant_activity` | Yes (`ccc.ts`) | **Critical** |
| `ccc_weekly_sales` | Yes (`ccc.ts`) | **Critical** |
| `match_validation_samples` | Yes (`match-validation.ts`) | **Critical** |
| `price_changes` | No | Low |
| `product_matches` | Yes (`match-validation.ts`) | **Critical** |

**Impact:** All routes using these tables rely on **raw SQL strings** (`db.execute(sql\`...\`)`) instead of type-safe Drizzle queries. Schema changes in DB won't be caught at compile time. Column renames silently break production.

**Fix:** Add Drizzle schema definitions for all 12 tables. Priority: `canonical_products`, `product_matches`, `match_validation_samples`, `ccc_pending_applications`, `ccc_weekly_sales`.  
**Effort:** 6 hours

### 3.2 Tables in Drizzle Schema but NOT in DB

**Severity: Critical**  
**Description:** The `pos_connections` table is defined in `schema.ts` but does **not exist** in the production database.

**Impact:** Any request to `/api/v1/pos/connections`, `/api/v1/health/sources` (POS section), or any call to `source-priority.ts` that queries `posConnections` will throw a runtime error. The POS API Integration feature is completely broken.

**Fix:** Run migration to create the `pos_connections` table:
```sql
CREATE TABLE pos_connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  provider VARCHAR(50) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  store_id VARCHAR(255),
  scopes JSONB DEFAULT '[]',
  last_sync_at TIMESTAMP WITH TIME ZONE,
  last_error TEXT,
  error_count INTEGER NOT NULL DEFAULT 0,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```
**Effort:** 0.5 hours

### 3.3 Column Mismatches

**Severity: High**  
**Description:** 
- `operators.license_number` is `NOT NULL UNIQUE` in `infra/schema.sql` but is nullable and non-unique in Drizzle schema. The auto-provisioning in `auth.ts` inserts `PENDING-${userId}` as license_number, which would violate the `UNIQUE` constraint if it exists in DB.
- `products.weight_grams` and `products.strain_type` exist in Drizzle schema but not in `infra/schema.sql`
- `products.subcategory` exists in Drizzle but not in `infra/schema.sql`

**Impact:** Auto-provisioned users could fail to create if DB has UNIQUE constraint on license_number. Schema drift makes `infra/schema.sql` unreliable as reference.

**Fix:** 
1. Verify actual DB constraints with `\d operators`
2. Update `infra/schema.sql` to match actual DB state
3. Make Drizzle schema the single source of truth
**Effort:** 3 hours

### 3.4 Materialized Views

**Severity: Medium**  
**Description:** Two materialized views exist (`mv_operator_health`, `mv_thc_integrity`) and are correctly referenced in `scores.ts` with fallback logic. The `refresh_health_scores()` function exists. This is well-implemented.

**Fix:** Document the refresh schedule. Currently no cron job refreshes these views automatically.
**Effort:** 1 hour

---

## 4. Route-by-Route Audit

### 4.1 Authentication Routes (`auth.ts`) — LIVE

**Severity: Medium**  
**Description:** Dual auth system: legacy email/password (bcrypt) + Clerk JWT. The legacy auth creates a parallel authentication path that should be deprecated for Clerk-only.

**Issues:**
- Password minimum length is 12 characters (good)
- Refresh token rotation implemented correctly (good)
- No brute-force protection on `/auth/login` — no rate limiting
- `password_hash` field set to `'clerk-managed'` for Clerk users — if legacy login is attempted with this value, bcrypt.compare would succeed for any input that bcrypt hashes to `'clerk-managed'` (extremely unlikely but technically impure)

**Fix:** Add rate limiting to `/auth/login`. Set `password_hash` to a random non-bcrypt string for Clerk-managed users.
**Effort:** 2 hours

### 4.2 Operators Routes (`operators.ts`) — LIVE

**Severity: Low**  
**Description:** Well-implemented CRUD with proper auth, role checks, and pagination. Search endpoint is public and rate-limited (good for onboarding). LIKE injection properly escaped.

**Issue:** `sql.identifier()` usage in ORDER BY clause is safe against injection but could expose column names in error messages.

### 4.3 Prices Routes (`prices.ts`) — LIVE

**Severity: Low**  
**Description:** Good join-based queries with proper sort field whitelisting. Movers endpoint uses raw SQL CTEs — correct but not type-safe.

### 4.4 Dashboard Routes (`dashboard.ts`) — LIVE

**Severity: Low**  
**Description:** Excellent use of `Promise.all()` for parallel data fetching. Morning brief aggregates 4 independent data sources concurrently. Well-architected.

### 4.5 Report Card Routes (`report-card.ts`) — LIVE

**Severity: Medium**  
**Description:** Most complex file (500+ lines). Implements multi-CTE queries for pricing, competition, assortment, and market position analysis. Has in-memory cache with TTL and size limits.

**Issues:**
- `ccc_pending_applications` table referenced via raw SQL (not in Drizzle schema)
- Expensive queries with no query plan optimization
- Cache is in-memory (lost on deploy)
- `buildReportCard()` function is 300+ lines — should be decomposed

**Fix:** Add Redis cache, add Drizzle definitions for CCC tables, refactor into smaller functions.
**Effort:** 8 hours

### 4.6 Public Report Card (`public-report-card.ts`) — LIVE

**Severity: Medium**  
**Description:** Duplicates its own rate limiter instead of using `utils/rate-limit.ts`. Slug-based operator lookup uses fragile string manipulation.

**Fix:** Use shared rate limiter. Add a `slug` column to operators table for reliable lookups.
**Effort:** 3 hours

### 4.7 Scores Routes (`scores.ts`) — LIVE

**Severity: Low**  
**Description:** Well-structured with proper fallback chain: `operator_scores` table → `mv_operator_health` view → on-the-fly computation. THC integrity endpoint correctly cross-references lab tests with menu prices.

### 4.8 CCC Routes (`ccc.ts`) — LIVE

**Severity: High**  
**Description:** References 6 tables not in Drizzle schema: `ccc_weekly_sales`, `ccc_avg_prices`, `ccc_pending_applications`, `ccc_demographics`, `ccc_plant_activity`, `ccc_monthly_prices` (this last one IS in schema). All queries use raw SQL.

**Issues:**
- `/admin/data-quality` and `/admin/duplicate-products` are registered at non-standard paths (under `/api/v1/` prefix but semantically admin endpoints)
- The `ccc/cross-reference` query hardcodes flower per-gram conversion at 3.5g — should be configurable
- No pagination on CCC endpoints — `LIMIT 1000` could be insufficient or excessive

**Fix:** Add Drizzle schema for CCC tables. Add pagination. Move admin endpoints to consistent `/admin/` prefix.
**Effort:** 6 hours

### 4.9 Billing Routes (`billing.ts`) — LIVE

**Severity: Low**  
**Description:** Solid Stripe integration with lazy-loading, proper webhook signature verification, and subscription lifecycle management. The webhook correctly handles `checkout.session.completed`, subscription updates/deletions, and invoice events.

**Issue:** The raw body parser for webhooks is correctly implemented with `parseAs: 'buffer'`.

### 4.10 Catalog Routes (`catalog.ts`) — LIVE (Service-to-Service)

**Severity: Low**  
**Description:** Service-to-service endpoint gated by `ROVIQ_SERVICE_API_KEYS`. Uses `LATERAL JOIN` for efficient latest-price queries. Well-implemented.

### 4.11 Budtender API Routes (`budtender-api.ts`) — LIVE (Service-to-Service)

**Severity: Low**  
**Description:** Telemetry ingestion for Virtual Budtender. Properly gated by service API key. Upsert logic for sessions is correct.

### 4.12 Match Validation Routes (`match-validation.ts`) — DORMANT

**Severity: High**  
**Description:** References `canonical_products`, `product_matches`, and `match_validation_samples` tables — all exist in DB but not in Drizzle schema. Uses `sql<Type>` generic syntax that doesn't actually enforce types at runtime.

**Impact:** Route will work as long as DB schema matches, but any column rename breaks silently.

**Fix:** Add Drizzle definitions for GPID-related tables.
**Effort:** 3 hours

### 4.13 POS API Integration (`pos-api-integration.ts`) — DORMANT

**Severity: Critical**  
**Description:** `pos_connections` table does not exist in production DB. All 4 POS connector classes (Dutchie, Jane, Clover, Blaze) are skeleton implementations with `TODO` comments — `fetchProducts()` returns empty arrays.

**Impact:** Creating a POS connection will crash. Triggering sync returns empty results. The "Trojan Horse" strategy described in the code is entirely aspirational.

**Fix:** Create `pos_connections` table. Implement at least the Dutchie connector (highest priority per strategy doc).
**Effort:** 40+ hours (full feature)

### 4.14 Ecosystem Routes (`ecosystem.ts`) — LIVE

**Severity: Low**  
**Description:** Clean event ingestion and query API. Properly gated.

### 4.15 Viz Routes (`viz.ts`) — LIVE

**Severity: Medium**  
**Description:** **20+ visualization endpoints** in a single 700+ line file. All use raw SQL. Many are expensive (haversine calculations, window functions, multiple CTEs).

**Issues:**
- No auth on most endpoints (price-matrix, volatility, cascade, ticker, operators-geo, etc.) — these expose competitive intelligence data publicly
- `operators-geo` joins threats with haversine in a cross-join pattern — O(n²) performance
- `viz/proximity` requires operator_id but no ownership check
- No caching on expensive queries

**Fix:** 
1. Split into `viz-geo.ts`, `viz-prices.ts`, `viz-market.ts`
2. Add auth or at least rate limiting to sensitive endpoints
3. Add query result caching
**Effort:** 12 hours

### 4.16 Other Routes

| Route | Status | Notes |
|-------|--------|-------|
| `waitlist.ts` | LIVE | Well-implemented with custom rate limiter, input validation, UTM tracking |
| `newsletter.ts` | LIVE | Beehiiv proxy with fallback for missing API keys |
| `profile.ts` | LIVE | Simple, correct |
| `exports.ts` | LIVE (partial) | CSV export works, PDF returns 501 Not Implemented |
| `sources.ts` | LIVE | Standard CRUD, well-implemented |
| `margin-rules.ts` | LIVE | Proper validation, unique constraint handling |
| `admin-vb.ts` | LIVE | VB tenant management, API key redaction (good security) |
| `health-sources.ts` | LIVE (buggy) | `Type` import at bottom of file; `productCount` incorrectly uses `failure_count` as proxy |

---

## 5. Dead vs Live Code Classification

### Services

| Component | Status | Justification |
|-----------|--------|---------------|
| `services/api/` | **LIVE** | Main API server, actively deployed |
| `services/intelligence/` | **DORMANT** | Requires Redis (BullMQ) — not provisioned. Well-designed but never started in production. |

### API Engine

| Component | Status | Justification |
|-----------|--------|---------------|
| `engine/generator.ts` | **LIVE** | Recommendation generation, called from `/recommendations/generate` |
| `engine/rules.ts` | **LIVE** | Margin rule evaluation, called from `/margin-rules/violations` |
| `engine/elasticity.ts` | **LIVE** | Price elasticity estimation, called from generator |

### Scripts

| Component | Status | Justification |
|-----------|--------|---------------|
| `scripts/daily-scrape.ts` | **LIVE** | Daily scraping orchestrator |
| `scripts/scrape-leafly.ts` | **LIVE** | Leafly scraper |
| `scripts/import-ccc-data.ts` | **DORMANT** | CCC data importer (may have been replaced by `import/` scripts) |
| `scripts/geocode-operators.ts` | **DORMANT** | One-time geocoding script |
| `scripts/import/*.ts` | **LIVE** | Active ETL importers for CCC data (lab tests, licenses, facility sales, monthly prices) |
| `scripts/auto-invite/` | **DORMANT** | Built but likely not running in production (uses Resend for email) |
| `scripts/etl/` | **DORMANT** | Demand signal aggregation and operator matching |
| `scripts/migrations/*.sql` | **LIVE** | Applied migration files |

### Infrastructure

| Component | Status | Justification |
|-----------|--------|---------------|
| `infra/schema.sql` | **DEAD** | Out of sync with actual DB schema — should not be used as reference |
| `infra/docker-compose.yml` | **DORMANT** | Local dev setup, not used in Railway deployment |
| `infra/docker-compose.test.yml` | **DEAD** | Test infrastructure never implemented |
| `infra/observability/` | **DEAD** | Prometheus/alert configs exist but no Prometheus is deployed |
| `infra/ci/github-actions.yml` | **DEAD** | CI pipeline exists but unclear if active |
| `infra/Dockerfile` | **DORMANT** | Alternative Dockerfile, likely not the one Railway uses |
| `infra/scripts/init-clickhouse.sh` | **DEAD** | ClickHouse was never deployed |

### Event Contracts

| Component | Status | Justification |
|-----------|--------|---------------|
| `contracts/events/scrape-events.json` | **DEAD** | Well-defined JSON schemas but NO code anywhere emits or consumes these events |
| `contracts/events/alert-events.json` | **DEAD** | Same — aspirational but unused |
| `contracts/events/ccc-events.json` | **DEAD** | Same |
| `contracts/openapi/glass-api.yaml` | **UNKNOWN** | Need to verify if it matches actual routes |
| `contracts/data-model.md` | **DORMANT** | Reference doc, may be outdated |

### API Utility Files

| Component | Status | Justification |
|-----------|--------|---------------|
| `services/api/seed-dispensaries.mjs` | **DORMANT** | One-time seeding script |
| `services/api/clean-db.mjs` | **DORMANT** | Database cleanup utility |
| `services/api/check-data.mjs` | **DORMANT** | Data verification utility |
| `services/api/list-tables.mjs` | **DORMANT** | Diagnostic utility |
| `services/api/create-schema.mjs` | **DORMANT** | Schema creation utility |
| `services/api/test-db-connection.mjs` | **DORMANT** | Connection test utility |
| `services/api/test-pg-connection.mjs` | **DORMANT** | Connection test utility |
| `services/api/run-migration.mjs` | **DORMANT** | Migration runner |
| `services/api/create-schema.sql` | **DEAD** | Superseded by Drizzle |
| `services/api/DB-MIGRATION-COMPLETE.md` | **DEAD** | Historical record |

---

## 6. Architecture Issues

### 6.1 Monorepo Structure

**Severity: Medium**  
**Description:** The project lives at `src/services/api/`, `src/services/intelligence/`, `src/scripts/`, etc. But there's no root `package.json` (confirmed: file not found). Each service has its own `package.json`. This is a pseudo-monorepo without workspace tooling.

**Issues:**
- No shared code between services (intelligence service duplicates the `threats` table schema)
- Drizzle ORM version mismatch: API uses `drizzle-orm@0.39.3`, intelligence uses `drizzle-orm@0.34.0`
- No shared types package — `types/index.ts` is API-specific
- Auto-invite scripts use raw `pg` client instead of Drizzle

**Fix:** Add root `package.json` with npm workspaces. Create `packages/db/` shared package for schema. Standardize ORM usage.
**Effort:** 8 hours

### 6.2 Event-Driven Architecture — Aspirational Only

**Severity: Medium**  
**Description:** The `contracts/events/` directory contains sophisticated JSON Schema definitions for scrape events, alert events, and CCC events. These are well-designed but **no code anywhere emits or consumes these events**. There is no event bus, no pub/sub, no message broker. The intelligence service uses BullMQ (Redis) for job scheduling, but this is task-based, not event-driven.

**Impact:** The scraper pipeline and intelligence service are completely disconnected from the API. There's no real-time notification when prices change or threats are detected.

**Fix:** For the consumer-first pivot, event-driven architecture is not needed yet. Focus on direct DB-driven data flow. Revisit when real-time features are required.
**Effort:** 0 hours (defer)

### 6.3 API ↔ Scraper Communication

**Severity: High**  
**Description:** The scraper scripts (`scripts/daily-scrape.ts`, etc.) write directly to the same Postgres database that the API reads from. There is no queuing, no notification, no coordination. The API has no way to know when new scrape data is available.

**Impact:** The "Verified X hours ago" freshness indicator required by the Master Strategy has no reliable data source. The `sources.last_scraped_at` field is updated by scrapers, but the API just reads whatever is there.

**Fix:** Scraper should update a `last_scraped_at` reliably. Add a `data_freshness` endpoint that reports actual freshness per operator.
**Effort:** 4 hours

### 6.4 Unused Dependencies

**Severity: Low**  
**Description:** The API `package.json` includes `bullmq` and `ioredis` but these are only used by the intelligence service. They are dead weight in the API deployment.

**Fix:** Remove `bullmq` and `ioredis` from API `package.json`.
**Effort:** 0.5 hours

### 6.5 Database Connection Configuration

**Severity: Medium**  
**Description:** `db/index.ts` creates a `postgres` connection with `{ max: 20 }`. Railway's proxy uses connection pooling. Having 20 connections from the app to Railway's proxy may be excessive and waste connection slots.

**Fix:** Reduce to `{ max: 5 }` for Railway. Add connection timeout and idle timeout settings.
**Effort:** 0.5 hours

---

## 7. Security Audit

### 7.1 API Key Management

**Severity: Medium**  
**Description:** Three key systems are in use:
1. **Clerk JWT** — well-implemented, JWKS verification with caching
2. **ADMIN_API_KEY** — passed via header `x-admin-key` or query param `?key=` — query param exposure in logs/URLs is a risk
3. **ROVIQ_SERVICE_API_KEYS** — comma-separated env var for service-to-service auth

**Issue:** Admin key passed as query parameter is logged in access logs and browser history.

**Fix:** Remove query parameter support for admin key. Require header-only.
**Effort:** 1 hour

### 7.2 SQL Injection

**Severity: Low**  
**Description:** All user inputs are properly parameterized through Drizzle ORM or template literal SQL parameters (`${value}`). The `escapeLike()` function properly escapes LIKE wildcards. No raw string concatenation detected in SQL queries.

**One concern:** `sql.identifier()` in `operators.ts` for dynamic ORDER BY. This is safe for SQL injection but could expose column names in error messages.

### 7.3 Rate Limiting

**Severity: High**  
**Description:** Rate limiting uses an in-memory `Map` that resets on every deploy/restart. On Railway with auto-scaling or restarts, this provides **zero protection**.

**Impact:** No effective rate limiting in production. An attacker can scrape all data or brute-force auth.

**Fix:** Replace with Redis-backed rate limiting or use Railway's built-in rate limiting if available. At minimum, use `@fastify/rate-limit` plugin.
**Effort:** 4 hours

### 7.4 Auth Bypass Possibilities

**Severity: Medium**  
**Description:** The `onRequest` hook strips `Authorization` headers for public routes (`/operators/search`, `/waitlist`, `/newsletter/subscribe`, `/public/`). This is a correct pattern to prevent stale tokens from blocking public endpoints.

**Issue:** The public route check uses `request.url.startsWith()` which could be bypassed with URL encoding or path traversal in edge cases. Use Fastify's routing context instead.

**Fix:** Use Fastify's route metadata/tags to mark public routes instead of URL prefix matching.
**Effort:** 3 hours

### 7.5 Exposed Endpoints

**Severity: High**  
**Description:** The following endpoints expose sensitive competitive intelligence data **without any authentication**:

- `GET /api/v1/viz/price-matrix` — Average prices per operator per category
- `GET /api/v1/viz/price-volatility` — Market-wide price distribution
- `GET /api/v1/viz/price-cascade` — Recent price changes across all operators
- `GET /api/v1/viz/price-ticker` — Real-time price change feed with operator names
- `GET /api/v1/viz/operators-geo` — All operator locations with product counts
- `GET /api/v1/viz/delivery-zones` — Operator delivery coverage
- `GET /api/v1/viz/brand-share` — Brand market share
- `GET /api/v1/viz/category-mix` — Product category distribution
- `GET /api/v1/viz/strain-trends` — Strain popularity trends
- `GET /api/v1/viz/operator-compare` — Head-to-head operator comparison
- `GET /api/v1/viz/price-wars` — Price war intensity metrics
- `GET /api/v1/viz/threats-network` — Threat network with operator names
- `GET /api/v1/viz/market-share-flow` — Market share flow
- `GET /api/v1/viz/economic-indicators` — Market economic indicators
- `GET /api/v1/viz/ccc-timeline` — CCC regulatory timeline
- `GET /api/v1/viz/license-pipeline` — License application pipeline
- `GET /api/v1/viz/market-size` — Market size trends
- `GET /api/v1/viz/category-growth` — Category growth over time
- `GET /api/v1/viz/price-distribution` — Price distribution by category
- `GET /api/v1/viz/geography` — Operator geography
- `GET /api/v1/viz/brand-landscape` — Brand landscape
- `GET /api/v1/health/sources` — Source health with operator details
- `GET /api/v1/report-card/:operator_id` — Full report card (though in protected section, registered under protectedRoutes)
- `GET /api/v1/market/health-leaders` — Public leaderboard (intentionally public)

**Impact:** A competitor (Hoodie Analytics) could scrape all competitive intelligence for free.

**Fix:** Move viz endpoints behind auth or at minimum behind rate-limited API key.
**Effort:** 4 hours

### 7.6 Hardcoded Admin Emails

**Severity: Medium**  
**Description:** `auth.ts` hardcodes `['torresr14@gmail.com', 'randy@roviq.ai']` as admin emails in two places. This is a security/maintenance risk.

**Fix:** Move to environment variable `ADMIN_EMAILS=email1,email2`.
**Effort:** 0.5 hours

---

## 8. Strategy Alignment & Gap Analysis

### Master Strategy Requirements vs Current State

| Requirement | Status | Gap |
|-------------|--------|-----|
| **Consumer-facing price comparison** | ❌ NOT BUILT | No public product search, no price comparison by location, no consumer-facing API |
| **Top 500 verified products (GPID)** | 🟡 PARTIAL | `canonical_products` table exists (DB), `product_matches` table exists, but no verified GPID endpoint, no consumer-facing product pages |
| **THC Accuracy Score** | 🟡 PARTIAL | `/operators/:id/thc-integrity` endpoint exists but is behind auth — not public |
| **"Verified X hours ago" freshness** | ❌ NOT BUILT | `sources.last_scraped_at` tracks freshness but no consumer-facing freshness indicator |
| **Public report card / store pages** | 🟡 PARTIAL | `/public/report-card/:slug` exists — good start, but limited data compared to full report card |
| **GPID cross-platform matching API** | ❌ NOT BUILT | `product_matches` table exists but no API endpoint exposes cross-platform price comparisons |
| **"Wrong price?" feedback endpoint** | ❌ NOT BUILT | No user feedback mechanism for price accuracy |
| **Post-tax out-the-door pricing** | ❌ NOT BUILT | Prices are pre-tax only. No tax calculation infrastructure |
| **Distance-based search** | ❌ NOT BUILT | Haversine distance exists in threat/viz queries but no consumer search-by-location |
| **SEO pages (385+ dispensary, 500+ product)** | ❌ NOT BUILT | This is a frontend concern but API doesn't provide the data endpoints for it |
| **Social content auto-generation** | ❌ NOT BUILT | No API for generating price comparison cards |
| **Report Out of Stock button** | ❌ NOT BUILT | No user feedback endpoint |
| **Auto-invite system** | 🟡 BUILT, DORMANT | `scripts/auto-invite/` exists, complete with email generation and Resend integration. Not running. |
| **Stripe billing** | ✅ BUILT | Full checkout, subscription, portal, webhook handling |
| **Virtual Budtender telemetry** | ✅ BUILT | Session and query tracking via service API |
| **Ecosystem events** | ✅ BUILT | Cross-product event ingestion |
| **Operator health scores** | ✅ BUILT | 5-component scoring with materialized views |
| **Margin rule engine** | ✅ BUILT | Rules, violations, recommendations with elasticity estimation |

### Critical Gaps for Consumer-First Pivot

1. **Consumer Product Search API** — Needs: `GET /api/v1/consumer/search?q=blue+dream&lat=42.36&lon=-71.06&radius=10`
2. **GPID Price Comparison API** — Needs: `GET /api/v1/consumer/products/:gpid/prices?lat=42.36&lon=-71.06`
3. **Store Page API** — Needs: `GET /api/v1/consumer/stores/:slug` (menu, prices, freshness)
4. **Price Feedback API** — Needs: `POST /api/v1/consumer/prices/:id/report` (wrong price, out of stock)
5. **Freshness Indicator** — Every price response needs `verified_at` and `freshness_status`
6. **Tax Calculation** — MA excise tax (10.75%) + sales tax (6.25%) + local tax (up to 3%)

---

## 9. Deployment Audit

### 9.1 Dockerfile Issues

**Severity: Medium**  
**Description:** The Dockerfile at `services/api/Dockerfile` has incorrect COPY paths:
```dockerfile
COPY services/api/package.json services/api/
COPY contracts/ contracts/
COPY services/api/ services/api/
```
These assume a build context of the `src/` directory, but the actual path is `src/services/api/`. This Dockerfile would fail unless the Docker build context is set to `src/`.

The `infra/Dockerfile` is a separate Docker config and is likely not the one Railway uses.

**Fix:** Verify Railway's Docker build configuration. Update Dockerfile paths to match actual directory structure.
**Effort:** 1 hour

### 9.2 Environment Variables Required

| Variable | Required | Status |
|----------|----------|--------|
| `DATABASE_URL` | Yes (production) | Must be set |
| `JWT_SECRET` | Yes (production) | Must be set |
| `CLERK_SECRET_KEY` | Yes (production) | Must be set |
| `CLERK_PUBLISHABLE_KEY` | Yes (production) | Must be set |
| `CORS_ORIGIN` | Yes (production) | Must be set |
| `ADMIN_API_KEY` | Recommended | For admin endpoints |
| `STRIPE_SECRET_KEY` | For billing | Optional |
| `STRIPE_PRICE_ID` | For billing | Optional |
| `STRIPE_WEBHOOK_SECRET` | For billing | Optional |
| `ROVIQ_SERVICE_API_KEYS` | For S2S | Optional |
| `BEEHIIV_API_KEY` | For newsletter | Optional |
| `BEEHIIV_PUBLICATION_ID` | For newsletter | Optional |
| `REDIS_URL` | Intelligence only | Not needed for API |
| `NODE_ENV` | Recommended | Defaults to dev mode |
| `PORT` | Optional | Defaults to 3000 |
| `LOG_LEVEL` | Optional | Defaults to info |

### 9.3 Health Check Configuration

**Severity: Low**  
**Description:** `/health` endpoint exists and returns appropriate status codes. Railway should be configured to use `GET /health` with a 200 expected response.

### 9.4 No CI/CD Pipeline

**Severity: Medium**  
**Description:** `infra/ci/github-actions.yml` exists but it's unclear if it's active. No test suite exists (`"test": "echo \"No tests configured yet\" && exit 0"`).

**Fix:** Implement at minimum: type checking, route registration test (boots without crash), and one integration test per major route group.
**Effort:** 16 hours

---

## 10. Prioritized Action List

### P0 — Critical (Fix This Week)

| # | Finding | Effort | Impact |
|---|---------|--------|--------|
| 1 | Create `pos_connections` table in production DB | 0.5h | Prevents crashes on POS/health-sources routes |
| 2 | Add Drizzle schema definitions for `canonical_products`, `product_matches`, `match_validation_samples` | 3h | Type safety for GPID matching system |
| 3 | Add Drizzle schema definitions for `ccc_weekly_sales`, `ccc_pending_applications`, `ccc_demographics`, `ccc_plant_activity`, `ccc_avg_prices` | 3h | Type safety for CCC routes |
| 4 | Add rate limiting to `/auth/login` | 1h | Prevents brute-force attacks |
| 5 | Move viz endpoints behind auth or API key | 4h | Prevents competitor data scraping |

### P1 — High (Fix This Sprint)

| # | Finding | Effort | Impact |
|---|---------|--------|--------|
| 6 | Replace in-memory rate limiting with persistent solution | 4h | Actual rate limiting in production |
| 7 | Fix health-sources `productCount` using `failure_count` | 0.5h | Correct health reporting |
| 8 | Remove `bullmq`/`ioredis` from API package.json | 0.5h | Smaller deployment, fewer dependencies |
| 9 | Remove admin key query parameter support | 1h | Security: no key in URLs/logs |
| 10 | Move hardcoded admin emails to env variable | 0.5h | Maintainability |
| 11 | Reduce DB connection pool to 5 for Railway | 0.5h | Resource efficiency |
| 12 | Build consumer price search API | 16h | **Master Strategy: critical path** |
| 13 | Build GPID price comparison endpoint | 12h | **Master Strategy: critical path** |

### P2 — Medium (Fix This Month)

| # | Finding | Effort | Impact |
|---|---------|--------|--------|
| 14 | Split `viz.ts` into multiple files | 4h | Maintainability |
| 15 | Add Redis cache for report cards | 4h | Performance |
| 16 | Fix Dockerfile COPY paths | 1h | Deployment reliability |
| 17 | Implement basic test suite | 16h | Quality assurance |
| 18 | Add `slug` column to operators table | 2h | Reliable public URL lookups |
| 19 | Wrap clerkPlugin in conditional registration | 0.5h | Dev environment stability |
| 20 | Create shared DB package (monorepo workspace) | 8h | Code reuse, schema consistency |
| 21 | Build price feedback endpoint | 4h | Consumer engagement |
| 22 | Add tax calculation infrastructure | 8h | Post-tax pricing |
| 23 | Document materialized view refresh schedule | 1h | Operations |

### P3 — Low (Backlog)

| # | Finding | Effort | Impact |
|---|---------|--------|--------|
| 24 | Deduplicate `escapeLike` function | 1h | Code cleanliness |
| 25 | Add Prometheus metrics | 4h | Observability |
| 26 | Add request timeout middleware | 2h | Reliability |
| 27 | Standardize error response format | 2h | API consistency |
| 28 | Update `infra/schema.sql` or delete it | 2h | Documentation accuracy |
| 29 | Implement PDF export | 8h | Feature completeness |
| 30 | Clean up dormant .mjs utility scripts | 1h | Repo cleanliness |

---

## 11. Dead Code Cleanup List

### Safe to Delete

| Path | Reason |
|------|--------|
| `src/infra/schema.sql` | Out of sync, Drizzle is source of truth |
| `src/infra/scripts/init-clickhouse.sh` | ClickHouse never deployed |
| `src/infra/docker-compose.test.yml` | Test infra never implemented |
| `src/infra/observability/prometheus.yml` | No Prometheus deployed |
| `src/infra/observability/alerts.yml` | No alerting system deployed |
| `src/services/api/create-schema.sql` | Superseded by Drizzle |
| `src/services/api/DB-MIGRATION-COMPLETE.md` | Historical, no value |
| `src/services/api/dist/` | Build artifacts — should be gitignored |
| `src/scripts/weedmaps-failed-slugs-*.json` | Transient scrape data |
| `src/scripts/*-scrape-summary-*.json` | Transient scrape data (7 files) |

### Consider Archiving (move to `archive/` branch)

| Path | Reason |
|------|--------|
| `src/contracts/events/` | Well-designed but unused — preserve for future event-driven architecture |
| `src/contracts/openapi/glass-api.yaml` | May be outdated — verify before keeping |
| `src/services/intelligence/` | Well-designed, well-typed, but requires Redis infrastructure not yet provisioned |

### Keep But Refactor

| Path | Reason |
|------|--------|
| `src/services/api/src/routes/viz.ts` | Split into 3-4 smaller files |
| `src/services/api/src/routes/ccc.ts` | Move admin endpoints to separate file |
| `src/services/api/src/routes/report-card.ts` | Extract `buildReportCard()` into service layer |
| `src/scripts/auto-invite/` | Working system, needs to be activated |

---

## 12. Architecture Recommendations for Consumer-First Pivot

### 12.1 New API Layer: Consumer Routes

Create `src/services/api/src/routes/consumer/` with these files:

```
routes/consumer/
├── search.ts         — Product search by name, category, location
├── products.ts       — GPID product pages with cross-store prices
├── stores.ts         — Store pages with menu, hours, location
├── feedback.ts       — "Wrong price?" and "Out of stock" reports
└── index.ts          — Consumer route registration
```

These should be:
- **Public** (no auth required)
- **Rate-limited** (per IP, 60 req/min)
- **Cached** (Redis, 5-min TTL)
- **Location-aware** (lat/lon parameters for distance calculations)

### 12.2 GPID Data Layer

The `canonical_products` and `product_matches` tables exist. Create a service layer:

```
services/gpid/
├── lookup.ts         — Resolve GPID → all matching products with prices
├── search.ts         — Full-text search over canonical products
├── freshness.ts      — Calculate "Verified X hours ago" for each price
└── tax.ts            — MA tax calculation (10.75% + 6.25% + local)
```

### 12.3 Caching Strategy

Current state: in-memory Maps that reset on deploy.

**Recommended:**
1. Use Railway Redis add-on
2. Cache report cards (1 hour TTL)
3. Cache consumer search results (5 min TTL)
4. Cache GPID price comparisons (5 min TTL)
5. Use Redis for rate limiting

### 12.4 API Versioning

Current: All routes under `/api/v1/`. This is correct. Consumer routes should also be under `/api/v1/consumer/` to allow future v2 changes.

### 12.5 Immediate Architecture Priority

```
Week 1: Schema fixes (P0 items 1-5)
Week 2: Consumer search + GPID comparison API (P1 items 12-13)
Week 3: Freshness indicators + tax calculation
Week 4: Public store pages + feedback endpoints
```

This gives you a consumer-facing API in 4 weeks, which can power the mobile-first site described in the Master Strategy.

---

## Appendix: Database Statistics

| Metric | Value |
|--------|-------|
| Total operators (excluding auto-provisioned) | ~1,254 |
| Total DB tables | 37 |
| Tables in Drizzle schema | 25 |
| Tables missing from Drizzle | 12 |
| Materialized views | 2 (`mv_operator_health`, `mv_thc_integrity`) |
| Stored functions | 1 (`refresh_health_scores`) |
| Tables in Drizzle but missing from DB | 1 (`pos_connections`) |

---

*End of Audit Report*
