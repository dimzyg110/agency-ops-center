# Dashboard

**Last updated:** 2026-02-11

---

## Active Build: GLASS

**Status:** Phase 2 + Phase 4 complete, reviews in progress
**Repo:** `github.com/Roviq-AI/glass` (private)

### Phase Status

| Phase | What | Status |
|-------|------|--------|
| 0 | Contracts, CI, ownership | ✅ Done |
| 1 | Backend skeleton, DB schema, frontend shell, auth | ✅ Done |
| 2 | Scraping core (Firecrawl, Playwright, BullMQ) | ✅ Merged (PR #8) |
| 4 | Threat Radar intelligence (CCC ingest, scoring) | 🔄 PR #9 — dual review in progress |
| 3 | Price Wire + Morning Brief | ⬜ Next |
| 5 | Margin Engine v1 | ⬜ Queued |
| 6 | Pilot + hardening | ⬜ Queued |

### GLASS Known Gaps
- [ ] Contracts V2 PR #2 — needs cleanup (accidental WIP files), then merge
- [ ] BullMQ worker framework in `services/api`
- [ ] Drizzle SQL migrations
- [ ] Frontend typecheck — 743 tsc errors (strict disabled for MVP build)
- [ ] `severity_breakdown.total` mismatch between backend/frontend

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
