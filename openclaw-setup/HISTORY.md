# OpenClaw Operating History (Roviq)

_Last updated: 2026-02-16 UTC_

This file captures the major operational history, decisions, incidents, and shipped work so the full OpenClaw setup has context (not just prompts/config).

---

## 1) Operating Model Evolution

### COO model and quality gates
- The system evolved from ad-hoc execution into a strict COO orchestration model:
  - specialists do execution
  - COO coordinates and synthesizes
  - 2-reviewer gate for deliverables
- Mandatory review gate was formalized after misses where unreviewed outputs propagated mistakes.
- Heartbeat workflow became the main control loop for status checks, blockers, and quality enforcement.

### Agent command structure
- Role docs were standardized under `team/`:
  - `ORCHESTRATOR.md`
  - `DEVELOPER.md`
  - `QA.md`
  - `RESEARCHER.md`
  - `DESIGNER.md`
  - `WORKFLOW.md`
- Session behavior moved to stronger task discipline with explicit state-machine style instructions and one-task-at-a-time controls.

---

## 2) Messaging / Multi-Agent Comms History

### bot-bus fanout and relay hardening
- War-room communications moved to bus-first + mention fallback due to brittle tag-only routing.
- Key merges (recorded in memory):
  - PR #7: bot-bus fanout + broadcast support + loop guards + mention fallback
  - PR #8: subscriber wiring + lifecycle hardening

### Runtime config changes
- `channels.discord.groupPolicy` moved to `open`.
- `session.agentToAgent.maxPingPongTurns` set to schema max (`5`).

### Noted issues and mitigations
- SSE subscriber flapping diagnosed as timeout applied to full stream (not just handshake).
- Durable mitigation guidance established:
  - use internal service URL where possible
  - increase fetch timeout / reconnect interval
  - long-term fix: handshake timeout only, then persistent stream.

---

## 3) GLASS Program History (high-level)

### Product direction
- GLASS positioned as consumer price comparison -> dispenser intelligence engine -> platform play.
- GTM direction anchored around the “Tom Sawyer / marketplace trap” strategy:
  - consumer traffic first
  - convert dispensaries via visibility pressure
  - expand to brand + operator tooling.

### Data/scraping context
- Multi-source scraping stack includes Weedmaps, Dutchie, Leafly, Jane.
- Recent focus concentrated on Weedmaps reliability and run quality.

---

## 4) 2026-02-16 Deep-Dive (Major Workday)

### A) Weedmaps incident and debugging cycle

#### Starting problem
- Reported low Weedmaps effectiveness (initially interpreted as ~10/173 quality).  
- Need: prove extraction quality, fix reliability, and avoid false dashboard interpretations.

#### Findings across iterations
- Early fixes introduced:
  - parse `#__NEXT_DATA__` payload for `menuItems`
  - context refresh every 10 stores
- Additional root causes discovered:
  - cookie/consent + age-gate interstitial variants blocking extraction
  - menu tab not reliably activated after redirects
  - dashboard/schema confusion between fields (`stores_scraped` vs `stores_attempted`, `products_scraped` vs `products_found`)
  - `source` vs `platform` usage mismatch in queries
  - schema/search_path assumptions and run metric mapping issues

#### Key outputs generated
- `projects/glass/weedmaps-scraper-fix.md`
- `projects/glass/weedmaps-debug-findings.md`
- `projects/glass/weedmaps-test-results.md`
- reproducible proof pack:
  - `projects/glass/weedmaps-proof-30stores.csv`
  - `projects/glass/weedmaps-proof-30stores.json`
  - `projects/glass/weedmaps-proof-report.md`
  - `projects/glass/proof-screenshots/`

#### Proof-pack status
- Deterministic 30-store diagnostic framework established (seeded sampling + reproducible command path).
- Provided hard evidence format (per-store slug/url/menu state/counts/failure reason + screenshots), replacing “trust me” reporting.

#### Operational decision
- Continue iterative Weedmaps nav-state-machine hardening until deterministic 30-store pass target is consistently cleared, then scale.

---

### B) Launch/GTM planning work

- Created `projects/glass/launch-plan.md` with:
  - launch criteria
  - stability window requirements
  - phased timeline
  - execution dependencies
- Established gating logic: do not push public launch until data reliability threshold is met.

---

### C) GCP migration track (parallel-only infra)

#### Why started
- Need clean migration for scrapers without touching current Railway production.
- Requirement: infra-as-code, auditable, repo-based deployment.

#### Initial scaffold created
- New branch: `feat/gcp-scraper-migration-infra`
- PR opened in GLASS repo: #115
- Added `infra/gcp-scrapers/` with Terraform, runtime, scripts, and docs.

#### Review and remediation cycle
- First independent review returned **NO-GO** with critical/high findings.
- Fix cycle addressed major issues:
  - runtime path contract mismatch
  - infinite rerun risk from restart model
  - over-privileged secret IAM
  - insecure exposure defaults
  - non-deterministic deploy behavior
  - script preflight/idempotency gaps
- Second review found remaining critical build-context mismatch.
- Follow-up fix shipped on same branch to enforce one deploy artifact contract and fail fast on invalid source layouts.

#### Key artifacts
- `projects/glass/reviews/gcp-infra-codex-review.md`
- `projects/glass/reviews/gcp-infra-codex-second-review.md`
- `projects/glass/reviews/pr-115-fix-summary.md`

---

### D) Infrastructure ops incident (VPS lockout)

#### Context
- Team began provisioning a new US VPS and attempted immediate hardening.

#### Incident
- SSH access was lost after config/security changes; host key changed; login path confusion (local vs server command execution).

#### Recovery pattern documented
- Use provider console/rescue mode for rapid SSH restore.
- Re-enable minimal SSH baseline first (listen + auth), then test login, then re-harden.
- Never disable root/password until replacement key-based login is confirmed in a second terminal.

---

## 5) Repo / Governance Practices Reinforced

- GitHub flow required:
  - feature branch -> PR -> review -> merge
- “Push and prove” approach reinforced:
  - include evidence files for claims
  - include deterministic reproduction steps where possible
- Infrastructure changes treated as code + reviewed artifacts, not ad-hoc shell-only changes.

---

## 6) Current active themes (as of this export)

1. **Weedmaps reliability hardening** with deterministic evidence-based validation
2. **Parallel scraper migration** strategy (current prod untouched)
3. **Launch readiness discipline** (data quality gates before GTM blast)
4. **Operational access model** for sustainable DevOps control without repeated credential sharing

---

## 7) Where to look for detailed context

- Core operating behavior:
  - `openclaw-setup/core/AGENTS.md`
  - `openclaw-setup/core/SOUL.md`
  - `openclaw-setup/core/HEARTBEAT.md`
- Role execution standards:
  - `openclaw-setup/team/WORKFLOW.md`
- Day log snapshot:
  - `memory/2026-02-16.md`
- GLASS work artifacts:
  - `projects/glass/launch-plan.md`
  - `projects/glass/weedmaps-proof-report.md`
  - `projects/glass/reviews/pr-115-fix-summary.md`
