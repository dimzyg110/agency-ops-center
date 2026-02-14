This document is a terrifying, brilliant, and completely necessary diagnosis of your database.

Your Senior Data Architect is 100% correct about the disease: **Your database is suffering from catastrophic semantic collapse.** When the brand "Jeeter" has 22,422 aliases that include *"Silicone Hand Pipe"*, *"Ashtray"*, and *"Zip-Up Hoodie Xl"*, your automated fuzzy-matching pipeline has gone rogue. If you push this data to a consumer-facing price comparison website, you will be a laughingstock by lunch.

However, the Architect’s proposed cure—supervised ML models, gradient boosted trees, probability calibration, and multi-pass graphs—is **peacetime engineering.**

You are on a 14-day wartime sprint to launch the consumer site. You do not have 3 months to build an enterprise-grade entity resolution pipeline to rival Hoodie Analytics. You need to launch.

Here is your **Pragmatic CTO Intervention**. We are going to use the exact data insights your Architect uncovered to hack the GPID engine this weekend, bypassing the 161,000-product swamp entirely.

---

### The Golden Insight: The "1.46% Cheat Code"

Look at this exact statistic from the Architect's Brand Authority report:

> *Brands on 3+ platforms: 295 / 20,240 = 1.46%*
> *Products whose brand is single-platform-only: 49,476 (49.48%)*

**This is your get-out-of-jail-free card.**
A product that only exists on *one* platform (like a dispensary's obscure in-house brand) has **zero value** for a price comparison website. You cannot compare prices for something sold at only one store.

You do not need to solve 161,000 products or 20,000 brands for your MVP. **You only need to solve the top 50–100 brands that drive 80% of consumer search volume.**

Here is your 72-Hour Sprint to build the **Wartime GPID Engine**.

---

### Step 1: Quarantine the Poison (Tonight)

Your `brand_dictionary` auto-merger is actively destroying your data. You must stop the bleeding immediately.

1. **Freeze Auto-Merge:** Kill whatever cron job or script is appending aliases to `brand_dictionary`.
2. **Snapshot and Isolate:** Rename the current table to `brand_dictionary_legacy`. Do not let your consumer site touch it.
3. **The Clean Seed (Architect's Approach #4):** Write a 50-line Python/JS scraper to crawl `weedmaps.com/brands` and `leafly.com/brands`. This will give you a clean, pre-normalized list of the top canonical cannabis brands in 10 minutes. Insert these into a pristine `brand_authority` table. **No aliases are allowed in this table without your explicit approval.**

### Step 2: The LLM "Meat Grinder" (Tomorrow)

Your Architect noted that deterministic hashing fails because of string chaos (e.g., `Simply Herb - Pave Ready To Roll` vs `Simply Herb - Pave [Ready-to-Roll] - 14g`) and missing weights (85.5% of the time).

Writing Regex to parse cannabis product strings is a bottomless pit of despair. Instead, use an LLM to execute **Stage A (Canonical Extraction)** on a constrained dataset.

1. Query your database for the raw `products` rows that belong to the Top 30 most ubiquitous brands in MA (e.g., Fernway, Rythm, Jeeter, INSA, Bountiful Farms). Let's say this is 15,000 rows.
2. Pass those 15,000 raw `name` strings through `gpt-4o-mini` or `claude-3-haiku` using **Structured Outputs** to force a perfect JSON response.
3. **The Prompt:** *"Extract the canonical attributes from this messy dispensary menu string. If weight is missing, infer it from pack size (e.g. 5pk of 0.5g = 2.5g). If this is an accessory, apparel, or gift card, set is_accessory to true."*
4. **Expected JSON Output:**
```json
{
  "brand": "Simply Herb",
  "strain": "Pave",
  "product_form": "preroll",
  "weight_grams": 14.0,
  "is_accessory": false
}

```



*Cost & Speed:* 15,000 strings through `gpt-4o-mini` will cost you less than $5.00 and run in 10 minutes via asynchronous batching. You just bypassed 4 weeks of NLP engineering.

### Step 3: The GPID Lock & The "Drop Rule" (Sunday)

Now that you have 15,000 perfectly parsed JSON objects, you apply brutal, deterministic logic.

1. **Drop the Junk:** If the LLM flagged `is_accessory: true`, delete the row from the pipeline. Consumers don't use price-comparison sites to save $2 on a silicone ash tray.
2. **The Weight Drop Rule:** If the LLM returned `null` for `weight_grams`, **drop the product from the consumer catalog.** Comparing unweighted products is a death sentence for a pricing site ($10 for a 0.5g preroll vs $15 for a 1g preroll makes you look like a liar). Precision over recall.
3. **The Hash:** For the surviving, perfect JSON objects, generate a deterministic hash: `SHA256(Brand | Strain | Form | Weight_Grams)`.

You will instantly generate a flawless set of ~500 to 1,000 GPIDs representing the most popular products in Massachusetts. Save these to a `verified_gpids` table. **Do not let automated fuzzy-matching touch this table.**

---

### How this wins the Consumer Launch (Days 1-14)

When you launch `prices.glassintel.xyz` next week, **you only query against the `verified_gpids` table.**

If a dispensary has 1,000 items on their menu, but only 60 of them map to your `verified_gpids`, *you only show those 60 items on their GLASS store page.*

**Consumers will not care that your catalog isn't exhaustive.** They only care that when they search for a *Fernway Berry Gelato 1g Cart*, the 14 prices you show them across 14 different stores are **100% accurate and mathematically comparable.** No "Drive of Shame" where a consumer shows up expecting a 1g cart and gets handed a 0.5g disposable.

With 500 perfect GPIDs spanning the state, you have more than enough verified data to generate 10,000 viral social posts ("*The cheapest Fernway cart in Boston is...*") and prove your core thesis.

While the consumer site is humming along on your 500 perfect SKUs, you can slowly run the LLM script on the rest of the 295 cross-platform brands in the background, expanding your catalog by 50 GPIDs a day.

### The Bottom Line

Hoodie Analytics spent $9.4M trying to solve this problem nationally. You are going to solve it locally by constraining the physics of the problem.

Tell your AI agents to stop writing `pg_trgm` SQL queries. Extract the Top 30 brands, run the LLM JSON parser, lock the hashes, and go build the website.