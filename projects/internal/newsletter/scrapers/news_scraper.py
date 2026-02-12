#!/usr/bin/env python3
"""MA cannabis news scraper using Brave Search API.

Replaces the old BeautifulSoup-based scraper with reliable API-based search.
Outputs the same JSON format expected by the pipeline data contract.

Usage:
    python news_scraper.py --output ./data/news_weekly.json [--days 7]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# Allow importing from same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brave_client


# ── Search queries (MA-first, then national) ──────────────────────────
MA_NEWS_QUERIES = [
    "Massachusetts cannabis news",
    "Massachusetts dispensary news",
    "Massachusetts marijuana regulation CCC",
    "Massachusetts cannabis license",
]

NATIONAL_NEWS_QUERIES = [
    "cannabis industry news",
    "marijuana legalization news",
]

# ── Filtering ─────────────────────────────────────────────────────────
JUNK_URL_PATTERNS = [
    "/about", "/contact", "/support", "/login", "/signup", "/register",
    "/subscribe", "/newsletter", "/privacy", "/terms", "/cookie",
    "/category/", "/tag/", "/author/", "/page/", "/feed",
    "/remove-ads", "/patreon", "/bills/marijuana-legislation",
]

JUNK_TITLE_PATTERNS = [
    "skip to", "remove ads", "subscribe", "login", "sign up",
    "cookie policy", "privacy policy", "about us", "contact us",
    "bill tracker", "login instructions",
]

# Blocked domains — non-credible or misleading sources
BLOCKED_DOMAINS = [
    "dontlegalizedrugs.com",
    "dailystormer.com",
    "infowars.com",
]

# Domains that indicate NON-MA content (wrong state publications)
NON_MA_PUBLICATION_DOMAINS = [
    "rcbizjournal.com",       # Rockland County (NY) Business Journal
    "hudsonvalley360.com",    # Hudson Valley, NY
    "njbiz.com",              # New Jersey
    "ctpost.com",             # Connecticut
    "nj.com",                 # New Jersey
    "silive.com",             # Staten Island, NY
]

MA_KEYWORDS = [
    "massachusetts", "boston", "cambridge", "worcester", "springfield",
    "mass.", "mass ", "ccc", "ma ", " ma",
]


def is_junk(result: dict) -> bool:
    """Filter out navigation pages, about pages, blocked domains, etc."""
    url = result.get("url", "").lower()
    title = result.get("title", "").lower()
    domain = result.get("domain", "").lower()

    # Block non-credible sources entirely
    for blocked in BLOCKED_DOMAINS:
        if blocked in domain or blocked in url:
            return True

    # Block non-MA regional publications (e.g., Rockland County NY)
    for non_ma in NON_MA_PUBLICATION_DOMAINS:
        if non_ma in domain:
            return True

    for pattern in JUNK_URL_PATTERNS:
        if pattern in url:
            return True
    for pattern in JUNK_TITLE_PATTERNS:
        if pattern in title:
            return True

    # Skip if title is too short (likely nav element)
    if len(title.strip()) < 15:
        return True

    return False


def is_ma_related(result: dict) -> bool:
    """Check if a result is Massachusetts-related."""
    text = f"{result.get('title', '')} {result.get('description', '')}".lower()
    return any(kw in text for kw in MA_KEYWORDS)


def score_result(result: dict, is_ma: bool) -> float:
    """Score a result for relevance."""
    score = 50.0

    # MA-related boost
    if is_ma:
        score += 30

    # Domain quality
    domain = result.get("domain", "")
    trusted = ["masslive.com", "bostonglobe.com", "wbur.org", "marijuanamoment.net",
               "mjbizdaily.com", "reuters.com", "cannabisbusinesstimes.com"]
    if any(d in domain for d in trusted):
        score += 15

    # Title keyword signals
    title = result.get("title", "").lower()
    high_value_words = ["license", "regulation", "approved", "announces", "launches",
                        "breaking", "exclusive", "revenue", "sales", "opens", "closes"]
    for word in high_value_words:
        if word in title:
            score += 5

    # Description length (more description = likely a real article)
    desc = result.get("description", "")
    if len(desc) > 100:
        score += 5

    return min(score, 100)


def brave_result_to_article(result: dict, geo_scope: str) -> dict:
    """Convert a Brave search result to the pipeline's article format."""
    is_ma = geo_scope == "ma"
    composite = score_result(result, is_ma)

    return {
        "headline": result["title"],
        "url": result["url"],
        "published": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "excerpt": result.get("description", ""),
        "source": result.get("source", ""),
        "source_id": f"brave_{result.get('domain', 'unknown')}",
        "ma_impact_score": 88 if is_ma else 55,
        "operator_actionability_score": 50,
        "evidence_confidence_score": 85,
        "composite_relevance_score": round(composite),
        "geo_scope": geo_scope,
    }


def main():
    parser = argparse.ArgumentParser(description="News scraper (Brave Search API)")
    parser.add_argument("--output", "-o", required=True, help="Output JSON path")
    parser.add_argument("--days", type=int, default=7, help="Freshness window in days")
    args = parser.parse_args()

    freshness = "pw" if args.days <= 7 else "pm"

    # Fetch MA news
    print("Searching for MA cannabis news...", file=sys.stderr)
    ma_results = brave_client.multi_search(
        MA_NEWS_QUERIES, count_per_query=20, freshness=freshness
    )

    # Fetch national news
    print("Searching for national cannabis news...", file=sys.stderr)
    national_results = brave_client.multi_search(
        NATIONAL_NEWS_QUERIES, count_per_query=10, freshness=freshness
    )

    # Filter junk
    ma_results = [r for r in ma_results if not is_junk(r)]
    national_results = [r for r in national_results if not is_junk(r)]

    # Dedupe across both sets
    seen_urls = {r["url"] for r in ma_results}
    national_results = [r for r in national_results if r["url"] not in seen_urls]

    # Convert to articles
    articles = []
    ma_domains = set()
    national_domains = set()

    for r in ma_results:
        articles.append(brave_result_to_article(r, "ma"))
        ma_domains.add(r.get("domain", ""))

    for r in national_results:
        geo = "ma" if is_ma_related(r) else "national"
        articles.append(brave_result_to_article(r, geo))
        national_domains.add(r.get("domain", ""))

    # Sort by composite score
    articles.sort(key=lambda a: a["composite_relevance_score"], reverse=True)

    # Build output
    now = datetime.now(timezone.utc).isoformat()
    all_domains = ma_domains | national_domains
    domain_counts = {}
    for a in articles:
        d = urlparse(a["url"]).netloc.replace("www.", "")
        domain_counts[d] = domain_counts.get(d, 0) + 1

    geo_counts = {}
    for a in articles:
        g = a["geo_scope"]
        geo_counts[g] = geo_counts.get(g, 0) + 1

    output = {
        "scraped_at": now,
        "articles": articles,
        "source_health": [
            {
                "source_id": "brave_search",
                "source_name": "Brave Search API",
                "priority_tier": "primary",
                "geo_scope": "ma",
                "status": "success" if articles else "empty",
                "item_count": len(articles),
                "error": None,
            }
        ],
        "coverage": {
            "geo_scope_counts": geo_counts,
            "domain_counts": domain_counts,
        },
        "freshness": {
            "oldest_published": articles[-1]["published"] if articles else None,
            "newest_published": articles[0]["published"] if articles else None,
        },
    }

    # Write output
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(
        json.dumps({"event": "output_written", "count": len(articles),
                     "output": str(out_path), "domains": len(all_domains)}),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
