#!/usr/bin/env python3
"""Brave Search API client for newsletter scrapers.

Wraps the Brave Web Search API with rate limiting, retries, and
structured result parsing. Loads BRAVE_API_KEY from the project .env.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional


def _load_env(env_path: Optional[str] = None) -> str:
    """Load BRAVE_API_KEY from .env file or environment."""
    key = os.environ.get("BRAVE_API_KEY")
    if key:
        return key

    # Walk up from this file to find .env
    search_dirs = []
    if env_path:
        search_dirs.append(Path(env_path))
    here = Path(__file__).resolve().parent
    for parent in [here, here.parent, here.parent.parent, here.parent.parent.parent]:
        search_dirs.append(parent / ".env")

    for env_file in search_dirs:
        if env_file.is_file():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("BRAVE_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            os.environ["BRAVE_API_KEY"] = val
                            return val
    raise RuntimeError(
        "BRAVE_API_KEY not found. Set it in environment or in a .env file."
    )


BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
_RATE_LIMIT_SEC = 1.0  # 1 request per second (free tier = 1 QPS)
_last_request_time = 0.0


def search(
    query: str,
    count: int = 20,
    freshness: str = "pw",
    country: str = "us",
    extra_params: Optional[dict[str, str]] = None,
    max_retries: int = 3,
) -> list[dict[str, Any]]:
    """Search Brave and return a list of web results.

    Args:
        query: Search query string.
        count: Number of results (max 20 per request).
        freshness: Time filter — pd (day), pw (week), pm (month), py (year).
        country: Country code for result localization.
        extra_params: Additional query parameters for the API.
        max_retries: Number of retries on transient errors.

    Returns:
        List of result dicts with keys: title, url, description, age,
        page_age, source, domain.
    """
    global _last_request_time

    api_key = _load_env()

    params: dict[str, str] = {
        "q": query,
        "count": str(min(count, 20)),
        "freshness": freshness,
        "country": country,
        "search_lang": "en",
        "text_decorations": "false",
    }
    if extra_params:
        params.update(extra_params)

    url = f"{BRAVE_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }

    for attempt in range(max_retries + 1):
        # Rate limit
        now = time.time()
        wait = _RATE_LIMIT_SEC - (now - _last_request_time)
        if wait > 0:
            time.sleep(wait)
        _last_request_time = time.time()

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                # Handle gzip if needed
                if resp.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    raw = gzip.decompress(raw)
                data = json.loads(raw.decode("utf-8"))

            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "age": item.get("age", ""),
                    "page_age": item.get("page_age", ""),
                    "source": _extract_source_name(item.get("url", "")),
                    "domain": _extract_domain(item.get("url", "")),
                })
            return results

        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError as exc:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            raise

    return []


def multi_search(
    queries: list[str],
    count_per_query: int = 20,
    freshness: str = "pw",
    country: str = "us",
    dedupe: bool = True,
) -> list[dict[str, Any]]:
    """Run multiple searches and merge/dedupe results.

    Returns combined results with duplicates (by URL) removed.
    """
    all_results: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for query in queries:
        try:
            results = search(query, count=count_per_query, freshness=freshness, country=country)
            for r in results:
                url = r["url"]
                if dedupe and url in seen_urls:
                    continue
                seen_urls.add(url)
                all_results.append(r)
        except Exception as exc:
            import sys
            print(f"Warning: search failed for '{query}': {exc}", file=sys.stderr)
            continue

    return all_results


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.replace("www.", "")
    except Exception:
        return ""


SOURCE_NAME_MAP = {
    "marijuanamoment.net": "Marijuana Moment",
    "masslive.com": "MassLive",
    "boston.com": "Boston.com",
    "mjbizdaily.com": "MJBizDaily",
    "reuters.com": "Reuters",
    "bostonglobe.com": "Boston Globe",
    "wbur.org": "WBUR",
    "wcvb.com": "WCVB",
    "nbcboston.com": "NBC Boston",
    "cbsnews.com": "CBS News",
    "leafly.com": "Leafly",
    "weedmaps.com": "Weedmaps",
    "cannabisbusinesstimes.com": "Cannabis Business Times",
    "ganjapreneur.com": "Ganjapreneur",
    "greenmarketreport.com": "Green Market Report",
    "hightimes.com": "High Times",
    "eventbrite.com": "Eventbrite",
    "meetup.com": "Meetup",
    "flowhub.com": "Flowhub",
    "dutchie.com": "Dutchie",
    "metrc.com": "Metrc",
    "iheartjane.com": "Jane",
    "producthunt.com": "Product Hunt",
}


def _extract_source_name(url: str) -> str:
    """Map domain to friendly source name."""
    domain = _extract_domain(url)
    for key, name in SOURCE_NAME_MAP.items():
        if key in domain:
            return name
    # Fallback: capitalize domain parts
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[-2].capitalize()
    return domain
