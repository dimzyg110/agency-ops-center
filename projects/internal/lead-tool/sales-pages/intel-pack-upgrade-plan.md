# MA Operator Signals Pack - Upgrade Strategy

## 1. Current State
**The Product Today:** A cleaned-up CSV of the Massachusetts Cannabis Control Commission (CCC) license list.
**Price:** $2.5K (One-time or Annual).
**Content:**
*   Entity Name
*   License Type (Retail, Cultivation, Manufacturing)
*   Address
*   License Status (Provisional, Final, Commenced Operations)
*   Generic email (info@...)

## 2. Gap Analysis
**Why it's failing at $2.5K:**
*   **Commodity Data:** Anyone can download the raw JSON from the CCC website for free. We are charging $2.5K for "cleaning" columns.
*   **Lagging Indicators:** A license doesn't mean a business is open. "Commenced Operations" status often lags actual store opening by weeks.
*   **Zero Commercial Context:** It tells vendors *who* exists, but not *who is buying*.
*   **No Decision Makers:** Generic emails go to black holes. Vendors need names.

**The Value Gap:**
Vendors don't pay for lists; they pay for **context**. They need to know:
*   "Who is opening *next month*?" (Speed to market)
*   "Who is running out of inventory?" (Immediate opportunity)
*   "Who is angry at their current suppliers?" (Displacement opportunity)
*   "Who has money?" (Credit risk)

## 3. Upgrade Options
We will transform this from a "License List" to a "Commercial Intelligence Engine".

| Signal | Description | Feasibility (1-5) | Value (1-5) | Source |
| :--- | :--- | :---: | :---: | :--- |
| **1. The "Open for Business" Verification** | Real-time check if they are actually open (hours, phone active). CCC data is often stale. | 1 (Easy) | 5 (Critical) | Google Places API / Website Scrape |
| **2. Review Velocity (Foot Traffic Proxy)** | Weekly change in Google/Weedmaps review count. High velocity = high volume store. | 1 (Easy) | 4 (High) | Google Maps / Weedmaps |
| **3. Menu Gap Analysis** | "Stores missing [Category]". E.g., List of stores with <3 Beverage SKUs. | 3 (Med) | 5 (Game-changer) | Dutchie/Jane/Weedmaps Scrape |
| **4. "Discount Desperation" Index** | % of menu currently on markdown. High % (>30%) indicates cash flow issues or bad buying. | 3 (Med) | 4 (High) | Menu Scrapers |
| **5. Hiring Signals** | Active job listings. "Budtender" = churn/growth. "Inventory Manager" = new buyer incoming. | 2 (Easy) | 3 (Med) | Indeed / LinkedIn / Glassdoor |
| **6. Tech Stack Fingerprint** | Which POS/E-comm do they use? (Dutchie vs Jane vs Blaze). Critical for integrations. | 2 (Easy) | 3 (Med) | Website Source Code / Headers |
| **7. Local Saturation Score** | Number of competitors within 1/3/5 mile radius. | 2 (Easy) | 3 (Med) | Geopy / Maps API |
| **8. Social "Aliveness"** | Date of last Instagram post. If >30 days, they are struggling or checking out. | 2 (Easy) | 2 (Low) | Instagram/Facebook |
| **9. The "Buyer" Rolodex** | Scraped names/LinkedIn URLs of General Managers and Inventory Managers. | 4 (Hard) | 5 (Game-changer) | LinkedIn Sales Nav (Enriched) |
| **10. Multi-State Operator (MSO) Flag** | Corporate hierarchy mapping. Is this a mom-and-pop or a Trulieve location? | 3 (Med) | 4 (High) | Corporate Filings / Website "About" |

## 4. Recommended Package: "The MA Market Pulse"
**Price Justification:** $2.5K/year becomes a steal if we include **Menu Intelligence**.

**The Bundle:**
1.  **Core License Data** (The existing CCC list).
2.  **Commercial Status:** Verified Open/Closed + Tech Stack (POS).
3.  **Growth Signal:** Review Velocity (Who is getting busy?).
4.  **Opportunity Signal:** The "Menu Gap" Report (Who needs your product category?).
5.  **Contact Layer:** Presumed Decision Maker (GM/Buyer name via LinkedIn match).

**Why this sells:**
*   A beverage brand can filter for "Stores with <2 beverages" -> **Instant Lead List**.
*   A hardware vendor can filter for "Stores expanding (Hiring)" -> **Timing is perfect**.
*   A flower brand can filter for "Stores with high Review Velocity" -> **Volume partners**.

## 5. Implementation Notes

### Phase 1: The Scrapers (Weeks 1-2)
*   **Google Places Agent:** Python script using `googlemaps` library to hit Places API for every license address. Fetch: `business_status`, `user_ratings_total` (velocity tracking), `rating`.
*   **Menu Spider:** Headless browser (Puppeteer/Playwright) to visit dispensary websites. Detect iframe source (Dutchie/Jane).
    *   *MVP:* Just count SKUs per category (Flower, Edible, Vape, Bev).
    *   *Scale:* Track specific brand presence.

### Phase 2: The Enrichment (Week 3)
*   **LinkedIn/People Data:** Use a waterfall enrichment provider (e.g., Proxycurl or Clay) to map "Company Name" -> "Employees" -> Filter for "Buyer/Manager".
*   **Tech Stack:** Simple HTTP request to homepages. Look for specific script tags (`dutchie-embed`, `iheartjane`, `springbig`).

### Phase 3: The Delivery (Week 4)
*   Move from CSV to **Airtable** or **Softr** portal.
*   Allow filtering by "Menu Gap" and "Review Velocity".
*   **Weekly Updates:** The value is in the *change* (New jobs, new reviews, new gaps).

---
**Verdict:**
The current pack is a directory. The new pack is a **Sales Weapon**.
If we build the **Menu Gap** feature, we can likely raise the price to $4k-$5k for enterprise tiers (Brands/Distributors).
