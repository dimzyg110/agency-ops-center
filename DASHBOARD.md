# Dashboard

**Last updated:** 2026-02-15 (10:00 PM UTC)

---

## Active Build: GLASS

**Status:** Live at glassintel.xyz — Phases 0-5 on branches, production-hardened
**Repo:** `github.com/Roviq-AI/glass` (private)
**Deploy:** Railway (glass-api + glass-web)

### Phase Status

| Phase | What | Status |
|-------|------|--------|
| 0 | Contracts, CI, ownership | ✅ Done |
| 1 | Backend skeleton, DB schema, frontend shell, auth | ✅ Done |
| 2 | Scraping core (Firecrawl, Playwright, BullMQ) | ✅ Merged — 100,849 products |
| 3 | Price Wire + Morning Brief | 🔄 Ready to merge (branches `codex/phase3-pricewire` + `kimi/phase3-morning-brief`) |
| 4 | Threat Radar intelligence (CCC ingest, scoring) | ✅ Merged (PR #9) |
| 5 | Margin Engine v1 | 🔄 Ready to merge (branch `opus/phase5-margin-engine`) |
| 6 | Pilot + hardening | ⬜ Next |

### Wartime Sprint (Feb 14-15) — ALL PHASES COMPLETE ✅
| Phase | PR | Result |
|-------|-----|--------|
| 0 Quarantine | #45 | brand_dict quarantined, 5 new tables |
| 1 Brand Authority | #46 | 308 verified brands (3+ platforms) |
| 2 LLM Parser | — | 36,556 products, Gemini 2.5 Flash |
| 3 GPID Lock | #48 | 174 verified GPIDs |
| 4 Consumer API | #47 | Search + detail + brands endpoints |
| Review Fixes | #49 | All feedback addressed |

**Runtime Hardening (Feb 15):**
- PR #86: Railway-only DB + Vertex-only Gemini guardrails
- PR #87: product-page store rows clickable/new-tab
- PR #88: GPID schema drift hardening
- PR #89: Dutchie import integration audit
- PR #90: `/brands` prerender 503 mitigation
- PR #91: store clickthrough URL fallback
- PR #92: Railway hostname allowlist
- PR #93: Vertex parser payload role fix
- PR #94: `$0` display artifact fix

**Production Fixes Applied:**
- `verified_gpids.short_code` column + index added
- Consumer API recovered from `CONSUMER_VIEW_UNAVAILABLE`
- Image coverage fix ready (branch `feature/image-representative-jane-gap`)

### GLASS Data Assets

| Dataset | Rows | Status |
|---------|------|--------|
| Products scraped (Dutchie + Weedmaps) | 100,849 | ✅ In DB |
| Price observations | 117,017 | ✅ |
| Parsed products | 8,877 | ✅ Growing |
| Verified GPIDs | 5,293 | ✅ Growing |
| CCC lab tests (THC/THCA%) | 298,343 | ⏳ Import running |
| CCC facility sales | 67,334 | ⏳ Queued |
| CCC licensed operators | 773 | ✅ With emails |
| CCC county market data | 1,754 | ✅ |
| Operators geocoded | 490/492 | ✅ |

### GLASS Live Features
- Store Report Card (green/yellow/red pricing comparison)
- 4-step onboarding (60 seconds to value)
- Flywheel/waitlist system
- Admin dashboard with data quality score
- GA4 tracking
- Clerk auth + security hardening
- Beehiiv newsletter + Resend auto-invite

### GLASS Known Issues
- [ ] Daily scraping stability (Dutchie: 195/235, Weedmaps: 10/173)
- [ ] Brand parsing garbage ("stock. Order soon." as brand)
- [ ] 298K lab test import — verify completion
- [ ] Image coverage: branch ready, prioritizes Jane images
- [ ] Parser 429 RESOURCE_EXHAUSTED fallback to OpenRouter Kimi

### GLASS Revenue Path
**"7 days stable scraping + 1 data quality fix + 1 good email = first paying customer"**
- Cue at $199/mo, 99.7% margin
- Target: 3-5 paid in 30 days, $5-7K MRR by 90 days

---

## Revenue Pipeline

### AC Toll Processing (Immediate)
- 86 personalized outreach emails ready
- Sample sent to Randy via Gmail — **waiting on approval to blast**
- Page live: `advancedcultivatorsllc.com/toll-processing` (pw: `ac2026`)

### Delivered Partnership (On Hold)
- Proposal V2 delivered, PDF ready
- **Waiting on Randy to schedule second meeting with founders**
- License MD1303 expires 3/5/2026 (~22 days)

### Cue (Blocked)
- Legal doc sent to AC legal team — **waiting on their approval**

---

## Client Work

### AC (Advanced Cultivators)
- [ ] Weekly social content
- [ ] YouTube channel strategy
- [ ] Toll processing outreach (waiting approval)

### CH (Cannabis Healing)
- [ ] Weekly social graphics
- [ ] Get Google Analytics export from Brian
- [ ] SEO keyword strategy (blocked: needs analytics)

### HOP (House of Pride)
- [ ] GTM strategy doc
- [ ] Website copy
- [ ] Labels + photos (blocked: needs Randy)

---

## Leads

### Decoded Shop
- Proposal delivered, demo live
- **Waiting on Randy's feedback / client meeting**

### Delivered Inc
- Proposal V2 delivered
- **Waiting on second founder meeting**

---

## Roviq Infrastructure

| Asset | Status |
|-------|--------|
| Website (roviqai.xyz) | V3 deployed, WebGL effects, GA live |
| Newsletter | Needs content + template overhaul |
| Cloudflare Pages | Build succeeds, deploy issue, nameservers pending |
| Resend email | `spacemanwins.win` verified, `roviqai.xyz` NOT verified |
| SEEDANCE (video gen) | API fallback working via FAL.ai |

---

## Blockers (Need Randy)

- [ ] Approve toll processing email blast
- [ ] Schedule Delivered second meeting (license expires 3/5)
- [ ] Cloudflare nameserver setup
- [ ] CH: Google Analytics export from Brian
- [ ] HOP: Labels finalized + photos
- [ ] Add `roviqai.xyz` to Resend
