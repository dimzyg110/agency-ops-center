#!/usr/bin/env python3
"""Reddit social scraper for newsletter system."""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

USER_AGENT = "NewsletterScraper/1.0 (contact: ops@example.com)"
RATE_LIMIT_SECONDS = 2

SUBREDDITS = ["bostontrees", "mainetrees", "cannabiscultivation"]

# Keywords indicating operator/professional relevance
ALLOW_KEYWORDS = [
    "cultivation",
    "grow",
    "harvest",
    "dry",
    "cure",
    "ph",
    "nutrient",
    "nutrients",
    "pest",
    "mold",
    "pm",
    "powdery mildew",
    "ipm",
    "integrated pest",
    "clone",
    "cloning",
    "genetic",
    "genetics",
    "breeding",
    "phenotype",
    "pheno",
    "yield",
    "equipment",
    "lighting",
    "led",
    "hvac",
    "dehumidifier",
    "extract",
    "extraction",
    "processing",
    "rosin",
    "hash",
    "compliance",
    "regulation",
    "license",
    "licensing",
    "business",
    "operations",
    "facility",
    "buildout",
    "commercial",
    "lab",
    "testing",
    "coa",
    "standards",
    "sop",
    "sops",
    "qa",
    "qc",
    "packaging",
    "distribution",
    "wholesale",
    "supply",
    "pricing",
    "market",
    "industry",
    "news",
    "policy",
    "legislation",
    "tax",
    "grant",
]

# Keywords indicating consumer-only chatter
DENY_KEYWORDS = [
    "first time",
    "smoke",
    "smoked",
    "joint",
    "blunt",
    "edible",
    "edibles",
    "high",
    "stoned",
    "cart",
    "carts",
    "pickup",
    "score",
    "stash",
    "plug",
    "dealer",
    "dispensary haul",
    "hauls",
    "review",
    "rate my",
    "what should i smoke",
    "bong",
    "dab",
    "dabbed",
    "concentrate",
    "looking for",
]


def is_operator_relevant(title: str, flair: str | None) -> bool:
    text = f"{title} {flair or ''}".lower()
    if any(kw in text for kw in DENY_KEYWORDS):
        return False
    if any(kw in text for kw in ALLOW_KEYWORDS):
        return True
    return False


def fetch_top_posts(subreddit: str, limit: int) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=week&limit={limit}"
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Failed to fetch {subreddit}: {exc}") from exc

    posts = []
    children = payload.get("data", {}).get("children", [])
    for child in children:
        data = child.get("data", {})
        title = data.get("title") or ""
        flair = data.get("link_flair_text")
        if not is_operator_relevant(title, flair):
            continue
        permalink = data.get("permalink") or ""
        url_full = f"https://reddit.com{permalink}" if permalink else data.get("url")
        posts.append(
            {
                "title": title,
                "url": url_full,
                "score": int(data.get("score") or 0),
                "comments": int(data.get("num_comments") or 0),
                "subreddit": subreddit,
                "flair": flair,
            }
        )
    return posts


def scrape(limit: int) -> dict:
    all_posts: list[dict] = []
    for idx, subreddit in enumerate(SUBREDDITS):
        if idx > 0:
            time.sleep(RATE_LIMIT_SECONDS)
        all_posts.extend(fetch_top_posts(subreddit, limit))

    all_posts.sort(key=lambda p: p["score"], reverse=True)
    top_posts = all_posts[:15]
    scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"scraped_at": scraped_at, "posts": top_posts}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reddit social scraper")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max posts per subreddit (default: 20)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output JSON path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = scrape(args.limit)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
