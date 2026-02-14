# GPID Matching Deep Dive (GLASS)

**Prepared for:** Gemini Pro Deep Think algorithm design  
**Author role:** Senior Data Architect  
**Generated:** 2026-02-14 UTC  
**Database:** `railway` PostgreSQL (`public` schema)  
**Query convention used:** `SET search_path TO public;`

---

## Executive Summary

GLASS aggregates cannabis menu/product pricing across Massachusetts operators from four primary menu ecosystems: **Dutchie, Jane, Leafly, and Weedmaps**. The platform-level product records are not standardized, and each platform can represent the same commercial SKU using different product names, brands, categories, weights, and metadata conventions.

The core matching objective is to assign a **cross-platform identity** (GPID-equivalent concept) to products that are actually the same real-world item. This enables apples-to-apples pricing, assortment intelligence, share-of-shelf analysis, and robust competitive benchmarking.

### Current measurable state (live DB snapshot)

- Distinct products across 4 platforms: **161,653**
- Total product matches in `product_matches`: **3,612**
  - exact: **1,751**
  - fuzzy_name: **1,861**
- Candidate pairs in `gpid_candidates`: **7,438**
- Candidate pairs still unmatched: **3,826 (51.4%)**
- Candidate pairs with missing/zero weight on at least one side: **85.5%**
- Human judgments in `gpid_verdicts`:
  - correct: **1,157**
  - wrong: **2,024**
  - unsure: **2,963**

This is enough signal to build a materially better system, but not enough to rely on single-stage deterministic logic. A robust algorithm should be **multi-pass, evidence-weighted, platform-aware, and verdict-trained**.

---

## 1) THE PROBLEM

### 1.1 What GLASS does

GLASS continuously scrapes and ingests dispensary menu data in Massachusetts from:

- **Dutchie**
- **Jane (IHeartJane)**
- **Leafly**
- **Weedmaps**

For each listing, GLASS stores product attributes in `products` and observed price points in `prices`, tied to source endpoints in `sources` and retailer entities in `operators`.

Because these platforms are retail publishing systems (not canonical product exchange systems), each operator + platform feed behaves like a custom schema with heavy lexical drift.

### 1.2 Why cross-platform matching matters

Without cross-platform matching, every record remains a local string island. That creates structural analytical failures:

1. **Price comparison failure:** one real SKU appears as many strings, fragmenting distributions.
2. **False brand fragmentation:** alias noise inflates apparent brand count.
3. **Weak demand signals:** true product-level trends are hidden by naming drift.
4. **Recommendation degradation:** alternatives and substitutions require identity certainty.
5. **Competitive blind spots:** cross-retailer market intelligence requires shared identifiers.

### 1.3 What a GPID is and why it is hard

In this environment, a GPID is a canonical identity for a real commercial product variant across platforms and operators.

Hardness drivers:

- **Names are overloaded fields**: product, weight, pack size, category, potency, promo copy, and brand may all be mixed into title.
- **Category drift**: same item may be tagged edible/flower, vape/concentrate, etc.
- **Weight sparsity**: explicit weight often missing; when present may conflict with title.
- **Brand instability**: trademark/case/punctuation variation; sometimes product descriptors are injected as brand.
- **No universal external SKU** spanning all four platforms.

Result: pure deterministic matching is brittle; unconstrained fuzzy matching increases false positives.

---

## 2) THE DATA (REAL EXAMPLES)

### 2.1 Platform footprint (current)

```sql
SELECT s.source_type, count(DISTINCT p.id) as distinct_products, count(*) as price_rows, count(DISTINCT pr.operator_id) operators
FROM products p
JOIN prices pr ON pr.product_id=p.id
JOIN sources s ON s.id=pr.source_id
WHERE s.source_type IN ('jane','leafly','weedmaps','dutchie')
GROUP BY s.source_type
ORDER BY s.source_type;
```

- dutchie: 51,412 distinct products / 65,762 price rows / 200 operators
- jane: 6,273 / 11,180 / 42
- leafly: 44,730 / 59,592 / 116
- weedmaps: 59,907 / 86,706 / 208

### 2.2 Data completeness stats per platform (requested query, executed)

```sql
SELECT s.source_type,
  count(*) as total_products,
  count(NULLIF(p.brand, '')) as has_brand,
  count(CASE WHEN p.weight_grams > 0 THEN 1 END) as has_weight,
  count(p.thc_percent) as has_thc,
  count(NULLIF(p.strain_type, '')) as has_strain,
  ROUND(count(NULLIF(p.brand, ''))::numeric / count(*) * 100, 1) as brand_pct,
  ROUND(count(CASE WHEN p.weight_grams > 0 THEN 1 END)::numeric / count(*) * 100, 1) as weight_pct
FROM products p
JOIN prices pr ON pr.product_id = p.id
JOIN sources s ON pr.source_id = s.id
GROUP BY s.source_type
ORDER BY s.source_type;
```

| source_type | total_products | has_brand | has_weight | has_thc | has_strain | brand_pct | weight_pct |
|---|---:|---:|---:|---:|---:|---:|---:|
| dutchie | 65762 | 27425 | 51220 | 53238 | 62242 | 41.7 | 77.9 |
| jane | 11180 | 10697 | 8591 | 6753 | 9337 | 95.7 | 76.8 |
| leafly | 59592 | 56948 | 9753 | 43188 | 408 | 95.6 | 16.4 |
| weedmaps | 86706 | 47857 | 41480 | 42109 | 175 | 55.2 | 47.8 |

(There is also a small `menu` source_type in DB; excluded from this matching analysis scope.)

### 2.3 10 example products from each platform (real rows)

```tsv
source_type\tid\tsku\tname\tbrand\tcategory\tweight_grams\tthc_percent\tstrain_type
dutchie\t00022ad3-7b8d-484a-b59f-a2f96849cc36\tGPID-de72211efedd\tLazy River | Juicee J | Lazy River | Lazy River Hybrid TAC: 29.5% THC: 26.3%\tJuicee J\tflower\t3.500\t26.30\tHybrid
dutchie\t00029443-126a-44fc-a04a-f922c9823d63\tGPID-455657fb720a\tGummies | 20pk of 5mg* Sponsored Prickly Pear | Gummies | 20pk of 5mg* Hashables Hybrid THC: 89.4 mg\tPrickly Pear\tedible\t\t\tHybrid
dutchie\t00047d82-4340-4714-ad07-fc2d4f298627\tGPID-c8d5ee0710ec\tDisposable | 1000mg Blueberry Haze | Disposable | 1000mg PAX Sativa TAC: 90 mg THC: 85.55%\tBlueberry Haze\tvape\t1.000\t85.55\tSativa
dutchie\t00062bb2-563f-4b10-9b9e-e7dffc3cccc0\tGPID-f7fe812f6189\tRuntz Banger Preroll Runtz Banger Preroll Bountiful Farms Hybrid THC: 24.71%\t\tpreroll\t1.000\t24.71\tHybrid
dutchie\t00083aca-9f56-44f9-a055-9336ab2ca45d\tGPID-dd681b56a2d8\tKo Ko | Preroll - 1g Highlands | Ko Ko | Preroll - 1g Highlands Hybrid TAC: 28.12% THC: 23.74% 1g Prerolls - 6 for 50\tHighlands\tpreroll\t1.000\t23.74\tHybrid
dutchie\t000919ae-3acf-4891-bfd3-503b055a8665\tGPID-1522e086773c\tBreathe Free - Papayamosa - Flower - 14g Breathe Free - Papayamosa - Flower - 14g Breathe Free Hybrid THC: 22.43%\t\tflower\t14.000\t22.43\tHybrid
dutchie\t000aa858-727e-49b6-8fec-4af5a56dd82b\tGPID-1e8ae28dc23d\tInfused Pre-Roll - Mango Mirage Infused Pre-Roll - Mango Mirage Sesh''n Hybrid TAC: 45.69% THC: 43.81%\t\tpreroll\t1.000\t43.81\tHybrid
dutchie\t000ac230-edab-4d02-8e30-3549d2864ab7\tGPID-85b05144c45e\tPre-roll - Pink Truffle - 1g Pre-roll - Pink Truffle - 1g Botanist Hybrid THC: 24.26%\t\tpreroll\t1.000\t24.26\tHybrid
dutchie\t000aeb38-695f-4b0e-a2a5-26563dd53886\tGPID-9792c01c85bf\tPre-Roll 5pk | 0.5g each Grape Bubblegum | Pre-Roll 5pk | 0.5g each Hidden Hemlock Indica-Hybrid TAC: 22.1% THC: 20.5% Staff Pick\tGrape Bubblegum\tpreroll\t2.500\t20.50\tIndica-Hybrid
dutchie\t000c314a-fc75-41d6-8e90-34014c2e660f\tGPID-74305256820c\tHi5 Beverage Enhancer -150mg Hi5 Beverage Enhancer -150mg Hi5 Hybrid THC: 150 mg\t\tedible\t\t\tHybrid
jane\t00051365-bbb6-4fe9-8a4a-f70408533e12\tGPID-cabd1bc3145e\tMandarin Cookies [1000mg]\tCheetah\tvape\t1.000\t73.97\tsativa
jane\t00192a33-a399-42cd-a886-ea6b07cd9685\tGPID-9721068bbb43\tVery Berry [20pk] (1000mg)\tHedy\tedible\t0.000\t\thybrid
jane\t0026b229-b98b-444f-a1d3-7c1a3a00680a\tGPID-5a927489f29d\tPeanut Butter Breath Live Hash Rosin\tAmber\tconcentrate\t1.000\t86.70\tindica
jane\t0027ee62-b640-49a8-80b7-637d156db881\tGPID-b4247e631115\tGolden Hour [1000mg]\tHoliday\tvape\t0.500\t87.28\tsativa
jane\t002d0576-1932-46cc-af27-903e8a04f663\tGPID-00bc5f4564f4\tDeath Star\t\tflower\t2.000\t\thybrid
jane\t0040e7c7-869d-4c2a-ac7f-e08038a1021e\tGPID-2c304cb7ef30\tCantaloupe Dream Disposable\tDime Industries\tvape\t2.000\t95.54\tsativa
jane\t0053dcb9-c163-4156-9794-f7766709433f\tGPID-245119c75db7\tLembrule\tMello\tflower\t3.500\t0.59\thybrid
jane\t0060dac4-e55f-4423-a20a-b3d9ca6e9409\tGPID-d49d25f63951\tGround Shake - Ginger Tea\tSanctuary\tflower\t14.000\t29.24\tsativa
jane\t006e3daf-2be2-449e-8da8-4b6d644db1a9\tGPID-3aa351c45b76\tPurple Trainwreck\t\tflower\t2.000\t\tsativa
jane\t007292eb-da0f-44cb-9d0f-4f5df737d08d\tGPID-36364975389a\tGarlic Drip\tHarbor House Collective\tflower\t7.000\t25.59\thybrid
leafly\t00020d83-b119-47c6-9ae0-29302dd9fa83\tGPID-aea7281eb402\tThe Cure Company | Curelato | 3.5g\tThe Cure Company\tflower\t3.500\t21.95\t
leafly\t00046156-bdbf-4c9e-bcd4-a08c4fdc1c61\tGPID-974373563540\tCamino 2:1 Freshly Squeezed Gummies 100mg 20pk (CBG:THC)\tCamino\tedible\t\t\t
leafly\t00063cd9-093b-42f4-adce-1de7dcba0d21\tGPID-d2496ebf99f3\tBlueberry Cinnamon Streusel Cheesecake\tDouble Baked\tedible\t\t\t
leafly\t0006e6b7-12f0-4398-b51f-e84412a32479\tGPID-40cf63248d14\tNature's Heritage | Cherimoya | 3.5g\tNature's Heritage\tflower\t\t22.41\t
leafly\t000767ff-6fe1-4e98-82a9-6e630d2a48b3\tGPID-9b9e5ec7489a\tSilicone Hand Pipe 5\t\tflower\t\t\t
leafly\t00081bee-4dca-4693-92fa-04b96c7bf244\tGPID-bdc6ef6b6548\t510 | Northern Lights | 1g\tSelect Oil\tvape\t\t\t
leafly\t000c66eb-477c-4a39-bf6a-232bb9d3a7b0\tGPID-a114d55f20e0\tLemon Drop | Live Badder - 3.5 g\tDope\tconcentrate\t3.500\t0.00\t
leafly\t000d767a-e4e6-4da6-a9e5-0e1b2ade6501\tGPID-ab46ec2714e7\tBABY JEETER Orange Daiquiri Infused Pre-Roll 0.5g 5pk\tJeeter\tpreroll\t\t33.82\t
leafly\t000f27df-f4a5-437a-8e93-0bf78deb883c\tGPID-e2fdaa5c6d1f\tGood Vibes | Plus Sleep 1:1:1 | Lemon Dreams | Tincture | 300mg\tGood Vibes Edibles\tconcentrate\t\t\t
leafly\t00100001-6511-4834-90cf-6be8cadee4f7\tGPID-4a7ac098656e\tRECTANGLE SILICONE DAB STRAW AND CHILLUM KIT\tHigh Mountain Imports\tflower\t\t\t
weedmaps\t000432cf-eeaf-4036-b4cc-9e3ba3914986\tGPID-9c9f276a97d9\t.5g Governmint Oasis Pre\t\tpreroll\t\t25.80\t
weedmaps\t0004af1f-8727-45e7-a753-8a484df4ecaa\tGPID-39046d237b6a\tDank | Infused Pre-Roll | Mango\tHaze\tpreroll\t\t\t
weedmaps\t0006ff7e-f314-40bd-95a2-5ee3eaa01873\tGPID-bfbd4dbe9205\t1/8 Oz Add To Cart Flower Shire 1/8th\t\tflower\t\t\t
weedmaps\t0007536e-118b-45a0-bd37-04cafee6774e\tGPID-5003d0f8c856\tGrassroots GMO (Indica) .4g\t\tpreroll\t5.000\t33.55\t
weedmaps\t0008d88b-3917-4981-bfd7-d3d4b49246c4\tGPID-71974a7381f5\tStreet Tartz\t\tflower\t3.500\t21.95\t
weedmaps\t000b266f-4ddd-47fa-9640-b812229c551a\tGPID-09abe794adc2\tHybrid\t\tconcentrate\t1.000\t74.69\t
weedmaps\t000cd024-a5c7-4688-a58e-c2691a53801e\tGPID-686fc2ccf5c8\tGold Cannabis Leaf Earrings\tZad Jewelry\tflower\t\t\t
weedmaps\t0010007a-2fd3-42ff-b165-6989f3b436bf\tGPID-b62c87c4f80e\tBlue ZKZ (I) 1g - Jeeter Infused Preroll\t\tpreroll\t1.000\t\t
weedmaps\t00106ebc-6b39-4cf8-a71d-3924a348b182\tGPID-0826e059ad1a\tAeterna | Gelato 33\tPre Roll\tpreroll\t1.000\t26.00\t
weedmaps\t0010d9b1-2771-4b4d-a92f-7108e164f4f2\tGPID-7b62b2dfa55f\tALL-IN-ONE Fernway AIO Vape (T PRO) | 2g\tStonefruit [H]\tflower\t2.000\t\t
(40 rows)

```

### 2.4 Same real product across platforms (Jeeter family) — field-level side-by-side

```tsv
match_type\tconfidence\ta_platform\ta_id\ta_sku\ta_name\ta_brand\ta_category\ta_weight\ta_thc\tb_platform\tb_id\tb_sku\tb_name\tb_brand\tb_category\tb_weight\tb_thc
exact\t0.9\tjane\t28f9a0c1-4a1c-487e-ac9d-2cb2fa15b08f\tGPID-06d6edb165b7\tCART - 1g Blue ZKZ\tJeeter\tvape\t0.000\t81.45\tleafly\t499afcde-41c2-4e84-8967-ecf102d66e64\tGPID-f4ff69ad5e55\tCART - 1g Blue ZKZ\tJeeter\tvape\t1.000\t81.45
fuzzy_name\t0.81\tleafly\t8ac39de1-3d91-4f40-9598-82e450cabd6e\tGPID-6e5e4222b2df\tJeeter - Blue ZKZ (I) Infused Jeeter (1g)\tJeeter\tpreroll\t\t35.76\tweedmaps\tae07b86f-3554-404f-a581-c7f5679b50ae\tGPID-e19c3351e9a3\tBlue ZKZ (I) Infused Jeeter (1g) |\tJeeter\tpreroll\t1.000\t35.76
fuzzy_name\t0.81\tweedmaps\t41e92a9b-2cd6-4921-9223-97fa84b26925\tGPID-0203008f9310\tBlue ZKZ XL Infused Pre-Roll |\tJeeter\tpreroll\t2.000\t35.61\tleafly\tf3b5e0e8-3521-46a3-b43b-3dc0f054e788\tGPID-18fb580aaf31\tXL Blue ZKZ Infused Pre-Roll 2g\tJeeter\tpreroll\t\t35.61
exact\t0.8\tweedmaps\t573c369b-a40c-4b3c-b13d-e8953f5336f0\tGPID-c60eda0faaa4\tBlue ZKZ | 1g Infused\tJeeter\tpreroll\t1.000\t\tleafly\tb74c0f4b-0f80-430b-8701-90591903a24e\tGPID-d2d1a645bfaa\tBlue ZKZ Infused 2g\tJeeter\tpreroll\t\t35.61
fuzzy_name\t0.7777\tweedmaps\t0f02aa63-2dad-4a1b-9e93-ad4b809a05d6\tGPID-89d126be7ee5\tBlue ZKZ | Infused Pre-Roll | 1g | by\tJeeter\tpreroll\t1.000\t35.76\tleafly\ta59ad4ec-ed23-4dcd-8149-8ed4bd4c2952\tGPID-96f954c2f455\tBlue ZKZ | Infused Pre-Roll | 1g\tJeeter\tpreroll\t\t35.76
fuzzy_name\t0.7583\tweedmaps\t41e92a9b-2cd6-4921-9223-97fa84b26925\tGPID-0203008f9310\tBlue ZKZ XL Infused Pre-Roll |\tJeeter\tpreroll\t2.000\t35.61\tleafly\ta59ad4ec-ed23-4dcd-8149-8ed4bd4c2952\tGPID-96f954c2f455\tBlue ZKZ | Infused Pre-Roll | 1g\tJeeter\tpreroll\t\t35.76
exact\t0.75\tweedmaps\t573c369b-a40c-4b3c-b13d-e8953f5336f0\tGPID-c60eda0faaa4\tBlue ZKZ | 1g Infused\tJeeter\tpreroll\t1.000\t\tleafly\teaac1812-f76c-4b66-9cb0-55d3c174e955\tGPID-a3c911f4ea75\tBlue ZKZ Infused 2g\tJeeter\tpreroll\t2.000\t35.61
fuzzy_name\t0.7294\tweedmaps\t0f02aa63-2dad-4a1b-9e93-ad4b809a05d6\tGPID-89d126be7ee5\tBlue ZKZ | Infused Pre-Roll | 1g | by\tJeeter\tpreroll\t1.000\t35.76\tleafly\tf3b5e0e8-3521-46a3-b43b-3dc0f054e788\tGPID-18fb580aaf31\tXL Blue ZKZ Infused Pre-Roll 2g\tJeeter\tpreroll\t\t35.61
(8 rows)

```

### 2.5 Field difference patterns seen in live data

- Name token ordering differs dramatically across platforms.
- Weight may appear in title only, field only, both, or neither.
- Brand may be clean, noisy, null, or embedded in title.
- Category can conflict even when name+brand similarities are 1.0.

---

## 3) CURRENT APPROACHES

### 3a) Exact hash matching (`makeSKU`)

#### How it works

Exact key generation conceptually uses:

`SHA256(normalized(brand|name|weight|category))`

with compact key materialized as `products.sku` (`GPID-...`).

#### What normalization does

From live DB helper functions:

- lowercase
- unaccent
- strip punctuation/non-alphanumerics
- collapse spacing
- for brands, remove legal suffix tokens (`inc`, `llc`, `corp`, etc.)

#### Result profile

- Historical reference target (from project context): **0.32% exact match** after re-hash migration.
- Current table snapshot:
  - exact matches = 1,751
  - exact rate vs 161,653 distinct products = **1.08%**

#### Why exact hash fails

Hash exactness requires normalized strings to converge. They do not when:

- token order moves (`Brand - Name` vs `Name | Brand | Weight`),
- bracketed formatting differs,
- category text appears in title in one platform only,
- weight is missing or encoded differently,
- category fields disagree despite same actual product.

#### 5 real examples that should match but fail deterministic exact keying

1. `Simply Herb - Pave Ready To Roll` ↔ `Simply Herb - Pave [Ready-to-Roll] - 14g`
2. `Nature's Heritage - Papaya Melonz Flower` ↔ `Papaya Melonz | Nature's Heritage | 3.5g`
3. `CART - 1g White Widow` ↔ `White Widow Cart`
4. `Elderflower Cart` ↔ `CART - Elderflower`
5. `3.5g | Mint Sherbert | The Botanist` ↔ `The Botanist | Mint Sherbert | Flower | 3.5g`

All of these are real pairs accepted only under fuzzy logic.

---

### 3b) Fuzzy matching (`pg_trgm`)

#### How it works

Candidate generation and matching use trigram similarity metrics on names and brands (`gpid_candidates`, `product_matches`).

Configured/assumed gating rules (from project context and pair behavior):

- `name_similarity > 0.78`
- `brand_similarity > 0.75` or exact brand
- category must match or be in compatibility groups:
  - `{flower, preroll}`
  - `{vape, concentrate}`
  - `{edible, tincture}`
- weight tolerance ~12% when both sides have usable weight
- neutral handling when weight is missing

#### Live results

- total matches: 3,612
  - exact: 1,751
  - fuzzy_name: 1,861
- candidate pairs: 7,438
- unmatched candidates: 3,826 (**51.4%**)

#### Category-gate impact

- all candidate pairs with `incompatible` category relation remain unmatched
- this is a major recall sink

#### Confidence score concept

Current schema stores `confidence`, `name_similarity`, `brand_similarity`. A practical scoring form for future implementation:

`score = 0.55*name_sim + 0.25*brand_sim + 0.10*category_score + 0.10*weight_score`

where category/weight scores can be positive, neutral, or negative based on evidence quality.

#### 10 unmatched candidate pairs that should match (real query output)

```tsv
id\tplatform_a\tname_a\tbrand_a\tcat_a\twt_a\tplatform_b\tname_b\tbrand_b\tcat_b\twt_b\tname_similarity\tbrand_similarity
116\tleafly\tOrange Chemeleon\tBerkshire Roots\tconcentrate\t1.000\tjane\tOrange Chemeleon\tBerkshire Roots\tflower\t3.500\t1\t1
204\tjane\tCHEW - 50mg 1:4:1 Cherry Betty's [10pk]\tBetty's Eddies\tedible\t0.050\tleafly\tCHEW - 50mg 1:4:1 Cherry Betty's [10pk]\tBetty's Eddies\tflower\t\t1\t1
75\tleafly\tSkunk | Pre-Roll\tAnthologie\tpreroll\t\tweedmaps\tSkunk Pre-Roll\tAnthologie\tpreroll\t1.000\t1\t1
106\tleafly\tBerkshire Roots | Uplift Tincture ~225mg\tBerkshire Roots\tedible\t\tjane\tBerkshire Roots - Uplift Tincture (225mg)\tBerkshire Roots\ttincture\t0.000\t1\t1
156\tleafly\tGo Betty Go - Watermelon [10pk] (50mg THC/25mg THCV)\tBetty's Eddies\tflower\t\tjane\tGo Betty Go - Watermelon [10pk] (50mg THC/25mg THCV)\tBetty's Eddies\tedible\t0.000\t1\t1
150\tjane\tBedtime Betty’s Lemon Agave [10pk] (50mg THC) Sleep Fruit Chews\tBetty's Eddies\tedible\t0.000\tleafly\tBedtime Betty’s Lemon Agave [10pk] (50mg THC) Sleep Fruit Chews\tBetty's Eddies\tflower\t\t1\t1
34\tleafly\tGrape Gas x White Runtz\tAmber\tvape\t0.000\tjane\tGrape Gas x White Runtz\tAmber\tconcentrate\t1.000\t1\t1
17\tjane\tPink Gushers\tAmber\tconcentrate\t1.000\tleafly\tPink Gushers\tAmber\tvape\t0.000\t1\t1
12\tjane\tRaspberry Rosin Revive (100mg)\tAhh Moments\tedible\t0.100\tleafly\tRaspberry Rosin Revive (100mg)\tAhh Moments\tedible\t\t1\t1
228\tleafly\tBetty's Eddies - Cranberry Orange "Bundle Up" 1:6 Chews (50mg 10pk)\tBetty's Eddies\tflower\t\tjane\tBetty's Eddies - Cranberry Orange "Bundle Up" 1:6 Chews (50mg 10pk)\tBetty's Eddies\tedible\t0.050\t1\t1
(10 rows)

```

Most striking pattern: several pairs have `name_similarity=1` and `brand_similarity=1`, but are blocked by category mismatch (`edible` vs `flower`, `vape` vs `concentrate`).

---

### 3c) Brand dictionary

#### How it works

`brand_dictionary` attempts to map diverse raw brand strings into canonical identities with aliases:

- canonical_name
- aliases[]
- product/platform coverage metadata

#### First vs second attempt dynamics

- Attempt 1 (too strict): low merge rate (reported ~6.8%)
- Attempt 2 (too loose): extreme over-merge (reported ~84.66%)

#### Live evidence of over-merge

`Jeeter` canonical node currently has:

- alias_count: **22,422**
- product_count: **73,214**
- platform_count: **5**

This is almost certainly semantically over-absorbed.

#### Jeeter problem: clearly wrong aliases (real)

```tsv
alias
-Blue Dream (Hybrid)
-Blue Dream Hybrid
-Grapple Pie (I)
-Grapple Pie I
-Lemon Cherry Gelato
-Northern Lights (Indica)
-Northern Lights Indica
-orange 1 1/4
-Orange 1 1/4
-Purple Push Pop
-Unicorn Tears Indico
-White Widow
– Blue Razz
: CBC ayrloom"
''Balance'' Mango Serenity
''Energy'' Tropical Burst Sours
''Recover'' Freshly Squeezed
''Uplifting'' Pineapple Habanero
'25 Pre-Roll
'26 Pre Roll
'N Cream Flower
'Rosin'
"ACCESSORIES Aleaf Silicone Bowl Pipe (w/ Cover): SP254
"ACCESSORIES Ashtray
"ACCESSORIES Ashtray \"Drop In\"
"ACCESSORIES Ashtray \"Paisley Weed\"
"ACCESSORIES Ashtray \"Toadally Stoned\"
"ACCESSORIES Ashtray \"Trippy Leaf\"
"ACCESSORIES Ashtray \"Y/Y Hearts\"
"ACCESSORIES Ashtray Silicone Poker
"ACCESSORIES Banger (Etched Design 14mm)
"ACCESSORIES Banger w/ Terp Pearls (Spinner Kit \"Z\")
"ACCESSORIES Barrington Coffee Roasting Co.
"ACCESSORIES Book
"ACCESSORIES Chillum: Small"
"ACCESSORIES Cookies Ashtray
"ACCESSORIES Dank Tank Stash Jar
"ACCESSORIES Dry Herb Bowl Pack (14mm)
"ACCESSORIES Large Bubbler
"ACCESSORIES Lighter: Clipper"
"ACCESSORIES MEGA Rocket w/ Barrel Perc Nectar Collector: NCLF12
"ACCESSORIES Mini Bubbler
"ACCESSORIES Nectar Collector \"420\"
"ACCESSORIES PUFFCO
"ACCESSORIES Rolling Tray (Large) \"Monsters\"
"ACCESSORIES Rolling Tray (Medium) \"Raw Black Monster\"
"ACCESSORIES Scorch Torch X-series Floral
"ACCESSORIES Skull Glycerin Nectar Collector
"ACCESSORIES Stash Jar
"ALL-IN-ONE Afternoon Delight #4 (H)
"ALL-IN-ONE Honeydew #2 (SH)
"ALL-IN-ONE Rugged Roots
"BADDER Crispy Commission
"BADDER Cured Badder : MAC x Dosi
"BADDER Cured Badder: Bosscotti
"BADDER Cured Badder: Buttermilk Biscuits
"BADDER Cured Badder: Chem I95
"BADDER Cured Badder: Crostomperz
"BADDER Cured Badder: Dante's Inferno
"BADDER Cured Badder: Diesel Butter
"BADDER Cured Badder: Expiration Date
"BADDER Cured Badder: Fogu
"BADDER Cured Badder: Garlic Cookies
"BADDER Cured Badder: Glazed Onion
"BADDER Cured Badder: Gorilla Mittens
"BADDER Cured Badder: Granny Mac
"BADDER Cured Badder: Hellcat
"BADDER Cured Badder: Oreoz
"BADDER Cured Badder: Permanent Marker
"BADDER Cured Badder: Princess Mean Girl
"BADDER Cured Badder: RS-11
"BADDER Cured Badder: Sour Cheese Berry
"BADDER Cured Badder: Sub Zero
"BADDER Cured Badder: Tahoe Brunch
"BADDER Cured Badder: Triangle Mintz
"BADDER Cured Badder: Waiting Game
"BADDER Cured Badder: Zuspenders
"BADDER High Ledges
"BALMS Lip Balm
"Banana Pudding" [H]
(80 rows)

```

The alias set includes accessory text, random fragments, category descriptors, malformed quote artifacts, and non-brand strings.

#### Missed merges that should have been caught

Even with aggressive merging, raw-brand duplicates still survive in source products.

```tsv
brand_a\tcnt_a\tbrand_b\tcnt_b\tsim
soon.\t2391\tsoon."\t39\t1
High Supply\t1031\tHigh Supply™\t61\t1
Find.\t336\tFIND\t64\t1
Wyld\t323\tWYLD\t91\t1
Cresco\t311\tCresco™\t36\t1
incredibles\t290\tIncredibles\t26\t1
Cali Blaze\t289\tCali-Blaze\t508\t1
Luvbuds\t277\tLuvBuds\t21\t1
Good News\t277\tGood News™\t45\t1
strane\t245\tStrane\t32\t1
Coast Cannabis Co.\t146\tCoast Cannabis Co™\t67\t1
Vape\t134\tVAPE\t39\t1
PAX\t114\tPAX®\t277\t1
Insa\t104\tINSA\t421\t1
Rove\t92\tROVE\t868\t1
Holiday\t87\tHOLIDAY\t118\t1
Betty''s Eddies\t86\tBetty's Eddies\t498\t1
Find\t83\tFIND\t64\t1
Find\t83\tFind.\t336\t1
Nature''s Heritage\t79\tNature's Heritage\t965\t1
(20 rows)

```

Examples include:

- `High Supply` vs `High Supply™`
- `Cresco` vs `Cresco™`
- `Nature''s Heritage` vs `Nature's Heritage`
- `Betty''s Eddies` vs `Betty's Eddies`

So the system simultaneously over-merges in one direction and under-normalizes in another.

---

## 4) THE STRUGGLES

### 4a) Name formatting chaos

#### 20 real examples of same Jeeter-family products with cross-platform name variance

```tsv
platform_a\tname_a\tplatform_b\tname_b\tcat_a\tcat_b\twt_a\twt_b
weedmaps\tTropicali Infused Pre-Roll - Sativa |\tleafly\tTropicali Infused Pre-Roll 1g\tpreroll\tpreroll\t1.000\t
weedmaps\tStrawberry Cough Infused Pre-Roll |\tleafly\tStrawberry Cough Infused Pre-Roll 1g\tpreroll\tpreroll\t1.000\t
weedmaps\tBanana Peel Infused Pre-Roll |\tleafly\tBanana Peel Infused Pre-Roll 1g\tpreroll\tpreroll\t1.000\t
leafly\tMimosa | Infused Pre-Roll | 1g\tweedmaps\tMimosa Infused Pre-Roll |\tpreroll\tpreroll\t\t1.000
weedmaps\tSour Tsunami Infused Pre-Roll |\tleafly\tSour Tsunami | Infused Pre-Roll | 1g\tpreroll\tpreroll\t1.000\t
leafly\tJeeter - Gelato (H) Infused Baby Jeeter 0.5g 5pk (2.5g)\tweedmaps\tGelato (H) Infused Baby Jeeter 0.5g 5pk (2.5g) |\tpreroll\tpreroll\t\t2.500
leafly\tBABY JEETER Strawberry Cough Infused Pre-Roll 0.5g 5pk\tweedmaps\tStrawberry Cough Baby Jeeter Infused Pre-Roll 5pk |\tpreroll\tpreroll\t\t2.500
leafly\tJeeter - Gelato (H) Infused Jeeter (1g)\tweedmaps\tGelato (H) Infused Jeeter (1g) |\tpreroll\tpreroll\t\t1.000
weedmaps\tMaui Wowie (S) Infused Jeeter (1g) |\tleafly\tJeeter - Maui Wowie (S) Infused Jeeter (1g)\tpreroll\tpreroll\t1.000\t
weedmaps\tMaui Wowie (S) Infused Baby Jeeter 0.5g 5pk (2.5g) |\tleafly\tJeeter - Maui Wowie (S) Infused Baby Jeeter 0.5g 5pk (2.5g)\tpreroll\tpreroll\t2.500\t
weedmaps\tIced Matcha (S) Infused Jeeter (1g) |\tleafly\tJeeter - Iced Matcha (S) Infused Jeeter (1g)\tpreroll\tpreroll\t1.000\t
weedmaps\tBlue ZKZ XL Infused Pre-Roll |\tleafly\tXL Blue ZKZ Infused Pre-Roll 2g\tpreroll\tpreroll\t2.000\t
leafly\tJeeter - Blue ZKZ (I) Infused Jeeter (1g)\tweedmaps\tBlue ZKZ (I) Infused Jeeter (1g) |\tpreroll\tpreroll\t\t1.000
weedmaps\tOrange Daiquiri XL Infused Pre-Roll |\tleafly\tXL Orange Daiquiri Infused Pre-Roll 2g\tpreroll\tpreroll\t2.000\t
weedmaps\tMango Sherbet (I) Infused Baby Jeeter 0.5g 5pk (2.5g) |\tleafly\tJeeter - Mango Sherbet (I) Infused Baby Jeeter 0.5g 5pk (2.5g)\tpreroll\tpreroll\t2.500\t
weedmaps\tTropicali | 1g Infused\tleafly\tTropicali | Infused 2g\tpreroll\tpreroll\t1.000\t
weedmaps\tGelato Infused PR |\tleafly\tGelato | 2g Infused PR\tpreroll\tpreroll\t1.000\t
leafly\tTropicali | Infused 5pk\tweedmaps\tTropicali | 2.5g Infused | 5pk\tpreroll\tpreroll\t\t2.500
weedmaps\tBlue ZKZ | 1g Infused\tleafly\tBlue ZKZ Infused 2g\tpreroll\tpreroll\t1.000\t
weedmaps\tWatermelon ZKZ | 2g Infused\tleafly\tWatermelon ZKZ | Infused 1g\tpreroll\tpreroll\t2.000\t
(20 rows)

```

#### Common patterns

1. Weight in title vs field (`1g`, `2g`, `2.5g`, `5pk`) with inconsistent conversion.
2. Strain markers `(I)/(H)/(S)` appear variably.
3. Delimiter drift (`|`, `-`, brackets, quotes) changes tokenization behavior.
4. Suffix/prefix category words (`Flower`, `Cart`, `Infused Pre-Roll`) move around.
5. Promo text leaks into title, creating false lexical uniqueness.

### 4b) Weight data disaster

#### Quantitative

- 85.5% of candidate pairs are missing valid weight on at least one side.

#### Consequences

- Weight cannot be a strong primary discriminator.
- Missing-weight neutrality helps recall but harms precision if not compensated elsewhere.
- Name parser must infer weight and pack math from text reliably.

#### Weight distribution by platform

- Dutchie and Jane are relatively better on explicit weights.
- Leafly is highly sparse in `weight_grams` despite title often containing size.
- Weedmaps is mixed quality; some unit anomalies appear (`quantity/unit` inconsistencies).

### 4c) Brand normalization nightmare

Observed failure modes:

- same brand with punctuation/trademark variants,
- product phrase used as brand,
- generic terms used as brand,
- malformed escaping and quote artifacts,
- giant canonical clusters swallowing unrelated aliases.

Net impact: brand is still useful, but needs confidence-weighted trust and quality controls.

### 4d) Category mapping

Platforms mostly align for broad categories, but edge behavior causes many misses:

- prerolls: sometimes grouped near flower, sometimes strict preroll
- vape vs concentrate ambiguity for carts/disposables
- edible mislabeled as flower (seen repeatedly in unmatched pairs)
- occasional null/other categories

Recommendation: category should be a **soft probabilistic feature**, not an absolute gate.

---

## 5) AVAILABLE DATA ASSETS

### 5.1 CCC assets present (live)

- `ccc_licenses`: 772
- `ccc_lab_tests`: 147,649
- `ccc_avg_prices`: 31,038
- `ccc_monthly_prices`: 71

(`ccc_lab_tests` is currently below previously-cited 298K; algorithm design should rely on live row counts at execution time.)

### 5.2 `ccc_licenses` utility

- 770/772 rows map to `operators.operator_id` (99.7% linkage)
- useful for operator normalization and geographic/business constraints

### 5.3 Potential use in matching pipeline

1. Operator plausibility priors (business-level coherence).
2. THC range plausibility checks against observed product labels.
3. Category harmonization references.
4. External sanity checks for suspicious cross-platform merges.

Limitation: CCC data generally lacks cross-platform consumer-facing SKU detail and direct brand alias mappings.

---

## 6) WHAT WE NEED

Target: **>15% cross-platform match rate** while preserving precision and explainability.

### 6.1 Required capabilities

- robust handling of missing fields,
- aggressive but controlled normalization,
- evidence-based confidence scoring,
- measurable performance with regression tests,
- scalability for 150K+ and growing product graph,
- online improvement from human verdicts.

### 6.2 Recommended system design for next-generation matcher

#### Stage A — Canonical extraction

Parse product names into structured slots:

- brand tokens,
- strain tokens,
- product form (cart, preroll, gummy, tincture, etc.),
- weight/pack (`1g`, `5x0.5g`, `10pk`),
- potency tokens,
- noise/promotional token filtering.

#### Stage B — Candidate generation (high-recall blocking)

- normalized brand bucket blocks,
- token signature blocks,
- inferred-weight band blocks,
- category-family blocks,
- plus fallback blocks for null-brand/null-weight cases.

#### Stage C — Pair scoring model

Features should include:

- trigram + token-based textual similarity,
- brand trust-weighted similarity,
- category compatibility likelihood (not binary),
- inferred and explicit weight agreement,
- potency agreement (when available),
- platform/operator priors,
- data quality confidence per side.

A calibrated supervised model (e.g., gradient boosted trees + probability calibration) can output interpretable confidence bands.

#### Stage D — Graph consolidation

- build weighted match graph from accepted edges,
- resolve conflicts with constraints,
- form connected components as GPID clusters,
- maintain provenance of every edge and feature contribution.

#### Stage E — Human-in-the-loop

- route uncertain edges to review,
- incorporate verdicts in regular retraining,
- track model drift and threshold stability.

### 6.3 Metrics and governance

- Precision/Recall/F1 on labeled verdicts.
- Platform-pair and category-family breakdowns.
- High-risk cluster audit (large alias expansions).
- Regression suite from frozen edge sets.
- Daily change alerts for large score distribution shifts.

---

## 7) CURRENT DB SCHEMA (CREATE TABLE)

```sql
CREATE TABLE public.products (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  sku varchar(255) NOT NULL,
  name varchar(500) NOT NULL,
  brand varchar(255),
  category varchar(50),
  quantity numeric(10,3),
  unit varchar(10),
  description text,
  thc_percent numeric(5,2),
  cbd_percent numeric(5,2),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  weight_grams numeric(10,3),
  strain_type varchar(50),
  subcategory varchar(50),
  PRIMARY KEY (id),
  UNIQUE (sku)
);

CREATE TABLE public.prices (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  product_id uuid NOT NULL,
  source_id uuid NOT NULL,
  operator_id uuid NOT NULL,
  price numeric(10,2) NOT NULL,
  promo_flag boolean NOT NULL DEFAULT false,
  availability varchar(20),
  confidence numeric(3,2) NOT NULL,
  parser_type varchar(20),
  raw_data jsonb,
  scrape_job_id varchar(100),
  scraped_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  price_per_gram numeric(10,4),
  weight_grams numeric(10,3),
  menu_type varchar(10) DEFAULT 'rec',
  run_id uuid,
  PRIMARY KEY (id)
);

CREATE TABLE public.sources (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  operator_id uuid NOT NULL,
  source_type varchar(20) NOT NULL,
  url text NOT NULL,
  preferred_method varchar(20) NOT NULL,
  fallback_method varchar(20),
  auth_required boolean NOT NULL DEFAULT false,
  status varchar(20) NOT NULL DEFAULT 'active',
  freshness_sla_minutes integer NOT NULL DEFAULT 360,
  last_scraped_at timestamptz,
  last_success_at timestamptz,
  last_failure_at timestamptz,
  failure_count integer NOT NULL DEFAULT 0,
  success_rate_7d numeric(5,4),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  UNIQUE (url)
);

CREATE TABLE public.operators (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name varchar(255) NOT NULL,
  license_number varchar(100),
  city varchar(100) NOT NULL,
  state varchar(2) NOT NULL,
  lat numeric(10,8),
  lon numeric(11,8),
  status varchar(20) NOT NULL DEFAULT 'pending',
  email varchar(255),
  phone varchar(20),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb DEFAULT '{}'::jsonb,
  platform varchar(50),
  platform_slug varchar(255),
  canonical_operator_id uuid,
  match_confidence real,
  match_method varchar(50),
  PRIMARY KEY (id),
  UNIQUE (license_number)
);

CREATE TABLE public.product_matches (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  product_a_id uuid NOT NULL,
  product_b_id uuid NOT NULL,
  confidence double precision NOT NULL,
  match_type varchar(20) NOT NULL,
  name_similarity double precision,
  brand_similarity double precision,
  created_at timestamptz DEFAULT now(),
  verified boolean,
  PRIMARY KEY (id),
  UNIQUE (product_a_id, product_b_id)
);

CREATE TABLE public.gpid_candidates (
  id integer NOT NULL DEFAULT nextval('gpid_candidates_id_seq'::regclass),
  product_a_id uuid NOT NULL,
  product_b_id uuid NOT NULL,
  platform_a varchar(20) NOT NULL,
  platform_b varchar(20) NOT NULL,
  name_similarity double precision NOT NULL,
  brand_similarity double precision NOT NULL,
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (id),
  UNIQUE (product_a_id, product_b_id)
);

CREATE TABLE public.gpid_verdicts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  product_a_id uuid NOT NULL,
  product_b_id uuid NOT NULL,
  verdict varchar(20) NOT NULL,
  comment text,
  reviewer varchar(100) DEFAULT 'randy',
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (id),
  UNIQUE (product_a_id, product_b_id),
  CHECK (verdict IN ('correct','wrong','unsure'))
);

CREATE TABLE public.brand_dictionary (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  canonical_brand_name varchar(255) NOT NULL,
  normalized_key varchar(255) NOT NULL,
  aliases text[] NOT NULL DEFAULT '{}'::text[],
  parent_company varchar(255),
  is_mso boolean NOT NULL DEFAULT false,
  is_house_brand boolean NOT NULL DEFAULT false,
  confidence numeric(5,4) NOT NULL DEFAULT 1.0,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  canonical_name varchar(255) NOT NULL,
  product_count integer DEFAULT 0,
  platform_count integer DEFAULT 0,
  platforms text[] DEFAULT '{}'::text[],
  PRIMARY KEY (id),
  UNIQUE (canonical_brand_name),
  UNIQUE (normalized_key),
  UNIQUE (canonical_name)
);
```

---

## 8) RAW DATA SAMPLES (50 products + price history + source/operator)

Selection logic:

- 10 products each from Dutchie, Jane, Leafly, Weedmaps (40)
- 10 additional products sampled from matched-product pool
- Includes product columns, source/operator, and condensed price timeline

```tsv
source_type\tid\tsku\tname\tbrand\tcategory\tsubcategory\tquantity\tunit\tdescription\tthc_percent\tcbd_percent\tweight_grams\tstrain_type\toperator_name\tsource_url\tprice_points\tmin_price\tmax_price\tavg_price\tlast_seen\tprice_timeline
dutchie\t00022ad3-7b8d-484a-b59f-a2f96849cc36\tGPID-de72211efedd\tLazy River | Juicee J | Lazy River | Lazy River Hybrid TAC: 29.5% THC: 26.3%\tJuicee J\tflower\t\t\t\t\t26.30\t\t3.500\tHybrid\tElevated Roots\thttps://dutchie.com/dispensary/elevated-roots\t1\t30.00\t30.00\t30.00\t2026-02-12 07:19:33.936702+00\t2026-02-12:30.00
dutchie\t00029443-126a-44fc-a04a-f922c9823d63\tGPID-455657fb720a\tGummies | 20pk of 5mg* Sponsored Prickly Pear | Gummies | 20pk of 5mg* Hashables Hybrid THC: 89.4 mg\tPrickly Pear\tedible\t\t\t\t\t\t\t\tHybrid\tenlite-indian-orchard\thttps://dutchie.com/dispensary/enlite-indian-orchard\t1\t20.00\t20.00\t20.00\t2026-02-12 07:28:31.80853+00\t2026-02-12:20.00
dutchie\t00047d82-4340-4714-ad07-fc2d4f298627\tGPID-c8d5ee0710ec\tDisposable | 1000mg Blueberry Haze | Disposable | 1000mg PAX Sativa TAC: 90 mg THC: 85.55%\tBlueberry Haze\tvape\t\t\t\t\t85.55\t\t1.000\tSativa\tethos-dorchester-rec\thttps://dutchie.com/dispensary/ethos-dorchester-rec\t1\t31.50\t31.50\t31.50\t2026-02-12 07:33:32.490482+00\t2026-02-12:31.50
dutchie\t00062bb2-563f-4b10-9b9e-e7dffc3cccc0\tGPID-f7fe812f6189\tRuntz Banger Preroll Runtz Banger Preroll Bountiful Farms Hybrid THC: 24.71%\t\tpreroll\t\t\t\t\t24.71\t\t1.000\tHybrid\tbotera-franklin1\thttps://dutchie.com/dispensary/botera-franklin1\t2\t8.00\t8.00\t8.00\t2026-02-13 11:32:52.167828+00\t2026-02-13:8.00, 2026-02-12:8.00
dutchie\t00083aca-9f56-44f9-a055-9336ab2ca45d\tGPID-dd681b56a2d8\tKo Ko | Preroll - 1g Highlands | Ko Ko | Preroll - 1g Highlands Hybrid TAC: 28.12% THC: 23.74% 1g Prerolls - 6 for 50\tHighlands\tpreroll\t\t\t\t\t23.74\t\t1.000\tHybrid\tGreen N&apos; Go\thttps://dutchie.com/dispensary/green-n-go\t1\t9.99\t9.99\t9.99\t2026-02-12 08:02:16.277358+00\t2026-02-12:9.99
dutchie\t000919ae-3acf-4891-bfd3-503b055a8665\tGPID-1522e086773c\tBreathe Free - Papayamosa - Flower - 14g Breathe Free - Papayamosa - Flower - 14g Breathe Free Hybrid THC: 22.43%\t\tflower\t\t\t\t\t22.43\t\t14.000\tHybrid\tembr-springfield\thttps://dutchie.com/dispensary/embr-springfield\t1\t54.00\t54.00\t54.00\t2026-02-12 07:23:40.493027+00\t2026-02-12:54.00
dutchie\t000aa858-727e-49b6-8fec-4af5a56dd82b\tGPID-1e8ae28dc23d\tInfused Pre-Roll - Mango Mirage Infused Pre-Roll - Mango Mirage Sesh''n Hybrid TAC: 45.69% THC: 43.81%\t\tpreroll\t\t\t\t\t43.81\t\t1.000\tHybrid\tINSA - Salem\thttps://dutchie.com/dispensary/insa-salem\t4\t10.00\t18.00\t16.00\t2026-02-12 08:28:41.229505+00\t2026-02-12:18.00, 2026-02-12:18.00, 2026-02-12:18.00, 2026-02-12:10.00
dutchie\t000ac230-edab-4d02-8e30-3549d2864ab7\tGPID-85b05144c45e\tPre-roll - Pink Truffle - 1g Pre-roll - Pink Truffle - 1g Botanist Hybrid THC: 24.26%\t\tpreroll\t\t\t\t\t24.26\t\t1.000\tHybrid\tSmyth Cannabis Co. - Tewksbury\thttps://dutchie.com/dispensary/smyth-cannabis-co-tewksbury\t1\t5.00\t5.00\t5.00\t2026-02-12 10:08:54.58562+00\t2026-02-12:5.00
dutchie\t000aeb38-695f-4b0e-a2a5-26563dd53886\tGPID-9792c01c85bf\tPre-Roll 5pk | 0.5g each Grape Bubblegum | Pre-Roll 5pk | 0.5g each Hidden Hemlock Indica-Hybrid TAC: 22.1% THC: 20.5% Staff Pick\tGrape Bubblegum\tpreroll\t\t\t\t\t20.50\t\t2.500\tIndica-Hybrid\tjimbuddys\thttps://dutchie.com/dispensary/jimbuddys\t1\t35.00\t35.00\t35.00\t2026-02-12 08:31:25.718911+00\t2026-02-12:35.00
dutchie\t000c314a-fc75-41d6-8e90-34014c2e660f\tGPID-74305256820c\tHi5 Beverage Enhancer -150mg Hi5 Beverage Enhancer -150mg Hi5 Hybrid THC: 150 mg\t\tedible\t\t\t\t\t\t\t\tHybrid\tst-roslindale-ma\thttps://dutchie.com/dispensary/st-roslindale-ma\t1\t20.00\t20.00\t20.00\t2026-02-12 10:13:23.634888+00\t2026-02-12:20.00
jane\t00051365-bbb6-4fe9-8a4a-f70408533e12\tGPID-cabd1bc3145e\tMandarin Cookies [1000mg]\tCheetah\tvape\t\t\t\t\t73.97\t\t1.000\tsativa\tVerilife - Shrewsbury, MA - MED\thttps://www.iheartjane.com/stores/3731/verilife-shrewsbury-ma-med/menu\t4\t55.00\t55.00\t55.00\t2026-02-13 22:53:10.93333+00\t2026-02-13:55.00, 2026-02-13:55.00, 2026-02-13:55.00, 2026-02-13:55.00
jane\t00192a33-a399-42cd-a886-ea6b07cd9685\tGPID-9721068bbb43\tVery Berry [20pk] (1000mg)\tHedy\tedible\t\t\t\t\t\t\t0.000\thybrid\tPatriot Care - Greenfield Medical\thttps://www.iheartjane.com/stores/731/patriot-care-greenfield-medical/menu\t1\t100.00\t100.00\t100.00\t2026-02-13 22:53:07.285849+00\t2026-02-13:100.00
jane\t0027ee62-b640-49a8-80b7-637d156db881\tGPID-b4247e631115\tGolden Hour [1000mg]\tHoliday\tvape\t\t\t\t\t87.28\t\t0.500\tsativa\tSanctuary - Gardner REC\thttps://www.iheartjane.com/stores/1591/sanctuary-gardner-rec/menu\t1\t35.00\t35.00\t35.00\t2026-02-13 22:52:46.499572+00\t2026-02-13:35.00
jane\t002d0576-1932-46cc-af27-903e8a04f663\tGPID-00bc5f4564f4\tDeath Star\t\tflower\t\t\t\t\t\t\t2.000\thybrid\tAmy's Apothecary\thttps://www.iheartjane.com/stores/3/amy-s-apothecary/menu\t1\t24.00\t24.00\t24.00\t2026-02-13 14:25:40.065195+00\t2026-02-13:24.00
jane\t0040e7c7-869d-4c2a-ac7f-e08038a1021e\tGPID-2c304cb7ef30\tCantaloupe Dream Disposable\tDime Industries\tvape\t\t\t\t\t95.54\t2.84\t2.000\tsativa\tFull Harvest Moonz - Haverhill\thttps://www.iheartjane.com/stores/2783/full-harvest-moonz/menu\t1\t80.00\t80.00\t80.00\t2026-02-13 22:52:24.309206+00\t2026-02-13:80.00
jane\t0053dcb9-c163-4156-9794-f7766709433f\tGPID-245119c75db7\tLembrule\tMello\tflower\t\t\t\t\t0.59\t\t3.500\thybrid\tSanctuary - Woburn REC\thttps://www.iheartjane.com/stores/5366/sanctuary-woburn-rec/menu\t3\t25.00\t40.00\t31.67\t2026-02-13 22:52:59.154608+00\t2026-02-13:30.00, 2026-02-13:25.00, 2026-02-13:40.00
jane\t0060dac4-e55f-4423-a20a-b3d9ca6e9409\tGPID-d49d25f63951\tGround Shake - Ginger Tea\tSanctuary\tflower\t\t\t\t\t29.24\t\t14.000\tsativa\tSanctuary - Woburn REC\thttps://www.iheartjane.com/stores/5366/sanctuary-woburn-rec/menu\t4\t45.00\t45.00\t45.00\t2026-02-13 14:44:08.118796+00\t2026-02-13:45.00, 2026-02-13:45.00, 2026-02-13:45.00, 2026-02-13:45.00
jane\t006e3daf-2be2-449e-8da8-4b6d644db1a9\tGPID-3aa351c45b76\tPurple Trainwreck\t\tflower\t\t\t\t\t\t\t2.000\tsativa\tAmy's Apothecary\thttps://www.iheartjane.com/stores/3/amy-s-apothecary/menu\t1\t24.00\t24.00\t24.00\t2026-02-13 14:25:40.237449+00\t2026-02-13:24.00
jane\t007292eb-da0f-44cb-9d0f-4f5df737d08d\tGPID-36364975389a\tGarlic Drip\tHarbor House Collective\tflower\t\t\t\t\t25.59\t\t7.000\thybrid\tSanctuary - Woburn REC\thttps://www.iheartjane.com/stores/5366/sanctuary-woburn-rec/menu\t1\t32.00\t32.00\t32.00\t2026-02-13 22:52:59.002305+00\t2026-02-13:32.00
jane\t008170b9-e61a-4f32-90c4-cae500213fb8\tGPID-b80e620ec179\tToxic Taffy\tSparq\tflower\t\t\t\t\t21.90\t\t14.000\thybrid\tVerilife - Wareham, MA - MED\thttps://www.iheartjane.com/stores/2936/verilife-wareham-ma-med/menu\t3\t70.25\t80.00\t76.75\t2026-02-13 22:53:08.940959+00\t2026-02-13:80.00, 2026-02-13:80.00, 2026-02-13:70.25
leafly\t00020d83-b119-47c6-9ae0-29302dd9fa83\tGPID-aea7281eb402\tThe Cure Company | Curelato | 3.5g\tThe Cure Company\tflower\t\t\t\t\t21.95\t\t3.500\t\tTemescal Wellness - Framingham (Medical)\thttps://www.leafly.com/dispensary-info/temescal-wellness-framingham\t2\t25.00\t25.00\t25.00\t2026-02-14 00:24:12.007141+00\t2026-02-14:25.00, 2026-02-14:25.00
leafly\t00046156-bdbf-4c9e-bcd4-a08c4fdc1c61\tGPID-974373563540\tCamino 2:1 Freshly Squeezed Gummies 100mg 20pk (CBG:THC)\tCamino\tedible\t\t\t\t\t\t\t\t\tStories Cannabis\thttps://www.leafly.com/dispensary-info/stories-cannabis\t1\t22.00\t22.00\t22.00\t2026-02-14 00:15:33.020405+00\t2026-02-14:22.00
leafly\t00063cd9-093b-42f4-adce-1de7dcba0d21\tGPID-d2496ebf99f3\tBlueberry Cinnamon Streusel Cheesecake\tDouble Baked\tedible\t\t\t\t\t\t\t\t\tGarden Wonders Cannabis\thttps://www.leafly.com/dispensary-info/garden-wonders\t1\t20.00\t20.00\t20.00\t2026-02-13 23:25:03.955461+00\t2026-02-13:20.00
leafly\t0006e6b7-12f0-4398-b51f-e84412a32479\tGPID-40cf63248d14\tNature's Heritage | Cherimoya | 3.5g\tNature's Heritage\tflower\t\t\t\t\t22.41\t0.00\t\t\tTemescal Wellness - Hudson (Medical)\thttps://www.leafly.com/dispensary-info/temescal-wellness-hudson\t3\t24.00\t25.00\t24.67\t2026-02-14 00:25:18.528555+00\t2026-02-14:25.00, 2026-02-14:25.00, 2026-02-13:24.00
leafly\t000767ff-6fe1-4e98-82a9-6e630d2a48b3\tGPID-9b9e5ec7489a\tSilicone Hand Pipe 5\t\tflower\t\t\t\t\t\t\t\t\tBliss - Lunenburg\thttps://www.leafly.com/dispensary-info/bliss-lunenburg\t1\t5.00\t5.00\t5.00\t2026-02-13 23:06:35.280166+00\t2026-02-13:5.00
leafly\t00081bee-4dca-4693-92fa-04b96c7bf244\tGPID-bdc6ef6b6548\t510 | Northern Lights | 1g\tSelect Oil\tvape\t\t\t\t\t\t\t\t\tBotera - Franklin\thttps://www.leafly.com/dispensary-info/botera-franklin\t1\t18.00\t18.00\t18.00\t2026-02-13 23:09:33.657363+00\t2026-02-13:18.00
leafly\t000c66eb-477c-4a39-bf6a-232bb9d3a7b0\tGPID-a114d55f20e0\tLemon Drop | Live Badder - 3.5 g\tDope\tconcentrate\t\t\t\t\t0.00\t\t3.500\t\tSublime Cannabis Co. - Mashpee Dispensary\thttps://www.leafly.com/dispensary-info/sublime-cannabis-co--b4365\t1\t80.00\t80.00\t80.00\t2026-02-14 00:16:24.999314+00\t2026-02-14:80.00
leafly\t000d767a-e4e6-4da6-a9e5-0e1b2ade6501\tGPID-ab46ec2714e7\tBABY JEETER Orange Daiquiri Infused Pre-Roll 0.5g 5pk\tJeeter\tpreroll\t\t\t\t\t33.82\t0.67\t\t\tBask - Adult Use (Recreational)\thttps://www.leafly.com/dispensary-info/bask---adult-use--recreational-\t1\t48.00\t48.00\t48.00\t2026-02-13 23:04:28.904292+00\t2026-02-13:48.00
leafly\t000f27df-f4a5-437a-8e93-0bf78deb883c\tGPID-e2fdaa5c6d1f\tGood Vibes | Plus Sleep 1:1:1 | Lemon Dreams | Tincture | 300mg\tGood Vibes Edibles\tconcentrate\t\t\t\t\t\t\t\t\tTemescal Wellness - Hudson (Medical)\thttps://www.leafly.com/dispensary-info/temescal-wellness-hudson\t3\t45.00\t45.00\t45.00\t2026-02-14 00:25:17.184341+00\t2026-02-14:45.00, 2026-02-14:45.00, 2026-02-14:45.00
leafly\t00100001-6511-4834-90cf-6be8cadee4f7\tGPID-4a7ac098656e\tRECTANGLE SILICONE DAB STRAW AND CHILLUM KIT\tHigh Mountain Imports\tflower\t\t\t\t\t\t\t\t\tDevine\thttps://www.leafly.com/dispensary-info/devine\t1\t10.00\t10.00\t10.00\t2026-02-13 23:20:53.04904+00\t2026-02-13:10.00
leafly\t0026b229-b98b-444f-a1d3-7c1a3a00680a\tGPID-5a927489f29d\tPeanut Butter Breath Live Hash Rosin\tAmber\tconcentrate\t\t\t\t\t86.70\t\t1.000\tindica\tCannabist - Lowell (Medical)\thttps://www.leafly.com/dispensary-info/patriot-care---lowell-\t2\t50.00\t50.00\t50.00\t2026-02-13 23:56:18.931347+00\t2026-02-13:50.00, 2026-02-13:50.00
leafly\t002d82bb-ea2f-4b6e-8c34-797026aa2a97\tGPID-c53a020ed272\tCelebrate Hybrid Seltzer | Levia | 5mg\tLEVIA\tedible\t\t\t\t\t0.00\t0.00\t\t\tElevated Roots - Halifax\thttps://www.leafly.com/dispensary-info/elevated-roots-halifax\t1\t7.00\t7.00\t7.00\t2026-02-13 23:22:14.460396+00\t2026-02-13:7.00
leafly\t0034d531-f834-494d-8330-3df47d73ced2\tGPID-ff0883b2aea7\tBlue Zushi 3.5g, Flower\tHigh Ledges Cannabis\tflower\t\t\t\t\t26.07\t0.00\t\t\tNova Farms - Dracut\thttps://www.leafly.com/dispensary-info/nova-farms-dracut\t1\t35.77\t35.77\t35.77\t2026-02-13 23:53:24.211412+00\t2026-02-13:35.77
leafly\t00adf800-3157-4351-8575-41550f9bea30\tGPID-20fbeecfc254\tBaby Jeeter Infused Pre-Roll Milk Man 5pk | 2.5g\tJeeter\tpreroll\t\t\t\t\t33.39\t0.30\t\t\tThe Holistic Concepts\thttps://www.leafly.com/dispensary-info/the-holistic-concepts\t2\t45.00\t48.00\t46.50\t2026-02-14 00:29:15.719263+00\t2026-02-14:45.00, 2026-02-13:48.00
leafly\t00b6f071-3d97-4507-9177-b1550067e26b\tGPID-7799e3826e15\tWhite Widow\tBudhaus\tflower\t\t\t\t\t24.74\t\t\t\tCannabist - Lowell (Adult-Use)\thttps://www.leafly.com/dispensary-info/patriot-care-lowell--recreational-\t1\t30.00\t30.00\t30.00\t2026-02-13 15:00:51.263137+00\t2026-02-13:30.00
leafly\t00c6a00d-29a8-41f5-8f9c-77c559b897db\tGPID-767f403f5f34\tSpace Queen Cart 1g\tFernway\tvape\t\t\t\t\t82.44\t\t1.000\t\t253 Farmacy (Amherst)\thttps://www.leafly.com/dispensary-info/253-farmacy-amherst\t1\t30.00\t30.00\t30.00\t2026-02-13 23:00:25.155744+00\t2026-02-13:30.00
weedmaps\t000432cf-eeaf-4036-b4cc-9e3ba3914986\tGPID-9c9f276a97d9\t.5g Governmint Oasis Pre\t\tpreroll\t\t\t\t\t25.80\t0.10\t\t\tFull Harvest Moonz - Haverhill\thttps://weedmaps.com/dispensaries/full-harvest-moonz\t1\t35.00\t35.00\t35.00\t2026-02-12 09:39:05.691791+00\t2026-02-12:35.00
weedmaps\t0004af1f-8727-45e7-a753-8a484df4ecaa\tGPID-39046d237b6a\tDank | Infused Pre-Roll | Mango\tHaze\tpreroll\t\t\t\t\t\t\t\t\tBudds Dispensary Catskill\thttps://weedmaps.com/dispensaries/budds-dispensary-catskill\t1\t18.00\t18.00\t18.00\t2026-02-13 03:55:09.170863+00\t2026-02-13:18.00
weedmaps\t0006ff7e-f314-40bd-95a2-5ee3eaa01873\tGPID-bfbd4dbe9205\t1/8 Oz Add To Cart Flower Shire 1/8th\t\tflower\t\t8.000\toz\t\t\t\t\t\tCannabis Cured - Eliot\thttps://weedmaps.com/dispensaries/cannabis-cured-eliot\t1\t35.00\t35.00\t35.00\t2026-02-13 05:58:38.92+00\t2026-02-13:35.00
weedmaps\t0007536e-118b-45a0-bd37-04cafee6774e\tGPID-5003d0f8c856\tGrassroots GMO (Indica) .4g\t\tpreroll\t\t\t\t\t33.55\t\t5.000\t\tStage One Dispensary\thttps://weedmaps.com/dispensaries/stage-one-dispensary\t1\t11.90\t11.90\t11.90\t2026-02-12 13:49:13.208323+00\t2026-02-12:11.90
weedmaps\t0008d88b-3917-4981-bfd7-d3d4b49246c4\tGPID-71974a7381f5\tStreet Tartz\t\tflower\t\t\t\t\t21.95\t\t3.500\t\tEmber Gardens\thttps://weedmaps.com/dispensaries/ember-gardens\t3\t15.00\t20.00\t18.33\t2026-02-13 05:52:00.72916+00\t2026-02-13:20.00, 2026-02-12:15.00, 2026-02-12:20.00
weedmaps\t000b266f-4ddd-47fa-9640-b812229c551a\tGPID-09abe794adc2\tHybrid\t\tconcentrate\t\t\t\t\t74.69\t\t1.000\t\tHidden Wonders\thttps://weedmaps.com/dispensaries/hidden-wonders\t3\t35.00\t35.00\t35.00\t2026-02-13 06:45:24.006138+00\t2026-02-13:35.00, 2026-02-12:35.00, 2026-02-12:35.00
weedmaps\t000cd024-a5c7-4688-a58e-c2691a53801e\tGPID-686fc2ccf5c8\tGold Cannabis Leaf Earrings\tZad Jewelry\tflower\t\t\t\t\t\t\t\t\tCanna Provisions Holyoke\thttps://weedmaps.com/dispensaries/canna-provisions-holyoke\t1\t10.00\t10.00\t10.00\t2026-02-12 07:57:49.317035+00\t2026-02-12:10.00
weedmaps\t0010007a-2fd3-42ff-b165-6989f3b436bf\tGPID-b62c87c4f80e\tBlue ZKZ (I) 1g - Jeeter Infused Preroll\t\tpreroll\t\t\t\t\t\t\t1.000\t\tDDM Cannabis\thttps://weedmaps.com/dispensaries/ddm-cannabis\t1\t24.00\t24.00\t24.00\t2026-02-13 05:26:10.192509+00\t2026-02-13:24.00
weedmaps\t00106ebc-6b39-4cf8-a71d-3924a348b182\tGPID-0826e059ad1a\tAeterna | Gelato 33\tPre Roll\tpreroll\t\t\t\t\t26.00\t\t1.000\t\tRiverbend Dispensary\thttps://weedmaps.com/dispensaries/riverbend-dispensary\t1\t10.00\t10.00\t10.00\t2026-02-12 13:06:29.971801+00\t2026-02-12:10.00
weedmaps\t0010d9b1-2771-4b4d-a92f-7108e164f4f2\tGPID-7b62b2dfa55f\tALL-IN-ONE Fernway AIO Vape (T PRO) | 2g\tStonefruit [H]\tflower\t\t\t\t\t\t\t2.000\t\tThTree\thttps://weedmaps.com/dispensaries/thtree\t1\t70.80\t70.80\t70.80\t2026-02-12 15:25:35.114352+00\t2026-02-12:70.80
weedmaps\t0069ac76-ac75-4dd0-a4c6-6ddcfe84b394\tGPID-6f07207d803d\tPeach Lemon (Hybrid) Seltzer\tLevia\tedible\t\t\t\t\t\t\t\t\tLocal Cannabis Company - Swampscott\thttps://weedmaps.com/dispensaries/local-cannabis-company-swampscott\t1\t6.00\t6.00\t6.00\t2026-02-12 11:35:49.533465+00\t2026-02-12:6.00
weedmaps\t008fbac7-61a1-45db-8e79-da9cbca2b311\tGPID-6549efda19eb\tUncle Snoop Pre-Roll |\tYour Highness\tpreroll\t\t\t\t\t27.84\t\t1.000\t\tElevated Roots - Halifax\thttps://weedmaps.com/dispensaries/elevated-roots-halifax\t2\t10.00\t12.00\t11.00\t2026-02-13 05:48:59.634386+00\t2026-02-13:10.00, 2026-02-13:12.00
weedmaps\t00a02b05-acbb-4d35-8aaa-5e95f8538739\tGPID-88654f28dcdc\tBored Grapes\tLazy River\tflower\t\t\t\t\t22.21\t\t3.500\t\tFirebrand Cannabis\thttps://weedmaps.com/dispensaries/stone-s-throw-cannabis-llc-dba-firebrand-cannabis\t1\t25.00\t25.00\t25.00\t2026-02-12 13:52:44.337745+00\t2026-02-12:25.00
weedmaps\t00d54df8-1a80-4eed-8034-6baae1786a18\tGPID-7f2a2705173a\tGrape High-Chew Flower (3.5g)\tDCC\tflower\t\t\t\t\t25.96\t\t3.500\t\tFine Fettle\thttps://weedmaps.com/dispensaries/fine-fettle\t2\t25.00\t25.00\t25.00\t2026-02-13 06:00:16.600353+00\t2026-02-13:25.00, 2026-02-12:25.00
(50 rows)

```

---

## Final Technical Readout for Algorithm Team

The matching challenge is not purely a fuzzy string problem. It is a **heterogeneous entity resolution problem under heavy missingness, label noise, and lexical contamination**. The current implementation already demonstrates that simple deterministic hashing underperforms and basic trigram matching with hard category gates misses many obviously correct pairs.

A next-generation pipeline should combine:

1. high-recall candidate generation,
2. richer semantic parsing,
3. calibrated probabilistic scoring,
4. graph-level consistency enforcement,
5. continual learning from verdicts.

If built with strong quality controls (especially around brand alias expansion and category soft logic), the >15% match-rate target is realistic.
