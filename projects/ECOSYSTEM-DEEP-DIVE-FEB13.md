# Roviq Ecosystem Integration Plan — Deep Dive Analysis

**Date:** February 13, 2026  
**Status:** Analysis Complete

---

## Executive Summary

This document provides a detailed analysis of the Roviq Ecosystem Integration Plan, cross-referenced against the actual codebase state. The plan outlines integration between four products: GLASS (live), Virtual Budtender (live at CH), Cue (MVP built), and Delivery (concept).

**Key Finding:** The plan is ambitious but the foundation is sound. However, given the directive "stop building, start selling," **Phase 1 should be dramatically reduced** to only the work needed to prove revenue quickly.

---

## 1. What's Still Needed vs. What's Already Done

### 1.1 GLASS API Routes — Cross-Reference

| Plan Endpoint | File in Plan | Actually Exists? | Notes |
|---------------|--------------|------------------|-------|
| `/api/v1/catalog/:operatorId/products` | `budtender-api.ts` | ❌ **NOT BUILT** | Needs new route file |
| `/api/v1/catalog/:operatorId/underperforming` | `budtender-api.ts` | ❌ **NOT BUILT** | Same as above |
| `/api/v1/ecosystem/events` | `ecosystem.ts` | ❌ **NOT BUILT** | Needs new route file |
| `/api/v1/budtender/sessions` | `budtender-api.ts` | ❌ **NOT BUILT** | Session logging |
| `/api/v1/budtender/queries` | `budtender-api.ts` | ❌ **NOT BUILT** | Query logging |
| `/api/v1/demand/:operatorId` | `demand.ts` | ❌ **NOT BUILT** | Demand signals |
| API key auth plugin | `api-key-auth.ts` | ❌ **NOT BUILT** | New plugin needed |

**Current GLASS routes that DO exist:**
- `products.ts` — Basic product CRUD (GET /products, GET /products/:id) with auth
- `prices.ts` — Price data
- `operators.ts` — Operator management
- `ccc.ts` — CCC data
- `recommendations.ts`, `scores.ts`, `dashboard.ts`, etc.

**Assessment:** The plan calls for 3 new route files and 1 new auth plugin. **None exist yet.** This is ~16 hours of new API work minimum.

---

### 1.2 GLASS Database Schema — Cross-Reference

| Plan Table | Actually Exists? | Notes |
|------------|------------------|-------|
| `operators` | ✅ Yes | 472+ records |
| `products` | ✅ Yes | 100K+ records |
| `prices` | ✅ Yes | 117K+ records |
| `sources` | ✅ Yes | |
| `scrape_runs`, `scrape_jobs` | ✅ Yes | |
| `threats`, `recommendations` | ✅ Yes | |
| `margin_rules`, `watchlists` | ✅ Yes | |
| `waitlist`, `alerts` | ✅ Yes | |
| CCC tables (6) | ✅ Yes | Full CCC data imported |
| `budtender_sessions` | ❌ **NOT BUILT** | Needs migration |
| `budtender_queries` | ❌ **NOT BUILT** | Needs migration |
| `demand_signals` | ❌ **NOT BUILT** | Needs migration |
| `ecosystem_events` | ❌ **NOT BUILT** | Needs migration |

**Assessment:** All GLASS core tables exist. **4 new integration tables need to be created** via migration. This is straightforward DDL work.

---

### 1.3 Virtual Budtender — Current State

**Current Architecture:**
- Products stored in **Firebase Firestore** (~300 CH products)
- Products imported via manual CSV upload (`npm run import-ch`)
- Data goes stale within days
- No live connection to GLASS

**Current Endpoints:**
- `GET /health` — Health check
- `GET /products` — Returns Firestore products
- `POST /recommend` — Product recommendations
- `POST /chat` — Chat interface

**Tenant Config:** Has `tenantId: "ch"` mapping but no `glassOperatorId` mapping exists.

**Assessment:** VB is currently **completely disconnected** from GLASS. The plan's Phase 1 correctly identifies this as the priority integration point. VB needs:
1. New `glassClient.js` module to call GLASS API
2. Replace Firestore calls with GLASS API calls
3. Add tenant mapping for CH → GLASS operator UUID

---

### 1.4 Cue — Current State

**Found:** The Cue repo at `/data/workspace-backup-20260209/projects/cue/` appears to be documentation-heavy. The plan states:
- MVP built
- Neon PostgreSQL
- Firebase Phone Auth
- Tables: users, brands, dispensaries, missions, submissions, rewards, redemptions, courses

**Missing:** I couldn't locate the active server source code in the available workspace. The backup shows README, legal docs, and branding — but the actual codebase wasn't found at expected paths.

**Assessment:** If the MVP is built, the plan identifies these as needing work:
- `participants` table (replaces `budtenders`)
- Driver mission types
- Delivery submissions table
- GLASS integration service
- Dual auth (Clerk + Firebase)

---

### 1.5 Integration Tables Status Summary

| Component | What's Done | What's Missing |
|-----------|-------------|----------------|
| GLASS API | 20+ routes | 3 new route files + API key auth |
| GLASS DB | 20+ tables | 4 integration tables |
| Virtual Budtender | Firestore + Express | GLASS API client |
| Cue | Documentation | Full MVP codebase + integration |

---

## 2. Priority Assessment

### Phase 1 Recommendation (THIS WEEK)

Given GLASS is the revenue priority and "stop building, start selling," Phase 1 should be **radically simplified**:

| Priority | Task | Hours | Rationale |
|----------|------|-------|-----------|
| **P0** | Build GLASS catalog endpoint (`/api/v1/catalog/:operatorId/products`) | 4h | **Enables VB → GLASS data flow** |
| **P0** | Add CH operator mapping to GLASS (find/create UUID) | 1h | Required for VB integration |
| **P0** | Add VB API key to GLASS env vars | 0.5h | Simple config |
| **P1** | VB backend: Replace Firestore with GLASS API call | 4h | Core integration |
| **P1** | Test VB with GLASS data | 2h | Manual QA |
| **P2** | Deploy GLASS API | 1h | Railway deploy |
| **P2** | Deploy VB backend | 1h | Existing process |

**Total Phase 1 (reduced): ~13.5 hours**

**What to SKIP in Phase 1:**
- API key auth plugin (can use simple header auth for now)
- Underperforming products endpoint (not needed for V1)
- Demand signals table (can log directly to existing tables initially)
- Any other integration tables until VB is proven

---

### What Can Wait (Phase 2+)

| Task | Wait Until | Why |
|------|------------|-----|
| Ecosystem events table | After VB integration proves valuable | Nice-to-have analytics |
| Demand signals aggregation | After getting query data | Build after we have data |
| Cue integration | After VB is live | Different product |
| Delivery integration | After Cue launches | Concept only |
| Auth plugin (formal) | When third-party integrations need it | Overhead for now |
| Firestore elimination | After GLASS data flow proven | Backup for now |

---

## 3. Architecture Validation

### Hub-and-Spoke Approach: ✅ SOUND

The plan correctly identifies **hub-and-spoke** (not monolith) as the right approach:

**Why it works:**
1. **Different deploy cadences:** GLASS runs on Railway, Cue will have its own hosting, VB is lightweight
2. **Different auth systems:** GLASS uses Clerk, Cue uses Firebase Phone Auth, VB is anonymous
3. **Different teams:** Each product can evolve independently
4. **API coupling is looser than DB coupling:** If Cue goes down, GLASS still works

### Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **API latency** | Medium | VB needs sub-500ms responses; GLASS must index properly |
| **Rate limiting** | Medium | Plan proposes 1000 req/min — need to validate GLASS can handle this |
| **Operator mapping errors** | High | CH's `tenantId: "ch"` must map to correct GLASS operator UUID; if wrong, VB shows wrong products |
| **Data freshness** | Medium | GLASS scrapes daily; VB currently stale. If GLASS scrapes fail, VB shows bad data |
| **No idempotency** | Low | Session/query logging should handle duplicates gracefully |

### Gaps in the Plan

1. **No fallback if GLASS API is down** — VB should cache last-known products
2. **No product mapping validation** — How do we know CH products in GLASS match Firestore products?
3. **No rate limiting implementation detail** — The plan mentions 1000 req/min but doesn't specify implementation
4. **No rollback plan** — If VB → GLASS integration fails, how do we revert to Firestore?

---

## 4. Cost/Effort Reality Check

### Hour Estimates: Mixed

| Phase | Plan Hours | Realistic? | Notes |
|-------|------------|------------|-------|
| Phase 1 | 14.5h | **~13.5h** ✅ | Close, but can trim API key plugin |
| Phase 2 | 55h | **~45-55h** ⚠️ | Depends on Cue codebase state; schema work is predictable |
| Phase 3 | 104h | **~80-90h** ⚠️ | Some tasks can run in parallel; some are over-estimated |
| Phase 4 | 600h | **Deferred** ❌ | Way out — not relevant now |

### Under-Estimated Tasks

| Task | Plan | Reality |
|------|------|---------|
| VB → GLASS integration | 4h | Likely 4-6h due to data mapping complexity |
| Cue → GLASS product sync | 4h | Could be 6-8h if product matching is tricky |
| Dual auth middleware | 12h | Could be 8h if straightforward |

### Over-Estimated Tasks

| Task | Plan | Reality |
|------|------|---------|
| VB config panel | 16h | Could be 8h if integrated into GLASS dashboard |
| Customer loyalty | 12h | Phase 4 deferred anyway |

### Bottom Line

**Total Phase 1-3: ~170 hours estimated**  
**Realistic: ~140-150 hours** (but most is Phase 3+)

Given "stop building, start selling," **we should only spend ~14 hours on Phase 1** to get VB → GLASS working. Everything else is premature.

---

## 5. Dependencies & Critical Path

### Critical Path (What Blocks What)

```
[Find CH operator ID in GLASS]
         ↓
[Build catalog API endpoint]
         ↓
[Add GLASS API key to VB env]
         ↓
[VB backend calls GLASS API]
         ↓
[Test & Deploy]
         ↓
✅ VB uses live GLASS data
```

**Any delay in Step 1 blocks everything else.**

### Secondary Dependencies

| This... | Blocks... |
|---------|-----------|
| VB → GLASS working | Demand signals (need query data first) |
| Cue deployed | Driver program |
| Demand signals exist | GLASS dashboard widget |
| GLASS + VB working | Cue → GLASS integration makes sense |

---

## 6. Revenue Impact

### Ranked by Revenue Impact

| Rank | Integration | Revenue Impact | Notes |
|------|-------------|----------------|-------|
| **1** | VB → GLASS | **HIGH** | Enables live product data; removes manual CSV work; proves integration works |
| **2** | GLASS → VB (catalog) | **HIGH** | Same as #1 from other direction |
| **3** | Cue → Driver incentives | **MEDIUM** | CH driver program can demonstrate ROI quickly |
| **4** | VB query logging | **MEDIUM** | Demand signals enable smarter missions |
| **5** | GLASS → Cue (product data) | **MEDIUM** | Enables mission targeting |
| **6** | Ecosystem analytics | **LOW** | Nice-to-have dashboard |
| **7** | Unified auth | **LOW** | Operational efficiency, not revenue |
| **8** | Delivery integration | **DEPENDS** | Only if Delivery partnership closes |

### Revenue-Enabling vs Nice-to-Have

**Revenue-Enabling (build now):**
- VB → GLASS integration (Phase 1)
- CH Driver program (Phase 2)

**Nice-to-Have (defer):**
- Full ecosystem analytics dashboard
- Unified Clerk auth
- Customer loyalty programs
- Delivery app

---

## 7. What to Kill or Defer

### Kill

| Item | Why Kill |
|------|----------|
| **Full Firestore elimination** | Keep as backup until GLASS integration is proven stable for 30+ days |
| **API key auth plugin (full)** | Use simple header auth for now; formal plugin is overhead |
| **Underperforming products endpoint** | Not needed for Phase 1; can build later when Cue is ready |
| **Demand aggregation cron job** | Don't build until we have query data to aggregate |

### Defer Until After First Revenue

| Item | Defer To | Why |
|------|----------|-----|
| GLASS "Demand Intelligence" widget | Post-revenue | Dashboard polish, not revenue blocker |
| GLASS "Ecosystem" tab | Post-revenue | Same |
| Cue → GLASS product sync | Post-revenue | Depends on Cue being deployed |
| VB config panel (Clerk) | Post-revenue | Can manage via env vars initially |
| Dual auth (Clerk + Firebase) | Post-revenue | Works fine as-is |
| Customer loyalty type | Post-revenue | Future expansion |
| Delivery app | Unknown | Concept only; depends on partnership |

### The "Stop Building, Start Selling" Test

Ask before any build: **"Does this directly enable or increase revenue in the next 30 days?"**

| Answer | Action |
|--------|--------|
| Yes | Build it |
| No (but enables future revenue) | Defer |
| No (nice-to-have) | Kill or backlog |

---

## 8. Specific Technical Findings

### CH Operator Mapping Issue

The plan mentions mapping `tenantId: "ch"` to a GLASS operator UUID but notes `glassOperatorId: null` in the config. **This must be resolved before Phase 1.**

**Action needed:**
```sql
-- Find CH in GLASS operators table
SELECT id, name, city, state FROM operators WHERE name ILIKE '%cannabis healing%' OR name ILIKE '%ch%';
```

If not found, may need to create operator manually or verify CH is scraped from Dutchie.

### VB → GLASS Data Mapping

The plan includes a detailed `mapGlassCategory()` function. Need to verify:
- GLASS categories: 'flower', 'pre-roll', 'vape', 'edible', etc.
- VB categories: 'flower', 'Pre-Rolls', 'Cartridge', 'Edibles', etc.

**Risk:** If categories don't match, products won't appear in VB.

### API Key Auth

The plan proposes `X-Roviq-API-Key` header. For Phase 1, I recommend using a simpler approach:
- Just check for a specific header with the key
- Don't build full plugin architecture yet

---

## 9. Recommendations Summary

### Do This Week (Phase 1 Only)

1. **Find CH's operator ID in GLASS DB** — 1 hour
2. **Build `/api/v1/catalog/:operatorId/products` endpoint** — 4 hours
3. **Add CH → GLASS operator mapping to VB** — 0.5 hours
4. **VB backend: Replace Firestore with GLASS API** — 4 hours
5. **Test & deploy** — 3 hours

**Total: ~12-14 hours**

### Don't Do Yet

- Any new integration tables (budtender_sessions, demand_signals, etc.)
- Ecosystem event endpoints
- Demand aggregation
- Cue integration
- Full API key auth plugin
- Firestore elimination
- Any dashboard widgets

### Success Criteria for Phase 1

- [ ] VB at CH shows products from GLASS (not Firestore)
- [ ] Products update automatically when GLASS scrapes run
- [ ] No manual CSV imports needed
- [ ] Can demonstrate live data flow to Randy

---

## Appendix: File Locations

| Component | Path |
|-----------|------|
| GLASS API routes | `/data/workspace/projects/glass/src/services/api/src/routes/` |
| GLASS DB schema | `/data/workspace/projects/glass/src/services/api/src/db/schema.ts` |
| GLASS plugins | `/data/workspace/projects/glass/src/services/api/src/plugins/` |
| Virtual Budtender backend | `/tmp/virtual-budtender/backend/server.js` |
| Virtual Budtender config | `/tmp/virtual-budtender/backend/tenantConfig.js` |
| Integration plan | `/data/.openclaw/media/inbound/59bb0605-3e1e-4de1-9e01-f8c5771757b6.txt` |

---

*Analysis completed: February 13, 2026*
