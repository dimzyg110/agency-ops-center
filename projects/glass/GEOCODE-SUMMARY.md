# GEOCODE SUMMARY

## Run Metadata
- Date (UTC): 2026-02-12
- Script: `/data/workspace/projects/glass/src/scripts/geocode-operators.ts`
- Database: Railway Postgres (`operators` table)
- API: Google Maps Geocoding API

## Before
- Total operators: **492**
- With coordinates: **10**
- Missing coordinates: **482**

## Processing Results
- Total operators processed (missing at start): **482**
- Successfully geocoded and updated: **480**
- Failed: **2**
  - Reason: missing usable city (`city = 'Unknown'`) for both records

Failed operator IDs:
- `4b3b6eec-65ec-4e1d-91d7-0da15c1a6233` (`New Operator`)
- `1b7d94a2-c3af-4ae3-96fb-846ec84d7c5a` (`New Operator`)

## After Verification
- Total operators: **492**
- With coordinates: **490**
- Still missing coordinates: **2**

Coordinate distribution:
- Min latitude: `41.26183750`
- Max latitude: `42.87443390`
- Min longitude: `-73.69178510`
- Max longitude: `-69.98380120`

Out-of-range check query (`lat < 40 OR lat > 44 OR lon < -74 OR lon > -69`):
- **0 rows**

## Out-of-Bounds (MA heuristic) During Script
Flagged by script using MA heuristic bounds (`lat 41.2-42.9`, `lon -73.5 to -69.9`):
1. `420 Bliss / Just A Little Higher - Troy` (city: `pittsfield`) → `42.7284117, -73.6917851` (Troy, NY)
2. `Wilde Roots Dispensary` (city: `great-barrington`) → `42.5419142, -73.6660468` (Castleton-On-Hudson, NY)

## Sample Updated Results
- `Zen Leaf - Ashford` | brimfield | `42.12254820, -72.20050590`
- `Zen Leaf - Sharon` | abington | `42.11801320, -71.23459500`
- `Zen Leaf Plymouth` | barnstable | `41.95677930, -70.70790910`
- `Zahara Cannabis` | attleboro | `41.91964170, -71.32468460`
- `Your Green Thumb` | merrimac | `42.83405820, -71.00055090`

## Notes
- Request pacing used: ~200ms between requests (~5 req/sec).
- Fallback query logic used when primary query returned no result.
- Full execution log: `/data/workspace/projects/glass/geocode-run.log`
