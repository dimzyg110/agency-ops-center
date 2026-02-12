# GLASS Messaging Action Plan — Randy's Execution Guide

**Created:** February 12, 2026  
**Purpose:** Prioritized, copy-paste-ready fixes to convert "Maria" (non-technical dispensary owner)  
**Source docs:** GLASS-MESSAGING-REVIEW.md, MASTER-INTEGRATION-PLAN.md, Landing.tsx, Budtender.tsx

---

## 🚨 Top 3 Messaging Violations That Will Make Maria Bounce

### Bounce Trigger #1: "Real-time Price Intelligence for Massachusetts Cannabis Operators"
**Where:** Landing.tsx hero eyebrow text (line ~143)  
**Why it kills:** Maria doesn't think of herself as wanting "price intelligence." She's not a SaaS buyer. She wants to know if the store down the street just dropped their prices. This reads like a B2B pitch deck, not a tool she'd use.

### Bounce Trigger #2: "AI-powered detection," "Multi-Tenant Ready," "Drop-In Widget," "Proximity-based threat scoring"
**Where:** Landing.tsx feature bullet points (lines ~224-231), Budtender.tsx feature cards (lines ~11-42)  
**Why it kills:** Maria reads "proximity-based threat scoring" and thinks "this isn't for me." Every piece of jargon is a tiny exit ramp. Six jargon terms on one page = she's gone. She doesn't know what a "widget" is, doesn't care about "multi-tenant," and "AI-powered" makes her eyes glaze.

### Bounce Trigger #3: The Cue section is a full product pitch inside the landing page
**Where:** Landing.tsx Cue Section (lines ~251-294)  
**Why it kills:** Maria came to learn about price tracking. Halfway down, she hits a completely different product pitch with its own signup form. It breaks the page's narrative rhythm and makes her feel like she landed on a sales catalog, not a tool that solves her problem. She closes the tab.

---

## 🎯 Top 3 Highest-Impact Copy Changes for Conversion

### Impact #1: Rewrite the hero — headline, subhead, CTA button, and sub-CTA
This is the first thing Maria reads. It determines whether she stays or bounces. The current hero is generic SaaS; the rewrite makes it personal and curiosity-driven.

### Impact #2: Replace all CTA buttons across the site with outcome-oriented language
"Get Started Free" is vague — started with what? "See My Market Free" tells Maria exactly what she gets. Every CTA on every page needs this treatment.

### Impact #3: Strip jargon from the landing page feature bullets
The bullet points under each feature section are where Maria decides "this is for someone like me" or "this is too technical." Swapping them from developer-speak to store-owner-speak is the highest ROI edit per character changed.

---

## 📋 Execution Tiers

---

## P0 — DO TONIGHT (Copy swaps, <1 hour, no structural changes)

These are text-only changes in existing components. Find → Replace. Deploy.

---

### P0-1: Landing Page Hero Rewrite

**File:** `src/apps/web/src/pages/Landing.tsx`

#### A. Eyebrow text (line ~143)

**FIND:**
```
Real-time Price Intelligence for Massachusetts Cannabis Operators
```

**REPLACE WITH:**
```
Every dispensary price in Massachusetts. Updated daily.
```

#### B. Main headline (lines ~147-151)

**FIND:**
```tsx
See what your{' '}
<span className="text-glass-accent">competitors</span>{' '}
charge
```

**REPLACE WITH:**
```tsx
Know exactly what the store{' '}
<span className="text-glass-accent">down the street</span>{' '}
charges
```

#### C. Subtext (lines ~155-158)

**FIND:**
```
GLASS tracks every price change across Massachusetts dispensaries. 
Know your market position. React faster. Protect your margins.
```

**REPLACE WITH:**
```
GLASS watches 500+ dispensary menus across the state so you can price smarter, spot threats early, and stop losing sales you didn't even know you were losing.
```

#### D. CTA button text (line ~171)

**FIND:**
```
Get Started Free
```

**REPLACE WITH:**
```
See My Market Free
```

#### E. Sub-CTA text (line ~175)

**FIND:**
```
No credit card required
```

**REPLACE WITH:**
```
Free to use · No credit card · Takes 2 minutes
```

**Expected impact:** HIGH. The hero is 80% of the conversion decision. Maria sees "the store down the street" and thinks "yes, that's exactly what I want to know."

---

### P0-2: Landing Page Feature Bullet Rewrites

**File:** `src/apps/web/src/pages/Landing.tsx`

These are inline strings in the JSX (lines ~218-231). The bullets are inside a map with conditional rendering per feature number.

#### Section 01 (PRICE WIRE) bullets:

**FIND:**
```
Track 100,000+ products across 490+ dispensaries
```
**REPLACE WITH:**
```
Your competitors' prices, right now — flower, edibles, vapes, concentrates
```

**FIND:**
```
Price change alerts within 24 hours
```
**REPLACE WITH:**
```
Get alerted when someone undercuts you — by product, by category, by store
```

**FIND:**
```
Export data to CSV for analysis
```
**REPLACE WITH:**
```
500+ dispensaries tracked daily — from Boston to the Berkshires
```

#### Section 02 (THREAT RADAR) bullets:

**FIND:**
```
New license application detection
```
**REPLACE WITH:**
```
New license alerts — know when someone applies to open near you
```

**FIND:**
```
Price undercut alerts by product
```
**REPLACE WITH:**
```
Price undercut warnings — find out the day it happens, not the month after
```

**FIND:**
```
Proximity-based threat scoring
```
**REPLACE WITH:**
```
Competitive heat map — see who's closing in on your territory
```

#### Section 03 (MORNING BRIEF) bullets — these are already decent, but tighten:

**FIND:**
```
Daily 6 AM email delivery
```
**REPLACE WITH:**
```
Shows up in your inbox at 6 AM — before you open the store
```

**FIND:**
```
Personalized for your market
```
**REPLACE WITH:**
```
Personalized to your locations — not state-level noise
```

**FIND:**
```
Actionable recommendations, not noise
```
**REPLACE WITH:**
```
Plain-English tips — "Lower your Blue Dream by $3" not "market repositioning detected"
```

**Expected impact:** HIGH. These bullets are where Maria decides "this is for someone like me." The current bullets say "we track data." The new bullets say "here's what you get."

---

### P0-3: Landing Page Feature Section Headlines & Descriptions

**File:** `src/apps/web/src/pages/Landing.tsx`

These are in the `features` array (lines ~13-47).

#### Section 01 (PRICE WIRE):

**FIND (headline):**
```
Every price. Every dispensary. Updated daily.
```
**REPLACE WITH:**
```
Know what every competitor charges — updated every day.
```

**FIND (description):**
```
Real-time pricing intelligence across Massachusetts operators. Track competitive positioning, spot market trends, and react before your competitors do.
```
**REPLACE WITH:**
```
You shouldn't have to send someone to your competitor's store to check prices. GLASS watches every menu in the state and shows you what matters: who's cheaper, who's more expensive, and where you're leaving money on the table.
```

#### Section 02 (THREAT RADAR):

**FIND (headline):**
```
Know when a competitor changes before your customers do.
```
**REPLACE WITH:**
```
Someone just applied for a license a mile from your store.
```

**FIND (description):**
```
AI-powered detection of new licenses, price undercuts, and market shifts. Get alerted to threats within hours, not weeks.
```
**REPLACE WITH:**
```
GLASS pulls from CCC licensing data and menu tracking to warn you about new competition, aggressive price drops, and market shifts — before they show up on your P&L.
```

#### Section 03 (MORNING BRIEF):

**FIND (headline):**
```
Your market at 6 AM. No noise.
```
**REPLACE WITH:**
```
Your market briefing, every morning at 6 AM.
```

**FIND (description):**
```
A daily digest of what matters: price movers in your area, new competitive threats, and personalized recommendations delivered to your inbox.
```
**REPLACE WITH:**
```
Open your email, know what changed overnight. The biggest price moves near you, any new competitive threats, and one or two things you should actually do about it. Takes 2 minutes to read.
```

**Expected impact:** MEDIUM-HIGH. The section headlines are second-level scannable content. Maria reads the hero, scrolls, reads these. If they still sound like SaaS marketing, she leaves.

---

### P0-4: Bottom CTA Section Rewrite

**File:** `src/apps/web/src/pages/Landing.tsx` (lines ~301-315)

**FIND:**
```
Start tracking your competitors today
```
**REPLACE WITH:**
```
Stop guessing what the competition is doing.
```

**FIND:**
```
Built for Massachusetts operators. Free forever for the core dashboard.
```
**REPLACE WITH:**
```
Built for Massachusetts dispensary owners. Free plan, real data, nothing to install.
```

**FIND:**
```
Start Free
```
**REPLACE WITH:**
```
See My Market Free
```

**Expected impact:** MEDIUM. This is the bottom-of-page CTA for Maria who scrolled all the way. "Free forever" is a dangerous promise; "Free plan" is honest. "Stop guessing" is more emotionally resonant than "Start tracking."

---

### P0-5: Ecosystem Section Rewrite

**File:** `src/apps/web/src/pages/Landing.tsx`

#### Section header (line ~256):

**FIND:**
```
Intelligence at every touchpoint
```
**REPLACE WITH:**
```
Run a smarter dispensary. One platform.
```

#### Ecosystem item descriptions (in the `ecosystemItems` array, lines ~55-74):

**FIND (GLASS):**
```
Market intelligence for Massachusetts operators.
```
**REPLACE WITH:**
```
See what every competitor charges, every day. Know your market.
```

**FIND (Virtual Budtender):**
```
AI product recommendations on your website — guided Q&A from your real Dutchie menu. Already live at Cannabis Healing.
```
**REPLACE WITH:**
```
Put a product recommender on your website. Customers get guided to the right product from your actual menu. You sell more.
```

**FIND (Cue):**
```
Budtender incentive and training platform — brands fund campaigns, dispensaries run programs, budtenders earn rewards.
```
**REPLACE WITH:**
```
Run budtender incentive programs. Brands pay the rewards. You get a motivated team.
```

**FIND (Delivery):**
```
Cannabis delivery as a service, powered by real-time GLASS data.
```
**REPLACE WITH:**
```
Offer delivery to your customers under your brand. We handle the logistics.
```

**Expected impact:** MEDIUM. Maria scanning the ecosystem section should immediately understand what each product does for HER. The old descriptions describe architecture; the new ones describe outcomes.

---

### P0-6: Budtender Page — Headline & Description Rewrite

**File:** `src/apps/web/src/pages/Budtender.tsx`

#### Headline (line ~74):

**FIND:**
```
An AI budtender on your website that knows your real menu
```
**REPLACE WITH:**
```
Your website recommends the right product to every customer — automatically.
```

#### Description (lines ~76-78):

**FIND:**
```
Customers ask what they want. The widget asks 4 quick questions and recommends 2–4 products from your actual inventory — in stock, at the right price, with explanations that help them buy. Already live at Cannabis Healing.
```
**REPLACE WITH:**
```
Customers land on your site, answer 4 quick questions, and get 2–4 product recommendations from what you actually have in stock. No more lost sales from overwhelmed browsers. Already running at Cannabis Healing.
```

#### CTA button (line ~106):

**FIND:**
```
Get Virtual Budtender
```
**REPLACE WITH:**
```
Put It On My Site — Free
```

**Expected impact:** HIGH for Budtender page. "AI budtender" is an awkward phrase — nobody calls it that. "Widget" is developer jargon. The rewrite speaks Maria's language.

---

### P0-7: Budtender Page — Feature Cards: Cut 2, Rewrite 4

**File:** `src/apps/web/src/pages/Budtender.tsx`

Replace the entire `features` array (lines ~7-42) with:

```tsx
const features = [
  {
    title: 'Guided Product Matching',
    description: 'A customer says "something for sleep, I\'m new to this, under $30." The tool walks them through 4 questions and serves up the best options from your actual shelf — not a generic list.',
    icon: MessageCircle,
  },
  {
    title: 'Always Your Real Inventory',
    description: 'Every recommendation is something you actually carry, actually in stock, at the price on your menu. Syncs with Dutchie daily. No recommending things you don\'t sell.',
    icon: ShoppingBag,
  },
  {
    title: 'On Your Website in a Day',
    description: 'We set it up for you. A small button on your site opens a chat panel. Customers use it like texting. No app download, no account creation, no friction.',
    icon: Code2,
  },
  {
    title: 'Smarter Than a Keyword Search',
    description: 'It doesn\'t just match keywords — it understands what the customer wants and finds the best fit from your whole menu. Explains why each pick is right for them.',
    icon: Sparkles,
  },
];
```

**CUT entirely:**
- "Multi-Tenant Ready" card (Maria doesn't know what a tenant is)
- "GLASS Intelligence" card (tells her about your data backend — she doesn't care)

Also remove the unused imports `Store` and `BarChart3` from line 2.

**Expected impact:** HIGH. These cards are where Maria decides "this is for me" or "this is for developers." Cutting the two jargon cards removes the two biggest exit triggers.

---

### P0-8: Budtender Page — "How It Works" Step Rewrites

**File:** `src/apps/web/src/pages/Budtender.tsx`

Replace the `howItWorks` array (lines ~58-63):

```tsx
const howItWorks = [
  { step: '01', title: 'We connect to your menu', description: 'If you\'re on Dutchie, we pull your products automatically. If not, just send us your menu — we\'ll handle it.' },
  { step: '02', title: 'We set it up with your brand', description: 'Your store name, your vibe, your compliance rules. Done in under an hour.' },
  { step: '03', title: 'It goes on your website', description: 'We send a small code snippet to whoever manages your site. One paste, it\'s live.' },
  { step: '04', title: 'Customers get answers', description: '4 quick questions, 2–4 personalized picks. Real products from your shelf with explanations that actually help.' },
];
```

**Key changes:**
- Step 1: "Export your menu: Pull a CSV from Dutchie" → "We connect to your menu" (Maria doesn't know what a CSV is)
- Step 3: "Paste the widget code: One component in your React app" → "It goes on your website" (Maria doesn't have a React app)

**Expected impact:** MEDIUM-HIGH. The setup steps are where Maria decides "can I actually do this?" The old steps required her to export CSVs and paste code. The new steps say "we handle it."

---

## P1 — THIS WEEK (1-2 hours each, simple component edits)

---

### P1-1: Remove the Full Cue Pitch from the Landing Page

**File:** `src/apps/web/src/pages/Landing.tsx`

**Current (lines ~251-294):** Full Cue section with headline, description, and CueSignup form component.

**Replace the entire Cue Section** with a simple teaser card:

```tsx
{/* Cue Teaser — White Background */}
<section className="bg-white py-24 lg:py-32">
  <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div className="mx-auto max-w-3xl text-center">
      {/* Section Marker */}
      <div className="section-marker mb-6 justify-center">
        <span>04 — COMING SOON</span>
      </div>

      {/* Headline */}
      <h2 className="font-display text-3xl font-medium leading-tight text-glass-black sm:text-4xl lg:text-5xl">
        Reward the budtenders who actually move product.
      </h2>

      {/* Description */}
      <p className="mt-6 text-lg leading-relaxed text-glass-light-muted">
        Cue is a new way to run incentive programs for your floor staff. Brands fund the rewards, you see who performs, budtenders earn $200–500/month on top of their paycheck.
      </p>

      {/* CTA */}
      <div className="mt-8">
        <a
          href="/cue"
          className="group inline-flex items-center gap-2 font-mono text-sm font-medium uppercase tracking-wider text-glass-black transition-colors hover:text-glass-accent"
        >
          Learn More
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </a>
      </div>
    </div>
  </div>
</section>
```

**Why:** The current Cue section breaks the landing page narrative. Maria came to learn about price tracking. A full second-product pitch with its own waitlist form is jarring. The teaser card lets her know it exists without derailing her journey.

**Also:** Remove the `CueSignup` import at the top of the file if it's no longer used on this page.

**Expected impact:** MEDIUM-HIGH. Reducing cognitive load on the landing page keeps Maria focused on the one thing she came for: price intelligence. She can click through to /cue if interested.

**Time estimate:** 30 minutes.

---

### P1-2: Remove "For Developers" Section from Budtender Page

**File:** `src/apps/web/src/pages/Budtender.tsx`

**Delete the entire "Embed code preview" section** (lines ~141-158):

```tsx
{/* DELETE THIS ENTIRE SECTION */}
<section className="py-20">
  <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <p className="font-mono text-xs uppercase tracking-[0.2em] text-glass-accent">For Developers</p>
    <h2 className="mt-2 font-display text-3xl sm:text-4xl">Two lines to install</h2>
    ...
  </div>
</section>
```

**Why:** Maria doesn't have developers. She sees `import { BudtenderWidget }` and React code and thinks "this is not for me." If developers need this, link to docs from the footer.

**Expected impact:** MEDIUM. Removes a major "this isn't for me" signal. Every section on the page should reinforce that Maria can use this product.

**Time estimate:** 10 minutes.

---

### P1-3: Fix Stat Inconsistencies Across All Pages

**Canonical numbers to use everywhere:**

| Stat | Use This | Don't Use |
|------|----------|-----------|
| Dispensaries tracked | **500+** | 490+, 492, 301 |
| Products tracked | **100,000+** | 100K+, 100.8K |
| Total MA cannabis sales | **$8.8 billion** | — |
| Operators | **500+ dispensary menus** | "operators" (confusing) |

**Files to update:**
- `Landing.tsx`: Meta description says "490+ dispensaries" → change to "500+"
- `Landing.tsx`: Feature bullet uses `formatCount(490)` → change to `500`
- `Landing.tsx`: Feature bullet uses `formatCount(100000)` → change to `100000` (keep same)
- `Budtender.tsx`: Integration section says "500+" → already correct ✅
- Any other page referencing dispensary counts → find and fix

**Add fine print to footer** (optional): "GLASS tracks 500+ dispensary menus from Dutchie and Weedmaps listings across Massachusetts."

**Expected impact:** LOW-MEDIUM. Inconsistent numbers erode trust. Maria sees "490" on one page and "301" on another and wonders which is real.

**Time estimate:** 30 minutes.

---

### P1-4: Meta Description Update

**File:** `src/apps/web/src/pages/Landing.tsx` (in the useEffect for SEO, line ~91)

**FIND:**
```
GLASS — Real-time price intelligence for Massachusetts cannabis operators. Track 100,000+ products across 490+ dispensaries. Free to start.
```
**REPLACE WITH:**
```
GLASS — See what every Massachusetts dispensary charges. 100,000+ products across 500+ dispensary menus, updated daily. Free to use.
```

**Expected impact:** LOW-MEDIUM. Affects search click-through rate. "See what every dispensary charges" is more compelling than "real-time price intelligence."

**Time estimate:** 5 minutes.

---

## P2 — NEXT SPRINT (1-2 days each, page restructuring)

---

### P2-1: Add "How It Works" Section to Landing Page

**Insert after the Features section, before the Cue teaser.**

This is the #1 missing structural element. Maria needs to know: "What do I actually DO to use this?" Three simple steps:

```tsx
{/* How It Works — White Background */}
<section className="bg-white py-24 lg:py-32">
  <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div className="text-center mb-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-glass-accent">How It Works</p>
      <h2 className="mt-2 font-display text-3xl font-medium text-glass-black sm:text-4xl">
        Three steps. Two minutes. Free.
      </h2>
    </div>

    <div className="grid gap-12 sm:grid-cols-3">
      <div className="text-center">
        <span className="font-mono text-4xl font-light text-glass-light-muted/40">01</span>
        <h3 className="mt-3 font-display text-xl text-glass-black">Sign up free</h3>
        <p className="mt-2 text-glass-light-muted">
          Enter your email, tell us your dispensary name and location. Two minutes, no credit card.
        </p>
      </div>
      <div className="text-center">
        <span className="font-mono text-4xl font-light text-glass-light-muted/40">02</span>
        <h3 className="mt-3 font-display text-xl text-glass-black">See your market</h3>
        <p className="mt-2 text-glass-light-muted">
          We show you what competitors near you charge — by product, by category. Updated daily from real dispensary menus across Massachusetts.
        </p>
      </div>
      <div className="text-center">
        <span className="font-mono text-4xl font-light text-glass-light-muted/40">03</span>
        <h3 className="mt-3 font-display text-xl text-glass-black">Make smarter moves</h3>
        <p className="mt-2 text-glass-light-muted">
          Get alerted when a competitor drops a price, spot products where you're leaving margin on the table, and see threats before they become problems.
        </p>
      </div>
    </div>
  </div>
</section>
```

**Expected impact:** HIGH. This is the bridge between "I'm interested" and "I'll sign up." Without it, Maria has to imagine what actually happens when she clicks the button.

**Time estimate:** 1-2 hours (add section, test responsive, deploy).

---

### P2-2: Add Trust/Proof Section to Landing Page

**Insert after "How It Works," before Ecosystem section.**

The current page has no social proof (correctly — no fake numbers). But it also has no data proof. This section uses the PRODUCT as the proof:

```tsx
{/* Trust Section — Light Background */}
<section className="border-y border-glass-light-muted/20 bg-[#FCFAF8] py-24 lg:py-32">
  <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
    <h2 className="font-display text-3xl font-medium text-glass-black sm:text-4xl">
      Real data. Not guesswork.
    </h2>
    <p className="mt-6 text-lg leading-relaxed text-glass-light-muted">
      GLASS doesn't rely on surveys, self-reported numbers, or estimates. We pull prices from{' '}
      <strong className="text-glass-black">500+ Massachusetts dispensary menus every day</strong> — that's{' '}
      <strong className="text-glass-black">100,000+ products</strong> tracked with real shelf prices.
    </p>
    <p className="mt-4 text-lg leading-relaxed text-glass-light-muted">
      Cross-referenced with official Cannabis Control Commission data, including transfer pricing, licensing, and the{' '}
      <strong className="text-glass-black">$8.8 billion</strong> in cannabis sales Massachusetts has processed since legalization.
    </p>
    <p className="mt-4 text-lg leading-relaxed text-glass-light-muted">
      You're not looking at projections. You're looking at what's actually on the shelf, right now.
    </p>
  </div>
</section>
```

**Expected impact:** HIGH. This is the trust layer Maria needs. She's skeptical of software companies. "500+ dispensary menus every day" and "$8.8 billion" and "official Cannabis Control Commission" — these are proof this is real.

**Time estimate:** 1-2 hours.

---

### P2-3: Rewrite the Delivery Page

The current delivery page says almost nothing. Maria can't tell what the service actually IS. Full rewrite needed (see GLASS-MESSAGING-REVIEW.md Part 1, Section 4 for copy).

Key elements:
- New headline: "Offer delivery to your customers — without getting a delivery license."
- 3-step "How it works" section
- "Why this matters" section explaining the 27-license bottleneck
- "Who it's for" section
- Remove "490+ operators tracked statewide" stat (irrelevant here)
- Remove "Location intelligence with operator control" (meaningless phrase)
- New CTA: "Get On the List — We'll Let You Know When It's Ready"

**Expected impact:** MEDIUM. Lower traffic page, but critically important for Maria who's considering delivery.

**Time estimate:** 2-4 hours.

---

### P2-4: Rewrite the Cue Page

Key changes:
- Replace "missions" with "goals" or "incentives" throughout
- Lead with "Your budtenders sell harder when there's something in it for them"
- Cut "GLASS-Powered Targeting" card (Maria doesn't need data backend details)
- Condense the "For Budtenders" section to a small callout box
- New CTA: "Start a Free Incentive Program"

**Expected impact:** MEDIUM. Important for the ecosystem story but Cue is still coming-soon.

**Time estimate:** 3-4 hours.

---

### P2-5: Fix Market Page Issues

Key changes:
- Fix or remove "Premium Data Teaser" broken boxes ("No data available" looks broken)
- Add plain-English headlines above every chart/table
- New headline: "The Massachusetts cannabis market, in real numbers."
- Fix stat inconsistencies to match canonical 500+ number
- New CCC × GLASS table intro: "What wholesale costs vs. what the shelf says."

**Expected impact:** MEDIUM. The market page is a credibility page. If it looks broken (empty teaser boxes), it undermines everything.

**Time estimate:** 2-3 hours.

---

## P3 — FULL REDESIGN (1-2 weeks)

---

### P3-1: Complete Maria-Optimized Homepage Rewrite

**Architecture:**
1. **Hero:** One problem, one promise. "Know exactly what the store down the street charges."
2. **How It Works:** Three steps. Sign up → See your market → Act on it.
3. **Trust/Data Proof:** "Real data. Not guesswork." + stats.
4. **The Four Capabilities:** GLASS, Budtender, Cue, Delivery — each with one-sentence hooks (teaser cards, not full pitches).
5. **Bottom CTA:** "Stop guessing what the competition is doing."

**Key principle:** Do NOT sell the ecosystem on the homepage. Sell GLASS. That's the door. Everything else follows inside the dashboard.

### P3-2: Unified Page Template Across All Product Pages

All product pages (Budtender, Cue, Delivery) should share the same layout DNA:
- Same section structure: Hero → Demo/Visual → Features (3-4 cards) → How It Works → CTA
- Same CTA button styling
- Same typography and spacing
- Small "Part of GLASS" connection aside (not a pitch)

### P3-3: Cross-Product Dashboard Hints

After the website pages convert Maria, the dashboard should introduce other products contextually:
- When looking at pricing data → hint about Virtual Budtender
- When looking at product performance → hint about Cue incentives
- When seeing competitors with delivery → hint about Delivery service

**Rules:** One hint per page max. Always tied to her data. Always dismissable. Never the first thing she sees.

### P3-4: Newsletter Page Fix

- **Remove** "Join 500+ MA operators" (violates anti-pattern rule — no fake social proof)
- **Replace with:** "Weekly · Free · 2-minute read"
- Replace third sample bullet: "Review Metrc tag accuracy to reduce compliance risk" → "Check if your top 5 sellers are priced above or below the stores near you"

---

## 📊 Summary Table

| ID | Task | Priority | Time | Impact | Page |
|----|------|----------|------|--------|------|
| P0-1 | Hero rewrite (eyebrow, headline, subhead, CTA, sub-CTA) | **P0** | 15 min | 🔴 Critical | Landing |
| P0-2 | Feature bullet rewrites (all 9 bullets) | **P0** | 15 min | 🔴 Critical | Landing |
| P0-3 | Feature section headlines & descriptions | **P0** | 15 min | 🟡 High | Landing |
| P0-4 | Bottom CTA section rewrite | **P0** | 5 min | 🟡 High | Landing |
| P0-5 | Ecosystem card rewrites | **P0** | 10 min | 🟡 High | Landing |
| P0-6 | Budtender headline, description, CTA | **P0** | 10 min | 🔴 Critical | Budtender |
| P0-7 | Budtender feature cards: cut 2, rewrite 4 | **P0** | 15 min | 🔴 Critical | Budtender |
| P0-8 | Budtender "How It Works" step rewrites | **P0** | 10 min | 🟡 High | Budtender |
| P1-1 | Replace Cue full pitch with teaser card | **P1** | 30 min | 🟡 High | Landing |
| P1-2 | Remove "For Developers" section | **P1** | 10 min | 🟡 High | Budtender |
| P1-3 | Fix stat inconsistencies (500+ everywhere) | **P1** | 30 min | 🟢 Medium | All |
| P1-4 | Meta description update | **P1** | 5 min | 🟢 Medium | Landing |
| P2-1 | Add "How It Works" 3-step section | **P2** | 2 hrs | 🔴 Critical | Landing |
| P2-2 | Add Trust/Data Proof section | **P2** | 2 hrs | 🔴 Critical | Landing |
| P2-3 | Rewrite Delivery page | **P2** | 3 hrs | 🟢 Medium | Delivery |
| P2-4 | Rewrite Cue page (kill "missions" jargon) | **P2** | 4 hrs | 🟢 Medium | Cue |
| P2-5 | Fix Market page (broken boxes, headlines) | **P2** | 3 hrs | 🟢 Medium | Market |
| P3-1 | Complete Maria-optimized homepage | **P3** | 1 week | 🔴 Critical | Landing |
| P3-2 | Unified page template | **P3** | 1 week | 🟡 High | All |
| P3-3 | Cross-product dashboard hints | **P3** | 1 week | 🟡 High | Dashboard |
| P3-4 | Newsletter page fix | **P3** | 30 min | 🟢 Medium | Newsletter |

---

## ✅ Tonight's Checklist (P0 items, in order)

1. [ ] Open `Landing.tsx` — do P0-1 through P0-5 (all copy swaps, ~45 min)
2. [ ] Open `Budtender.tsx` — do P0-6 through P0-8 (all copy swaps, ~25 min)
3. [ ] Build locally, check for rendering issues
4. [ ] Commit with message: `fix(copy): Maria-optimized messaging — hero, features, CTAs, budtender`
5. [ ] Deploy
6. [ ] Read the live pages on your phone (Maria reads from her phone)

**Total time for P0: ~70 minutes.**

---

## 🚫 Anti-Pattern Enforcement List

These must NEVER appear on any customer-facing page:

| ❌ Don't Say | ✅ Say Instead |
|---|---|
| "Real-time pricing intelligence" | "See what competitors charge" |
| "AI-powered" (anything) | Describe what it does, not how |
| "Multi-tenant ready" | Remove entirely |
| "Widget" | "the tool," "the product recommender," "the chat button" |
| "Export data to CSV" | "Download your data" or remove |
| "Proximity-based threat scoring" | "See who's opening near you" |
| "Join 500+ operators" | Remove (no fake social proof) |
| "Free forever" | "Free plan" or "Free to use" |
| Feature comparison grids | Never add — not Maria's language |
| Charts without headlines | Every chart needs a plain-English insight above it |
| "Missions" (on Cue page) | "Goals" or "Incentives" |
| "Intelligence at every touchpoint" | "Run a smarter dispensary" |

---

*This document is your execution guide. The P0 items are copy-paste ready. Open the files, find the strings, replace them, deploy. Maria will thank you by signing up.*
