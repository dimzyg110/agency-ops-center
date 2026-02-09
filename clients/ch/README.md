# CH - Cannabis Healing

## Overview
Boston's Premier Wellness Dispensary. Closest dispensary to Logan Airport (5-min drive, 20-min walk).

**Tagline:** "Land. Walk. Relax."

**Positioning:** Transforming cannabis retail into a health-focused, modern customer experience for Boston travelers and locals alike.

**Key Stats:**
- 76% of cannabis buyers research online first
- Dispensaries with loyalty programs see 2x repeat sales
- Social cannabis content views: 1B+ monthly

---

## Brand Identity

### Core Identity
"Modern Luxury Meets Street Culture — The New Standard"

"We are the new standard where luxury, street, and self-care converge. Cannabis Healing isn't a dispensary, it's a movement built on craft, confidence, and culture. Every drop, design, and moment is engineered to elevate how people see cannabis and themselves."

### Mission
To build a wearable lifestyle brand that fuses high fashion with ritual. We curate designs, products, and experiences that feel premium, intentional, and alive—crafted to turn everyday moments into expressions of identity.

### Vision
To become East Boston's most coveted culture house, a destination for creators, travelers, and tastemakers. Through exclusive drops, celebrity collaborations, and community-driven events, Cannabis Healing will redefine what it means to live, dress, and move with elevation.

---

## Brand Architecture

### Cannabis Healing Core (70%)
Everyday brand: layout, logo usage, base palette, type, grids.

### CH Athletics (20%)
Sports/merch mode: outlined numerals, court micro-graphics, stitched labels.
- Tone: Athletic, luxurious, confident, cinematic, exclusive, real
- Use for: merch drops, local sports tie-ins, event signage

### CH Syndicate (10%)
Anime/dark-luxury mode: cinematic grain, noir lighting, poster grids.
- Tone: Moody, Refined, Cultural, Underground, Artistic, Premium
- Use for: cinematic teasers, collab posters, night-mode reels
- Requires Creative sign-off

### Guardrails
- Don't mix Athletics numerals with Syndicate title-cards
- No off-palette neons
- No effects on logos; keep Core clearspace

---

## Brand Guidelines

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Ink Black | `#0F0F10` | Primary dark |
| Gold | `#D4AF37` | Primary accent |
| Bone | `#F4F2EC` | UI/print off-white |
| Graphite | `#232427` | Text |
| Indigo Purple | `#310465` | Accent |

### Typography

**Core:**
- Primary: Avenir Next LT Pro
- Secondary: Neue Haas Grotesk Display

**Athletics:**
- Primary: Bebas Neue
- Secondary: Avenir

**Syndicate:**
- Primary: Monument Extended
- Secondary: Satoshi Variable
- Third: Brush Script

---

## Loyalty Program: Flight Club

**Platform:** Alpine IQ + Dutchie integration

### How It Works
- 1 point = $1 spent
- Points auto-sync with customer profile
- No app needed
- No tiers (yet)

### Staff Enrollment Script
"Want to join Flight Club? It's free and you earn points every time you shop."

### Key Points
- Rewards viewable in wallet and in-store
- ONE reward per transaction
- Daily deals still in Dutchie
- Loyalty bonuses (Welcome, Birthday, Event Pass) handled by Alpine automatically
- Do NOT stack deals + rewards unless manager approves

---

## Website

**Code Repo:** `/Users/randytorres/Projects/ch-web`
**Live:** https://cannabishealingllc.com
**Status:** Production

### Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18 + Vite 5 |
| Styling | Tailwind CSS 3.4 |
| Router | React Router DOM 7 |
| Icons | Lucide React |
| Analytics | Firebase Analytics, Google Analytics |
| Fonts | Neue Haas Grotesk Display Pro, Avenir LT Pro |

### Pages (10)

| Route | Description |
|-------|-------------|
| `/` | Hero video, Flight Deck, promos |
| `/shop` | Dutchie embedded menu |
| `/shop/:category` | Category filtering |
| `/airport` | Airport-specific landing (5 min from Logan) |
| `/faq` | 6 categories, 25+ Q&As |
| `/contact` | Map, messaging options |
| `/about` | Brand story, community |
| `/flight-club` | Alpine IQ loyalty signup |
| `/blog` | Blog listing with featured posts |
| `/blog/:slug` | Individual blog posts (1 published) |

### Features

- **Dutchie Integration:** Embedded POS menu, category filtering
- **Flight Club:** Alpine IQ loyalty signup iframe
- **Age Gate:** 21+ verification (session-based)
- **Airport Landing:** Speed rail, real-time hours, pickup checklist
- **Blog System:** Markdown support, SEO optimized
- **SEO:** Structured data (LocalBusiness, FAQPage, BlogListing), sitemaps, meta tags

### Integrations

| Service | Purpose |
|---------|---------|
| Firebase | Analytics |
| Google Analytics | Traffic tracking (G-LTSSR06PT8) |
| Dutchie | POS menu |
| Alpine IQ | Loyalty program |
| SendGrid | Email delivery |
| Cloudflare R2 | CDN/media |
| Virtual Budtender | Custom widget |

### Key Files

- `src/data/faq.json` - 6 categories, 25+ Q&As
- `src/data/blogs/` - Blog content (Markdown)
- `public/_redirects` - Netlify SPA routing

---

## Strategic Growth System

1. **Branding & Identity** - Health-focused design, professional presence
2. **E-Commerce & SEO** - Online orders, airport landing page, blog content
3. **Social Content Engine** - Instagram x YouTube x Twitter growth loops
4. **Loyalty & Retention** - SMS/email automation, referrals, VIP perks
5. **Delivery & Experience Events** - Airport delivery, pop-ups, collabs

---

## Original Plan Timeline

### Quick Wins (Months 1-3)
- Brand Identity + Full Website Launch
- Loyalty Beta + SEO Landing Page (Airport + Local Search)
- Social Content Engine Kickoff

### Scaling Growth (Months 3-4)
- SEO Blog Strategy + Influencer Partnerships
- Referral + Loyalty Automation
- Advanced Analytics → SEO + Campaign ROI
- Paid Ad Campaigns (Mantis, Surfside, etc)

### Future Vision (Months 5-6)
- White-Label Mobile App → Ordering + Loyalty + Push Notifications
- Delivery Partnerships → Hotels, Restaurants, Event Spaces
- Experience Events → Product Launches, Cannabis Wellness Workshops

---

## Original Pricing (Reference)

**One-Time Setup:** $5,000
- Discovery Process → Brand Identity, Goals, SEO Keywords
- Technical Setup → Domains, Hosting, Integrations
- Initial Analytics + Tracking Installation

**Monthly Tiers:**
| Tier | Price | Includes |
|------|-------|----------|
| Launch | $1,500/mo | Full Website Build, SEO Airport Landing Page, Loyalty/Deals Integration, Ongoing Maintenance |
| Launch + Growth | $3,000-$3,500/mo | + Social Content (4-6 posts/week), SEO Blogs (2/month), Loyalty SMS/Email Campaigns, Analytics |

**Content Production Add-Ons:**
| Model | Price | Includes |
|-------|-------|----------|
| Hybrid | $2,000-$2,500/mo | You film easy content, we film & edit bigger shoots |
| Full Production | $4,000-$5,000/mo | We handle all planning, filming, editing (1-2 content days/month) |

---

## Current Focus

### Airport + Uber Customer Acquisition (PRIORITY)
**Goal:** 10+ airport customers per day

**Strategy:**
- All airport + Uber focus for now
- In-store experience: Stand with flyers/promotions when customers walk in
- Flyer distribution: Brian + 2 people dedicated to this
- Scout Uber pickup/dropoff locations near airport
- Talk with businesses in the area for partnerships

### Uber Punch Card Program
- Customer gets punch card
- After 10 punches → 3 reward options (TBD)
- Incentivizes repeat visits from rideshare drivers/passengers

### Encore Casino Partnership
- **Flyer promo:** Bring in flyer → 25% off
- Target casino visitors/employees

### Flight Kits (Idea)
- Pre-packaged cannabis kits for travelers
- Needs development

### Equipment / Content Deal
**Proposal:** `proposals/equipment-content-deal.md`

Negotiating with Brian to fund ~$5K camera equipment in exchange for reduced monthly content rate ($1,500/mo vs $4-5K full production).

**Status:** Proposal drafted, ready to send.

### Ongoing
- Blog posts
- Social posting (chboston)
- [x] Alpine loyalty points setup - **DONE: Points are live**
- Cards and Eastie roll
- Social content creation
- **Update window graphics to say "Healing"**

---

## Superbowl Event Involvement (Feb 4th)

**Status:** Option C - Attendance Only

AC is hosting a Superbowl watch party with TNG. CH's involvement:
- CH team invited to attend and network
- Capture content featuring CH for their social
- Provide co-promotion assets for CH to use leading up
- No formal integration or budget required from CH

**Deliverables for CH:**
- [ ] Co-promotion social assets (leading up to event)
- [ ] Content captured at event featuring CH team
- [ ] Post-event assets for CH social

---

## Upcoming: 4-Week Campaign

When Randy is back from travel, CH will run a 4-week campaign:
- Pass out flyers
- Pop-up team in store
- Full strategy to be developed

This aligns with AC's Certified program rollout timing

## Weekly Content Goal
- 1-2 Sales Drivers → Airport convenience, deals, speed, product highlights
- 1 Fun/Brand video → Culture, humor, team personality
- 1 Engagement/Education video → Build trust + SEO

## Asset Locations
- Brand book: `./briefs/CannabisH-BrandBook.pdf`
- Loyalty guide: `./assets/CANNABIS HEALING - LOYALTY PROGRAM STAFF GUIDE.pdf`
- Strategy deck: `./briefs/Cannabis-Healing-Bostons-Premier-Wellness-Dispensary.pdf`

## Key Contacts
- Brian Jones - brian@cannabishealingllc.com
- Randy Torres - randy@roviqai.xyz

## Notes
- Plans have evolved from original - need strategy refresh
- Focus on airport convenience angle
- Fun, modern brand tone

---

## Meeting Notes

### 2026-01-20 - Strategy Meeting with Brian

**Focus Areas:**
1. **In-Store Experience** - Have a stand with all flyers/promotions ready when someone walks in
2. **Uber Punch Card** - 10 punches → 3 reward options (details TBD)
3. **Flyer Team** - Brian + 2 people dedicated to flyer distribution
4. **Uber Location Scouting** - Check out Uber pickup/dropoff spots near airport
5. **Local Business Outreach** - Talk with businesses in the area for partnerships
6. **Social Content** - Keep creating
7. **Flight Kits** - Explore pre-packaged travel kits
8. **Airport + Uber = Main Focus** - All efforts here for now
9. **Goal:** 10+ airport customers per day
10. **Encore Casino Promo** - Flyer for 25% off when brought in
11. **Window Graphics** - Update to say "Healing"
