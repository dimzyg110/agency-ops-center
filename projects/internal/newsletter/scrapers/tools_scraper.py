#!/usr/bin/env python3
"""Cannabis industry tools/tech scraper using Brave Search API.

Replaces the old BeautifulSoup-based scraper with reliable API-based search.
Outputs the same JSON format expected by the pipeline data contract.

Usage:
    python tools_scraper.py --output ./data/tools_weekly.json
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


# ── Search queries ────────────────────────────────────────────────────
TOOLS_QUERIES = [
    "cannabis dispensary software tools",
    "cannabis POS system technology",
    "dispensary inventory management software",
    "cannabis compliance tracking software",
    "seed to sale tracking software",
    "cannabis retail technology",
]


JUNK_URL_PATTERNS = [
    "/about", "/contact", "/login", "/signup", "/privacy", "/terms",
    "/category/", "/tag/", "/author/", "/careers",
]


def is_junk(result: dict) -> bool:
    """Filter out non-tool pages."""
    url = result.get("url", "").lower()
    title = result.get("title", "").lower()

    for pattern in JUNK_URL_PATTERNS:
        if pattern in url:
            return True
    if len(title.strip()) < 10:
        return True

    return False


def score_tool(result: dict) -> float:
    """Score a tool result for operator relevance."""
    score = 50.0
    text = f"{result.get('title', '')} {result.get('description', '')}".lower()

    operator_keywords = [
        "pos", "inventory", "compliance", "tracking", "seed-to-sale",
        "dispensary", "cultivation", "retail", "erp", "crm", "analytics",
        "point of sale", "ecommerce", "menu", "ordering", "delivery",
    ]
    for kw in operator_keywords:
        if kw in text:
            score += 8

    # Domain quality
    domain = result.get("domain", "")
    known_tools = ["dutchie.com", "flowhub.com", "iheartjane.com", "metrc.com",
                   "biotrack.com", "blaze.me", "treez.io", "meadow.com",
                   "indica.online", "greenline.io", "cova.com", "sweed.is"]
    if any(d in domain for d in known_tools):
        score += 20

    return min(score, 100)


def brave_result_to_tool(result: dict) -> dict:
    """Convert a Brave search result to the pipeline's tool format."""
    composite = score_tool(result)

    return {
        "title": result["title"],
        "name": result["title"],
        "url": result["url"],
        "description": result.get("description", ""),
        "summary": result.get("description", ""),
        "source": result.get("source", ""),
        "source_id": f"brave_{result.get('domain', 'unknown')}",
        "ma_impact_score": 55,
        "operator_actionability_score": 70,
        "evidence_confidence_score": 80,
        "composite_relevance_score": round(composite),
        "geo_scope": "national",
    }


def main():
    parser = argparse.ArgumentParser(description="Tools scraper (Brave Search API)")
    parser.add_argument("--output", "-o", required=True, help="Output JSON path")
    args = parser.parse_args()

    print("Searching for cannabis industry tools...", file=sys.stderr)
    results = brave_client.multi_search(
        TOOLS_QUERIES, count_per_query=10, freshness="pm"  # Past month
    )

    # Filter junk
    results = [r for r in results if not is_junk(r)]

    # Convert to tools
    tools = [brave_result_to_tool(r) for r in results]

    # Sort by score
    tools.sort(key=lambda t: t["composite_relevance_score"], reverse=True)

    # Build domain counts
    domain_counts = {}
    for t in tools:
        d = urlparse(t["url"]).netloc.replace("www.", "")
        domain_counts[d] = domain_counts.get(d, 0) + 1

    # Build output
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    output = {
        "scraped_at": now,
        "tools": tools,
        "source_health": [
            {
                "source_id": "brave_search",
                "source_name": "Brave Search API",
                "priority_tier": "primary",
                "geo_scope": "national",
                "status": "success" if tools else "empty",
                "item_count": len(tools),
                "error": None,
            }
        ],
        "coverage": {
            "geo_scope_counts": {"national": len(tools)},
            "domain_counts": domain_counts,
        },
        "freshness": {
            "oldest_published": now,
            "newest_published": now,
        },
    }

    # Write output
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(
        json.dumps({"event": "output_written", "count": len(tools),
                     "output": str(out_path)}),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
