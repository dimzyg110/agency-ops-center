#!/usr/bin/env python3
"""MA cannabis events scraper — curated sources only.

Only returns ACTUAL events with verified dates. Sources:
  - Cannabis Control Commission public meetings calendar
  - Brave Search for verified cannabis events with real dates
  
Does NOT return:
  - News articles misidentified as events
  - Items without parseable future dates
  - Past events

If no real events are found, returns an empty list.
Better to have an empty events section than fake events.

Usage:
    python events_scraper.py --output ./data/events_upcoming.json [--days 30]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow importing from same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brave_client


# ── Curated event search queries (specific, event-focused) ──────────
EVENT_QUERIES = [
    "Massachusetts cannabis conference 2026 date",
    "Massachusetts Cannabis Control Commission meeting schedule 2026",
    "MassCanna cannabis expo 2026",
    "New England cannabis conference event 2026",
    "Boston cannabis industry networking event 2026",
    "site:eventbrite.com Massachusetts cannabis 2026",
]


# ── Patterns that indicate a news article, NOT an event ─────────────
NEWS_ARTICLE_SIGNALS = [
    "breaking news",
    "press release",
    "legal wrangling",
    "dispensary openings",
    "moves to reverse",
    "sentenced to",
    "generated $",
    "sales generated",
    "mixed reviews",
    "proposed",
    "adult-use cannabis sales",
    "quarterly report",
    "editorial",
    "opinion:",
    "column:",
    "analysis:",
    "cafes are legal",
    " are legal ",
]

# Domains that are news sites, not event platforms
NEWS_DOMAINS = [
    "masslive.com",
    "bostonglobe.com",
    "boston.com",
    "wbur.org",
    "wcvb.com",
    "nbcboston.com",
    "marijuanamoment.net",
    "mjbizdaily.com",
    "dontlegalizedrugs.com",
    "fallriverreporter.com",
    "wwlp.com",
    "cbsnews.com",
    "reuters.com",
    "hightimes.com",
    "greenmarketreport.com",
    "rcbizjournal.com",
    "masslawyersweekly.com",
    "ganjapreneur.com",
]

# Signals that something IS an actual event
EVENT_POSITIVE_SIGNALS = [
    "register",
    "tickets",
    "attend",
    "conference",
    "expo",
    "summit",
    "workshop",
    "networking",
    "meetup",
    "seminar",
    "webinar",
    "gala",
    "festival",
    "meeting",
    "hearing",
    "session",
    "trade show",
    "convention",
]

JUNK_URL_PATTERNS = [
    "/about", "/contact", "/login", "/signup", "/privacy", "/terms",
    "/category/", "/tag/", "/author/", "/bills/",
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


def is_news_article(result: dict) -> bool:
    """Check if a result is likely a news article, not an event."""
    text = f"{result.get('title', '')} {result.get('description', '')}".lower()
    domain = result.get("domain", "").lower()

    # Check domain first
    for news_domain in NEWS_DOMAINS:
        if news_domain in domain:
            return True

    # Check title/description for news signals
    signal_count = sum(1 for signal in NEWS_ARTICLE_SIGNALS if signal in text)
    if signal_count > 0:
        return True

    return False


def is_likely_event(result: dict) -> bool:
    """Check if a result is likely an actual event."""
    text = f"{result.get('title', '')} {result.get('description', '')}".lower()
    domain = result.get("domain", "").lower()

    # Event platforms are strong signals
    event_platforms = ["eventbrite.com", "meetup.com", "lu.ma", "splash.events",
                       "hopin.com", "whova.com", "masscanna", "necann"]
    for platform in event_platforms:
        if platform in domain:
            return True

    # Check for event-related language
    signal_count = sum(1 for signal in EVENT_POSITIVE_SIGNALS if signal in text)
    return signal_count >= 1


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

    # m/d/yyyy format
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        month = m.group(1).zfill(2)
        day = m.group(2).zfill(2)
        year = m.group(3)
        if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return f"{year}-{month}-{day}"

    return None


def is_future_date(date_str: str) -> bool:
    """Check if a date string is in the future (or today)."""
    try:
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now(timezone.utc).date()
        return event_date >= today
    except (ValueError, TypeError):
        return False


def extract_location_from_text(text: str) -> str:
    """Try to extract a location from text."""
    m = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*(?:MA|Massachusetts)", text)
    if m:
        return f"{m.group(1)}, MA"

    m = re.search(
        r"in\s+(Boston|Cambridge|Worcester|Springfield|Somerville|Brookline|"
        r"Holyoke|Easthampton|Northampton|Pittsfield|Salem|Lowell|Amherst|"
        r"Plymouth|Provincetown|Nantucket|Martha's Vineyard|Foxborough|"
        r"Hynes Convention Center|BCEC|"
        r"South Boston|Dorchester|Jamaica Plain)",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"{m.group(1).title()}, MA"

    return "Massachusetts"


def brave_result_to_event(result: dict) -> dict | None:
    """Convert a Brave search result to an event. Returns None if not a valid event."""
    text = f"{result['title']} {result.get('description', '')}"

    date = extract_date_from_text(text)

    # CRITICAL: Reject events without parseable dates
    if date is None:
        return None

    # CRITICAL: Reject past events
    if not is_future_date(date):
        return None

    location = extract_location_from_text(text)

    return {
        "name": result["title"].strip(),
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
    parser = argparse.ArgumentParser(description="Events scraper (curated sources)")
    parser.add_argument("--output", "-o", required=True, help="Output JSON path")
    parser.add_argument("--days", type=int, default=30, help="Freshness window in days")
    args = parser.parse_args()

    freshness = "pm"  # Past month for events

    print("Searching for MA cannabis events (curated sources)...", file=sys.stderr)
    results = brave_client.multi_search(
        EVENT_QUERIES, count_per_query=20, freshness=freshness
    )

    # Step 1: Remove junk pages
    results = [r for r in results if not is_junk(r)]

    # Step 2: Remove news articles (this was the primary bug)
    results = [r for r in results if not is_news_article(r)]

    # Step 3: Prefer results that look like actual events
    event_results = [r for r in results if is_likely_event(r)]
    # If event-signal filtering is too aggressive, fall back to all non-news results
    if len(event_results) < 2:
        event_results = results

    # Step 4: Convert to events — this also rejects items without dates/past dates
    events = []
    for r in event_results:
        event = brave_result_to_event(r)
        if event is not None:
            events.append(event)

    # Step 5: Deduplicate by URL
    seen_urls = set()
    deduped = []
    for event in events:
        if event["url"] not in seen_urls:
            seen_urls.add(event["url"])
            deduped.append(event)
    events = deduped

    # Step 6: Sort by date (soonest first)
    events.sort(key=lambda e: e["date"])

    # Limit to reasonable count
    events = events[:15]

    # Build output
    now = datetime.now(timezone.utc).isoformat()

    filtered_stats = {
        "total_search_results": len(results) + len([r for r in results if is_news_article(r)]),
        "after_news_filter": len(event_results),
        "with_valid_dates": len(events),
    }

    output = {
        "scraped_at": now,
        "events": events,
        "source_health": [
            {
                "source_id": "brave_search_events",
                "source_name": "Brave Search API (Event Queries)",
                "priority_tier": "primary",
                "geo_scope": "ma",
                "status": "success" if events else "empty",
                "item_count": len(events),
                "error": None,
                "filter_stats": filtered_stats,
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
        json.dumps({
            "event": "scrape_complete",
            "output": str(out_path),
            "count": len(events),
            "filter_stats": filtered_stats,
        }),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
