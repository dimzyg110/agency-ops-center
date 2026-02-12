# Newsletter Pipeline Fix Summary

**Date:** February 12, 2026  
**Scope:** P0 fixes from PIPELINE-AUDIT.md + GLASS integration  

---

## Changes Made

### 1. ✅ NEW: `scrapers/glass_data_processor.py`
- Connects to GLASS PostgreSQL database (Railway)
- Fetches **Price Wire** data: MA avg prices by category (flower, edible, vape, concentrate, preroll), biggest drops, biggest increases
- Fetches **Threat Radar** data: new operators detected this week, active threats (price wars, enforcement, new competitors)
- Fetches **Brand Movers** data: top brands by shelf presence across MA dispensary menus
- Fetches **Market Stats**: total operators, products, price observations
- Uses `thc_percent > 0` filter to exclude accessories (grinders, rolling papers, etc.) mis-categorized in product data
- Cleans product names (removes duplicated text, THC/TAC percentages, "Low stock" suffixes)
- Cleans operator names (converts slugs like `clear-sky-belchertown` to `Clear Sky Belchertown`)
- Outputs structured JSON matching data contract schema

### 2. ✅ FIXED: `scrapers/events_scraper.py`
**Problem:** Was returning news articles as events (49/54 had TBD dates). "Cannabis Cafes Are Legal In Massachusetts" is a news article, not an event.

**Fix:**
- Added `is_news_article()` filter that checks domain + title signals
- Added `is_likely_event()` that checks for event platforms (Eventbrite, Meetup) and event language (register, tickets, conference)
- **Rejects items without parseable future dates** — no more TBD dates
- **Rejects past events** — no more Jan 5 events in Feb newsletter
- Returns empty list if no real events found (better than fake events)
- Uses curated event-specific search queries

### 3. ✅ FIXED: `composer.py` — GLASS integration + new sections
- **Price Wire section** (new): Formats GLASS price data as category table + biggest drops/increases
- **Threat Radar section** (new): Shows new competitors detected, active threat alerts with severity emoji
- **Brand Movers section** (new): Top brands by shelf presence across MA
- **GLASS CTA in footer**: "Powered by GLASS — real-time price intelligence from 490+ MA dispensary menus"
- **Roviq branding in footer**: Replaced generic "The Margin Report Team" with "The Operator's Margin Report is published by Roviq — AI-powered intelligence for cannabis operators."
- **Removed Jake placeholder** — no more "— Jake" signature
- **Non-MA source penalty**: Added -60 score penalty for non-MA regional domains (rcbizjournal.com, etc.)
- **Dubious source penalty**: Added -100 score penalty for blocked sources (dontlegalizedrugs.com, etc.)
- Loads `glass_data.json` alongside existing data files

### 4. ✅ FIXED: `pipeline.py` — GLASS stage + quality gate
- Added `glass` stage (runs `scrapers/glass_data_processor.py` before `market`)
- Added `glass` to `OUTPUT_REQUIRED` set
- **Re-enabled quality gate**: `GATE_STAGES = {"validate"}` — validation errors now BLOCK composition
- Improved gate failure logging: shows error count, first 10 issues with ❌ emoji
- Clear message: "The pipeline will NOT produce a draft until these issues are resolved."

### 5. ✅ FIXED: `scrapers/news_scraper.py` — MA relevance filtering
- Added `BLOCKED_DOMAINS` list: dontlegalizedrugs.com, etc.
- Added `NON_MA_PUBLICATION_DOMAINS` list: rcbizjournal.com (Rockland County NY), etc.
- `is_junk()` now checks domain against blocked + non-MA lists
- Prevents non-MA regional news from appearing as top story

### 6. ✅ UPDATED: `data_contract.py` — GLASS schema
- Added `glass: "glass_data.json"` to `DATASET_FILES`
- Added `glass` to `STAGE_OUTPUT_FILES`
- Added `GLASS_SCHEMA` dict with expected keys for: price_wire, threat_radar, brand_movers, market_stats

### 7. ✅ UPDATED: `quality_checker.py` — new section aliases
- Added `price_wire`, `threat_radar`, `brand_movers` to section aliases for quality checks

### 8. ✅ GENERATED: `drafts/newsletter_2026-02-12_test.md`
- Test newsletter with full GLASS integration
- Price Wire leads with 24,000+ price observations across 5 categories
- Threat Radar shows 20 new dispensaries + 6 active alerts
- Brand Movers shows top 10 brands by shelf presence
- Proper Roviq branding in footer

---

## New Newsletter Structure

```
📊 PRICE WIRE          ← NEW (GLASS)
🔥 TOP STORY           ← EXISTING (improved)
📊 THE NUMBER          ← EXISTING
📈 MARKET PULSE        ← EXISTING
🔴 THREAT RADAR        ← NEW (GLASS)
🏷️ BRAND MOVERS        ← NEW (GLASS)
🌍 DEMOGRAPHIC SIGNAL  ← EXISTING
📋 LICENSE WATCH        ← EXISTING
🛠️ TOOL OF THE WEEK    ← EXISTING
📅 UPCOMING EVENTS     ← EXISTING (fixed)
⚡ QUICK HITS          ← EXISTING (improved)
💡 MARGIN TIP          ← EXISTING
📋 COMPLIANCE          ← EXISTING
📬 FOOTER              ← FIXED (Roviq branding)
```

## Data Flow

```
GLASS Database (Railway PostgreSQL)
    ├── prices (24K+ observations/week)
    ├── products (20K+ tracked)
    ├── operators (492 tracked)
    └── threats (6 active)
          │
          ▼
glass_data_processor.py
          │
          ▼
data/glass_data.json
          │
          ▼
composer.py ──→ Price Wire + Threat Radar + Brand Movers
          │
          ▼
drafts/newsletter_YYYY-MM-DD.md
```

## What's NOT Done Yet (P1/P2)
- [ ] Beehiiv API integration (no automated send)
- [ ] Cron scheduling (pipeline still manual)
- [ ] LP signup form fix (still `action="#"`)
- [ ] Data Spotlight rotating section
- [ ] CCC Watchlist section
- [ ] Border Patrol section
- [ ] HTML template update to match BRANDING.md colors
- [ ] Tools scraper auto-generate `why_ma_impact`
