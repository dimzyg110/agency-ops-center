# Dashboard

**Last updated:** 2026-02-12 (8:55 PM UTC)

---

## Active Build: GLASS

**Status:** Live at glassintel.xyz — Phases 0-4 on main, Phases 3+5 on branches ready to merge
**Repo:** `github.com/Roviq-AI/glass` (private)
**Deploy:** Railway (glass-api + glass-web)

### Phase Status

| Phase | What | Status |
|-------|------|--------|
| 0 | Contracts, CI, ownership | ✅ Done |
| 1 | Backend skeleton, DB schema, frontend shell, auth | ✅ Done + Phase 1 CCC tables/scores deploying |
| 2 | Scraping core (Firecrawl, Playwright, BullMQ) | ✅ Merged — 100,849 products from 517 dispensaries |
| 4 | Threat Radar intelligence (CCC ingest, scoring) | ✅ Merged (PR #9) |
| 3 | Price Wire + Morning Brief | 🔄 Built on branches (`codex/phase3-pricewire` + `kimi/phase3-morning-brief`) — reviewed, ready to merge |
| 5 | Margin Engine v1 | 🔄 Built on branch (`opus/phase5-margin-engine`) — reviewed, ready to merge |
| 6 | Pilot + hardening | ⬜ Next — need 7 days stable scraping |

### GLASS Data Assets

| Dataset | Rows | Status |
|---------|------|--------|
| Products scraped (Dutchie + Weedmaps) | 100,849 | ✅ In DB |
| Price observations | 117,017 | ✅ First full MA snapshot |
| CCC lab tests (THC/THCA%) | 298,343 | ⏳ Import running |
| CCC facility sales | 67,334 | ⏳ Queued |
| CCC licensed operators (with emails!) | 773 | ✅ Downloaded |
| CCC county market data | 1,754 | ✅ Downloaded |
| Operators geocoded | 490/492 | ✅ |

### GLASS Live Features
- Store Report Card (green/yellow/red pricing comparison)
- 4-step onboarding (60 seconds to value)
- Flywheel/waitlist system
- Admin dashboard with data quality score
- GA4 tracking
- Clerk auth + security hardening (all data endpoints locked)
- Beehiiv newsletter + Resend auto-invite wired

### GLASS Known Issues
- [ ] Daily scraping not stable (Dutchie: 195/235, Weedmaps: 10/173)
- [ ] Brand parsing garbage ("stock. Order soon." as brand name)
- [ ] Fake sparklines in UI — need honest empty states
- [ ] 298K lab test import — verify completion
- [ ] services/scrape: 2 TS errors (string | undefined)
- [ ] services/intelligence: missing @types/node
- [ ] apps/web: Vite build broken (package resolution)
- [ ] 55 commits ahead of origin (unpushed)
- [ ] Codex 5.3 CLI not available in sandbox

### GLASS Revenue Path
**"7 days stable scraping + 1 data quality fix + 1 good email = first paying customer"**
- Cue at $199/mo, 99.7% margin
- Target: 3-5 paid in 30 days, $5-7K MRR by 90 days

---

## Revenue Pipeline

### AC Toll Processing (Immediate)
- 86 personalized outreach emails ready (`clients/ac/toll-processing/outreach-emails-v2.md`)
- Sample sent to Randy via Gmail — **waiting on approval to blast**
- Page live: `advancedcultivatorsllc.com/toll-processing` (pw: `ac2026`)

### Delivered Partnership (On Hold)
- Proposal V2 delivered, PDF ready
- **Waiting on Randy to schedule second meeting with founders**
- License MD1303 expires 3/5/2026 (~22 days) — already past 90-day renewal deadline

### Cue (Blocked)
- Legal doc sent to AC legal team — **waiting on their approval**

---

## Client Work

### AC (Advanced Cultivators)
- [ ] Weekly social content
- [ ] YouTube channel strategy
- [ ] Toll processing outreach (see above)

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
- Proposal delivered, demo live at `roviq-ai.github.io/decoded-demo/`
- **Waiting on Randy's feedback / client meeting**

### Delivered Inc
- Proposal V2 delivered
- **Waiting on second founder meeting**

---

## Roviq Infrastructure

| Asset | Status |
|-------|--------|
| Website (roviqai.xyz) | V3 deployed (white/editorial), WebGL effects, GA live |
| Newsletter | V1 rejected by Randy — needs content + template overhaul |
| Cloudflare Pages | Build succeeds, deploy command issue, nameservers pending |
| Resend email | `spacemanwins.win` verified, `roviqai.xyz` NOT verified |

---

## Blockers (Need Randy)

- [ ] Approve toll processing email blast (sample in Gmail)
- [ ] Schedule Delivered second meeting (license expires 3/5)
- [ ] Cloudflare nameserver setup (Namecheap → Cloudflare)
- [ ] CH: Google Analytics export from Brian
- [ ] HOP: Labels finalized + photos
- [ ] Add `roviqai.xyz` to Resend for professional outreach
