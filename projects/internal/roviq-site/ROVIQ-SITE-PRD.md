# ROVIQ — Product Requirements Document

**roviqai.xyz — Portfolio & Services Site**

| | |
|---|---|
| **Version** | 1.1 |
| **Date** | February 6, 2026 |
| **Author** | Randy Torres / Roviq |
| **Domain** | roviqai.xyz |
| **Design Reference** | haptic.studio |
| **Status** | Draft |

---

## 1. Overview

Roviq is a creative studio that builds marketing, design, software, and data intelligence systems for brands that want to grow. Cannabis is our deepest vertical — we've built an entire market intelligence platform tracking 150+ Massachusetts operators — but Roviq's capabilities span any industry where marketing, data, and design intersect.

The current roviqai.xyz site needs a complete rebuild into a high-impact portfolio and services site that converts visitors into leads and newsletter subscribers without traditional sales tactics.

### 1.1 Design Philosophy

Inspired by haptic.studio: bold single accent color, massive serif typography, extreme whitespace, editorial grid. The site should feel like a premium creative studio, not a niche agency. Every section earns its space. No filler, no stock photography, no generic copy.

### 1.2 Core Principles

- **Don't sell.** Build things so good people come to you.
- **Value first.** Give before you ask. Free tools, insights, case studies — all free.
- **Data-driven credibility.** Show the numbers, not just the visuals.
- **Portfolio as proof.** Every piece of client work is a conversion tool.
- **Industry depth, not limits.** Lead with capability. Let verticals prove expertise.

---

## 2. Brand & Design System

### 2.1 Color Palette

| Token | Hex | Usage |
|---|---|---|
| Primary (Roviq Red) | #D94F3D | CTAs, accent elements, hover states, section dividers |
| Background (Dark) | #1A1917 | Hero, footer, bottom-line sections, nav (scrolled) |
| Background (Warm) | #F5F2EA | Page background, card backgrounds |
| Text (Primary) | #333333 | Body copy, descriptions |
| Text (Secondary) | #666666 | Captions, metadata, supporting text |
| Text (Inverted) | #F5F2EA | White text on dark backgrounds |
| Border / Divider | #DDDDDD | Section dividers, card borders |

### 2.2 Typography

| Element | Font | Weight | Size |
|---|---|---|---|
| Hero headline | Playfair Display (serif) | 700 | 72–96px |
| Section headlines | Playfair Display (serif) | 700 | 36–48px |
| Subheadlines | Inter (sans-serif) | 600 | 20–24px |
| Body text | Inter (sans-serif) | 400 | 16–18px |
| Labels / metadata | Inter (sans-serif) | 500 | 11–12px, uppercase, letterspaced |
| Code / data | JetBrains Mono (monospace) | 400 | 14px |
| CTA buttons | Inter (sans-serif) | 600 | 14–16px, uppercase |

### 2.3 Spacing & Layout

- Max content width: 1200px (centered)
- Section padding: 120–160px vertical (desktop), 80px (mobile)
- Grid system: 12-column CSS Grid with 24px gutters
- Whitespace ratio: ≥60% of viewport should be negative space
- Breakpoints: 480px (mobile), 768px (tablet), 1024px (desktop), 1440px (wide)

---

## 3. Site Architecture & Navigation

### 3.1 Page Structure

Single-page scrolling site with anchor navigation. Smooth scroll between sections. Minimal nav that transforms on scroll.

| Section | Anchor | Purpose |
|---|---|---|
| Navigation | #nav | Fixed top bar: Logo + section links + CTA button |
| Hero | #hero | Bold statement + primary CTA |
| Work | #work | Project grid showing client deliverables across industries |
| Capabilities | #capabilities | What Roviq builds: marketing, design, dev, data, growth |
| Statement | #about | Who Roviq is, why we exist |
| Data (Vertical Spotlight) | #data | Live market intelligence showcase — cannabis as proof of depth |
| Newsletter | #newsletter | The Operator's Margin Report signup (cannabis vertical) |
| Testimonials | #testimonials | Client quotes and partner logos |
| Contact | #contact | Simple contact form |
| Footer | #footer | Links, social, legal |

---

## 4. Section Content & Specifications

### 4.1 Navigation

**Behavior**
- Default state: Transparent background, logo left, links right
- Scrolled state (>100px): Dark background (#1A1917), slight blur, compact height
- Mobile: Hamburger menu with full-screen overlay

**Elements**
- **Logo:** "ROVIQ" wordmark in Inter Bold, letterspaced
- **Links:** Work, Capabilities, Data, Newsletter, Contact
- **CTA Button:** "Let's Talk" → scrolls to #contact

### 4.2 Hero Section

**Layout**

Full viewport height. Dark background (#1A1917). Centered content. Subtle grain texture overlay at 3% opacity.

**Content**
- **Label:** "MARKETING · DATA · DESIGN · DEV" (uppercase, letterspaced, Roviq Red)
- **Headline:** "We build things that make brands money." (Playfair Display, 72–96px, warm white)
- **Subhead:** "Marketing, design, software, and data intelligence for brands that want to stop guessing and start growing." (Inter, 20px, #888)
- **Primary CTA:** "See the Work" → scrolls to #work (red button)
- **Secondary CTA:** "Get Free Market Intel" → scrolls to #newsletter (text link)

**Interactions**
- Headline fades in on load with 0.6s delay
- Scroll indicator at bottom (thin animated line)

### 4.3 Work / Portfolio Grid

**Layout**

Warm background (#F5F2EA). Asymmetric grid: alternating 2-column and full-width project cards. Each card is a high-quality screenshot/mockup with project name, client, and service tags.

**Content Per Card**
- **Image:** Full-bleed project screenshot or mockup (16:10 or 3:2 aspect ratio)
- **Project name:** e.g. "Advanced Cultivators Brand System"
- **Client:** e.g. "AC" or "Cannabis Healing"
- **Tags:** e.g. "Branding · Content · Social Media"
- **Industry tag:** e.g. "Cannabis" or "Apparel" (small pill/badge)
- **Result metric (optional):** e.g. "+340% Instagram growth" or "$3K Sprint in Week 1"

**Projects to Feature**

| Project | Client | Tags | Industry | Type |
|---|---|---|---|---|
| Brand Identity System | Advanced Cultivators | Branding, Design, Strategy | Cannabis | Full-width |
| Dispensary Marketing Engine | Cannabis Healing | Marketing, SEO, Automation | Cannabis | Half-width |
| GTM Launch Strategy | House of Pride | Branding, Website, Launch | Cannabis / Apparel | Half-width |
| Margin Pressure Snapshot Tool | Roviq (Internal) | Data, Python, Automation | Cannabis / SaaS | Full-width |
| AC Blacksite App | Advanced Cultivators | App, Dev, Content | Cannabis | Half-width |
| Cue Platform | Roviq (Core Product) | SaaS, Design, Development | Cannabis / Tech | Half-width |
| The Operator's Margin Report | Roviq Newsletter | Content, Data, Growth | Cannabis | Full-width |

> **Note:** As Roviq takes on work in other industries, new project cards slot in naturally. The grid is industry-agnostic — the work speaks for itself. Cannabis depth is proven by volume, not by limiting the label.

**Interactions**
- Cards fade in on scroll (staggered, 0.1s between)
- Hover: Image scales 1.02x, shadow deepens, project name slides up
- Click: Expands to full case study overlay (optional V2 feature)
- Optional: Filter pills at top to filter by industry or capability ("All", "Cannabis", "Branding", "Data", "Dev")

### 4.4 Capabilities

**Layout**

Warm background. Grid of 5 capability cards with icon, name, description, and example deliverables. This replaces a narrow "services + pricing" section with a broader view of what Roviq actually does.

**Capabilities**

| Capability | Description | Example Deliverables |
|---|---|---|
| **Marketing & Growth** | Strategy, content, social, SEO, paid ads, email — whatever moves the needle | Content calendars, social campaigns, SEO audits, growth playbooks, email sequences |
| **Brand & Design** | Identity systems, packaging, web design, pitch decks, visual storytelling | Logos, brand guides, packaging, UI/UX, presentations, social templates |
| **Software & Development** | Web apps, mobile apps, tools, automations, integrations, APIs | Websites, dashboards, internal tools, Chrome extensions, API integrations |
| **Data Intelligence** | Market research, competitive analysis, lead scoring, custom data pipelines | Operator intel packs, distress scoring, hiring signal monitors, enrichment pipelines |
| **Consulting & Strategy** | Operational audits, go-to-market strategy, margin optimization, growth roadmaps | 14-day sprints, 30-60-90 plans, pricing strategy, market entry playbooks |

**Pricing (shown below capabilities or on hover/expand)**

| Package | Price | What It Is |
|---|---|---|
| Sprint (14-Day) | $3,000 | Done-for-you audit + optimization — any vertical |
| Intel Pack | $500 | Data snapshot of competitive position |
| Growth Retainer | Custom | Ongoing marketing, design, content, and strategy |

**Additional Products (Cannabis Vertical)**

| Product | Price | Description |
|---|---|---|
| Toll Processing Connector | $750 + 2% | Connects cultivators to manufacturer partners |
| Intel Subscription | $299/mo | Recurring vendor data and market signals |
| Distress List (M&A) | $2,500 | Full scored operator list for PE firms and advisors |

> Cannabis-specific products are shown in a sub-section or expandable area — they demonstrate vertical depth without limiting Roviq's perceived scope.

### 4.5 Statement / About

**Layout**

Dark background (#1A1917). Large centered text block, max-width 800px. This is the "who we are" moment.

**Content**
- **Label:** "ABOUT ROVIQ" (uppercase, letterspaced, Roviq Red)
- **Statement:** "We're not a marketing agency. We're builders. We make the marketing, the tools, the data systems, and the design that brands actually need to grow. We happen to know cannabis better than anyone — but the skills that built 150-operator intelligence platforms and automated outreach pipelines don't stop at one industry. Based in Massachusetts. Data-obsessed. Allergic to bullshit."
- **Founder line:** "Founded by Randy Torres" + small photo or avatar (optional)

### 4.6 Data Intelligence Showcase (Vertical Spotlight)

**Purpose**

This section is unique to Roviq and differentiates from every other studio. It proves that Roviq doesn't just make things look good — it builds real data systems. Cannabis is the showcase vertical, but the section is framed as "here's what we can build for any industry."

**Layout**

Warm background. Three-column stat strip at top, then a live-looking data visualization area.

**Content**
- **Label:** "DATA INTELLIGENCE" (uppercase, Roviq Red)
- **Headline:** "We don't just design. We build intelligence systems."
- **Subhead:** "Our cannabis vertical tracks 150+ operators with live Google data, hiring signals, and distress scoring. This is what depth looks like — and we build it for every industry we touch."

**Stat Strip (3 columns)**

| Stat | Value | Label |
|---|---|---|
| Operators Tracked | 150+ | Scored and enriched weekly |
| Data Points Per Operator | 21 | Signals, reviews, hiring, licensing records |
| Market Coverage | MA Cannabis | First vertical — more coming |

**Visualization Area**
- Embedded preview of a Margin Pressure Snapshot (screenshot or live render)
- Caption: "We built this for cannabis. Imagine what we'd build for your market."
- **CTA:** "Get Your Free Snapshot" → scrolls to #newsletter or opens email compose

### 4.7 Newsletter Section

**Layout**

Dark background (#1A1917). Full-width. Clean email signup form. This is the primary lead capture mechanism for the cannabis vertical and demonstrates content marketing capability for other prospects.

**Content**
- **Label:** "FREE WEEKLY INTEL" (Roviq Red, uppercase)
- **Headline:** "The Operator's Margin Report"
- **Subhead:** "The numbers they won't tell you. Margin data, market signals, and competitive intel for MA cannabis operators. Every Tuesday."
- **Form:** Email input + "I am a..." dropdown (Dispensary/Brand Owner, Service Provider, Investor, Not in Cannabis — Just Watching) + Subscribe button
- **Social proof:** "Join 300+ MA operators" (updated dynamically from Beehiiv count)
- **Lead magnet:** "+ Get the free 2026 MA Cannabis Survival Checklist"
- **Non-cannabis hook:** Small text below form: "Not in cannabis? We still build data-driven newsletters and content systems for other industries. Let's talk."

**Integration**
- **Beehiiv API:** Publication ID pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3
- Form submits via Beehiiv API with segmentation tag from dropdown
- "Not in Cannabis" selection routes to contact form instead of Beehiiv
- 5-email automated welcome sequence triggers on subscribe

### 4.8 Testimonials & Social Proof

**Layout**

Warm background. Horizontal scrolling testimonial cards + logo strip below. If client testimonials aren't available yet, use partner mentions and data proof points instead.

**Logo Strip**
- Client logos: AC, Cannabis Healing, House of Pride
- Tool/platform logos: Python, Next.js, Beehiiv, Resend, Vercel, Figma
- Grayscale by default, color on hover
- As new clients in other industries come on, their logos add naturally

### 4.9 Contact Section

**Layout**

Simple two-column: form on left, info on right. Dark background.

**Form Fields**
- Name (required)
- Email (required)
- Company (optional)
- "What can we help with?" (dropdown: Marketing & Growth, Brand & Design, Software & Dev, Data Intelligence, Consulting & Strategy, Other)
- "What industry are you in?" (optional text field)
- Message (textarea)

**Info Panel**
- Email: randy@roviqai.xyz (or randy@spacemanwins.win until domain is set)
- Location: Massachusetts
- Response time: "Usually within 24 hours"

### 4.10 Footer

- Dark background (#1A1917), minimal
- **Left:** ROVIQ wordmark + "© 2026 Roviq AI"
- **Center:** Section links (Work, Capabilities, Data, Newsletter, Contact)
- **Right:** Twitter (@roviqai), LinkedIn, GitHub

---

## 5. Technical Specifications

### 5.1 Stack

| Layer | Technology | Notes |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSG for performance, ISR for dynamic content |
| Styling | Tailwind CSS + custom CSS variables | Brand tokens defined as CSS custom properties |
| Hosting | Vercel or Cloudflare Pages | roviqai.xyz already on Cloudflare |
| CMS (optional) | MDX or Notion API | For case study content updates |
| Newsletter | Beehiiv API | Direct API integration for signup forms |
| Email | Resend API | Contact form submissions via spacemanwins.win domain |
| Analytics | Plausible or PostHog | Privacy-focused, no cookie banners needed |
| Animations | Framer Motion | Scroll-triggered, intersection observer based |

### 5.2 Performance Targets

| Metric | Target |
|---|---|
| Lighthouse Performance | ≥95 |
| Lighthouse Accessibility | ≥95 |
| First Contentful Paint | <1.2s |
| Largest Contentful Paint | <2.5s |
| Cumulative Layout Shift | <0.05 |
| Total Bundle Size (JS) | <150KB gzipped |
| Image Format | WebP/AVIF with fallbacks |

### 5.3 SEO Requirements

- Title: "Roviq — Marketing, Design, Data & Software Studio"
- Meta description: "We build marketing, design, software, and data intelligence systems for brands that want to grow. Deep cannabis expertise. Broader than one industry."
- Open Graph image: Custom branded OG image (1200x630)
- Schema.org: LocalBusiness + ProfessionalService markup
- Sitemap: Auto-generated XML sitemap

---

## 6. Funnel & Conversion Architecture

Every section of the site maps to a step in the revenue funnel. The site is not just a portfolio — it's a conversion engine.

| Site Section | Funnel Stage | Conversion Action | Destination |
|---|---|---|---|
| Hero | Awareness | "See the Work" | Scroll to #work |
| Work Grid | Interest | Browse projects, build credibility | Click through to case study (V2) |
| Capabilities | Consideration | "Start a Sprint" / explore services | Scroll to #contact |
| Data Showcase | Proof | "Get Your Free Snapshot" / see depth | #newsletter signup or #contact |
| Newsletter | Capture (cannabis) | Email subscribe | Beehiiv API → welcome sequence |
| Contact | Conversion (all) | Submit inquiry | Resend API → Randy gets notified |

### 6.1 Post-Signup Flow (Cannabis Vertical)

1. Visitor subscribes to newsletter via site form
2. Beehiiv triggers 5-email welcome sequence with segmentation
3. Email #2 includes their free Margin Pressure Snapshot (auto-generated)
4. Email #4 introduces the 14-Day Sprint offer
5. Weekly newsletter maintains engagement and trust
6. Operator replies or books a call → Sprint or Intel Pack sale

### 6.2 General Inquiry Flow (All Industries)

1. Visitor browses Work and Capabilities sections
2. Submits contact form with industry and service interest
3. Resend delivers notification to Randy
4. Randy responds within 24 hours with a custom proposal
5. For recurring work → Growth Retainer; for one-off → Sprint

---

## 7. MVP Scope & Phasing

### 7.1 V1 (MVP) — Launch Target: 2 Weeks

- Single-page site with all sections
- Static project cards (screenshots, not dynamic)
- Newsletter signup via Beehiiv API
- Contact form via Resend
- Responsive (mobile-first)
- Deployed to Cloudflare Pages on roviqai.xyz

### 7.2 V2 — Post-Launch Enhancements

- Case study detail pages (click-through from project cards)
- Industry filter on Work grid
- Live data dashboard embed (operator count, market stats)
- Blog/insights section powered by MDX
- Animated data visualization in Data section
- Client portal / login (for Sprint deliverables)

### 7.3 V3 — Growth Features

- Self-serve Snapshot request (enter business name → auto-generate)
- Stripe integration for direct Intel Pack / Sprint purchase
- Calendly embed for discovery calls
- New vertical pages (e.g. roviqai.xyz/cannabis, roviqai.xyz/ecommerce)
- Referral program tracking
- Template marketplace (design assets, playbooks)

---

## 8. Content Requirements

All content needs to be created or gathered before build begins.

| Content Item | Status | Owner | Notes |
|---|---|---|---|
| Project screenshots (7 projects) | Needed | Randy | High-res mockups or live screenshots of client work |
| Project descriptions (7) | Needed | Randy/Claude | 2–3 sentences each with result metrics |
| Hero headline copy | Draft in PRD | Randy | May want to A/B test variations |
| Statement/About copy | Draft in PRD | Randy | Personality-driven, not corporate |
| Capability descriptions | Draft in PRD | Randy | Deliverables lists need final review |
| Newsletter copy | Exists in Beehiiv | Randy | Repurpose from existing landing page |
| Testimonial quotes | Needed | Randy | Ask AC, CH, HOP for short quotes |
| Client logos (3+) | Needed | Randy | SVG format preferred |
| OG image (1200x630) | Needed | Randy | Branded social share image |
| Favicon + touch icons | Needed | Randy | ROVIQ wordmark icon |
| Industry tags for each project | Needed | Randy | For future filtering |
