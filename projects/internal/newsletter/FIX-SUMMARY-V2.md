# Fix Summary V2 — Newsletter Pipeline P0 Blockers

Date: 2026-02-12

## ✅ Completed Fixes

### 1) P0: Removed hardcoded DB credentials
- **File:** `scrapers/glass_data_processor.py`
- Replaced hardcoded fallback credential with required env var:
  - `DATABASE_URL = os.environ.get("DATABASE_URL")`
  - Raises `ValueError("DATABASE_URL environment variable is required")` when missing.
- Updated DB connection to use `DATABASE_URL` only.

### 2) P0: Fixed events to future-only and regenerated events data
- **File:** `scrapers/events_scraper.py` already contained future-date filtering; re-ran scraper to regenerate data.
- **Regenerated:** `data/events_upcoming.json`
- Verification: current events file contains only future events (`past=0`).
- Added defense-in-depth in composer:
  - **File:** `composer.py` (`select_events`)
  - Now filters out past events even if stale data slips in.

### 3) P0: Added MA-only filtering to License Watch
- **File:** `composer.py` (`extract_license_news`)
- Added filtering so License Watch only includes MA-relevant items:
  - Blocks known bad/non-MA domains
  - Requires MA keywords in title/content before inclusion
- Result in new draft: no NY/non-MA leak-through in License Watch.

## ✅ Data Quality Fixes

### 4) Fixed mislabeled "Brand Movers"
- **Decision:** The GLASS `products.brand` values are effectively strain-like labels in this dataset.
- Implemented rename to strain framing:
  - **Processor output structure updated:** `top_strains`, `total_strains_tracked`
  - **File:** `scrapers/glass_data_processor.py` (`fetch_strain_movers`)
  - **Composer section renamed:** `### 🌿 STRAIN MOVERS`
  - **File:** `composer.py` (`format_brand_movers` now renders strain wording)
  - **Contract updated:** `data_contract.py` GLASS schema now expects strain keys.

### 5) Fixed inflated "new dispensaries" count
- **File:** `scrapers/glass_data_processor.py` (`fetch_threat_radar`)
- New-operator queries now:
  - limit to last 7 days
  - exclude inferred initial bulk-import day (largest historical import day by record count)
- Result in regenerated data/draft: count reduced from inflated values to realistic weekly detection.

### 6) Added missing dependencies
- **File:** `requirements.txt`
- Added:
  - `psycopg2-binary>=2.9.9,<3.0.0`
  - `openai>=1.0.0,<2.0.0`

## ▶️ Runs Performed

1. Regenerated GLASS data:
```bash
DATABASE_URL="..." python3 scrapers/glass_data_processor.py --output ./data/glass_data.json
```
Status: success.

2. Regenerated events data:
```bash
python3 scrapers/events_scraper.py --output ./data/events_upcoming.json --days 30
```
Status: success.

3. Composed new test draft:
```bash
python3 composer.py --data-dir ./data --output ./drafts/newsletter_2026-02-12_test
```
Status: success.

## 🔎 Verification Against Requested Checks

- **No past-dated events:** ✅
- **No NY/non-MA license leak-through:** ✅
- **Strains section properly labeled:** ✅ (`STRAIN MOVERS`)
- **No hardcoded credentials in source:** ✅
- **New dispensary count adjusted to avoid initial bulk import inflation:** ✅

## Note on full `pipeline.py` run
- Attempted full pipeline execution with `DATABASE_URL`, but run stalled on network-bound stages in this environment.
- To ensure deliverable correctness, required artifacts were regenerated directly (GLASS + events + compose), and the resulting draft reflects all requested fixes.
