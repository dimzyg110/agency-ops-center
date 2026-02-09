#!/usr/bin/env python3
"""
Decision Maker Lookup - Lead Tool Phase 3

Finds GM/Buyer decision makers for each dispensary using LinkedIn search via Brave API.
Fallbacks to Google search if Brave API key is missing.

Outputs enriched CSV with:
- decision_maker_name
- decision_maker_title
- decision_maker_linkedin
- dm_confidence

Usage:
    python decision_maker_lookup.py --input signals_pack.csv --output dm_enriched.csv --limit 10

Environment:
    BRAVE_API_KEY - required for Brave Search API (recommended)
    LEAD_TOOL_STATE - optional default state for location scoring/query (e.g., "Massachusetts" or "MA")
"""

import argparse
import csv
import json
import logging
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Dict, Optional


# =============================================================================
# CONFIG
# =============================================================================

DEFAULT_INPUT = "output/signals_pack_enriched.csv"
DEFAULT_OUTPUT = "output/dm_enriched.csv"
DEFAULT_STATE = os.environ.get("LEAD_TOOL_STATE", "Massachusetts")
REQUEST_TIMEOUT = 20
RATE_LIMIT_SECONDS = 1.2  # delay between searches
MAX_RESULTS = 5

DECISION_TITLES = [
    "general manager",
    "store manager",
    "inventory manager",
    "purchasing manager",
    "buyer",
    "procurement",
    "operations manager",
    "director of operations",
    "vp operations",
]

LINKEDIN_PERSON_RE = re.compile(r"linkedin\.com/(in|pub)/", re.IGNORECASE)
TRANSIENT_HTTP_STATUS = {429, 500, 502, 503, 504}
BRAVE_RETRY_DELAYS = [1, 2, 4]
GOOGLE_RETRY_DELAYS = [2, 4, 8]  # exponential backoff for fragile HTML fallback

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# SEARCH HELPERS
# =============================================================================


def fetch_with_retries(
    req: urllib.request.Request,
    retry_delays: List[int],
    description: str,
    transient_statuses: Optional[set] = None,
) -> bytes:
    """Fetch URL with retry/backoff for transient errors."""
    for attempt in range(len(retry_delays) + 1):
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            if transient_statuses and e.code in transient_statuses and attempt < len(retry_delays):
                delay = retry_delays[attempt]
                logger.warning("Transient HTTP error during %s (%s). Retrying in %ss...", description, e.code, delay)
                time.sleep(delay)
                continue
            logger.warning("HTTP error during %s: %s", description, e)
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < len(retry_delays):
                delay = retry_delays[attempt]
                logger.warning("Network error during %s: %s. Retrying in %ss...", description, e, delay)
                time.sleep(delay)
                continue
            logger.warning("Network error during %s: %s", description, e)
            raise

    raise RuntimeError(f"Failed to fetch during {description}")


def brave_search(query: str, api_key: str, count: int = MAX_RESULTS) -> List[Dict[str, str]]:
    """Search Brave API and return list of results (title, url, description)."""
    params = urllib.parse.urlencode({"q": query, "count": count})
    url = f"https://api.search.brave.com/res/v1/web/search?{params}"
    req = urllib.request.Request(url, headers={"X-Subscription-Token": api_key})

    try:
        raw = fetch_with_retries(req, BRAVE_RETRY_DELAYS, "Brave search", TRANSIENT_HTTP_STATUS)
        data = json.loads(raw.decode("utf-8"))
        results = data.get("web", {}).get("results", [])
        parsed = []
        for item in results:
            parsed.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", "") or item.get("snippet", "")
            })
        return parsed
    except Exception as e:
        logger.warning("Brave search failed: %s", e)
        return []


def google_search_fallback(query: str, count: int = MAX_RESULTS) -> List[Dict[str, str]]:
    """Fallback Google search (HTML scrape). Best-effort only."""
    params = urllib.parse.urlencode({"q": query})
    url = f"https://www.google.com/search?{params}"

    for attempt in range(len(GOOGLE_RETRY_DELAYS) + 1):
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                html = response.read().decode("utf-8", errors="ignore")

            # very simple extraction of result links
            links = re.findall(r"/url\?q=(https?://[^&]+)", html)
            results = []
            for link in links:
                if "linkedin.com" not in link:
                    continue
                results.append({"title": "", "url": urllib.parse.unquote(link), "description": ""})
                if len(results) >= count:
                    break
            return results
        except urllib.error.HTTPError as e:
            if e.code in TRANSIENT_HTTP_STATUS and attempt < len(GOOGLE_RETRY_DELAYS):
                delay = GOOGLE_RETRY_DELAYS[attempt]
                logger.warning("Google fallback HTTP %s for '%s'. Retrying in %ss...", e.code, query, delay)
                time.sleep(delay)
                continue
            logger.warning("Google fallback failed: %s", e)
            return []
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < len(GOOGLE_RETRY_DELAYS):
                delay = GOOGLE_RETRY_DELAYS[attempt]
                logger.warning("Google fallback network error for '%s': %s. Retrying in %ss...", query, e, delay)
                time.sleep(delay)
                continue
            logger.warning("Google fallback failed: %s", e)
            return []

    return []


# =============================================================================
# PARSING & CONFIDENCE
# =============================================================================


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def build_state_terms(state: str) -> List[str]:
    """Normalize state input into searchable terms (name + abbreviation)."""
    if not state:
        return []
    terms = [t.strip().lower() for t in re.split(r"[/,]", state) if t.strip()]
    if len(terms) == 1 and len(terms[0]) > 2:
        # Best-effort abbreviation from words (e.g., New York -> ny)
        abbr = "".join([part[0] for part in terms[0].split() if part])
        if abbr:
            terms.append(abbr.lower())
    return list(dict.fromkeys(terms))


def extract_candidate(result: Dict[str, str], company: str, state_terms: List[str]) -> Optional[Dict[str, str]]:
    """Extract name/title from a search result."""
    url = result.get("url", "")
    if not LINKEDIN_PERSON_RE.search(url):
        return None

    title = normalize_text(result.get("title", ""))
    desc = normalize_text(result.get("description", ""))

    name = ""
    role = ""

    # Common LinkedIn title format: "Name - Title - Company | LinkedIn"
    m = re.match(r"^(.*?)\s+-\s+(.+?)\s*\|\s*LinkedIn", title, re.IGNORECASE)
    if m:
        name = normalize_text(m.group(1))
        role = normalize_text(m.group(2))
    else:
        # Alternate: "Name - Title - Company"
        m2 = re.match(r"^(.*?)\s+-\s+(.+)$", title)
        if m2:
            name = normalize_text(m2.group(1))
            role = normalize_text(m2.group(2))

    # If title parsing failed, try description
    if not name and desc:
        m3 = re.match(r"^(.*?)\s+-\s+(.+)$", desc)
        if m3:
            name = normalize_text(m3.group(1))
            role = normalize_text(m3.group(2))

    if not name and "linkedin.com" in url:
        # Use URL slug as best-effort name
        slug = url.rstrip("/").split("/")[-1]
        name = slug.replace("-", " ").title()

    if not name:
        return None

    confidence = score_confidence(company, title, desc, role, state_terms)

    return {
        "name": name,
        "title": role,
        "linkedin": url,
        "confidence": confidence,
    }


def score_confidence(company: str, title: str, desc: str, role: str, state_terms: List[str]) -> float:
    """Score confidence (0-1) based on company/title matches."""
    score = 0.2
    company_norm = company.lower()
    text_blob = f"{title} {desc} {role}".lower()

    if company_norm and company_norm in text_blob:
        score += 0.4

    if any(t in text_blob for t in DECISION_TITLES):
        score += 0.3

    if state_terms and any(term in text_blob for term in state_terms):
        score += 0.1

    return round(min(score, 1.0), 2)


def select_best_candidate(candidates: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    if not candidates:
        return None
    return sorted(candidates, key=lambda c: c.get("confidence", 0), reverse=True)[0]


def generate_mock_dm(company: str) -> Dict[str, str]:
    """Deterministic mock decision maker for dry-run."""
    import hashlib
    h = hashlib.md5(company.encode("utf-8")).hexdigest()
    name = f"{company.split(' ')[0].title()} Manager"
    title = "General Manager" if int(h[:2], 16) % 2 == 0 else "Inventory Manager"
    linkedin = f"https://www.linkedin.com/in/{company.lower().replace(' ', '')}-{h[:6]}/"
    confidence = 0.65
    return {
        "name": name,
        "title": title,
        "linkedin": linkedin,
        "confidence": confidence
    }


# =============================================================================
# MAIN PROCESSING
# =============================================================================


def process(input_path: str, output_path: str, limit: Optional[int], dry_run: bool, state: str) -> None:
    if not os.path.exists(input_path):
        logger.error("Input file not found: %s", input_path)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    total = len(rows)
    if limit:
        rows = rows[:limit]

    api_key = os.environ.get("BRAVE_API_KEY")
    if not api_key and not dry_run:
        logger.warning("BRAVE_API_KEY not set. Using Google search fallback (best-effort).")

    state_terms = build_state_terms(state)
    state_query = state_terms[0] if state_terms else state

    # Append output columns if missing
    new_cols = [
        "decision_maker_name",
        "decision_maker_title",
        "decision_maker_linkedin",
        "dm_confidence",
    ]
    output_fields = fieldnames + [c for c in new_cols if c not in fieldnames]

    enriched = []

    for idx, row in enumerate(rows):
        company = row.get("Business Name") or row.get("Company") or row.get("company_name") or ""
        company = company.strip()

        if not company:
            logger.info("[SKIP] Row %s: missing company name", idx + 1)
            row.update({
                "decision_maker_name": "",
                "decision_maker_title": "",
                "decision_maker_linkedin": "",
                "dm_confidence": "",
            })
            enriched.append(row)
            continue

        logger.info("[%s/%s] Searching decision makers for: %s", idx + 1, len(rows), company)

        if dry_run:
            dm = generate_mock_dm(company)
            row.update({
                "decision_maker_name": dm["name"],
                "decision_maker_title": dm["title"],
                "decision_maker_linkedin": dm["linkedin"],
                "dm_confidence": str(dm["confidence"]),
            })
            enriched.append(row)
            continue

        queries = [
            f"{company} {state_query} General Manager LinkedIn",
            f"{company} {state_query} Inventory Manager LinkedIn",
        ]

        candidates = []
        for q in queries:
            time.sleep(RATE_LIMIT_SECONDS)
            if api_key:
                results = brave_search(q, api_key=api_key)
            else:
                results = google_search_fallback(q)

            for result in results:
                candidate = extract_candidate(result, company, state_terms)
                if candidate:
                    candidates.append(candidate)

        best = select_best_candidate(candidates)

        if best:
            row.update({
                "decision_maker_name": best["name"],
                "decision_maker_title": best["title"],
                "decision_maker_linkedin": best["linkedin"],
                "dm_confidence": str(best["confidence"]),
            })
            logger.info("  [OK] %s | %s | %s | %s", best["name"], best["title"], best["linkedin"], best["confidence"])
        else:
            row.update({
                "decision_maker_name": "",
                "decision_maker_title": "",
                "decision_maker_linkedin": "",
                "dm_confidence": "",
            })
            logger.info("  [NOT FOUND]")

        enriched.append(row)

    # Write output
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(enriched)

    logger.info("\n[DONE] Wrote %s rows to %s", len(enriched), output_path)
    if limit and total > limit:
        logger.info("[INFO] Processed %s/%s rows due to --limit", limit, total)


def main():
    parser = argparse.ArgumentParser(description="Decision maker lookup via LinkedIn search")
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT, help=f"Input CSV (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help=f"Output CSV (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows processed")
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls, generate mock data")
    parser.add_argument(
        "--state",
        default=DEFAULT_STATE,
        help="State name/abbrev for search + confidence (default: LEAD_TOOL_STATE or Massachusetts)",
    )

    args = parser.parse_args()

    process(args.input, args.output, args.limit, args.dry_run, args.state)


if __name__ == "__main__":
    main()
