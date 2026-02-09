# Lead Tool

**Code Repo:** `/Users/randytorres/Projects/claude/projects/lead-tool`

## Overview
Python-based lead qualification system for Massachusetts cannabis operators. **Fully working** - identifies operators under buying pressure using a 3-layer signal model.

**Status:** Production-ready for MA market intelligence

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 (pure stdlib, no pip dependencies) |
| Storage | SQLite (`leads.db`) |
| Geocoding | OpenStreetMap Nominatim (free, rate-limited) |
| Data Source | MA Cannabis Control Commission Open Data API |
| Visualization | Leaflet.js map (`map.html`) |
| Export | CSV, GeoJSON |

---

## Current Capabilities

### Working Features ✅

**Data Collection**
- Fetches MA CCC license data (2 API endpoints)
- 1,693 total licensed entities → filters to ~750 relevant (Cultivators, Manufacturers, Microbusinesses)
- Retry logic with exponential backoff
- Cross-references commenced operations data

**3-Layer Signal Model**
| Layer | Signal Type | Meaning |
|-------|-------------|---------|
| 1 | Structural Fit | Cultivator, Manufacturer, or Microbusiness |
| 2 | Pressure Signals | Licensed but not operating, stalled 12+ months, ramping up |
| 3 | Capacity Mismatch | Cultivation without manufacturing, manufacturing without cultivation, capacity-limited |

**Bucket Triage**
- **Bucket A (Immediate):** Pressure + capacity signals → 45 leads ready for calls
- **Bucket B (Watchlist):** Pressure only OR 2+ capacity signals → 48 leads for soft outreach
- **Bucket C (Ignore):** Structural fit only → 146 leads (background noise)

**Data Collected (31 fields)**
- Business name, license number, type, status
- Contact info: email, phone, address, city
- 7 signal flags with weighted scoring
- "Why Now" talking point for each lead
- Brand routing tags (AC_candidate, CH_candidate, HOP_candidate)
- Suspected buyer type (toll_rolling, bulk_material, contract_production)
- Geocoded lat/long coordinates

**Outputs**
- `leads.db` - SQLite database with full schema
- `leads.geojson` - 204 geocoded features
- `map.html` - Interactive Leaflet map with 3 viewing modes
- `ac_market_intel_YYYY-MM-DD.csv` - CRM-ready export

**Map Features**
- 3 visualization modes: Pressure, Opportunity Type, Brand Fit
- Marker sizing by signal strength
- Zone clustering (15-mile radius opportunity zones)
- Click popups with contact info + talking points
- Toggle filters for Bucket C

---

## Usage

```bash
python3 signals_pack_export.py --output-dir ./output --limit 150
```

**Runtime:** ~1-2 minutes (geocoding is rate-limited to 1 req/sec)

**Output:**
```
🌿 AC Market Intelligence Engine - Massachusetts v3.0

📄 TRIAGE RESULTS
🔴 Bucket A (Immediate):   45 leads → Call today
🟡 Bucket B (Watchlist):   48 leads → Soft outreach
⚪ Bucket C (Ignore):     146 leads → Don't waste time

🗺️  Geocoding leads...
   • Already geocoded (cached): 204
   • Need geocoding: 35
```

---

## Key Numbers (Last Run: Dec 29, 2025)

| Metric | Count |
|--------|-------|
| MA licensed entities | 1,693 |
| Structurally fit | 750 |
| Total with signals | 239 |
| Bucket A (immediate) | 45 (18.8%) |
| Bucket B (watchlist) | 48 (20.1%) |
| Bucket C (ignore) | 146 (61.1%) |
| Geocoded | 204/239 (85%) |

---

## Data Quality

**Known Limitations:**
- Self-reported data (typos/staleness possible)
- ~20% missing email or phone
- ~40% missing cultivation tier (mostly manufacturers)
- 35 leads couldn't be geocoded (invalid addresses)
- Massachusetts only (hardcoded)

---

## Not Yet Implemented

- [ ] Multi-state support (other CCC APIs)
- [ ] Social media / web presence signals
- [ ] Email/outreach automation
- [ ] CRM integration (Salesforce/HubSpot/Apex)
- [ ] Slack notifications
- [x] ~~Real-time change detection (tier changes, new licenses)~~ → See `change_log.py`
- [x] ~~Contact validation (email/phone verification)~~ → See `contact_merge.py`
- [ ] Enrichment (Apollo, Hunter, BuiltWith)

---

## Phase 1 Tools (Added Feb 2026)

### 1. Signals Pack Export (`signals_pack_export.py`)
Generate a curated list of Top 150 distressed operators for outreach.

```bash
python3 signals_pack_export.py --output-dir ./output --limit 150
```

**Output:**
- `ma_operator_signals_pack_YYYY-MM-DD.csv` - Top 150 operators with contacts, signals, talk tracks
- `signals_pack_readme.txt` - Market context and usage notes

### 2. Margin Pressure Snapshot (`snapshot_generator.py`)
Generate 1-page snapshot data for individual operators.

```bash
# Single operator
python3 snapshot_generator.py --name "Business Name" --output-dir ./output/snapshots

# Batch mode
python3 snapshot_generator.py --input targets.csv --output-dir ./output/snapshots
```

**Output:**
- JSON snapshots with market context, pressure signals, likely leaks, fast wins
- CSV batch export for CRM integration

### 3. Contact Merge (`contact_merge.py`)
Merge verified contact data into lead files.

```bash
python3 contact_merge.py --leads leads.csv --contacts clean-contacts.csv --output enriched.csv
```

**Adds columns:**
- `contact_email_verified`, `contact_phone_verified`
- `contact_confidence` (0-1 score)
- `contact_match_method` (exact/fuzzy/name+city)

### 4. Distress Scoring (in `unified_intel.py`)
Added `distress_score` calculation weighting:
- Stalled operations (up to 60 points)
- Pressure signals (10 points each)
- Capacity mismatches (15 points each)
- Bucket boost (A: 20, B: 10)

**Output:**
- `distressed_top_100_YYYY-MM-DD.csv` - Top 100 operators by distress score

### 5. Change Log (`change_log.py`)
Track weekly changes in CCC license data.

```bash
# Save snapshot
python3 change_log.py --snapshot-only

# Generate delta report
python3 change_log.py

# Compare to specific date
python3 change_log.py --compare 2026-01-01
```

**Tracks:**
- New licenses issued
- Status changes (Active → Expired, etc.)
- Commenced operations
- Cultivation tier changes

---

## Integration Opportunities

**This tool feeds into:**
- AC wholesale sales efforts (Bucket A = call today)
- Cue onboarding prospects (manufacturers needing sell-through)
- Geographic planning (cluster analysis for pop-ups)

**Could integrate with:**
- Apex CRM - route hot leads
- Email tools - light outreach sequences
- Slack - new Bucket A lead notifications
