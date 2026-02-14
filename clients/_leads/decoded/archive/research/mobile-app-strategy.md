# Mobile App Strategy — Decoded Shop

**Prepared by:** Roviq Strategic Marketing Agency  
**Date:** February 9, 2026  
**Client:** Decoded (@decoded.shop)  
**Store:** decodedshop.myshopify.com  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Profile & Current Digital Presence](#2-business-profile--current-digital-presence)
3. [Market Opportunity & Why a Mobile App](#3-market-opportunity--why-a-mobile-app)
4. [Competitive Landscape — Brands with Successful Apps](#4-competitive-landscape--brands-with-successful-apps)
5. [Architecture Recommendation: Build vs. Buy](#5-architecture-recommendation-build-vs-buy)
6. [Shopify App Builder Comparison](#6-shopify-app-builder-comparison)
7. [Recommended Approach & Tech Stack](#7-recommended-approach--tech-stack)
8. [Core Feature Set (MVP)](#8-core-feature-set-mvp)
9. [User Journey Map](#9-user-journey-map)
10. [Shopify Integration Points](#10-shopify-integration-points)
11. [Development Timeline](#11-development-timeline)
12. [Cost Estimates](#12-cost-estimates)
13. [KPIs & Success Metrics](#13-kpis--success-metrics)
14. [Risk Assessment & Mitigation](#14-risk-assessment--mitigation)
15. [Phased Roadmap](#15-phased-roadmap)
16. [Final Recommendation](#16-final-recommendation)

---

## 1. Executive Summary

Decoded is a growing DTC streetwear / luxury fashion brand operating on Shopify with 40 products, an Instagram presence at @decoded.shop, and a premium price point ($25–$150). The brand's identity is centered on exclusivity, bold design, and curated drops — particularly the "Decoded Noir" luxury collection.

**Our recommendation:** A native mobile app built using **Vajro (Superfans)** — a Shopify app builder — is the right first step. It provides app-store presence, push notifications, and a branded shopping experience at a fraction of custom development cost. This positions Decoded to capture higher mobile conversions, build a loyal "superfan" base, and own a direct marketing channel beyond Instagram's algorithm.

**Key finding:** At Decoded's current size, a custom-built app ($80K–$200K+) is premature. A Shopify app builder at ~$150–$300/month delivers 80% of the value at <5% of the cost. Once Decoded scales past ~$1M annual revenue, a custom or enterprise-tier solution becomes worth evaluating.

---

## 2. Business Profile & Current Digital Presence

### What We Found

| Dimension | Details |
|-----------|---------|
| **Brand Name** | Decoded |
| **Store URL** | decodedshop.myshopify.com (no custom domain observed) |
| **Instagram** | @decoded.shop |
| **Platform** | Shopify (standard theme) |
| **Product Count** | 40 active SKUs, all in stock |
| **Price Range** | $25 (youth tee) — $150 (premium pieces) |
| **Average Price** | ~$75–$80 (estimated) |
| **Collections** | "Decoded Noir" (luxury line), general catalog |
| **Product Types** | Graphic tees, hoodies, sweatshirts, zip-ups, bottoms/sets |
| **Payment Methods** | Visa, Mastercard, Amex, Discover, PayPal, Apple Pay, Google Pay, Shop Pay |
| **Site Features** | Basic — HOME + CONTACT pages, email subscribe, product filtering |
| **Custom Domain** | Not observed (still on .myshopify.com subdomain) |

### Brand Positioning

Decoded positions itself in the **premium streetwear / luxury casual** space. Their copy is aspirational:

> *"This isn't just fashion. This is DECODED NOIR — a luxury brand that speaks in silence and moves in Power. Defined by precision, crafted with intention, designed for those who refuse to blend."*

This language maps to brands like:
- **Fear of God Essentials** (luxury-adjacent streetwear)
- **Represent** (UK-based premium streetwear)
- **MNML** (affordable luxury streetwear)

### Product Catalog Highlights

Notable product names that signal the brand DNA:
- 911 Turbo Shirt/Sweatshirt (car culture × fashion)
- "Ain't Ralph Tho" Tee (luxury brand counter-culture)
- "Hand of God" ($150 premium piece)
- "Noir Strata" sets (tops + bottoms, coordinated luxury)
- "DAWG" line including Youth sizing (family/community appeal)
- "Homeless Rich" Zip Up (provocative streetwear messaging)

### Digital Maturity Assessment

| Area | Score | Notes |
|------|-------|-------|
| Product catalog | ⭐⭐⭐ | 40 SKUs is solid for a growing brand |
| Brand identity | ⭐⭐⭐⭐ | Strong voice, clear positioning |
| Website sophistication | ⭐⭐ | Basic Shopify theme, no custom domain, minimal pages |
| Marketing channels | ⭐⭐ | Instagram-dependent; email subscribe present |
| Customer accounts | ⭐⭐⭐ | Login enabled via Shopify |
| SEO/Content | ⭐ | Minimal — no blog, limited meta content |

**Key insight:** Decoded has strong brand energy but an early-stage digital infrastructure. A mobile app could leapfrog several web improvements by providing a premium branded experience directly on customers' phones.

---

## 3. Market Opportunity & Why a Mobile App

### The Mobile Commerce Gap

| Metric | Statistic |
|--------|-----------|
| Mobile share of e-commerce traffic | ~73% of all Shopify visits |
| Average Shopify mobile conversion rate | 1.2% (vs. 1.9% desktop) |
| Mobile app conversion rate (industry avg) | 3–5× higher than mobile web |
| Push notification conversion vs. email | 10–15× higher |
| Push notification conversion vs. SMS | 9× higher |
| Push notification cost | Free (unlimited) vs. $0.01+/SMS |
| App user repurchase rate | 2–3× higher than web-only |

### Why It Matters for Decoded Specifically

1. **Drop Culture = Push Notifications.** Decoded's product strategy (limited runs, Noir collection, new drops) is perfectly suited to push notifications. When you drop a new "Hand of God" tee, a push notification puts it in front of your core fans instantly — for free.

2. **Brand Real Estate.** Having your icon on a customer's home screen is the ultimate brand presence. For a brand selling $100+ hoodies, this perceived premium positioning matters.

3. **Instagram Algorithm Independence.** Decoded currently relies heavily on Instagram. An app creates a direct channel to customers that no algorithm controls.

4. **Higher Conversion.** Mobile apps convert 3–5× better than mobile websites. Even a small improvement on a $75 AOV adds up fast.

5. **Customer Lifetime Value.** App users are the most engaged customers. They buy more often, spend more per order, and have higher retention.

### When NOT to Build an App

Industry consensus suggests brands should reach **$500K–$1M+ in annual revenue** before investing in a mobile app (some experts say $10M, but that applies more to custom builds). For Decoded:

- If current revenue is **under $250K/year**: Focus on website improvements, custom domain, and growing the customer base first. A PWA (see Section 5) would be the interim step.
- If current revenue is **$250K–$1M/year**: A Shopify app builder (Vajro/Tapcart) is the sweet spot — low risk, meaningful upside.
- If current revenue is **$1M+/year**: App builder immediately, with a path to custom build as scale warrants.

---

## 4. Competitive Landscape — Brands with Successful Apps

### Streetwear / Premium Fashion Brands with Apps

| Brand | App Platform | Key Features | What Works |
|-------|-------------|--------------|------------|
| **Fashion Nova** | Tapcart (native) | Push notifications, exclusive drops, live events | Push-driven flash sales; app-exclusive pricing |
| **Gymshark** | Custom native | Training content + shopping, community, events | Content beyond commerce; "drop" model for urgency |
| **SHEIN** | Custom native | Gamification, daily check-ins, social sharing | Points system, style community, addictive UX |
| **Princess Polly** | Tapcart | Clean UI, push for new arrivals, wishlist | Simple and brand-consistent; strong conversion |
| **Chubbies** | Tapcart | Fun branded experience, push for drops | Personality-driven; exclusive app offers |
| **Represent** | Shopify app builder | Premium aesthetic, drop notifications | Luxury-feel within app builder constraints |

### Lessons for Decoded

**What works for brands at this scale:**
- ✅ Push notifications for new drops and restocks
- ✅ Exclusive app-only products or early access
- ✅ Clean, brand-consistent visual design
- ✅ Simple checkout (Apple Pay / Shop Pay)
- ✅ Wishlist / save for later

**What doesn't work (avoid):**
- ❌ Over-engineered features (AR try-on, AI styling) — too expensive, too early
- ❌ Social features / community forums — hard to maintain with small team
- ❌ Gamification / loyalty points — adds complexity; better via Shopify app like Smile.io
- ❌ Custom-built app — cost doesn't justify at this stage

---

## 5. Architecture Recommendation: Build vs. Buy

### Option Comparison

| Approach | Upfront Cost | Monthly Cost | Time to Launch | Best For |
|----------|-------------|--------------|----------------|----------|
| **PWA (Progressive Web App)** | $2K–$10K | $0–$50/mo | 1–3 weeks | Brands under $250K rev; testing the concept |
| **Shopify App Builder** (Vajro, Tapcart) | $0 | $150–$500/mo | 1–2 weeks | Brands $250K–$10M; best ROI path |
| **Hybrid Custom** (React Native / Flutter) | $50K–$120K | $2K–$5K/mo maint. | 3–6 months | Brands $5M+; need unique features |
| **Native Custom** (Swift + Kotlin) | $100K–$250K | $5K–$10K/mo maint. | 6–12 months | Brands $10M+; enterprise requirements |

### Our Recommendation: Shopify App Builder (Vajro)

**Why not custom?**
- Decoded has 40 SKUs and an early-stage web presence
- Custom app development costs $80K–$200K+ and takes 4–8 months
- Ongoing maintenance costs $3K–$8K/month (updates, bug fixes, OS compatibility)
- At Decoded's apparent revenue stage, ROI would take 2–4 years

**Why not PWA?**
- PWAs lack push notifications on iOS (Apple restrictions)
- No app store presence (discoverability and credibility)
- Limited offline capabilities
- Doesn't deliver the "premium" signal Decoded's brand needs

**Why Vajro (Shopify app builder)?**
- Ships in 1–2 weeks
- $150/month starting price
- Full Shopify sync (products, orders, inventory)
- Unlimited push notifications
- Native iOS + Android apps in the App Store / Play Store
- 4.9★ rating with 887 reviews
- 24/7 support on all plans
- No revenue share on lower tiers
- Integrates with Klaviyo, Recharge, Judge.me, and more

---

## 6. Shopify App Builder Comparison

### Head-to-Head: Vajro vs. Tapcart vs. Plobal vs. MobiLoud

| Feature | Vajro (Superfans) | Tapcart | Plobal Apps | MobiLoud |
|---------|-------------------|---------|-------------|----------|
| **Starting Price** | $150/mo | $250/mo | $199/mo | $399/mo + $850 setup |
| **Free Trial** | 30 days | No | 30 days | Free preview |
| **Revenue Share** | No (until $100K/mo on Plus) | 2.5% success fee | Varies | None |
| **Setup Fee** | None | None | None | $850–$1,500 |
| **Shopify Rating** | 4.9★ (887 reviews) | 4.8★ (480+ reviews) | 4.6★ | N/A (not in app store) |
| **Launch Time** | <1 week | 1–2 weeks | 1–2 weeks | 2–3 weeks |
| **Builder Type** | Drag-and-drop + templates | Drag-and-drop | Template-based | Website wrapper |
| **Push Notifications** | Unlimited, segmented | Unlimited, advanced | Unlimited | Via OneSignal/Klaviyo |
| **Live Selling** | ✅ Built-in | ❌ | ✅ | ❌ |
| **24/7 Support** | ✅ All plans | ❌ (email on lower tiers) | ✅ | Email + calls |
| **Integrations** | 70+ native (Klaviyo, Recharge, Yotpo, etc.) | 50+ native | 40+ | All (website-based) |
| **A/B Testing** | ❌ | ❌ | ❌ | ❌ |
| **Deep Linking** | Basic | Rolling out | Basic | ✅ Full |
| **Design Control** | Moderate (template-driven) | High (drag-and-drop) | Moderate | Full (mirrors website) |
| **Best For** | Small–mid brands wanting speed + value | Growing DTC with design teams | Mid-market | Brands wanting exact site parity |

### Our Ranking for Decoded

1. **🥇 Vajro (Superfans)** — Best value, fastest launch, strong support, lowest barrier. The 30-day free trial is ideal for testing. Live selling feature could be powerful for limited drops.

2. **🥈 Tapcart** — More design control, stronger push notification platform, but 67% more expensive at the starter level with a revenue share fee. Better fit once Decoded is doing $500K+.

3. **🥉 MobiLoud** — Best for mature brands wanting exact website parity. Overkill for Decoded's current site (which itself needs work).

4. **Plobal** — Functional but less differentiated. Mixed reviews on customization reliability.

---

## 7. Recommended Approach & Tech Stack

### Recommended Stack

| Component | Tool | Why |
|-----------|------|-----|
| **App Builder** | Vajro (Superfans) | Best price/value; fastest to launch; 30-day free trial |
| **Push Notifications** | Vajro built-in | Unlimited, segmented, scheduled |
| **Email Marketing** | Klaviyo (if not already) | Integrates with Vajro; industry standard for Shopify |
| **Reviews** | Judge.me or Yotpo | Social proof in-app; Vajro integrations |
| **Analytics** | Shopify Analytics + GA4 | Baseline tracking; app attribution |
| **Payments** | Apple Pay, Google Pay, Shop Pay | Already enabled; critical for app conversion |
| **Customer Support** | Gorgias or Tidio | In-app chat support (Vajro integration) |

### Pre-Launch Requirements

Before launching the app, Decoded should:

1. **Get a custom domain** — "decodedshop.myshopify.com" looks unprofessional for a brand claiming luxury positioning. Something like `decoded.shop` or `decodednoir.com` would be ideal.

2. **Improve product photography** — App real estate is precious. High-quality lifestyle photos convert dramatically better.

3. **Set up email marketing** — The app will drive email collection + push opt-ins. Need both channels working.

4. **Create Apple Developer + Google Play accounts** — Apple Developer: $99/year, Google Play: $25 one-time.

5. **Prepare launch content** — 3–5 push notifications planned for the first 2 weeks. Welcome sequence, first drop announcement, exclusive offer.

---

## 8. Core Feature Set (MVP)

### Must-Have (Phase 1 — Launch)

| Feature | Revenue Impact | Difficulty |
|---------|---------------|------------|
| **Product browsing & search** | High — core shopping experience | Built-in |
| **Push notifications** | High — free marketing channel, drop alerts | Built-in |
| **Seamless checkout** (Apple Pay, Shop Pay) | High — reduces cart abandonment | Built-in |
| **Wishlist / Save for later** | Medium — increases return visits | Built-in |
| **Collection browsing** (Decoded Noir, etc.) | Medium — guides discovery | Built-in |
| **Account / Order tracking** | Medium — reduces support tickets | Built-in |
| **Email + SMS capture** | Medium — list building | Configuration |
| **Size guide** | Medium — reduces returns | Custom block |

### Nice-to-Have (Phase 2 — Month 2–3)

| Feature | Revenue Impact | Difficulty |
|---------|---------------|------------|
| **Early access / app-exclusive drops** | High — drives downloads and retention | Push + timing |
| **Loyalty program** (via Smile.io integration) | Medium — increases LTV | Integration |
| **Product reviews** (Judge.me) | Medium — social proof | Integration |
| **Abandoned cart push notifications** | High — recovers lost sales | Configuration |
| **Back-in-stock alerts** | Medium — captures demand | Integration |

### Future (Phase 3 — Month 4+)

| Feature | Revenue Impact | Difficulty |
|---------|---------------|------------|
| **Live selling events** (Vajro built-in) | High — hype events for drops | Planning + execution |
| **Referral program** | Medium — organic growth | Integration |
| **Style lookbooks / editorial content** | Low–Medium — brand building | Content creation |
| **In-app chat support** | Low — reduces friction | Integration |

---

## 9. User Journey Map

### Journey 1: New Customer (Discovery → First Purchase)

```
Instagram Post/Story → Link in Bio → App Download CTA
          ↓
    App Store Page (branded screenshots, reviews)
          ↓
    Download + Open App
          ↓
    Welcome Push: "Welcome to Decoded. Here's 10% off your first order."
          ↓
    Browse Decoded Noir Collection
          ↓
    View Product → Size Guide → Add to Cart
          ↓
    Checkout (Apple Pay / Shop Pay — 2 taps)
          ↓
    Order Confirmation Push + Email
          ↓
    Shipping Update Push Notification
          ↓
    Delivered → Review Request Push (7 days later)
```

### Journey 2: Returning Customer (Drop Notification → Purchase)

```
Push Notification: "🔥 NEW DROP: Kingdom Has Fallen — Available Now"
          ↓
    Tap → Opens directly to product page (deep link)
          ↓
    View Product → Already has payment info saved
          ↓
    One-Tap Purchase (Shop Pay / Apple Pay)
          ↓
    Order Confirmation
          ↓
    Share on Instagram Stories → Social proof
```

### Journey 3: Lapsed Customer (Re-engagement)

```
Day 14 No Activity → Push: "New in the Noir collection. Made for you."
          ↓
Day 30 No Activity → Push: "We saved something for you. 15% off, 24 hours."
          ↓
Day 60 No Activity → Push: "Miss us? Exclusive restock alert."
          ↓
    Re-open app → Browse → Purchase
```

---

## 10. Shopify Integration Points

### Automatic Syncs (via Vajro/Tapcart)

| Data | Sync Direction | Frequency |
|------|---------------|-----------|
| Product catalog (name, price, images, variants) | Shopify → App | Real-time |
| Inventory / stock levels | Shopify → App | Real-time |
| Collections | Shopify → App | Real-time |
| Orders | App → Shopify | Real-time |
| Customer accounts | Bidirectional | Real-time |
| Discount codes | Shopify → App | Real-time |
| Shipping rates | Shopify → App | Real-time |
| Payment processing | Via Shopify Checkout | Real-time |

### Additional Integration Opportunities

| Integration | Purpose | Priority |
|-------------|---------|----------|
| **Klaviyo** | Email + SMS marketing synced with app events | High |
| **Judge.me** | Product reviews displayed in-app | Medium |
| **Smile.io** | Loyalty points program | Medium |
| **Gorgias** | Customer support chat in-app | Low |
| **Google Analytics 4** | App analytics + attribution | High |
| **Facebook/Meta Pixel** | Retargeting app users | High |
| **Recharge** | Subscription products (future) | Low |
| **AfterShip** | Order tracking in-app | Medium |

### Technical Considerations

- **Shopify Checkout:** Vajro/Tapcart use Shopify's native checkout. This means no additional 30% Apple/Google in-app purchase fees. All Shopify payment methods work.
- **Discount codes:** Any discount created in Shopify works in the app automatically.
- **Shopify Scripts:** Custom pricing logic via Shopify Scripts is supported.
- **Multi-currency:** If Decoded enables Shopify Markets, currency conversion works in-app.

---

## 11. Development Timeline

### Using Vajro (Recommended Path)

| Week | Milestone | Details |
|------|-----------|---------|
| **Week 0** | Pre-work | Set up Apple Developer ($99/yr) + Google Play ($25) accounts; prepare brand assets (logo, colors, app icon, screenshots) |
| **Week 1** | App setup + design | Install Vajro; configure theme to match Decoded brand; set up collections, navigation, home screen layout |
| **Week 1** | Content + configuration | Upload app icon, splash screen; configure push notification welcome sequence; set up analytics |
| **Week 2** | Testing + submission | Internal testing on iOS + Android; submit to App Store + Play Store for review |
| **Week 2–3** | App store review | Apple review: 1–3 days; Google review: 1–7 days |
| **Week 3** | 🚀 Launch | App live; announce on Instagram + email; begin push notification strategy |
| **Week 4–6** | Optimize | Analyze first 30 days; adjust home screen, push cadence, featured products |
| **Week 6–8** | Phase 2 features | Add loyalty integration, reviews, abandoned cart push |

**Total time to live app: 2–3 weeks**

### If Custom Build Were Chosen (for reference)

| Phase | Duration | Details |
|-------|----------|---------|
| Discovery + Design | 4–6 weeks | Wireframes, UI/UX, brand integration |
| Development (MVP) | 8–12 weeks | iOS + Android + backend |
| Testing + QA | 2–4 weeks | Device testing, bug fixes |
| App Store Submission | 1–2 weeks | Review + potential rejections |
| **Total** | **16–24 weeks** | 4–6 months |

---

## 12. Cost Estimates

### Option A: Vajro (Recommended) — Year 1 Costs

| Line Item | Cost | Frequency |
|-----------|------|-----------|
| Vajro Starter Plan | $150/mo ($1,800/yr) | Monthly |
| Apple Developer Account | $99 | Annual |
| Google Play Account | $25 | One-time |
| Brand asset preparation (if needed) | $0–$500 | One-time |
| **Year 1 Total** | **$1,924–$2,424** | |
| **Monthly Run Rate** | **~$160/mo** | |

### Option B: Tapcart — Year 1 Costs

| Line Item | Cost | Frequency |
|-----------|------|-----------|
| Tapcart Core Plan | $250/mo ($3,000/yr) | Monthly |
| Revenue share (2.5% on app sales) | Variable | Monthly |
| Apple Developer + Google Play | $124 | Annual / one-time |
| **Year 1 Total** | **$3,124 + 2.5% of app revenue** | |
| **Monthly Run Rate** | **~$260+/mo** | |

### Option C: Custom Build — Year 1 Costs

| Line Item | Cost | Frequency |
|-----------|------|-----------|
| Design + Development (React Native) | $80,000–$150,000 | One-time |
| App Store accounts | $124 | Annual |
| Hosting + infrastructure | $200–$500/mo | Monthly |
| Maintenance + updates | $2,000–$5,000/mo | Monthly |
| **Year 1 Total** | **$106,524–$216,124** | |
| **Monthly Run Rate (post-build)** | **$2,200–$5,500/mo** | |

### ROI Calculation (Vajro)

**Assumptions (conservative):**
- Current monthly revenue: $15,000 (hypothetical)
- App drives 8% of sales (industry low-end for new app)
- App conversion rate is 2× mobile web
- Push notifications replace some paid ad spend

| Metric | Value |
|--------|-------|
| Monthly app revenue (8% of $15K) | $1,200 |
| Incremental revenue (20–30% truly new) | $240–$360/mo |
| Push notification savings vs. SMS (500 sends/mo × $0.015) | $7.50/mo |
| Vajro cost | -$150/mo |
| **Net monthly impact** | **+$97–$217/mo** |
| **Breakeven** | **Month 1–2** |

Even under conservative assumptions, the app pays for itself almost immediately. The real value compounds as the app audience grows.

---

## 13. KPIs & Success Metrics

### Primary KPIs (Revenue-Driving)

| KPI | Target (Month 1) | Target (Month 6) | Target (Month 12) |
|-----|------------------|------------------|-------------------|
| App installs | 100–200 | 500–1,000 | 1,500–3,000 |
| App conversion rate | 2.5% | 3.5% | 4.0%+ |
| App revenue as % of total | 3–5% | 8–12% | 15–20% |
| Push notification opt-in rate | 60% | 65% | 70% |
| Push notification click-through rate | 5–8% | 6–10% | 8–12% |
| App AOV vs. mobile web AOV | Parity | +5% | +10% |

### Secondary KPIs (Engagement & Health)

| KPI | Target | Notes |
|-----|--------|-------|
| Monthly active users (MAU) | 30% of installs | Industry benchmark |
| Session duration | 3+ minutes | Indicates browsing, not just checking |
| Sessions per user/month | 4+ | Healthy repeat engagement |
| Cart abandonment rate (app) | <60% | vs. ~75% on mobile web |
| App store rating | 4.5+ stars | Social proof for new installs |
| Uninstall rate (30-day) | <25% | Industry average is ~28% |
| Customer retention rate (app users) | 40%+ at 90 days | vs. ~20% for non-app customers |

### Tracking Setup

- **Shopify Analytics:** Revenue attribution, order source tracking
- **Google Analytics 4:** App + web unified tracking (requires GA4 configuration)
- **Vajro Dashboard:** Push notification performance, in-app engagement
- **UTM Parameters:** Tag all push notification links for Shopify attribution

---

## 14. Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Low download numbers | Medium | High | Promote aggressively on Instagram, offer app-exclusive incentive (10% off first in-app order), add download CTA to order confirmation emails |
| Push notification fatigue | Medium | Medium | Cap at 3–4 pushes per week; segment by behavior; personalize content |
| App store rejection | Low | Medium | Follow Apple/Google guidelines; Vajro handles submission and compliance |
| Brand inconsistency (app vs. web) | Medium | Low | Use Decoded brand colors, fonts, imagery consistently; Vajro templates are customizable |
| Low ROI at current scale | Medium | Medium | Start with free trial (30 days); kill or pause if metrics don't justify $150/mo |
| Platform dependency (Vajro) | Low | Medium | All data lives in Shopify; switching app builders takes 1–2 weeks; no lock-in |
| Technical issues | Low | Low | Vajro offers 24/7 support; Shopify sync is mature and reliable |

---

## 15. Phased Roadmap

### Phase 1: Foundation (Weeks 1–3) — "Get Live"

**Goal:** Launch a clean, branded app on iOS and Android

- [ ] Set up Apple Developer + Google Play accounts
- [ ] Install Vajro; begin 30-day free trial
- [ ] Configure app branding (colors, fonts, logo, icon, splash screen)
- [ ] Set up home screen: hero banner (Decoded Noir), featured collections, new arrivals
- [ ] Configure product detail pages with size guide
- [ ] Set up welcome push notification sequence
- [ ] Internal testing (3–5 devices)
- [ ] Submit to app stores
- [ ] Launch announcement: Instagram post + stories + email blast
- [ ] **Cost: $0 (free trial) + $124 (store accounts)**

### Phase 2: Growth (Weeks 4–8) — "Drive Downloads"

**Goal:** Build the app user base to 200+

- [ ] Begin Vajro paid plan ($150/mo)
- [ ] Run "App Exclusive" campaign: early access to next drop for app users only
- [ ] Set up abandoned cart push notifications
- [ ] Add product reviews integration (Judge.me)
- [ ] Optimize push notification strategy based on Week 1–3 data
- [ ] Add app download CTA to:
  - Instagram bio link
  - Order confirmation emails
  - Website banner
  - Package inserts (QR code)
- [ ] **Monthly Cost: $150**

### Phase 3: Optimize (Months 3–6) — "Increase LTV"

**Goal:** Make the app a revenue engine, not just a channel

- [ ] Implement loyalty program (Smile.io integration)
- [ ] Set up back-in-stock push alerts
- [ ] Create app-exclusive "Decoded Members" pricing or drops
- [ ] Test live selling feature for major drops (Vajro built-in)
- [ ] Analyze and optimize: push frequency, home screen layout, featured products
- [ ] Consider Vajro plan upgrade if volume warrants it
- [ ] **Monthly Cost: $150–$300**

### Phase 4: Scale (Months 6–12) — "Level Up"

**Goal:** App generates 15–20% of total revenue

- [ ] Evaluate upgrade to Tapcart (if more design control needed)
- [ ] Implement referral program (app users invite friends)
- [ ] Add editorial content / lookbooks
- [ ] Explore in-app chat support
- [ ] Begin planning for custom app if revenue exceeds $1M/year
- [ ] **Monthly Cost: $150–$500**

---

## 16. Final Recommendation

### For Decoded, Right Now:

| Decision | Recommendation |
|----------|---------------|
| **Should Decoded build a mobile app?** | ✅ Yes — IF current revenue supports $150/mo and there's bandwidth to promote it |
| **Which platform?** | **Vajro (Superfans)** — best value, fastest launch, free trial to validate |
| **Native, Hybrid, or PWA?** | **Native via app builder** — gets app store presence + push notifications at low cost |
| **Custom build?** | ❌ Not yet — revisit when revenue exceeds $1M/year |
| **When to launch?** | Within 30 days of starting; target a product drop to coincide with launch |
| **Biggest ROI feature?** | Push notifications for drops and abandoned cart recovery |
| **Biggest risk?** | Low downloads due to small audience — mitigate with aggressive cross-channel promotion |

### If Budget Is Extremely Tight (Under $150/mo):

Start with a **PWA (Progressive Web App)** instead. Shopify has PWA-capable themes and apps (e.g., Ampify, PushOwl for web push). This costs $0–$50/month and provides some app-like benefits (add to home screen, faster loading) without app store presence. Graduate to Vajro once revenue justifies it.

### What Roviq Can Deliver:

As their strategic marketing agency, Roviq can support Decoded through:

1. **App setup and configuration** (using Vajro — no code required)
2. **Brand asset preparation** (app icon, screenshots, store listing copy)
3. **Push notification strategy** (content calendar, segmentation, automation)
4. **Launch campaign** (Instagram, email, cross-channel promotion plan)
5. **Ongoing optimization** (monthly performance review, A/B testing push content)
6. **Growth roadmap** (when to upgrade, when to go custom)

This is a **low-risk, high-upside project** that can be delivered fast and demonstrate clear value to the client. It also creates an ongoing retainer opportunity for Roviq.

---

*Report prepared by Roviq AI Research Team. For questions or to initiate the project, contact Randy at roviqai.xyz.*
