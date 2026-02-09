#!/usr/bin/env python3
"""
MSO Mapper - Lead Tool Phase 3

Identifies whether a dispensary is part of a Multi-State Operator (MSO),
local MA chain, or independent operator.

Approach:
- Match company name against known MSO/local chain list
- Optionally search website "About" page for parent company mentions

Output columns:
- operator_type (mso | local_chain | independent)
- parent_company
- location_count

Usage:
    python mso_mapper.py --input signals_pack.csv --output mso_enriched.csv
"""

import argparse
import csv
import logging
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Optional


# =============================================================================
# CONFIG
# =============================================================================

DEFAULT_INPUT = "output/signals_pack_enriched.csv"
DEFAULT_OUTPUT = "output/mso_enriched.csv"
REQUEST_TIMEOUT = 20
RATE_LIMIT_SECONDS = 1.0

# Known MSOs and local chains
MSO_LIST = {
    "curaleaf": "Curaleaf",
    "trulieve": "Trulieve",
    "green thumb industries": "Green Thumb Industries",
    "gti": "Green Thumb Industries",
    "cresco labs": "Cresco Labs",
    "columbia care": "Columbia Care",
    "ascend wellness": "Ascend Wellness",
    "terrascend": "TerrAscend",
    "ayr wellness": "Ayr Wellness",
    "verano": "Verano",
    "medmen": "MedMen",
}

LOCAL_CHAIN_LIST = {
    "neta": "NETA",
    "revolutionary clinics": "Revolutionary Clinics",
    "berkshire roots": "Berkshire Roots",
    "theory wellness": "Theory Wellness",
}

ABOUT_KEYWORDS = ["about", "our story", "company", "who we are"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# HELPERS
# =============================================================================


def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    name = re.sub(r"\b(llc|inc|corp|corporation|co|company|ltd)\b", "", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    return re.sub(r"\s+", " ", name).strip()


def detect_from_name(company: str) -> Optional[Dict[str, str]]:
    """Return operator info if company matches known list."""
    norm = normalize_name(company)

    for key, parent in MSO_LIST.items():
        if key in norm:
            return {"operator_type": "mso", "parent_company": parent}

    for key, parent in LOCAL_CHAIN_LIST.items():
        if key in norm:
            return {"operator_type": "local_chain", "parent_company": parent}

    return None


def fetch_url(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_text(html: str) -> str:
    # Remove scripts/styles
    html = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style.*?>.*?</style>", " ", html, flags=re.I | re.S)
    # Strip tags
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def find_about_link(base_url: str, html: str) -> Optional[str]:
    links = re.findall(r"href=['\"](.*?)['\"]", html, flags=re.I)
    for link in links:
        for kw in ABOUT_KEYWORDS:
            if kw.replace(" ", "-") in link.lower() or kw in link.lower():
                return urllib.parse.urljoin(base_url, link)
    return None


def detect_from_website(website: str, company: str) -> Optional[Dict[str, str]]:
    """Check website/about page for parent company mentions."""
    if not website:
        return None

    try:
        html = fetch_url(website)
        text = extract_text(html).lower()

        # Check main page for parent mentions
        for key, parent in {**MSO_LIST, **LOCAL_CHAIN_LIST}.items():
            if key in text:
                operator_type = "mso" if key in MSO_LIST else "local_chain"
                return {"operator_type": operator_type, "parent_company": parent}

        # Try about page
        about_url = find_about_link(website, html)
        if about_url:
            about_html = fetch_url(about_url)
            about_text = extract_text(about_html).lower()
            for key, parent in {**MSO_LIST, **LOCAL_CHAIN_LIST}.items():
                if key in about_text:
                    operator_type = "mso" if key in MSO_LIST else "local_chain"
                    return {"operator_type": operator_type, "parent_company": parent}

    except Exception as e:
        # Log failures with context instead of silently swallowing them
        logger.warning("Website detection failed for %s (%s): %s", company, website, e, exc_info=True)
        return None

    return None


def get_website_from_row(row: Dict[str, str]) -> str:
    for key in ["Website", "website", "website_url", "Website URL", "url", "URL"]:
        if row.get(key):
            return row.get(key)
    return ""


def compute_location_counts(rows: List[Dict[str, str]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        name = normalize_name(row.get("Business Name") or row.get("Company") or "")
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1
    return counts


# =============================================================================
# MAIN
# =============================================================================


def process(input_path: str, output_path: str, limit: Optional[int], dry_run: bool) -> None:
    if not os.path.exists(input_path):
        logger.error("Input file not found: %s", input_path)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    total = len(rows)
    # Compute counts on full dataset before applying --limit
    location_counts = compute_location_counts(rows)

    if limit:
        rows = rows[:limit]

    new_cols = ["operator_type", "parent_company", "location_count"]
    output_fields = fieldnames + [c for c in new_cols if c not in fieldnames]

    enriched = []

    for idx, row in enumerate(rows):
        company = row.get("Business Name") or row.get("Company") or ""
        company = company.strip()
        norm = normalize_name(company)

        if not company:
            row.update({"operator_type": "", "parent_company": "", "location_count": ""})
            enriched.append(row)
            continue

        # Name-based detection
        detected = detect_from_name(company)

        # Website-based detection (if not found)
        if not detected and not dry_run:
            website = get_website_from_row(row)
            if website:
                time.sleep(RATE_LIMIT_SECONDS)
                detected = detect_from_website(website, company)

        # Chain inference from dataset frequency
        loc_count = location_counts.get(norm, 1)
        if not detected:
            if loc_count >= 3:
                detected = {"operator_type": "local_chain", "parent_company": company}
            else:
                detected = {"operator_type": "independent", "parent_company": ""}

        row["operator_type"] = detected.get("operator_type", "independent")
        row["parent_company"] = detected.get("parent_company", "")
        row["location_count"] = str(loc_count)

        enriched.append(row)

        logger.info("[%s/%s] %s -> %s (%s)", idx + 1, len(rows), company, row["operator_type"], row["parent_company"])

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(enriched)

    logger.info("\n[DONE] Wrote %s rows to %s", len(enriched), output_path)
    if limit and total > limit:
        logger.info("[INFO] Processed %s/%s rows due to --limit", limit, total)


def main():
    parser = argparse.ArgumentParser(description="Map dispensaries to MSO/local chain/independent")
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT, help=f"Input CSV (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help=f"Output CSV (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows processed")
    parser.add_argument("--dry-run", action="store_true", help="Skip external calls (website fetch)")

    args = parser.parse_args()

    process(args.input, args.output, args.limit, args.dry_run)


if __name__ == "__main__":
    main()
