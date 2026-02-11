# GLASS Product Plan — Massachusetts Cannabis Operator OS

## 1. Executive Summary

GLASS is the operating system for Massachusetts cannabis operators. It is a hub with paid spokes. The core platform is free and delivers immediate, daily value. It includes Price Wire for competitor pricing, Threat Radar for CCC intelligence, and Margin Engine for AI pricing recommendations. Paid spokes plug into the core: Cue for budtender incentives, Delivered for delivery as a service, AC Toll Processing for prerolls, and Roviq Agency for marketing upsell.

All three plans agree on the core architecture and the hub plus spokes model. That is decided. Two of three plans emphasize a single daily command screen as the main interface and a newsletter as the primary funnel. We will use both. Where the plans diverge on the core pricing model, the best choice is to keep core free and charge for premium analytics plus spokes. This maximizes adoption and data density, which is the main moat. The hub is the funnel, not the profit center.

GLASS wins because it fixes the daily pain of operators in a collapsing market. It is fast to value and built around actions that change pricing and merchandising today. The flywheel is simple: more operators create better pricing and regulatory data, better recommendations drive more adoption, and spokes monetize that traffic without adding friction.

Success looks like this within 12 months:
1. Fifty operators active, with 20 in the seed cohort.
2. Price Wire data updated at least every 6 hours for full MA coverage.
3. Threat Radar alerts within 24 hours of CCC publication.
4. Margin Engine recommendations adopted by at least 30 percent of active operators.
5. Cue signed by at least 10 brands, Delivered live in 10 stores, AC Toll processing active in 5 stores.

GLASS is not another menu platform. It is the intelligence layer that makes every operator more profitable, and it is the operating system that connects operators to the services that support them.

---

## 2. Product Architecture

### 2.1 Core Screens and Navigation

**Top bar**
- Store selector with multi location support
- Data freshness timestamp
- Alerts bell
- Quick actions: Create Price Move, Launch Cue Campaign, Enable Delivered

**Left navigation**
- Home
- Price Wire
- Threat Radar
- Margin Engine
- Spokes
  - Cue
  - Delivered
  - AC Toll Processing
  - Roviq Agency
- Settings

### 2.2 Home Screen, Morning Brief

The home screen is a daily checklist. All three plans agree that operators want a single view that tells them what to do now. This is the Morning Brief and it is the product’s main habit loop.

**Core widgets**
1. Price Wire Today
   - Top 10 price movers in a 5 mile radius
   - Your price position by category percentile
   - Three competitor price drops with direct links to detail
2. Threat Radar
   - New CCC applications within radius
   - Enforcement actions or recalls that affect brands you carry
3. Margin Engine Recommendations
   - Five highest impact price moves with expected unit and margin delta
   - One click approval or edit
4. Action Center
   - Launch Cue incentive
   - Enable Delivered for eligible towns
   - Request AC Toll Processing quote
   - Roviq Agency growth gaps banner

**Opinionated choice where plans differ**
Two plans favor a strict morning brief layout, one favors a multi column dashboard. We adopt a morning brief layout on mobile and a three column dashboard on desktop. This keeps the ritual while enabling deep analysis on desktop.

### 2.3 Key Screens

**Price Wire**
- Map of competitors with price index heat map
- Table of SKU, brand, size, competitor price range, your price, delta, last update
- Price watch list with alert triggers
- 90 day price history chart per SKU
- CSV export and shareable report

**Threat Radar**
- Map view with pins for new applications, violations, renewals
- Timeline feed for CCC items
- Watchlist for specific competitors or brands
- Impact score that ranks relevance by proximity, category, and market share

**Margin Engine**
- Inputs: your cost, inventory on hand, velocity, target margin
- Outputs: recommended price, confidence score, expected unit and margin impact
- What if slider for price and volume changes
- Apply creates a task, not an auto change, unless explicitly opted in

**Spokes Hub**
- Cards for Cue, Delivered, AC Toll, Roviq with status and ROI snapshots
- Each card has a primary action button

### 2.4 Data Flows

1. Menu scrape to SKU normalization to price index
2. CCC and municipal data ingest to geo matching to alert engine
3. Operator sales and inventory data to Margin Engine model
4. Margin Engine recommendations to operator action logging
5. Spoke data and outcomes back into model features and dashboards

### 2.5 User Journey

**Onboarding**
1. Signup with store name, license number, city
2. Auto detect menu source by URL
3. Show Price Wire Today immediately from cached data
4. Ask for cost and sales data later, do not block
5. First email report within 24 hours

**Daily Operator Flow**
1. Open GLASS, Morning Brief loads
2. Scan alerts and top price moves, 30 to 60 seconds
3. Approve or edit top pricing recommendations
4. Launch Cue or enable Delivered only if needed

**Weekly Power User Flow**
1. Review category trends in Price Wire
2. Apply bulk recommendations
3. Export report for ownership

### 2.6 Mobile vs Desktop

**Mobile**
- Consumption first
- Top 5 price moves, critical alerts, quick approve
- Push alerts for competitor undercuts and CCC actions

**Desktop**
- Full data tables, exports, deeper analysis
- Bulk pricing adjustments and scenario modeling

---

## 3. Technical Build

### 3.1 Scraping and Pricing Data Pipeline

**Sources**
- Dutchie, Leafly, Weedmaps, Jane, I Heart Jane, direct dispensary sites

**Pipeline**
1. Source registry per store with URL and method
2. Scheduler triggers daily full scrape and hourly deltas for watched SKUs
3. Parse to common schema, normalize units, brands, and categories
4. SKU matching with fuzzy matching and brand dictionary
5. Store raw data and normalized data with timestamps
6. Flag outliers and changes for manual review

**Quality controls**
- Price sanity checks with thresholds
- Confidence scores on SKU matches
- Manual override tool for high volume SKUs

**Decision where plans differ**
Two plans specify 6 hour refresh cycles. One suggests 12 hours. We choose 6 hours for competitive advantage and data freshness. Hourly deltas for watched SKUs.

### 3.2 CCC Intelligence Pipeline

**Sources**
- CCC license lists, meeting minutes, enforcement actions
- Municipal zoning agendas and permits
- Commercial real estate listings for cannabis zones

**Processing**
- OCR and NLP on PDFs
- Entity extraction for licensee, address, license type, decision
- Geocode and match to operator locations
- Alert classification by threat level

### 3.3 Margin Engine AI

**Inputs**
- Competitor price index by SKU and category
- Operator price history and velocity data
- Inventory levels if integrated
- Seasonal factors and promo history

**Models**
- Baseline rules for minimum margin thresholds
- Gradient boosting for price elasticity and recommendation
- Optional LLM for natural language reasoning in recommendation cards

**Outputs**
- Recommended price with confidence score
- Expected units, revenue, margin impact
- Suggested Cue campaign if inventory risk is high

**Decision where plans differ**
One plan suggests a Bayesian model for sparse data. Two favor gradient boosting with rule based backstop. We choose gradient boosting with rules, and add Bayesian later once data density improves. This is faster to explain and easier to trust.

### 3.4 Tech Stack

- Frontend: React, TypeScript, Tailwind, Recharts
- Mobile: React Native
- Backend: Node.js with Fastify or NestJS
- ML: Python with FastAPI
- DB: Postgres for core, ClickHouse for time series, Redis for cache
- Scraping: Playwright with proxy pool
- Queue: BullMQ or SQS
- Hosting: AWS ECS, RDS, S3, CloudFront
- Monitoring: Datadog, Sentry

### 3.5 Phased Timeline

**Phase 0, Weeks 1 to 2**
- Scrape 20 dispensaries, validate Price Wire
- Five operator interviews with live data

**Phase 1, Weeks 3 to 6**
- Core dashboard, Price Wire, Threat Radar MVP
- Manual CSV upload for velocity data
- Mobile shell with Morning Brief

**Phase 2, Weeks 7 to 12**
- Margin Engine v1 with rules and simple model
- Desktop web app with exports
- Expand scraping to 50 stores

**Phase 3, Weeks 13 to 20**
- Cue integration, budtender profiles, payouts
- Delivered toggle with eligibility logic
- AC Toll Processing request flow

**Phase 4, Weeks 21 to 30**
- Full MA coverage, performance hardening
- Premium analytics tier and API access
- Scale to 100 operators

---

## 4. Go to Market

### 4.1 Seed the First 20 Operators

**Selection criteria**
- High volume and price sensitive operators
- Geographic coverage across MA
- Existing Roviq or AC relationships

**Outreach sequence**
1. Email with a screenshot of their price position
2. Call with a competitor undercut example
3. Offer a daily price digest and a 10 minute demo

**Promise**
- Price Wire live within 48 hours
- First insight delivered within 24 hours

### 4.2 Pricing

**Core**
- Free forever for Price Wire, Threat Radar, basic Margin Engine

**Premium analytics**
- $99 per store per month for real time alerts, exports, and API access

**Margin Engine Pro**
- $299 to $399 per store per month depending on data integrations

**Cue**
- Brands pay 10 percent of spend or a flat tier
- Operators pay nothing

**Delivered**
- 12 to 20 percent of delivery GMV, with minimums by store

**AC Toll Processing**
- Per unit fee with volume discounts, GLASS earns a commission

**Roviq Agency**
- Standard retainers, GLASS operators get priority and a small discount

**Decision where plans differ**
Two plans propose free core with paid spokes. One includes a paid core. We keep core free and monetize premium analytics plus spokes. This is best for adoption and data density.

### 4.3 Cue Brand Acquisition

- Start with 5 local brands and 3 MSO brands
- Use AC as anchor brand
- Offer a pilot with two operators and guaranteed placement
- Provide closed loop reporting on units sold and budtender payouts

### 4.4 Newsletter Funnel

**GLASS Weekly**
- Top price moves, CCC updates, and best performing promos
- CTA: claim your Price Wire dashboard

Targets
- Month 3: 500 subscribers
- Month 6: 1,500 subscribers
- Month 12: 5,000 subscribers

---

## 5. Revenue Model

### 5.1 Assumptions
- 50 operators in year 1, 100 in year 2
- 10 to 15 percent convert to premium analytics
- Cue grows from 10 to 30 brands by year 2

### 5.2 Projections, Year 1

**Margin Engine Pro**
- 30 stores at $399 per month
- Annual: $143,640

**Cue**
- 10 brands, average $1,000 per month spend, 10 percent fee
- Annual: $120,000

**Delivered**
- 10 stores, average $1,500 per month minimum
- Annual: $180,000

**AC Toll Processing**
- 2 million prerolls at $0.25 to $0.50 margin
- Annual: $500,000 to $1,000,000

**Roviq Agency**
- 6 clients at $2,500 per month
- Annual: $180,000

**Premium analytics**
- 5 stores at $99 per month
- Annual: $5,940

### 5.3 Timeline to First Dollar
- Month 1: AC Toll pilot
- Month 2: Roviq Agency upsell
- Month 3: Delivered pilot
- Month 4: Cue contracts
- Month 4 to 5: Margin Engine Pro subscriptions

### 5.4 Unit Economics
- Blended CAC: $500 to $1,200 per operator
- Scraping cost per store per month: $3 to $5
- Core cost per operator per month: $40 to $50 including support
- Margin Engine Pro gross margin: 85 percent
- Cue gross margin: 70 percent
- Delivered gross margin: 25 percent

---

## 6. Competitive Moat

### 6.1 Against Dutchie, Leafly, LeafLink

- Dutchie is a POS and ecommerce platform, not a competitive intelligence layer
- Leafly is consumer focused and lacks operator workflows
- LeafLink is wholesale, not retail

GLASS is operator first and built for daily decisions. None of the incumbents can credibly show competitor pricing across all platforms, nor can they offer MA specific CCC intelligence.

### 6.2 Network Effects

More operators create more pricing data and better models. Better models deliver better recommendations, which increases adoption. Cue and Delivered grow with operator density. This flywheel is the core moat.

### 6.3 Massachusetts Advantages

- MA is small and dense, which makes local data accuracy a major advantage
- CCC data is unique and complex, GLASS is tuned to MA regulatory structure
- Delivered has delivery exclusivity through 2029, which competitors cannot replicate

---

## 7. Risks and Mitigations

### Legal and Compliance
- **Risk:** scraping terms enforcement
  - **Mitigation:** use public pages only, rate limit, maintain operator sourced data, legal review
- **Risk:** budtender incentive compliance
  - **Mitigation:** legal review, use compliant payout models, restrict campaigns by rules

### Technical
- **Risk:** menu source changes break scrapers
  - **Mitigation:** modular scrapers, monitoring, fast patch cycles, multiple sources
- **Risk:** inaccurate recommendations harm trust
  - **Mitigation:** confidence scores, explain reasoning, manual approval, gradual rollout
- **Risk:** data breach
  - **Mitigation:** encryption, minimal data collection, security audits, incident plan

### Market
- **Risk:** operator skepticism
  - **Mitigation:** free core, value in first 60 seconds, social proof from local operators
- **Risk:** slow Cue adoption
  - **Mitigation:** use AC and Delivered relationships to seed, pilot offers with guaranteed placement

---

## 8. Implementation Roadmap

### Phase 0, Weeks 1 to 2
- Scrape 20 dispensaries, validate Price Wire accuracy
- Five operator demos with real data
- Newsletter landing page live

### Phase 1, Weeks 3 to 6
- Morning Brief dashboard on web and mobile
- Threat Radar MVP with CCC data
- Basic alert engine and price watch lists

### Phase 2, Weeks 7 to 12
- Margin Engine v1 with rules and basic model
- Desktop analytics and exports
- Expand to 50 stores

### Phase 3, Weeks 13 to 20
- Cue beta, budtender payouts, brand dashboards
- Delivered toggle for eligible towns
- AC Toll Processing request and scheduling flow

### Phase 4, Weeks 21 to 30
- Full MA coverage
- Premium analytics tier
- Operator base to 100

### Key Milestones
- 20 seed operators live by Week 6
- Margin Engine adoption above 30 percent by Week 12
- First Cue brand paying by Week 16
- Delivered live in 10 stores by Week 20
