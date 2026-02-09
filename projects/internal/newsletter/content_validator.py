#!/usr/bin/env python3
"""Pre-composition data validator for newsletter pipeline.

Validates scraped JSON data files BEFORE the composer runs.
Checks:
1. Schema validation (required fields present)
2. Event date sanity (not past, not too far future, parseable)
3. Event deduplication (same name, different dates)
4. Data staleness (scraped_at age)
5. Placeholder detection in required fields
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

from data_contract import DATASET_FILES


# ---------------------------------------------------------------------------
# Schemas: required fields per data type
# ---------------------------------------------------------------------------

SCHEMAS = {
    "events": {
        "file": DATASET_FILES["events"],
        "items_key": "events",
        "required": ["name", "date", "url"],
    },
    "news": {
        "file": DATASET_FILES["news"],
        "items_key": "articles",
        "required": ["headline", "url", "published"],
    },
    "reddit": {
        "file": DATASET_FILES["reddit"],
        "items_key": "posts",
        "required": ["title", "url"],
    },
    "tools": {
        "file": DATASET_FILES["tools"],
        "items_key": "tools",
        "required": ["name", "url"],
    },
    "market": {
        "file": DATASET_FILES["market"],
        "items_key": "market_pulse",
        "required": [],
    },
}

PLACEHOLDER_VALUES = {"n/a", "na", "tbd", "tba", "none", "coming soon", ""}

SECTION_MIN_ITEMS = {
    "news": 3,
    "events": 1,
    "tools": 2,
}

SECTION_MIN_DOMAINS = {
    "news": 1,
    "tools": 1,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    category: str       # schema | date_sanity | duplicate | staleness | placeholder
    severity: str       # error | warning
    item_type: str      # events | news | reddit | tools | pipeline
    message: str
    item_index: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    checked_at: str
    status: str                          # PASS | WARN | FAIL
    issues: List[Issue] = field(default_factory=list)
    summary: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_date(text: str) -> Optional[datetime]:
    """Try multiple date formats and return a datetime or None."""
    if not text:
        return None
    text = text.strip()
    if not text:
        return None

    iso_candidate = text
    if iso_candidate.endswith("Z"):
        iso_candidate = iso_candidate[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(iso_candidate)
    except (ValueError, TypeError):
        pass

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text[:len(text)], fmt)
        except (ValueError, TypeError):
            continue
    return None


def parse_latest_timestamp(data: dict) -> tuple[Optional[datetime], Optional[str]]:
    """Return the best available timestamp from known metadata keys."""
    for field in ("scraped_at", "generated_at", "checked_at"):
        raw_value = data.get(field)
        if raw_value is None:
            continue
        dt = parse_date(str(raw_value))
        if dt is not None:
            return dt, field
    return None, None


def normalize_event_name(name: str) -> str:
    """Normalize an event name for dedup comparison."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    # Strip year suffixes like "2026"
    name = re.sub(r"\s*\d{4}\s*$", "", name)
    return name.strip()


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def validate_schema(data: dict, schema: dict, data_type: str) -> List[Issue]:
    """Check that required fields are present and non-null in each item."""
    issues: List[Issue] = []
    items_key = schema["items_key"]
    required = schema["required"]

    items = data.get(items_key)
    if items is None:
        issues.append(Issue(
            category="schema",
            severity="error",
            item_type=data_type,
            message=f"Missing top-level key '{items_key}' in {schema['file']}",
            suggestion=f"Ensure the scraper outputs a '{items_key}' array.",
        ))
        return issues

    if not isinstance(items, list):
        issues.append(Issue(
            category="schema",
            severity="error",
            item_type=data_type,
            message=f"'{items_key}' is not a list in {schema['file']}",
        ))
        return issues

    if len(items) == 0:
        issues.append(Issue(
            category="schema",
            severity="warning",
            item_type=data_type,
            message=f"'{items_key}' is empty in {schema['file']}",
            suggestion="Check if the scraper ran successfully.",
        ))

    for idx, item in enumerate(items):
        for fld in required:
            val = item.get(fld)
            if val is None or (isinstance(val, str) and val.strip() == ""):
                issues.append(Issue(
                    category="schema",
                    severity="error",
                    item_type=data_type,
                    item_index=idx,
                    message=f"{data_type}[{idx}].{fld} is missing or empty",
                    suggestion=f"Ensure the scraper populates '{fld}'.",
                ))

    return issues


def validate_event_dates(
    events: list,
    max_days_future: int = 365,
) -> List[Issue]:
    """Check event dates are parseable, not past, and not absurdly far out."""
    issues: List[Issue] = []
    now = utc_now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    for idx, event in enumerate(events):
        name = event.get("name", f"event[{idx}]")
        date_str = event.get("date", "")

        dt = parse_date(date_str)
        if dt is None:
            issues.append(Issue(
                category="date_sanity",
                severity="error",
                item_type="events",
                item_index=idx,
                message=f"Cannot parse date '{date_str}' for event '{name}'",
                suggestion="Check the scraper's date extraction for this source.",
            ))
            continue

        # Make timezone-aware for comparison
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        if dt < today:
            days_ago = (today - dt).days
            issues.append(Issue(
                category="date_sanity",
                severity="error",
                item_type="events",
                item_index=idx,
                message=f"Event '{name}' has date {date_str} ({days_ago} day(s) in the past)",
                suggestion="Remove past events or re-scrape for current listings.",
            ))

        future_limit = now + timedelta(days=max_days_future)
        if dt > future_limit:
            issues.append(Issue(
                category="date_sanity",
                severity="warning",
                item_type="events",
                item_index=idx,
                message=f"Event '{name}' is {(dt - now).days} days in the future ({date_str})",
                suggestion="Verify this date is correct; it's unusually far out.",
            ))

    return issues


def detect_event_duplicates(events: list) -> List[Issue]:
    """Flag events with the same normalized name but different dates."""
    issues: List[Issue] = []
    groups: dict[str, list] = defaultdict(list)

    for idx, event in enumerate(events):
        name = event.get("name", "")
        norm = normalize_event_name(name)
        if norm:
            groups[norm].append((idx, event))

    for norm_name, entries in groups.items():
        if len(entries) < 2:
            continue
        dates = set()
        for _, ev in entries:
            dates.add(ev.get("date", "unknown"))
        if len(dates) > 1:
            date_list = ", ".join(sorted(dates))
            indices = [str(i) for i, _ in entries]
            issues.append(Issue(
                category="duplicate",
                severity="error",
                item_type="events",
                message=(
                    f"Event '{entries[0][1].get('name')}' appears {len(entries)} times "
                    f"with conflicting dates: {date_list} (indices: {', '.join(indices)})"
                ),
                suggestion="Deduplicate events; keep the date from the most authoritative source.",
            ))

    return issues


def check_staleness(
    data: dict,
    data_type: str,
    filename: str,
    max_age_days: int = 3,
) -> List[Issue]:
    """Fail when freshness metadata is missing, invalid, or stale."""
    issues: List[Issue] = []
    ts, ts_field = parse_latest_timestamp(data)

    if ts is None:
        issues.append(Issue(
            category="staleness",
            severity="error",
            item_type=data_type,
            message=f"No parseable freshness timestamp in {filename}",
            suggestion="Add a valid 'scraped_at' or 'generated_at' ISO timestamp.",
        ))
        return issues

    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    age = utc_now() - ts
    if age.days > max_age_days:
        issues.append(Issue(
            category="staleness",
            severity="warning",
            item_type=data_type,
            message=(
                f"{data_type} data is {age.days} day(s) old "
                f"({ts_field}={ts.isoformat()})"
            ),
            suggestion=f"Re-run the {data_type} scraper to get fresh data.",
        ))

    return issues


def detect_placeholders(data: dict, schema: dict, data_type: str) -> List[Issue]:
    """Flag placeholder values in required fields."""
    issues: List[Issue] = []
    items_key = schema["items_key"]
    required = schema["required"]
    items = data.get(items_key, [])

    if not isinstance(items, list):
        return issues

    for idx, item in enumerate(items):
        for fld in required:
            val = item.get(fld)
            if isinstance(val, str) and val.strip().lower() in PLACEHOLDER_VALUES:
                issues.append(Issue(
                    category="placeholder",
                    severity="warning",
                    item_type=data_type,
                    item_index=idx,
                    message=f"{data_type}[{idx}].{fld} contains placeholder value: '{val}'",
                    suggestion=f"Replace with real data or remove the item.",
                ))

    return issues


def validate_market_payload(data: dict) -> List[Issue]:
    """Validate market payload structure used by composer."""
    issues: List[Issue] = []

    the_number = data.get("the_number")
    if not isinstance(the_number, dict):
        issues.append(Issue(
            category="schema",
            severity="error",
            item_type="market",
            message="market.the_number is missing or not an object",
            suggestion="Ensure market_data_processor outputs {'the_number': {'value', 'context'}}.",
        ))
    else:
        value = str(the_number.get("value", "")).strip()
        context = str(the_number.get("context", "")).strip()
        if not value:
            issues.append(Issue(
                category="schema",
                severity="error",
                item_type="market",
                message="market.the_number.value is missing",
                suggestion="Provide a verified numeric headline value.",
            ))
        if not context:
            issues.append(Issue(
                category="schema",
                severity="error",
                item_type="market",
                message="market.the_number.context is missing",
                suggestion="Provide context describing what the value represents.",
            ))

    pulse = data.get("market_pulse")
    if not isinstance(pulse, list) or len(pulse) == 0:
        issues.append(Issue(
            category="schema",
            severity="error",
            item_type="market",
            message="market.market_pulse is missing or empty",
            suggestion="Provide at least one verified market pulse item.",
        ))
    elif len(pulse) < 3:
        issues.append(Issue(
            category="minimums",
            severity="error",
            item_type="market",
            message=f"market.market_pulse has {len(pulse)} items (minimum: 3)",
            suggestion="Provide at least 3 market pulse bullets.",
        ))

    trend_card = data.get("demographic_trend_card")
    if not isinstance(trend_card, dict):
        issues.append(Issue(
            category="minimums",
            severity="error",
            item_type="market",
            message="market.demographic_trend_card is missing",
            suggestion="Run ccc_ingest and market_data_processor to include demographic trend card.",
        ))
    else:
        if not str(trend_card.get("insight", "")).strip():
            issues.append(Issue(
                category="minimums",
                severity="error",
                item_type="market",
                message="market.demographic_trend_card.insight is missing",
                suggestion="Include one concise demographic trend insight.",
            ))
        if not str(trend_card.get("source_url", "")).strip():
            issues.append(Issue(
                category="minimums",
                severity="error",
                item_type="market",
                message="market.demographic_trend_card.source_url is missing",
                suggestion="Include at least one cited demographic source URL.",
            ))

    return issues


def _domain_from_url(url: str) -> str:
    match = re.match(r"^https?://([^/]+)", url.strip())
    if not match:
        return ""
    return match.group(1).lower().replace("www.", "")


def validate_section_minimums(data: dict, data_type: str, schema: dict) -> List[Issue]:
    issues: List[Issue] = []
    items_key = schema["items_key"]
    items = data.get(items_key, [])
    if not isinstance(items, list):
        return issues

    min_items = SECTION_MIN_ITEMS.get(data_type)
    if min_items is not None and len(items) < min_items:
        issues.append(Issue(
            category="minimums",
            severity="error",
            item_type=data_type,
            message=f"{data_type} has {len(items)} items (minimum: {min_items})",
            suggestion="Expand source coverage or fallback tiers before composing.",
        ))

    min_domains = SECTION_MIN_DOMAINS.get(data_type)
    if min_domains is not None:
        domains = set()
        for item in items:
            url = str(item.get("url") or "")
            domain = _domain_from_url(url)
            if domain:
                domains.add(domain)
        if len(domains) < min_domains:
            issues.append(Issue(
                category="minimums",
                severity="error",
                item_type=data_type,
                message=f"{data_type} has {len(domains)} distinct domains (minimum: {min_domains})",
                suggestion="Enable additional primary/fallback sources for source diversity.",
            ))

    for idx, item in enumerate(items):
        geo_scope = str(item.get("geo_scope", "ma"))
        if geo_scope != "ma":
            note = str(item.get("why_ma_impact", "")).strip()
            if not note:
                issues.append(Issue(
                    category="minimums",
                    severity="error",
                    item_type=data_type,
                    item_index=idx,
                    message=f"{data_type}[{idx}] is non-MA content without 'why_ma_impact' note",
                    suggestion="Add a clear MA operator relevance explanation for non-MA entries.",
                ))

    return issues


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def determine_status(issues: List[Issue]) -> str:
    if any(i.severity == "error" for i in issues):
        return "FAIL"
    if any(i.severity == "warning" for i in issues):
        return "WARN"
    return "PASS"


def build_summary(issues: List[Issue]) -> dict:
    by_category: dict[str, int] = defaultdict(int)
    by_severity: dict[str, int] = defaultdict(int)
    for i in issues:
        by_category[i.category] += 1
        by_severity[i.severity] += 1
    return {
        "total": len(issues),
        "by_category": dict(by_category),
        "by_severity": dict(by_severity),
    }


def validate_all(
    data_dir: Path,
    max_event_days_future: int = 365,
    max_data_age_days: int = 3,
) -> ValidationReport:
    issues: List[Issue] = []

    for data_type, schema in SCHEMAS.items():
        filepath = data_dir / schema["file"]
        if not filepath.exists():
            issues.append(Issue(
                category="schema",
                severity="error",
                item_type=data_type,
                message=f"Data file not found: {filepath.name}",
                suggestion=f"Run the {data_type} scraper first.",
            ))
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            issues.append(Issue(
                category="schema",
                severity="error",
                item_type=data_type,
                message=f"Cannot read {filepath.name}: {exc}",
            ))
            continue

        # Schema validation
        issues.extend(validate_schema(data, schema, data_type))

        # Staleness
        issues.extend(check_staleness(data, data_type, filepath.name, max_data_age_days))

        # Placeholder detection
        issues.extend(detect_placeholders(data, schema, data_type))

        # Section minimums and non-MA relevance annotation
        if data_type in {"news", "events", "tools"}:
            issues.extend(validate_section_minimums(data, data_type, schema))

        # Event-specific checks
        if data_type == "events":
            events = data.get(schema["items_key"], [])
            if isinstance(events, list):
                issues.extend(validate_event_dates(events, max_event_days_future))
                issues.extend(detect_event_duplicates(events))

        if data_type == "market":
            issues.extend(validate_market_payload(data))

    report = ValidationReport(
        checked_at=utc_now().isoformat().replace("+00:00", "Z"),
        status=determine_status(issues),
        issues=issues,
        summary=build_summary(issues),
    )
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Validate newsletter data before composition")
    parser.add_argument("--data-dir", required=True, help="Path to data directory with scraped JSON")
    parser.add_argument("--output", required=True, help="Path to write validation report JSON")
    parser.add_argument("--max-event-days-future", type=int, default=365)
    parser.add_argument("--max-data-age-days", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_dir = Path(args.data_dir)

    if not data_dir.is_dir():
        print(f"Error: data directory not found: {data_dir}", file=sys.stderr)
        return 1

    report = validate_all(
        data_dir=data_dir,
        max_event_days_future=args.max_event_days_future,
        max_data_age_days=args.max_data_age_days,
    )

    # Serialize
    report_dict = {
        "checked_at": report.checked_at,
        "status": report.status,
        "issues": [asdict(i) for i in report.issues],
        "summary": report.summary,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    print(json.dumps(report_dict, indent=2))

    if report.status == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
