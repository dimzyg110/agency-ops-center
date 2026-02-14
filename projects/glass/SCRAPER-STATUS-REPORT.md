# SCRAPER STATUS REPORT

Generated: 2026-02-14 UTC  
Scope: Railway scraper services (dutchie, jane, leafly, weedmaps) + live DB verification using provided Railway `DATABASE_URL`.

---

## Executive Summary

I verified the exact database and code paths requested.

**Result:** I cannot confirm Randy’s claim that all 4 scrapers are running successfully on Railway from production telemetry, because the `scrape_runs` and `scrape_jobs` tables at the provided Railway database are empty.

What is confirmed:
- All 4 scraper services **exist in repo** with Railway deployment configs and cron schedules.
- Service entrypoints are implemented and production-oriented (run lock, timeouts, DB writes, notifications).

What is **not** confirmed from DB:
- No recent runs, no job history, no Dutchie failure row, no success-rate data.

---

## 1) Database Verification (provided Railway URL)

Connection used:
`postgresql://postgres:***@turntable.proxy.rlwy.net:18582/railway`

### Schema reality
- `scrape_runs` and `scrape_jobs` are in schema `glass` (not `public`).
- Querying with `SET search_path TO glass, public;` succeeds.

### Query results

#### A. Last 30 scrape runs across all platforms
```sql
SELECT platform, status, started_at, completed_at, stores_attempted, stores_succeeded,
       stores_failed, products_found, prices_inserted, duration_seconds, source
FROM scrape_runs
ORDER BY started_at DESC
LIMIT 30;
```
**Result:** `0 rows`

#### B. Railway cron vs sandbox source breakdown
```sql
SELECT platform, source, COUNT(*) as runs,
  COUNT(*) FILTER (WHERE status='completed') as completed,
  COUNT(*) FILTER (WHERE status='failed') as failed,
  MAX(started_at) as last_run
FROM scrape_runs
GROUP BY platform, source
ORDER BY platform, source;
```
**Result:** `0 rows`

#### C. scrape_jobs success rates (last 7 days)
Requested query uses `scrape_jobs.platform`, but that column does not exist in this DB schema.
I ran the adapted version joining `sources.source_type`:
```sql
SELECT s.source_type AS platform, j.status, COUNT(*)
FROM scrape_jobs j
JOIN sources s ON s.id = j.source_id
WHERE j.created_at > NOW() - INTERVAL '7 days'
GROUP BY s.source_type, j.status
ORDER BY s.source_type, j.status;
```
**Result:** `0 rows`

#### D. Dutchie last 5 runs + error_log
```sql
SELECT ... FROM scrape_runs WHERE platform='dutchie' ORDER BY started_at DESC LIMIT 5;
```
**Result:** `0 rows`

### Additional DB context
- `sources` has 10 rows, all `source_type='dutchie'`, created around `2026-02-11`.
- `operators` has 10 rows (same time window).
- `prices` has `0` rows.
- `scrape_jobs` has `0` rows.
- `scrape_runs` has `0` rows.

Interpretation: some Dutchie source/operator seeding happened, but no recorded run/job execution persisted in `scrape_runs`/`scrape_jobs` at this DB.

---

## 2) Service Code Verification (Railway entrypoints vs script versions)

## Dutchie
- Railway service: `src/scrapers/dutchie/index.ts`
- Script version: `src/scripts/scrape-dutchie.ts`

Key differences:
- Railway version uses `acquireRunLock`, hard timeout wrapper, Discord notifications, and writes run/job lifecycle via scraper lib DB helpers.
- Railway version is CamoFox-only (explicitly aborts if CamoFox unavailable).
- Script version is a more general/local CLI workflow (discovery flags, richer category snapshotting, worker pool behavior).

## Jane
- Railway service: `src/scrapers/jane/index.ts`
- Script version: `src/scripts/scrape-jane.ts`

Key differences:
- Railway version launches embedded Playwright Firefox and performs browser-context `fetch()` for Algolia via Cloudflare-cleared session.
- Includes run lock + hard timeout + notifications.
- Script version relies on `JaneClient` abstraction and local script orchestration.

## Leafly
- Railway service: `src/scrapers/leafly/index.ts`
- Script version: `src/scripts/scrape-leafly.ts`

Key differences:
- Railway version is browser-first (CamoFox), with page `__NEXT_DATA__`, browser API calls, and direct API fallback.
- Includes run lock + hard timeout + notifications.
- Script version is more traditional script flow and uses a different ingest method label (`leafly_ssr_v1` vs Railway’s `leafly_browser_v1`).

## Weedmaps
- Railway service: `src/scrapers/weedmaps/index.ts`
- Script version: `src/scripts/scrape-weedmaps.ts`

Key differences:
- Railway version is simplified CamoFox service with run lock, timeout wrapper, notifications.
- Script version is much larger local workflow (pagination heuristics, retries/categorized errors/snapshots with plain Playwright Firefox).

Conclusion: the Railway service files are present and purpose-built for production service execution (distinct from local script runners).

---

## 3) Railway Cron Schedules (exact from `railway.toml`)

- `src/scrapers/dutchie/railway.toml` → `cronSchedule = "0 8 * * *"` (08:00 UTC)
- `src/scrapers/jane/railway.toml` → `cronSchedule = "0 7 * * *"` (07:00 UTC)
- `src/scrapers/leafly/railway.toml` → `cronSchedule = "5 7 * * *"` (07:05 UTC)
- `src/scrapers/weedmaps/railway.toml` → `cronSchedule = "30 3 * * *"` (03:30 UTC)

All four also have:
- `restartPolicyType = "NEVER"`
- explicit `startCommand` pointing to each service index.

---

## 4) Dutchie Failure Diagnosis (requested Feb 13 failure)

Unable to diagnose from production run logs in this DB because:
- `scrape_runs` has **no Dutchie rows** (or any rows), therefore no `error_log` entries to inspect.

Code-level likely Dutchie failure modes in `src/scrapers/dutchie/index.ts`:
- DB connectivity failure at startup.
- Run lock denial (active/stale lock behavior).
- CamoFox launch failure (hard fail by design).
- Store-level scraping/parsing errors (captured into `stats.errorLog`).
- Per-store job marked failed when normalized product count is zero.

But the specific Feb 13 failure cannot be proven from queried DB telemetry because no matching run records exist here.

---

## 5) Definitive Platform Status (based on evidence collected)

| Platform | Deployed in repo (service + railway.toml) | Cron configured | Last successful run (DB evidence) | Success rate (DB evidence) | Data freshness |
|---|---|---|---|---|---|
| dutchie | Yes | Yes (`0 8 * * *`) | Not available (no rows) | Not measurable (no rows) | Stale/unknown (no runs, no prices) |
| jane | Yes | Yes (`0 7 * * *`) | Not available (no rows) | Not measurable (no rows) | Stale/unknown |
| leafly | Yes | Yes (`5 7 * * *`) | Not available (no rows) | Not measurable (no rows) | Stale/unknown |
| weedmaps | Yes | Yes (`30 3 * * *`) | Not available (no rows) | Not measurable (no rows) | Stale/unknown |

---

## Issues Found

1. **No production run telemetry in `glass.scrape_runs` / `glass.scrape_jobs`** at provided Railway DB URL.
2. Requested query for `scrape_jobs` assumes a `platform` column that this schema does not have.
3. Evidence suggests partial setup happened for Dutchie sources/operators only, but no persisted run/job executions.

---

## Confidence Statement

This report is factual from:
- live SQL queries against the provided Railway DB connection,
- direct reads of all 4 Railway scraper entrypoints,
- direct reads of all 4 Railway scraper `railway.toml` files,
- direct comparison against script versions.

I did **not** infer successful production operation without DB evidence.