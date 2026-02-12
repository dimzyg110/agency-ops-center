# OpenClaw Skill & Agent Setup — Improvement Plan

**Based on:** [Shell + Skills + Compaction: Tips for long-running agents](https://developers.openai.com/blog/skills-shell-tips)
**Audited:** 2026-02-12
**Scope:** 22 skills, agent config (AGENTS.md, SOUL.md, TOOLS.md, HEARTBEAT.md), memory system, compaction strategy

---

## Executive Summary

Our setup is structurally sound — we have skills, memory, heartbeat cycles, and a multi-agent orchestration pattern. But measured against OpenAI's 10 tips for production agent workflows, we have clear gaps: skill descriptions are inconsistent (some are routing logic, some are marketing copy), we have 4+ overlapping frontend skills that will confuse routing, templates and procedures live in system prompts instead of skills, and our compaction strategy hasn't been stress-tested for long runs. This plan fixes all of it.

---

## 1. Skill Descriptions — Routing Logic vs Marketing Copy

**OpenAI Tip #1:** Descriptions should answer: When should I use this? When should I NOT? What are the outputs?

### ✅ Already Good (have "Use when / Don't use when" patterns)

| Skill | Why It Works |
|-------|-------------|
| `agent-browser` | Has explicit "Use agent-browser when..." vs "Use built-in browser tool when..." |
| `human-optimized-frontend` | Has "Activate this skill only when..." and explicit "Do not activate for:" list |
| `self-improvement` | Has 6 specific trigger conditions in the description |
| `humanizer` | Lists specific patterns it detects — clear trigger criteria |

### ❌ Needs Rewrite (vague, marketing-style, or missing boundaries)

| Skill | Current Problem | Fix |
|-------|----------------|-----|
| `deep-research` | Description says "complex, multi-step research" — too vague. When is research "complex enough"? | Add: "Use when: research requires 3+ sources, cross-referencing, or multi-day synthesis. Don't use when: user wants a quick web search or single-source lookup." |
| `frontend-design` (superdesign) | "Expert frontend design guidelines" — could match anything UI-related | Add: "Use when: building new UI from scratch and need design workflow (layout → theme → animation → code). Don't use when: extracting design from existing code (use frontend-design-extractor) or need full production site (use frontend-design-ultimate)." |
| `frontend-design-ultimate` | Long description but no "don't use when" — will fight with superdesign, ui-ux-pro-max | Add: "Don't use when: redesigning existing frontend (use human-optimized-frontend), extracting design systems (use frontend-design-extractor), or need UX critique without code (use ui-ux-pro-max)." |
| `ui-ux-pro-max` | Longest description of all skills, tries to cover everything UI/UX | Narrow: "Use when: user needs UX flows, information architecture, design critique, or design-system tokens. Don't use when: building a full static site (use frontend-design-ultimate) or redesigning an existing app (use human-optimized-frontend)." |
| `client-onboarding` | "Onboard new digital agency client with full project setup" — too brief | Add: "Use when: new client identified, need folder structure + brief + research. Don't use when: existing client needs a new deliverable (that's regular task execution)." |
| `new-project` | "Pipeline for validating, designing, and building new projects" — overlaps with client-onboarding | Clarify: "Use when: internal Roviq project or product idea needs validation. Don't use when: onboarding an external client (use client-onboarding)." |
| `byterover` | Description is fine but doesn't explain when NOT to use memory_search instead | Add: "Don't use when: looking up simple facts from MEMORY.md (use memory_search). Use ByteRover when: persisting patterns, conventions, or architectural decisions for a specific project." |
| `proactive-agent` | Description is a feature list, not routing logic | Rewrite: "Use when: configuring an agent to be proactive (anticipate needs, self-heal, reverse-prompt). Don't use when: agent is already configured and running — this is a setup/architecture skill, not a runtime skill." |
| `playwright-cli` | "Browser automation via Playwright CLI" — overlaps with agent-browser and built-in browser | Add: "Use when: need Playwright CLI specifically (testing workflows, complex multi-page automation with code). Don't use when: simple page snapshots (use built-in browser tool) or accessibility-tree-based automation (use agent-browser)." |
| `roles` | "Subagent role definitions" — too generic | Add: "Use when: spawning a specialist subagent and need the role definition. Don't use when: you already know the role instructions or the task is self-contained." |
| `theme-gen` | "Generate a complete design system from brand colors" — fine but no boundaries | Add: "Don't use when: you need a full site build (use frontend-design-ultimate) or are extracting existing design tokens (use frontend-design-extractor)." |
| `reddit` | Fine for what it is, but no "don't use when" | Add: "Don't use when: user wants general web search (use web_search). Use only for Reddit-specific browsing, searching, or posting." |
| `x-trends` | Fine, simple scope | No change needed |
| `clawddocs` | Fine, very specific scope | No change needed |

---

## 2. Negative Examples — Preventing Misfires

**OpenAI Tip #2:** Adding "Don't call this skill when..." prevents the 20% triggering drop Glean observed.

### Critical: Frontend Skill Cluster (4 skills that look similar)

This is our biggest routing risk. Four skills all match "build me a UI":

| Skill | Intended Use | Misfire Risk |
|-------|-------------|-------------|
| `frontend-design` (superdesign) | Design workflow: layout → theme → animation → code | Gets triggered for any UI task |
| `frontend-design-ultimate` | Full production static sites (Vite/Next.js) | Overlaps with superdesign |
| `ui-ux-pro-max` | UX flows, design systems, critique | Overlaps with everything |
| `human-optimized-frontend` | Quantified redesign of existing frontend | Could trigger on any "redesign" mention |

**Fix:** Add a routing decision tree to each skill's description:

```
"Building new site from scratch?" → frontend-design-ultimate
"Need UX critique or design tokens?" → ui-ux-pro-max  
"Redesigning an existing frontend?" → human-optimized-frontend
"Need design workflow (wireframe → theme → code)?" → frontend-design (superdesign)
"Extracting design from existing codebase?" → frontend-design-extractor
```

Each skill should include this tree in its description with itself highlighted.

### Secondary: Browser Skill Cluster (3 skills)

| Skill | Intended Use |
|-------|-------------|
| `agent-browser` | Accessibility tree snapshots, ref-based selection |
| `playwright-cli` | Full Playwright CLI, testing workflows |
| `fast-browser-use` | Rust-powered, performance-critical DOM work |
| Built-in `browser` tool | Simple page interaction, screenshots |

`agent-browser` already has good routing. `playwright-cli` and `fast-browser-use` need "Don't use when" blocks.

### Tertiary: Research/Knowledge Cluster

| Skill | Intended Use |
|-------|-------------|
| `deep-research` | Multi-step research with planning |
| `byterover` | Project knowledge persistence |
| Built-in `web_search` | Quick lookups |
| Built-in `memory_search` | Recall from MEMORY.md |

Add negative examples: "Don't use deep-research for simple fact lookups. Don't use byterover for ephemeral queries."

---

## 3. Templates in System Prompts → Move Into Skills

**OpenAI Tip #3:** Templates inside skills are loaded only when invoked. Templates in system prompts inflate every request.

### Currently in AGENTS.md (should be in skills):

| Template/Procedure | Current Location | Move To |
|-------------------|-----------------|---------|
| Standard Task Execution (Steps 1-6) | AGENTS.md §📋 | `skills/roles/SKILL.md` or new `skills/task-execution/SKILL.md` |
| `sessions_spawn()` template with voice rules | AGENTS.md §Step 3 | `skills/roles/SKILL.md` — the voice rules string is 200+ tokens repeated in every spawn |
| Model Selection Strategy table | AGENTS.md §📊 | `skills/roles/SKILL.md` or `TOOLS.md` |
| Review workflow (Steps 4-5.5) | AGENTS.md §Step 4-5.5 | `skills/roles/reviewer/SKILL.md` — this is the review procedure |
| Humanizer gate procedure | AGENTS.md §Step 5.5 | `skills/humanizer/SKILL.md` — reference it, don't inline it |
| Client folder structure | TOOLS.md §📁 | `skills/client-onboarding/SKILL.md` |
| Strategic Pattern Recognition | AGENTS.md §🧠 | New `skills/strategic-scan/SKILL.md` |
| Cross-client scan checklist | AGENTS.md §🧠 Strategic | Same new skill |

### Estimated token savings: ~2,500-3,000 tokens per request

AGENTS.md is currently ~4,500 tokens. Moving templates into skills that load on-demand would cut system prompt by ~60% while keeping everything accessible.

### What STAYS in AGENTS.md:
- Core mission (orchestrate, don't execute)
- Critical rules (no solo execution, mandatory review, no system building without approval)
- Git discipline
- API key isolation
- Success metrics

### What MOVES to skills:
- All step-by-step procedures
- All templates and examples
- Model selection tables
- Folder structure conventions

---

## 4. Compaction Strategy

**OpenAI Tip #4:** Use compaction as a default primitive, not an emergency fallback.

### Current: `"compaction": { "mode": "safeguard" }`

Safeguard mode compacts only when approaching context limits. This is the "emergency fallback" approach the article warns against.

### Risk Assessment:
- **Main session (Opus 4.6):** 1M context window — unlikely to hit limits in normal sessions
- **Subagents:** Varies by model. Gemini 3 Pro High = 128K, Kimi K2.5 = 256K, older Claude models = 200K
- **Long GLASS review tasks:** 60+ files = easily 100K+ tokens. Subagents on 128K models are at risk
- **Heartbeat cycles:** 15-min cycles accumulate context. Over a day = hundreds of thousands of tokens

### Recommendation:
- **Keep safeguard for main session** — 1M window is generous enough
- **Consider proactive compaction for subagents** — especially on smaller context models
- **Add pre-compaction memory flush** — the `proactive-agent` skill already has this pattern. Before compaction triggers, write critical context to a file so it survives

### Action Items:
1. No config change needed for main session (1M is fine)
2. For long-running subagents, add explicit "write progress to file" checkpoints in task prompts
3. Review if OpenClaw supports per-session compaction modes (if so, set subagents to more aggressive compaction)

---

## 5. Skill Overlap — Routing Confusion Risk

**Severity: HIGH for frontend skills, MEDIUM for browser/research skills**

### Frontend Skills — Consolidation Recommendation

We have 5 frontend-related skills. That's too many for clean routing.

**Option A: Consolidate to 2 skills**
- `frontend-build` — Combines superdesign + frontend-design-ultimate (design workflow + production build)
- `frontend-analyze` — Combines frontend-design-extractor + human-optimized-frontend (analyze/redesign existing)
- Keep `ui-ux-pro-max` for pure UX/design-system work (no code output)

**Option B: Keep all 5 but add strict routing (faster to implement)**
- Add the decision tree from Section 2 to every frontend skill's description
- Add explicit "Don't use when" blocks referencing sister skills by name
- Test routing with 10 sample prompts to verify correct skill selection

**Recommendation:** Option B now (quick fix), Option A later (when we have time to merge skills properly).

### Browser Skills — Lower Risk
- `agent-browser` already has good routing
- `playwright-cli` needs "Don't use when" (see Section 1)
- `fast-browser-use` — check if this even works in our sandbox. If not, remove it.

---

## 6. Missing Skills

Based on our actual workflows, these skills don't exist but should:

### P0 — Would use daily

| Skill | Purpose | Why Missing Hurts |
|-------|---------|------------------|
| `deployment` | Railway/Vercel/Netlify deploy procedures, env var checklists, post-deploy verification | GLASS deployment was a mess partly because there's no standardized deploy skill |
| `git-workflow` | Branch strategy, PR creation, commit conventions, worktree management for parallel agents | Currently scattered across AGENTS.md and TOOLS.md |
| `newsletter` | Beehiiv newsletter creation workflow, content formatting, scheduling | Newsletter is "core funnel" but has no skill |

### P1 — Would use weekly

| Skill | Purpose | Why Missing Hurts |
|-------|---------|------------------|
| `strategic-scan` | Cross-client opportunity scanning, "build our own" evaluation, ecosystem play identification | Currently a big block in AGENTS.md that loads every request |
| `cannabis-market` | MA cannabis market data, CCC lookup procedures, license types, regulatory context | Agents keep having to re-learn this context |
| `margin-snapshot` | Margin Snapshot generation for leads | Was identified as key lead magnet but no standardized process |

### P2 — Nice to have

| Skill | Purpose |
|-------|---------|
| `social-content` | Social media content creation and scheduling |
| `email-outreach` | Personalized outreach email generation (for AC toll processing, etc.) |
| `seo-audit` | Already installed via skills.sh but not in workspace skills/ |

---

## 7. Security Posture

**OpenAI Tip #6:** Treat skills + networking as high-risk. Design for containment.

### Current State:
- Skills: ✅ Allowed (correct)
- Shell: ✅ Allowed with exec tool (correct)
- Network: ⚠️ No explicit allowlist — sandbox has some restrictions but not skill-level containment
- Credentials: ✅ API keys in .env, agents instructed not to touch (AGENTS.md rule)
- Git: ✅ Agents can push but can't modify credentials

### Gaps:
1. **No per-skill network policy** — A skill that needs web access gets the same access as one that doesn't
2. **Subagent credential exposure** — When we spawn subagents with task descriptions containing file paths, they can read .env if they choose to (honor system, not enforcement)
3. **No output validation** — Skills write wherever they want. No containment boundary like /mnt/data

### Recommendations:
1. **Document which skills need network** — Most don't. `deep-research`, `reddit`, `x-trends`, `web_search` do.
2. **Standardize output locations** — See Section 8
3. **Keep current credential isolation** — The honor-system approach works for our scale. Enforcement would require containerization we don't have.

---

## 8. Artifact Handoff — Consistent Output Locations

**OpenAI Tip #7:** Treat a standard directory as the handoff boundary for artifacts.

### Current State: Inconsistent
- Client work → `/data/workspace/clients/[name]/deliverables/` (when remembered)
- Project work → `/data/workspace/projects/[name]/` (varies)
- Subagent output → Sometimes `/tmp/`, sometimes workspace, sometimes nowhere
- Memory → `/data/workspace/memory/` (consistent ✅)

### Proposed Standard:

```
/data/workspace/                          # Root
├── clients/{name}/deliverables/          # Client deliverables (reviewed, final)
├── clients/{name}/drafts/                # Client work-in-progress
├── projects/{name}/                      # Internal projects
├── output/                               # NEW: Standard subagent output directory
│   ├── reviews/                          # Review feedback files
│   ├── research/                         # Research reports
│   ├── builds/                           # Build artifacts, screenshots
│   └── temp/                             # Ephemeral working files
├── memory/                               # Daily logs, long-term memory
└── skills/                               # Skill definitions
```

### Key Change:
Every subagent task prompt should specify: "Save output to `/data/workspace/output/[category]/[descriptive-name].md`"

This gives the COO a single place to check for all subagent deliverables instead of hunting through /tmp/ and random paths.

---

## 9. Recommended Implementation Order

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Add "Don't use when" to all frontend skills (Section 2) | 30 min | HIGH — prevents routing misfires |
| 2 | Move templates from AGENTS.md into skills (Section 3) | 1 hour | HIGH — saves ~3K tokens/request |
| 3 | Rewrite vague skill descriptions (Section 1) | 45 min | MEDIUM — better routing accuracy |
| 4 | Create `deployment` skill (Section 6) | 1 hour | HIGH — prevents another GLASS mess |
| 5 | Create `output/` directory structure (Section 8) | 15 min | MEDIUM — consistent artifact handoff |
| 6 | Create `git-workflow` skill (Section 6) | 45 min | MEDIUM — standardizes parallel agent work |
| 7 | Create `newsletter` skill (Section 6) | 30 min | MEDIUM — core funnel needs a skill |
| 8 | Create `strategic-scan` skill (Section 6) | 30 min | LOW-MEDIUM — moves weight out of AGENTS.md |
| 9 | Evaluate frontend skill consolidation (Section 5, Option A) | 2 hours | LOW — Option B is sufficient for now |
| 10 | Remove `fast-browser-use` if non-functional | 5 min | LOW — cleanup |

**Total estimated effort: ~7 hours of agent work**

---

## 10. Quick Wins (Do Right Now)

1. **Create `/data/workspace/output/` directory structure** — 1 command
2. **Add decision tree to frontend skill descriptions** — copy-paste the routing tree from Section 2 into each skill
3. **Remove `fast-browser-use`** if `chrome` binary isn't available in sandbox
4. **Update subagent spawn template** to always include output path in `/data/workspace/output/`

---

*Generated from audit of 22 skills against OpenAI's "Shell + Skills + Compaction" best practices guide.*
*Next review: When new skills are added or after implementing Priority 1-4 changes.*
