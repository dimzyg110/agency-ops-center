# HOP - House of Pride / Pride Packz

## Overview

Luxury cannabis house founded by a master grower with 20+ years of experience and his son (Kam), united by a mission to create a place of belonging. LGBTQ+ community focused.

**Current Assets:**

- 24 dispensary locations (distribution gold)
- Authentic founder story (Kam + Dad)
- Proven event success (launch sold out, profitable)
- Master grower (20+ years experience)
- Community loyalty & word-of-mouth
- Pre-rolls already selling

**Gaps to Close:**

- No website or online presence
- Inconsistent brand identity
- Limited merch strategy
- No partnership/collab framework
- Untapped revenue streams

---

## Brand Identity

### About

House of Pride is a luxury cannabis house that blends elite cultivation with high-end design to offer products that make our community feel rare, seen, and unapologetically themselves. Rooted in craft, courage, and community, our vision extends beyond cannabis into a global lifestyle brand.

### Mission

To set the standard where excellence and identity are inseparable.

"We cultivate with the patience of a legacy estate. We design with the precision of a fashion house. Every product, every experience, every detail exists to make our community feel rare, seen, and unapologetically themselves."

### Vision

To build a global luxury house rooted in cannabis, fashion, and pride, inspiring families, supporting the LGBTQ+ community, and proving that authenticity is a winning brand.

### Slogan

"Pride is for everyone"

### Values

- **Craft** - Excellence in everything
- **Courage** - Bold authenticity
- **Community** - Building belonging

### Tone

Authentic, Inclusive, Empowering

---

## Brand Guidelines

### Colors

| Name               | Hex       | Usage               |
| ------------------ | --------- | ------------------- |
| New Orleans (Gold) | `#e7cc95` | Primary brand color |
| White              | `#fcfcfc` | Background          |
| Black              | `#000000` | Text, contrast      |
| Tan                | `#dfd5c5` | Secondary           |

### Typography

- **Open Sans** - Primary
- **Poppins** - Secondary

### Logo Versions

- Full logo (gold on white)
- Full logo (white on black)
- Full logo (black on white)

---

## Strategic Vision

### The Billion-Dollar Play

"You're not scaling cannabis volume. You're building a brand around authenticity, exclusivity, and community. Like Supreme. Like Stüssy. Like Goop. Cannabis is your anchor. Merch is your business."

### Revenue Targets

| Phase    | Timeline               | Target                |
| -------- | ---------------------- | --------------------- |
| Year 1   | Foundation             | $100-150k revenue     |
| Year 2-3 | Regional dominance     | $500k-$1M revenue     |
| Year 5+  | Global lifestyle brand | $10M+ revenue pathway |

---

## Original Plan (90 Days + Beyond)

### Phase 1: Launch (Months 1-3)

- Website launch (Shopify + POD integration)
- Brand refresh (visual identity, messaging)
- 5-7 core merch designs
- Social content strategy
- In-store merch displays (24 locations)
- First pop-up event planning
- **Goal:** Website live, merch selling, $1-3k/month revenue

### Phase 2: Scale (Months 4-12)

- 2-3 Kam pop-up events (sponsor partnerships)
- Limited edition merch drops (event-tied)
- Community partnerships (Cape Cod expansion)
- Brand collab framework (Bobby Bags, luxury brands)
- Weekly content + social management
- Event sponsorship revenue
- **Goal:** $20-50k/month revenue, sustainable growth engine

### Phase 3: Expand (Year 2+)

- Multiple events across regions
- Premium merch line (designed collabs)
- International pilot market
- Lifestyle category expansion
- Strategic investment/partnership conversations
- **Goal:** Multi-million dollar brand trajectory

---

## Original Pricing (Reference)

### Tier 1: Lean Launch (90-Day Test)

- $3,000 one-time fee + $1,500/month + 5% of merch & event revenue
- Website + POD setup
- 5-7 core merch designs
- Monthly content strategy
- 1 event consultation per quarter
- Bi-weekly check-ins

### Tier 2: Growth Mode (6+ Months)

- $3,500/month + 10% of merch & event revenue
- Everything from Tier 1, plus:
- Weekly strategy sessions
- Full event planning & execution (2-3/quarter)
- Sponsor outreach & partnership deals
- Weekly content calendar + social management

---

## Website

**Code Repo:** `/Users/randytorres/Projects/House-Pride`
**Deployment:** Netlify + Replit
**Status:** Frontend complete, backend skeleton

### Tech Stack

| Layer     | Technology                                           |
| --------- | ---------------------------------------------------- |
| Frontend  | React 19 + Vite 7 + TypeScript                       |
| Styling   | Tailwind CSS 4                                       |
| Routing   | Wouter (lightweight SPA)                             |
| Animation | Framer Motion 12                                     |
| Data      | TanStack React Query 5                               |
| Forms     | React Hook Form + Zod                                |
| UI        | Radix UI components                                  |
| Backend   | Express 4 (skeleton)                                 |
| Database  | PostgreSQL 16 + Drizzle ORM (defined, not connected) |
| CDN       | Cloudflare R2                                        |

### Pages (4)

| Route       | Description                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------------- |
| `/`         | Hero, Triptych (Craft/Courage/Community), TheHouse parallax, Drop001, Manifesto, RequestAccess |
| `/products` | Prerolls & 1/8ths showcase with motion animations                                              |
| `/about`    | Brand narrative (Identity, Mission, Vision)                                                    |
| `/account`  | Placeholder (auth not implemented)                                                             |

### Working Features ✅

**Frontend**

- Luxury design with iridescent text effects
- Complex Framer Motion animations (parallax, scroll-triggered, mouse-tracking)
- Responsive mobile-first design
- RequestAccess email form with validation
- Toast notifications (Sonner)
- Product showcase with R2-hosted images

**Build/Dev**

- Vite builds successfully
- Hot module replacement
- TypeScript compilation

### Not Implemented ❌

**Backend**

- API routes empty (template only)
- No endpoints for products/email/auth
- Passport configured but not wired
- Express server minimal

**Database**

- Schema defined (users table) but not migrated
- Using in-memory storage (not PostgreSQL)
- No data persistence

**Missing Features**

- [ ] Real email capture (form doesn't save)
- [ ] Merch/e-commerce integration
- [ ] 21+ age verification
- [ ] User authentication
- [ ] Analytics

### Architecture

```
/client    - React frontend (Vite)
/server    - Express backend (skeleton)
/shared    - Database schema, types
/attached_assets - AI-generated images
```

**Summary:** Marketing/showcase site ready to launch. Backend ready for features to be added.

---

## Current Focus

- **Priority:** Fix email capture (backend not connected - form doesn't save)
- Launch video production (add cannabis content)
- Backend implementation (auth, database connection)
- Merch integration planning

## Content Available

- TikTok videos (None need to make)
- IG posts (None need to make)

## Blockers

- [ ] Missing label designs - blocking asset creation
- [ ] Email capture not working - backend skeleton only, no data persistence
- [ ] 21+ age verification not implemented

## Asset Locations

- Briefs: `./briefs/`

## Key Contacts

- Kam (Founder/Son)
- Dad (Master Grower)

## Notes

- Launch video needs cannabis content added
- Plans have evolved - need strategy refresh
