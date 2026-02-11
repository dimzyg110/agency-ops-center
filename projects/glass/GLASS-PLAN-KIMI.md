# GLASS Product Plan
## Unified Operating System for Massachusetts Cannabis Operators

**Version 1.0 | February 2026**

---

## Executive Summary

GLASS is the central nervous system for Massachusetts cannabis operators. It is not another menu platform. It is the intelligence layer operators need to survive a market where wholesale prices have collapsed 72% and margins are razor thin.

We are building GLASS because every operator in Massachusetts is flying blind. They do not know what competitors charge until a customer shows them a cheaper menu. They do not know when a new license opens nearby until customers disappear. They do not know if their pricing is optimized or leaving money on the table.

GLASS solves this. Free for operators. Paid by the ecosystem that depends on them.

---

## 1. Product Architecture

### 1.1 Core Philosophy: The Command Center

GLASS is designed as a command center, not a toolbelt. Operators do not want twenty tabs open. They want one screen that tells them what matters right now.

The UX follows three principles:
- **Zero friction adoption**: No integrations required to see value. No POS connection needed for core features.
- **Signal over noise**: Every alert is actionable. No vanity metrics.
- **Mobile first, desktop deep**: Check status on phone. Dig deep on laptop.

### 1.2 Dashboard Architecture

#### Primary Dashboard: The Morning Brief

Every operator starts their day with the Morning Brief. This is a single scrollable screen updated at 6 AM daily.

**Layout (Mobile):**

```
┌─────────────────────────────────────┐
│  6:23 AM  |  Green Leaf Delivery    │
│  Your market at a glance            │
├─────────────────────────────────────┤
│  🔥 PRICE ALERTS (3)                │
│  • CommCan dropped GMO 8ths to $30  │
│  • Theory Wellness added BOGO       │
│  • Your Sour D is $5 above median   │
├─────────────────────────────────────┤
│  🚨 THREAT RADAR                    │
│  • New retail license filed 2.1mi   │
│    away (Worcester, 02105)          │
│  • Cultivator violation 0.8mi east  │
│    (product recall, 3 SKUs)         │
├─────────────────────────────────────┤
│  💰 MARGIN ENGINE                   │
│  AI Recommendation: Lower Sour D    │
│  8th by $3. Projected +12 units/    │
│  week, +$89 profit.                 │
│  [Apply Now] [Dismiss] [Ask Why]    │
├─────────────────────────────────────┤
│  📊 TODAY'S NUMBERS                 │
│  Median 8th price in your radius:   │
│  $32 (down $4 from last week)       │
│  Your position: 87th percentile     │
│  [View Full Price Wire]             │
└─────────────────────────────────────┘
```

**Layout (Desktop):**

The desktop version expands to a three-column layout:
- **Left column (25%)**: Navigation, account, quick actions
- **Center column (50%)**: Data visualizations, detailed charts, threat maps
- **Right column (25%)**: Real-time alerts, Cue activity feed, deliverability status

### 1.3 Screen Breakdown

#### Screen 1: Price Wire

Purpose: Live competitor pricing intelligence

**Data displayed:**
- All products from all ~200 MA retailers, updated every 6 hours
- Filterable by: product type, brand, price range, distance, operator type (rec vs med)
- Historical price tracking (90 days)
- Price change velocity (which products are dropping fastest)
- Brand distribution (who has what SKUs)

**Key interaction: Price Watch**
Operators can "watch" specific products or categories. When prices move, they get alerted. This creates a personalized intelligence feed.

**Screen layout:**
- Top: Search bar, filter chips, radius selector
- Middle: Heat map visualization of prices by geography
- Bottom: Sortable table with: product, brand, retailer, price, price change, last updated

**Mock data example:**
```
GMO 3.5g by Happy Valley
├── CommCan: $30 (↓ $5, 2 days ago)
├── Theory Wellness: $35 (unchanged)
├── Green Leaf (YOU): $38
└── Market median: $33.50
```

#### Screen 2: Threat Radar

Purpose: Regulatory and competitive intelligence

**Data sources integrated:**
- CCC license applications and approvals (scraped daily from public records)
- CCC violations and enforcement actions (from meeting minutes and press releases)
- Local zoning board activity (scraped from municipal agendas)
- Property records (new commercial leases in cannabis zones)

**Alert types:**
- **RED**: Direct threat. New competitor opening within your defined radius.
- **YELLOW**: Indirect threat. New license in your city but different zone.
- **ORANGE**: Regulatory. Violations or recalls affecting brands you carry.
- **BLUE**: Opportunity. Competitor closed, suspended, or recalling product.

**Geographic visualization:**
Map view with threat cones radiating from the user's location. Click any marker for details.

**Example alert:**
```
🚨 NEW COMPETITOR DETECTED
Location: 847 Main Street, Worcester, MA
Distance: 2.1 miles from your location
Type: Retail (Recreational)
License Status: Provisional approved (CCC meeting 2/3/26)
Estimated Opening: Q3 2026
Owner: Green Horizon LLC (first-time operator)
Action: Monitor pricing in this zone closely
```

#### Screen 3: Margin Engine

Purpose: AI-powered pricing recommendations

**Inputs:**
- Competitor pricing data (from Price Wire)
- User's current menu prices (self-reported or POS-integrated)
- Historical sales data (if user integrates POS)
- Local demand signals (web traffic, delivery orders, search trends)
- Inventory levels (if integrated)

**Outputs:**
- Specific price recommendations by SKU
- Confidence score (how certain the AI is)
- Expected impact: units sold, revenue, margin
- Alternative scenarios: "If you matched market rate" vs "if you held premium"

**Recommendation card:**
```
SKU: Sour Diesel 3.5g (Your House Brand)
Current Price: $38
Recommended Price: $34
Confidence: 82%

Rationale:
• 5 competitors within 5 miles now offer comparable quality at $30-35
• Your sales velocity is down 23% month-over-month
• At $34, projected sales increase 15 units/week
• Even at lower price, margin remains 62%

Expected Outcome:
Weekly Revenue Impact: +$89
Weekly Unit Impact: +12 units
Margin Impact: -4% but +$89 total margin

[Apply Recommendation] [Adjust] [Dismiss] [Ask Questions]
```

**Learning loop:**
Operators can feedback on recommendations: "I took this advice" or "This was wrong because..." This trains the model specifically for Massachusetts market dynamics.

### 1.4 Spoke Integration Architecture

GLASS core stays clean. Spokes are modular add-ons visible only when relevant.

#### Cue Integration

When enabled, Cue appears as:
- Staff leaderboard widget on dashboard
- "Active Spiffs" section showing current brand incentives
- "Payment Queue" showing pending payouts to budtenders

#### Delivered Integration

For operators who activate delivery-as-a-service:
- Delivery status widget (orders in queue, drivers active, delivery radius heatmap)
- "Toggle Delivery" switch with one-click activation
- Order management interface for delivery orders

#### AC Toll Processing Integration

For operators using AC's house brand preroll service:
- Inventory widget showing current roll stock
- Order placement interface for new batches
- Margin calculator comparing roll-your-own vs outsource

### 1.5 User Journey Flows

#### New Operator Onboarding (Day 0-7)

**Day 0: Account Creation**
1. Email capture on landing page
2. Immediate access to demo dashboard with dummy data
3. Prompt to claim their dispensary from dropdown list of all MA operators
4. Email verification
5. Basic profile: name, role, notification preferences

**Day 1: First Value**
- Dashboard shows real competitor data immediately
- Highlight: "Your top 5 competitors by proximity"
- Interactive tutorial: "Set up your first Price Watch"

**Day 3: Engagement Hook**
- Push notification (if app installed) or email: "Prices changed on 12 products you are watching"
- Opens app to personalized alert screen
- Prompt: "Add your menu for personalized Margin Engine recommendations"

**Day 7: Activation Milestone**
- Check if they have added any products or prices
- If yes: Introduce Margin Engine
- If no: Re-engagement email with case study: "How Theory Wellness uses Price Wire"

#### Daily Active User Flow

1. Open app → Morning Brief loads automatically
2. Scan alerts (10-30 seconds)
3. Tap any alert for detail (30 seconds-2 minutes)
4. Possible actions:
   - Adjust own price (takes to Margins screen)
   - Watch a competitor (takes to Price Wire)
   - Respond to Cue spiff (takes to Cue)
   - Check delivery status (takes to Delivered)
5. Exit with zero or one action taken

Target: Average session under 3 minutes. This is intelligence, not work.

#### Weekly Power User Flow

1. Review full Price Wire for category trends (15 minutes)
2. Run Margin Engine recommendations. Apply or dismiss (10 minutes)
3. Check Threat Radar for new developments (5 minutes)
4. Adjust pricing strategy based on data (10 minutes)
5. Export report for ownership/management (5 minutes)

Total: 45 minutes once per week. This operator gets disproportionate value from GLASS.

### 1.6 Mobile vs Desktop Strategy

**Mobile (70% of sessions expected):**
- Optimized for consumption, not action
- Push notifications for critical alerts
- Quick-apply recommendations (one-tap pricing changes)
- Location-aware features (check competitor prices when visiting other dispensaries)
- Offline mode: Last-loaded data available without connection

**Desktop (30% of sessions, higher value):**
- Full data analysis capabilities
- Export functions (CSV, PDF reports)
- Bulk pricing adjustments
- Deep-dive investigation tools
- Admin features: team management, API access, integrations

**Shared state:**
Any action on mobile reflects immediately on desktop. Same account, same data, different interface density.

---

## 2. Technical Build

### 2.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         GLASS PLATFORM                          │
├─────────────────────────────────────────────────────────────────┤
│  PRESENTATION LAYER                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Mobile App │  │   Web App   │  │  Partner Dashboards     │  │
│  │(React Native)│ │  (React/Web)│  │  (Cue, Delivered, AC)   │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────────┘  │
├─────────┴────────────────┴──────────────────────────────────────┤
│  API GATEWAY (Kong/AWS API Gateway)                             │
│  • Auth (JWT) • Rate limiting • Request routing • Logging       │
├─────────────────────────────────────────────────────────────────┤
│  APPLICATION LAYER (Node.js/TypeScript Microservices)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐  │
│  │   User   │ │  Pricing │ │  Threat  │ │  Margin Engine     │  │
│  │ Service  │ │ Service  │ │ Service  │ │  (Python/ML)       │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐  │
│  │   Cue    │ │ Delivered│ │   AC     │ │  Notification      │  │
│  │ Service  │ │ Service  │ │ Service  │ │  Service           │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐  │
│  │PostgreSQL│ │ClickHouse│ │   Redis  │ │  Vector DB         │  │
│  │(Users,   │ │ (Time-   │ │  (Cache, │ │  (Pinecone/Weaviate│  │
│  │Products) │ │ series)  │ │  Queues) │ │  for AI)           │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  INTEGRATION LAYER                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐  │
│  │Scraping  │ │CCC Ingest │ │ POS APIs │ │  Webhooks          │  │
│  │Engine    │ │Pipeline   │ │(Dutchie, │ │  (External)        │  │
│  │(Playwright│ │(Airflow) │ │  Leafly) │ │                    │  │
│  │  + Proxy)│ │           │ │          │ │                    │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Scraping Pipeline (Price Wire Data)

This is the critical infrastructure. If the scraping fails, GLASS has no value.

#### Target Data Sources

**Tier 1: Direct menu sites (highest priority, majority of data)**
- Dutchie-powered menus (60%+ of MA operators)
- Leafly menus
- Jane menus
- I Heart Jane
- Custom dispensary websites with ecommerce

**Tier 2: Aggregators (validation layer)**
- Leafly listing pages
- Weedmaps (if legally accessible)
- Google Shopping results

**Tier 3: Manual fallback**
- Operators who email menus
- Phone verification for price disputes

#### Technical Implementation

**Scraping Bot Architecture:**

```python
# Core scraping module structure
class PriceScraper:
    def __init__(self):
        self.proxy_pool = ProxyPool()  # Rotating residential proxies
        self.browser_pool = BrowserPool()  # Playwright browsers
        self.rate_limiter = RateLimiter(max_requests=10/minute/source)
    
    async def scrape_dispensary(self, dispensary: Dispensary) -> ScrapedData:
        # 1. Load browser with fingerprint rotation
        # 2. Navigate to menu page
        # 3. Handle pagination/infinite scroll
        # 4. Extract structured data
        # 5. Detect changes from last scrape
        # 6. Store with provenance metadata
        pass
```

**Anti-detection measures:**
- Rotating residential proxies (PacketProxy, BrightData)
- Browser fingerprint randomization
- Human-like behavior patterns (random delays, mouse movements)
- Request rotation (never same pattern twice)
- JavaScript execution (not just HTML parsing)

**Data normalization:**
- Product name standardization (fuzzy matching)
- Unit conversion (3.5g = 1/8th, 7g = 1/4, etc.)
- Brand extraction from product names
- Category classification (flower, vape, edible, etc.)
- Price per unit calculation (price per gram for comparison)

**Storage format:**
```json
{
  "scraped_at": "2026-02-11T06:00:00Z",
  "dispensary_id": "disp_12345",
  "source_url": "https://...",
  "products": [
    {
      "sku_id": "sku_abc123",
      "raw_name": "GMO Flower 3.5g by Happy Valley",
      "normalized_name": "GMO",
      "brand": "Happy Valley",
      "category": "flower",
      "quantity_g": 3.5,
      "price": 30.00,
      "price_per_g": 8.57,
      "availability": "in_stock",
      "promotions": ["new_batch"],
      "last_changed_at": "2026-02-09T14:30:00Z"
    }
  ]
}
```

#### Scheduling

- **Full scrapes**: Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
- **High-priority watches**: Every hour (products users are actively monitoring)
- **New/changed detection**: Immediate re-scrape when anomaly detected
- **Historical backfill**: Full 90-day history on first run for trend analysis

#### Quality Assurance

- **Validation rules**: Price sanity checks (flag $1/g as error, flag $100/g as premium)
- **Cross-reference**: Same product should have similar prices across sources
- **Human review queue**: Flagged changes go to manual verification
- **User feedback loop**: Operators can report incorrect data

### 2.3 CCC Intelligence Pipeline (Threat Radar)

The Cannabis Control Commission publishes meeting minutes, license lists, and violation records. We need to turn this unstructured data into structured intelligence.

#### Data Sources

**Public CCC pages:**
- Approved license list (Excel, monthly update)
- Meeting agendas and minutes (PDF, weekly)
- Enforcement actions (web page, sporadic)
- Public comment notices (for new licensees)

**Municipal sources:**
- Zoning board agendas (varies by city, often PDF)
- City council meeting minutes
- Building permit databases

**Commercial real estate:**
- LoopNet listings
- CoStar feeds
- Local broker reports

#### Processing Pipeline

```python
class CCCIntelligencePipeline:
    def process_meeting_minutes(self, pdf_url: str) -> List[Dict]:
        # 1. Download PDF
        # 2. OCR if needed
        # 3. Extract text
        # 4. NER (Named Entity Recognition) to find:
        #    - Business names
        #    - Addresses
        #    - License types
        #    - Decision outcomes
        #    - Conditions or violations
        # 5. Geocode addresses
        # 6. Match to existing operators or flag as new
        # 7. Generate alerts
        pass
```

**NLP Model:**
- Fine-tuned BERT model for cannabis regulatory text
- Trained on historical CCC minutes
- Extracts entities: licensee names, addresses, license categories, decision types, violations, fines

**Geocoding:**
- Google Maps API for address standardization
- Distance calculations to all operator locations
- Radius-based alert assignment

**Alert classification:**
```python
class AlertType(Enum):
    NEW_COMPETITOR = "new_competitor"  # New retail within 5 miles
    NEW_SUPPLY = "new_supply"  # New cultivation or manufacture
    VIOLATION_NEARBY = "violation_nearby"  # Compliance issue in area
    ENFORCEMENT_ACTION = "enforcement_action"  # License suspension, fines
    ZONING_CHANGE = "zoning_change"  # Municipal policy shift
    OPPORTUNITY = "opportunity"  # Competitor closed or suspended
```

### 2.4 Margin Engine AI Models

The recommendation engine is GLASS's moat. This is not generic ML. It is trained specifically on cannabis pricing dynamics.

#### Model Architecture

**Primary model: Gradient Boosted Decision Trees (XGBoost/LightGBM)**

Why not deep learning? Because interpretability matters. Operators want to know WHY a price is recommended. Tree-based models provide feature importance naturally.

**Input features:**

Product-level:
- Current price
- Price percentile vs market (0-100)
- Price vs nearest 5 competitors
- Historical price changes (volatility)
- Days since last price change

Market-level:
- Median price in radius (5mi, 10mi, statewide)
- Price trend (7-day, 30-day slope)
- Number of competing SKUs
- Supply pressure indicators (new licenses nearby)
- Seasonal factors (4/20, summer dip, harvest season)

Operator-level (if integrated):
- Sales velocity for this SKU
- Days of inventory remaining
- Overall operator price position (premium vs discount)
- Historical response to price changes

**Output:**
- Optimal price point
- Confidence interval
- Expected demand elasticity
- Revenue impact projection
- Margin impact projection

#### Training Data

Simulated training data for initial model:
- Synthetic operator profiles representing MA market diversity
- Historical price data from scraping
- Estimated demand elasticities from academic cannabis studies
- Hand-labeled "good" vs "bad" pricing decisions by domain experts

As real data flows in:
- Operator actions on recommendations (did they take the suggestion?)
- Actual outcomes (sales data from integrated POS)
- Continuous retraining pipeline (weekly batch updates)

#### Recommendation Confidence

```python
def calculate_confidence(
    data_quality: float,  # How complete is the input data
    market_volatility: float,  # Recent price variance
    operator_history: float,  # Do we have past outcomes for this operator
    model_agreement: float  # Do multiple models agree
) -> ConfidenceLevel:
    score = weighted_average([
        data_quality * 0.3,
        (1 - market_volatility) * 0.2,
        operator_history * 0.3,
        model_agreement * 0.2
    ])
    
    if score > 0.8:
        return ConfidenceLevel.HIGH
    elif score > 0.5:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW
```

### 2.5 Tech Stack Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| API/Backend | Node.js + TypeScript + Express/Fastify | Team familiarity, ecosystem |
| ML Services | Python + FastAPI | Ecosystem for data science |
| Database (OLTP) | PostgreSQL 15 | ACID compliance, user data |
| Database (Analytics) | ClickHouse | Fast time-series queries |
| Cache | Redis | Session, queues, real-time data |
| Vector DB | Pinecone | Product similarity matching |
| Scraping | Playwright + Python | Modern JS sites, headless |
| Orchestration | Apache Airflow | Pipeline scheduling |
| Queue | Bull (Redis) | Background job processing |
| Auth | Auth0 or Clerk | Fast implementation, security |
| Hosting | AWS (ECS/RDS/Elasticache) | Scalability, compliance |
| CDN | CloudFront | Static assets, edge caching |
| Monitoring | Datadog | Full observability |
| Error Tracking | Sentry | Real-time alerts |

### 2.6 Build Phases

#### Phase 1: Foundation (Weeks 1-6)

**Goal:** Working Price Wire for 20 seed operators

Week 1-2: Infrastructure
- AWS account setup, VPC, security groups
- Database provisioning (PostgreSQL, Redis)
- CI/CD pipeline (GitHub Actions)
- Scraping infrastructure (proxies, browser farm)

Week 3-4: Core API
- User service (auth, profiles, preferences)
- Price service (scraping, storage, retrieval)
- Basic mobile app shell (React Native)

Week 5-6: Price Wire MVP
- Scraper running for top 50 MA dispensaries
- Mobile dashboard showing competitor prices
- Price Watch alerts (push notifications)
- Onboard 5 friendly operators for feedback

**Success criteria:**
- Scraper captures 95%+ of products from target sites
- Data freshness under 6 hours
- 5 operators using app daily

#### Phase 2: Intelligence (Weeks 7-12)

**Goal:** Threat Radar + Margin Engine v1

Week 7-8: CCC Pipeline
- Meeting minutes ingestion (PDF parsing, NLP)
- License database matching
- Alert generation engine
- Map visualization

Week 9-10: Margin Engine
- Feature engineering pipeline
- Initial model training
- Recommendation API
- A/B testing framework

Week 11-12: Desktop Web App
- Full dashboard web interface
- Export/reporting tools
- Admin panel for internal use
- Expand to 20 operators

**Success criteria:**
- Threat Radar alerts within 24 hours of CCC publication
- Margin Engine generates recommendations with >60% operator adoption rate
- 20 active operators (daily active users)

#### Phase 3: Spokes (Weeks 13-20)

**Goal:** Cue integration and Delivered toggle

Week 13-14: Cue API
- Budtender profile management
- Spiff creation interface (brands)
- Payment tracking
- Leaderboards

Week 15-16: Delivered Integration
- Delivery toggle in operator settings
- Order routing to Delivered backend
- Status tracking in GLASS dashboard

Week 17-18: AC Toll Processing
- Order placement UI
- Inventory tracking
- Margin calculator

Week 19-20: Polish and Scale
- Performance optimization
- Security audit
- Expand operator base to 50

**Success criteria:**
- First Cue brand pays for featured placement
- 5 operators enable Delivered delivery option
- 100 total operators on platform

#### Phase 4: Scale (Weeks 21-30)

**Goal:** 200 operators (full MA retail market)

- Aggressive onboarding campaigns
- Referral program
- Advanced analytics features
- API access for enterprise operators
- White-label options for multi-state operators

---

## 3. Go-to-Market Strategy

### 3.1 Target Market Analysis

**Total Addressable Market (TAM):**
- ~200 retail dispensaries (rec + med)
- ~100 cultivation facilities
- ~50 manufacturing/processing licenses

**Serviceable Available Market (SAM):**
We are only targeting retail dispensaries for GLASS core.
- 200 dispensaries
- Average 3 decision-makers per dispensary (owner, GM, buyer)
- 600 potential user accounts

**Serviceable Obtainable Market (SOM):**
Year 1 target: 50 operators (25% market penetration)
Year 2 target: 100 operators (50% market penetration)

### 3.2 Seed Cohort Strategy: The First 20

The first 20 operators are not random. They are selected for influence, feedback quality, and willingness to engage.

**Selection criteria:**
1. **Market leaders** (top 10 by revenue) - They set the pace others follow
2. **Innovators** (early tech adopters) - They will give real feedback
3. **Geographic spread** - Cover all regions to validate scraping everywhere
4. **Roviq relationships** - Existing agency clients get priority access

**Seed cohort benefits:**
- Free lifetime access to core features
- Direct hotline to Roviq team for support
- Input on product roadmap
- Co-marketing: "Founding Partner" badge on their GLASS profile
- First access to new features

**Recruitment sequence:**

Week 1-2: Warm outreach
- Email to Roviq agency contacts
- Personal calls to existing relationships
- Target: 5 commitments

Week 3-4: Cold outreach with social proof
- Email to remaining targets mentioning early commitments
- LinkedIn outreach with case study preview
- Target: 10 more commitments

Week 5-6: Event recruitment
- Attend industry events with demo
- Collect signups in person
- Target: 5 more to reach 20

**Outreach template:**
```
Subject: Early access: Massachusetts cannabis intelligence platform

Hi [Name],

I am reaching out because [Roviq/AC/Delivered] has worked with [their company or similar].

The Massachusetts cannabis market is brutal. Prices down 72%. Margins compressed. Every operator is flying blind on what competitors charge.

We built GLASS to fix this. It is intelligence for operators:
- Daily competitor price tracking across all 200 MA dispensaries
- Automated alerts when threats emerge (new licenses, violations nearby)
- AI recommendations for optimal pricing

We are selecting 20 operators for our Founding Partner program. Founding Partners get:
  • Free lifetime access to core features
  • Direct input on product direction
  • Founding Partner badge

I would love to show you a 10-minute demo next week. Are you available [day] or [day]?

Best,
[Name]
```

### 3.3 Pricing Strategy

#### Core Platform (Free Forever)

All operators get:
- Price Wire (competitor pricing data)
- Threat Radar (regulatory intelligence)
- Margin Engine (AI recommendations)
- Morning Brief daily alerts
- Mobile and web access

**Why free?**
- Zero friction adoption. Skeptical operators have no excuse not to try.
- Network effects require volume. We need data from 100+ operators for the Margin Engine to be valuable.
- Revenue comes from spokes, not core. The core is the funnel.

#### Premium Tier (Optional, $99/month)

For power users who want more:
- Real-time price alerts (vs 6-hour delay)
- Historical data exports (CSV, Excel)
- Advanced analytics (custom reports)
- API access
- Priority support
- White-label reports for investors/lenders

Target: 10-20% of base converts to premium.

#### Spoke Pricing

**Cue:**
- Free for operators (it is inside GLASS)
- Brands pay: $500/month for spiff placement
- $50 per completed spiff (operator/budtender paid separately)

**Delivered:**
- Free to enable (toggle inside GLASS)
- Delivered takes 15% of delivery orders (standard marketplace fee)
- Operators keep 85% for zero operational overhead

**AC Toll Processing:**
- Pricing TBD by AC, likely per-unit fee
- Commission to Roviq/GLASS: 10% of AC revenue from GLASS-sourced orders

**Roviq Agency:**
- Standard agency rates
- GLASS operators get 10% discount on all services (incentive to join)

### 3.4 Cue Brand Acquisition

**Target brands:** 50+ cannabis brands selling in Massachusetts

**Value proposition:**
- "Your competitors are paying budtenders to push their products. Are you?"
- Direct access to budtender community through GLASS
- Detailed analytics: which stores, which budtenders, conversion rates
- No setup: just fund spiffs and watch them work

**Acquisition channels:**
1. Direct sales: Roviq BD team targets top 20 brands
2. Self-serve: Brands apply through GLASS website
3. Referral: Operators tell their brand reps about Cue
4. Events: Tabling at CannaCon, NECANN with live demos

**Pricing tiers for brands:**
- Starter: $500/month, 1 active spiff, basic analytics
- Growth: $1,500/month, 5 active spiffs, detailed reporting
- Enterprise: $5,000/month, unlimited spiffs, API access, dedicated account manager

### 3.5 Newsletter as Distribution Channel

**"The GLASS Weekly"**

Sent every Monday morning to all subscribers (operators, brands, industry observers).

**Content format:**
- **Market Snapshot**: Average price movement this week, top moving products
- **Intelligence Brief**: Notable CCC activity, upcoming license decisions
- **Operator Spotlight**: Interview with featured operator using GLASS
- **Product Updates**: New features, upcoming releases

**Primary goal:** Drive operator signups
- Every issue has a clear CTA: "Get these alerts for your own store"
- Forward tracking to see which operators share it
- Reply-to for direct feedback

**Secondary goal:** Brand list building
- Brands subscribe to see market trends
- CTA: "Want to influence these trends? Learn about Cue."

**Subscriber targets:**
- Month 3: 500 subscribers
- Month 6: 1,500 subscribers
- Month 12: 5,000 subscribers

### 3.6 Launch Timeline

**Month 1-2: Quiet Beta**
- 5 operators on platform
- Daily feedback calls
- Rapid iteration

**Month 3: Seed Launch**
- 20 operators on platform
- Newsletter launches
- Soft press release

**Month 4-6: Public Launch**
- Open signup
- First Cue brand pays
- First Delivered orders flow

**Month 7-12: Scale**
- 50 operators
- 10 Cue brands
- 5 operator Delivered integration
- Consider Series A for expansion

---

## 4. Revenue Model

### 4.1 Revenue Projections by Spoke

**Assumptions:**
- Year 1: 50 operators on GLASS (25% of market)
- Year 2: 100 operators (50% of market)
- Year 3: 150 operators (75% of market)

#### Cue Revenue

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Operators on GLASS | 50 | 100 | 150 |
| Active budtenders per operator | 8 | 8 | 8 |
| Total budtender reach | 400 | 800 | 1,200 |
| Paying brands on Cue | 12 | 30 | 60 |
| Average spend per brand/month | $800 | $1,200 | $1,500 |
| Monthly Cue revenue | $9,600 | $36,000 | $90,000 |
| Annual Cue revenue | $115,200 | $432,000 | $1,080,000 |

**Notes:**
- Year 1 focused on proving model with 12 committed brands
- Year 2 scale to 30 brands (half of major MA brands)
- Year 3 market saturation with enterprise contracts

#### Delivered Revenue

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Operators with delivery enabled | 10 | 25 | 40 |
| Average orders per operator/week | 50 | 75 | 100 |
| Average order value | $85 | $85 | $85 |
| Total weekly GMV | $42,500 | $159,375 | $340,000 |
| Delivered take rate (15%) | $6,375 | $23,906 | $51,000 |
| GLASS referral fee (20% of Delivered revenue) | $1,275 | $4,781 | $10,200 |
| Monthly GLASS Delivered revenue | $5,100 | $19,125 | $40,800 |
| Annual GLASS Delivered revenue | $61,200 | $229,500 | $489,600 |

**Notes:**
- Delivered revenue flows to Delivered entity
- GLASS takes referral fee for driving the integration
- Delivered exclusivity through 2029 is key selling point

#### AC Toll Processing Revenue

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Operators using AC Toll | 5 | 15 | 30 |
| Units processed per operator/month | 2,000 | 3,000 | 4,000 |
| Total monthly units | 10,000 | 45,000 | 120,000 |
| AC revenue per unit | $0.50 | $0.50 | $0.50 |
| Total AC monthly revenue | $5,000 | $22,500 | $60,000 |
| GLASS commission (10%) | $500 | $2,250 | $6,000 |
| Annual GLASS AC revenue | $6,000 | $27,000 | $72,000 |

**Notes:**
- Conservative unit estimates
- Commission subject to negotiation with AC

#### Roviq Agency Revenue

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| GLASS operators using Roviq | 10 | 25 | 45 |
| Average monthly spend per operator | $2,000 | $2,500 | $3,000 |
| Monthly agency revenue from GLASS | $20,000 | $62,500 | $135,000 |
| Annual agency revenue from GLASS | $240,000 | $750,000 | $1,620,000 |

**Notes:**
- These are existing Roviq services
- GLASS provides qualified leads at lower CAC
- Full agency revenue counts toward Roviq, not just GLASS entity

#### Core Premium Subscriptions

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Operators on GLASS | 50 | 100 | 150 |
| Premium conversion rate | 10% | 15% | 15% |
| Premium subscribers | 5 | 15 | 22 |
| Monthly revenue | $495 | $1,485 | $2,178 |
| Annual premium revenue | $5,940 | $17,820 | $26,136 |

### 4.2 Total Revenue Projection

| Revenue Source | Year 1 | Year 2 | Year 3 |
|----------------|--------|--------|--------|
| Cue (brand fees) | $115,200 | $432,000 | $1,080,000 |
| Delivered referral | $61,200 | $229,500 | $489,600 |
| AC Toll commission | $6,000 | $27,000 | $72,000 |
| Core Premium subs | $5,940 | $17,820 | $26,136 |
| **Total GLASS Revenue** | **$188,340** | **$706,320** | **$1,667,736** |

### 4.3 Unit Economics

**Customer Acquisition Cost (CAC):**
| Channel | CAC |
|---------|-----|
| Warm referrals (existing relationships) | $200 |
| Cold outreach + demo | $800 |
| Events/tradeshows | $1,200 |
| Newsletter organic | $100 |
| Average blended CAC | $500 |

**Lifetime Value (LTV):**
| Metric | Value |
|--------|-------|
| Average operator lifespan | 36 months |
| Core premium revenue (15% convert) | $445 per operator |
| Cue revenue per operator | $2,304 over 36 months |
| Delivered referral per operator | $1,224 over 36 months |
| AC Toll per operator | $108 over 36 months |
| **Total LTV per operator** | **$4,081** |

**LTV:CAC Ratio:** 8.16:1

This is excellent. Anything above 3:1 is considered healthy.

**Payback period:** 1.5 months

### 4.4 Cost Structure

**Fixed Costs (Monthly):**
| Expense | Amount |
|---------|--------|
| Engineering (2 FTE) | $25,000 |
| Infrastructure (AWS, proxies, etc.) | $3,000 |
| Data providers (POS integrations) | $1,000 |
| Tools and software | $500 |
| Office/admin | $1,500 |
| **Total Monthly Fixed** | **$31,000** |

**Variable Costs:**
| Expense | Unit Cost |
|---------|-----------|
| Per-operator support | $20/month |
| Per-scrape cost (proxy/browser) | $0.05 |
| Daily scrapes (200 operators x 4x day) | $40/day = $1,200/month |

**Break-even Analysis:**
- Fixed costs: $31,000/month
- Variable per operator: $20 + $24 (scraping) = $44/month
- Average revenue per operator by year: $377/month
- Break-even: 31,000 / (377 - 44) = 93 operators

We break even at 93 operators, about 18 months in.

---

## 5. Competitive Moat

### 5.1 Competitor Analysis

#### Dutchie

**What they do:** POS and e-commerce for dispensaries

**Strengths:**
- Dominant market share (60%+ of MA operators)
- Integrated payments
- Strong e-commerce platform

**Weaknesses (our opportunity):**
- No competitive intelligence
- No pricing recommendations
- Closed ecosystem (does not pull competitor data)
- Expensive (operators already pay them, do not want another bill)

**Our advantage:** We are neutral. Dutchie will never show you competitor prices because they want you locked in. We show everything.

#### Leafly

**What they do:** Consumer discovery platform (Yelp for weed)

**Strengths:**
- Massive consumer brand recognition
- Some menu data
- Reviews system

**Weaknesses:**
- Consumer-first, not operator-first
- Limited data accuracy (user-reported)
- No intelligence features
- Not actionable for operators

**Our advantage:** We are built FOR operators, not for consumers. Leafly wants to sell your products. We want to make you smarter.

#### LeafLink

**What they do:** B2B wholesale marketplace

**Strengths:**
- Wholesale order management
- Brand discovery
- Some pricing data (wholesale)

**Weaknesses:**
- Wholesale only, not retail
- No competitive intelligence for retailers
- No regulatory tracking

**Our advantage:** We focus on retail operators. LeafLink helps you buy. GLASS helps you sell.

#### Other Price Tracking (Headset, BDSA)

**What they do:** Market data and analytics

**Strengths:**
- Comprehensive historical data
- Professional reports
- Industry standard

**Weaknesses:**
- Expensive ($10K+/year)
- Aggregated data only (not store-by-store)
- Delayed (weeks or months, not hours)
- No alerts, no recommendations

**Our advantage:** We are real-time and affordable. We tell you what happened yesterday, not last quarter.

### 5.2 Network Effects

This is the real moat.

**Data Network Effect:**
- More operators on GLASS → more data points → better scraping coverage → better Margin Engine recommendations → more value → more operators join

**Flywheel visualization:**
```
    More Operators
          ↓
    Better Data Coverage
          ↓
    Smarter AI Models
          ↓
    Better Recommendations
          ↓
    More Value Delivered
          ↓
    More Operators Join
```

Once we hit 100 operators (50% of market), it becomes nearly impossible for a competitor to catch up. Their models would be trained on half the data.

**Integration Network Effect:**
- Delivered needs GLASS operators to fulfill deliveries
- Cue needs GLASS budtenders to push products
- AC needs GLASS operators to sell prerolls

Each spoke makes the core more valuable. Each core user makes each spoke more valuable.

### 5.3 Massachusetts Advantages

**Regulatory complexity as a barrier:**
- MA has unique CCC reporting requirements
- Our CCC pipeline is built specifically for MA
- A competitor building generic would miss MA nuances

**Geographic concentration:**
- 200 operators is manageable for deep relationships
- We can visit every operator in person
- Word travels fast in MA cannabis (tight-knit community)

**License scarcity:**
- 27 delivery licenses total. Delivered has one. That exclusivity to 2029 is real protection.
- New cultivation/manufacturing licenses are limited
- Threat Radar becomes more valuable as the market matures

**Price compression data:**
- The 72% price drop is MA-specific
- Operators here are desperate for solutions
- First-mover advantage in a distressed market

### 5.4 Defensibility Over Time

| Year | Moat Strength | Why |
|------|---------------|-----|
| 1 | Low | Anyone can scrape prices |
| 2 | Medium | Network effects kick in, data advantage builds |
| 3 | High | AI models trained on years of MA-specific data |
| 4+ | Very High | Switching costs, habit formation, ecosystem lock-in |

---

## 6. Risks and Mitigations

### 6.1 Legal and Regulatory Risks

#### Risk: Scraping Terms of Service Violations

**Description:** Dutchie, Leafly, etc. could claim scraping violates their ToS. They could sue or block our scrapers.

**Likelihood:** Medium
**Impact:** High (core feature destroyed)

**Mitigation:**
1. **Legal review:** Have cannabis-experienced IP attorney review scraping vs. public data law
2. **Data provenance:** Only scrape publicly visible menu pages (no login required)
3. **Rate limiting:** Respect robots.txt, stay under reasonable request thresholds
4. **Alternative data:** Build direct API partnerships with willing operators
5. **Operator-sourced data:** If scraping fails, incentivize operators to share their own data

**Fallback:** If all else fails, pivot to operator-self-reported pricing (less automated, but legally bulletproof).

#### Risk: CCC Regulatory Changes

**Description:** CCC could restrict data sharing, prohibit certain types of competitive intelligence, or change reporting requirements.

**Likelihood:** Low
**Impact:** Medium

**Mitigation:**
- CCC data is all public record. We are not accessing non-public information.
- Maintain relationships with CCC staff to anticipate changes
- Stay compliant with all CCC guidance on data handling
- Be prepared to pivot Threat Radar focus if regulations shift

#### Risk: Cannabis Banking/Financial Restrictions

**Description:** Payment processors could flag GLASS as cannabis-related and freeze accounts.

**Likelihood:** Low (we do not touch plant)
**Impact:** High

**Mitigation:**
- Form entity separate from plant-touching businesses
- Use cannabis-friendly payment processors (Hypur, Safe Harbor)
- Structure revenue as SaaS/software fees, not cannabis revenue
- Maintain relationships with multiple banking options

### 6.2 Technical Risks

#### Risk: Scraping Failure

**Description:** Target sites change structure, implement bot detection, or block our IP ranges. Data quality degrades.

**Likelihood:** High (ongoing arms race)
**Impact:** High

**Mitigation:**
- **Redundancy:** Multiple scraping methods per target (Playwright, API, manual fallback)
- **Monitoring:** Alert when data freshness degrades
- **Rapid response:** Engineering team on-call for scraper fixes
- **Diversification:** Do not rely on single source (direct menus + aggregators + user input)
- **Escrow fund:** Keep 3 months of proxy/browser costs in reserve

#### Risk: AI Model Accuracy

**Description:** Margin Engine recommendations are wrong. Operators lose money on bad advice. Trust destroyed.

**Likelihood:** Medium (early days)
**Impact:** Very High

**Mitigation:**
- **Confidence scoring:** Never present low-confidence recommendations
- **Transparency:** Always explain WHY a recommendation is made
- **Gradual rollout:** Start with "information only" mode, move to "recommendation" mode later
- **Feedback loop:** Fast mechanism for operators to flag bad recommendations
- **Human oversight:** All recommendations reviewed by domain expert first 6 months
- **Insurance:** Consider E&O insurance for AI recommendation liability

#### Risk: Data Breach

**Description:** Operator data (pricing strategies, alerts) exposed. Competitive advantage leaked. Regulatory scrutiny.

**Likelihood:** Low (with proper security)
**Impact:** Very High (business ending)

**Mitigation:**
- SOC 2 Type II compliance from day one
- Encryption at rest and in transit
- Minimal data collection (only what is needed)
- Regular penetration testing
- Incident response plan documented and tested
- Cyber insurance

### 6.3 Market Risks

#### Risk: Operator Skepticism

**Description:** Massachusetts operators have been burned by tech platforms. They do not trust "free" tools. Adoption is slow.

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- **Zero commitment:** No contracts, no credit cards to start
- **Social proof:** Feature testimonials from trusted local operators
- **Roviq credibility:** Lean on existing agency relationships
- **Demonstrate value fast:** Show competitor prices in first 60 seconds
- **Persistence:** Multiple touchpoints over months (operators are busy, not ignoring)

#### Risk: Market Consolidation

**Description:** Small operators fail or get acquired. Our addressable market shrinks. Fewer, larger operators buy enterprise tools instead.

**Likelihood:** High (prices down 72%, consolidation happening)
**Impact:** High

**Mitigation:**
- **Enterprise features:** Build for multi-location operators early
- **White-label:** Allow chains to brand GLASS for their internal use
- **Data value:** Even large operators need competitive intelligence
- **Expand markets:** Plan expansion to other states (CT, RI, NY) once MA proven

#### Risk: Price Stabilization

**Description:** If prices stop dropping and stabilize, the urgency for pricing intelligence decreases.

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- **Expand value proposition:** Threat Radar and Cue are not price-dependent
- **Product expansion:** Inventory optimization, demand forecasting, compliance tools
- **International expansion:** Other states will have similar dynamics

### 6.4 Competitive Risks

#### Risk: Incumbent Response

**Description:** Dutchie or Leafly add competitive intelligence features. They have more resources and existing relationships.

**Likelihood:** Medium
**Impact:** High

**Mitigation:**
- **Speed:** Move fast, build network effects before they react
- **Neutrality:** Position as neutral platform (Dutchie is conflicted, cannot truly be neutral)
- **Depth:** Go deeper on MA-specific features than a national platform would
- **Integration:** Lock in with Cue, Delivered, AC partnerships
- **Community:** Build operator community that would be hard for incumbents to replicate

#### Risk: New Entrant

**Description:** Another startup sees the opportunity and copies GLASS.

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- **First-mover advantage:** Establish brand recognition fast
- **Data moat:** Every day of scraping is data a competitor does not have
- **Relationships:** Personal relationships with operators built over time
- **Spokes:** Cue, Delivered, AC give us distribution channels entrants lack

### 6.5 Financial Risks

#### Risk: Capital Runway

**Description:** Burn rate exceeds projections. 18-month break-even stretches to 30. Running out of cash.

**Likelihood:** Medium
**Impact:** Business failure

**Mitigation:**
- **Lean team:** Only hire when necessary
- **Revenue-first:** Prioritize revenue-generating spokes (Cue) over pure growth
- **Roviq funding:** GLASS can be funded from Roviq agency profits initially
- **Clear milestones:** Define fundraising triggers at 20, 50, 100 operators
- **Cost discipline:** Review all expenses monthly

#### Risk: Spoke Revenue Delay

**Description:** Cue brands take longer to acquire than planned. Delivered integration is delayed. Revenue projections miss.

**Likelihood:** Medium
**Impact:** High

**Mitigation:**
- **Diversified revenue:** 4 spoke channels, not dependent on one
- **Core premium:** Hedge with paid tier conversion
- **Agency service:** Roviq services keep lights on regardless
- **Conservative projections:** Built buffer into financial model

---

## 7. Success Metrics and KPIs

### 7.1 North Star Metric

**Daily Active Operators (DAO)**

We measure success by how many operators check GLASS daily. This shows habit formation and genuine value delivery.

Targets:
- Month 3: 10 DAO
- Month 6: 25 DAO
- Month 12: 50 DAO
- Month 24: 100 DAO

### 7.2 Core Metrics Dashboard

| Metric | Definition | Target |
|--------|------------|--------|
| Operators Signed Up | Total registered accounts | 50 by Month 6 |
| Daily Active Operators | Logged in past 24 hours | 50% of base by Month 6 |
| Weekly Active Operators | Logged in past 7 days | 70% of base by Month 6 |
| Price Watches Set | Total product/category watches | 10 per operator by Month 6 |
| Recommendation Adoption | % of Margin Engine recs applied | 30% by Month 6 |
| Threat Alerts Acknowledged | % of alerts opened | 60% by Month 6 |
| Net Promoter Score | Operator satisfaction | 50+ by Month 6 |

### 7.3 Spoke Metrics

**Cue:**
- Brands signed: 5 by Month 6, 20 by Month 12
- Active spiffs: 20 by Month 6
- Budtenders enrolled: 100 by Month 6, 500 by Month 12
- Payouts processed: $10K by Month 6

**Delivered:**
- Operators enabled: 5 by Month 6
- Weekly delivery orders: 250 by Month 6
- GMV flowing through: $21K/week by Month 6

**AC Toll:**
- Operators ordering: 5 by Month 6
- Units processed: 30K by Month 6

### 7.4 Financial Metrics

| Metric | Month 6 | Month 12 | Month 24 |
|--------|---------|----------|----------|
| Monthly Recurring Revenue | $5,000 | $15,000 | $40,000 |
| Annual Run Rate | $60,000 | $180,000 | $480,000 |
| Burn Rate | $31,000 | $35,000 | $40,000 |
| Cash Position | $150,000 | $120,000 | $200,000* |

*Assuming successful funding round at Month 18

---

## 8. Implementation Checklist

### Immediate (This Week)
- [ ] Finalize team structure and roles
- [ ] Set up AWS infrastructure
- [ ] Begin scraping development
- [ ] Draft founder agreements and equity split
- [ ] Open business bank account

### Month 1
- [ ] Scraper running for top 20 dispensaries
- [ ] Mobile app wireframes complete
- [ ] Database schema finalized
- [ ] First 5 warm operator commitments
- [ ] Newsletter landing page live
- [ ] Legal review of scraping approach

### Month 2
- [ ] Alpha app with real data
- [ ] 5 operators using daily
- [ ] CCC pipeline development started
- [ ] First brand conversations for Cue
- [ ] Pricing strategy locked

### Month 3
- [ ] 20 operators in seed cohort
- [ ] Threat Radar functional
- [ ] Margin Engine v1 deployed
- [ ] Newsletter launched (500 subs)
- [ ] First Cue pilot with brand

### Month 4-6
- [ ] 50 operators on platform
- [ ] 3 Cue brands paying
- [ ] Delivered integration live
- [ ] Break-even on unit economics
- [ ] Series A conversations begin

---

## Conclusion

GLASS is the operating system Massachusetts cannabis operators need. Not because it is another tool, but because it is THE hub. Everything connects to it. Everything gets better because of it.

The market is in crisis. Prices have collapsed. Margins are gone. Operators are desperate for any edge. GLASS gives them that edge. Free intelligence on competitors. Alerts on threats. AI recommendations on pricing. A direct line to more revenue through Cue, Delivered, and AC.

We build this now because the window is open. Dutchie is bloated and conflicted. Leafly is consumer-first and dying. No one is building operator-first intelligence.

The flywheel starts with 20 operators. It compounds from there. More operators. Better data. Smarter AI. More value. More operators.

We are not building a feature. We are building infrastructure. The nervous system of Massachusetts cannabis.

The time to build is now.

---

*Document Version 1.0*
*Prepared by Roviq for internal planning*
*February 2026*
