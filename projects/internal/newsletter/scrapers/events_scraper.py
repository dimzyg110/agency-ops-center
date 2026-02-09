#!/usr/bin/env python3
"""MA cannabis events scraper using Brave Search API.

Replaces the old Eventbrite HTML scraper with reliable API-based search.
Outputs the same JSON format expected by the pipeline data contract.

Usage:
    python events_scraper.py --output ./data/events_upcoming.json [--days 30]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow importing from same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brave_client


# ── Search queries ────────────────────────────────────────────────────
EVENT_QUERIES = [
    "Massachusetts cannabis events 2026",
    "Massachusetts dispensary event",
    "Boston cannabis industry event",
    "Massachusetts marijuana networking event",
    "cannabis conference Massachusetts",
]


JUNK_URL_PATTERNS = [
    "/about", "/contact", "/login", "/signup", "/privacy", "/terms",
    "/category/", "/tag/", "/author/",
]


def is_junk(result: dict) -> bool:
    """Filter out non-event pages."""
    url = result.get("url", "").lower()
    title = result.get("title", "").lower()

    for pattern in JUNK_URL_PATTERNS:
        if pattern in url:
            return True
    if len(title.strip()) < 10:
        return True

    return False


def extract_date_from_text(text: str) -> str | None:
    """Try to extract a date from text. Returns YYYY-MM-DD or None."""
    # ISO date
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)

    # Written dates like "February 14, 2026"
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12",
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "jun": "06", "jul": "07", "aug": "08", "sep": "09",
        "oct": "10", "nov": "11", "dec": "12",
    }
    m = re.search(
        r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"\s+(\d{1,2}),?\s*(\d{4})",
        text,
        re.IGNORECASE,
    )
    if m:
        month = months.get(m.group(1).lower())
        day = m.group(2).zfill(2)
        year = m.group(3)
        if month:
            return f"{year}-{month}-{day}"

    return None


def extract_location_from_text(text: str) -> str:
    """Try to extract a location from text."""
    # Look for "City, MA" or "City, Massachusetts"
    m = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*(?:MA|Massachusetts)", text)
    if m:
        return f"{m.group(1)}, MA"

    # Look for "in Boston" pattern
    m = re.search(
        r"in\s+(Boston|Cambridge|Worcester|Springfield|Somerville|Brookline|"
        r"Holyoke|Easthampton|Northampton|Pittsfield|Salem|Lowell|Amherst|"
        r"Plymouth|Provincetown|Nantucket|Martha's Vineyard)",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"{m.group(1).title()}, MA"

    return "Massachusetts"


def brave_result_to_event(result: dict) -> dict:
    """Convert a Brave search result to the pipeline's event format."""
    text = f"{result['title']} {result.get('description', '')}"

    date = extract_date_from_text(text) or "TBD"
    location = extract_location_from_text(text)

    return {
        "name": result["title"],
        "date": date,
        "time": "TBD",
        "location": location,
        "url": result["url"],
        "description": result.get("description", ""),
        "price": None,
        "source": result.get("source", "Brave Search"),
        "source_id": f"brave_{result.get('domain', 'unknown')}",
        "ma_impact_score": 88,
        "operator_actionability_score": 50,
        "evidence_confidence_score": 70,
        "composite_relevance_score": 65,
        "geo_scope": "ma",
    }


def main():
    parser = argparse.ArgumentParser(description="Events scraper (Brave Search API)")
    parser.add_argument("--output", "-o", required=True, help="Output JSON path")
    parser.add_argument("--days", type=int, default=30, help="Freshness window in days")
    args = parser.parse_args()

    freshness = "pm"  # Past month for events

    print("Searching for MA cannabis events...", file=sys.stderr)
    results = brave_client.multi_search(
        EVENT_QUERIES, count_per_query=20, freshness=freshness
    )

    # Filter junk
    results = [r for r in results if not is_junk(r)]

    # Convert to events
    events = [brave_result_to_event(r) for r in results]

    # Sort by date (TBD goes last)
    events.sort(key=lambda e: e["date"] if e["date"] != "TBD" else "9999-99-99")

    # Build output
    now = datetime.now(timezone.utc).isoformat()

    output = {
        "scraped_at": now,
        "events": events,
        "source_health": [
            {
                "source_id": "brave_search",
                "source_name": "Brave Search API",
                "priority_tier": "primary",
                "geo_scope": "ma",
                "status": "success" if events else "empty",
                "item_count": len(events),
                "error": None,
            }
        ],
        "coverage": {
            "geo_scope_counts": {"ma": len(events)},
            "domain_counts": {},
        },
        "freshness": {
            "oldest_published": events[0]["date"] if events else None,
            "newest_published": events[-1]["date"] if events else None,
        },
    }

    # Write output
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(
        json.dumps({"event": "scrape_complete", "output": str(out_path),
                     "count": len(events)}),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
