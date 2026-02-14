# Plan 2 — Technical App Specification + VC Readiness (Partnership Proposal)

## 1. App Technical Specification (Native iOS — Swift)

### Why Native iOS (Swift) vs. Cross-Platform
- **Performance + UX:** Smooth product browsing, real-time driver tracking, and cinematic brand UX need native performance (SwiftUI + MapKit + CoreLocation).
- **Security + Compliance:** Stronger device-level security for ID storage, biometric login, and encrypted keychain handling.
- **Apple ecosystem leverage:** Apple Pay **not used** (cannabis), but native push notifications, background location, and offline caching are far more reliable.
- **Speed to premium feel:** Cross-platform apps often feel generic; Delivered’s differentiator is a premium mobile experience (no competitors have an app).

### Core Screens
- **Home:** Featured categories, “Delivered in 45–60 min” status, AC/HOP spotlight, deals, recent reorder.
- **Menu/Browse:** Filter by category, potency, price, brand, effects, THC/CBD; favorites.
- **Product Detail:** Full product info, testing data, brand story, inventory, add-to-cart.
- **Cart:** Subtotal, taxes, fees, minimum order validation, delivery window selection.
- **Checkout:** Address validation, payment (ACH/debit/cash), ID verification confirmation.
- **Order Tracking:** Driver map, ETA, status timeline, “5 min away” alert.
- **Profile:** Order history, saved payment, loyalty tier, referral code, ID status.
- **Notifications:** Deals, restocks, delivery updates, loyalty milestones.

### Ordering System
- **Real-time inventory sync** from Dutchie/POS (menu, pricing, availability).
- **Delivery window selection** (time slots with capacity).
- **Minimum order validation** (per zone/municipality).
- **Purchase limit enforcement** (daily/monthly per MA regs).

### Payment (Cannabis-Compliant)
- **ACH** (bank transfer)
- **Debit** (PIN-based solutions)
- **Cash** (standard cannabis delivery)
- **No credit cards** (federal restrictions)

### Push Notifications
- Order status updates (accepted → packed → out for delivery)
- Deals/discounts
- Restock alerts
- Loyalty milestones
- “5 min away” delivery notification

### Real-Time Tracking
- Live driver location (MapKit)
- ETA calculations + re-route alerts
- Optional driver status notes (traffic, delivery delay)

### Loyalty + Rewards
- Points system (spend-based + behaviors)
- Tier progression (Silver/Gold/Platinum)
- Referral codes (both sender + recipient rewards)

### Compliance + Safety
- Age verification flow + ID capture
- Encrypted ID storage (opt-in, for faster reorders)
- Body cam usage notice + consent language
- Purchase limits tracked and enforced

### AC / HOP Integration
- **Featured products section** (house brand spotlight)
- **Exclusive drops** (limited runs, app-first)
- **Brand storytelling** (cultivator narrative, QC/testing)

### Analytics (Built-In)
- Order patterns (by time, zone, category)
- Reorder frequency
- LTV + cohort analysis
- Drop-off points in funnel

### Offline Capability
- Cached menu + inventory snapshot
- Saved payment methods
- “Quick reorder” even during brief outages

### Backend Architecture (High-Level)
- **API Gateway**: REST/GraphQL endpoint for app
- **Services:**
  - Inventory service (Dutchie/POS sync)
  - Order service (validation, routing, tax calc)
  - Payment service (ACH/debit/cash handling)
  - Loyalty service (points + tiers)
  - Notification service (push + SMS fallback)
- **Database (conceptual schema):**
  - Users, Orders, OrderItems, InventoryItems, Drivers, DeliveryZones, LoyaltyAccounts, Referrals
- **Admin Dashboard:**
  - Order queue management
  - Delivery zone capacity
  - Push notification campaign builder
  - Driver status + routing

---

## 2. Development Timeline (8–10 Weeks to MVP)

### Weeks 1–2: Foundation
- Requirements finalization
- UX wireframes + UI design system
- API architecture + data schema planning
- Integration plan with Dutchie/POS

### Weeks 3–4: Core Build
- Home, Menu, Product Detail screens
- Cart + Checkout + payment flows
- Inventory sync integration

### Weeks 5–6: Compliance + Tracking
- ID verification flow
- Purchase limit enforcement
- Driver tracking module + ETA

### Weeks 7–8: Loyalty + Notifications
- Loyalty system
- Push notification engine
- Referral system

### Weeks 9–10: QA + App Store
- Full QA + edge cases
- Load testing (inventory spikes)
- App Store submission

#### V1 (MVP)
- Ordering + tracking + compliance
- Basic loyalty
- Standard push notifications

#### V2
- Advanced personalization
- Dynamic pricing by zone
- Deeper analytics dashboard

#### V3
- Multi-warehouse logistics
- AI-powered reorder recommendations
- Driver efficiency tools

---

## 3. Cost Analysis

### In-House Build (Randy)
- **Time cost:** 8–10 weeks of full-time development
- **Opportunity cost:** Equivalent to $80–120K build value at market rate

### Infrastructure Costs (Monthly)
- Hosting + APIs: $300–800
- Push notifications + SMS: $150–500
- Analytics + BI: $200–600
- Map/Tracking API: $100–300

### Ongoing Maintenance
- 10–15 hrs/week for updates, bug fixes, compliance changes
- Estimated $2–4K/month equivalent

### Market Comparisons
- **Agency build:** $80–150K (often generic UX)
- **Dev team hire:** $200K+/year
- **Dutchie white-label app:** generic, no differentiation

---

## 4. VC Pitch Package (What Makes Delivered Fundable)

### Key Metrics
- DAU/MAU + retention
- Reorder frequency
- LTV per customer
- Revenue per user
- CAC vs LTV ratio
- Market penetration (% of MA delivery market)

### Fundability Assets
- **Proprietary tech:** First mover app in MA delivery
- **Regulatory moat:** Social equity exclusivity locked until 2029
- **Supply chain leverage:** AC/HOP vertical integration
- **App + data moat:** behavior intelligence + retention

### Comparable Benchmarks
- Zyp Run funded at $2.6M with **no app**
- Rolling Releaf and others are web-only
- Delivery-first models often trade at 2–5x revenue in cannabis

### Series A Deck Outline
1. Problem: Web ordering friction, no mobile
2. Solution: First true cannabis delivery app
3. Market: $20.4M delivery market in MA, expanding statewide
4. Traction: growth metrics + SEO rank
5. Business Model: delivery margin + brand partnerships
6. Tech Moat: app + data + supply chain
7. Competition: all web-only
8. Financials: CAC, LTV, margin
9. Team: founders + Roviq partnership
10. Ask: growth capital + expansion

---

## 5. Data Strategy

### App Captures Data Web Doesn’t
- Geo-precise reorder behavior
- Push notification responsiveness
- App session behavior (screen-by-screen)
- In-app preferences + wishlist

### Competitive Advantage
- Personalized retention at scale
- Zone-by-zone demand forecasting
- Inventory optimization for higher margins

### VC Story
- Data-driven scaling makes Delivered more than delivery — it becomes a consumer platform.

### Compliance Considerations
- HIPAA is not required, but **privacy + cannabis compliance is critical**
- Encrypted user data, limited retention policies
- ID storage opt-in only

---

## 6. Competitive Technology Comparison

| Feature | Delivered App | Zyp Run (web) | Rolling Releaf (web) | Dutchie (generic) |
|---|---|---|---|---|
| Native iOS app | ✅ | ❌ | ❌ | ❌ |
| Real-time driver tracking | ✅ | ❌ | ❌ | ❌ |
| Push notifications | ✅ | ❌ | ❌ | ❌ |
| Loyalty tiers + referrals | ✅ | ❌ | ❌ | ❌ |
| Offline reorder | ✅ | ❌ | ❌ | ❌ |
| AC/HOP exclusive drops | ✅ | ❌ | ❌ | ❌ |
| Dynamic zone pricing (V2) | ✅ | ❌ | ❌ | ❌ |
| Advanced analytics dashboard | ✅ | ❌ | ❌ | ❌ |
| Personalized reorder prompts | ✅ | ❌ | ❌ | ❌ |

**Summary:** The Delivered app creates a durable moat by shifting the customer relationship from web/marketplace to owned mobile platform.

---

## 7. Statewide Scaling — Technical Requirements

- **Multi-zone delivery management** (separate minimums + ETAs)
- **Second warehouse integration** (inventory sync per location)
- **Driver fleet management** (route optimization, zone routing)
- **Dynamic pricing by zone** (congestion, distance, demand)
- **Coverage map** with real-time availability + service blackout windows

---

### Partnership Positioning (Reminder)
This is not a vendor build — it is a strategic equity + rev-share partnership that creates technology + data advantage for Delivered, built by Roviq.
