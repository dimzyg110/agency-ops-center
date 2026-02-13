# Dutchie Failure Investigation + Fix (2026-02-13)

## Scope
Investigated the Feb 12 Dutchie run failures and patched `scripts/scrape-dutchie.ts` + `scripts/lib/parser.ts`.

---

## 1) Failing run identified
Using Railway DB (`scrape_runs`):

- **Run ID:** `dd81f57a-b8b3-4298-b5b1-31273db646d8`
- **Started:** `2026-02-12 04:07:22+00`
- **Completed:** `2026-02-12 10:54:55+00`
- **Attempted:** 235
- **Succeeded:** 195
- **Failed:** 40

All 40 failed `scrape_jobs` had error text equivalent to:
- `...: 0 products found across all categories`

---

## 2) Failure categorization
### DB-level categories (from job error messages)
- **Empty menu (reported):** 40/40
- Timeout: 0
- Age gate: 0
- Browser crash: 0
- Parse exception: 0

### Snapshot-level root cause (from raw snapshots)
I analyzed failed snapshots in `/data/workspace/projects/glass/src/scripts/raw-snapshots/2026-02-12/`.

- **39/40 stores:** product rows are present (`parsedCount > 0`) but `normalizedCount = 0`.
- **1/40 store (`referral`):** truly empty (`rawRows = []` across all categories).

This means most failures were **false negatives** caused by normalization/pricing, not real empty menus.

### Why normalizedCount was 0
`normalizeProduct` keeps only items where `price > 0`, but parser price extraction relied on **button text only**.
Many Dutchie stores now expose button text as just `"Add to cart"` (no `$`), so price stayed undefined and all rows were filtered out.

Observed patterns in failed snapshots:
- rows visible, parsed, but no button prices
- some stores have price tokens only in product/link text (`"5 for $35"`, etc.)

---

## 3) Today’s running scrape cross-check
From `/tmp/dutchie-scrape-20260213-1328.log` (in-progress):

Current `products:0` stores include:
- alternative-therapies-group-amesbury
- alternative-therapies-group-salem
- alternative-therapies-group-salisbury
- ayr-dispensary-back-bay
- ayr-dispensary-watertown

These overlap with Feb 12 failures and match the same symptom pattern (categories parsed > 0, products stored = 0).

---

## 4) Code fixes made

### A) Parser fallback for price extraction
**File:** `scripts/lib/parser.ts`

- Updated `parsePriceButton()` to:
  1. parse price from button text first (existing behavior)
  2. if missing, fallback to `linkText` for `$xx` patterns
- Updated call site to pass both `buttonText` and `linkText`.

This recovers pricing on stores where Dutchie hides price from button labels but includes it in the card/link text.

### B) No-menu detection in Dutchie scraper
**File:** `scripts/scrape-dutchie.ts`

- Added `isLikelyNoMenu(snapshot)` (Weedmaps-style early detection) with markers such as:
  - `menu not available`
  - `no products available`
  - `currently unavailable`
  - `this dispensary is not accepting orders`
  - `this location is closed` / `store is closed`
  - `medical only`
- Applied detection per-category after snapshot capture; if hit, mark category and break early.

### C) Prevent false store failure when products exist but pricing is unavailable
**File:** `scripts/scrape-dutchie.ts`

- Changed `zeroAcrossAllCategories` logic to use **parsed product presence** (`parsedCount`) instead of normalized-priced rows.
- If parsed products exist but priced rows are zero, store now records warning:
  - `products detected but no prices parsed from snapshot`
- Store is no longer auto-failed in this scenario.

### D) Age gate hardening
**File:** `scripts/scrape-dutchie.ts`

- Added `pool.handleAgeGate(tabId)` after each category navigation, not just initial page load.

---

## 5) Expected impact
- The 39 false-empty stores should no longer be marked as failed solely due to missing button-price text.
- Truly empty/no-menu stores (e.g., `referral`) are now detected explicitly and classified earlier.
- Better diagnostics for partial extraction (products present, pricing unavailable).

---

## 6) Files changed
- `/data/workspace/projects/glass/src/scripts/lib/parser.ts`
- `/data/workspace/projects/glass/src/scripts/scrape-dutchie.ts`
