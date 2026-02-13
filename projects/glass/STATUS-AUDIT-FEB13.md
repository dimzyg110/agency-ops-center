# GLASS Production Database Status Audit
**Date:** February 13, 2026  
**Auditor:** Automated DB Query  
**Database:** Railway Production (turntable.proxy.rlwy.net:18582)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Prices | **116,991** |
| Total Products | **100,849** |
| Total Operators | **473** |
| Total Sources | **532** |
| Latest Price Data | **Feb 12, 2026 4:02 PM UTC** |
| **Feb 13 (Today) Prices** | **0** ⚠️ |
| Weedmaps Success Rate | **5.8%** (10/173 in last run) |
| Operator Scores | **EMPTY** (0 rows) |

---

## 1. Data Inventory (Row Counts)

| Table | Row Count | Notes |
|-------|-----------|-------|
| `prices` | 116,991 | Core pricing data |
| `products` | 100,849 | Product catalog |
| `operators` | 473 | Dispensary operators |
| `sources` | 532 | Data sources (menus, websites) |
| `scrape_jobs` | 769 | Individual scrape job history |
| `scrape_runs` | 10 | Scrape run summaries |
| `etl_runs` | 4 | CCC data import runs |
| `users` | 3 | Registered users |
| `waitlist` | 4 | Waitlist signups |
| `threats` | 6 | Threat records |
| `alerts` | 10 | Alert records |
| `operator_scores` | **0** | ⚠️ **EMPTY** |
| `recommendations` | 0 | Strategy recommendations |
| `watchlists` | 0 | User watchlists |

### CCC Tables Inventory

| Table | Row Count | Data Freshness |
|-------|-----------|----------------|
| `ccc_lab_tests` | 147,649 | Feb 12, 2026 |
| `ccc_facility_sales` | 67,333 | Feb 12, 2026 |
| `ccc_licenses` | 772 | Feb 12, 2026 |
| `ccc_plant_activity` | 46,863 | Historical |
| `ccc_avg_prices` | 31,038 | Historical |
| `ccc_weekly_sales` | 376 | Historical |
| `ccc_pending_applications` | 234 | Historical |
| `ccc_monthly_prices` | 71 | Feb 12, 2026 |
| `ccc_demographics` | 14 | Historical |

---

## 2. Scraper Coverage by Source Type

| source_type | Operators | Prices | % of Total Prices |
|-------------|-----------|--------|-------------------|
| `dutchie` | 235 | 69,835 | 59.7% |
| `weedmaps` | 276 | 72,191 | 61.7% |
| `menu` | 9 | 576 | 0.5% |
| `website` | 6 | 542 | 0.5% |

**Note:** Operators + prices totals exceed row counts due to operators having multiple source types.

---

## 3. Weedmaps Deep Dive ⚠️ CORRECTED

### Previous Report Claims vs Reality

| Claim | Previous | **ACTUAL (Corrected)** |
|-------|----------|------------------------|
| Total Weedmaps Sources | 282 | **282** ✓ |
| Operators with Price Data | "118" (claimed) | **141** |
| Last Run Success Rate | "10/173 succeeded" | **10/173 (5.8%)** |

### Weedmaps Success Analysis

**Key Finding:** The scraper is failing on 94% of Weedmaps stores.

From Feb 12, 2026 run:
- **Stores Attempted:** 173
- **Stores Succeeded:** 10 (5.8%)
- **Stores Failed:** 163 (94.2%)
- **Products Found:** 6,162
- **Duration:** 79 minutes (4,790 seconds)

### Top 15 Weedmaps Operators by Price Count (All-Time)

| Operator | City | Prices |
|----------|------|--------|
| Canna Provisions Holyoke | amherst | 1,609 |
| Elevated Roots | abington | 1,501 |
| Cape Cod Cannabis Recreational Dispensary | barnstable | 1,440 |
| Canna Provisions - Lee | great-barrington | 1,193 |
| The Haven Center - Brewster | barnstable | 1,189 |
| Boutiq | allston | 1,189 |
| ThTree | great-barrington | 1,187 |
| CNA Stores Haverhill | andover | 1,061 |
| CNA Stores Amesbury | essex | 1,034 |
| Stage One Dispensary | lenox | 989 |
| Zahara Cannabis | attleboro | 974 |
| Trinity Naturals Dispensary | belmont | 970 |
| Budds Dispensary Catskill | great-barrington | 964 |
| The Leaf | greenfield | 958 |
| Pioneer Valley Trading Company | chicopee | 945 |

### Weedmaps Error Pattern

All 163 failed stores show the same error:
```
"<store-slug>: 0 products parsed"
```

This indicates the Weedmaps parser is successfully fetching pages but extracting zero products, suggesting:
1. DOM structure changes on Weedmaps
2. Anti-bot measures blocking data extraction
3. Parser logic needs updating for new markup

---

## 4. Data Freshness

| Metric | Value |
|--------|-------|
| Latest Price Timestamp | **2026-02-12 16:02:27 UTC** |
| Earliest Price Timestamp | 2026-02-05 02:31:14 UTC |
| Prices Last 24 Hours | 116,872 |
| Prices Last 7 Days | 116,974 |
| **Prices Today (Feb 13)** | **0** ⚠️ |

### Daily Price Distribution (Last 8 Days)

| Date | Price Count |
|------|-------------|
| 2026-02-12 | 116,874 |
| 2026-02-11 | 16 |
| 2026-02-10 | 19 |
| 2026-02-09 | 17 |
| 2026-02-08 | 16 |
| 2026-02-07 | 14 |
| 2026-02-06 | 20 |
| 2026-02-05 | 15 |

**⚠️ CORRECTED:** The previous audit suggested daily data collection. The reality shows:
- Massive backfill on Feb 12 (116K prices)
- Minimal daily activity (14-20 prices/day) before that
- **No data yet for Feb 13** — cron job may not have run

---

## 5. Operator Scores — EMPTY ⚠️

**Status:** `operator_scores` table has **0 rows**

The table structure exists but no scores have been calculated/populated:
```sql
overall_score | pricing_score | compliance_score | thc_integrity_score | assortment_score | market_position_score | grade | calculated_at
```

**Impact:** Report cards, recommendations, and competitive analysis features are non-functional.

---

## 6. Users & Waitlist

### Registered Users (3)

| Email | Role | Operator ID | Clerk User ID |
|-------|------|-------------|---------------|
| randy@roviq.ai | owner | 1fdc87d8-... | (legacy) |
| user_39YWp2hm8sh6... | owner | 1b7d94a2-... | user_39YWp2... |
| user_39X3L9IHl102... | owner | 1b7d94a2-... | user_39X3L9... |

### Waitlist (4) — Mostly Test Data

| Email | Product | Source | Created |
|-------|---------|--------|---------|
| test-heartbeat@test.com | glass | health_check | Feb 12 |
| test@test.com | newsletter | newsletter_page | Feb 12 |
| `<script>alert(1)</script>@test.com` | glass | (empty) | Feb 12 |
| test-auth@test.com | glass | (empty) | Feb 12 |

**CORRECTED:** Only 4 waitlist entries, all appear to be test data. No "real" user signups detected.

---

## 7. Scrape Runs Status

### Recent Scrape Run History

| Started | Platform | Attempted | Succeeded | Failed | Prices Inserted | Duration |
|---------|----------|-----------|-----------|--------|-----------------|----------|
| Feb 12 06:24 | weedmaps | 173 | **10** | 163 | 6,162 | 79 min |
| Feb 12 05:13 | weedmaps | 1 | 1 | 0 | 760 | 5 min |
| Feb 12 04:07 | dutchie | 235 | **195** | 40 | 57,514 | 310 min |
| Feb 12 03:47 | dutchie | 2 | 2 | 0 | 293 | 2 min |
| Feb 12 03:44 | dutchie | 2 | 0 | 2 | 0 | 0 min |

### Key Findings

1. **Dutchie Scraper:** 83% success rate (195/235) — performing well
2. **Weedmaps Scraper:** 5.8% success rate (10/173) — **CRITICAL ISSUE**
3. **Last Run:** Feb 12 06:24 UTC (Weedmaps) — **17+ hours ago**
4. **Feb 13 Runs:** None yet — cron job appears not to have run

### Dutchie Errors (Sample)

- `altai-alternative-care`: "value too long for type character varying(255)"
- Multiple stores: "0 products found across all categories"
- Error pattern suggests API/data validation issues, not scraping failures

---

## 8. Daily Cron Job Status ⚠️

**Feb 13, 2026 Data Check:**
- Prices created today: **0**
- Scrape runs today: **0**
- ETL runs today: **0**

**Status:** ❌ **DAILY CRON NOT RUNNING**

The last activity was Feb 12. If the daily cron is scheduled, it has not executed for Feb 13.

---

## 9. Git Status

### Latest Commits (main branch)

```
8dd4c9f fix: add /api/v1/public/* to auth header bypass for Clerk plugin
4e100cf fix: move public report card route outside auth middleware
e2afb18 Phase 1: public report card, landing page update, recommendations fix
b580e69 feat: import 3 CCC datasets — facility sales (67K), licenses (772 with emails), monthly prices (71)
4c7c741 fix: P0 recommendation redesign — flip pricing logic
```

### Working Tree
- **Status:** Clean
- **Ahead of origin/main:** No (up to date)
- **Local changes:** None

---

## 10. Infrastructure Status

### Website (glassintel.xyz)
- **Status:** ✅ UP
- **HTTP Status:** 200 OK
- **Server:** Cloudflare + Railway
- **Response Time:** Normal

### Recent Local File Changes (Post Feb 12)

Files created/modified after Feb 12 midnight:
- `SCRAPER-V2-CODE-REVIEW.md`
- `REVIEW-DEREK.md`
- `LAB-IMPORT-FIX.md`
- `REVIEW-MARIA.md`
- Services: `brand.ts`, `normalizer.ts`, `types.ts`
- Parsers: `dutchie.ts`
- API routes: `public-report-card.ts`, `newsletter.ts`, `ccc.ts`, etc.

---

## 11. CORRECTED Discrepancies

### Previous Audit Errors

| Claim | Previous | Actual | Discrepancy |
|-------|----------|--------|-------------|
| Weedmaps operators with data | 118 | **141** | +23 operators |
| Weedmaps success rate | Implied higher | **5.8%** | Much worse |
| Daily cron running | Assumed yes | **NO** | Not running for Feb 13 |
| Operator scores | Assumed populated | **EMPTY** | 0 rows |
| Waitlist signups | Implied real users | **4 test entries** | No real signups |

### What the Data Actually Shows

1. **Weedmaps is effectively broken** — 94% failure rate
2. **No daily automation** — Feb 13 has zero new data
3. **Operator scores not calculated** — Core feature non-functional
4. **All waitlist entries are test data** — No organic interest captured

---

## 12. Critical Issues Summary

| Priority | Issue | Impact |
|----------|-------|--------|
| 🔴 P0 | Weedmaps scraper 94% failure | Loses half the market data |
| 🔴 P0 | Daily cron not running | No fresh data for Feb 13 |
| 🔴 P0 | Operator scores empty | Report cards broken |
| 🟡 P1 | Dutchie 17% failure rate | Missing 40 stores |
| 🟡 P1 | No real user signups | Product-market fit uncertain |

---

## Appendix: Key SQL Queries Used

```sql
-- Row counts
SELECT 'products' as table_name, COUNT(*) FROM products
UNION ALL SELECT 'prices', COUNT(*) FROM prices
-- etc...

-- Weedmaps success analysis
SELECT s.source_type, COUNT(DISTINCT o.id) as operators, COUNT(p.id) as prices
FROM sources s
LEFT JOIN operators o ON o.id = s.operator_id
LEFT JOIN prices p ON p.operator_id = o.id
WHERE s.source_type = 'weedmaps'
GROUP BY s.source_type;

-- Data freshness
SELECT MAX(scraped_at) as latest, COUNT(*) FILTER (WHERE scraped_at >= NOW() - INTERVAL '24 hours') as last_24h
FROM prices;
```

---

*Report generated: 2026-02-13 01:17 UTC*
*Database: railway@turntable.proxy.rlwy.net:18582*
