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
- **Delivered Inc (Lead):** Licensed delivery operator (MD1303), Clinton MA, ~30 towns Central MA. Founders: Ruben Seyde, Eddy Twal, Tut Liu. Social equity. Can expand statewide. Site hacked (casino spam — confirmed live by 3 agents, 5 URLs in sitemap, WordPress compromised Oct 2022-Aug 2023). Partnership deal: equity + rev share + small upfront. App play = first operator-branded cannabis delivery app in MA. AC supplies wholesale. Exclusivity until April 2029. **Jointly partnership**: Delivered currently fulfills for Jointly (third-party AI shopping app) — building own app = owning the customer. License expires 3/5/2026 (renewal should have been filed by 12/5/2025, they're late). Renewal = 4-step process + $10K fee, NOT just a payment. Google Play bans cannabis sales apps (Android blocked). Lantern tried in 2022, died in 2 months.

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
- **Opus 4.6T subagent bug**: Works as main session model but fails on multi-turn subagent sessions (thinking.signature field required error). Single-turn subagent tasks work. Fallback: Sonnet 4.5T or Gemini 3 Pro High for subagents.
- **Opus 4.6 (non-thinking)**: Returns 404 on Antigravity — model not available without thinking enabled.
- Kimi K2.5 for large file writes — NVIDIA proxy truncates at ~8K chars. **FIXED: use `openrouter/moonshotai/kimi-k2.5` instead.** OpenRouter handles 48K+ in a single write. NVIDIA route still works for small tasks (free). Moonshot direct (`moonshot/kimi-k2.5`) requires balance top-up.
- **iOS Safari video autoplay**: `muted + playsInline + autoPlay` should work without user gesture. Common failure causes: (1) conditional rendering that destroys/recreates video elements (breaks autoplay), (2) too many simultaneous videos, (3) Low Power Mode, (4) video at tiny size (1x1px won't autoplay), (5) wrong H.264 profile. Use baseline profile level 3.1 for maximum iOS compatibility. Only render one video at a time (active card).
- **Canvas video rendering** to avoid native play button: works but video must be full-size for iOS to autoplay it. Canvas approach adds CPU overhead on mobile.
- **archive.org for music**: Direct CDN URLs work (`ia800608.us.archive.org`), redirect URLs don't work for cross-origin audio. Many mainstream tracks are "dark" (restricted). Video uploads sometimes have accessible audio that can be extracted with ffmpeg.
- **GitHub Pages video hosting**: Works but cache-control is only 10 min (`max-age=600`). Not as fast as R2 CDN but avoids cross-origin issues. Deploy takes ~45-60s after push.
- **ffmpeg video compression**: CRF 25, H.264 baseline profile, 1080p, `movflags +faststart` gives good mobile results. 87MB → 7MB (92% reduction) while keeping acceptable quality.

## Tech Stack for Client Work

- **Delivered**: Blaze POS (open API at `apidocs.blaze.me`, BPN partner network). App = React Native frontend, Blaze = backend. Blaze handles dispatch, driver app, payments, manifests, inventory. App only needs to be the customer experience layer.
- **CH**: React + Vite + Tailwind on Netlify. Blog posts in `src/data/blogPosts.js`. Repo: `randytorres/ch-web` (private).
- **AC**: Swift native iOS (AC Blacksite app — Randy built). Cinematic UX.
- **All clients**: React-based sites, unique brand identities, NO WordPress.

## Delivered Partnership — Key Facts

- Blaze POS is their platform (they approached Blaze for partnership too)
- License MD1303 covers statewide delivery — scaling is operational, not regulatory
- Social equity exclusivity locked until April 2029 (CCC voted 4-0)
- Only 27 delivery operators in MA — no one has a mobile app
- Midnight Cannabis Lounge = the brand direction (premium launch standard)
- React Native for cross-platform (iOS + Android), 12-week MVP, Delivered owns app IP
- AC supplies wholesale (house brand "Delivered Collection" at 35%+ margins)
- Proposal V2 final: `clients/_leads/delivered/PROPOSAL-DRAFT.md` (commit `32a4e39`)
- Brand vision in reserve: `clients/_leads/delivered/plans/plan-3-full.md` (63K, Kimi)

---

- **19 skills from skills.sh installed** (Feb 10): programmatic-seo, seo-audit, content-strategy, copywriting, copy-editing, email-sequence, social-content, schema-markup, analytics-tracking, vercel-react-native-skills, competitor-alternatives, referral-program, docx, pdf, pptx, xlsx, doc-coauthoring, webapp-testing, web-design-guidelines. In `~/.agents/skills/`.
- **Humanizer pipeline works**: Gemini 3 Pro High is reliable for humanizer passes. Opus 4.6T works if task completes in one turn.
- **No deploy service credentials configured** — need Vercel/Netlify/Cloudflare token from Randy to deploy demos/sites from sandbox. GitHub Pages blocked on private repos (free plan).
- **Decoded demo built** at `projects/decoded-demo/` — Vite + React + Tailwind, TikTok-style feed. Randy hasn't seen it yet.

_Last updated: 2026-02-10 (evening)_
