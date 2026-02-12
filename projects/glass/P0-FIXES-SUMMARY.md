# GLASS P0 Security Fixes — Summary

**Date:** 2026-02-12  
**Commit:** `412806d`  
**Branch:** `main`  
**Files changed:** 14 (13 modified, 1 new)

---

## Fix 1: Remove Hardcoded DB Password (P0 — CRITICAL)

**Files:** `scripts/daily-scrape.ts`, `scripts/import-ccc-data.ts`, `scripts/auto-invite/db.ts`

**Before:**
```typescript
const DATABASE_URL = process.env.DATABASE_URL ?? 
  'postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway';
```

**After:**
```typescript
const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
  console.error('FATAL: DATABASE_URL environment variable is required');
  process.exit(1);
}
```

**Verification:** `grep -r "rcsulogGljjcDcBMxfMeGNlqbmbgHspa" src/` returns 0 results.

> ⚠️ **ACTION REQUIRED:** Rotate the DB password on Railway since it was committed to git history.

---

## Fix 2: Operator Search — Prevent Enumeration (P0)

**File:** `services/api/src/routes/operators.ts`

**Changes:**
- Added `escapeLike()` function to escape `%`, `_`, `\` in LIKE patterns
- Query minimum length: 2 chars (was already there)
- Query maximum length: 100 chars (new)
- Result limit: 20 (was 15, now 20+1 to detect truncation)
- Returns `{ truncated: true, message: "..." }` if results were truncated
- Returns 400 status for invalid queries (was 200 with empty data)

**Before:**
```typescript
ilike(schema.operators.name, `%${searchTerm}%`)
```

**After:**
```typescript
const safeQuery = escapeLike(q.trim());
ilike(schema.operators.name, `%${safeQuery}%`)
```

**Also fixed:** `sql.raw(pagination.order!)` replaced with explicit `sql\`ASC\`` / `sql\`DESC\`` to prevent SQL injection in orderBy.

---

## Fix 3: Protect Admin Endpoints (P0)

**File:** `services/api/src/routes/ccc.ts`

**Changes:**
- `/admin/data-quality` now requires either:
  - `?key=<ADMIN_API_KEY>` query parameter, OR
  - `X-Admin-Key: <ADMIN_API_KEY>` header
- If `ADMIN_API_KEY` env var is not set, endpoint remains open (dev mode)
- `/admin/waitlist/stats` already had `onRequest: [fastify.authenticate]` + `requireRole('admin')` — verified secure
- Waitlist stats already mask emails via `maskEmail()` — verified correct

**New endpoint:** `GET /admin/duplicate-products?operator_id=UUID` with same admin key gate.

---

## Fix 4: Bound All CTE Queries (P0)

**File:** `services/api/src/routes/viz.ts`

**Changes:**
| Endpoint | Before | After |
|----------|--------|-------|
| `/viz/price-matrix` | Full table DISTINCT ON scan | `WHERE scraped_at >= NOW() - INTERVAL '7 days'` |
| `/viz/price-ticker` | Full table LAG scan | `WHERE scraped_at >= NOW() - INTERVAL '7 days'` |
| `/viz/price-distribution` | Full table DISTINCT ON scan | `WHERE scraped_at >= NOW() - INTERVAL '7 days'` |
| `/viz/operator-compare` | Full table DISTINCT ON scan | `WHERE scraped_at >= NOW() - INTERVAL '7 days'` |
| `/viz/proximity` | LIMIT 100 | LIMIT 50 |
| `/viz/category-breakdown` | No LIMIT | LIMIT 50 |

Other endpoints (`price-cascade`, `price-volatility`, `price-wars`, `market-share-flow`, etc.) already had date filters.

---

## Fix 5: Escape LIKE in All Search Routes (P0)

**Files:** `routes/operators.ts`, `routes/prices.ts`, `routes/products.ts`

Added `escapeLike()` to every `ilike()` call that accepts user input:

- `operators.ts`: search endpoint + city filter
- `prices.ts`: SKU filter + brand filter  
- `products.ts`: brand filter + search filter

---

## Fix 6: Brand Cleanup on Ingest (P0)

**Files:** `scripts/lib/brand-filter.ts`, `scripts/lib/db.ts`

**`normalizeBrandCandidate()` — Before:**
```typescript
export function normalizeBrandCandidate(raw: string): string {
  return raw.replace(/\s+/g, ' ').trim();
}
```

**After:** Now strips 9 noise patterns (stock alerts, medical tags, promo text) and extracts brand from pipe-delimited strings before validation.

**`upsertProduct()` — Before:**
```typescript
brand || null
```

**After:**
```typescript
cleanBrand(brand) // Runs normalizeBrandCandidate + isValidBrand, returns null for garbage
```

**Examples:**
| Input | Output |
|-------|--------|
| `"Fernway \| In stock. Order soon."` | `"Fernway"` |
| `"Happy Valley \| Medical patients only"` | `"Happy Valley"` |
| `"stock. Order soon."` | `null` |
| `"Good Chemistry"` | `"Good Chemistry"` |

---

## Fix 7: Cross-Platform Product Deduplication (P0)

**Files:** `services/api/src/routes/ccc.ts`, database

**Changes:**
- Created `GET /admin/duplicate-products?operator_id=UUID` endpoint
  - Groups products by `LOWER(TRIM(name)) + category`
  - Returns duplicate count, all product IDs, brands, SKUs
  - Protected by admin key gate
- Created database index: `CREATE INDEX idx_products_name_lower ON products (LOWER(name))`

This does NOT auto-merge — it flags duplicates for manual review.

---

## Fix 8: Rate Limit Cache Cleanup (P0)

**Files:** `services/api/src/routes/waitlist.ts`, `services/api/src/routes/report-card.ts`

**Waitlist rate limit map:**
- Added `setInterval` cleanup every 10 minutes
- Deletes entries older than the rate limit window (1 hour)

**Report card cache:**
- Added `setInterval` cleanup every 10 minutes for expired entries
- Added LRU eviction with `MAX_CACHE_SIZE = 200` in `writeCache()`
- When cache is full, oldest entry is evicted before inserting new one

---

## Bonus: React Error Boundaries (P1)

**Files:** `apps/web/src/components/ErrorBoundary.tsx` (new), `apps/web/src/main.tsx`

- Created `ErrorBoundary` class component with:
  - `getDerivedStateFromError` for error state
  - `componentDidCatch` for logging
  - "Try again" button that resets error state
  - Custom fallback prop support
- Wrapped `<App />` in `<ErrorBoundary>` in `main.tsx`

---

## Remaining Action Items

1. **Rotate DB password on Railway** — the old password is in git history
2. **Set `ADMIN_API_KEY` env var** on Railway for admin endpoint protection
3. **Run brand cleanup SQL** on existing dirty data:
   ```sql
   UPDATE products SET brand = TRIM(SPLIT_PART(brand, '|', 1))
   WHERE brand LIKE '%|%' AND TRIM(SPLIT_PART(brand, '|', 1)) != '';
   
   UPDATE products SET brand = NULL
   WHERE brand ~* 'stock\.?\s*order\s+soon|medical\s+patients?\s+only|out\s+of\s+stock'
     OR LENGTH(TRIM(COALESCE(brand, ''))) < 2;
   ```
4. **Deploy** — Railway auto-deploys on push to main
