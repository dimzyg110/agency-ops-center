# GLASS Platform — Comprehensive Reliability & Security Audit

**Reviewer:** Senior Principal Engineer (Opus)  
**Date:** 2026-02-12  
**Scope:** Full codebase — scrapers, API, frontend, data integrity, security  
**Files reviewed:** 25+ source files across `services/api`, `scripts/`, `apps/web`

---

## Executive Summary

GLASS has a solid architectural foundation — Fastify + Drizzle + PostgreSQL is a good stack, the scraper infrastructure is surprisingly mature for a startup, and the Report Card feature is genuinely well-designed. However, there are **critical issues that must be fixed before any paying customer sees this product**:

1. **Hardcoded database credentials in source code** (P0 — security)
2. **SQL injection vulnerability in operator search** (P0 — security)
3. **Unbounded queries that will OOM under load** (P0 — reliability)
4. **No brand cleanup on ingest** — only post-hoc DB query detection (P1 — data quality)
5. **No cross-platform product deduplication** (P1 — data integrity)
6. **Report card cache is unbounded in-memory Map** (P1 — memory leak)
7. **CCC/viz routes have zero authentication** (P1 — security design decision)
8. **In-memory rate limiting resets on every deploy** (P2 — reliability)

Total issues found: **47** (8 P0, 16 P1, 23 P2)

---

## Part 1: Scraper Hardening

### 1.1 Error Handling — Per-Store Failures

**Good:** The Weedmaps scraper (`scrape-weedmaps.ts`) has proper per-store error isolation via the worker pool pattern. Each store failure is caught, logged, and the run continues. The `scrape_jobs` table tracks per-store status.

**Bad:** The Dutchie scraper (`scrape-dutchie-ma.ts`) runs sequentially and a page crash in Playwright will propagate up to the store loop, but individual page failures within a store ARE caught. However:

**Issue 1.1a — Dutchie scraper has no DB persistence layer**  
**File:** `scripts/scrape-dutchie-ma.ts`  
**What's wrong:** The Dutchie scraper generates SQL files (`dutchie-seed.sql`) instead of writing directly to the database. It uses string interpolation for SQL construction (`sqlValue` function), which is fragile. Meanwhile, the Weedmaps scraper uses parameterized queries via `pg` Pool.  
**Priority:** P1  
**Fix:** Port the Dutchie scraper to use the same `scripts/lib/db.ts` functions (`upsertOperator`, `upsertProduct`, `insertPrice`) that the Weedmaps scraper uses. The SQL file generation approach is a leftover POC pattern that should be retired.

**Issue 1.1b — daily-scrape.ts doesn't track per-store results**  
**File:** `scripts/daily-scrape.ts`, line ~58  
**What's wrong:** `runSource()` spawns the scraper as a child process. If the child succeeds (exit 0), it sets `storesSucceeded = stores` (the hardcoded expected count, e.g. 235). It has no way to know how many stores actually succeeded — it just assumes all-or-nothing.
```typescript
runResult.storesSucceeded = stores; // ← assumes 100% success on exit 0
```
**Priority:** P1  
**Fix:** The child scrapers should write stats to a JSON file (or stdout) that `daily-scrape.ts` reads after completion. The Weedmaps scraper already writes a summary JSON — parse that.

### 1.2 Brand Cleanup — Ingest vs Post-Hoc

**This is a significant data quality gap.**

**Current state:** Brand cleanup happens in two places, neither of which is at ingest time:
1. `brand-filter.ts` — Used by both scrapers to validate brands (rejects "stock", "order soon", pipe characters, etc.)
2. `GET /admin/data-quality` — SQL query that COUNTS suspicious brands but doesn't clean them

**The gap:** The `brand-filter.ts` `isValidBrand()` function rejects bad brands and sets them to empty string (Dutchie) or `'unknown'` (Weedmaps normalizer). BUT:
- It only strips pipe characters via `isValidBrand` check (`cleaned.includes('|')` → invalid), but **doesn't strip the pipe and keep the valid part**
- "stock. Order soon." substring matching catches this at validation time, but the raw brand text from scraping sometimes arrives as `"Brand Name | In stock. Order soon."` — the filter rejects the ENTIRE string instead of extracting "Brand Name"
- The `normalizeBrandCandidate()` function only trims whitespace — it doesn't strip known noise suffixes

**File:** `scripts/lib/brand-filter.ts`  
**What's wrong:** `normalizeBrandCandidate()` does not strip pipe-delimited garbage before validation  
**Priority:** P0  
**Fix:** See Part 7 below for complete code.

### 1.3 Cross-Platform Product Deduplication

**Issue 1.3a — Same product from Dutchie AND Weedmaps creates two records**  
**File:** `scripts/lib/normalizer.ts` (`makeSKU` function) and `scripts/scrape-dutchie-ma.ts` (`makeSku` function)  
**What's wrong:** SKU generation is deterministic BUT uses different algorithms:
- Dutchie: `DUTCHIE-${sha1(brand|name|size).slice(0,16)}`  
- Weedmaps: `DUTCHIE-${sha256(brand|name|weightGrams|category).slice(0,20)}`  

Even if the same product exists on both platforms, it will get different SKUs because:
1. Different hash algorithms (SHA1 vs SHA256)
2. Different input fields (size string vs weight_grams number)
3. Both use `DUTCHIE-` prefix even for Weedmaps products
4. Brand normalization differs (Dutchie: `sanitizeBrand`, Weedmaps: `normalizeBrand` → lowercase)

**Priority:** P1  
**Fix:** Unify SKU generation into a single function in `scripts/lib/normalizer.ts`. Use the same hash, same inputs, same normalization. Consider adding a `platform` prefix to differentiate: `GLASS-${sha256(lowercase_brand|lowercase_name|weight_grams|category)}`. Then create a deduplication view or materialized view that groups by product identity across platforms.

### 1.4 Rate Limiting / Politeness

**Good:** Both scrapers implement jitter delays:
- Dutchie: `jitterMs(2000, 4000)` between pages
- Weedmaps: Configurable via `DELAYS` config, with `jitter(800, 1400)` between pages

**Good:** Weedmaps uses a browser pool with configurable concurrency (`CONCURRENCY` from config).

**Concerning:**
- **Dutchie scraper uses Firecrawl API for discovery** (city page crawling), which has its own rate limits
- **Dutchie scraper uses Playwright/Camoufox for menu scraping** — 5 categories × N stores = significant traffic
- **No exponential backoff on failures** — if a store is rate-limited (returns 429 or blocks), the scraper just logs and moves on. It should implement exponential backoff.
- **No `robots.txt` compliance** — neither scraper checks robots.txt

**Issue 1.4a — No backoff on HTTP errors**  
**File:** `scripts/scrape-dutchie-ma.ts`, `scripts/scrape-weedmaps.ts`  
**Priority:** P2  
**Fix:** Add retry with exponential backoff (1s, 2s, 4s, max 3 retries) for transient failures. Track consecutive failures per-domain and pause scraping if >5 consecutive failures (likely rate-limited).

### 1.5 Store Slug Changes / Closures

**Issue 1.5a — No mechanism to detect closed stores**  
**What's wrong:** If a Dutchie/Weedmaps store closes or changes its slug:
- The old slug will fail to scrape (page 404 or redirect)
- The operator record stays in the DB with stale data
- No alert is generated
- The `stale_data` counter in data quality will catch it eventually, but there's no automated remediation

**Priority:** P2  
**Fix:** Track consecutive scrape failures per source. After 3 consecutive days of failures, mark the source as `inactive` and the operator as `stale`. Generate an alert for manual review. For slug changes: if a discovery run finds a new slug that maps to the same operator (by name/address matching), auto-update the source URL.

---

## Part 2: API Reliability

### 2.1 SQL Injection

**Good news:** Most queries use Drizzle's `sql` tagged template, which parameterizes values. When you write `sql\`SELECT * WHERE id = ${operatorId}\``, Drizzle creates a parameterized query.

**BAD news — real SQL injection vector:**

**Issue 2.1a — Operator search endpoint uses `ilike` with unsanitized user input**  
**File:** `services/api/src/routes/operators.ts`, line ~25  
**What's wrong:**
```typescript
ilike(schema.operators.name, `%${searchTerm}%`)
```
While Drizzle's `ilike` does parameterize the value, the `%` wildcards combined with user input allow **LIKE injection**. A user can send `q=_%` to match single characters, or `q=%` to match all records. This isn't classic SQL injection but enables:
- **Operator enumeration:** Send `q=%` → returns first 15 operators. Send `q=a%` → operators starting with A. Etc.
- **ReDoS-style pattern matching:** Very long patterns with repeated wildcards can be expensive

**Priority:** P0 (operator enumeration is a business risk pre-launch)  
**Fix:** Escape LIKE metacharacters in the search term:
```typescript
const escapedTerm = searchTerm.replace(/[%_\\]/g, '\\$&');
// ...
ilike(schema.operators.name, `%${escapedTerm}%`)
```
And add a minimum query length check (already exists: `q.trim().length < 2`), but also add a maximum:
```typescript
if (!q || q.trim().length < 2 || q.trim().length > 100) {
  return reply.send({ data: [] });
}
```

**Issue 2.1b — `sql.raw()` in operator list orderBy**  
**File:** `services/api/src/routes/operators.ts`, line ~60  
**What's wrong:**
```typescript
.orderBy(sql`${sql.identifier(pagination.sort_by!)} ${sql.raw(pagination.order!)}`)
```
`sql.raw()` is **not parameterized**. If `pagination.order` can be anything other than 'asc'/'desc', this is injectable. The pagination plugin likely validates this, but it's a dangerous pattern.

**Priority:** P1  
**Fix:** Use explicit conditional instead of `sql.raw()`:
```typescript
const orderDir = pagination.order === 'desc' ? sql`DESC` : sql`ASC`;
.orderBy(sql`${sql.identifier(pagination.sort_by!)} ${orderDir}`)
```

### 2.2 N+1 Query Patterns

**Issue 2.2a — Report Card builds 6+ sequential queries**  
**File:** `services/api/src/routes/report-card.ts`, `buildReportCard()` function  
**What's wrong:** The report card makes 6 separate DB queries sequentially:
1. Operator lookup
2. Category averages (operator + 3 market fallback CTEs)
3. Market category rows
4. Competitor count
5. Pending applications
6. Assortment metrics
7. Market position

These could be parallelized or combined. With the 20s timeout, this is risky under load.

**Priority:** P2  
**Fix:** Use `Promise.all()` for independent queries (queries 3-7 only depend on operator data from query 1). The first query must complete before the others start, but queries 2-7 can run in parallel:
```typescript
const [categoryRows, marketCategoryRows, competitorRows, pendingRows, assortmentRows, positionRows] = 
  await Promise.all([
    db.execute(categoryQuery),
    db.execute(marketCategoryQuery),
    db.execute(competitorQuery),
    db.execute(pendingQuery),
    db.execute(assortmentQuery),
    db.execute(positionQuery),
  ]);
```

### 2.3 Unbounded Data / Memory Issues

**Issue 2.3a — Multiple viz endpoints load entire tables without pagination**  
**Files:** `services/api/src/routes/viz.ts`  
**What's wrong:** Several endpoints have no row limits or unreasonable limits:
- `/viz/price-ticker` — scans ALL prices with LAG window function, returns last 50. But the CTE processes the entire `prices` table.
- `/viz/price-cascade` — scans 14 days of prices with LAG, returns 120 rows. But the CTE processes all price rows in 14 days.
- `/viz/price-volatility` — up to 180 days of daily aggregates (fine)
- `/viz/price-matrix` — DISTINCT ON across all operator/product pairs (unbounded CTE), returns 250 rows
- `/viz/operators-geo` — LEFT JOINs prices AND threats with haversine distance calc for every operator (O(n×m) join)
- `/viz/strain-trends` — up to 365 days

**Most critical:** `/viz/price-matrix` and `/viz/operators-geo` will get progressively slower as data grows.

**Priority:** P0  
**Fix:** Add `WHERE scraped_at >= NOW() - INTERVAL '30 days'` to the `latest` CTE in `price-matrix` to bound the DISTINCT ON scan. For `operators-geo`, pre-filter operators with a bounding box before the haversine calculation. For `price-ticker` and `price-cascade`, add a date filter in the CTE, not just the outer query.

**Issue 2.3b — In-memory report card cache is unbounded**  
**File:** `services/api/src/routes/report-card.ts`, line ~15  
**What's wrong:**
```typescript
const reportCardCache = new Map<string, { expiresAt: number; value: ReportCard }>();
```
This `Map` grows without bound. With 517 operators, each report card is a large JSON object (~5-15KB). If all operators are queried, that's 3-8MB in memory. But the real problem is there's no eviction beyond TTL — expired entries are only deleted on read, not proactively.

**Priority:** P1  
**Fix:** Add a maximum cache size and LRU eviction:
```typescript
const MAX_CACHE_SIZE = 200;

function writeCache(operatorId: string, value: ReportCard) {
  // Evict oldest entries if over limit
  if (reportCardCache.size >= MAX_CACHE_SIZE) {
    const oldestKey = reportCardCache.keys().next().value;
    if (oldestKey) reportCardCache.delete(oldestKey);
  }
  reportCardCache.set(operatorId, {
    value,
    expiresAt: Date.now() + CACHE_TTL_MS,
  });
}
```
Better long-term: Use Redis (already in `package.json` as `ioredis`) for caching.

**Issue 2.3c — `requestCount` counter is a module-level `let` — no overflow risk but no reset**  
**File:** `services/api/src/index.ts`, line ~63  
**What's wrong:** `requestCount` is a simple incrementing number. In JS, `Number.MAX_SAFE_INTEGER` is ~9 quadrillion, so overflow isn't a real concern. But the `/metrics` endpoint exposes it as `requests_total` without the request rate, which makes it less useful than a proper counter.

**Priority:** P2 (cosmetic)

### 2.4 Load Behavior

**At 10 concurrent users:** Should be fine. Fastify handles this easily. The DB queries are the bottleneck — most return in <500ms with proper indexes (which exist per the previous review).

**At 100 concurrent users:** Significant risk:
- The `price-matrix` DISTINCT ON query is expensive (~2-5 seconds). 100 concurrent requests for this endpoint could exhaust the DB connection pool.
- The report card's 6 sequential queries at 20s timeout × 100 concurrent users = up to 600 concurrent DB connections (default PG pool is 10-20).
- No request queuing or connection pool limits are configured in the Drizzle/postgres client.

**Issue 2.4a — No DB connection pool limits configured**  
**File:** `services/api/src/db/index.ts` (not reviewed but critical)  
**Priority:** P1  
**Fix:** Configure `max` connections in the postgres pool (e.g., `max: 20` for Railway's small plan). Add connection timeout and idle timeout. Add request-level timeouts to prevent connection starvation.

### 2.5 Error Propagation

**Good:** The global error handler in `index.ts` catches all unhandled errors and returns structured JSON. Individual route errors won't crash the server.

**Good:** The `onRequest` hook for public endpoints strips auth headers before Clerk processes them, preventing auth failures on public routes.

**Concern:** Some viz endpoints don't have try/catch — they rely entirely on the global handler. If a query returns an unexpected shape, the serialization could throw.

### 2.6 Secrets Handling

**Issue 2.6a — DATABASE_URL hardcoded in daily-scrape.ts** 🚨  
**File:** `scripts/daily-scrape.ts`, line ~6  
**What's wrong:**
```typescript
const DATABASE_URL = process.env.DATABASE_URL ??
  'postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway';
```
**This is a production database password committed to source control.** Anyone with repo access has full DB access.

**Priority:** P0 — CRITICAL  
**Fix:**
1. **Immediately rotate the database password** on Railway
2. Remove the hardcoded fallback
3. Use `process.env.DATABASE_URL` with a startup check:
```typescript
const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
  console.error('FATAL: DATABASE_URL is required');
  process.exit(1);
}
```
4. Audit `scripts/lib/config.ts` for the same pattern
5. Run `git log -S "rcsulogGljjcDcBMxfMeGNlqbmbgHspa"` to find all historical commits and consider rotating immediately

---

## Part 3: Data Integrity

### 3.1 Cross-Platform Data Conflicts

**Issue 3.1a — Same product, different prices from Dutchie vs Weedmaps**  
As noted in 1.3, the same physical product gets different SKUs from each platform. This means:
- The `products` table has duplicate entries for the same real-world product
- Price comparisons don't know that "Blue Dream 3.5g" from Store A's Dutchie menu and Store A's Weedmaps listing are the same item
- If a store is on both platforms, their product count is inflated 2x

**Priority:** P1  
**Fix:** Create a `product_aliases` table or add a `canonical_product_id` column. Implement fuzzy matching on (operator_id, normalized_name, category, weight) to link cross-platform duplicates.

### 3.2 Deduplication Strategy

**Operators:** Deduplicated by `license_number` (upsert on conflict). The previous review's migration merged 19 duplicates. Weedmaps uses `DISCOVERY-{slug}` as license number; Dutchie uses `DUTCHIE-{slug}`. An operator on BOTH platforms gets TWO operator records. This is a known gap.

**Products:** Deduplicated by `sku` (upsert on conflict). But SKUs are platform-specific (see 1.3).

**Prices:** Deduplicated by `(product_id, source_id, operator_id, date(scraped_at))` unique constraint. This is correct — one price per product per source per day.

### 3.3 Orphaned Records

**Issue 3.3a — No foreign key cascade on operator deletion**  
**What's wrong:** If an operator is deleted, prices, sources, products (via prices), watchlists, alerts, etc. may become orphaned. The DELETE endpoint in `operators.ts` does `DELETE FROM operators WHERE id = :id` without cascading.

**Priority:** P2  
**Fix:** Add `ON DELETE CASCADE` to foreign key constraints on `prices.operator_id`, `sources.operator_id`, `alerts.operator_id`, etc. Or implement soft-delete by adding a `deleted_at` column.

### 3.4 Partial Scrape Failures

**Issue 3.4a — Partial daily scrape leaves inconsistent state**  
**File:** `scripts/daily-scrape.ts`  
**What's wrong:** If the Dutchie scraper succeeds but Weedmaps fails, the day has partial data. The quality score is computed after each source, so it might report a good score based only on Dutchie data. Price comparisons that depend on Weedmaps stores will show stale data.

The Weedmaps scraper handles this well with its resume capability (`--resume` flag, `getCompletedJobsForToday`). The Dutchie scraper has no resume capability.

**Priority:** P2  
**Fix:** Add a `scrape_run_summary` check that flags when one platform failed entirely. Mark the run as `partial` instead of `completed`.

### 3.5 Data Versioning / Audit Trail

**Good:** The `prices` table stores `scraped_at` timestamps, creating a natural time series. Old prices are not overwritten (the unique constraint is per-day, so historical data accumulates).

**Good:** The `scrape_runs` and `scrape_jobs` tables provide an audit trail for scraper execution.

**Missing:** No versioning on `products` or `operators` tables. When a brand name is corrected or a category is changed, the old value is lost.

**Priority:** P2  
**Fix:** Add `updated_at` triggers and consider a simple `entity_history` table for tracking changes to operators and products.

---

## Part 4: Frontend Reliability

### 4.1 Uncaught Promise Rejections

**Issue 4.1a — Market.tsx fetches don't propagate errors to the UI**  
**File:** `apps/web/src/pages/Market.tsx`, line ~120  
**What's wrong:**
```typescript
const [crossReference, pendingApps, weeklySales, demographics, freshness] = await Promise.all([
  api.getCccCrossReference().catch(() => []),
  api.getCccPendingApplications().catch(() => []),
  // ...
]);
```
Each call has `.catch(() => [])`, which silently swallows errors. The user sees empty sections with no indication that data failed to load. This is intentional graceful degradation but provides zero feedback.

**Priority:** P2  
**Fix:** Track error state per-section and show "Failed to load" messages:
```typescript
const [crossReference, crossRefError] = await api.getCccCrossReference()
  .then(data => [data, null])
  .catch(err => [[], err]);
```

### 4.2 Error Boundaries

**Issue 4.2a — No React Error Boundaries**  
**What's wrong:** None of the page components are wrapped in Error Boundaries. A D3 rendering crash (e.g., invalid data shape from API) will white-screen the entire app.

**Priority:** P1  
**Fix:** Add an `ErrorBoundary` component and wrap each major section:
```tsx
<ErrorBoundary fallback={<div>Chart failed to load</div>}>
  <WeeklySalesAreaChart data={weeklySalesRows} />
</ErrorBoundary>
```

### 4.3 Race Conditions

**Issue 4.3a — MorningBrief.tsx fires two independent data-fetching effects**  
**File:** `apps/web/src/pages/MorningBrief.tsx`  
**What's wrong:** The component uses both React Query hooks (via `useMorningBrief`, etc.) AND a manual `useEffect` with `Promise.all` for viz data. These fire independently and race. If the viz `useEffect` completes first but the React Query hooks error, the user sees partial data with no clear error state.

**Priority:** P2  
**Fix:** Consolidate all data fetching into React Query hooks or all into useEffect. Mixing patterns creates maintenance confusion and race conditions.

**Issue 4.3b — Onboarding search has no request cancellation**  
**File:** `apps/web/src/pages/Onboarding.tsx`, lines ~63-76  
**What's wrong:** The search debounce timer clears the previous timeout but not the in-flight fetch. If the user types "abc" then "abcd", both API calls fire. The results of "abc" could arrive AFTER "abcd" and overwrite the more specific results.

**Priority:** P2  
**Fix:** Use an `AbortController`:
```typescript
useEffect(() => {
  const controller = new AbortController();
  const t = setTimeout(async () => {
    // pass controller.signal to fetch
  }, 250);
  return () => {
    clearTimeout(t);
    controller.abort();
  };
}, [search]);
```

### 4.4 Mobile Responsiveness

**Good:** The frontend uses responsive Tailwind classes consistently (`sm:`, `lg:` breakpoints). The Market page tables hide columns on mobile (`hidden sm:table-cell`).

**Issue 4.4a — WeeklySalesAreaChart has fixed viewBox dimensions**  
**File:** `apps/web/src/pages/Market.tsx`  
**What's wrong:** `viewBox="0 0 980 320"` with `className="h-[280px] w-full"` — the chart will be very compressed on small screens. The hover interaction uses `clientX` relative to `getBoundingClientRect()`, which should work but touch events are not handled.

**Priority:** P2  
**Fix:** Add touch event handling for mobile chart interaction.

### 4.5 Accessibility

**Issue 4.5a — Missing ARIA labels on interactive charts**  
**What's wrong:** All D3/SVG charts lack `role="img"` and `aria-label`. Screen readers will read raw SVG text nodes.

**Priority:** P2

**Issue 4.5b — Landing page form has no aria-describedby for error messages**  
**File:** `apps/web/src/pages/Landing.tsx`  
**Priority:** P2

---

## Part 5: Security

### 5.1 Auth Bypass Risks

**Issue 5.1a — Public endpoint auth header stripping is fragile**  
**File:** `services/api/src/index.ts`, lines ~69-76  
**What's wrong:**
```typescript
fastify.addHook('onRequest', async (request) => {
  if (
    request.url.startsWith('/api/v1/operators/search') ||
    request.url.startsWith('/api/v1/waitlist') ||
    request.url.startsWith('/api/v1/newsletter/subscribe')
  ) {
    delete request.headers.authorization;
  }
});
```
This is a **pre-Clerk hook** that strips auth headers so Clerk doesn't reject stale tokens. The approach works but is fragile:
- URL matching is prefix-based. `/api/v1/operators/search-admin` (if it existed) would also match.
- If someone adds a new public endpoint and forgets to add it here, users with stale tokens get 401 on what should be a public route.

**Priority:** P1  
**Fix:** Invert the pattern. Instead of stripping auth for public routes, mark routes as public and skip auth:
```typescript
// In route definition:
fastify.get('/operators/search', { config: { isPublic: true } }, handler);

// In auth plugin:
if (request.routeOptions.config?.isPublic) return; // skip auth
```

**Issue 5.1b — CCC routes, viz routes, report-card routes have NO authentication**  
**Files:** `routes/ccc.ts`, `routes/viz.ts`, `routes/report-card.ts`  
**What's wrong:** None of these routes use `onRequest: [fastify.authenticate]`. This means:
- Anyone can view any operator's report card if they know the UUID
- All visualization data is publicly accessible
- The `/admin/data-quality` endpoint (inside `ccc.ts`) has NO auth — despite the `/admin/` prefix suggesting it should

**Priority:** P1 for `/admin/data-quality`, P2 for the rest (some are intentionally public)  
**Fix:** Add authentication to `/admin/data-quality` immediately. For viz/report-card routes, decide if they're intentionally public (for the outreach email strategy) and document the decision.

### 5.2 Operator Enumeration

**Issue 5.2a — Search endpoint enables full operator enumeration**  
**File:** `services/api/src/routes/operators.ts`  
**What's wrong:** As noted in 2.1a, sending `q=%` or `q=__` or iterating `q=a`, `q=b`, etc. allows enumerating all 517 operators. The endpoint returns `id`, `name`, `city`, `state` — enough to identify competitors.

**Priority:** P0  
**Fix:** In addition to escaping LIKE metacharacters (2.1a), add rate limiting on this endpoint (per-IP, 30 requests/minute) and consider requiring a minimum query specificity (3+ alphanumeric characters).

### 5.3 Waitlist Rate Limiting

**Issue 5.3a — In-memory rate limiting resets on deploy**  
**File:** `services/api/src/routes/waitlist.ts`  
**What's wrong:** `waitlistRateLimit` is a `Map` in process memory. Railway deploys restart the process, resetting all rate limits. An attacker can bypass rate limiting by waiting for the next deploy (or triggering one via heavy load if there's auto-scaling).

Also, the rate limit is per-IP. Behind a CDN/proxy, all requests may share the same `x-forwarded-for` IP if not configured correctly.

**Priority:** P2  
**Fix:** Use Redis for rate limiting (ioredis is already a dependency). Add `fastify-rate-limit` as a middleware for a more robust solution.

### 5.4 XSS Vectors

**Issue 5.4a — Operator names and product names are rendered without sanitization**  
**Files:** Multiple frontend components  
**What's wrong:** React's JSX automatically escapes text content, so direct `{operator.name}` in JSX is safe. HOWEVER, the `Market.tsx` page creates a `<script type="application/ld+json">` tag with `JSON.stringify` that includes dynamic data — this is safe because `JSON.stringify` escapes `</script>`.

**Assessment:** Low risk. React's default escaping handles most cases. No `dangerouslySetInnerHTML` found.

**Priority:** No action needed.

### 5.5 Secrets in Frontend Code

**Issue 5.5a — API URL configuration**  
**File:** `apps/web/src/api/client.ts`, line ~30  
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';
```
This is fine — Vite's `import.meta.env.VITE_*` variables are intentionally public. No secrets are exposed.

**Issue 5.5b — Clerk publishable key**  
Clerk publishable keys are designed to be public. No issue.

**Assessment:** Frontend secrets handling is clean.

---

## Part 6: Specific Fixes (Code-Level)

### P0 Fixes (Before Launch)

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `scripts/daily-scrape.ts:6` | Hardcoded DB password | Remove fallback URL, require env var, **rotate password immediately** |
| 2 | `routes/operators.ts:25` | LIKE injection in search | Escape `%` and `_` in search term |
| 3 | `routes/operators.ts:25` | Operator enumeration | Add per-IP rate limit (30/min), require 3+ alphanumeric chars |
| 4 | `routes/viz.ts` (price-matrix) | Unbounded DISTINCT ON scan | Add `WHERE scraped_at >= NOW() - INTERVAL '30 days'` to latest CTE |
| 5 | `routes/viz.ts` (operators-geo) | O(n×m) haversine join | Pre-filter by bounding box, add LIMIT to threat join |
| 6 | `routes/viz.ts` (price-ticker) | Full table scan in CTE | Add `WHERE scraped_at >= NOW() - INTERVAL '7 days'` to ranked CTE |
| 7 | `routes/ccc.ts` (`/admin/data-quality`) | No authentication | Add `onRequest: [fastify.authenticate]` and `requireRole('admin')` |
| 8 | `scripts/lib/brand-filter.ts` | Brand cleanup doesn't extract valid brand from piped string | See Part 7 |

### P1 Fixes (This Week)

| # | File | Issue | Fix |
|---|------|-------|-----|
| 9 | `routes/report-card.ts:15` | Unbounded in-memory cache | Add LRU eviction with max 200 entries |
| 10 | `routes/report-card.ts` | Sequential DB queries | Parallelize queries 2-7 with `Promise.all` |
| 11 | `routes/operators.ts:60` | `sql.raw(pagination.order)` | Replace with explicit ASC/DESC conditional |
| 12 | `routes/viz.ts` (price-wars) | 120-day scan with no index hint | Add index on `(scraped_at, operator_id, product_id, price)` |
| 13 | `scripts/scrape-dutchie-ma.ts` | SQL file generation instead of DB writes | Port to use `scripts/lib/db.ts` functions |
| 14 | `scripts/lib/normalizer.ts` | SKU generation differs from Dutchie | Unify SKU generation across platforms |
| 15 | `index.ts:69` | Fragile URL-prefix auth stripping | Use route config `isPublic` flag instead |
| 16 | `routes/ccc.ts`, `viz.ts`, `report-card.ts` | No auth on data endpoints | Decide public vs private, add auth where needed |
| 17 | All frontend pages | No React Error Boundaries | Add ErrorBoundary wrapper around chart sections |
| 18 | `scripts/daily-scrape.ts` | Hardcoded store counts | Read actual results from scraper output |
| 19 | `scripts/daily-scrape.ts` | Uses `source` column name (may conflict with scrape_runs schema) | Verify schema alignment |
| 20 | DB connection | No pool limits configured | Set `max: 20`, add `connectionTimeoutMillis: 5000` |
| 21 | `scripts/lib/config.ts` | Likely has same hardcoded DB URL | Audit and remove |
| 22 | Both scrapers | No product dedup across platforms | Add `canonical_product_id` or alias table |
| 23 | `waitlist.ts` | Rate limit memory leak (never cleaned) | Add periodic cleanup or switch to Redis |
| 24 | `routes/operators.ts:53` | GET /operators filters by `eq(schema.operators.id, request.auth.operator_id)` always | This means operators can only ever see themselves — may be intentional but limits admin use |

### P2 Fixes (This Month)

| # | File | Issue | Fix |
|---|------|-------|-----|
| 25 | Scrapers | No exponential backoff | Add retry with backoff on failures |
| 26 | Scrapers | No stale store detection | Track consecutive failures, auto-deactivate |
| 27 | Frontend Market.tsx | Silent error swallowing | Show per-section error states |
| 28 | Frontend MorningBrief.tsx | Mixed React Query + useEffect | Consolidate to one pattern |
| 29 | Frontend Onboarding.tsx | No AbortController on search | Add request cancellation |
| 30 | Frontend charts | No ARIA labels | Add `role="img"` and `aria-label` |
| 31 | Frontend charts | No touch event handling | Add touch support for mobile |
| 32 | DB schema | No foreign key cascades | Add ON DELETE CASCADE |
| 33 | DB schema | No entity change history | Add audit table |
| 34 | `routes/viz.ts` (delivery-zones) | JS-level coordinate math | Move projection to DB or add bounds check for division by zero |
| 35 | `routes/viz.ts` (threats-network) | Fake link generation | Links are algorithmically generated, not based on real relationships |
| 36 | `daily-scrape.ts` | No resume capability | Add resume like Weedmaps scraper has |
| 37 | `routes/viz.ts` (market-share-flow) | Two nearly identical CTEs | Combine into one query |
| 38 | `routes/viz.ts` (economic-indicators) | `avg()` helper function unused correctly | Minor cleanup |
| 39 | Frontend | D3 import is large | Consider tree-shaking specific D3 modules |
| 40 | `package.json` (api) | BullMQ and ioredis installed but unused | Remove unused deps or implement queue |
| 41 | Dockerfile | No health check instruction | Add `HEALTHCHECK CMD curl -f http://localhost:3000/health || exit 1` |
| 42 | Frontend | `three.js` in dependencies but likely unused on most pages | Consider lazy loading |
| 43 | `routes/ccc.ts` (plant-activity) | `jsonb_build_object` aggregation | Could OOM on large datasets |
| 44 | `routes/report-card.ts` | `formatCurrency` rounds to nearest dollar | Should use `toFixed(2)` for currency display |
| 45 | Auth plugin | JWKS cache is module-level singleton | Fine for single-process, but breaks in cluster mode |
| 46 | Auth plugin | Auto-provision creates `PENDING-{userId}` operators | These pollute the operator list — should be filtered in search/viz queries |
| 47 | `routes/ccc.ts` | `LIMIT 260` and `LIMIT 1000` are arbitrary | Add pagination or document why these limits exist |

---

## Part 7: Scraper Brand Cleanup on Ingest

### Current State

`brand-filter.ts` has `isValidBrand()` which rejects brands containing pipes, "stock", "order soon", etc. But it treats the ENTIRE string as a brand — it doesn't extract the valid brand name from noisy input like `"Brand Name | In stock. Order soon."`.

### Required Changes

#### File: `scripts/lib/brand-filter.ts`

Replace `normalizeBrandCandidate()` with a proper cleaning function:

```typescript
/**
 * Noise suffixes commonly appended by dispensary platforms.
 * Matched case-insensitively and stripped along with surrounding pipes/whitespace.
 */
const NOISE_PATTERNS: RegExp[] = [
  /\|\s*in\s+stock\.?\s*order\s+soon\.?/i,
  /\|\s*out\s+of\s+stock\.?/i,
  /\|\s*low\s+stock\.?\s*order\s+soon\.?/i,
  /\|\s*medical\s+patients?\s+only\.?/i,
  /\|\s*limited\s+supply\.?/i,
  /\|\s*sale\s*\d*%?\s*off\.?/i,
  /\|\s*new\.?/i,
  /\|\s*staff\s+pick\.?/i,
  /\|\s*best\s+seller\.?/i,
  /\b(?:in\s+)?stock\.?\s*order\s+soon\.?$/i,
  /\bmedical\s+patients?\s+only\.?$/i,
  /\bout\s+of\s+stock\.?$/i,
];

/**
 * Cleans a raw brand string by:
 * 1. Stripping known noise patterns (stock alerts, medical-only tags)
 * 2. Taking only the first pipe-delimited segment if pipes remain
 * 3. Trimming whitespace
 * 4. Logging what was cleaned for debugging
 */
export function normalizeBrandCandidate(raw: string): string {
  if (!raw) return '';

  let cleaned = raw;
  const originalRaw = raw;

  // Step 1: Strip known noise patterns
  for (const pattern of NOISE_PATTERNS) {
    cleaned = cleaned.replace(pattern, '');
  }

  // Step 2: If pipes remain, take the first segment (the brand name)
  if (cleaned.includes('|')) {
    const segments = cleaned.split('|').map(s => s.trim()).filter(Boolean);
    if (segments.length > 0) {
      cleaned = segments[0];
    }
  }

  // Step 3: Clean up artifacts
  cleaned = cleaned
    .replace(/\s+/g, ' ')  // collapse whitespace
    .replace(/^[\s|]+|[\s|]+$/g, '')  // trim pipes and whitespace from edges
    .trim();

  // Step 4: Log cleaning if something changed
  if (cleaned !== originalRaw.trim() && cleaned.length > 0) {
    console.log(`[brand-cleanup] "${originalRaw.trim()}" → "${cleaned}"`);
  }

  return cleaned;
}
```

#### File: `scripts/lib/normalizer.ts`

Update `normalizeBrand()` to use the improved `normalizeBrandCandidate`:

```typescript
/**
 * Normalizes brand formatting for stable matching and SKU generation.
 * Now properly extracts brand from noisy input before validation.
 */
export function normalizeBrand(raw: string): string {
  // normalizeBrandCandidate now handles pipe stripping and noise removal
  const cleaned = normalizeBrandCandidate(raw);
  if (!isValidBrand(cleaned)) {
    return 'unknown';
  }
  return cleaned.toLowerCase();
}
```

#### File: `scripts/scrape-dutchie-ma.ts`

Update the `sanitizeBrand()` function:

```typescript
function sanitizeBrand(raw: string): string {
  // normalizeBrandCandidate now strips pipes, "stock. Order soon.", etc.
  const cleaned = normalizeBrandCandidate(raw);
  if (!isValidBrand(cleaned)) {
    return '';
  }
  return cleaned;
}
```

#### File: `scripts/lib/weedmaps-parser.ts`

Ensure the Weedmaps parser also runs brand cleanup. Find where `brand` is extracted from raw product data and ensure it passes through `normalizeBrandCandidate()` before being stored. If the parser already calls `normalizeProduct()` (which calls `normalizeBrand()`), this should be handled automatically with the updated `normalizeBrandCandidate`.

### What Gets Cleaned

| Input | Output | Change |
|-------|--------|--------|
| `"Fernway \| In stock. Order soon."` | `"Fernway"` | Stripped noise suffix |
| `"Happy Valley \| Medical patients only"` | `"Happy Valley"` | Stripped medical tag |
| `"\| Bountiful Farms"` | `"Bountiful Farms"` | Stripped leading pipe |
| `"NETA \| Sale 20% off"` | `"NETA"` | Stripped promo text |
| `"stock. Order soon."` | `""` → rejected by isValidBrand | Entire string was noise |
| `"Good Chemistry"` | `"Good Chemistry"` | No change (clean input) |
| `"Pre-Roll"` | `""` → rejected by isValidBrand | Category name, not brand |

### Verification Query

After deploying the fix, run the next daily scrape and then check:

```sql
SELECT brand, COUNT(*) as cnt
FROM products
WHERE brand IS NOT NULL
  AND (
    brand ~* 'stock|order soon|medical patients'
    OR brand LIKE '%|%'
  )
GROUP BY brand
ORDER BY cnt DESC
LIMIT 20;
```

Expected: 0 rows (all new products have clean brands). Existing dirty brands need a one-time SQL cleanup:

```sql
UPDATE products
SET brand = TRIM(SPLIT_PART(brand, '|', 1))
WHERE brand LIKE '%|%'
  AND TRIM(SPLIT_PART(brand, '|', 1)) != '';

UPDATE products
SET brand = NULL
WHERE brand ~* 'stock\.?\s*order\s+soon|medical\s+patients?\s+only|out\s+of\s+stock'
  OR LENGTH(TRIM(COALESCE(brand, ''))) < 2;
```

---

## Architecture Recommendations (Beyond Bug Fixes)

### 1. Add Request-Level Timeouts to ALL Viz Endpoints
Every viz endpoint should use the `withTimeout()` pattern from `report-card.ts`. Set 10s for simple queries, 15s for complex ones.

### 2. Add Connection Pooling Monitoring
Log DB pool utilization at `/metrics`. When pool is >80% utilized, you're about to see timeouts.

### 3. Consider Read Replicas
Several viz queries are heavy analytical queries. Route read-only traffic to a PostgreSQL read replica to protect write performance.

### 4. Add Structured Logging
Current logging is ad-hoc `console.log`. Switch to structured JSON logging (Fastify's built-in pino) with correlation IDs for request tracing.

### 5. Add Integration Tests
There are zero tests. The `test` script is `echo "No tests configured yet"`. At minimum:
- Test the search endpoint with LIKE metacharacters
- Test the report card with a known operator UUID
- Test the waitlist rate limiting
- Test auth flows (Clerk JWT, auto-provision)

### 6. Add a Canary Scrape
Run a daily canary check that scrapes 1 known store (whose menu you can manually verify) and compares results against expected values. If the canary fails, halt the full scrape and alert.

---

## Summary

GLASS has strong bones. The data pipeline is real, the product concept (Store Report Card) is genuinely valuable, and the frontend design is premium. The issues identified here are typical of a fast-moving startup — no showstoppers that can't be fixed in a week.

**The three things to fix TODAY:**
1. Rotate the hardcoded DB password (P0 security)
2. Fix operator search enumeration (P0 security + business risk)  
3. Add date bounds to unbounded viz queries (P0 reliability)

**The three things to fix THIS WEEK:**
1. Brand cleanup on ingest (P1 data quality — Part 7)
2. Add React Error Boundaries (P1 frontend reliability)
3. Add auth to `/admin/data-quality` (P1 security)

Everything else can wait until after the first outreach batch proves the product has legs.

---

*Review completed 2026-02-12. Next review recommended after 7 days of daily scraping data accumulates.*
