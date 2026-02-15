# Scraper Infrastructure Gaps & Action Plan

## Current State Analysis (2026-02-15)

### Success Rates (Last 7 Days)

| Platform | Run Success | Store Success | Issue |
|----------|-------------|----------------|-------|
| Dutchie | 50% (17/34) | 39% (634/1631) | Browser crashes |
| Jane | 60% (12/20) | 61% (171/280) | Moderate |
| Leafly | 43% (6/14) | 25% (225/890) | Low extraction |
| Weedmaps | 90% (9/10) | 15% (223/1462) | Very low extraction |

### Data in Database

- **319,929** total price records
- **1,103** configured sources
- **5,528** scrape jobs tracked

---

## Identified Gaps

### 1. Critical: High Failure Rates

**Problem:** All scrapers have significant failure rates, with store-level success rates as low as 15% (Weedmaps).

**Root causes identified:**
- Dutchie: Browser context closing mid-run (memory or timeout issues)
- Leafly: Not extracting products despite running
- Weedmaps: Very low extraction rate (only 15% of stores)
- Jane: Working best but still 40% failure

### 2. Critical: No Monitoring/Alerting

**Problem:** No automated alerts when scrapers fail.

**Impact:** Failures go unnoticed until manually checked.

### 3. High: No Automatic Retries

**Problem:** Failed stores are not retried automatically.

**Impact:** One failed store stays failed until next day.

### 4. High: No Visibility Into Store-Level Issues

**Problem:** Can't easily see which specific stores are failing and why.

**Impact:** Hard to diagnose platform-wide changes.

### 5. Medium: No Dead Store Detection

**Problem:** Slugs files may contain stores that no longer exist.

**Impact:** Wasted scrape time on closed stores.

### 6. Medium: No Data Quality Metrics

**Problem:** No automated checks for data freshness, completeness.

**Impact:** Don't know if data is actually good.

### 7. Low: No Local Dev Testing

**Problem:** Can't easily test changes locally before deploying.

**Impact:** Risk of breaking production.

---

## Action Plan

### Phase 1: Stabilization (Week 1)

**Goal:** Get scrapers to 80%+ store success rate

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| P0 | Fix Dutchie browser crash issue | Dev | Not started |
| P0 | Investigate Leafly/Weedmaps low extraction | Dev | Not started |
| P1 | Add retry logic for failed stores (3 retries) | Dev | Not started |
| P1 | Add Discord/Slack alerts for failures | Dev | Not started |

### Phase 2: Observability (Week 2)

**Goal:** Know immediately when things break

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| P1 | Set up uptime monitoring for Railway services | DevOps | Not started |
| P1 | Add daily status report to Discord | Dev | Not started |
| P2 | Create Grafana dashboard for scraper metrics | DevOps | Not started |

### Phase 3: Reliability (Week 3)

**Goal:** Self-healing scrapers

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| P2 | Auto-retry failed stores within same run | Dev | Not started |
| P2 | Add health checks between store batches | Dev | Not started |
| P2 | Implement circuit breaker for problematic stores | Dev | Not started |

### Phase 4: Data Quality (Week 4)

**Goal:** Trust the data

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| P2 | Add freshness checks (alert if >24h no data) | Dev | Not started |
| P2 | Detect and flag dead stores | Dev | Not started |
| P3 | Add completeness metrics (% of expected prices) | Dev | Not started |

---

## Minimum Viable Setup (MVP)

For immediate improvement, implement:

1. **Alerts** - Discord webhook on failure (2 hours)
2. **Retries** - 3 retries per store with exponential backoff  
3. **Dead store detection** - Remove stores with 5+ consecutive failures
4. **Dashboard** - Simple status page showing last run success/failure

---

## Ideal Setup (Target)

| Component | Description |
|-----------|-------------|
| **Orchestrator** | Central service that coordinates all scrapers, handles retries |
| **Queue** | Redis-backed job queue for store-level parallel processing |
| **Monitoring** | Grafana + Prometheus for metrics |
| **Alerting** | PagerDuty/Slack for failures |
| **Health API** | Endpoint that reports scraper health status |
| **Backfill** | Ability to re-scrape specific stores/dates |

---

## Next Steps

1. **Assign owner** for each Phase 1 task
2. **Schedule** daily standup to review scraper health
3. **Create** Railway project for scraper improvements
4. **Deploy** fix for Dutchie browser crash first (highest impact)

---

## Resources

- **Database:** `postgresql://postgres:***@turntable.proxy.rlwy.net:18582/railway`
- **Railway Project:** GLASS
- **Docs:** `/data/workspace/projects/glass/docs/SCRAPER-*.md`
