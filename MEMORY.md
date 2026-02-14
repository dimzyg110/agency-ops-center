# Long-Term Memory

_Curated essentials. Stale info removed Feb 14. Daily logs in memory/._

---

## Randy

- Hates traditional sales — never cold call, pitch, or chase
- Loves cinematic content — premium, not generic
- Direct communication only — no filler
- Cannabis industry expert, builds in React/Swift
- Location: Boston area, timezone EST

## Clients

- **AC** (Advanced Cultivators): Cultivator, Indoor Tier 2, Lowell. Debbie+Clarice execute. First Latino-owned rec cultivator in MA. Retail location coming. Ranks #91 in GLASS data (89 products, 4 platforms). Toll processing outreach: 85 emails ready.
- **CH** (Cannabis Healing): Retailer, East Boston. Brian is contact. Repo: `randytorres/ch-web` (React+Vite+Tailwind, Netlify). NEVER push to main. SEO pages built for Logan Airport.
- **HOP** (House of Pride): LGBTQ+ cannabis apparel, GTM phase. Kam is partner. Uses AC's license.
- **Delivered Inc (Lead)**: Delivery operator MD1303, Clinton MA. License expires 3/5/2026 (late renewal). Partnership deal: equity + rev share. App = React Native + Blaze POS backend. Exclusivity until April 2029.

## Model Hierarchy (LOCKED)

| Tier | Model | Route | Use For |
|------|-------|-------|---------|
| T1 | GPT 5.3 Codex | `openai-codex/gpt-5.3-codex` | Architecture, code, review |
| T2 | Claude Opus 4.6 | `anthropic/claude-opus-4-6` | Strategy, orchestration |
| T3 | MiniMax M2.5 | `openrouter/minimax/minimax-m2.5` | Clear tasks, fast execution |
| T4 | Kimi K2.5 | `openrouter/moonshotai/kimi-k2.5` | Frontend, long context |
| Imagen | Gemini 2.0 Flash | `google/gemini-2.0-flash-exp-image-generation` | Image gen ONLY |

- Gemini NOT for code/review/research (Randy directive). Exception: Gemini 2.5 Flash for LLM parsing.
- Specialist and reviewer MUST be different models.
- Every spawn needs role prompt (DEVELOPER.md or QA.md).

## GLASS — Current State (Feb 14)

### Database
- **Railway Postgres ONLY**: `postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway`
- Schema: `public` (NOT `glass`). Always `SET search_path TO public`.
- Neon is DEPRECATED (sandbox DATABASE_URL still points to it — always override).
- **150K products, 206K prices, 1,255 operators, 778 sources**

### Wartime Sprint (Feb 14 — ALL PHASES BUILT)
| Phase | Status | PR | Result |
|-------|--------|-----|--------|
| 0 Quarantine | ✅ | #45 | brand_dict quarantined, 5 new tables |
| 1 Brand Authority | ✅ | #46 | 308 verified brands (3+ platforms) |
| 2 LLM Parser | 🔄 | — | 36,556 products, Gemini 2.5 Flash |
| 3 GPID Lock | ✅ | #48 | 174 verified GPIDs (growing) |
| 4 Consumer API | ✅ | #47 | Search + detail + brands endpoints |
| Review Fixes | ✅ | #49 | All feedback addressed |

### Parser Stats
- **Winner: Gemini 2.5 Flash** — 0.952 avg confidence, $0.15/$0.60/M tokens, forces JSON via responseMimeType
- Gemini 2.5 Pro: 0.950 (same quality, 8x cost)
- Gemini 3 Pro: 0.935 (WORSE, rejected)
- Gemini 3 Flash: 0.939 (WORSE + JSON errors, rejected)
- Script: `scripts/gpid/parse-top-brands.ts` — 4 providers (NVIDIA, Anthropic, OpenRouter, Google)

### Site Direction
- Dark mode, teal (#00E5A0) → amber (#FFB020), Cash App aesthetic
- Zero cannabis green, zero AI mentions, zero sign-up walls
- "Every dispensary. Every price."
- Next.js 15 + Tailwind + shadcn/ui
- Master plan: `projects/glass/PRICES-SITE-GAMEPLAN.md`

### GTM: Tom Sawyer Strategy
- `projects/glass/GTM-MARKETPLACE-TRAP.md` — external advisor playbook
- Phase 1: Reddit exposé → 10K visitors
- Phase 2: Dispensaries claim pages → free data labeling
- Phase 3: Brand MAP violation dossiers → $3.5K/quarter revenue
- Phase 4: ML flywheel → state expansion
- Phase 5: POS API → become cannabis UPC code

### Key Strategy Docs
- `WARTIME-SPRINT-PLAN.md`, `WARTIME-CTO-DIAGNOSIS.md`
- `GPID-MONOPOLY-PLAYBOOK.md`, `GTM-MARKETPLACE-TRAP.md`
- `PRICES-SITE-GAMEPLAN.md`, `GPID-MATCHING-DEEP-DIVE.md`

## Operations Rules

- **COO never executes directly** — spawn subagents for everything
- **2+ reviews per deliverable** — Codex T1 + MiniMax T3 standard pair
- **Investigate before implementing** — investigator → findings → implementer
- **Git**: Bot token `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` (randyt1444-arch). PRs only, Randy merges.
- **Always `cleanup: "delete"` on spawns**
- **Don't replace assets without Randy seeing replacements first**

## Technical Lessons

- **CamoFox is the PROBLEM**: Plain Playwright Firefox works. CamoFox Fission breaks cross-origin fetch. Anti-detection = realistic viewport/UA/locale, nothing more.
- **CamoFox needs libgtk-3-0**: `apt-get install libgtk-3-0` after sandbox restart.
- **Sandbox restarts lose packages**: psql, pg, libgtk all need reinstall.
- **`memory_search` broken**: OpenAI embeddings key expired (401). Manual file reads only.
- **MEMORY.md limit**: 20,000 chars max or it gets truncated in context injection.
- **OpenRouter balance = $0**: Can't use for scripts.
- **Anthropic key not accessible from scripts**: Stored in OpenClaw auth profile (token mode).
- **Railway has 491GB RAM**: OOM kills are sandbox process limits, not memory.
- **nohup + pipe = fully buffered stdout**: Node output invisible until exit.

## Revenue & Products

- **GLASS**: Consumer price comparison → dispensary SaaS → brand portal → POS API
- **SIGNAL**: SEO automation. $1.5-2K/mo pilot target. At `projects/signal/`.
- **Newsletter**: "The Operator's Margin Report". Beehiiv distribution.
- **Roviq website**: `Roviq-AI/roviq-web`. White/editorial, red accent #D94F3D.

_Last updated: 2026-02-14 03:49 UTC_
