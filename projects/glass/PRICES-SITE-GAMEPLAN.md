# GLASS Prices — Complete Product & Design Blueprint

**glassintel.xyz/prices**
**Date:** February 14, 2026
**Version:** 1.0 — The Only Draft That Matters
**Author:** Product Vision Team

---

> "The best interface is the one you don't notice. You just see the price."

---

## Table of Contents

1. [The Thesis](#1-the-thesis)
2. [First Impression — The Landing](#2-first-impression--the-landing)
3. [The Core Experience](#3-the-core-experience)
4. [The Controversy Play](#4-the-controversy-play)
5. [Visual Language](#5-visual-language)
6. [The Anti-Pattern Rules](#6-the-anti-pattern-rules)
7. [Technical Architecture](#7-technical-architecture)
8. [The Virality Engine](#8-the-virality-engine)
9. [Revenue Path (V2)](#9-revenue-path-v2)
10. [Wireframes & Layout Descriptions](#10-wireframes--layout-descriptions)
11. [The Name & Tagline](#11-the-name--tagline)
12. [Launch Playbook](#12-launch-playbook)

---

## 1. The Thesis

Massachusetts cannabis buyers have been getting ripped off — not by one store, but by opacity. The same Fernway cart is $35 at one dispensary and $55 at another 4 miles away. The buyer has no way to know this without driving to both, opening two different apps, and comparing screenshots they took 20 minutes apart.

**GLASS Prices is Google Flights for weed.** One search, every store, sorted by price. That's it.

We are not a dispensary. We are not a review site. We are not a cannabis brand. We are a **price tool**. We exist to answer one question:

> **"Where's the cheapest [product] near me?"**

Every design decision, every pixel, every word on this site must trace back to that question. If it doesn't help someone find a cheaper price faster, it doesn't ship.

### Why This Works Now

- **74% price drop** in MA cannabis over the past few years — buyers are now price-hunting, not brand-hunting
- **500+ dispensaries** in MA — too many to comparison shop manually
- **Google Shopping doesn't exist** for cannabis — federally illegal, banned from ads
- **Weedmaps/Leafly** are dispensary portals, not comparison tools — you see one store at a time
- **We have the data** — 150K+ products across 4 platforms, ~500+ GPIDs (same-product matches), updated daily

### The Emotional Core

When someone lands on GLASS Prices, they should feel one thing: **"Finally."**

Not impressed. Not curious. Not entertained. Just... relief. Like someone finally built the obvious thing.

The closest analog: the first time you used Google Flights and saw that price graph. You thought, "Why did I ever use Kayak?" GLASS Prices should feel that inevitable.

---

## 2. First Impression — The Landing

### The 0.5-Second Rule

When someone taps a link from their group chat or finds us through Google, here's what they see — in order, top to bottom, in the first half-second:

1. **A search bar.** Massive. Centered. Placeholder: `Search any product... "Fernway cart" "cheapest eighth" "Blue Dream"`
2. **Below it, immediately: real prices.** Not a hero image. Not a mission statement. Not "Welcome to GLASS." Actual product cards with actual prices, already loaded. Today's best deals.
3. **A single line of context** above the search bar, in small caps: `EVERY DISPENSARY IN MASSACHUSETTS. EVERY PRICE. UPDATED DAILY.`

That's it. No splash. No animation. No loading skeleton. The page loads with prices already visible.

### What Makes Them Screenshot It

The screenshot moment is when they see something like this on their first scroll:

```
┌─────────────────────────────────────────┐
│  Fernway Berry Gelato — 0.5g Cart       │
│                                         │
│  $35  ← NETA Brookline         4.2 mi  │
│  $40  ← Berkshire Roots        6.1 mi  │
│  $48  ← The Botanist           2.8 mi  │
│  $55  ← Theory Wellness        5.7 mi  │
│                                         │
│  You'd pay $20 more at the wrong store. │
└─────────────────────────────────────────┘
```

That last line — **"You'd pay $20 more at the wrong store"** — is the screenshot. That's the text message to the group chat. That's the Reddit post. That's the controversy.

### Hero Section — Detailed Spec

**No hero image.** Hero images are for brands that need to explain themselves. We don't. The product IS the hero.

**Layout (mobile, 375px):**

```
┌─────────────────────────────────────┐
│  ≡  GLASS                     📍 MA │  ← 48px nav, minimal
├─────────────────────────────────────┤
│                                     │
│  EVERY DISPENSARY. EVERY PRICE.     │  ← 12px, all-caps, #888
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 🔍 "Fernway cart" ·"cheap… │    │  ← 56px tall search bar
│  └─────────────────────────────┘    │
│                                     │
│  Flower · Carts · Edibles · Pre-R… │  ← Horizontal scroll chips
│                                     │
├─────────────────────────────────────┤
│  🔥 BIGGEST PRICE GAPS RIGHT NOW   │  ← Section header
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Fernway Berry Gelato 0.5g   │    │
│  │ Cart                        │    │
│  │                             │    │
│  │ $35 ───────────────── $55   │    │  ← Price range bar
│  │ NETA Brookline    Theory    │    │
│  │                             │    │
│  │ ▸ Compare 4 stores          │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Good Chemistry Grease Monk  │    │
│  │ 3.5g Flower                 │    │
│  │                             │    │
│  │ $28 ───────────────── $45   │    │
│  │ CommCan           Curaleaf  │    │
│  │                             │    │
│  │ ▸ Compare 6 stores          │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ ... more cards              │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

### Landing Page Content Strategy

**Below the fold (scroll to see):**

1. **"Biggest Price Gaps Right Now"** — Products with the highest min/max spread. These are the controversy cards. Auto-generated from API data. Always fresh.

2. **"Popular Searches"** — `Fernway carts` · `cheapest eighth` · `PAX pods` · `edibles under $30` · `Cookies flower`. These are real search links, not static text. Tapping one runs the search.

3. **"Deals by City"** — Boston · Cambridge · Worcester · Springfield · Cape Cod. Each links to a geo-filtered results page.

4. **Footer** — Minimal. `About` · `How Prices Work` · `For Dispensaries` · `Contact`. No social links (we don't need followers, we need users).

### What the Landing Page Does NOT Have

- ❌ Hero image or banner
- ❌ "Welcome to..." or "We're building..." or any brand narrative
- ❌ Testimonials (we have no users yet, and even when we do, this isn't that kind of site)
- ❌ Feature list or "How it works" section
- ❌ Newsletter signup (not on landing — it lives on deal pages)
- ❌ App download prompt
- ❌ Login/signup button (there are no accounts)

---

## 3. The Core Experience

### 3.1 Search UX

**The search bar is the product.** It needs to feel as natural as Google.

**Behavior:**

1. **Type anything.** Brand names, strain names, product types, natural language. The API already supports `q` parameter with ILIKE matching across brand, strain, and form.

2. **Instant results.** As-you-type suggestions after 2 characters, debounced at 200ms. Show top 5 matching GPIDs with mini price ranges.

   ```
   🔍 fernway ber|
   ─────────────────────────────────
   Fernway Berry Gelato · Cart · 0.5g    $35 – $55
   Fernway Berry Blast · Cart · 0.5g     $38 – $52
   Fernway Berry Gelato · Cart · 1g      $60 – $82
   ```

3. **Category filters.** Horizontal scrolling chips below the search bar: `All` · `Flower` · `Carts` · `Edibles` · `Pre-Rolls` · `Concentrates` · `Tinctures`. Tapping a chip filters results AND updates the URL (`/prices?category=flower`).

4. **"Near me" is automatic.** On first visit, request geolocation (one-time browser prompt). If granted, all results include distance and sort by relevance + proximity. If declined, show all MA results sorted by price spread. Never ask again — use a toggle: `📍 Near me · Statewide`.

5. **No advanced search.** No filters panel. No "sort by" dropdown with 8 options. The only controls are: search text, category chip, and near-me toggle. That's it. Constraints breed clarity.

**URL structure for search:**
```
/prices?q=fernway+cart                     → search results
/prices?q=fernway+cart&category=carts      → filtered
/prices?q=fernway+cart&lat=42.36&lng=-71.05&radius=10  → geo-filtered
```

### 3.2 Search Results Page

**This is where the magic happens.** The results page is the core of the entire product.

**Layout concept: "The Price Ladder"**

Each search result is a product card showing the full price range across all stores. Not a table. Not a grid. A **ladder** — a visual stack that makes price differences visceral.

**Product Card (Mobile, Full Width):**

```
┌─────────────────────────────────────────┐
│                                         │
│  Fernway Berry Gelato                   │  ← Brand + Strain, bold
│  0.5g Cartridge                         │  ← Form + weight, muted
│                                         │
│  ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━●         │  ← Price range bar
│  $35                          $55       │  ← Min / Max labels
│                                         │
│  CHEAPEST                               │
│  $35 · NETA Brookline · 4.2 mi         │  ← Highlighted cheapest
│                                         │
│  +3 more stores from $40 – $55          │  ← Collapsed other stores
│                                         │
│  Save up to $20 ─────── Compare ▸       │  ← CTA
│                                         │
└─────────────────────────────────────────┘
```

**Key design decisions:**

1. **The price range bar is the star.** It's a horizontal bar (think progress bar) where the left edge is the cheapest price and the right edge is the most expensive. The wider the spread, the more dramatic it looks. A product with $35–$55 range has a visually wide bar. A product with $40–$42 has a tiny bar. **The bar itself tells you if it's worth comparison shopping.**

2. **Cheapest store is always shown.** No need to tap into the card to see where to go. The cheapest option is right there.

3. **"+3 more stores" collapses the rest.** Tap to expand and see all stores. This keeps the results page scannable — you can see 4-5 products at a glance on mobile.

4. **"Save up to $20"** — This is the emotional hook. It's the spread between min and max. For products with only 1 store, this line doesn't appear.

5. **Distance is shown only if location is available.** If not, city name replaces distance.

**Sorting:**
- Default: By **price spread** (biggest savings first). This is the most interesting sort — it surfaces the products where comparison shopping matters most.
- Alternative: By **lowest price** (cheapest products first). Toggle at top of results.
- We do NOT sort by "relevance" in a vague way. Every sort has a clear, honest meaning.

### 3.3 Product Detail Page (GPID Page)

**URL:** `/prices/gpid/[gpid-slug]` (e.g., `/prices/gpid/fernway-berry-gelato-cart-0.5g`)

This is the SEO powerhouse and the shareable page. When someone shares a link, THIS is what loads.

**Layout:**

```
┌─────────────────────────────────────────┐
│  ← Back to results                      │
│                                         │
│  Fernway Berry Gelato                   │
│  0.5g Cartridge                         │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │         PRICE COMPARISON         │    │
│  │                                 │    │
│  │  ● $35  NETA Brookline    4.2mi │    │  ← #1, highlighted
│  │  ○ $40  Berkshire Roots   6.1mi │    │
│  │  ○ $42  CommCan Lowell    8.3mi │    │
│  │  ○ $48  The Botanist      2.8mi │    │
│  │  ○ $55  Theory Wellness   5.7mi │    │  ← Most expensive
│  │                                 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  THE SPREAD                     │    │
│  │                                 │    │
│  │  Cheapest     $35   NETA        │    │
│  │  Median       $42              │    │
│  │  Most Exp.    $55   Theory      │    │
│  │                                 │    │
│  │  You'd save $20 buying from     │    │
│  │  NETA instead of Theory.        │    │
│  │                                 │    │
│  │  [Share This Price] [Get Alert] │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  ABOUT THIS PRODUCT             │    │
│  │                                 │    │
│  │  Brand:     Fernway             │    │
│  │  Category:  Cartridge           │    │
│  │  Weight:    0.5g                │    │
│  │  Found at:  5 stores            │    │
│  │  Updated:   Today               │    │
│  │                                 │    │
│  │  Prices checked across Dutchie, │    │
│  │  Jane, Leafly, and Weedmaps.    │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Similar Products                       │
│  Fernway Strawberry Cough 0.5g Cart     │
│  $32 – $50 · 4 stores                  │
│  ...                                    │
└─────────────────────────────────────────┘
```

**Key decisions:**

1. **The price list IS the page.** The store-by-store comparison is the entire point. It's the first thing you see after the product name.

2. **Stores are sorted by price, cheapest first.** Always. No option to sort by distance or name. Price is king. (Distance is shown as context, not a sort option.)

3. **"The Spread" box** makes the savings explicit. "$20 difference between cheapest and most expensive" is more impactful than any chart.

4. **"Share This Price" generates a shareable card** (see Virality Engine section). Not a social share button — it generates an image.

5. **"Get Alert"** — email-only price drop notification. No account needed. Just type your email and which price point you want. "Alert me when this drops below $30." One field, one button.

6. **Similar Products** at the bottom — same brand, different strains. Or same category, different brands. Cross-sell without selling.

7. **"Prices checked across Dutchie, Jane, Leafly, and Weedmaps."** — This is the only mention of platforms. It's not explaining how we work; it's showing breadth. It's social proof in one line. We checked EVERYWHERE so you don't have to.

### 3.4 Brand Page

**URL:** `/prices/brand/[brand-slug]` (e.g., `/prices/brand/fernway`)

Every brand = a page. Good for SEO, good for browsing.

```
┌─────────────────────────────────────────┐
│                                         │
│  Fernway                                │
│  24 products at 38 stores across MA     │
│                                         │
│  Flower · Carts · Pre-Rolls             │  ← Category tabs
│                                         │
│  [Product cards, same format as         │
│   search results, filtered to this      │
│   brand]                                │
│                                         │
│  Price Range: $25 – $82                 │
│  Cheapest Fernway product:              │
│  Berry Gelato 0.5g Cart — $35 at NETA   │
│                                         │
└─────────────────────────────────────────┘
```

### 3.5 Store Page

**URL:** `/prices/store/[store-slug]` (e.g., `/prices/store/neta-brookline`)

Every store = a page. This is where the controversy lives.

```
┌─────────────────────────────────────────┐
│                                         │
│  NETA Brookline                         │
│  Brookline, MA · 4.2 mi                │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  PRICE POSITION                 │    │
│  │                                 │    │
│  │  Cheapest price:    42% of      │    │
│  │                     products    │    │
│  │  Mid-range:         35%         │    │
│  │  Most expensive:    23%         │    │
│  │                                 │    │
│  │  Compared to all MA stores      │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Products at NETA Brookline             │
│  [Product list with "vs market"         │
│   indicator on each]                    │
│                                         │
│  Fernway Berry Gelato 0.5g Cart         │
│  $35 here · $42 median · CHEAPEST 🏷️   │
│                                         │
│  Cookies Gary Payton 3.5g Flower        │
│  $55 here · $45 median · $10 ABOVE ⚠️  │
│                                         │
└─────────────────────────────────────────┘
```

**This page is a weapon.** It tells consumers exactly how this store's prices compare to the market. Stores with honest pricing look great. Stores gouging on popular products get exposed. We're not editorializing — we're just showing the numbers. The data speaks.

### 3.6 Map View (Secondary, Not Default)

**NOT the default view.** The default is always the list. But a map toggle exists for "show me what's near me."

- Toggle between `List` and `Map` on search results
- Map shows dispensary pins with their cheapest price for the searched product
- Tap a pin → mini card with store name, price, distance
- Tap the card → full product detail page
- Map uses Mapbox GL JS (free tier covers our usage)

**Why map is secondary:** Maps are slow, require geo permission, and hide data. Lists show more info in less space. The map exists for the "I'm driving, which store should I stop at?" use case. It's not the primary use case.

### 3.7 City/Region Pages (Auto-Generated)

**URLs:**
```
/prices/boston           → Best deals in Boston
/prices/cambridge       → Best deals in Cambridge  
/prices/worcester       → Best deals in Worcester
/prices/springfield     → Best deals in Springfield
/prices/cape-cod        → Best deals on Cape Cod
```

These are auto-generated pages that aggregate the best deals within a geographic radius. They serve two purposes:

1. **SEO** — "cheapest weed in Boston" is a real search query
2. **Browse without searching** — not everyone knows what product they want

Content:
- Top 10 biggest price gaps in [city]
- Cheapest products by category in [city]  
- Number of dispensaries tracked in [city]
- Updated daily (static generation + ISR)

---

## 4. The Controversy Play

### 4.1 The Framing

We don't attack dispensaries. We don't call anyone a ripoff. We **show numbers and let the reader draw conclusions.** This is more powerful than any editorial because it feels objective.

The controversy isn't in what we say — it's in what the data says.

**Examples of controversy-by-data:**

- "This product costs $20 more at Theory than at NETA. Same product. Same city."
- "23% of products at [Store X] are the most expensive in their market."
- "The average cart costs $45 in Boston but $38 in Worcester."

We never say "Store X is ripping you off." We say "Store X charges $55 for this. Store Y charges $35." The reader does the math. That's the controversy.

### 4.2 The Tone

**We are on the buyer's side. Full stop.**

- "You'd save $20 buying from NETA instead of Theory." ← This is editorial. We own it.
- "Compare before you go." ← Practical, not preachy.
- "Every dispensary. Every price. No bullshit." ← Direct.

We are NOT neutral. We are buyer-first. But we achieve this through transparency, not attacks. The data IS the attack.

### 4.3 Specific Controversy Mechanics

**"The Spread" on every product page.** The explicit call-out of the cheapest vs. most expensive store. This is the thing dispensaries will hate and consumers will love.

**"Store Price Position"** on every store page. A simple percentage: "This store has the cheapest price on 42% of products, and the most expensive on 23%." Cold, factual, devastating.

**"Biggest Price Gaps Right Now"** on the landing page. Auto-generated, always fresh. These are the products with the widest min-max spread. They exist specifically to spark "can you believe this?" conversations.

**Weekly "Price Report" pages** (auto-generated):
- "This Week's Best Deals in Boston"
- "5 Products Where You're Overpaying"
- "Price Changes This Week: Who Dropped, Who Raised"

These are designed to be shared. Every report page has a shareable card (see Virality Engine).

### 4.4 What Happens When Dispensaries Complain

They will. Here's the response framework:

1. **"Our data comes from your own public menus."** We're not inventing prices. We're showing what you published.
2. **"Want your prices to look better? Lower them."** The fix is in their hands.
3. **"Claim your store page for free."** This is the V2 monetization hook. "Claim your page to add context, hours, deals, and respond to price comparisons."

Complaints are validation. If dispensaries are mad, we're doing it right.

### 4.5 The Reddit/Social Strategy

We don't need to post. Users will. But we make it easy:

- Every product page has a clean URL that previews well (OG tags with price data)
- The "Share This Price" button generates a clean image card
- City deal pages are perfect for r/bostontrees, r/MAtrees
- The landing page "Biggest Price Gaps" section is designed to be screenshotted

**We will seed exactly ONE Reddit post to r/bostontrees:**
> "Found this site that compares prices across every dispensary in MA. [Brand] is $35 at [Store] and $55 at [Store]. Pretty wild."

That's it. If the product is good, the community does the rest.

---

## 5. Visual Language

### 5.1 Color Palette

**NOT green.** Green = every cannabis site ever. We need to feel like a fintech utility, not a head shop.

**Primary Palette:**

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Background | Off-black | `#0A0A0B` | Dark mode default body |
| Surface | Dark gray | `#141416` | Cards, containers |
| Surface elevated | Mid-dark | `#1C1C20` | Hover states, modals |
| Border | Subtle gray | `#2A2A30` | Card borders, dividers |
| Text primary | Near-white | `#F0F0F0` | Headlines, prices |
| Text secondary | Medium gray | `#888892` | Labels, metadata |
| Text muted | Dim gray | `#555560` | Timestamps, fine print |

**Accent Colors:**

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Cheapest / Best deal | Electric teal | `#00E5A0` | Lowest price highlight, savings badges |
| Most expensive / Warning | Warm amber | `#FFB020` | Highest price, "above median" flags |
| Interactive / CTA | Bright white | `#FFFFFF` | Buttons, links, active states |
| Price range bar (low) | Electric teal | `#00E5A0` | Left end of price bar |
| Price range bar (high) | Warm amber | `#FFB020` | Right end of price bar |
| Price range bar (fill) | Gradient | teal → amber | The bar itself |

**Why dark mode default:**
- 80% mobile usage = most people browse at night or in low light
- Dark mode feels premium (Cash App, Robinhood, Coinbase)
- Price numbers POP on dark backgrounds
- Lower battery usage on OLED screens
- It looks cooler in screenshots (→ virality)

**Light mode:** Available via system preference toggle. Same structure, inverted. But we design dark-first.

### 5.2 Typography

**Font Stack:**

- **Headlines / Prices:** `Inter` — tight letter-spacing, geometric, reads clean at every size. Prices render in `Inter` with `font-variant-numeric: tabular-nums` so dollar amounts align perfectly.
- **Body / Labels:** `Inter` — same font, different weights. One font family, zero decisions.
- **Weights used:** 400 (body), 500 (labels/medium), 600 (semibold prices), 700 (bold headlines)

**Why Inter:** It's the best UI font on the internet. It was designed for screens. It has tabular numbers. It's free. It's on every CDN. It loads fast. It has no personality to distract from the data.

**Type Scale (mobile):**

| Element | Size | Weight | Tracking |
|---------|------|--------|----------|
| Product name | 18px | 600 | -0.01em |
| Price (large, detail page) | 32px | 700 | -0.02em |
| Price (card, results) | 20px | 700 | -0.01em |
| Store name | 14px | 500 | 0 |
| Labels / category | 12px | 500 | 0.04em |
| Body text | 14px | 400 | 0 |
| Fine print | 12px | 400 | 0.01em |

### 5.3 Iconography

**No cannabis leaves. No smoke. No joints. No buds.**

Icons used (Lucide icon set, consistent with shadcn/ui):

| Concept | Icon | Usage |
|---------|------|-------|
| Search | `Search` | Search bar |
| Location | `MapPin` | Distance, "near me" |
| Price down | `TrendingDown` | Price drops |
| Price up | `TrendingUp` | Price increases |
| Share | `Share2` | Share button |
| Alert bell | `Bell` | Price alerts |
| Store | `Store` | Store pages |
| Filter | `SlidersHorizontal` | Category filter (if needed) |
| External link | `ExternalLink` | "Visit store" links |
| Check | `Check` | Cheapest store indicator |

### 5.4 The Price Range Bar

This is the signature visual element. It appears on every product card and detail page. It needs to be **instantly readable.**

**Spec:**

- Height: 6px (mobile), 8px (desktop)
- Border radius: full (pill shape)
- Background: `#2A2A30` (track)
- Fill: linear gradient from `#00E5A0` (cheapest) to `#FFB020` (most expensive)
- Left label: cheapest price in teal
- Right label: most expensive price in amber
- If only 1 store: single dot, no bar, price in white
- If 2 stores: bar with two endpoints
- If 3+ stores: bar with dots at each price point

**The bar tells a story at a glance.** A wide bar = big savings opportunity. A narrow bar = prices are consistent. No bar (1 store) = no comparison available.

### 5.5 Motion & Animation

**Almost none.** This is a utility, not an experience.

- Page transitions: none (instant navigation)
- Card interactions: subtle hover lift (2px translateY, 100ms ease)
- Search suggestions: fade in (150ms)
- Price range bar: draws left-to-right on first appear (300ms, once)
- Everything else: instant

**No loading skeletons.** If data is loading, show a single muted spinner. But the architecture should prevent visible loading (SSR + edge caching).

---

## 6. The Anti-Pattern Rules

These are non-negotiable. They are the brand. Breaking any of these means the feature doesn't ship.

### The Immutable Laws

| # | Rule | Why |
|---|------|-----|
| 1 | **No "powered by AI" anywhere** | Nobody cares how we got the data. AI badges are tech vanity. |
| 2 | **No sign-up walls** | Every price is free. Every page is accessible. Zero gates. |
| 3 | **No app download prompts** | PWA yes, native app prompt no. Not now, not ever. |
| 4 | **No dispensary ads (V1)** | We are buyer-first. Ads compromise that instantly. V2 gets "Featured" placement. |
| 5 | **No cannabis culture aesthetic** | No leaves, no tie-dye, no "420," no Bob Marley, no smoke effects. |
| 6 | **No "disrupting the industry" language** | We're a price tool. We compare prices. That's it. |
| 7 | **No tech stack mentions** | Nobody visiting this site cares that we use React. |
| 8 | **No data collection explanation** | "Where do you get your prices?" → "From public dispensary menus." End of story. |
| 9 | **No social features** | No profiles, no reviews, no comments, no likes. This is a utility. |
| 10 | **No dark patterns** | No countdown timers, no "only 2 left," no manipulative urgency. Real prices, real time. |
| 11 | **No price anchoring tricks** | Don't show a fake "retail price" crossed out. Show actual prices at actual stores. |
| 12 | **No affiliate links or tracking redirects** | When we link to a store, it's a clean link. No tracking parameters. Trust > monetization. |

### The "Would Randy's Mom Use This?" Test

Every feature gets this test: If a 55-year-old who buys edibles twice a month went to this site on her iPhone, would she:

1. Understand what the site does within 3 seconds?
2. Find the product she wants within 10 seconds?
3. Know where to buy it cheaper within 15 seconds?
4. Be able to do all this without creating an account, downloading anything, or dismissing any popups?

If any answer is "no," the feature is wrong.

---

## 7. Technical Architecture

### 7.1 Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Framework | **Next.js 15 (App Router)** | SSR for SEO, ISR for freshness, React Server Components for performance |
| Styling | **Tailwind CSS 4** | Utility-first, fast, consistent with existing GLASS stack |
| Components | **shadcn/ui** | Accessible, unstyled base components. We customize everything. |
| State | **Nuqs (URL state)** | All filter/search state lives in the URL. Shareable, bookmarkable. |
| Maps | **Mapbox GL JS** | Free tier sufficient, beautiful dark mode map |
| API | **Existing Fastify consumer endpoints** | `/v1/consumer/search`, `/v1/consumer/gpid/:gpid`, `/v1/consumer/brands/top` |
| Hosting | **Vercel** | Edge functions, ISR, analytics, speed |
| Analytics | **Plausible** | Privacy-first, no cookies, no consent banner needed |
| Fonts | **Inter (self-hosted)** | Single WOFF2 file, subset for Latin. No Google Fonts call. |

### 7.2 API Integration

**Existing Consumer API Endpoints:**

```
GET /v1/consumer/search
  ?q=fernway+cart
  &brand=Fernway
  &category=carts
  &lat=42.36&lng=-71.05&radius_miles=10
  &limit=20&offset=0

GET /v1/consumer/gpid/:gpid

GET /v1/consumer/brands/top
  ?limit=50
```

**New Endpoints Needed (V1):**

```
GET /v1/consumer/deals/top
  ?city=boston
  &category=carts
  &limit=10
  → Returns products with highest price spreads

GET /v1/consumer/store/:store_slug
  → Returns store info + price position + product list

GET /v1/consumer/store/:store_slug/products
  ?category=flower
  &limit=20&offset=0
  → Paginated product list for a store

GET /v1/consumer/cities
  → Returns list of cities with dispensary counts

GET /v1/consumer/search/suggest
  ?q=fern
  &limit=5
  → Fast typeahead suggestions (brand + strain + form combos)
```

**API Caching Strategy:**

| Endpoint | Cache TTL | Strategy |
|----------|-----------|----------|
| `/consumer/search` | 5 min | Edge cache, stale-while-revalidate |
| `/consumer/gpid/:gpid` | 10 min | Edge cache, ISR on detail pages |
| `/consumer/brands/top` | 1 hour | Static, rebuild hourly |
| `/consumer/deals/top` | 15 min | Edge cache |
| `/consumer/store/:slug` | 10 min | Edge cache, ISR |
| `/consumer/search/suggest` | 1 min | Edge cache, aggressive |

### 7.3 Page Architecture

```
/prices                          → Landing (SSR + client search)
/prices?q=fernway&category=carts → Search results (SSR)
/prices/gpid/[gpid-slug]         → Product detail (ISR, 10min revalidate)
/prices/brand/[brand-slug]       → Brand page (ISR, 1hr revalidate)
/prices/store/[store-slug]       → Store page (ISR, 10min revalidate)
/prices/[city-slug]              → City deals (ISR, 15min revalidate)
/prices/about                    → Static: how it works, FAQ
/prices/dispensaries             → Static: "For Dispensaries" (V2 hook)
```

**Every page is a valid URL. Every URL is shareable. Every shared URL shows the same content the user saw.** No client-side-only state. No "you need to search again." If you share `/prices/gpid/fernway-berry-gelato-cart-0.5g`, the recipient sees the full price comparison immediately.

### 7.4 SEO Strategy

**This is how we win.** Cannabis is banned from Google Ads, but NOT from Google organic search. We will own every "cheapest [product] in Massachusetts" query.

**Page Types for SEO:**

1. **GPID Pages** (~500+ pages, growing)
   - Title: `Fernway Berry Gelato 0.5g Cart — Compare Prices Across MA | GLASS`
   - Meta: `$35 at NETA Brookline to $55 at Theory Wellness. Compare prices at 5 stores.`
   - Structured data: `Product` schema with `offers` array

2. **Brand Pages** (~100+ pages)
   - Title: `Fernway Products & Prices in Massachusetts | GLASS`
   - Meta: `Compare prices on 24 Fernway products at 38 stores across MA. Cheapest: $25.`

3. **Store Pages** (~400+ pages)
   - Title: `NETA Brookline Menu & Prices — Compare to Other Dispensaries | GLASS`
   - Meta: `NETA Brookline has the cheapest price on 42% of products. See full menu with price comparisons.`

4. **City Pages** (~15-20 pages)
   - Title: `Best Weed Deals in Boston — Price Comparison Across Dispensaries | GLASS`
   - Meta: `Compare cannabis prices across 47 dispensaries in Boston. Updated daily.`

5. **Category + City Combos** (~80+ pages)
   - `/prices/boston?category=carts` → "Cheapest Carts in Boston"
   - Auto-generated, thin but useful

**Total SEO surface: 1,000+ unique, content-rich pages at launch.** Each with unique price data that updates daily. This is a moat.

**Schema.org markup on every GPID page:**

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Fernway Berry Gelato 0.5g Cart",
  "brand": { "@type": "Brand", "name": "Fernway" },
  "category": "Cannabis Cartridge",
  "offers": {
    "@type": "AggregateOffer",
    "lowPrice": "35.00",
    "highPrice": "55.00",
    "offerCount": 5,
    "priceCurrency": "USD"
  }
}
```

### 7.5 Performance Targets

| Metric | Target | How |
|--------|--------|-----|
| First Contentful Paint | < 800ms | SSR, edge caching, self-hosted font |
| Largest Contentful Paint | < 1.2s | Above-fold prices server-rendered |
| Time to Interactive | < 1.5s | Minimal JS, React Server Components |
| Cumulative Layout Shift | < 0.05 | Fixed-height cards, no lazy-load shifts |
| Total JS bundle | < 80KB gzip | Tree-shake aggressively, no heavy deps |
| First load (3G) | < 2s | Critical CSS inline, font preload |

**Performance is a feature.** Our audience is on phones, often on cellular. Every 100ms of load time is someone who bounces back to Weedmaps.

### 7.6 PWA Considerations

- **Add to home screen:** Yes. Manifest with GLASS icon. No install prompt (anti-pattern).
- **Offline:** No. Prices must be fresh. Don't cache stale prices.
- **Push notifications:** No. Email alerts only. Push requires an install we won't prompt.
- **Service worker:** Minimal — cache font, CSS, shell HTML. Never cache price data.

---

## 8. The Virality Engine

### 8.1 The Shareable Price Card

When a user taps "Share This Price" on a product detail page, we generate an image card (server-side, via `@vercel/og` or Satori):

```
┌─────────────────────────────────────────┐
│                                         │
│  GLASS                                  │
│                                         │
│  Fernway Berry Gelato · 0.5g Cart       │
│                                         │
│  $35  ←──────── $20 spread ────────→ $55│
│  NETA Brookline              Theory     │
│                                         │
│  Same product. Different price.         │
│  glassintel.xyz/prices                  │
│                                         │
└─────────────────────────────────────────┘
```

**Design:** Dark background, teal/amber accent, clean type. Looks good as an iMessage preview, Instagram story, Reddit embed, or tweet image.

**Implementation:** OG image route at `/api/og/gpid/[gpid]` that generates this card server-side. Used for both social sharing (og:image) AND the manual "Share" button.

### 8.2 The "Savings Receipt"

When someone finds a deal through GLASS, we let them generate a "receipt":

```
┌─────────────────────────────────────────┐
│  ✓ YOU JUST SAVED $20                   │
│                                         │
│  Fernway Berry Gelato 0.5g Cart         │
│  $35 at NETA Brookline                  │
│  Instead of $55 at Theory Wellness      │
│                                         │
│  Found on GLASS · glassintel.xyz/prices │
└─────────────────────────────────────────┘
```

This is the flex. "Look how much I saved." It's the same mechanic as Cash App's payment receipts that people screenshot. The savings amount is the hook.

**Not actual purchase verification** — we don't know if they actually bought it. But that doesn't matter. The intent is "I found this deal" not "I completed this transaction."

### 8.3 Price Alerts (Email Only)

**How it works:**

1. On any product detail page, there's a small "Get Alert" section
2. User enters email + target price ("Alert me below $30")
3. No account created. We store email + gpid + target price
4. Daily job checks prices → sends email if target is hit
5. Email contains: product, new price, store, direct link to GLASS page
6. One-click unsubscribe in every email

**What we DON'T do:**
- No account creation
- No app required
- No marketing emails — ONLY the alert they asked for
- No "weekly digest" unless they explicitly opt into it later

### 8.4 Weekly Deal Pages (Auto-Generated)

Every Monday at 6 AM ET, an automated job generates:

```
/prices/deals/week-of-feb-14-2026
/prices/deals/boston/week-of-feb-14-2026
/prices/deals/cambridge/week-of-feb-14-2026
```

Content:
- "Top 10 Price Drops This Week"
- "Biggest Price Gaps in [City]"
- "New Products Added"
- "Most-Compared Products"

These pages are designed to be shared in r/bostontrees, local Facebook groups, and group chats. They have unique OG images with the week's headline stat ("Average cart price dropped $3 this week").

### 8.5 Social Proof Without Accounts

We don't have user accounts, but we can still show activity:

- **"12,847 prices compared today"** — Real number, updated hourly. Shows on landing page footer. Social proof that this is a living, active tool.
- **"Prices updated 3 hours ago"** — Freshness indicator on every page. Builds trust.
- **"Tracked across 487 dispensaries"** — Coverage stat. Shows breadth.

These are not vanity metrics. They answer the unspoken question: "Is this site legit? Is the data real?"

---

## 9. Revenue Path (V2)

**V1 is 100% free, 0% monetized.** This is critical. Any hint of monetization in V1 kills trust. We build the audience first.

### V2 Monetization (Post-Traction, ~10K weekly users)

**9.1 "Claim Your Store" (Free)**

Any dispensary can "claim" their store page on GLASS. This is free and gives them:
- Verified badge on their store page
- Ability to add: store hours, deals/promotions, description
- Email notifications when their prices are compared
- Analytics: how many times their page was viewed

**Why free:** It gets dispensaries into our ecosystem. It's the top of the funnel.

**9.2 Featured Placement (Paid: $199-499/mo)**

For claimed stores, optional paid upgrades:
- **Featured placement** in search results (marked as "Featured" — transparent, not deceptive)
- **"Deal of the Week"** highlight on city pages
- **Priority in "near me" results** (still sorted by price, but tie-breaker goes to featured)
- **Monthly "Price Position" report** delivered via email

**Pricing:**
- Featured listing: $199/mo (1 store)
- Featured + deal highlight: $349/mo
- Featured + deal + analytics dashboard: $499/mo

**Why this works:** Dispensaries NEED to be visible where price-conscious buyers are shopping. GLASS becomes the only way to reach comparison shoppers. It's the Google Ads of cannabis.

**9.3 Brand Portal (V3)**

Brands (Fernway, Good Chemistry, Cookies, etc.) can:
- Claim their brand page
- Upload official product photos and descriptions
- See which stores carry their products and at what price
- Get notified when a store drops below MAP (Minimum Advertised Price)

**Pricing:** $500-2000/mo depending on SKU count.

**9.4 Revenue Projections**

| Quarter | Free Users | Claimed Stores | Featured Stores | MRR |
|---------|-----------|----------------|-----------------|-----|
| Q2 2026 | 2K-5K/wk | 20-30 | 0 | $0 |
| Q3 2026 | 10K-20K/wk | 80-120 | 5-10 | $1,500-$4,000 |
| Q4 2026 | 30K-50K/wk | 200+ | 20-40 | $6,000-$16,000 |
| Q1 2027 | 50K-100K/wk | 350+ | 50-80 + brands | $20K-$60K |

**Key insight:** We don't need many paying customers. 50 dispensaries at $300/mo average = $15K MRR. There are 400+ dispensaries in MA. We only need 12.5% conversion.

---

## 10. Wireframes & Layout Descriptions

### 10.1 Landing Page — Mobile (375 × 812)

```
╔═══════════════════════════════════════╗
║  ≡  GLASS                     📍 MA  ║  48px, bg: #0A0A0B
╠═══════════════════════════════════════╣
║                                       ║  20px padding top
║  EVERY DISPENSARY. EVERY PRICE.       ║  12px, Inter 500, #888892
║  UPDATED DAILY.                       ║  same
║                                       ║  12px spacer
║  ┌───────────────────────────────┐    ║
║  │ 🔍  Search any product...     │    ║  56px tall, bg: #141416
║  │     "Fernway cart"            │    ║  border: #2A2A30
║  └───────────────────────────────┘    ║  border-radius: 14px
║                                       ║
║  ┌────┐┌────┐┌────┐┌────┐┌────┐      ║  Category chips
║  │All ││Flwr││Cart││Edib││PreR│      ║  32px tall, horizontal
║  └────┘└────┘└────┘└────┘└────┘      ║  scroll, gap: 8px
║                                       ║  bg: #141416, active: #fff
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  🔥 BIGGEST PRICE GAPS               ║  14px, Inter 600, #F0F0F0
║     RIGHT NOW                         ║  left-aligned
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │ Fernway Berry Gelato          │    ║  Card bg: #141416
║  │ 0.5g Cartridge                │    ║  border-radius: 12px
║  │                               │    ║  padding: 16px
║  │ ●━━━━━━━━━━━━━━━━━━━━━━━●    │    ║  6px bar
║  │ $35                     $55   │    ║  teal      amber
║  │                               │    ║
║  │ Cheapest: NETA Brkln · 4.2mi │    ║  14px, teal text
║  │ +3 more stores                │    ║  12px, muted
║  │                               │    ║
║  │ Save up to $20     Compare ▸  │    ║  14px, bold
║  └───────────────────────────────┘    ║
║                                       ║  16px gap between cards
║  ┌───────────────────────────────┐    ║
║  │ Good Chemistry Grease Monkey  │    ║
║  │ 3.5g Flower                   │    ║
║  │                               │    ║
║  │ ●━━━━━━━━━━━━━━━━━●          │    ║
║  │ $28                $45        │    ║
║  │                               │    ║
║  │ Cheapest: CommCan · 8.3mi     │    ║
║  │ +5 more stores                │    ║
║  │                               │    ║
║  │ Save up to $17     Compare ▸  │    ║
║  └───────────────────────────────┘    ║
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │ [Third card...]               │    ║
║  └───────────────────────────────┘    ║
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  POPULAR SEARCHES                     ║
║                                       ║
║  ┌──────────────┐ ┌──────────────┐    ║  Pill-shaped links
║  │ Fernway carts│ │cheapest 8th  │    ║  bg: #1C1C20
║  └──────────────┘ └──────────────┘    ║  border: #2A2A30
║  ┌──────────────┐ ┌──────────────┐    ║  tap → runs search
║  │ PAX pods     │ │edibles <$30  │    ║
║  └──────────────┘ └──────────────┘    ║
║  ┌──────────────┐ ┌──────────────┐    ║
║  │Cookies flower│ │ preroll deals │    ║
║  └──────────────┘ └──────────────┘    ║
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  DEALS BY CITY                        ║
║                                       ║
║  Boston · 47 stores ──────────── ▸    ║  Tap → /prices/boston
║  Cambridge · 12 stores ──────── ▸     ║
║  Worcester · 18 stores ─────── ▸      ║
║  Springfield · 9 stores ────── ▸      ║
║  Cape Cod · 14 stores ──────── ▸      ║
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  487 dispensaries tracked             ║  12px, #555560
║  33,440 prices compared today         ║  centered
║  Updated every 24 hours               ║
║                                       ║
║  About · How Prices Work ·            ║
║  For Dispensaries · Contact            ║
║                                       ║
║  © 2026 GLASS                         ║  12px, #555560
║                                       ║
╚═══════════════════════════════════════╝
```

### 10.2 Search Results — Mobile (375 × 812)

```
╔═══════════════════════════════════════╗
║  ← GLASS                     📍 4mi  ║  48px nav
╠═══════════════════════════════════════╣
║  ┌───────────────────────────────┐    ║
║  │ 🔍  fernway cart              │    ║  Search bar (pre-filled)
║  └───────────────────────────────┘    ║
║                                       ║
║  ┌────┐┌────┐┌─────┐┌────┐           ║  Category chips
║  │All ││Cart✓││Flower││Edib│          ║  "Cart" is active
║  └────┘└────┘└─────┘└────┘           ║
║                                       ║
║  8 results · sorted by savings ▾      ║  12px, muted
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │ Fernway Berry Gelato          │    ║  FIRST RESULT
║  │ 0.5g Cart                     │    ║
║  │                               │    ║
║  │ ●━━━━━━━━━━━━━━━━━━━━━━━●    │    ║
║  │ $35                     $55   │    ║
║  │                               │    ║
║  │ ✓ $35 · NETA Brookline       │    ║  teal, highlighted
║  │   $40 · Berkshire Roots       │    ║  muted
║  │   $48 · The Botanist          │    ║  muted
║  │   $55 · Theory Wellness       │    ║  amber, faded
║  │                               │    ║
║  │ Save $20          Share ↗     │    ║
║  └───────────────────────────────┘    ║
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │ Fernway Strawberry Cough      │    ║  SECOND RESULT
║  │ 0.5g Cart                     │    ║
║  │                               │    ║
║  │ ●━━━━━━━━━━━━━━━●            │    ║
║  │ $32              $50          │    ║
║  │                               │    ║
║  │ ✓ $32 · CommCan Lowell       │    ║
║  │   +2 more stores              │    ║
║  │                               │    ║
║  │ Save $18          Share ↗     │    ║
║  └───────────────────────────────┘    ║
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │ [More results...]             │    ║
║  └───────────────────────────────┘    ║
║                                       ║
╚═══════════════════════════════════════╝
```

**Key UX details for search results:**

- **On mobile, show ALL stores expanded by default** for the first 2 results. Results 3+ collapse to "cheapest + X more stores."
- **Sort toggle** between "Biggest savings" and "Lowest price" — small, top-right, not prominent. Default is savings.
- **"Near me" radius** indicator in nav: `📍 4mi` — tapping opens a slider to adjust radius (2mi, 5mi, 10mi, 25mi, Statewide).
- **No pagination.** Infinite scroll with 20 results per batch. Most searches return < 50 results anyway.
- **Empty state:** If no results, show: "No results for '[query]'. Try a different search." + Popular searches below. No "Oops!" no sad face emoji. Just clear direction.

### 10.3 Product Detail Page — Mobile (375 × 812)

```
╔═══════════════════════════════════════╗
║  ← Back                       Share ↗║  48px nav
╠═══════════════════════════════════════╣
║                                       ║
║  Fernway                              ║  14px, #888892
║  Berry Gelato                         ║  24px, Inter 700, #F0F0F0
║  0.5g Cartridge                       ║  14px, #888892
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  PRICE COMPARISON                     ║  12px, all-caps, #888892
║  5 stores · Updated today             ║  12px, #555560
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │                               │    ║
║  │  ✓ $35   NETA Brookline      │    ║  CHEAPEST — bg: teal/10%
║  │          Brookline · 4.2 mi   │    ║  border-left: 3px teal
║  │                               │    ║
║  ├───────────────────────────────┤    ║
║  │    $40   Berkshire Roots      │    ║  Standard row
║  │          Pittsfield · 6.1 mi  │    ║  border-left: none
║  ├───────────────────────────────┤    ║
║  │    $42   CommCan              │    ║
║  │          Lowell · 8.3 mi      │    ║
║  ├───────────────────────────────┤    ║
║  │    $48   The Botanist         │    ║
║  │          Worcester · 2.8 mi   │    ║
║  ├───────────────────────────────┤    ║
║  │  ⚠ $55   Theory Wellness     │    ║  MOST EXPENSIVE
║  │          Great Barrington     │    ║  amber text, subtle
║  │          5.7 mi               │    ║
║  │                               │    ║
║  └───────────────────────────────┘    ║
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  ┌───────────────────────────────┐    ║  THE SAVINGS BOX
║  │                               │    ║  bg: #141416
║  │  You'd save $20               │    ║  20px, Inter 700
║  │  buying at NETA instead       │    ║  14px
║  │  of Theory.                   │    ║
║  │                               │    ║
║  │  ●━━━━━━━━━━━━━━━━━━━━━━●    │    ║  Price bar
║  │  $35                    $55   │    ║
║  │  cheapest            highest  │    ║  10px, muted
║  │  median: $42                  │    ║
║  │                               │    ║
║  │  ┌───────────┐ ┌───────────┐ │    ║
║  │  │Share Price │ │ Get Alert │ │    ║  Two buttons
║  │  └───────────┘ └───────────┘ │    ║  bg: white/#0A0A0B
║  │                               │    ║
║  └───────────────────────────────┘    ║
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  PRODUCT INFO                         ║  12px header
║                                       ║
║  Brand       Fernway                  ║  Simple key-value
║  Category    Cartridge                ║
║  Weight      0.5g                     ║
║  Stores      5                        ║
║  Platforms   Dutchie · Jane · Leafly  ║
║  Updated     Today                    ║
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  MORE FROM FERNWAY                    ║
║                                       ║
║  Strawberry Cough 0.5g Cart           ║  Mini cards
║  $32 – $50 · 4 stores                ║
║                                       ║
║  Blue Dream 0.5g Cart                 ║
║  $38 – $48 · 3 stores                ║
║                                       ║
╚═══════════════════════════════════════╝
```

### 10.4 Store Page — Mobile

```
╔═══════════════════════════════════════╗
║  ← Back                              ║
╠═══════════════════════════════════════╣
║                                       ║
║  NETA                                 ║  24px, bold
║  Brookline, MA · 4.2 mi              ║  14px, muted
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  PRICE POSITION                       ║  12px header
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │                               │    ║
║  │  ✓ Cheapest   █████████ 42%  │    ║  teal bar
║  │    Mid-range   ███████  35%   │    ║  white bar
║  │  ⚠ Highest    ████     23%   │    ║  amber bar
║  │                               │    ║
║  │  vs. all MA dispensaries      │    ║  10px, muted
║  └───────────────────────────────┘    ║
║                                       ║
╠═══════════════════════════════════════╣
║                                       ║
║  ┌────┐┌────┐┌────┐┌────┐            ║  Category tabs
║  │All ││Flwr││Cart││Edib│            ║
║  └────┘└────┘└────┘└────┘            ║
║                                       ║
║  47 products                          ║
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │ Fernway Berry Gelato 0.5g     │    ║
║  │ $35 here · median $42         │    ║
║  │ 🏷️ CHEAPEST IN MA             │    ║  teal badge
║  └───────────────────────────────┘    ║
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │ Cookies Gary Payton 3.5g      │    ║
║  │ $55 here · median $45         │    ║
║  │ ⚠️ $10 ABOVE MEDIAN           │    ║  amber badge
║  └───────────────────────────────┘    ║
║                                       ║
║  ┌───────────────────────────────┐    ║
║  │ [More products...]            │    ║
║  └───────────────────────────────┘    ║
║                                       ║
╚═══════════════════════════════════════╝
```

### 10.5 Desktop Layout (1440px)

**Desktop mirrors mobile but uses the extra width for a two-column layout:**

```
┌────────────────────────────────────────────────────────────────────┐
│  GLASS                                📍 Brookline, MA    About   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  EVERY DISPENSARY. EVERY PRICE. UPDATED DAILY.                     │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │ 🔍  Search any product... "Fernway cart" "cheapest 8th" │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                    │
│  All · Flower · Carts · Edibles · Pre-Rolls · Concentrates        │
│                                                                    │
├────────────────────────────────┬───────────────────────────────────┤
│                                │                                   │
│  🔥 BIGGEST PRICE GAPS        │  📍 MAP VIEW                     │
│                                │                                   │
│  [Product Card 1]              │  ┌───────────────────────────┐   │
│                                │  │                           │   │
│  [Product Card 2]              │  │    [Mapbox dark map]      │   │
│                                │  │    with dispensary pins    │   │
│  [Product Card 3]              │  │    showing prices          │   │
│                                │  │                           │   │
│  [Product Card 4]              │  │                           │   │
│                                │  └───────────────────────────┘   │
│  [Product Card 5]              │                                   │
│                                │  POPULAR BRANDS                   │
│                                │  Fernway · Good Chemistry ·      │
│                                │  Cookies · PAX · Cresco          │
│                                │                                   │
├────────────────────────────────┴───────────────────────────────────┤
│  DEALS BY CITY                                                     │
│  Boston · Cambridge · Worcester · Springfield · Cape Cod           │
├────────────────────────────────────────────────────────────────────┤
│  Footer                                                            │
└────────────────────────────────────────────────────────────────────┘
```

**Desktop product detail page:**
- Left column (60%): Price comparison list + savings box
- Right column (40%): Product info + "More from this brand" + map showing store locations
- Sticky header with product name when scrolled past

---

## 11. The Name & Tagline

### The Name

**GLASS Prices**

Why it works:
- "GLASS" = the parent brand (GLASS Intel). But on the consumer site, we just say "GLASS."
- "Prices" is literal. It's what the site does. No ambiguity.
- Together: "GLASS Prices" feels like "Google Flights" or "Amazon Prices" — a known brand + a specific function.
- In conversation: "Check GLASS for the price." "I found it on GLASS." Short, memorable, one syllable.

Why not something else:
- ❌ "PriceCheck" — too generic, sounds like an app from 2012
- ❌ "BudgetBud" — cannabis pun, violates our anti-culture rule
- ❌ "CannCompare" — clunky, forgettable
- ❌ "GLASS Intel Prices" — too long, "Intel" is B2B language

**The brand name on the site is just "GLASS."** Not "GLASS Intel," not "GLASS Prices." Just GLASS. The URL and context make it clear this is the price comparison tool.

### The Tagline

**Primary (appears on site):**
> **Every dispensary. Every price.**

Why: It's a promise. It's specific. It tells you what you'll get. It doesn't try to be clever.

**Secondary (for social/PR/about page):**
> **Same product. Different price. Now you know.**

Why: It captures the controversy. The first two sentences are the problem. The third is the solution. It's the "you'd pay $20 more" concept in tagline form.

**NOT used:**
- ❌ "The smarter way to buy cannabis" — implies everyone else is dumb
- ❌ "Disrupting cannabis retail" — startup cringe
- ❌ "Your price advantage" — sounds like a coupon app
- ❌ "Transparency for every tray" — trying too hard to be clever
- ❌ Anything with "powered by" or "built with" or "using"

### URL Structure

```
glassintel.xyz/prices                    → Main landing
glassintel.xyz/prices?q=fernway+cart     → Search
glassintel.xyz/prices/gpid/[slug]        → Product detail
glassintel.xyz/prices/brand/[slug]       → Brand page
glassintel.xyz/prices/store/[slug]       → Store page
glassintel.xyz/prices/[city]             → City deals
glassintel.xyz/prices/deals/[date-slug]  → Weekly deals
glassintel.xyz/prices/about              → About page
glassintel.xyz/prices/dispensaries       → "For Dispensaries" (V2 hook)
```

**Future consideration:** If GLASS Prices becomes big enough, it moves to its own domain: `glassprices.com` or `pricesglass.com`. But for V1, keeping it under `glassintel.xyz` is fine — it leverages whatever SEO authority the parent domain has.

---

## 12. Launch Playbook

### Phase 0: Pre-Launch (Before any public URL)

1. ✅ Consumer API endpoints working and tested
2. ✅ Scrapers running daily with 90%+ success rate
3. ✅ 300+ GPIDs verified and matched
4. Build the frontend (this doc is the spec)
5. Load test with realistic traffic patterns
6. Manual QA of 50 random product pages for data accuracy
7. OG image generation working for all page types

### Phase 1: Soft Launch (Week 1)

- **Deploy to production** at `glassintel.xyz/prices`
- **No announcement.** Just let Google index it.
- **Share with 5-10 trusted cannabis buyers** for feedback
- **Fix every bug and data issue** they find
- **Monitor:** Page load times, API response times, error rates

### Phase 2: Community Launch (Week 2-3)

- **One Reddit post** in r/bostontrees — personal, not promotional
  > "Built a site that compares cannabis prices across every dispensary in MA. Wanted to share it because I got tired of checking 3 different apps. [link] Let me know what's useful and what sucks."
- **Monitor Reddit comments** — respond to every question honestly
- **Fix issues in real-time** based on feedback
- **Track:** DAU, searches per session, most-searched products

### Phase 3: Growth (Week 4+)

- **SEO starts compounding** — 1000+ indexed pages with unique price data
- **Weekly deal pages** auto-publish every Monday
- **Price alerts** launch (email only)
- **"Share Price" cards** go live
- **Monitor:** Organic search traffic, share rate, alert signups

### Phase 4: Monetization Prep (Month 3+)

- **"For Dispensaries" page** goes live with "Claim Your Store" CTA
- **Outbound to dispensaries** whose store pages are getting traffic
- **Featured placement** beta with 3-5 willing dispensaries
- **Track:** Store claim rate, featured conversion rate, dispensary engagement

---

## Appendix A: "How Prices Work" Page Content

This is the ONLY page that explains anything about the product. It lives at `/prices/about` and is linked from the footer.

**Content:**

> ### How GLASS Prices Work
>
> We check every dispensary menu in Massachusetts every day and compare prices on the same products across different stores.
>
> **Where do the prices come from?**
> From the public online menus that dispensaries publish on Dutchie, Jane, Leafly, and Weedmaps. These are the same prices you'd see if you visited each store's website individually. We just put them all in one place.
>
> **How do you know it's the same product?**
> We match products by brand, strain, form, and weight. When we confirm a match, we give it a unique product ID (we call it a GPID). Only verified matches appear on the site.
>
> **How fresh are the prices?**
> Prices are checked daily. Every page shows when it was last updated. If a price is more than 48 hours old, we label it as "aging" so you know to verify.
>
> **Is this free?**
> Yes. No account required. No app to download. Just prices.
>
> **I'm a dispensary and my prices are wrong.**
> Email us at prices@glassintel.xyz and we'll investigate immediately. We want accuracy above everything.

That's it. No tech explanation. No "our proprietary algorithm." No "machine learning pipeline." Just honest answers to honest questions.

---

## Appendix B: Component Library Spec

**Reusable components needed (shadcn/ui base + custom):**

| Component | Base | Custom Behavior |
|-----------|------|----------------|
| `SearchBar` | `Input` | 56px tall, search icon, debounced typeahead |
| `CategoryChips` | `Toggle Group` | Horizontal scroll, single select, URL-synced |
| `PriceRangeBar` | Custom | SVG bar with gradient, min/max labels |
| `ProductCard` | `Card` | Brand, strain, form, price bar, store list |
| `StoreRow` | Custom | Store name, city, distance, price, cheapest badge |
| `SavingsBox` | `Card` | Savings amount, price bar, share + alert buttons |
| `ShareCard` | Custom | OG image generator, canvas-based |
| `PriceAlert` | `Dialog` | Email input + target price input |
| `CityCard` | `Card` | City name, store count, link |
| `BrandHeader` | Custom | Brand name, product count, store count |
| `StoreHeader` | Custom | Store name, city, distance, price position |
| `PricePositionBar` | Custom | Horizontal bar chart (cheapest/mid/highest %) |
| `NearMeToggle` | `Switch` | Geo toggle with radius selector |
| `MapView` | Mapbox GL | Dark style, price pins, mini cards |

---

## Appendix C: Data Requirements for Launch

**Minimum data thresholds before going public:**

| Metric | Minimum | Ideal | Current |
|--------|---------|-------|---------|
| Verified GPIDs | 200 | 500+ | ~500 |
| Stores with prices | 200 | 400+ | ~385 |
| Daily scrape success | 80% | 95%+ | ~61% (needs fix) |
| Categories covered | 4+ | 6+ | TBD |
| Price freshness (< 48h) | 70% | 90%+ | TBD |
| Brands represented | 30+ | 100+ | TBD |
| Avg stores per GPID | 2+ | 4+ | TBD |

**Critical path items:**
1. Fix Weedmaps scraper (94% failure rate → needs < 20%)
2. Fix Dutchie scraper stability (Camoufox crashes)
3. Add Jane and Leafly scrapers for coverage
4. Verify GPID matching accuracy > 95%
5. Build new API endpoints (deals/top, store/:slug, cities, suggest)

---

## Appendix D: Metrics & Success Criteria

**North Star Metric:** Weekly unique users who complete a price comparison (view a GPID page).

**Leading Indicators:**
- Searches per session (target: 2+)
- GPID pages viewed per session (target: 3+)
- Share rate (target: 5% of GPID views generate a share)
- Return rate (target: 30% weekly return)
- Alert signup rate (target: 2% of GPID views)

**Lagging Indicators:**
- Weekly active users
- Organic search traffic
- Store claim rate (V2)
- Revenue (V2)

**Tracking:** Plausible for page views, custom events for searches/shares/alerts. No cookies, no consent banner, no tracking pixels.

---

*This document is the complete blueprint. Every decision is intentional. Every omission is intentional. Build exactly this, nothing more, nothing less. Ship it, then iterate based on what real humans do.*

**The only question that matters: does this help a buyer find the cheapest price faster?**

If yes, ship it. If no, kill it.
