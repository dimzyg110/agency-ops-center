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

## 7) Historical Timeline (Deep Dive)

### 2026-02-09 — Foundation reset and model unlock day
- OpenClaw model catalog was manually patched so Opus 4.6 variants were available pending upstream support.
- Subagent model allowlist behavior was diagnosed (`agents.defaults.models`), explaining prior “model not allowed” failures.
- Workspace migrated into `agency-ops-center` with full COO operating files and client/project structure.
- GitHub org migration to `Roviq-AI` completed; dual-account auth context documented.
- Decoded lead pipeline was executed with 5-agent research and full synthesis discipline.
- Key operating lesson captured: provider/model compatibility must be verified per route, not assumed by model name.

### 2026-02-10 — Delivered lead intelligence and proposal-quality hardening
- Delivered lead research completed with multiple specialist agents and dual-review gate.
- Casino-spam compromise on Delivered web footprint was independently re-verified after challenge.
- “First app” positioning refined with regulatory/platform caveats (Android policy, Lantern failure history, Zyp Run context).
- Humanizer pipeline was stress-tested; provider-specific failures documented; fallback routing established.
- Strategic direction clarified: partnership/equity posture over vendor posture; React Native app direction and ownership terms corrected.

### 2026-02-11 — GLASS deployment realism day
- "Deployed" claims were separated from "working product" claims.
- Clerk auth and routing failures were repeatedly tested and documented across attempts.
- Backend deploy + DB migration progress occurred in parallel with unresolved auth flow issues.
- Tool-signature bug on Antigravity/Claude tool calls was investigated; partial fix applied; broader model coverage issue identified.
- Core lesson reinforced: every deployment claim requires E2E verification against user flows.

### 2026-02-12 — Security/reliability and ecosystem expansion
- Security hardening landed (secret removal, endpoint protection, role defaults, rate limits, security headers).
- Data endpoints were locked behind auth and verified in production.
- Budtender messaging and product positioning were corrected to reflect actual delivered capability.
- Large CCC data import program initiated (lab tests, facility sales, operators, county data).
- Multiple integration/master-plan artifacts produced to align GLASS + Cue + client ecosystem execution.

### 2026-02-13 — Scraper architecture inflection point
- Major discovery: CamoFox assumptions were wrong/fragile in production context; plain Playwright Firefox had been the real reliable engine for historical successful runs.
- Three Opus engineering lanes executed targeted fixes:
  - Jane browser rewrite
  - Weedmaps progress visibility and behavior diagnosis
  - Leafly exponential backoff and adaptive throttling
- PR #30 became the primary convergence branch for multi-scraper reliability changes.
- Structured logging framework added across scraper services.
- Gateway instability from too many concurrent/stale sessions prompted stricter subagent cleanup practice.
- Critical COO lesson logged: stop repeating broken tactics; pivot architecture when failure pattern repeats.

### 2026-02-14 — GPID wartime sprint and matching engine buildup
- High-volume schema/data operations performed (dedupe, SKU normalization, candidate precompute, verification flow acceleration).
- Match quality rose through staged interventions: re-hash + fuzzy matching + verifier + dashboard logic updates.
- Brand dictionary/fuzzy pipelines underwent review-fix cycles, including explicit rejection of over-aggressive merging behavior.
- Testing plan and regression baselines were introduced to prevent silent quality regressions.
- Long-form GPID deep-dive and model research documents created for strategic/technical alignment.

### 2026-02-15 — ZeroClaw + operational deploy stabilization
- Multi-service ZeroClaw/bot-bus deployments were stabilized via config-path corrections, startup-time key injection, and model-id fixes.
- Discord flapping behavior was narrowed to token identity/intents and service-level config alignment.
- GLASS UX/API fixes continued in parallel; known issues triaged with explicit blocker accounting.
- Durable lesson: token-to-bot identity mapping must be validated before redeploy loops.

### 2026-02-16 — Evidence-first operations day
- Weedmaps diagnosis shifted from anecdotal status to reproducible proof artifacts.
- Deterministic 30-store proof mechanism produced CSV/JSON/screenshot evidence sets.
- GCP migration scaffold PR (#115) followed full review-remediation cadence (NO-GO -> fixes -> blocker closure).
- OpenClaw operating pack was exported into agency repo for portability and continuity.
- VPS bootstrap attempt triggered SSH lockout incident, generating a clearer “recover first, harden second” ops doctrine.

---

## 8) Incident Postmortems (Condensed)

### A) Deploy claim vs product reality drift
- **Pattern:** Build/deploy success interpreted as product success.
- **Impact:** False “done” states while user journeys were still broken.
- **Correction:** Mandatory E2E flow checks for all externally meaningful completion claims.

### B) Scraper anti-detection overreach
- **Pattern:** Engineering cycles focused on anti-detection stack assumptions that were not actually the source of throughput reliability.
- **Impact:** Multiple PR churn loops and delayed fixes.
- **Correction:** Empirical baseline first (what currently works), then minimal-change reliability improvements.

### C) Session/gateway overload
- **Pattern:** Too many long-lived/stale subagent sessions causing gateway instability and degraded observability.
- **Correction:** strict cleanup behavior, bounded concurrency, and heartbeat-based status hygiene.

### D) SSH hardening lockout
- **Pattern:** Security controls applied before replacement login path was verified.
- **Impact:** access outage and operational delay.
- **Correction:** always test new non-root auth in parallel terminal first; only then disable root/password.

---

## 9) Technical Patterns Worth Preserving

1. **Proof packs over assertions**
   - For data-quality claims: machine-readable output + reproducible command + screenshots.
2. **Review-fix-review loops**
   - Independent reviewer model catches architecture/runtime mismatches better than single-pass coding.
3. **Parallel-only migration strategy**
   - New infra in isolated branch/folder; current production untouched until shadow-mode gates pass.
4. **Schema/query contract verification**
   - Validate table/column names and semantic fields (e.g., `platform` vs `source`) before KPI reporting.
5. **Runtime contract alignment**
   - Compose paths, deploy scripts, and docs must share one artifact/layout contract or deployment breaks at first clean host.

---

## 10) Expanded artifact index (historical)

### Core memory documents
- `memory/MEMORY.md`
- `memory/2026-02-09.md`
- `memory/2026-02-10.md`
- `memory/2026-02-11.md`
- `memory/2026-02-12.md`
- `memory/2026-02-13.md`
- `memory/2026-02-14.md`
- `memory/2026-02-15.md`
- `memory/2026-02-16.md`

### GLASS execution artifacts
- `projects/glass/launch-plan.md`
- `projects/glass/weedmaps-scraper-fix.md`
- `projects/glass/weedmaps-debug-findings.md`
- `projects/glass/weedmaps-test-results.md`
- `projects/glass/weedmaps-proof-report.md`
- `projects/glass/weedmaps-proof-30stores.csv`
- `projects/glass/weedmaps-proof-30stores.json`
- `projects/glass/proof-screenshots/`

### Infra review/fix artifacts
- `projects/glass/reviews/gcp-infra-codex-review.md`
- `projects/glass/reviews/gcp-infra-codex-second-review.md`
- `projects/glass/reviews/pr-115-fix-summary.md`

---

## 11) Current projects and portfolio snapshot (as of 2026-02-16)

### A) Primary build: GLASS
- Repo: `Roviq-AI/glass`
- Live surface: `glassintel.xyz`
- Current reality:
  - core platform phases largely built
  - reliability and data-quality hardening still active
  - Weedmaps extraction reliability remains a focused execution lane
- Known execution tracks:
  - consumer pricing site UX cleanup (hero/product page refinement)
  - dispensary visibility/claim flow progression
  - scraper infrastructure migration in parallel path (current prod untouched)

### B) Client portfolio (active)

#### AC (Advanced Cultivators)
- Ongoing:
  - weekly social/content production
  - YouTube/media strategy
  - toll processing outbound campaign
- Near-term dependency:
  - outbound blast approval

#### CH (Cannabis Healing)
- Ongoing:
  - weekly social graphics
  - SEO expansion and content planning
  - automation opportunities
- Near-term dependency:
  - analytics export + platform access confirmation

#### HOP (House of Pride)
- Ongoing:
  - GTM strategy + copy + launch prep
- Near-term dependency:
  - label/photo assets finalized

### C) Lead pipeline (strategic)
- **Decoded**: proposal/demo stage, awaiting decision movement.
- **Delivered**: partnership proposal delivered; follow-up meeting timing is key constraint.

### D) Revenue and ops initiatives
- Newsletter funnel remains strategic operating channel but needs template/content overhaul.
- Cue pathway and legal/partner dependencies remain partially blocked.
- Infrastructure effort split:
  - keep current services stable
  - establish reproducible migration infrastructure as code

### E) Active blockers pattern
- approvals and external access are recurring critical path blockers
- data reliability gates must clear before public GTM escalation
- deployment/access operations need stable runbooks to avoid productivity loss during incident recovery

---

## 12) Where to look for detailed context

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
