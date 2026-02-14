# GLASS GTM: The Marketplace Trap (Tom Sawyer Strategy)

_Source: External strategic advisor. Saved Feb 14, 2026._
_This is the definitive go-to-market playbook. Every phase weaponizes greed, fear, or vanity._

---

This is exactly how you turn a 500-SKU wedge into a national data monopoly.

You are no longer launching a software product. You are launching a **Marketplace Trap**. Every step of this Go-To-Market (GTM) plan uses the greed, fear, or vanity of one market participant to force the compliance of another.

In platform economics, we call this the "Tom Sawyer Strategy": You are going to trick the entire cannabis industry into painting your fence for free.

Here is your ruthless, day-by-day playbook to execute this starting Monday morning.

---

### PHASE 1: The Consumer Spark (Days 1–14)

**Goal:** Generate 10,000 local MA site visitors. Prove to the ecosystem that GLASS moves markets.
**The Rule:** Do not pitch a single B2B operator. Only talk to consumers.

* **Day 1 (The Launch):** Deploy `prices.glassintel.xyz`. It must be dead simple: Search bar, location filter, results.
* **The Trap:** It **ONLY** displays items that match your 500 verified GPIDs. If a dispensary has 800 items on their Weedmaps menu but only 30 map to your Top 500, *their GLASS page only shows those 30 items.*
* **The Trust Moat:** Add a massive banner: *"We only track Verified Products to prevent bait-and-switch pricing. All prices are Post-Tax (Out the Door)."*

* **Day 2 (The Reddit Drop):** Go to `r/bostontrees` (32K members). Do not post a corporate "Try my app" link. Post a data exposé: *"I scraped the 500 most popular products in MA. The price gouging is insane. [Store A] is charging $20 more for a Fernway cart than [Store B] two miles away. All prices post-tax."*
* **Days 3–14 (The Outrage Loop):** Turn your AI agents on. Generate 3-5 "Price Shock" image cards per day.
  * *Format:* Split screen. Top: "Dispensary A: $60." Bottom: "Dispensary B: $40." Center: "Same Product. 2 Miles Apart."
  * *The Hack:* **@Tag the exact dispensaries on X and Instagram.** Consumers will share it. Dispensary owners will panic.

* **The KPI:** 10,000 unique visitors. 300 price alerts set up by consumers.

---

### PHASE 2: The Retailer Trap (Days 15–45)

**Goal:** Crowdsource your data engineering. Trick dispensaries into building your 100,000-product catalog for free.
**The Weapon:** FOMO on consumer traffic.

* **Day 15 (The Realization):** Dispensary owners see the social tags. They see referral traffic from `glassintel.xyz` in their analytics. They search for their store on your site.
* **Day 16 (The Trap Springs):** The owner sees their GLASS page. They realize they are losing the "Cheapest Near Me" ranking because their cheap inventory isn't showing up. A massive banner reads: *"GLASS only displays Verified GPID products. We found 755 unmatched items on your menu. Claim your page (Free) to map them to the Consumer Catalog."*
* **Days 17–45 (The Labor Force):** The dispensary owner claims the page. You give them a dead-simple dashboard:
  * *Left side:* Their messy POS string (`"B. Dream 1/8"`).
  * *Right side:* A search box to select the official GLASS GPID.
  * *The Incentive:* The second they map it, it goes live on the consumer site, eligible to win local price searches.

* **The Monetization (Path A):** Once inside the portal mapping their data, prompt them: *"Want real-time SMS alerts when your neighbors drop their prices? Upgrade to Premium ($199/mo)."*
* **The KPI:** 50 dispensaries claimed. 20,000 messy strings manually mapped to GPIDs by dispensary staff. **You just got thousands of hours of data labeling for $0.**

---

### PHASE 3: The Brand Squeeze (Days 46–90)

**Goal:** Acquire the "Source of Truth" catalogs and your first high-ticket MRR.
**The Weapon:** Brand Vanity and MAP Violations.

* **Day 46 (The Upstream Pivot):** Your catalog is growing fast, but it's reacting to retail menus. You need the master data. Export a report for the Top 20 MA Brands (e.g., INSA, Bountiful Farms, Rythm).
* **Days 47–60 (The "FedEx Nuke"):** FedEx a physical, 3-page dossier to the VP of Sales at these brands.
  * *"Dispensaries are misspelling your product names, meaning you aren't showing up when our 50,000 users search for your brand. Also, here are 12 stores selling your product below MAP (Minimum Advertised Price)."*

* **Days 61–90 (The Master Catalog):** When the VP calls you furious at their sales reps, you sell them a **$3,500 Quarterly Data Audit**. Then you tell them: *"Claim your free Brand Portal and upload your master product spreadsheet (High-Res Image, Exact Name, Weight, THC%, Terpenes)."*
  * **This is the holy grail.** You now mint official GPIDs from the manufacturer's master list. You no longer have to guess what products exist.

* **The Monetization (Path B):** Charge Brands $1,000–$3,500/month for "Brand Pro." This gives them the MAP violation alerts, out-of-stock alerts, and "Sponsored Featured Placement" on the consumer site.
* **The KPI:** 10 Brands upload their master catalogs. $20,000+ in early cash collected.

---

### PHASE 4: The ML Flywheel (Months 4–6)

**Goal:** Drop the marginal cost of matching to zero. Scale instantly to new states.
**The Weapon:** The Human-Verified Training Dataset.

* **Month 4:** You now have 50,000+ examples of messy strings mapped to pristine GPIDs (thanks to the greedy dispensary staff and vain brands in Phases 2 & 3).
* **Month 5:** Use this pristine, human-labeled dataset to train a lightweight, proprietary classification model (using `fastText` or `pgvector`). Turn off the expensive OpenAI API. Your proprietary model can now look at garbage cannabis nomenclature and predict the correct GPID with 99% accuracy for fractions of a penny.
* **Month 6 (State Expansion):** Point your scrapers at Connecticut, Rhode Island, and New York. Because East Coast cannabis nomenclature is similar, your ML model instantly maps 85% of their menus to your GPIDs on Day 1. Launch consumer sites in 3 new states in one weekend with zero manual effort.
* **The KPI:** >90% automated match rate without LLM APIs. Multi-state consumer presence.

---

### PHASE 5: The POS Tollbooth (Months 6–12)

**Goal:** Become the un-rippable infrastructure of the cannabis industry.
**The Weapon:** B2B Efficiency.

* **Month 7:** Dispensary intake managers spend hours every week manually typing new products into Dutchie, Jane, and Treez. It is their most hated task, resulting in typos and broken search.
* **Months 8–10 (The API Pitch):** Approach the POS providers.
  * *"Integrate the free GLASS GPID API. When a dispensary receives a shipment, they type the first 4 letters into Dutchie. Our API auto-completes the canonical name, exact weight, category, and pulls the high-res image directly from the Brand's master catalog."*

* **Months 11–12 (The Monopoly):** Dutchie integrates your API because it saves their customers millions of hours of labor.

### The Endgame

The second a POS system uses your API for inventory intake, **you stop needing to scrape the internet.** The product is mapped to a GPID at the exact moment it enters the legal retail supply chain.

You are now the "Clearbit/UPC Code of Cannabis." Regulators, Lenders, MSOs, and Brands all pay you $50,000/year to access the canonical data feed.

Hoodie Analytics' board will ask their CEO why they have zero market share in the Northeast. They will realize it costs too much to fight you because you own the ground-truth data layer. They will have to buy you for $30M–$50M, or you will raise a Series A and crush them nationally.

---

### Your Monday Morning Checklist (Execute Immediately)

1. **Extract the 500:** Run the SQL query to isolate the top 500 most ubiquitous SKUs in your database.
2. **LLM the 500:** Run them through structured JSON output to normalize the Brand, Strain, Weight, and Category. Drop anything missing a weight.
3. **Lock the Hashes:** Generate the `GPID-XXXX` hashes for those 500 perfect items. Insert them into `verified_gpids`.
4. **Deploy the Site:** Launch `prices.glassintel.xyz`. The search bar and category pages *only* query against the 500 `verified_gpids`.
5. **Generate the Ammo:** Have your AI agent spit out 10 "Price Shock" graphics comparing prices for those exact 500 SKUs across MA dispensaries.

You have the blueprint. You have the data. Light the spark.
