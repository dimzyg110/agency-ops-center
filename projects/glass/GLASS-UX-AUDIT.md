# GLASS UX Audit & Redesign Plan
**Version 1.0 | February 2026**
**Theme: Bloomberg Terminal meets Apple**

---

## Executive Summary

GLASS currently has a functional but uninspired interface that fails to communicate the premium, high-stakes nature of cannabis market intelligence. The product works, but it doesn't *feel* like the critical operating system it claims to be.

**The Core Problem:** The current design looks like a generic admin dashboard. It lacks the authority, precision, and urgency that operators need when making pricing decisions worth thousands of dollars.

**The Solution:** A radical visual and structural overhaul that positions GLASS as the Bloomberg Terminal of cannabis—premium, dark, data-dense but clean, with zero friction onboarding and immediate value delivery.

---

## Part A: Current State Audit

### What's Working
- **Functional dashboard** with Morning Brief, Price Wire, Threat Radar, Recommendations
- **Dark mode base** (gray-950) is appropriate for data-heavy interfaces
- **Clerk auth** provides secure, low-friction authentication
- **Real-time data** display with price movers and sparklines
- **Responsive layout** works on mobile and desktop

### What's Broken
1. **NO PUBLIC LANDING PAGE** — The site immediately redirects to authentication. Zero marketing presence.
2. **Generic visual identity** — Green "G" logo looks like a grocery app, not intelligence software
3. **Weak typography hierarchy** — Everything feels the same weight
4. **Cluttered dashboard** — Too many competing elements, no clear focal point
5. **Missing onboarding flow** — No progressive disclosure, users land in a complex dashboard
6. **No instant value** — First-time users see empty/mock data instead of real market intelligence
7. **Weak CTAs** — "View All" links instead of action-driving buttons
8. **Missing retention hooks** — No visible newsletter, no delivery waitlist, no community

### Critical Missing Pages
- Public marketing landing page
- Newsletter signup
- Delivery waitlist
- RSS/Industry news feed
- Proper onboarding wizard
- Feature-specific landing pages

---

## Part B: Branding & Visual Identity Redesign

### Design Philosophy: "Command Intelligence"

**The Feel:**
- Bloomberg Terminal precision + Apple simplicity + Fintech urgency
- Dark, immersive, focused
- Every pixel communicates: "This is where serious operators work"

### Color Palette (LOCKED)

```css
/* Primary Brand Colors */
--glass-accent: #00F0C8;        /* Electric teal — CTAs, highlights, active states */
--glass-accent-dim: #00B89A;    /* Hover states */
--glass-accent-glow: rgba(0, 240, 200, 0.15);  /* Subtle glows */

/* Background Hierarchy */
--bg-base: #0A0A0F;             /* Deepest black — page background */
--bg-elevated: #111118;         /* Cards, modals */
--bg-hover: #1A1A24;            /* Hover states */
--bg-active: #222230;           /* Active/selected states */

/* Border & Divider */
--border-subtle: rgba(255, 255, 255, 0.06);
--border-medium: rgba(255, 255, 255, 0.1);
--border-accent: rgba(0, 240, 200, 0.3);

/* Text Hierarchy */
--text-primary: #FFFFFF;
--text-secondary: rgba(255, 255, 255, 0.7);
--text-tertiary: rgba(255, 255, 255, 0.5);
--text-muted: rgba(255, 255, 255, 0.3);

/* Semantic Colors */
--success: #00D084;             /* Price down (good for buyer) */
--danger: #FF4766;              /* Price up, threats, critical */
--warning: #FFB800;             /* Medium priority */
--info: #3391FF;                /* Neutral information */
```

**Color Usage Rules:**
- Only `--glass-accent` for primary CTAs and brand moments
- Red is for threats, urgent alerts ONLY
- Green is for positive trends, success states
- 80% of UI should use neutral grays
- Gradients are forbidden (except subtle glow effects)

### Typography System (LOCKED)

```css
/* Font Stack */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
font-feature-settings: 'tnum' 1;  /* Tabular numbers for data */

/* Scale */
--text-hero: 48px / 1.1 / -0.02em / font-weight: 700;
--text-h1: 32px / 1.2 / -0.01em / font-weight: 700;
--text-h2: 24px / 1.3 / 0 / font-weight: 600;
--text-h3: 18px / 1.4 / 0 / font-weight: 600;
--text-body: 14px / 1.6 / 0 / font-weight: 400;
--text-small: 12px / 1.5 / 0 / font-weight: 400;
--text-micro: 11px / 1.4 / 0.02em / font-weight: 500;  /* uppercase labels */

/* Data Typography */
--data-large: 36px / 1 / -0.02em / font-weight: 600;    /* Hero metrics */
--data-medium: 24px / 1.2 / -0.01em / font-weight: 500; /* Stat cards */
--data-small: 14px / 1 / 0 / font-weight: 500;          /* Table data */
```

### Logo & Wordmark Direction

**Abandon the "G" icon.** It looks like Gmail or a grocery chain.

**New Direction:**
```
GLΛSS
    ↑
    Lambda replaces A — signals analytical, intelligent, premium
```

**Logo Usage:**
- Primary: Wordmark "GLΛSS" in all caps, custom logotype
- Icon: Abstract prism/glass shard shape (suggests clarity, refraction, intelligence)
- Never use the green circle "G" again

**Wordmark Specs:**
- Font: Custom or Inter Black with modified "A"
- Color: White on dark, or accent teal when highlighted
- Clearspace: Minimum 1x height on all sides

---

## Part C: Information Architecture & Page Structure

### New Site Map

```
/
├── / (Public Landing — NEW)
│   ├── Hero: "See what your competitors charge before your customers do"
│   ├── Social proof (logos, testimonials)
│   ├── Feature grid (Price Wire, Threat Radar, Margin Engine, Morning Brief)
│   ├── Secondary CTAs (Newsletter, Delivery waitlist)
│   └── Footer
│
├── /signup (Enhanced — NEW FLOW)
│   ├── Step 1: Email + Password (or Google)
│   ├── Step 2: Dispensary Name + City
│   └── Step 3: Instant Dashboard (show real data immediately)
│
├── /onboarding (NEW — Progressive)
│   ├── WelcomeScreen: "Here's your market"
│   ├── ConnectMenu: Dutchie/Leafly/IHeartJane
│   ├── SetMarginRules: Optional
│   └── Complete: Full dashboard unlocked
│
├── /app/* (Authenticated Dashboard)
│   ├── /app/ (Morning Brief — redesigned)
│   ├── /app/prices (Price Wire — enhanced)
│   ├── /app/threats (Threat Radar — enhanced)
│   ├── /app/recommendations (Margin Engine — enhanced)
│   ├── /app/alerts (Notifications center — enhanced)
│   └── /app/settings (Account management)
│
├── /newsletter (NEW PAGE)
│   ├── Subscribe form
│   ├── Benefits list
│   └── Archive of past issues
│
├── /delivery (NEW PAGE)
│   ├── Zip code checker
│   ├── Conditional: Available / Waitlist
│   └── Waitlist signup form
│
└── /intel (NEW PAGE — replaces RSS)
    ├── Curated cannabis news
    ├── CCC regulatory updates
    └── Market data highlights
```

---

## Part D: Page-by-Page Redesign Specifications

### PAGE 1: Public Landing Page (NEW — Highest Priority)

**Purpose:** Convert anonymous visitors to signups in under 60 seconds.

**Wireframe Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  [GLΛSS Logo]                              [Sign In] [Get Free] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     MASSACHUSETTS CANNABIS INTELLIGENCE                         │
│                                                                 │
│     See what your competitors charge                            │
│     before your customers do                                    │
│                                                                 │
│     [Start Free — Get Price Wire in 60 seconds]                 │
│                                                                 │
│     No credit card required • Free for operators                │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│     Trusted by 50+ Massachusetts operators                      │
│     [LOGO] [LOGO] [LOGO] [LOGO] [LOGO]                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  THE ONLY DASHBOARD YOU NEED                                    │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ PRICE WIRE  │  │THREAT RADAR │  │MARGIN ENGINE│             │
│  │             │  │             │  │             │             │
│  │ Real-time   │  │ AI-powered  │  │ AI pricing  │             │
│  │ competitor  │  │ threat      │  │ recommendations           │
│  │ pricing     │  │ detection   │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  YOUR MORNING BRIEF, DELIVERED AT 6 AM                          │
│                                                                 │
│  Every day, get a summary of:                                   │
│  • Price movers in your area                                    │
│  • New competitive threats                                      │
│  • Recommended price adjustments                                │
│                                                                 │
│  [Get the Daily Brief]                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  COMING SOON: DELIVERY                                          │
│                                                                 │
│  Check if we're in your area:                                   │
│  [Enter ZIP code]  [Check Availability]                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  GLΛSS                                                          │
│  [Morning Brief] [Price Wire] [Threat Radar] [Margin Engine]    │
│  [Newsletter] [Delivery] [Help Center]                          │
│                                                                 │
│  © 2026 GLASS Intelligence. Built for Massachusetts operators.  │
└─────────────────────────────────────────────────────────────────┘
```

**Hero Copy:**
- Headline: "See what your competitors charge before your customers do"
- Subheadline: "Massachusetts cannabis intelligence. Real-time pricing, threat detection, and AI-powered recommendations."
- CTA Primary: "Start Free — Get Price Wire in 60 seconds"
- CTA Secondary: "See how it works" (scrolls to demo/video)

**Technical Specs:**
- Full viewport height hero with subtle animated gradient background (deep black to faint teal)
- Floating dashboard mockup/screenshot to right of hero text (absolute positioned)
- Smooth scroll navigation
- Exit intent popup: "Wait — get the Weekly Intel free"

---

### PAGE 2: Signup Flow (Redesigned)

**Current Problem:** Straight to Clerk widget, no context, no value promise.

**New Flow:**

```
STEP 1: Account Creation
┌─────────────────────────────────────────────┐
│                                             │
│      GLΛSS                                  │
│                                             │
│      Join 50+ operators getting             │
│      real-time market intelligence          │
│                                             │
│      ┌─────────────────────────────────┐   │
│      │ Continue with Google            │   │
│      └─────────────────────────────────┘   │
│                                             │
│      ───────────── OR ─────────────        │
│                                             │
│      Email                                  │
│      ┌─────────────────────────────────┐   │
│      │ you@dispensary.com              │   │
│      └─────────────────────────────────┘   │
│                                             │
│      Password                               │
│      ┌─────────────────────────────────┐   │
│      │ ••••••••••••••                │   │
│      └─────────────────────────────────┘   │
│                                             │
│      ┌─────────────────────────────────┐   │
│      │ Continue →                      │   │
│      └─────────────────────────────────┘   │
│                                             │
│      Already have an account? Sign in       │
│                                             │
└─────────────────────────────────────────────┘

STEP 2: Dispensary Info
┌─────────────────────────────────────────────┐
│                                             │
│      Tell us about your business            │
│                                             │
│      Dispensary Name *                      │
│      ┌─────────────────────────────────┐   │
│      │ Green Leaf Dispensary           │   │
│      └─────────────────────────────────┘   │
│                                             │
│      City *                                 │
│      ┌─────────────────────────────────┐   │
│      │ Boston                          │   │
│      └─────────────────────────────────┘   │
│                                             │
│      [Complete Setup →]                     │
│                                             │
└─────────────────────────────────────────────┘

STEP 3: Instant Value (THE MOMENT)
┌─────────────────────────────────────────────┐
│                                             │
│      Welcome to GLΛSS, [Name]               │
│                                             │
│      Here's what's happening in             │
│      your market right now:                 │
│                                             │
│      ┌─────────────────────────────────┐   │
│      │ ⚠️ PRICE ALERT                  │   │
│      │ 3 competitors dropped GMO       │   │
│      │ prices today                    │   │
│      │                                 │   │
│      │ Current lowest: $42/8th         │   │
│      └─────────────────────────────────┘   │
│                                             │
│      ┌─────────────────────────────────┐   │
│      │ 📈 TOP MOVER                    │   │
│      │ Wedding Cake up 12% at          │   │
│      │ Curaleaf Newton                 │   │
│      └─────────────────────────────────┘   │
│                                             │
│      ┌─────────────────────────────────┐   │
│      │ 🎯 NEW THREAT                   │   │
│      │ License application filed       │   │
│      │ 0.8 miles from you              │   │
│      └─────────────────────────────────┘   │
│                                             │
│      [View Your Dashboard →]                │
│                                             │
│      Get daily briefs + Connect your menu   │
│                                             │
└─────────────────────────────────────────────┘
```

**Copy Guidelines:**
- NO "Submit" — use action language: "Continue", "Complete Setup", "View Dashboard"
- Show real (cached) data for their city immediately after signup
- Make them FEEL the value before asking for more info

---

### PAGE 3: Morning Brief (Redesigned Dashboard)

**Current Problems:**
- Too many elements competing for attention
- No clear visual hierarchy
- Weak data visualization

**New Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  [≡]  MORNING BRIEF                      [🔍] [🔔 3] [👤]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Wednesday, February 12, 2026                    STATUS: LIVE   │
│                                                                 │
│  ┌──────────────────┬──────────────────┬──────────────────┐  │
│  │  2,847           │  156             │  3               │  │
│  │  Products        │  Price Changes   │  Active Threats  │  │
│  │  Tracked         │  24h             │  ⚠️ 1 Critical   │  │
│  └──────────────────┴──────────────────┴──────────────────┘  │
│                                                                 │
│  ─── PRICE WIRE ─────────────────────────────────────────────   │
│                                                                 │
│  Top Movers (24h)                                [View All →]   │
│                                                                 │
│  PRODUCT              OPERATOR           CHANGE    PRICE        │
│  ─────────────────────────────────────────────────────────      │
│  Wedding Cake         Curaleaf Newton    ▲ 12.4%   $52.00    📈 │
│  GMO                  Rise Amherst       ▼ 8.2%    $38.00    📉 │
│  Blue Dream           NETA Brookline     ▲ 5.1%    $45.00    📈 │
│                                                                 │
│  ─── THREAT RADAR ────────────────────────────────────────────  │
│                                                                 │
│  🔴 New competitor license application 0.8 mi away    [View]    │
│  🟡 High: Price pressure detected in Vape category    [View]    │
│                                                                 │
│  ─── RECOMMENDATIONS ─────────────────────────────────────────  │
│                                                                 │
│  Lower Sour D price to match market        [Apply] [Edit] [✕]   │
│  Expected impact: +$340/week margin                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Changes:**
1. **Single column layout** on desktop (readable, focused)
2. **Large hero metrics** at top — the numbers that matter
3. **Table-based Price Wire** — easier to scan than cards
4. **Inline actions** on recommendations — Apply/Edit/Dismiss without navigation
5. **Sticky date/status bar** — always know data freshness
6. **Reduced card styling** — flat design with subtle borders only

**Component Specs:**

```typescript
// Hero Metric Component
interface HeroMetricProps {
  value: string | number;
  label: string;
  status?: 'neutral' | 'positive' | 'negative' | 'warning';
  trend?: { value: number; direction: 'up' | 'down' };
}

// Style
.hero-metric {
  padding: 24px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
}
.hero-metric-value {
  font-size: 36px;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}
```

---

### PAGE 4: Price Wire (Enhanced)

**New Features to Add:**
1. **Map view toggle** — See competitor locations geographically
2. **Price position indicator** — "You're priced higher than 72% of competitors"
3. **Watchlist quick-add** — Star any product to track it
4. **Export to CSV** — Already exists, enhance with filtering

**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  PRICE WIRE                                          [Map/List] │
│  Real-time pricing across Massachusetts                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Filter: [All Categories ▼]  [Search products...    ] 🔍   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  PRODUCT          CATEGORY    PRICE    COMPETITOR RANGE  TREND │
│  ──────────────────────────────────────────────────────────────│
│  Wedding Cake 8th Flower      $52.00   $42 - $58        ↑ 12% │
│  ☆ GMO 8th       Flower       $45.00   $38 - $48        ↓ 8%  │
│  Blue Dream 8th  Flower       $45.00   $40 - $50        → 0%  │
│                                                                 │
│  Price position: You're higher than 65% of competitors         │
│  [Adjust Pricing] [Download Report]                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### PAGE 5: Threat Radar (Enhanced)

**New Features:**
1. **Distance-based visualization** — How close is this threat?
2. **Impact scoring** — "High impact: Direct competitor"
3. **Timeline view** — When did these threats emerge?
4. **Alert configuration** — Set custom threat thresholds

**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  THREAT RADAR                                        [⚙️ Alert] │
│  AI-powered competitive intelligence                            │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ 🔴 1        │ │ 🟡 3        │ │ 🔵 8        │               │
│  │ CRITICAL    │ │ HIGH        │ │ MEDIUM      │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                 │
│  ────────────────────────────────────────────────────────────   │
│                                                                 │
│  🔴 CRITICAL — New License Application                          │
│  ─────────────────────────────────────────                      │
│  Green Valley Cannabis                                          │
│  0.8 miles from your location (Newton)                          │
│  Impact score: 94/100 (Direct competitor, close proximity)      │
│                                                                 │
│  Detected: Feb 10, 2025        [View CCC Filing] [Set Alert]    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### PAGE 6: Newsletter Page (NEW)

**Purpose:** Capture emails for users not ready to sign up for the full platform.

```
┌─────────────────────────────────────────────────────────────────┐
│  GLASS WEEKLY INTEL                                             │
│  The cannabis market briefing Massachusetts operators read      │
│                                                                 │
│  Every Friday, get:                                             │
│  ✓ Top price movers of the week                                 │
│  ✓ New license applications & competitive threats               │
│  ✓ Regulatory updates from the CCC                              │
│  ✓ Anonymous operator case studies                              │
│                                                                 │
│  ┌─────────────────────────────────┐  ┌─────────────────────┐  │
│  │ your@email.com                  │  │ Subscribe Free →    │  │
│  └─────────────────────────────────┘  └─────────────────────┘  │
│                                                                 │
│  Join 1,200+ operators. Unsubscribe anytime.                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  LATEST ISSUES                                                  │
│                                                                 │
│  Feb 7: Price War Erupts in Western Mass                       │
│  Jan 31: New Licenses Filed in Boston Metro                     │
│  Jan 24: Q4 Margin Analysis Report                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### PAGE 7: Delivery Waitlist (NEW)

```
┌─────────────────────────────────────────────────────────────────┐
│  GLASS DELIVERY                                                 │
│  Cannabis delivery, powered by your intelligence                │
│                                                                 │
│  Check availability in your area:                               │
│                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────┐      │
│  │ Enter ZIP code          │  │ Check Availability      │      │
│  └─────────────────────────┘  └─────────────────────────┘      │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  [IF AVAILABLE]:                                                │
│  ✅ We're delivering to 02134!                                  │
│  [Get Started]                                                  │
│                                                                 │
│  [IF NOT AVAILABLE]:                                            │
│  📍 We're not in your area yet.                                 │
│  Be the first dispensary in [ZIP] to offer delivery.            │
│  [Join Waitlist]                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### PAGE 8: Industry Intel / RSS (NEW)

```
┌─────────────────────────────────────────────────────────────────┐
│  CANNABIS INTEL                                                 │
│  Curated news & regulatory updates                              │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ All News     │ │ Regulatory   │ │ Market Data  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                 │
│  CCC announces new social equity licensing round               │
│  Cannabis Control Commission • 2 hours ago                      │
│                                                                 │
│  Massachusetts wholesale prices drop 12% in Q1                 │
│  MJ Biz Daily • 5 hours ago                                     │
│                                                                 │
│  [Subscribe to RSS] [Get Weekly Summary]                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part E: Onboarding Flow (Step-by-Step)

### The 60-Second Rule
User must see real, valuable data within 60 seconds of landing on the site.

**New User Flow:**
```
1. LANDING PAGE
   ↓ Click "Start Free"
   
2. SIGNUP SCREEN
   ↓ Email + Password (or Google OAuth)
   
3. BUSINESS INFO
   ↓ Dispensary name + City
   
4. INSTANT VALUE SCREEN (CRITICAL)
   → Pre-populate with REAL cached data for their city
   → Show 3 specific, relevant insights:
      • "3 competitors dropped GMO prices today"
      • "Wedding Cake trending up 12% in Eastern Mass"
      • "New license filed 0.8 miles from you"
   ↓ Click "View Dashboard"
   
5. ONBOARDING CHECKLIST (in dashboard)
   [✓] Account created
   [ ] Connect your menu (Dutchie/Leafly/IHeartJane)
   [ ] Set your margin targets
   [ ] Download the mobile app
   
6. FULL DASHBOARD
   → All features accessible
   → Morning Brief already populated
```

**Technical Implementation:**
```typescript
// Pre-populate onboarding with cached data
const cachedCityData = await fetch(`/api/cached-market-snapshot?city=${userCity}`);

// Show these 3 cards on instant value screen:
interface InstantValueCard {
  type: 'price_alert' | 'trend' | 'threat';
  headline: string;
  detail: string;
  actionLabel: string;
  actionHref: string;
}

// Example cards for Boston:
const cards: InstantValueCard[] = [
  {
    type: 'price_alert',
    headline: '3 competitors dropped GMO prices',
    detail: 'Current lowest: $42/8th at Rise Amherst',
    actionLabel: 'See all prices',
    actionHref: '/app/prices'
  },
  {
    type: 'trend',
    headline: 'Wedding Cake trending up 12%',
    detail: 'Average price now $52 across Eastern Mass',
    actionLabel: 'View trend',
    actionHref: '/app/prices?product=wedding-cake'
  },
  {
    type: 'threat',
    headline: 'New license filed near you',
    detail: 'Green Valley Cannabis — 0.8 miles away',
    actionLabel: 'View threat',
    actionHref: '/app/threats'
  }
];
```

---

## Part F: Retention & Value Loop

### Email Communication Strategy

**1. Daily Morning Brief Email (6 AM)**
```
Subject: Morning Brief — 3 price alerts, 1 new threat

[GLΛSS Logo]

Wednesday, February 12

─── TODAY'S HIGHLIGHTS ───

⚠️ PRICE ALERTS (3)
• GMO down $4 at 2 competitors
• Wedding Cake up 12% market-wide

🎯 RECOMMENDATION
Lower Sour D by $3 → +$340/week margin
[Apply in Dashboard]

🔴 THREAT DETECTED
New license: Green Valley Cannabis
0.8 miles from you

[View Full Dashboard]

───
You're receiving this because you signed up for GLASS.
Unsubscribe | Update preferences
```

**2. Weekly Intel Newsletter (Friday)**
```
Subject: GLASS Weekly — Price war in Western Mass, CCC updates

[In-depth market analysis]
[Operator case study (anonymized)]
[Upcoming regulatory deadlines]

[Read Full Issue]
```

**3. Price Alert Notifications (Real-time)**
```
Push: 🚨 Curaleaf dropped Wedding Cake to $38
Email: Weekly summary of all price changes
```

**4. Monthly Margin Report**
```
Subject: Your February Margin Report

[Applied recommendations]
[Missed opportunities]
[Market position vs competitors]
[Projected revenue impact]
```

---

## Part G: Technical Implementation Plan

### Files to Modify/Create

#### 1. New Files to Create

```
src/apps/web/src/
├── pages/
│   ├── Landing.tsx              # Public landing page (NEW)
│   ├── Newsletter.tsx           # Newsletter signup (NEW)
│   ├── Delivery.tsx             # Delivery waitlist (NEW)
│   ├── Intel.tsx                # Industry news/RSS (NEW)
│   ├── Onboarding.tsx           # Post-signup flow (NEW)
│   └── OnboardingInstantValue.tsx # Real data preview (NEW)
│
├── components/
│   ├── HeroMetric.tsx           # Large stat display (NEW)
│   ├── SectionHeader.tsx        # Consistent section headers (NEW)
│   ├── PriceTable.tsx           # Enhanced table component (ENHANCE)
│   └── Navigation/
│       ├── MarketingNav.tsx     # Public nav (NEW)
│       └── AppNav.tsx           # Dashboard nav (REFACTOR)
│
├── styles/
│   └── design-system.css        # Centralized tokens (NEW)
│
└── hooks/
    └── useCachedMarketData.ts   # Pre-fetch city data (NEW)
```

#### 2. Files to Modify

**tailwind.config.ts:**
```typescript
// NEW COLORS
const config: Config = {
  theme: {
    extend: {
      colors: {
        // Brand
        glass: {
          DEFAULT: '#00F0C8',
          dim: '#00B89A',
          glow: 'rgba(0, 240, 200, 0.15)',
        },
        // Backgrounds
        base: '#0A0A0F',
        elevated: '#111118',
        hover: '#1A1A24',
        active: '#222230',
        // Semantic
        success: '#00D084',
        danger: '#FF4766',
        warning: '#FFB800',
        info: '#3391FF',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'hero': ['48px', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'data-lg': ['36px', { lineHeight: '1', letterSpacing: '-0.02em' }],
        'data-md': ['24px', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
      },
    },
  },
}
```

**index.css — New Tokens:**
```css
@layer base {
  :root {
    /* Brand */
    --glass-accent: #00F0C8;
    --glass-dim: #00B89A;
    --glass-glow: rgba(0, 240, 200, 0.15);
    
    /* Background */
    --bg-base: #0A0A0F;
    --bg-elevated: #111118;
    --bg-hover: #1A1A24;
    --bg-active: #222230;
    
    /* Borders */
    --border-subtle: rgba(255, 255, 255, 0.06);
    --border-medium: rgba(255, 255, 255, 0.1);
    
    /* Text */
    --text-primary: #FFFFFF;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --text-tertiary: rgba(255, 255, 255, 0.5);
    --text-muted: rgba(255, 255, 255, 0.3);
    
    /* Semantic */
    --success: #00D084;
    --danger: #FF4766;
    --warning: #FFB800;
    --info: #3391FF;
  }
  
  body {
    @apply bg-[var(--bg-base)] text-[var(--text-primary)] antialiased;
    font-feature-settings: 'tnum' 1;
  }
}
```

**App.tsx — New Routes:**
```typescript
function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Landing />} />
      <Route path="/newsletter" element={<Newsletter />} />
      <Route path="/delivery" element={<Delivery />} />
      <Route path="/intel" element={<Intel />} />
      
      {/* Auth routes */}
      <Route path="/login" element={<PublicRoute><GlassSignIn /></PublicRoute>} />
      <Route path="/signup" element={<PublicRoute><GlassSignUp /></PublicRoute>} />
      
      {/* Onboarding */}
      <Route path="/onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
      
      {/* App routes */}
      <Route path="/app" element={<ProtectedRoute><MorningBrief /></ProtectedRoute>} />
      <Route path="/app/prices" element={<ProtectedRoute><PriceWire /></ProtectedRoute>} />
      <Route path="/app/threats" element={<ProtectedRoute><ThreatRadar /></ProtectedRoute>} />
      <Route path="/app/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
      <Route path="/app/alerts" element={<ProtectedRoute><Alerts /></ProtectedRoute>} />
      <Route path="/app/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
```

### Component Implementation Priority

**Phase 1: Foundation (Week 1)**
1. Update color tokens in Tailwind config
2. Update global CSS variables
3. Create new Logo component
4. Build MarketingNav component
5. Create Landing page shell

**Phase 2: Public Pages (Week 2)**
1. Complete Landing page
2. Build Newsletter page
3. Build Delivery page
4. Build Intel page

**Phase 3: Onboarding (Week 3)**
1. Redesign signup flow
2. Build Onboarding wizard
3. Build Instant Value screen
4. Create cached data API endpoints

**Phase 4: Dashboard Redesign (Week 4)**
1. Redesign Morning Brief
2. Update Sidebar navigation
3. Enhance Price Wire
4. Enhance Threat Radar
5. Update Settings page

**Phase 5: Polish (Week 5)**
1. Mobile responsiveness audit
2. Animation & micro-interactions
3. Performance optimization
4. Accessibility audit

---

## Part H: Responsive & Mobile Considerations

### Breakpoints
```
sm: 640px   — Small tablets
md: 768px   — Tablets
lg: 1024px  — Desktop
xl: 1280px  — Large desktop
2xl: 1536px — Ultra-wide
```

### Mobile-First Patterns

**Navigation:**
- Public pages: Hamburger menu on mobile
- Dashboard: Bottom tab bar + collapsible sidebar

**Dashboard Cards:**
```
Mobile:  Single column stack
default: Single column with horizontal scroll for tables
lg:      Two-column grid for stats, single for content
xl:      Three-column for stats, two for content
```

**Tables:**
- Mobile: Card-based display (not tables)
- Desktop: Full tables with sorting

**Touch Targets:**
- Minimum 44px touch targets
- Increased padding on mobile buttons
- Swipe gestures for common actions

---

## Part I: Performance Optimizations

### Critical Path
1. **Preload hero image** on landing page
2. **Lazy load** dashboard components below fold
3. **Code split** by route:
   ```typescript
   const PriceWire = lazy(() => import('./pages/PriceWire'));
   ```

### Data Loading
1. **Prefetch** market data on signup page
2. **Stale-while-revalidate** for price data
3. **Optimistic UI** for recommendation actions

### Bundle Size
- Tree-shake unused Lucide icons
- Use React.memo for stat cards
- Virtualize long lists (Price Wire table)

---

## Part J: Accessibility Requirements

### WCAG 2.1 AA Compliance
- Color contrast ratio: 4.5:1 minimum
- All interactive elements keyboard accessible
- Focus indicators visible (2px accent border)
- Screen reader labels on all icons
- Reduced motion support: `@media (prefers-reduced-motion: reduce)`

### Implementation
```css
/* Focus styles */
:focus-visible {
  outline: 2px solid var(--glass-accent);
  outline-offset: 2px;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Summary: The 10 Commandments of GLASS UX

1. **No public page is a death sentence.** Build the landing page first.
2. **60 seconds to value.** Show real data immediately after signup.
3. **Dark mode is brand.** No light mode switch—commit to the Bloomberg aesthetic.
4. **Typography creates hierarchy.** Use size and weight, not color, to guide attention.
5. **Data density is a feature.** Operators want information, not whitespace.
6. **Green "G" logo dies today.** Use the GLΛSS wordmark.
7. **Every page needs a single dominant CTA.** Never compete for clicks.
8. **Email is a product.** The newsletter and briefs are retention engines.
9. **Mobile is for monitoring, desktop is for action.** Design accordingly.
10. **Performance is UX.** Load in <2s or don't ship.

---

## Appendices

### A. Copy Library

**CTAs:**
- Primary: "Start Free — Get Price Wire in 60 seconds"
- Secondary: "View Dashboard"
- Tertiary: "See all prices →"

**Headlines:**
- "See what your competitors charge before your customers do"
- "The only dashboard you need"
- "Your Morning Brief, delivered at 6 AM"

**Microcopy:**
- Loading: "Loading your market intelligence..."
- Error: "Couldn't load data. [Retry]"
- Empty: "No threats detected. Check back soon."

### B. Animation Guidelines

**Timing:**
- Micro-interactions: 150ms
- Page transitions: 300ms
- Data updates: 200ms with fade

**Easing:**
- UI interactions: `cubic-bezier(0.4, 0, 0.2, 1)`
- Entrance animations: `cubic-bezier(0, 0, 0.2, 1)`
- Exit animations: `cubic-bezier(0.4, 0, 1, 1)`

### C. Image Assets Needed

1. **Logo:** GLΛSS wordmark (SVG)
2. **Hero:** Dashboard screenshot/mockup
3. **Social proof:** Partner/dispensary logos
4. **Icons:** Custom icon set for features

---

**Document Version:** 1.0
**Last Updated:** 2026-02-12
**Status:** Ready for implementation
