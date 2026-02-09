#!/usr/bin/env python3
"""
Google Places Verification Agent for Lead Tool Phase 2

Enriches CCC license data with Google Places information:
- Business operational status
- Star ratings and review counts
- Review velocity tracking (week-over-week change)

Usage:
    python google_places_agent.py [--input FILE] [--output FILE] [--dry-run]

Environment:
    GOOGLE_PLACES_API_KEY - Required for live API calls (not needed for --dry-run)
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Constants
DEFAULT_INPUT = "output/signals_pack_enriched.csv"
DEFAULT_OUTPUT_DIR = "output"
CACHE_FILE = "data/places_cache.json"
API_BASE_URL = "https://places.googleapis.com/v1/places:searchText"
MAX_REQUESTS_PER_SECOND = 10
REQUEST_DELAY = 1.0 / MAX_REQUESTS_PER_SECOND  # 0.1 seconds between requests
# Retry cap for rate-limit responses to avoid unbounded recursion
MAX_RETRIES = 3


def load_cache(cache_path: str) -> dict:
    """
    Load the places cache from disk.
    
    Cache structure:
    {
        "business_key": {
            "place_id": "ChIJ...",
            "status": "operational",
            "rating": 4.5,
            "review_count": 142,
            "last_verified": "2026-02-01T12:00:00",
            "history": [
                {"date": "2026-01-25", "review_count": 138},
                {"date": "2026-02-01", "review_count": 142}
            ]
        }
    }
    """
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARN] Could not load cache: {e}")
    return {}


def save_cache(cache: dict, cache_path: str) -> None:
    """Save the places cache to disk."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def make_cache_key(business_name: str, city: str) -> str:
    """Generate a consistent cache key from business name and city."""
    return f"{business_name.lower().strip()}|{city.lower().strip()}"


def search_google_places(
    business_name: str,
    city: str,
    api_key: str,
    state: str = "Massachusetts"
) -> Optional[dict]:
    """
    Search Google Places API for a business.
    
    Uses the new Places API (v1) Text Search endpoint.
    
    Args:
        business_name: Name of the business
        city: City where business is located
        api_key: Google Places API key
        state: State (defaults to Massachusetts)
    
    Returns:
        Dict with place details or None if not found
    """
    # Build search query
    query = f"{business_name} {city} {state}"
    
    # Request body for Places API v1
    request_body = {
        "textQuery": query,
        "maxResultCount": 1,
        "languageCode": "en"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.businessStatus,places.rating,places.userRatingCount,places.regularOpeningHours"
    }
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                API_BASE_URL,
                data=json.dumps(request_body).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                
                if "places" in data and len(data["places"]) > 0:
                    place = data["places"][0]
                    return {
                        "place_id": place.get("id", ""),
                        "name": place.get("displayName", {}).get("text", ""),
                        "status": normalize_status(place.get("businessStatus", "UNKNOWN")),
                        "rating": place.get("rating"),
                        "review_count": place.get("userRatingCount", 0),
                        "has_hours": "regularOpeningHours" in place
                    }
                return None
                
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                # Exponential backoff to respect rate limits
                backoff_seconds = 2 ** attempt
                print(f"[RATE LIMIT] Sleeping {backoff_seconds}s before retry {attempt + 1}/{MAX_RETRIES}...")
                time.sleep(backoff_seconds)
                continue
            if e.code == 403:
                print(f"[ERROR] API key invalid or quota exceeded: {e}")
                return None
            print(f"[ERROR] HTTP {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"[ERROR] Network error: {e.reason}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return None
    
    return None


def normalize_status(google_status: str) -> str:
    """Convert Google's business status to our simplified format."""
    status_map = {
        "OPERATIONAL": "operational",
        "CLOSED_TEMPORARILY": "closed_temp",
        "CLOSED_PERMANENTLY": "closed_perm",
        "UNKNOWN": "unknown"
    }
    return status_map.get(google_status, "unknown")


def generate_dry_run_data(business_name: str, city: str) -> dict:
    """Generate mock data for dry-run mode."""
    import hashlib
    
    # Use hash for deterministic but varied mock data
    h = hashlib.md5(f"{business_name}{city}".encode()).hexdigest()
    rating = 3.0 + (int(h[:2], 16) % 20) / 10  # 3.0 to 4.9
    reviews = 10 + (int(h[2:4], 16) % 500)  # 10 to 509
    
    statuses = ["operational", "operational", "operational", "closed_temp", "unknown"]
    status_idx = int(h[4:6], 16) % len(statuses)
    
    return {
        "place_id": f"DRY_RUN_{h[:12]}",
        "name": business_name,
        "status": statuses[status_idx],
        "rating": round(rating, 1),
        "review_count": reviews,
        "has_hours": True
    }


def calculate_velocity(cache_entry: dict, current_count: int) -> Optional[int]:
    """
    Calculate review velocity (change since last recorded count).
    
    Returns the difference in review count, or None if no history.
    """
    if not cache_entry or "review_count" not in cache_entry:
        return None
    
    prev_count = cache_entry.get("review_count", 0)
    if prev_count and current_count:
        return current_count - prev_count
    return None


def process_businesses(
    input_path: str,
    output_path: str,
    cache_path: str,
    api_key: Optional[str],
    dry_run: bool = False,
    limit: Optional[int] = None
) -> None:
    """
    Main processing loop: read CSV, lookup each business, write enriched output.
    """
    # Load cache
    cache = load_cache(cache_path)
    print(f"[INFO] Loaded cache with {len(cache)} entries")
    
    # Read input CSV
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    
    total = len(rows)
    if limit:
        rows = rows[:limit]

    print(f"[INFO] Loaded {len(rows)} businesses from {input_path}")
    if limit and total > limit:
        print(f"[INFO] Processed {limit}/{total} rows due to --limit")
    
    # Add new columns
    new_columns = [
        "google_verified",
        "google_status", 
        "google_rating",
        "google_review_count",
        "review_velocity",
        "last_verified"
    ]
    output_fieldnames = list(fieldnames) + [c for c in new_columns if c not in fieldnames]
    
    # Process each business
    enriched_rows = []
    now = datetime.now(timezone.utc).isoformat()
    
    verified_count = 0
    error_count = 0
    
    for i, row in enumerate(rows):
        business_name = row.get("Business Name", "")
        city = row.get("City", "")
        
        if not business_name or not city:
            print(f"[SKIP] Row {i+1}: Missing business name or city")
            row.update({
                "google_verified": "False",
                "google_status": "unknown",
                "google_rating": "",
                "google_review_count": "",
                "review_velocity": "",
                "last_verified": ""
            })
            enriched_rows.append(row)
            continue
        
        cache_key = make_cache_key(business_name, city)
        prev_entry = cache.get(cache_key, {})
        
        # Rate limiting
        if i > 0:
            time.sleep(REQUEST_DELAY)
        
        # Progress indicator
        pct = (i + 1) / len(rows) * 100
        print(f"[{i+1}/{len(rows)}] ({pct:.1f}%) Looking up: {business_name}, {city}")
        
        # Get place data
        if dry_run:
            place_data = generate_dry_run_data(business_name, city)
            print(f"  [DRY-RUN] Mock data: {place_data['status']}, {place_data['rating']}★, {place_data['review_count']} reviews")
        elif api_key:
            place_data = search_google_places(business_name, city, api_key)
            if place_data:
                print(f"  [OK] {place_data['status']}, {place_data.get('rating', 'N/A')}★, {place_data.get('review_count', 0)} reviews")
            else:
                print(f"  [NOT FOUND]")
        else:
            print(f"  [SKIP] No API key and not in dry-run mode")
            place_data = None
        
        # Calculate velocity
        velocity = None
        if place_data:
            velocity = calculate_velocity(prev_entry, place_data.get("review_count", 0))
            
            # Update cache
            history = prev_entry.get("history", [])
            if prev_entry.get("review_count") != place_data.get("review_count"):
                history.append({
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "review_count": place_data.get("review_count", 0)
                })
                # Keep last 12 weeks of history
                history = history[-12:]
            
            cache[cache_key] = {
                "place_id": place_data.get("place_id", ""),
                "status": place_data.get("status", "unknown"),
                "rating": place_data.get("rating"),
                "review_count": place_data.get("review_count", 0),
                "last_verified": now,
                "history": history
            }
            verified_count += 1
        else:
            error_count += 1
        
        # Build output row
        row["google_verified"] = str(place_data is not None)
        row["google_status"] = place_data.get("status", "unknown") if place_data else "unknown"
        row["google_rating"] = str(place_data.get("rating", "")) if place_data and place_data.get("rating") else ""
        row["google_review_count"] = str(place_data.get("review_count", "")) if place_data else ""
        row["review_velocity"] = str(velocity) if velocity is not None else ""
        row["last_verified"] = now if place_data else ""
        
        enriched_rows.append(row)
    
    # Save cache
    save_cache(cache, cache_path)
    print(f"[INFO] Saved cache with {len(cache)} entries")
    
    # Write output CSV
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)
    
    print(f"\n[DONE] Results written to {output_path}")
    print(f"  Verified: {verified_count}")
    print(f"  Errors/Not Found: {error_count}")
    print(f"  Total: {len(rows)}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enrich CCC license data with Google Places information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run (no API calls)
    python google_places_agent.py --dry-run
    
    # With API key
    GOOGLE_PLACES_API_KEY=xxx python google_places_agent.py
    
    # Custom input/output
    python google_places_agent.py --input my_data.csv --output enriched.csv
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        default=DEFAULT_INPUT,
        help=f"Input CSV file (default: {DEFAULT_INPUT})"
    )
    
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output CSV file (default: output/places_enriched_YYYY-MM-DD.csv)"
    )
    
    parser.add_argument(
        "--cache",
        default=CACHE_FILE,
        help=f"Cache file path (default: {CACHE_FILE})"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip API calls, generate mock data for testing"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of rows processed"
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        output_path = f"{DEFAULT_OUTPUT_DIR}/places_enriched_{date_str}.csv"
    
    # Check for API key
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    
    if not api_key and not args.dry_run:
        print("[WARN] No GOOGLE_PLACES_API_KEY found. Use --dry-run for testing.")
        print("       Set the environment variable or use --dry-run to continue.")
        sys.exit(1)
    
    if args.dry_run:
        print("[MODE] Dry-run enabled - using mock data")
    else:
        print("[MODE] Live API calls enabled")
    
    # Run processing
    process_businesses(
        input_path=args.input,
        output_path=output_path,
        cache_path=args.cache,
        api_key=api_key,
        dry_run=args.dry_run,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
