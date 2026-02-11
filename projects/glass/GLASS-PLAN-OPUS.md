# GLASS Product Plan — Massachusetts Cannabis OS

GLASS is the hub. Everything else is a spoke. Core is free and immediate value. Spokes are paid, operationally tied to Core data.

## 1. Product Architecture

### Dashboard Layout

**Top bar**
- Location selector, time window, export, alerts bell, account

**Left nav**
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

**Home dashboard (single screen)**
- Today’s Market Pulse
  - Median price by category in 10 mile radius
  - Price delta vs your store for top 20 SKUs
  - Velocity ranking for your top 30 SKUs
- Alerts
  - 3 competitor price drops
  - CCC license update near you
  - Margin risk list
- “Fix It Now” actions
  - Price 5 SKUs
  - Launch Cue incentive
  - Turn on Delivered for 2 zip codes

Strong opinion: The home screen should be a checklist. Operators are skeptical. They need immediate, visible fixes.

### Key Screens

**Price Wire**
- Map of competitors with distance and price index
- Table: SKU, competitor price range, your price, delta, last change time
- Drilldown: SKU history, price volatility, suggested change
- Export to CSV and POS integration later

**Threat Radar**
- CCC feed summary by county
- Filters: license actions, violations, enforcement actions, new approvals, renewals
- “Impact score” that ranks relevance to your location and category

**Margin Engine**
- Pricing recommendation list
- Confidence score and reasoning
- Simulated impact: revenue, margin, unit velocity
- “Apply” button that creates a task, not auto change. Auto change only after explicit opt in

**Spokes Hub**
- Cards for each spoke with status and ROI snapshot
- CTA: Start trial, request setup, or enable toggle

### Data Flows

1. **Menu scrape → SKU normalization → price index**
2. **CCC data ingest → location match → alert engine**
3. **Operator sales velocity data → model training**
4. **All above → Margin Engine recommendations**
5. **Spoke data → performance feedback → model tuning**

### Spoke Integration

**Cue**
- Inside Margin Engine list, add a “Promo bias” toggle. If a brand sponsor exists, recommendations can prioritize that SKU in suggested incentives
- Incentive results feed back into velocity data for Margin Engine

**Delivered**
- Toggle in Home dashboard with zip code coverage and expected revenue
- Delivered data becomes a channel in margin and velocity analytics

**AC Toll Processing**
- “House brand potential” panel in Margin Engine based on gross margin and repeat purchase
- Suggests SKUs for white label prerolls and sends a one click quote request to AC

**Roviq Agency**
- “Growth gaps” banner appears if operator lacks SEO, ads, or email. Single click schedule call

### User Journey

**Signup → value in 60 seconds → paid conversion**

1. **Signup**
   - Owner or GM enters store name and POS or menu URL
   - If POS not connected, allow menu URL for instant Price Wire

2. **60 seconds to value**
   - GLASS shows 10 SKU price deltas and one high risk margin gap
   - One CCC alert relevant to their city
   - One actionable recommendation

3. **7 day conversion path**
   - Day 1: Price Wire insights and saved list
   - Day 3: Margin Engine trial recommendation set, email and SMS
   - Day 5: Offer Cue incentive trial paid by brand, no cost to operator
   - Day 7: Offer Delivered pilot or AC Toll quote

### Mobile vs Desktop

- **Desktop** is for deep pricing work, exports, and management
- **Mobile** is for alerts, quick approval, and Cue incentives for managers on floor
- Mobile should be a companion, not a full admin tool

## 2. Technical Build

### Menu Scraping Pipeline

**Targets**: Dutchie, Leafly, Weedmaps, Jane

**Flow**
1. **Discovery**
   - Seed list of MA dispensaries with menu platform
   - Store URL templates per provider

2. **Scrape jobs**
   - Provider specific workers in a queue
   - Daily full refresh, hourly delta checks

3. **Normalization**
   - Standard schema: SKU name, category, brand, THC, size, price, specials
   - Product matching via fuzzy hash and brand dictionary

4. **Quality**
   - Confidence scores on SKU match
   - Manual override tool in admin

Strong opinion: accuracy beats volume. If a SKU match is wrong, trust is gone.

### CCC Data Integration

**Sources**
- Public CCC data feeds and filings
- Manual entries when needed

**Pipeline**
- Nightly ingest of CCC updates
- Geocode addresses for distance alerts
- Classify into “risk” and “opportunity” alerts

### Margin Engine AI

**Inputs**
- Competitor price index by SKU and category
- Operator velocity data by SKU and time window
- Seasonality, promotions, holidays

**Models**
- Baseline rules: min margin thresholds per category
- Predictive model: gradient boosting for price elasticity
- Optional ML: Bayesian hierarchical model to handle sparse data across operators

**Outputs**
- Recommended price, confidence, expected impact
- Suggested promotion or bundle when elasticity is low

### Tech Stack

- **Frontend**: React, Vite, Tailwind
- **Backend**: Node.js with NestJS or Fastify
- **DB**: Postgres for core, Redis for cache, ClickHouse for time series price history
- **Scraping**: Playwright workers, Python for parsing, or Node workers for scale
- **Hosting**: AWS or Fly.io for core app, S3 for assets
- **Queue**: BullMQ or AWS SQS
- **Auth**: Clerk or Supabase Auth

### Build Phases and Timelines

**Phase 0. Two week validation**
- Scrape 20 dispensaries, show Price Wire prototype
- Validate with 5 operators

**Phase 1. Month 1 to 2**
- Core dashboard, Price Wire, CCC ingest
- Manual CSV upload for velocity data

**Phase 2. Month 3 to 4**
- Margin Engine v1 with rule based pricing
- Cue integration stub and sign up

**Phase 3. Month 5 to 6**
- ML pricing model, Delivered toggle, AC Toll quote workflow
- Premium analytics and exports

## 3. Go to Market

### Seed First 20 Operators

**Target list**
- Use 321 retailer contacts
- Prioritize: high volume, price sensitive, multi location

**Outreach**
- 1:1 outreach by Randy and Roviq
- “Price Wire in 48 hours” promise
- Free first 30 days of Margin Engine, paid after

**Onboarding goal**
- First insight delivered in 1 day
- If not, refund time with white glove support

### Pricing Per Spoke

**Core**
- Free forever, no limits on Price Wire or Threat Radar

**Margin Engine**
- $399 per location per month after 30 day trial

**Cue**
- Brands pay $2,000 per month per retailer for incentives
- Operator cost is zero, operator approves which brands

**Delivered**
- 12 percent of delivery GMV, minimum $1,500 per month per store

**AC Toll Processing**
- $0.50 per preroll tolling fee, plus material cost

**Roviq Agency**
- $2,500 per month retainer for marketing and growth

### Brand Acquisition for Cue

- Start with 5 local brands and 3 national MSO brands
- Pitch: only channel that reaches budtenders at moment of sale
- Show closed loop reporting from incentives to units sold

### Newsletter Funnel

- Weekly “GLASS Market Pulse”
- Top 3 price moves, CCC alert, best performing promotions
- CTA: claim your Price Wire link and free dashboard

## 4. Revenue Model

Assume 200 MA retailers, 50 targetable in first year

**Year 1 projections**
- Margin Engine: 30 stores x $399 x 12 = $143,640
- Delivered: 10 stores x $1,500 x 12 = $180,000
- Cue: 15 brands x 10 retailers x $2,000 x 12 = $3,600,000
- AC Toll: 5M prerolls x $0.50 = $2,500,000
- Roviq Agency: 6 clients x $2,500 x 12 = $180,000

**Timeline to first dollar**
- Month 1: AC Toll pilot with AC
- Month 2: Roviq agency upsell to first GLASS users
- Month 3: Delivered pilot revenue
- Month 4: Cue brand contracts
- Month 4 to 5: Margin Engine subscriptions

**Unit economics per operator**
- CAC: $1,200, mostly founder time and on site
- Core cost: $40 per month per operator for scraping and data
- Margin Engine gross margin: 85 percent
- Delivered gross margin: 25 percent after driver cost and compliance
- Cue gross margin: 70 percent

## 5. Competitive Moat

- **Local density**. MA market is small and regulated. Data quality wins. National platforms have lower incentive to stay current.
- **Exclusive delivery**. Delivered license MD1303 locks delivery access to 2029. Leafly cannot replicate without a license.
- **Integrated workflow**. Price Wire feeds Margin Engine and Cue. Competitors sell isolated products.
- **Brand and operator network effects**. More operators give better pricing models, which drives more operator adoption. Brands follow the budtenders.
- **MA relationships**. Roviq is local, AC is local, Delivered is local. This is not a national play.

## 6. Risks and Mitigations

### Legal

**Risk**: Scraping claims from menu platforms
- **Mitigation**: Follow robots, cache minimal data, store only normalized pricing, be ready to license data from platforms if needed

**Risk**: CCC data accuracy and licensing
- **Mitigation**: Maintain data logs, link to original public sources, add manual validation

### Technical

**Risk**: SKU matching errors
- **Mitigation**: Confidence scoring, manual override tool, focus on high volume SKUs first

**Risk**: Pipeline downtime
- **Mitigation**: redundant scraping providers, queue retries, monitoring with alerting

### Market

**Risk**: Operators refuse to pay
- **Mitigation**: Free core, proof of margin gain within 14 days, paid only if saved margin exceeds 3x fee

**Risk**: Skepticism toward AI
- **Mitigation**: Human readable reasoning, manual approval workflow, show comparisons to competitor price moves
