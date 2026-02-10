# Long-Term Memory

_Curated patterns, preferences, and lessons. Updated weekly from daily logs._

---

## Randy's Preferences

- Hates traditional sales — never suggest cold calling, pitching, or chasing
- Loves cinematic content — everything should feel premium, not generic
- Moves fast — needs help staying focused on revenue-generating work
- Direct communication only — no corporate speak, no filler
- Cannabis industry expertise — understands the market deeply

## Client Patterns

- **AC:** Creative client, values aesthetic and storytelling. Debbie and Clarice execute. Generate concepts → Randy curates → they produce. Active cultivator license (Indoor Tier 2, 5-10K sqft, Lowell). Has prerolls license. Pending manufacturer license (edibles/concentrates — incomplete). First Latino-owned rec cultivator in MA. Physical retail location coming soon.
- **CH:** Practical client, needs data-driven results. Brian is the point of contact. Growth through SEO, automations, and partner channels. Retailer in East Boston (MR283634). No delivery license. Website repo: `randytorres/ch-web` (React + Vite + Tailwind, Netlify deploy). Blog posts in `src/data/blogPosts.js`.
- **HOP:** Launch-phase client. Kam is the partner. Needs full GTM before anything else. Sells cannabis products through AC's license (white labeled).
- **Delivered Inc (Lead):** Licensed delivery operator (MD1303), Clinton MA, ~30 towns Central MA. Founders: Ruben Seyde, Eddy Twal, Tut Liu. Social equity. Can expand statewide. Site hacked (casino spam). Partnership deal: equity + rev share + small upfront. App play = first cannabis delivery app in MA. AC supplies wholesale. Exclusivity until April 2029.

## Operations Patterns

- Newsletter is the core funnel — everything feeds into it
- Margin Snapshots are the best lead magnet — free, specific, proves capability
- Multi-model reviews catch different issues — always use 2+ models for review
- Sprint pricing ($3K) is the sweet spot for initial engagement
- Content automation for social is the biggest time sink — needs systemization
- **When research reveals a competitor tool/platform, the COO move is "build our own" — don't just report, propose the play across all clients** (learned 2026-02-10, Prometheus incident)
- **Cross-client pattern recognition is mandatory** — every finding should be scanned against CH, AC, HOP, and pipeline leads
- **Every insight has two layers: client impact AND Roviq growth** — client work is a means to grow Roviq. If we build a tool for one client, ask: can we sell this to 26 others? Is this a new vertical? Does this reposition Roviq in the market? (clarified 2026-02-10)

## What Works

- Value-first approach > any sales tactic
- AI-generated content + Randy curation > pure AI output
- Ecosystem thinking > isolated projects
- Weekly rhythm > ad-hoc work

## What Doesn't Work

- Cold outreach (Randy won't do it, clients don't respond)
- Over-building before validation (too many ideas, not enough shipped)
- Manual social posting (time sink, should be automated)
- WordPress for client sites — Randy builds in React, each client has unique brand identity. Blog generator should produce React-compatible content, not WP posts.
- Kimi K2.5 for large file writes — NVIDIA proxy truncates at ~8K chars. **FIXED: use `openrouter/moonshotai/kimi-k2.5` instead.** OpenRouter handles 48K+ in a single write. NVIDIA route still works for small tasks (free). Moonshot direct (`moonshot/kimi-k2.5`) requires balance top-up.

---

_Last updated: 2026-02-10_
