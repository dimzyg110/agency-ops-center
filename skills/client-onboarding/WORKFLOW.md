# New Client Pipeline

**Trigger:** Lead identified or inbound inquiry received.
**Goal:** Go from "who is this business?" → deep research → multi-agent strategic plans → proposal → formal client.

---

## Phase 1: Lead Intake

**Who:** Randy or COO
**Time:** 5 min

1. Create lead file: `clients/_leads/<business-name>/LEAD.md`
2. Fill in basics:

   ```markdown
   # [Business Name]

   - Website:
   - Instagram:
   - Location:
   - Industry/Niche:
   - How they found us:
   - Initial ask:
   - Randy's gut feeling:
   ```

3. Status: `LEAD`

---

## Phase 2: Deep Dive Research (Multi-Agent)

**Who:** COO spawns 5 research agents
**Time:** ~30-60 min agent time, then Randy reviews

### Spawn Research Agents

Each agent gets a specialized, detailed prompt. All agents share this context header:

```
CONTEXT (include in every agent prompt):
Business: [name]
Website: [url]
Instagram: [handle]
Location: [city, state]
Industry: [niche]
Initial ask: [what they came to us for]
Randy's gut: [his initial impression]

You are a senior analyst at Roviq, a cannabis marketing, data, and consulting agency
based in Massachusetts. Roviq's approach: we don't sell — we build things so good
that operators come to us. We specialize in cinematic content, data intelligence,
growth strategy, and digital products for cannabis businesses.

Your output must be specific, data-backed where possible, and opinionated.
No filler. No "this is a great opportunity." Give the real picture — what's
working, what's broken, what's missing, and what would move the needle.
```

---

#### Agent 1: Website & Digital Presence Audit

```
[INSERT CONTEXT HEADER]

MISSION: Perform a comprehensive audit of [business]'s website and digital presence.

STEP 1 — SCRAPE & CATALOG
Use Firecrawl (or browser tools) to scrape the full website. Catalog:
- Total page count and sitemap structure
- Every product/service listed with descriptions and pricing (if visible)
- All CTAs and conversion paths (forms, phone numbers, booking links, etc.)
- Menu/navigation structure
- Footer links (social, legal, third-party integrations)
- Any blog, resources, or content hub

STEP 2 — TECHNICAL ANALYSIS
- Page load speed (use Lighthouse or similar metrics if possible)
- Mobile responsiveness — does it actually work or just "exist" on mobile?
- Tech stack: what platform (Shopify, WordPress, Dutchie, custom)? Any analytics installed?
- SSL, security headers, broken links
- ADA accessibility basics (alt text, contrast, keyboard navigation)

STEP 3 — DESIGN & UX EVALUATION
Score each 1-10 with specific reasoning:
- Visual design quality (is it premium or does it look like a 2018 template?)
- Brand consistency (colors, typography, imagery — is there a system or is it random?)
- Information architecture (can a first-time visitor find what they need in <3 clicks?)
- Trust signals (reviews, certifications, press mentions, team photos, about page)
- Imagery quality (stock photos? real photos? AI-generated? nothing?)
- Call-to-action clarity (does the user know what to do next on every page?)

STEP 4 — CONVERSION PATH ANALYSIS
- Map the primary user journey from landing page → desired action
- Identify friction points (too many steps, confusing navigation, dead ends)
- Is there any lead capture? Email signup? SMS?
- What happens after conversion? Any follow-up automation visible?
- Compare conversion path to top 2-3 competitors in their market

STEP 5 — COMPETITIVE COMPARISON
Find 3 direct competitors' websites in the same market/location. For each:
- URL, design quality (1-10), mobile experience, unique features
- What do competitors do BETTER than [business]?
- What does [business] do better than competitors?

STEP 6 — VERDICT
Write a blunt summary:
- Overall grade (A-F) with justification
- Top 3 things that are working
- Top 3 things that are actively hurting them
- Single biggest missed opportunity
- Estimated effort to fix (light refresh vs. full rebuild)

OUTPUT FORMAT: Use headers for each step. Include screenshots/URLs where relevant.
Save to: clients/_leads/<name>/research/website-audit.md
```

---

#### Agent 2: Social Media & Content Audit

```
[INSERT CONTEXT HEADER]

MISSION: Audit [business]'s entire social media presence and content strategy.

STEP 1 — PLATFORM INVENTORY
Check ALL platforms. For each active platform, document:
- Handle/URL, follower count, following count
- Account creation date (approximate)
- Bio text (exact copy)
- Link in bio (where does it go?)
- Verified? Business account?
- Is it actually active or abandoned?

Platforms to check: Instagram, TikTok, Facebook, X/Twitter, YouTube,
LinkedIn (company page), Pinterest, Threads, Snapchat

STEP 2 — CONTENT ANALYSIS (Last 30 Posts per Platform)
For each active platform, analyze the most recent 30 posts:
- Posting frequency (posts per week, any patterns?)
- Content types breakdown (% photo, video, carousel, stories, reels)
- Content themes/pillars (what topics do they repeatedly cover?)
- Visual style (cohesive or random? branded templates or one-offs? UGC?)
- Caption style (long-form storytelling? short? emoji-heavy? hashtag-stuffed?)
- Hashtag strategy (relevant? too many? branded hashtags?)
- Video production quality (professional, iPhone, AI-generated, CGI?)

STEP 3 — ENGAGEMENT DEEP DIVE
- Average likes, comments, shares per post (calculate from last 30)
- Engagement rate (engagement / followers × 100)
- Which content types get the MOST engagement?
- Which content types FLOP?
- Comment sentiment — are people asking questions? Praising? Complaining?
- Does the brand respond to comments? How fast? What tone?
- Any viral or breakout posts? What made them work?

STEP 4 — AUDIENCE ANALYSIS
- Who appears to follow them? (demographics visible from commenters)
- Are followers real or purchased? (engagement ratio vs. follower count — if <1% on 10K+, suspicious)
- Local vs. national audience?
- Are they attracting their ideal customer or random followers?

STEP 5 — CONTENT GAPS & OPPORTUNITIES
- What content are competitors posting that [business] ISN'T?
- What's trending in their niche that they're missing?
- Are they using platform-specific features? (Reels, Stories, Lives, Guides, Shops)
- Could they leverage UGC, customer spotlights, behind-the-scenes?
- Is there educational content opportunity? (budtender tips, product education, industry news)
- Any partnership/collab content visible?

STEP 6 — COMPETITIVE BENCHMARKS
Find 3 competitors with strong social presence. For each:
- Follower counts across platforms
- Posting frequency, engagement rates
- What they do BETTER (be specific — "better photos" isn't enough, explain WHY)
- Steal-worthy tactics that [business] could adapt

STEP 7 — VERDICT
- Overall social grade (A-F) per platform
- The #1 content type they should be creating MORE of (with examples)
- The #1 thing they should STOP doing
- Quick win: one change they could make this week to improve
- 90-day content strategy recommendation (high level)

OUTPUT FORMAT: Use headers for each step. Include post URLs for specific examples.
Save to: clients/_leads/<name>/research/social-audit.md
```

---

#### Agent 3: SEO, Local Search & Paid Advertising Audit

```
[INSERT CONTEXT HEADER]

MISSION: Audit [business]'s search engine presence, local search, and any paid advertising.

STEP 1 — GOOGLE BUSINESS PROFILE (GBP)
- Is there a claimed, active Google Business Profile?
- Name, address, phone (NAP consistency with website?)
- Category selections (primary + secondary)
- Business hours, holiday hours updated?
- Photos: count, quality, recency (last upload date)
- Google reviews: total count, average rating
- Read the 10 most recent reviews — what do customers praise? Complain about?
- Response rate to reviews — are they replying? What tone?
- Q&A section — any questions posted? Answered?
- Posts on GBP — are they using Google Posts? Frequency?
- Attributes (accessibility, amenities, payments, cannabis-specific attributes)

STEP 2 — ORGANIC SEO ANALYSIS
- What keywords does the site currently rank for? (use search results, SERPs)
- Are they ranking for their own brand name?
- Local keyword presence: "[business type] in [city]" — where do they show up?
- Page title tags — are they optimized or generic ("Home", "Products")?
- Meta descriptions — written or auto-generated?
- Header structure (H1, H2) — logical hierarchy or random?
- Internal linking — do pages link to each other logically?
- Blog/content — does it exist? How many posts? Are they keyword-targeted?
- URL structure — clean (/products/flower) or messy (/page?id=12345)?
- Image alt text — present? Descriptive?
- Schema markup — any structured data? (LocalBusiness, Product, FAQ)
- Sitemap.xml and robots.txt — properly configured?

STEP 3 — BACKLINK & DOMAIN ANALYSIS
- Domain age (approximate)
- Any notable backlinks? (press mentions, directory listings, industry sites)
- Are they listed on key cannabis directories? (Leafly, Weedmaps, Dutchie, etc.)
- Directory listing consistency — is NAP the same everywhere?
- Any toxic or spammy backlinks visible?

STEP 4 — PAID ADVERTISING AUDIT
Note: Cannabis advertising is heavily restricted. Check what they're doing:
- Google Ads: Any search ads running? (search their brand + competitor terms)
- Meta Ads: Check Meta Ad Library for any active campaigns
- Weedmaps/Leafly/Dutchie paid placements — are they boosting listings?
- Any programmatic or display ads? (check via browsing industry sites)
- Direct mail, billboards, events, sponsorships (search for mentions)
- If NO paid ads: is this a huge gap or smart given regulations?

STEP 5 — LOCAL COMPETITION
For the top 3 local competitors:
- GBP: review count, rating, photo count, post frequency
- Organic rankings: what keywords do THEY rank for?
- Are competitors running ads that [business] isn't?
- Map pack: who appears in the local 3-pack for key terms?

STEP 6 — KEYWORD OPPORTUNITY MAP
Build a table with 15-20 target keywords:

| Keyword | Monthly Volume Est. | Current Position | Difficulty | Priority |
|---------|-------------------|------------------|------------|----------|
| ...     | ...               | ...              | ...        | ...      |

Prioritize: high intent + achievable difficulty + relevant to revenue

STEP 7 — VERDICT
- SEO grade (A-F)
- Local search grade (A-F)
- Paid ads grade (A-F, or N/A with reasoning)
- Top 3 SEO quick wins (things fixable in 1-2 weeks)
- Top 3 long-term SEO plays (3-6 month investment)
- Estimated organic traffic opportunity if SEO is done right

Save to: clients/_leads/<name>/research/seo-audit.md
```

---

#### Agent 4: Competitive Landscape & Market Position

```
[INSERT CONTEXT HEADER]

MISSION: Map the full competitive landscape and [business]'s position within it.

STEP 1 — MARKET DEFINITION
- Define the exact market: geographic boundaries, customer segments, product categories
- Market size and trends (cannabis in [location] — growing? consolidating? struggling?)
- Regulatory environment (any recent license changes, new laws, local restrictions?)
- Consumer trends (what are buyers in this market gravitating toward?)

STEP 2 — COMPETITOR IDENTIFICATION
Identify 5-7 DIRECT competitors (same city/region, same type of business).
Identify 3-5 ASPIRATIONAL competitors (best-in-class, any market, who they SHOULD look like).

For each competitor, build a profile:
- Name, Location, Website, Instagram
- What they sell / what services they offer
- Estimated years in business
- Online presence score (1-10)
- Unique value proposition (what makes THEM different?)
- Visible weaknesses
- What [business] can learn from them

STEP 3 — COMPETITIVE POSITIONING MAP
Create a 2x2 positioning map. Suggested axes:
- X-axis: Price point (budget → premium)
- Y-axis: Brand sophistication (basic → elevated)

Place [business] and all competitors on the map. Where's the white space?

STEP 4 — DIFFERENTIATOR ANALYSIS
Answer honestly:
- What does [business] currently do BETTER than anyone in their market?
- What do they do WORSE?
- What do they do the SAME as everyone else (commodity zone — dangerous)?
- What does NO ONE in the market do? (gap = opportunity)
- If you removed their name, could a customer tell them apart from competitors?

STEP 5 — PRICING & PRODUCT COMPARISON
If pricing is visible (menus, websites, listings):
- How does [business] price vs. competitors?
- Product/service range — broader or narrower?
- Any unique products or exclusive partnerships?
- Loyalty programs, rewards, subscription models?

STEP 6 — INDUSTRY & MACRO TRENDS
- What's happening in the broader cannabis market that affects this business?
- New entrants expected? Market consolidation?
- Technology shifts (delivery, AI, e-commerce, app integrations)?
- Consumer behavior changes (preferences, purchasing patterns)?
- Regulatory pipeline (anything coming that changes the game)?

STEP 7 — STRATEGIC POSITION VERDICT
- Where does [business] sit today? (leader, follower, niche, struggling?)
- What is their defensible competitive advantage? (be honest — they may not have one)
- What's the #1 move that would shift their market position?
- Biggest threat in the next 12 months
- Biggest opportunity in the next 12 months

Save to: clients/_leads/<name>/research/competitive-analysis.md
```

---

#### Agent 5: Revenue Model, Partnerships & Growth Opportunities

```
[INSERT CONTEXT HEADER]

MISSION: Evaluate [business] as if you're a fractional CMO doing a discovery call.
Your goal: figure out every way Roviq could help this business grow revenue.

STEP 1 — CURRENT REVENUE MODEL
Reverse-engineer how this business makes money:
- Primary revenue streams (product sales, services, subscriptions, etc.)
- Revenue mix estimate (what % from each stream?)
- Average transaction value (if estimable from menu/pricing)
- Customer frequency (daily regulars? monthly visits? one-time?)
- Customer acquisition cost (how are they getting customers today?)
- Visible revenue optimization (upsells, bundles, loyalty, tiered pricing?)

STEP 2 — CUSTOMER JOURNEY MAPPING
Map how a customer goes from "never heard of them" → "paying customer" → "repeat buyer":
- Discovery: How do people find this business? (Google, Instagram, word of mouth, Weedmaps?)
- Consideration: What convinces them to choose this over competitors?
- Purchase: What's the buying experience? (online, in-store, delivery?)
- Retention: What brings them back? (loyalty program, quality, convenience, nothing?)
- Advocacy: Do customers refer others? Any referral program? Are they leaving reviews?
- Identify WHERE the journey breaks: biggest drop-off point

STEP 3 — PARTNERSHIP & CHANNEL OPPORTUNITIES
- Who are their natural partners? (other brands, complementary businesses, events, media)
- Are there partnership channels they're not using? (wholesale, white-label, co-marketing)
- For dispensaries: which brands/cultivators should they be featuring? Why?
- For brands: which retailers should they be in? Any exclusive opportunities?
- Events, pop-ups, collaborations in their market
- Influencer or creator partnerships (who in their niche has the audience they want?)

STEP 4 — PRODUCT/SERVICE EXPANSION
What SHOULD this business be doing that they're not?
- New products or product lines
- New services (delivery, subscription boxes, events, education)
- Digital products (merch, content, NFTs, apps, community)
- B2B opportunities (wholesale, platform licensing, data)
- Adjacencies (what else does their customer buy that they could provide?)

STEP 5 — MARKETING & GROWTH LEVERS
Evaluate each channel for this specific business (not generic advice):
- Content marketing: What content would their audience actually consume?
- Email/SMS: Do they have a list? What would they send? What automations?
- SEO: What's the organic search opportunity? (reference SEO audit)
- Social: What's the growth path? (reference social audit)
- Paid: What paid channels are available given regulations?
- Community: Is there a community play? (Discord, IRL events, loyalty tiers?)
- Referral: What would a referral program look like for them specifically?

STEP 6 — ROVIQ SERVICE FIT
Be specific about WHAT Roviq would do and WHY:
- Which Roviq services does this business actually need?
- What's the estimated value of each service to their bottom line?
- What's the quick win that proves Roviq's value in week 1?
- What's the long-term engagement that keeps them paying monthly?
- What's the Roviq service they DON'T need? (be honest — don't upsell for upselling's sake)

STEP 7 — REVENUE OPPORTUNITY SUMMARY
| Opportunity | Revenue Impact | Effort | Timeline | Roviq Role |
|-------------|---------------|--------|----------|------------|
| ...         | ...           | ...    | ...      | ...        |

Top 3 recommendations ranked by: (Revenue Impact × Likelihood of Success) ÷ Effort

Save to: clients/_leads/<name>/research/growth-opportunities.md
```

---

### Model Assignments (diverse perspectives):

| Agent | Track | Primary Model | Fallback | Rationale |
|-------|-------|--------------|----------|-----------|
| 1 | Website & Digital Presence | `google-antigravity/claude-opus-4-6-thinking` | `google-antigravity/claude-opus-4-6` | Deepest reasoning for technical audit |
| 2 | Social Media & Content | `google-antigravity/gemini-3-pro-high` | `google-antigravity/gemini-3-flash` | Visual/creative reasoning for content analysis |
| 3 | SEO, Local Search & Paid Ads | `openai/gpt-5.2-codex` | `google-antigravity/claude-opus-4-6` | Structured data analysis, keyword maps |
| 4 | Competitive Landscape | `google-antigravity/claude-opus-4-6` | `nvidia/moonshotai/kimi-k2.5` | Fast synthesis across many sources |
| 5 | Revenue Model & Growth | `nvidia/moonshotai/kimi-k2.5` | `google-antigravity/claude-opus-4-6-thinking` | Different architecture = fresh perspective |

**Batching (max 2 Antigravity at a time):**
- Batch 1: Agent 1 (Antigravity) + Agent 2 (Antigravity) + Agent 3 (OpenAI)
- Batch 2: Agent 4 (Antigravity) + Agent 5 (NVIDIA)

**Principle:** 4 different architectures (Claude, Gemini, GPT, Kimi), 3 providers, never >2 Antigravity concurrent.

---

## Phase 3: Randy Reviews Research

**Who:** Randy
**Time:** 15-30 min

1. COO compiles a summary of all research into `clients/_leads/<name>/RESEARCH-SUMMARY.md`
2. Randy reviews and annotates:
   - ✅ Agree
   - ❌ Wrong / Irrelevant
   - 💡 Additional context or insights
3. Randy writes 2-3 sentences: "Here's what I think the play is..."

---

## Phase 4: Multi-Agent Strategy Plans

**Who:** COO spawns 3 strategy agents (SAME prompt, different models)
**Time:** ~30-60 min agent time

### Core Strategy Prompt (given to ALL 3 agents):

```
CONTEXT:
Business: [name]
Website: [url]
Location: [city, state]
Industry: [niche]

You are a senior strategist at Roviq — a cannabis marketing, data, and consulting
agency. Randy Torres (Roviq's founder) is evaluating [business] as a potential
client. Your job: create the most compelling, specific, actionable growth plan
that demonstrates exactly how Roviq would transform this business.

Read EVERYTHING in clients/_leads/<name>/research/
Read Randy's notes in clients/_leads/<name>/RESEARCH-SUMMARY.md

DO NOT write generic marketing advice. Every recommendation must be:
1. Specific to THIS business (reference their actual data, competitors, gaps)
2. Tied to a revenue outcome (how does this make or save them money?)
3. Estimated in cost AND return
4. Sequenced (what to do first, second, third)

YOUR PLAN MUST INCLUDE:

## Executive Summary (3-5 sentences)
- What's the core insight? What's the big play?
- Why is NOW the right time?

## Current State Diagnosis
- Grade their business across 5 dimensions (1-10 each):
  Brand, Digital Presence, Marketing, Revenue Optimization, Customer Experience
- The #1 thing killing their growth right now

## The Transformation Plan

### Quick Wins (First 30 Days) — Low effort, high visibility
- Specific actions that show results fast
- These build trust and prove Roviq's value
- Include expected outcomes per action

### Foundation Layer (Days 30-60) — Build the systems
- Website (redesign/rebuild? specific pages? new features?)
- Brand (refresh? full overhaul? just tighten up?)
- Content engine (what to produce, how often, which platforms)
- Data & analytics (what to track, what tools to set up)
- Include estimated Roviq pricing for each deliverable

### Growth Layer (Days 60-90) — Scale what works
- Paid acquisition (what's possible given regulations?)
- Partnerships (specific partners to approach, why, what the deal looks like)
- New revenue streams (products, services, channels)
- Community building (if applicable)
- Include projected ROI estimates

### Long-Term Vision (90 Days+)
- Where could this business be in 6 months with Roviq?
- What does the endgame look like?
- Any moonshot ideas worth mentioning?

## What They Should STOP Doing
- Be direct. If something is wasting their time or money, say so.

## Proposed Pricing

### Tier 1: Growth Sprint — $3,000 (one-time, 14 days)
[Specify exactly what's included for THIS business]

### Tier 2: Monthly Partnership — $X/month
[Specify ongoing deliverables, meeting cadence, what they get]

### Tier 3: Full Strategic Partner — $X/month
[Specify the all-in package — strategy, execution, reporting]

## Why Roviq (Not a Generic Agency)
- What makes Roviq uniquely positioned to help THIS business?
- Reference specific Roviq capabilities (data intelligence, AI content, cannabis expertise)
- What would a generic agency miss that Roviq catches?

Save to: clients/_leads/<name>/plans/plan-[agent-number].md
```

### Models:

| Plan | Primary Model | Fallback | Rationale |
|------|--------------|----------|-----------|
| Plan 1 | `google-antigravity/claude-opus-4-6-thinking` | `google-antigravity/claude-opus-4-6` | Deepest strategic reasoning |
| Plan 2 | `openai/gpt-5.2-codex` | `google-antigravity/claude-opus-4-6` | Balanced execution focus |
| Plan 3 | `google-antigravity/gemini-3-pro-high` | `nvidia/moonshotai/kimi-k2.5` | Creative/unconventional angles |

---

## Phase 5: Final Plan Synthesis

**Who:** Randy reviews all 3 plans → Claude Opus 4.6 synthesizes
**Time:** 20-30 min

1. Randy reviews all 3 plans and marks what to keep/drop from each
2. Claude Opus 4.6 synthesizes Randy's picks into ONE final plan:

   ```
   Read all 3 strategic plans in clients/_leads/<name>/plans/
   Read Randy's annotations and selections.

   Create the FINAL proposal for [business]. This is what Randy will actually
   present. It needs to:
   - Lead with the insight (not "we're a marketing agency")
   - Show you understand THEIR business deeply (reference specific data points)
   - Make the ROI case clearly (they spend $X, they get $Y)
   - Include 3 pricing tiers with clear scope per tier
   - Feel premium, not salesy — this is a strategic partnership pitch
   - End with a clear next step (not "let us know!")

   Tone: Confident, data-backed, direct. Like a McKinsey deck meets a startup pitch.

   Save to: clients/_leads/<name>/PROPOSAL-DRAFT.md
   ```

3. Status: `PROPOSAL`

---

## Phase 6: Proposal → Formal Client

**Who:** Randy (human conversation)

1. Randy presents proposal to client
2. If accepted:
   - Move `clients/_leads/<name>/` → `clients/<name>/`
   - Create `clients/<name>/BRIEF.md` from the approved plan
   - Create `clients/<name>/roadmap.md` with milestones
   - Update `CLIENTS.md` with new client playbook
   - Update `DASHBOARD.md` with active projects
   - Status: `ACTIVE`

---

## File Structure

```
clients/_leads/<business-name>/
├── LEAD.md                  # Initial info
├── RESEARCH-SUMMARY.md      # COO's compiled summary + Randy's notes
├── research/
│   ├── website-audit.md
│   ├── social-audit.md
│   ├── seo-audit.md
│   ├── competitive-analysis.md
│   └── growth-opportunities.md
├── plans/
│   ├── plan-1.md            # Claude Opus
│   ├── plan-2.md            # Claude Sonnet
│   └── plan-3.md            # Gemini
└── PROPOSAL-DRAFT.md        # Final synthesized proposal
```

---

## Quick Reference

| Phase              | Who               | Output              | Approver |
| ------------------ | ----------------- | ------------------- | -------- |
| 1. Lead Intake     | Randy/COO         | LEAD.md             | —        |
| 2. Deep Dive       | 5 research agents | research/\*.md      | —        |
| 3. Research Review | Randy             | RESEARCH-SUMMARY.md | Randy    |
| 4. Strategy Plans  | 3 strategy agents | plans/\*.md         | —        |
| 5. Final Synthesis | Opus 4.6 + Randy  | PROPOSAL-DRAFT.md   | Randy    |
| 6. Close           | Randy             | Move to clients/    | Client   |
