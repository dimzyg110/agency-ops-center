# Lead Tool Roadmap

*Updated: 2026-02-04*

## Phase 1: Core Intelligence (COMPLETE ✅)

| Task | Status | File |
|------|--------|------|
| Signals Pack Export (Top 150) | ✅ Done | `signals_pack_export.py` |
| Margin Pressure Snapshot Generator | ✅ Done | `snapshot_generator.py` |
| Clean Contacts Merge | ✅ Done | `contact_merge.py` |
| Distress Lead Scoring v1 | ✅ Done | `unified_intel.py` |
| Change Log Snapshot | ✅ Done | `change_log.py` |

**PR:** https://github.com/randytorres/ops-center/compare/main...feat/lead-tool-phase1

---

## Phase 2: Intel Pack Upgrade - Scrapers (NEW)

Transform from "CCC list" to "Commercial Intelligence Engine"

| Task | Priority | Effort | Value | Status |
|------|----------|--------|-------|--------|
| **Google Places Verification** | P0 | Easy | Critical | ⬜ Todo |
| - Verify open/closed status | | | | |
| - Fetch review count + rating | | | | |
| - Track review velocity weekly | | | | |
| **Menu Scraper (Dutchie/Jane)** | P0 | Medium | Game-changer | ⬜ Todo |
| - Detect POS/menu platform | | | | |
| - Count SKUs per category | | | | |
| - Menu Gap Analysis ("stores with <3 beverages") | | | | |
| **Discount Tracker** | P1 | Medium | High | ⬜ Todo |
| - % of menu on markdown | | | | |
| - "Desperation Index" scoring | | | | |
| **Job Posting Monitor** | P1 | Easy | Medium | ⬜ Todo |
| - Indeed/LinkedIn scraper | | | | |
| - Hiring = growth signal | | | | |
| - "Inventory Manager" = new buyer incoming | | | | |
| **Tech Stack Fingerprint** | P2 | Easy | Medium | ⬜ Todo |
| - Detect POS (Dutchie/Jane/Blaze/Flowhub) | | | | |
| - Detect marketing tools (Springbig, etc) | | | | |

---

## Phase 3: Intel Pack Upgrade - Enrichment

| Task | Priority | Effort | Value | Status |
|------|----------|--------|-------|--------|
| **Decision Maker Lookup** | P0 | Hard | Game-changer | ⬜ Todo |
| - LinkedIn scrape for GM/Buyer names | | | | |
| - Email pattern matching | | | | |
| - Build "Buyer Rolodex" | | | | |
| **MSO/Corporate Mapping** | P1 | Medium | High | ⬜ Todo |
| - Identify parent companies | | | | |
| - Flag chains vs independents | | | | |
| **Competitive Density Score** | P2 | Easy | Medium | ⬜ Todo |
| - Count dispensaries in 1/3/5 mile radius | | | | |
| - Saturation mapping | | | | |
| **Social Aliveness Check** | P3 | Easy | Low | ⬜ Todo |
| - Last Instagram/Facebook post date | | | | |
| - >30 days = struggling | | | | |

---

## Phase 4: Delivery & Automation

| Task | Priority | Effort | Value | Status |
|------|----------|--------|-------|--------|
| **Airtable/Softr Portal** | P1 | Medium | High | ⬜ Todo |
| - Filterable web interface | | | | |
| - "Show me stores with X gap" | | | | |
| **Weekly Delta Reports** | P1 | Easy | High | ⬜ Todo |
| - What changed this week | | | | |
| - New licenses, status changes | | | | |
| - Review velocity changes | | | | |
| **Automated Refresh Pipeline** | P2 | Medium | High | ⬜ Todo |
| - Cron jobs for all scrapers | | | | |
| - Data freshness guarantees | | | | |

---

## Implementation Timeline

**Week 1-2: Phase 2 (Scrapers)**
- Google Places agent
- Menu scraper MVP (count by category)
- Job posting monitor

**Week 3: Phase 3 (Enrichment)**
- LinkedIn/decision maker lookup
- MSO mapping
- Tech stack detection

**Week 4: Phase 4 (Delivery)**
- Airtable interface
- Weekly automation
- Customer onboarding flow

---

## Value Proposition Evolution

| Version | What It Is | Price |
|---------|-----------|-------|
| v1 (Current) | Cleaned CCC list | $2,500 |
| v2 (Phase 2) | + Live status, menu gaps, review velocity | $3,500 |
| v3 (Phase 3) | + Decision maker contacts, MSO mapping | $5,000 |
| Enterprise | + Custom filters, API access, white-label | $10,000+ |

---

## Notes

- **Menu Gap Analysis is the killer feature** - lets vendors filter by "who needs my product category"
- Review velocity is easy win, high signal
- Decision maker lookup is hardest but most valuable
- Consider partnering with data enrichment provider (Clay, Proxycurl) vs building
