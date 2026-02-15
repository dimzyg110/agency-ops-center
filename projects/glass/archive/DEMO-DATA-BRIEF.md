# GLASS — Full Logged-In Experience Data Brief

_For reviewer agents: This is what a logged-in operator sees._

---

## Landing Page (Public — glassintel.xyz)

**Hero:** "See what your competitors charge"
**Subtext:** "GLASS tracks every price change across Massachusetts dispensaries. Know your market position. React faster. Protect your margins."
**CTA:** Work email → GET STARTED FREE
**Sections scrolling down:**
1. Price Wire — "Every price. Every dispensary. Updated daily." Track 100,000+ products across 490+ dispensaries. Price change alerts within 24 hours.
2. Threat Radar — "Know when the market changes before your customers do." New license application detection, price undercut alerts, proximity-based threat scoring.
3. Morning Brief (COMING SOON) — "Your market at 6 AM. No noise."
4. Cue (COMING SOON) — "Train, Motivate, and Reward Your Budtenders." Brand-funded incentives, $200-500/month for budtenders.
5. Product Cards — GLASS (LIVE), Virtual Budtender (LIVE), Cue (COMING SOON)

## Market Page (Public — glassintel.xyz/market)

**Hero:** "Market intelligence that operators can trust."
**Stats:** 301 operators tracked, 100.8K products, 117K price observations
**Killer Feature section — CCC × GLASS:**
- Table comparing CCC transfer prices vs GLASS shelf prices: Concentrate ($17.35 CCC vs $41.98 shelf), Edible ($3.55 vs $17.89), Flower ($4.04 vs $10.08, +149.5%), Vape ($26.64 vs $35.48, +33.2%)
- "CCC reports average transfer prices between licensees. GLASS tracks retail shelf prices across 490+ MA dispensary menus."
**Price Index:** Massachusetts average prices by category
**CTA:** "Want these insights for YOUR store? Get personalized competitor tracking, alerts, and daily recommendations. START FREE →"

---

## Logged-In Dashboard

### Sidebar Navigation:
- Morning Brief (main dashboard)
- Price Wire
- Threat Radar
- Competitors
- Recommendations
- Alerts
- — divider —
- Virtual Budtender (link out)
- Cue (coming soon)

### Morning Brief (Dashboard Home)

Shows a Report Card for YOUR store with:

**Cannabis Healing (example operator) Report Card:**

| Category | Your Avg | Market Avg | Diff | Status |
|----------|----------|------------|------|--------|
| Flower | $31.99 | $35.30 | -9.4% | 🟡 Priced below market — room to earn more |
| Preroll | $15.55 | $18.57 | -16.3% | 🔴 Leaving money on the table |
| Vape | $48.52 | $35.45 | +36.9% | 🟡 Premium position — monitor velocity |
| Edible | $22.90 | $17.89 | +28.0% | 🟡 Premium position — monitor velocity |
| Concentrate | $45.00 | $41.98 | +7.2% | 🟢 Healthy positioning |

**Pricing section (auto-expanded):**
- Status: Shows color-coded status per category
- Suggestions now say things like "Premium position — your edibles command a premium. Monitor sales velocity" and "Room to earn more — your prerolls are 16.3% below market. You could be earning an extra $X/week"
- **Estimated opportunity:** Green callout "Potential extra margin from underpriced categories: $XXX/week"

**Actions section:**
- Primary (high priority): "Your prerolls are priced 16.3% below market average. Raising to market rate could add ~$X/week in margin."
- Secondary (medium): "Your vapes are 36.9% above market. Monitor velocity — if sales are strong, hold your premium."

**Other sections:**
- Competition: Shows count of nearby competitors, nearest competitor, new threats
- Assortment: Your product count vs market average, missing categories
- Market Position: Percentile ranking

### Price Wire Page
- Searchable table of ALL 100,849 products with prices
- Filter by category, brand, operator
- Real competitor prices from 490+ stores
- "Watch" button to track specific products/competitors

### Threat Radar Page
Shows 6 active threats (seed data):
1. **New Adult-Use Retail Applicant — Kendall Square** (HIGH) — Host community agreement filed
2. **Worcester Cluster** (CRITICAL) — Three stores dropped eighth pricing below $32
3. **MA Cannabis Control Commission** (MEDIUM) — Tighter packaging disclosure enforcement
4. **Berkshire Distribution Lane** (HIGH) — Weather delays reducing concentrate shipments
5. **Boston Metro Compliance Sweep** (MEDIUM) — Increased spot checks on promo claims
6. **Lowell/North Shore Value Segment** (LOW) — Sustained bundle discounts pressuring margins

### Recommendations Page
Shows 6 active recommendations (seed data):
- 2-pack preroll bundle: $19 → $17 (reduce to increase basket attach)
- 1g vape cart: $72 → $68 (above local tolerance band)
- Gummy: $34 → $31 (elasticity high, align with $30-32 band)
- Rosin: $78 → $74 (slower turns, slight adjustment)
- Quarter-ounce: $88 → $81 (over-indexed vs Worcester)
- Competitor median: $46 → $42 (controlled reduction)

**⚠️ NOTE:** These recommendations still use the OLD "lower your price" framing in seed data. The Report Card API was fixed but the recommendations table seeds weren't updated yet. This is a P1 fix.

---

## Data Assets Available (511K+ rows)

### What No One Else Has:

1. **147K State Lab Tests** — THC/THCA from actual CCC testing. Can cross-reference with menu claims.
   - Example: Product claims 30% THC on menu, lab test shows 22% total THC → ❌ Inflated
   - Product categories: Buds (129K), Shake/Trim (17K), Plants (962), Concentrate (221)
   - 7 testing labs, data from April 2021–March 2024

2. **67K Facility Sales Records** — ACTUAL daily revenue by product category, 2018-2025
   - Shows what's SELLING not just what's priced
   - Delivery vs adult-use breakdowns
   - Example: Dec 21, 2025 — Concentrate (Each): 5,747 units, $205,919.67

3. **71 Months of Price Collapse Data:**
   - Jan 2020: $14.68/gram → Nov 2025: $4.01/gram (-73%)
   - Every month declining: Nov 2025 was -12% YoY, -1.7% MoM
   - This is the industry's biggest story and GLASS has the timeline

4. **772 Licensed Operators with Contact Info:**
   - Business emails, phone numbers, license types, cities
   - Cultivators, retailers, manufacturers, microbusinesses
   - This IS the outreach list

5. **Nearby Competitor Intelligence (CH example — East Boston area):**
   - 15+ dispensaries within the area, 390-483 products each
   - Price range: $19.73 avg (quincy-cannabis) to $35.41 avg (native-sun)
   - CH at $31.99 avg flower sits in the upper-middle

---

## What Operators Care About (Randy's Rule)

**"People want to make more money, save money, or get more customers."**

- Never tell them to lower prices
- Frame everything as opportunity (money on table, premium validation)
- Show the dollar impact, not percentages
- They want to know: Am I leaving money on the table? Is someone about to steal my customers? What should I stock?
