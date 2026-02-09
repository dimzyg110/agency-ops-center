# Revenue Discovery System v1

## Overview
24/7 automated system to find revenue opportunities in Boston (40mi) + remote, auto-qualify, and auto-outreach via email (Resend) + voice agents.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          REVENUE DISCOVERY ENGINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       │
│  │   DISCOVERY      │    │   QUALIFICATION  │    │    OUTREACH      │       │
│  │     LAYER        │───▶│      LAYER       │───▶│     LAYER        │       │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘       │
│         │                        │                       │                   │
│         ▼                        ▼                       ▼                   │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                         DATA STORE                                │       │
│  │  opportunities.db  │  contacts.db  │  outreach_log.db            │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Wins — DO TODAY

1. **Craigslist RSS** (zero code):
   - `https://boston.craigslist.org/search/gig?format=rss`
   - `https://boston.craigslist.org/search/lbg?format=rss`

2. **Register Thumbtack Pro** — leads come to you

3. **Register SAM.gov** — takes 24-48h to activate

4. **Verify roviqai.xyz in Resend** — enable outreach

---

## Channels Ranked by Speed-to-Revenue

### < 7 Days to Cash
| Channel | Revenue/Mo | Action |
|---------|------------|--------|
| Contractor marketing offer | $8-40K | Sell setup fees to GCs |
| Freelance (Upwork/Thumbtack) | $3-20K | Post productized gigs |
| Service arbitrage (cleaning/hauling) | $5-30K | Line up 3 sub crews |

### < 30 Days to Cash
| Channel | Revenue/Mo | Action |
|---------|------------|--------|
| Construction subcontracting | $20-200K | Prequal with GCs (COMPASS/Highwire) |
| Government (small procurements) | $10-100K | Boston Supplier Portal + COMMBUYS |

---

## Cron Schedule

| Job | Frequency | Description |
|-----|-----------|-------------|
| `craigslist_scrape` | Every 15 min | Boston gigs/labor |
| `upwork_scan` | Every 30 min | Construction/marketing jobs |
| `sam_gov_check` | 3x daily | Federal contracts |
| `commbuys_check` | Daily 7am | MA state bids |
| `score_queue` | Every 10 min | Score new opps |
| `email_outreach` | 9am/1pm/5pm | Send email batches |
| `voice_queue` | Every 30min 9-5 | Process call queue |

---

## Scoring Engine

| Score | Tier | Action | Response Time |
|-------|------|--------|---------------|
| 80-100 | 🔥 HOT | Voice call + manual | <1 hour |
| 50-79 | 🟡 WARM | Priority email | <4 hours |
| 25-49 | 🔵 COLD | Batch email | <24 hours |
| 0-24 | ⚪ SKIP | Log only | — |

---

## Phase 1 — Week 1

### Day 1-2: Foundation (8h)
- Project structure + SQLite
- Scoring engine
- Resend integration

### Day 2-3: Scrapers (10h)
- Craigslist Boston
- Upwork API

### Day 3-4: Outreach (8h)
- Email templates
- Sequence logic

### Day 5-6: Voice (6h)
- Voice agent integration
- Call scripts

### Day 7: Deploy (4h)
- Cron jobs
- Testing

---

## Key Registration Links (Boston/MA)

- **City of Boston Supplier Portal:** https://procurement.boston.gov/
- **MA COMMBUYS:** https://www.commbuys.com/bso/
- **Massport Bids:** https://www.massport.com/business/bids-and-opportunities
- **SAM.gov:** https://sam.gov/
- **MA SDO Certification:** https://www.mass.gov/certification-program-for-sdo

---

## GC Prequal Platforms

| GC | Platform | Notes |
|----|----------|-------|
| Gilbane | COMPASS (Bespoke) | Financials, EMR, OSHA logs |
| BOND | Highwire | Safety manual, subscription fee |
| DPR | Direct portal | W-9, insurance, bonding |

---

## Week 1 Targets

| Metric | Target |
|--------|--------|
| Opportunities discovered | 500 |
| Qualified leads | 50 |
| Outreach sent | 100 |
| Response rate | 5% |
| Deals closed | 3 |
| Revenue | $5K |

---

## Files Created
- `/data/workspace/projects/revenue-engine/SYSTEM-SPEC.md` (this file)
- `/data/workspace/outreach_templates.md` (15 email templates + 3 voice scripts)
