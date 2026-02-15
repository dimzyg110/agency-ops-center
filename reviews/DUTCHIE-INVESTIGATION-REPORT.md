# Dutchie Scraper Investigation - Root Cause Analysis

**Investigation by**: Codex Dutchie Deep Dive  
**Date**: 2026-02-15  
**Status**: COMPLETE - Root Cause Identified

---

## Executive Summary

**Primary Root Cause**: DB schema misconfiguration introduced in commit `9ba354d` (2026-02-14)  
**Secondary Issue**: Cloudflare bot blocking  

The Dutchie scraper is broken due to a schema mismatch - the scraper code now points to `public` schema but tables are in `glass` schema.

---

## Findings

### 1) Database - No Dutchie Jobs Recorded

```
jobs_last_24h = 0
failed_jobs_last_24h = 0
total_dutchie_runs = 0
total_dutchie_jobs = 0
```

No scrape runs/jobs are being created at all.

### 2) Schema Mismatch (PRIMARY)

**Commit `9ba354d`** (2026-02-14): `fix(db): consolidate to public schema, remove glass schema references`

Changed in `scrapers/lib/db.ts`:
- **Before**: `SET search_path TO glass, public`
- **After**: `SET search_path TO public`

**Reality**: Tables (`scrape_runs`, `scrape_jobs`, etc.) exist in `glass` schema, NOT `public`.

```sql
SET search_path TO public;
SELECT count(*) FROM scrape_runs;
-- ERROR: relation "scrape_runs" does not exist

SET search_path TO glass;
SELECT count(*) FROM scrape_runs;
-- works
```

**Impact**: `acquireRunLock()` cannot read/insert `scrape_runs`, so runs fail before jobs are created.

### 3) Cloudflare Blocking (SECONDARY)

Live curl test to Dutchie returns:
- `<title>Attention Required! | Cloudflare</title>`
- "Sorry, you have been blocked"
- "Performing security verification"

This environment's IP is being blocked. Even with DB fixed, would need to handle Cloudflare challenges.

---

## Recommended Fixes

### A) Fix DB Search Path (REQUIRED)

**File**: `scrapers/lib/db.ts`

```diff
- pool.on('connect', (client) => {
-   client.query('SET search_path TO public');
- });
+ const DB_SCHEMA = process.env.DB_SCHEMA || 'glass';
+ pool.on('connect', (client) => {
+   client.query(`SET search_path TO ${DB_SCHEMA}, public`);
+ });
```

### B) Add Cloudflare Detection)

**File**: (Recommended `scrapers/dutchie/index.ts`

Add `assertNotBlocked()` method to detect Cloudflare challenge pages and throw actionable errors.

---

## Action Required

This is a **production-breaking bug** introduced in yesterday's deployment. Recommend immediate fix + redeploy.
