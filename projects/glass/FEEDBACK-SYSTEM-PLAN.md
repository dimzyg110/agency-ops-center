# GLASS Feedback System — Community-Powered Data Accuracy

**Date:** February 13, 2026  
**Status:** PLAN — Ready to Build  
**For:** Randy Torres, Roviq

---

## 1. Executive Summary

GLASS scrapes menus from Dutchie, Weedmaps, Leafly, and iHeartJane across 385+ Massachusetts dispensaries. Scrapers are good but imperfect — prices go stale between scrapes, parsers misread data, stores open and close, and products get miscategorized. Every wrong price erodes consumer trust.

The feedback system turns this weakness into a competitive advantage. Instead of silently serving stale data, GLASS invites users to correct it. Every correction makes the dataset more accurate than any single scraper could achieve alone. Over time, GLASS becomes a community-validated source of truth — the Wikipedia of Massachusetts cannabis pricing.

**The core loop:**
```
Scraper collects data → Consumer/Dispensary spots error → Submits correction
    → Correction validated (trust scoring + cross-reference) → Data improves
    → Scraper learns (frequency adjustments, parser fixes) → Fewer errors
    → Users trust GLASS more → More users → More corrections → Better data
```

**Design philosophy:** Dead simple for users, sophisticated on the backend. A consumer should be able to report a wrong price in under 5 seconds without logging in. A dispensary operator should be able to bulk-correct their entire menu in one upload. Everything else happens invisibly.

---

## 2. Error Taxonomy

### 2.1 What Goes Wrong

| Error Type | Source | Frequency | User Impact | Who Notices |
|-----------|--------|-----------|-------------|-------------|
| **Stale price** | Time between scrapes (up to 24h) | Very High | Consumer shows up expecting $35, it's $45 | Consumer at the store |
| **Wrong price** | Parser misread, multi-weight confusion | High | Trust destruction | Consumer comparing to live menu |
| **Wrong category** | Parser assigned flower as pre-roll, etc. | Medium | Search results polluted | Consumer filtering by category |
| **Wrong THC/CBD%** | Parser error, dispensary entered wrong data | Medium | Consumer made wrong choice | Experienced consumers, operators |
| **Wrong store info** | Hours changed, store moved, closed | Low-Medium | Wasted trip | Consumer who drove there |
| **Missing product** | Scraper didn't load full menu (lazy loading, pagination) | Medium | Incomplete comparisons | Consumer who knows the product exists |
| **Missing store** | Not in our slug list, new store opened | Low | No coverage | Local consumers, the operator |
| **GPID false merge** | Two different products linked as one | Low | Wrong price comparison (critical) | Consumer who knows both products |
| **GPID false split** | Same product not linked across stores | Medium | Missing price comparisons | Consumer searching across stores |
| **Discontinued product** | Store removed it but we still show it | Medium | Consumer expects to find it | Consumer at the store |
| **Wrong store name/address** | Scraper pulled from wrong field | Low | Confusion, misdirection | Anyone who visits the page |

### 2.2 Who Notices What

**Consumers notice:**
- Price discrepancies (they're staring at the actual menu in-store or on Dutchie)
- Store closures, wrong hours (they drove there)
- Missing products they know exist ("I bought this here yesterday, why isn't it on GLASS?")
- Wrong categories (they searched for flower and got a pre-roll)
- GPID issues (they know two "Blue Dream 1/8" entries are the same product from different listings)

**Consumers DON'T notice:**
- Systematic parser errors (they see one price, not patterns)
- Cross-platform deduplication bugs
- Scraper infrastructure issues
- THC% discrepancies (unless they're experienced)

**Dispensary operators notice:**
- Every error about their own store (they know their menu, hours, and inventory perfectly)
- Competitor prices that seem wrong (they shop each other)
- Missing products from their menu (lost sales opportunity)
- Wrong store information (brand damage)

**Dispensary operators DON'T notice:**
- Errors at stores they don't watch
- GPID matching issues outside their product line
- Internal pipeline or scraping logic issues

### 2.3 Error Severity Tiers

| Tier | Description | Examples | Action Required |
|------|-------------|----------|-----------------|
| **P0 — Trust Killer** | Wrong price shown to consumer | Price off by >20%, product shows wrong store | Auto-flag, highest priority review |
| **P1 — Misleading** | Data is wrong but not catastrophically | Wrong category, stale THC%, wrong hours | Queue for review, apply if validated |
| **P2 — Incomplete** | Missing data that should be there | Missing products, missing stores | Log, batch process |
| **P3 — Cosmetic** | Technically wrong but low impact | Misspelled brand name, wrong image | Low priority, batch fix |

---

## 3. User Feedback UX

### 3.1 Core Principle: Google Maps "Suggest an Edit" Simplicity

Every correction should take **under 10 seconds** for a consumer and **under 2 minutes** for bulk dispensary corrections. No login required for basic reports. No forms longer than 3 fields.

### 3.2 Consumer Feedback Flows

#### Flow 1: "Wrong Price" (The #1 Use Case)

**Where it appears:** Next to every price on product cards, comparison tables, and dispensary menu pages.

**Wireframe:**
```
┌─────────────────────────────────────┐
│  Blue Dream 1/8                     │
│  Green Thumb Dispensary             │
│  $45.00          [⚑ Wrong price?]   │
│  Updated 6 hours ago                │
└─────────────────────────────────────┘

User taps "⚑ Wrong price?" →

┌─────────────────────────────────────┐
│  What's the real price?             │
│                                     │
│  ┌─────────────────────────┐        │
│  │ $  [  35.00           ] │        │
│  └─────────────────────────┘        │
│                                     │
│  ○ I saw this in-store today        │
│  ○ I saw this on their website      │
│  ○ I'm not sure, it just looks wrong│
│                                     │
│  [Submit]            [Cancel]       │
│                                     │
│  💡 No login needed. Corrections    │
│  with accounts get applied faster.  │
└─────────────────────────────────────┘
```

**Key decisions:**
- Single input field for the new price — no dropdowns, no multi-step
- One-tap source selector (in-store / website / unsure) feeds confidence scoring
- "No login needed" lowers friction; gentle nudge toward accounts
- Confirmation toast: "Thanks! We'll verify and update this." (not "submitted for review" — too cold)

#### Flow 2: "Report Issue" (General Product Problems)

**Where it appears:** Three-dot menu or small flag icon on every product listing.

**Wireframe:**
```
User taps "..." or "⚑" on a product →

┌─────────────────────────────────────┐
│  What's wrong with this listing?    │
│                                     │
│  ☐ Price is wrong                   │
│  ☐ Product doesn't exist anymore    │
│  ☐ Wrong category (it's not flower) │
│  ☐ Wrong THC/CBD percentage         │
│  ☐ Wrong brand or product name      │
│  ☐ Wrong store (not sold here)      │
│  ☐ Something else                   │
│                                     │
│  Details (optional):                │
│  ┌─────────────────────────┐        │
│  │ [Free text, 280 chars ] │        │
│  └─────────────────────────┘        │
│                                     │
│  [Submit Report]                    │
└─────────────────────────────────────┘
```

**Key decisions:**
- Checkboxes, not radio buttons — multiple issues can exist simultaneously
- "Price is wrong" opens the dedicated price correction flow (Flow 1)
- Free text is optional, not required — reduce friction
- "Product doesn't exist anymore" is common and critical (stale data)

#### Flow 3: "Store Issue" (Wrong Hours, Closed, Moved)

**Where it appears:** On every dispensary page, below the store info section.

**Wireframe:**
```
┌─────────────────────────────────────┐
│  Green Thumb Dispensary             │
│  123 Main St, Boston, MA            │
│  Open: 10am - 8pm                   │
│                                     │
│  [📝 Suggest an edit]               │
└─────────────────────────────────────┘

User taps "Suggest an edit" →

┌─────────────────────────────────────┐
│  What needs fixing?                 │
│                                     │
│  ○ Hours are wrong                  │
│    → [Opens hour picker]            │
│                                     │
│  ○ Address is wrong                 │
│    → [Opens address field]          │
│                                     │
│  ○ Store is permanently closed      │
│  ○ Store has moved                  │
│    → [Opens address field]          │
│                                     │
│  ○ Store name is wrong              │
│    → [Opens text field]             │
│                                     │
│  ○ Missing from GLASS entirely      │
│    (I know a dispensary not listed)  │
│    → [Opens name + URL fields]      │
│                                     │
│  [Submit]                           │
└─────────────────────────────────────┘
```

#### Flow 4: "Same Product" / "Not Same Product" (GPID Assist)

**Where it appears:** On comparison pages where we show the same GPID across stores, and on product detail pages that list "also available at."

**Wireframe:**
```
┌─────────────────────────────────────────────┐
│  Blue Dream 1/8 — Available at 5 stores     │
│                                             │
│  ┌───────────────────┐  ┌────────────────┐  │
│  │ Green Thumb  $45  │  │ Bud's Place $38│  │
│  │ Blue Dream 3.5g   │  │ Blue Dream 1/8 │  │
│  └───────────────────┘  └────────────────┘  │
│                                             │
│  Are these the same product?                │
│  [✓ Yes, same]  [✗ No, different]           │
│                                             │
│  ── or on a single product page ──          │
│                                             │
│  "This is also available at Bud's Place"    │
│  [✓ Correct]  [✗ That's a different product]│
└─────────────────────────────────────────────┘
```

**Key decisions:**
- Binary choice only — no explanation needed from user
- Surface this passively, not as a call-to-action (reduce cognitive load)
- Aggregate votes: if 5 people say "different product," auto-flag the GPID match
- This is a Month 2+ feature — needs a critical mass of GPID matches first

#### Flow 5: "Was This Helpful?" (Implicit Quality Signal)

**Where it appears:** After a consumer uses a price comparison result.

**Wireframe:**
```
┌─────────────────────────────────────┐
│  You're viewing prices near Boston  │
│  for "Blue Dream 1/8"              │
│                                     │
│  Was this comparison helpful?       │
│  [👍 Yes]  [👎 No]                  │
│                                     │
│  (if No) → What was wrong?         │
│  ○ Prices were outdated             │
│  ○ Missing a store I know carries it│
│  ○ Wrong products in results        │
│  ○ Other: [________]               │
└─────────────────────────────────────┘
```

**Key decisions:**
- Only show after meaningful engagement (viewed 3+ results, or clicked a store link)
- "No" expands into a mini-feedback form; "Yes" just logs the positive signal
- Implicit signal: high thumbs-down rate on a search query = data quality issue to investigate

### 3.3 Dispensary Operator Feedback Flows

#### Flow 6: "Claim Your Page" → Full Edit Access

**Where it appears:** Every dispensary page has a "Own this dispensary? Claim your page" link. (Already planned in Consumer Strategy Week 3-4.)

**Once claimed and verified:**

```
┌─────────────────────────────────────────────┐
│  GREEN THUMB DISPENSARY — Operator Dashboard │
│                                             │
│  ⚠️ 3 items need attention                  │
│                                             │
│  Price Corrections:                         │
│  ┌─────────────────────────────────────┐    │
│  │ Blue Dream 1/8    GLASS: $45  →     │    │
│  │ [Correct price: $ _____ ] [Save]    │    │
│  ├─────────────────────────────────────┤    │
│  │ GMO Cookies 1g    GLASS: $15  →     │    │
│  │ [Correct price: $ _____ ] [Save]    │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Store Info:                                │
│  Hours: [Mon-Sat 10-8, Sun 10-6] [Edit]    │
│  Address: [123 Main St] [Edit]              │
│  Phone: [(617) 555-1234] [Edit]             │
│  Status: ● Open  ○ Temporarily Closed       │
│           ○ Permanently Closed               │
│                                             │
│  Menu Management:                           │
│  [Upload Full Menu CSV/Excel]               │
│  [Flag products we don't carry anymore]     │
│  [Add products GLASS is missing]            │
│                                             │
│  Last scraped: 6 hours ago                  │
│  [Request immediate re-scrape]              │
└─────────────────────────────────────────────┘
```

**Key decisions:**
- Inline editing — click a price, type the correct one, save. No forms.
- Bulk upload via CSV/Excel (we define the template; columns: product_name, brand, category, price, weight, thc_pct, cbd_pct)
- "Flag as discontinued" is a toggle on each product — one-tap removal
- "Request re-scrape" triggers a priority scrape of their specific store within 30 minutes
- Operator corrections bypass review queue — applied immediately to display layer with an `operator_verified` flag

#### Flow 7: Bulk Menu Upload (Operator)

```
┌─────────────────────────────────────────────┐
│  Upload Your Current Menu                   │
│                                             │
│  Download our template: [CSV] [Excel]       │
│                                             │
│  ┌─────────────────────────────┐            │
│  │  [Drag & drop or click to  │            │
│  │   upload your menu file]    │            │
│  └─────────────────────────────┘            │
│                                             │
│  Or paste your Dutchie/Weedmaps admin URL:  │
│  ┌─────────────────────────────┐            │
│  │ https://...                 │            │
│  └─────────────────────────────┘            │
│  (We'll pull your menu directly)            │
│                                             │
│  Preview: (after upload)                    │
│  ┌────────────────────────────────────────┐ │
│  │ Product        | Price | Status        │ │
│  │ Blue Dream 1/8 | $38   | ✅ Matched    │ │
│  │ GMO Cookies 1g | $15   | ⚠️ Price diff │ │
│  │ Sunset Sherb   | $42   | ➕ New to GLASS│ │
│  └────────────────────────────────────────┘ │
│                                             │
│  [Apply All Corrections]  [Review One by One]│
└─────────────────────────────────────────────┘
```

**Key decisions:**
- We match uploaded products to existing GLASS data using fuzzy matching
- Show diff: what matches, what's different, what's new
- Operator confirms the diff → all corrections applied immediately
- This doubles as GPID training data — operator-confirmed product matches are high-confidence signals

---

## 4. Trust & Verification System

### 4.1 Trust Tiers

| Tier | Who | Trust Score Multiplier | Auto-Apply Threshold | Example |
|------|-----|----------------------|---------------------|---------|
| **T0: Anonymous** | No account, fingerprint only | 0.3x | Never auto-apply | Random visitor reports wrong price |
| **T1: Authenticated** | Logged in with email/Google | 1.0x | 3+ agreeing reports | Registered user reports wrong price |
| **T2: Verified Consumer** | Account with history of accurate reports | 2.0x | 2+ agreeing reports | Power user who's been right 10+ times |
| **T3: Claimed Operator** | Verified dispensary owner/manager | 5.0x (own store), 1.5x (other stores) | Immediate (own store) | Dispensary manager correcting their menu |
| **T4: GLASS Admin** | Internal team | ∞ | Immediate | Manual review override |

### 4.2 Confidence Scoring Algorithm

Each feedback submission gets a confidence score (0.0 - 1.0):

```
confidence = base_score × trust_multiplier × recency_factor × corroboration_factor × source_factor

Where:
  base_score = {
    price_correction: 0.4,      // Prices need verification
    discontinued_product: 0.5,   // Moderate base — could be temporary stockout
    store_closed: 0.3,          // High impact, needs strong verification
    wrong_category: 0.6,        // Usually obvious and correct
    wrong_name: 0.5,            // Usually correct but could be variant confusion
    gpid_match/split: 0.3,      // Complex, needs multiple signals
    store_info: 0.5,            // Usually verifiable
  }
  
  trust_multiplier = user.trust_tier_multiplier  // 0.3 to 5.0 per tier above

  recency_factor = {
    reported_within_1h: 1.0,     // Very recent — likely accurate
    reported_within_24h: 0.9,
    reported_within_7d: 0.7,
    older: 0.5,
  }

  corroboration_factor = {
    1_report: 1.0,
    2_reports: 1.5,
    3+_reports: 2.0,
    5+_reports: 3.0,            // Near-certain at this point
  }

  source_factor = {
    "saw_in_store": 1.2,        // Physical verification
    "saw_on_website": 1.0,
    "not_sure": 0.7,
  }
```

**Auto-apply thresholds:**
- `confidence >= 0.8` → Auto-apply to display layer, log for audit
- `confidence 0.4 - 0.79` → Queue for review (daily review batch)
- `confidence < 0.4` → Store for pattern analysis only

**Operator override:**
- T3 (Claimed Operator) corrections to **their own store** always auto-apply (confidence = 1.0)
- T3 corrections to **other stores** get standard 1.5x multiplier — they know the market but might have motives

### 4.3 Cross-Reference Validation

Before applying a correction, the system checks:

1. **Multi-source check:** If we scrape the same product from Dutchie AND Weedmaps, does the correction align with either source? If the reported price matches another platform's price → confidence +0.3.

2. **Historical reasonableness:** Is the correction within normal range for this product category and market?
   - Price correction within ±30% of current value → normal
   - Price correction >50% different → flag for review regardless of confidence
   - Price correction to $0 or >$500 → auto-reject

3. **Scraper re-verification:** When a high-confidence correction comes in, trigger a priority re-scrape of that specific store. If the new scrape confirms the correction → auto-apply. If scrape contradicts → hold for manual review.

4. **Temporal validation:** If the last scrape was 2 hours ago and a user reports a different price, the user is likely right. If the last scrape was 10 minutes ago and the user disagrees, investigate — our scrape might have caught a real price change.

### 4.4 Trust Score Evolution

Users build trust over time:

```
After each correction is resolved:
  if correction was validated (confirmed by scrape, other users, or operator):
    user.accurate_submissions += 1
    user.trust_score += 1  (up to tier threshold)
  if correction was rejected (contradicted by scrape or other evidence):
    user.inaccurate_submissions += 1
    user.trust_score -= 2  (faster penalty than reward)
  
  accuracy_rate = accurate / (accurate + inaccurate)
  
  Tier thresholds:
    T1 → T2: 5+ accurate submissions AND accuracy_rate > 0.80
    T2 → T1: accuracy_rate drops below 0.60 OR 3+ consecutive rejections
```

### 4.5 Abuse Detection

| Attack Vector | Detection | Response |
|--------------|-----------|----------|
| **Competitor spam** (submitting fake low prices for rivals) | Same user correcting multiple stores' prices downward; price corrections that don't match any known source | Rate limit: max 10 corrections per user per day; flag accounts that only correct one competitor's prices |
| **Troll submissions** | Absurd values ($0, $9999), profanity in text fields, rapid-fire submissions | Auto-reject values outside category norms; cooldown after 3 submissions in 5 minutes |
| **Bot/automated abuse** | Device fingerprint analysis, submission velocity, pattern detection | reCAPTCHA on anonymous submissions after first correction; behavioral anomaly flagging |
| **Well-meaning but wrong** | Confusion between product variants (different sizes), different store locations | Show current data alongside correction form; ask "Are you sure?" for >30% price changes |
| **Operator gaming** (claimed stores manipulating competitor data) | T3 corrections to competitors flagged separately; pattern: operator always reports competitor prices as higher | Alert on T3 cross-store correction patterns; restrict T3 elevated trust to own store only if abuse detected |

---

## 5. Data Pipeline: Feedback → Correction → Model Improvement

### 5.1 Submission Flow

```
User submits correction
    │
    ├── Frontend validates (non-empty, reasonable range, no profanity)
    │
    ├── Store in `feedback` table with initial confidence score
    │
    ├── IF anonymous: set device fingerprint, rate-check
    │   IF authenticated: lookup trust tier, adjust confidence
    │   IF claimed operator (own store): auto-apply, flag as operator_verified
    │
    ├── Calculate confidence score (§4.2 algorithm)
    │
    ├── BRANCH by confidence:
    │   │
    │   ├── HIGH (≥ 0.8): 
    │   │   ├── Apply correction to `display_overrides` table
    │   │   ├── Mark in UI with "Community corrected" badge
    │   │   ├── Trigger priority re-scrape of affected store
    │   │   └── Log for weekly audit
    │   │
    │   ├── MEDIUM (0.4 - 0.79):
    │   │   ├── Add to review queue
    │   │   ├── If similar correction already pending → merge & boost confidence
    │   │   ├── Trigger priority re-scrape
    │   │   └── Email notification to admin (batched daily)
    │   │
    │   └── LOW (< 0.4):
    │       ├── Store in feedback table
    │       ├── Do NOT display or apply
    │       └── Aggregate for pattern analysis
    │
    └── Return "Thanks!" confirmation to user
```

### 5.2 Review Queue

Admin review interface (internal tool, not public):

```
┌──────────────────────────────────────────────────────┐
│  FEEDBACK REVIEW QUEUE — 23 pending                  │
│                                                      │
│  Filter: [All] [Prices] [Products] [Stores] [GPID]  │
│  Sort: [Confidence ↓] [Newest] [Most Reported]       │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │ #1247 — Price Correction (confidence: 0.72)  │    │
│  │ Blue Dream 1/8 at Green Thumb                │    │
│  │ Current: $45.00 → Reported: $35.00           │    │
│  │ Reporter: user_abc (T1, 83% accuracy)        │    │
│  │ Source: "saw in store today"                  │    │
│  │ Last scraped: 14 hours ago                   │    │
│  │ Other sources: Dutchie says $45, WM n/a      │    │
│  │ Re-scrape result: PENDING                    │    │
│  │                                              │    │
│  │ [✓ Apply] [✗ Reject] [⏸ Hold for re-scrape] │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │ #1248 — Store Closed (confidence: 0.65)      │    │
│  │ Bud's Place, Worcester                       │    │
│  │ 3 users reported this in the past week       │    │
│  │ Last scraped: menu returned 0 products       │    │
│  │                                              │    │
│  │ [✓ Mark Closed] [✗ Still Open] [🔍 Verify]  │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### 5.3 Display Override Layer

Corrections don't modify the raw scraped data. Instead, a `display_overrides` table sits between the scraper data and the API response:

```
API Query: "What's the price of Blue Dream at Green Thumb?"

1. Check display_overrides for active override → if exists, return override value
2. If no override, return scraped value from prices table
3. When next scrape runs:
   - If scrape confirms override → remove override (scraper caught up)
   - If scrape contradicts override → flag for review (who's right?)
   - If scrape returns same old value → keep override active
```

This means:
- Raw scraper data is never mutated by user feedback
- Overrides are transparent and auditable
- Overrides auto-expire when the scraper catches up
- We can always "undo" a bad community correction by removing the override

### 5.4 Scraper Feedback Loop

Feedback data improves scraping over time:

**Frequency Adjustment:**
```
For each store:
  error_rate = feedback_corrections_last_30d / total_data_points
  
  if error_rate > 0.10:  // >10% of data gets corrected
    increase_scrape_frequency(store, factor=2x)
    // e.g., daily → twice daily
  
  if error_rate > 0.20:  // >20% corrected — scraper is struggling
    flag_for_parser_review(store)
    // Something systematic is wrong

  if error_rate < 0.02:  // <2% corrected — data is solid
    decrease_scrape_frequency(store, factor=0.5x)
    // Save resources on accurate stores
```

**Parser Improvement:**
```
Aggregate: "For Dutchie stores, prices are reported as wrong 15% of the time 
            when the product has multiple weight options."

Action: → Investigate parser handling of multi-weight products
        → Fix the parser → Re-scrape affected stores → Validate fix

Aggregate: "Weedmaps category is wrong for 8% of edibles."

Action: → Check Weedmaps category mapping logic
        → Adjust parser → Re-scrape
```

**Store Discovery:**
```
User reports: "You're missing [store name] at [address]"

Action: → Search for store on Dutchie, Weedmaps, iHeartJane, Leafly
        → If found: add to slug list, run initial scrape
        → If not found on any platform: store in "manual_discovery" queue
```

### 5.5 GPID Model Training

User GPID feedback becomes training data:

```
User votes: "Blue Dream 3.5g at Store A" == "Blue Dream 1/8 at Store B" → SAME

Training signal:
  positive_pair(product_A_features, product_B_features)
  → Features: normalized_name, brand, weight, category, strain_type

User votes: "Blue Dream 3.5g at Store A" != "Blue Dream CBD 3.5g at Store B" → DIFFERENT

Training signal:
  negative_pair(product_A_features, product_B_features)
  → The "CBD" suffix is a distinguishing feature

After 500+ labeled pairs:
  → Retrain GPID matching model
  → Evaluate against holdout set
  → If accuracy improves: deploy new model
  → Re-run GPID matching across entire product catalog
```

---

## 6. Database Schema

### 6.1 Core Tables

```sql
-- ============================================================
-- FEEDBACK: Individual user submissions
-- ============================================================
CREATE TABLE feedback (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Who submitted
    user_id         UUID REFERENCES users(id),   -- NULL for anonymous
    device_fp       TEXT,                          -- Browser fingerprint for anon dedup
    session_id      TEXT,                          -- For grouping anonymous corrections
    trust_tier      SMALLINT NOT NULL DEFAULT 0,   -- 0-4, snapshot at submission time
    
    -- What entity they're correcting
    entity_type     TEXT NOT NULL,                  -- 'price', 'product', 'operator', 'gpid'
    entity_id       UUID NOT NULL,                 -- FK to prices.id, products.id, operators.id, etc.
    operator_id     UUID REFERENCES operators(id), -- Store context (always present for price/product)
    
    -- The correction
    field           TEXT NOT NULL,                  -- 'price', 'category', 'thc_pct', 'hours', 'status', 'name', etc.
    old_value       TEXT,                           -- What GLASS currently shows (snapshot)
    new_value       TEXT,                           -- What user says it should be
    correction_type TEXT NOT NULL,                  -- 'update', 'delete' (discontinued), 'create' (missing), 'merge', 'split'
    
    -- Context
    source          TEXT,                           -- 'in_store', 'website', 'unsure', 'operator_dashboard', 'bulk_upload'
    details         TEXT,                           -- Free text (optional user note)
    
    -- Scoring
    confidence      DECIMAL(4,3) NOT NULL DEFAULT 0.0,  -- 0.000 to 1.000
    
    -- Resolution
    status          TEXT NOT NULL DEFAULT 'pending',     -- 'pending', 'applied', 'rejected', 'merged', 'expired'
    resolved_at     TIMESTAMPTZ,
    resolved_by     UUID REFERENCES users(id),           -- Admin who reviewed, NULL if auto-applied
    resolution_note TEXT,
    
    -- Validation
    rescrape_confirmed  BOOLEAN,                         -- Did a re-scrape confirm this?
    cross_ref_match     BOOLEAN,                         -- Did another platform confirm?
    
    -- Meta
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    ip_hash         TEXT,                                -- Hashed IP for abuse detection
    user_agent      TEXT
);

-- Indexes for common queries
CREATE INDEX idx_feedback_status ON feedback(status) WHERE status = 'pending';
CREATE INDEX idx_feedback_entity ON feedback(entity_type, entity_id);
CREATE INDEX idx_feedback_operator ON feedback(operator_id);
CREATE INDEX idx_feedback_user ON feedback(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_feedback_created ON feedback(created_at DESC);
CREATE INDEX idx_feedback_confidence ON feedback(confidence DESC) WHERE status = 'pending';


-- ============================================================
-- FEEDBACK_VOTES: Community corroboration on feedback items
-- ============================================================
CREATE TABLE feedback_votes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id     UUID NOT NULL REFERENCES feedback(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES users(id),
    device_fp       TEXT,
    vote            TEXT NOT NULL CHECK (vote IN ('agree', 'disagree')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- One vote per user/device per feedback item
    UNIQUE(feedback_id, user_id),
    UNIQUE(feedback_id, device_fp)
);

CREATE INDEX idx_feedback_votes_feedback ON feedback_votes(feedback_id);


-- ============================================================
-- DISPLAY_OVERRIDES: Active corrections applied to display layer
-- ============================================================
CREATE TABLE display_overrides (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- What's being overridden
    entity_type     TEXT NOT NULL,        -- 'price', 'product', 'operator'
    entity_id       UUID NOT NULL,
    field           TEXT NOT NULL,        -- 'price', 'category', 'thc_pct', etc.
    
    -- Override value
    override_value  TEXT NOT NULL,
    original_value  TEXT,                 -- Snapshot of what was there before
    
    -- Source
    feedback_id     UUID REFERENCES feedback(id),  -- The correction that triggered this
    source          TEXT NOT NULL,                   -- 'community', 'operator', 'admin', 'auto_scrape'
    
    -- Lifecycle
    is_active       BOOLEAN NOT NULL DEFAULT true,
    applied_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,                     -- Auto-expire after 7 days if not confirmed
    superseded_at   TIMESTAMPTZ,                     -- When a new scrape confirmed/replaced this
    superseded_by   TEXT,                             -- 'scrape_confirmed', 'scrape_contradicted', 'newer_override', 'admin_reverted'
    
    UNIQUE(entity_type, entity_id, field) WHERE (is_active = true)
);

CREATE INDEX idx_display_overrides_active ON display_overrides(entity_type, entity_id) WHERE is_active = true;
CREATE INDEX idx_display_overrides_expires ON display_overrides(expires_at) WHERE is_active = true;


-- ============================================================
-- USER_TRUST_SCORES: Track user reliability over time
-- ============================================================
CREATE TABLE user_trust_scores (
    user_id                 UUID PRIMARY KEY REFERENCES users(id),
    
    -- Submission stats
    total_submissions       INTEGER NOT NULL DEFAULT 0,
    accurate_submissions    INTEGER NOT NULL DEFAULT 0,
    inaccurate_submissions  INTEGER NOT NULL DEFAULT 0,
    pending_submissions     INTEGER NOT NULL DEFAULT 0,
    
    -- Computed
    accuracy_rate           DECIMAL(4,3),              -- accurate / (accurate + inaccurate)
    trust_tier              SMALLINT NOT NULL DEFAULT 1, -- 1-4
    trust_score             INTEGER NOT NULL DEFAULT 0,  -- Running score for tier progression
    
    -- Abuse flags
    is_flagged              BOOLEAN NOT NULL DEFAULT false,
    flag_reason             TEXT,
    flagged_at              TIMESTAMPTZ,
    
    -- Specialization (what they correct most)
    primary_correction_type TEXT,                       -- 'prices', 'products', 'stores'
    primary_operator_id     UUID,                      -- Store they correct most (might be their store)
    
    -- Meta
    first_submission_at     TIMESTAMPTZ,
    last_submission_at      TIMESTAMPTZ,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ============================================================
-- OPERATOR_CLAIMS: Dispensary ownership claims
-- ============================================================
CREATE TABLE operator_claims (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operator_id     UUID NOT NULL REFERENCES operators(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    
    -- Verification
    status          TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'verified', 'rejected', 'revoked'
    verification_method TEXT,                          -- 'email_domain', 'phone', 'document', 'manual'
    verification_data   JSONB,                        -- Evidence (redacted after verification)
    
    -- Role
    role            TEXT NOT NULL DEFAULT 'manager',   -- 'owner', 'manager', 'staff'
    
    -- Meta
    claimed_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    verified_at     TIMESTAMPTZ,
    verified_by     UUID REFERENCES users(id),        -- Admin who approved
    revoked_at      TIMESTAMPTZ,
    revoke_reason   TEXT
);

CREATE UNIQUE INDEX idx_operator_claims_active ON operator_claims(operator_id, user_id) 
    WHERE status IN ('pending', 'verified');


-- ============================================================
-- SCRAPER_ERROR_RATES: Aggregate feedback → scraper adjustments
-- ============================================================
CREATE TABLE scraper_error_rates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operator_id     UUID NOT NULL REFERENCES operators(id),
    platform        TEXT NOT NULL,                     -- 'dutchie', 'weedmaps', 'iheartjane', 'leafly'
    
    -- Metrics (rolling 30-day window)
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    total_data_points   INTEGER NOT NULL DEFAULT 0,
    corrections_received INTEGER NOT NULL DEFAULT 0,
    corrections_confirmed INTEGER NOT NULL DEFAULT 0,
    error_rate          DECIMAL(4,3),                  -- corrections_confirmed / total_data_points
    
    -- Action taken
    scrape_frequency_multiplier DECIMAL(3,1) NOT NULL DEFAULT 1.0,  -- 0.5x to 3.0x
    parser_flagged              BOOLEAN NOT NULL DEFAULT false,
    
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    UNIQUE(operator_id, platform, period_start)
);


-- ============================================================
-- GPID_VOTES: Community product matching signals
-- ============================================================
CREATE TABLE gpid_votes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    product_a_id    UUID NOT NULL REFERENCES products(id),
    product_b_id    UUID NOT NULL REFERENCES products(id),
    
    user_id         UUID REFERENCES users(id),
    device_fp       TEXT,
    
    vote            TEXT NOT NULL CHECK (vote IN ('same', 'different')),
    confidence      DECIMAL(4,3),
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Ensure consistent ordering (product_a_id < product_b_id)
    CHECK (product_a_id < product_b_id),
    UNIQUE(product_a_id, product_b_id, user_id)
);

CREATE INDEX idx_gpid_votes_products ON gpid_votes(product_a_id, product_b_id);


-- ============================================================
-- FEEDBACK_AUDIT_LOG: Immutable record of all actions taken
-- ============================================================
CREATE TABLE feedback_audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id     UUID REFERENCES feedback(id),
    action          TEXT NOT NULL,  -- 'submitted', 'auto_applied', 'manually_applied', 'rejected', 'expired', 'reverted'
    actor_type      TEXT NOT NULL,  -- 'user', 'system', 'admin', 'scraper'
    actor_id        TEXT,           -- user_id, 'auto_confidence', 'scraper_confirm', admin user_id
    details         JSONB,          -- Action-specific metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_feedback_audit_feedback ON feedback_audit_log(feedback_id);
CREATE INDEX idx_feedback_audit_created ON feedback_audit_log(created_at DESC);
```

### 6.2 Key Queries

```sql
-- Get pending review queue, highest confidence first
SELECT f.*, 
       u.trust_tier as reporter_trust,
       uts.accuracy_rate as reporter_accuracy,
       COUNT(fv.id) FILTER (WHERE fv.vote = 'agree') as agree_votes,
       COUNT(fv.id) FILTER (WHERE fv.vote = 'disagree') as disagree_votes
FROM feedback f
LEFT JOIN users u ON f.user_id = u.id
LEFT JOIN user_trust_scores uts ON f.user_id = uts.user_id
LEFT JOIN feedback_votes fv ON f.id = fv.feedback_id
WHERE f.status = 'pending'
GROUP BY f.id, u.trust_tier, uts.accuracy_rate
ORDER BY f.confidence DESC, f.created_at ASC;

-- Get active display overrides for a store
SELECT do.*
FROM display_overrides do
WHERE do.entity_type IN ('price', 'product')
  AND do.entity_id IN (SELECT id FROM prices WHERE operator_id = $1)
  AND do.is_active = true;

-- Stores with highest error rates (scraper needs attention)
SELECT o.name, ser.platform, ser.error_rate, ser.corrections_confirmed,
       ser.scrape_frequency_multiplier
FROM scraper_error_rates ser
JOIN operators o ON ser.operator_id = o.id
WHERE ser.period_end >= CURRENT_DATE - INTERVAL '30 days'
  AND ser.error_rate > 0.10
ORDER BY ser.error_rate DESC;

-- GPID consensus (products that users agree are the same)
SELECT product_a_id, product_b_id,
       COUNT(*) FILTER (WHERE vote = 'same') as same_votes,
       COUNT(*) FILTER (WHERE vote = 'different') as different_votes
FROM gpid_votes
GROUP BY product_a_id, product_b_id
HAVING COUNT(*) >= 3
ORDER BY COUNT(*) FILTER (WHERE vote = 'same') DESC;
```

---

## 7. API Endpoints

### 7.1 Consumer Endpoints (Public)

```
POST /api/v1/feedback
  Body: { entity_type, entity_id, field, new_value, source, details, correction_type }
  Auth: Optional (Clerk JWT or anonymous with device fingerprint)
  Rate limit: 10/day anonymous, 30/day authenticated
  Returns: { feedback_id, status: "received", message }

POST /api/v1/feedback/:id/vote
  Body: { vote: "agree" | "disagree" }
  Auth: Optional
  Rate limit: 50/day
  Returns: { total_agrees, total_disagrees }

GET  /api/v1/feedback/entity/:type/:id
  Returns: Active overrides and pending corrections for an entity
  (So the UI can show "Community reports this price is $35" even before it's fully applied)
```

### 7.2 Operator Endpoints (Claimed + Verified)

```
PUT  /api/v1/operator/:operator_id/corrections
  Body: { corrections: [{ entity_id, field, new_value }] }
  Auth: Clerk JWT + verified claim
  Rate limit: 500/day
  Auto-applies: Yes (operator's own store)

POST /api/v1/operator/:operator_id/menu-upload
  Body: CSV/Excel file
  Auth: Clerk JWT + verified claim
  Returns: { matched, new, conflicts, preview_url }

POST /api/v1/operator/:operator_id/rescrape
  Auth: Clerk JWT + verified claim
  Rate limit: 3/day
  Returns: { job_id, estimated_minutes }

PUT  /api/v1/operator/:operator_id/store-info
  Body: { hours, address, phone, status }
  Auth: Clerk JWT + verified claim
  Auto-applies: Yes
```

### 7.3 Admin Endpoints

```
GET  /api/v1/admin/feedback/queue
  Query: status, entity_type, min_confidence, sort_by
  Auth: Admin API key
  Returns: Paginated list of pending feedback with context

POST /api/v1/admin/feedback/:id/resolve
  Body: { action: "apply" | "reject" | "hold", note }
  Auth: Admin API key

GET  /api/v1/admin/feedback/stats
  Returns: { pending_count, applied_today, rejected_today, avg_confidence, 
             top_corrected_stores, error_rate_by_platform }

GET  /api/v1/admin/scraper/error-rates
  Returns: Per-store, per-platform error rates with frequency recommendations
```

---

## 8. Competitive Moat Analysis

### 8.1 The Flywheel Effect

```
More consumers use GLASS
    → More corrections submitted
        → Data becomes more accurate than scrapers alone
            → Consumer trust increases ("GLASS is always right")
                → More consumers use GLASS
                    → More corrections submitted
                        → ...
```

At scale, this creates data quality that is **structurally impossible** for scraper-only competitors to match. No amount of proxy spending or parser optimization produces human-verified accuracy.

### 8.2 Why Competitors Can't Copy This

| Advantage | Why It's Defensible |
|-----------|-------------------|
| **Community corrections** | Network effect — corrections from 50K users > corrections from 500. Starting later means permanently less accurate data. |
| **Operator engagement** | Once a dispensary claims their page and corrects data weekly, switching cost is real. Their data history, trust score, and correction patterns are locked in. |
| **GPID matching from users** | Community-labeled product pairs are training data for matching models. More labels = better model = better matches = more useful comparisons = more users. |
| **Scraper feedback loop** | Every correction teaches our scraper what it gets wrong. Over time, the scraper improves AND the community catches what the scraper misses. Dual-layer accuracy. |
| **Trust scoring** | Our system knows which users are reliable. A new competitor starts with zero trust data. We know that user_abc has been right 94% of the time across 200 corrections — their signal is gold. |
| **Historical correction data** | "This store's prices are corrected 3x more often on Fridays" — patterns that only emerge from months of data. |

### 8.3 The Wikipedia Analogy

Wikipedia's moat isn't its software (MediaWiki is open-source). It's the **accumulated corrections, editorial standards, and contributor community** that took 20+ years to build. GLASS's feedback system is the same play for cannabis pricing data:

- Anyone can scrape prices (software)
- Nobody else has 50K consumers verifying those prices daily (community)
- Nobody else has 200+ dispensaries actively maintaining their listings (operators)
- Nobody else has 6 months of correction history feeding ML models (data)

### 8.4 Moat Maturation Timeline

| Timeframe | Moat Strength | What's Happening |
|-----------|---------------|-----------------|
| Month 1-2 | Weak | Few corrections, mostly manual review. Data quality = scraper quality. |
| Month 3-6 | Growing | Enough corrections to auto-apply high-confidence ones. Operators claiming pages. Error rate dropping. |
| Month 6-12 | Moderate | GPID matching benefiting from user votes. Scraper frequency optimized per store. Consumer trust visibly higher than alternatives. |
| Year 1-2 | Strong | Community corrections > scraper volume for certain data types. GPID model trained on thousands of user-labeled pairs. Dispensaries dependent on GLASS for their public pricing narrative. |
| Year 2+ | Very Strong | Self-reinforcing. Data quality gap vs. competitors widens over time, not narrows. |

---

## 9. Implementation Phases

### 9.1 Week 1 MVP — "Report Wrong Price" Button

**Goal:** Collect feedback. Learn what users actually report. Manual review only.

**Build:**
- [ ] `feedback` table in PostgreSQL (schema above, simplified — just id, entity_type, entity_id, field, old_value, new_value, source, status, device_fp, created_at)
- [ ] `POST /api/v1/feedback` endpoint — accepts corrections, stores in DB, no auth required
- [ ] "⚑ Wrong price?" link on every price display in the consumer site
  - Tap → inline form: price input + source radio (in-store / website / unsure)
  - Submit → POST to API → toast "Thanks! We'll verify this."
- [ ] Device fingerprint via FingerprintJS (free tier) for anonymous dedup
- [ ] Rate limiting: max 10 submissions per device per day
- [ ] Basic validation: price > 0, price < $500, not identical to current value
- [ ] Admin email notification: daily digest of new corrections (Resend or simple cron → email)
- [ ] Manual review: Randy checks corrections against live menus, applies valid ones by hand

**Not building yet:** Trust scoring, auto-apply, operator features, GPID voting, review dashboard.

**Success criteria:** >20 corrections in the first week. If users actually report wrong prices, the thesis is validated.

**Estimated effort:** 1 developer day (frontend + API endpoint + DB migration).

### 9.2 Month 1 — Trust Scoring + Operator Claims + Auto-Apply

**Goal:** Automate the easy corrections. Get dispensaries engaged.

**Build:**
- [ ] `display_overrides` table — the override layer between scraped data and API responses
- [ ] `user_trust_scores` table + basic scoring logic
- [ ] `operator_claims` table + "Claim Your Page" flow (name, email, phone verification)
- [ ] Confidence scoring algorithm (§4.2)
- [ ] Auto-apply for high-confidence corrections (≥ 0.8)
- [ ] Operator dashboard: inline price editing, store info editing, "product discontinued" toggle
- [ ] Operator corrections auto-apply to own store (bypass review)
- [ ] "Community corrected" badge on overridden prices in consumer UI
- [ ] "Last updated" + "Verified by [community/operator]" labels on all prices
- [ ] Admin review queue (simple table view, approve/reject buttons)
- [ ] General "Report Issue" flow (Flow 2 — multi-issue reporting on products)
- [ ] "Suggest an edit" flow for store info (Flow 3)
- [ ] "Was this helpful?" thumbs up/down on comparison results
- [ ] Priority re-scrape trigger: when high-confidence correction comes in, scrape that store next

**Success criteria:** 
- 5+ dispensaries claim their page
- 50+ corrections auto-applied
- Error rate (community-reported) decreasing week over week

**Estimated effort:** 2-3 developer weeks.

### 9.3 Month 3+ — GPID Assist + Scraper Learning + Full Feedback Loop

**Goal:** Community intelligence feeds back into every layer of the data pipeline.

**Build:**
- [ ] `gpid_votes` table + GPID matching UI (Flow 4 — "Same product? / Different product?")
- [ ] `scraper_error_rates` table + automated frequency adjustment
- [ ] `feedback_audit_log` table for full audit trail
- [ ] Operator bulk menu upload (Flow 7 — CSV/Excel with preview and diff)
- [ ] Abuse detection system:
  - Flag users with >30% rejection rate
  - Detect competitor-targeting patterns
  - Rate limit escalation (captcha after multiple corrections)
- [ ] Scraper frequency adjustment: stores with high error rates get scraped 2x more often
- [ ] Parser improvement queue: aggregate error patterns → flag specific parser issues
- [ ] GPID model retraining pipeline (batch: collect labeled pairs → retrain → evaluate → deploy)
- [ ] User notifications: "Your correction was applied!" / "Thanks for helping — you're now a Verified Contributor"
- [ ] Leaderboard (optional): top contributors, most active verifiers
- [ ] Store discovery from feedback: "Missing dispensary" reports → automatic slug discovery attempt
- [ ] Cross-reference validation: check corrections against other platforms before applying
- [ ] Override expiration: auto-expire overrides after 7 days if not confirmed by scraper or operator
- [ ] Weekly data quality report: automated email to admin with correction trends, error hotspots, scraper health

**Success criteria:**
- GPID matching accuracy improves measurably from user votes
- Scraper frequency adjustments reduce correction volume by >20%
- <5% of auto-applied corrections are later reverted

**Estimated effort:** 4-6 developer weeks (can be incremental, not a big bang).

---

## 10. Anti-Abuse & Edge Cases

### 10.1 Abuse Scenarios and Mitigations

| Scenario | Example | Detection | Mitigation |
|----------|---------|-----------|------------|
| **Competitor manipulation** | Store A submits artificially high prices for Store B to make themselves look cheaper | Single user correcting same competitor repeatedly; corrections always in one direction (higher) | Flag accounts that disproportionately correct a single competitor; require corroboration for corrections >20% change |
| **Operator self-promotion** | Claimed operator lowers their own price in GLASS without actually lowering it in-store | Consumer reports "this corrected price is also wrong"; re-scrape contradicts operator | If re-scrape contradicts operator correction 2+ times: flag account, require supporting evidence |
| **Rage reporting** | Disgruntled customer reports everything at a store as wrong | Burst of corrections from one user targeting one store | Rate limit per-store: max 5 corrections per user per store per day; human review if all 5 submitted |
| **Price war gaming** | Two dispensaries using GLASS corrections to signal price wars (correcting to lower and lower prices) | Rapid back-and-forth corrections on same products between claimed operators | Alert admin on correction ping-pong (>3 corrections to same product in 48h) |
| **Honest confusion** | User reports "wrong price" but they're looking at a different size/variant | Correction is close to another variant's actual price | Show all variants when user reports wrong price: "Which size are you looking at?" |
| **Stale correction** | User reports price from last week, store already updated | Correction matches old data, not current | Timestamp on correction form: "When did you see this price?" + cross-reference with scrape history |
| **Bot/spam** | Automated submissions to pollute data | High velocity, consistent patterns, unusual user agents | reCAPTCHA on 3rd anonymous submission; device fingerprint dedup; IP-based rate limiting |

### 10.2 Edge Cases

**Edge Case: Conflicting corrections**
Two users report different "correct" prices for the same product.
→ **Resolution:** Neither auto-applies. Both go to review queue with a "conflicting" flag. Trigger re-scrape. If re-scrape matches either, apply that one and credit the correct reporter.

**Edge Case: Operator and community disagree**
Operator says price is $38, three consumers say it's $35.
→ **Resolution:** Operator wins for their own store (they know their menu). BUT: if consumer corrections persist after operator correction, flag for admin — the operator might be gaming (showing old price, selling at different price).

**Edge Case: Store has different prices on different platforms**
Dutchie says $40, Weedmaps says $35, user says "it's $35 in store."
→ **Resolution:** Display the in-store price as the canonical price. Add a note: "Online price may differ." Feed this back to the scraper: which platform matches in-store pricing? Prefer that platform's data.

**Edge Case: Product variant confusion**
"Blue Dream" comes in 1g, 3.5g, 7g, 14g, 28g. User reports "wrong price" but is looking at a different weight.
→ **Resolution:** The correction form should show all available variants for the product at that store. "Which one are you looking at?" Reduces false corrections by 30%+ (estimated from similar systems).

**Edge Case: Recreational vs. Medical pricing**
Some stores have different prices for rec and medical customers. User reports "wrong" but they're seeing the other price tier.
→ **Resolution:** Display both price tiers where available. Correction form asks: "Are you a recreational or medical customer?" Route correction to correct price tier.

**Edge Case: Tax-inclusive vs. tax-exclusive**
MA cannabis has ~20% effective tax. Some menus show pre-tax, some post-tax. User confusion is guaranteed.
→ **Resolution:** Always display pre-tax pricing (match menu source). Add visible note: "Price before tax. Estimated total: $X.XX." Accept corrections to either and normalize.

### 10.3 Privacy Considerations

- **Anonymous submissions:** No PII stored. Device fingerprint is a hash, not identifiable.
- **Authenticated submissions:** User ID linked to correction. Visible to admins only, never publicly displayed.
- **Operator claims:** Verification data (email, phone, documents) encrypted at rest. Redacted after verification is complete. Only the claim status and role are retained.
- **IP addresses:** Hashed before storage. Used only for rate limiting and abuse detection, never exposed.
- **GDPR/CCPA-style rights:** Users can request deletion of all their feedback data. Corrections that were already applied to the display layer are kept (de-linked from user) — similar to how Wikipedia keeps edits when a user account is deleted.

---

## 11. Metrics & Monitoring

### 11.1 Health Metrics (Track from Day 1)

| Metric | Target (Month 1) | Target (Month 3) | Target (Month 6) |
|--------|------------------|------------------|------------------|
| Total corrections submitted | 50+ | 500+ | 2,000+ |
| Corrections per day | 2-5 | 15-25 | 50-100 |
| % auto-applied | 0% (manual only) | 30-40% | 50-60% |
| Avg time to resolution | 24h (manual) | 4h (mixed) | 1h (mostly automated) |
| Corrections that are accurate (post-validation) | >70% | >80% | >85% |
| Operator claims | 0 | 10+ | 50+ |
| Operator corrections/week | 0 | 20+ | 100+ |
| GPID votes collected | 0 | 50+ | 500+ |
| Stores with >10% error rate | Unknown | <20% | <10% |

### 11.2 Alerts

- **New corrections spike:** >3x daily average → something happened (scraper broke, store had a sale, viral post drove traffic to a store page with bad data)
- **Auto-apply accuracy drops:** If >10% of auto-applied corrections are reverted/overridden → tighten thresholds
- **Operator claim surge:** >5 claims in one day → could be organic growth or could be an outreach response — capitalize either way
- **Zero corrections for 3 days:** Feedback system might be broken or UX is buried — investigate

---

## 12. Summary: The 3 Things That Matter

1. **Week 1: Ship "Wrong price?" and learn.** Don't over-build. A button, an API endpoint, and a database table. See what users actually report. Learn from real data before building trust scoring or auto-apply.

2. **Month 1: Let operators own their data.** The moment a dispensary claims their page and starts correcting prices, they're invested in GLASS. This is the B2B engagement hook that drives premium subscriptions. Their corrections are also the highest-quality data we can get.

3. **Month 3+: Close the loop.** Corrections feed back into scraper frequency, parser improvements, and GPID matching. The system gets smarter over time, not just more populated. This is the moat that compounds.

**The feedback system isn't a feature. It's the mechanism that turns GLASS from "a scraper with a UI" into "the community source of truth for Massachusetts cannabis pricing."**

---

*Every correction is a gift from a user who cares enough to make GLASS better. Treat it that way — fast acknowledgment, visible impact, and zero friction. If reporting a wrong price is harder than ignoring it, the system fails.*
