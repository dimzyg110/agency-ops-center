#!/usr/bin/env python3
from __future__ import annotations
"""Newsletter draft quality checker.

Validates:
1) Links (HEAD requests)
2) Duplicates vs previous issues
3) Variety by source
4) Required sections present & non-empty
5) Placeholder text detection (N/A, TBD, etc.)
6) Event date format validation
7) Date consistency vs source JSON
8) Minimum content thresholds per section
"""

import argparse
import concurrent.futures
import datetime as _dt
import json
import os
import re
import sys
import threading
import time
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from data_contract import DATASET_FILES


URL_REGEX = re.compile(r"https?://[^\s)\]>\"']+")
MD_LINK_REGEX = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
DATE_REGEX = re.compile(r"(\d{4}-\d{2}-\d{2})")
HEADING_REGEX = re.compile(r"^(#{2,6})\s+(.*)\s*$")

DEFAULT_REQUIRED_SECTIONS = [
    "top_story",
    "license_watch",
    "market_pulse",
    "demographic_equity_signal",
    "tool_of_the_week",
    "events",
    "quick_hits",
    "the_number",
    "margin_tip",
]

SECTION_ALIASES = {
    "top story": "top_story",
    "license watch": "license_watch",
    "market pulse": "market_pulse",
    "demographic equity signal": "demographic_equity_signal",
    "tool of the week": "tool_of_the_week",
    "event calendar": "events",
    "upcoming events": "events",
    "events": "events",
    "quick hits": "quick_hits",
    "the number": "the_number",
    "margin tip": "margin_tip",
}

GENERIC_LINK_TITLES = {
    "read more",
    "check it out",
    "learn more",
    "source",
    "link",
}

SECTION_MIN_LINKS = {
    "top_story": 1,
    "demographic_equity_signal": 1,
    "tool_of_the_week": 1,
    "quick_hits": 1,
    "events": 1,
}

LINK_CHECK_MAX_WORKERS = int(os.getenv("NEWSLETTER_LINKCHECK_WORKERS", "6"))
LINK_CHECK_MIN_INTERVAL_SEC = float(os.getenv("NEWSLETTER_LINKCHECK_MIN_INTERVAL_SEC", "0.35"))
_LINK_CHECK_LOCK = threading.Lock()
_LAST_LINK_CHECK_BY_HOST: dict[str, float] = {}


def normalize_heading(text: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip().lower()
    return SECTION_ALIASES.get(clean, clean.replace(" ", "_"))


def extract_urls(text: str):
    return sorted(set(URL_REGEX.findall(text)))


def extract_md_links(text: str):
    return MD_LINK_REGEX.findall(text)


def check_url(url: str, timeout: int = 10):
    req_headers = {"User-Agent": "newsletter-quality-checker/1.0"}
    host = urlparse(url).netloc.lower()
    if host and LINK_CHECK_MIN_INTERVAL_SEC > 0:
        with _LINK_CHECK_LOCK:
            now = time.monotonic()
            last = _LAST_LINK_CHECK_BY_HOST.get(host)
            if last is not None:
                sleep_for = LINK_CHECK_MIN_INTERVAL_SEC - (now - last)
                if sleep_for > 0:
                    time.sleep(sleep_for)
            _LAST_LINK_CHECK_BY_HOST[host] = time.monotonic()
    try:
        head_req = Request(url, headers=req_headers, method="HEAD")
        with urlopen(head_req, timeout=timeout) as resp:
            status = getattr(resp, "status", resp.getcode())
            return url, status
    except HTTPError as exc:
        if exc.code in {401, 403, 405}:
            try:
                get_req = Request(url, headers=req_headers, method="GET")
                with urlopen(get_req, timeout=timeout) as resp:
                    status = getattr(resp, "status", resp.getcode())
                    return url, status
            except (HTTPError, URLError):
                return url, None
        return url, exc.code
    except URLError:
        return url, None


def link_validator(urls):
    issues = []
    if not urls:
        return issues
    with concurrent.futures.ThreadPoolExecutor(max_workers=LINK_CHECK_MAX_WORKERS) as executor:
        futures = [executor.submit(check_url, url) for url in urls]
        for fut in concurrent.futures.as_completed(futures):
            url, status = fut.result()
            if status is None or status >= 400:
                issues.append({"type": "broken_link", "url": url, "status": status})
    return issues


def parse_sections(draft_text: str):
    lines = draft_text.splitlines()
    sections = []
    current = None
    buffer = []

    def flush():
        nonlocal current, buffer
        if current is None:
            return
        content = "\n".join(buffer).strip()
        sections.append((current, content))
        buffer = []

    for line in lines:
        match = HEADING_REGEX.match(line)
        if match:
            flush()
            heading_text = match.group(2).strip()
            current = heading_text
        else:
            buffer.append(line)
    flush()
    return sections


def section_validator(draft_text: str, required_sections):
    issues = []
    found = {}
    sections = parse_sections(draft_text)
    section_map = {}
    for heading, content in sections:
        key = normalize_heading(heading)
        section_map[key] = content

    for key in required_sections:
        present = key in section_map
        found[key] = present
        if not present:
            issues.append({"type": "missing_section", "section": key})
        else:
            content = section_map[key]
            if not re.search(r"[A-Za-z0-9]", content or ""):
                issues.append({"type": "empty_section", "section": key})

    return issues, found


def section_link_validator(draft_text: str, min_links=None):
    """Require citation links in core sections."""
    issues = []
    thresholds = min_links or SECTION_MIN_LINKS
    sections = parse_sections(draft_text)
    section_map = {}
    for heading, content in sections:
        section_map[normalize_heading(heading)] = content

    for section_key, min_count in thresholds.items():
        content = section_map.get(section_key)
        if content is None:
            continue
        link_count = len(MD_LINK_REGEX.findall(content))
        if link_count < min_count:
            issues.append({
                "type": "section_missing_links",
                "section": section_key,
                "minimum": min_count,
                "actual": link_count,
                "message": (
                    f"Section '{section_key}' has {link_count} citation link(s); "
                    f"minimum required is {min_count}"
                ),
            })
    return issues


def extract_items_with_sources(draft_text: str):
    items = []
    for line in draft_text.splitlines():
        for title, url in MD_LINK_REGEX.findall(line):
            source = None
            trailing = line.split(")", 1)[-1] if ")" in line else ""
            dash_match = re.search(r"[—\-–]\s*([A-Za-z0-9 .&/]+)", trailing)
            paren_match = re.search(r"\(([^)]+)\)", trailing)
            if dash_match:
                source = dash_match.group(1).strip()
            elif paren_match:
                source = paren_match.group(1).strip()
            else:
                domain = urlparse(url).netloc
                source = domain.replace("www.", "").split(":")[0]
            items.append({"title": title.strip(), "url": url, "source": source})
    return items


def variety_checker(items):
    issues = []
    if not items:
        return issues
    counts = Counter([i["source"] for i in items if i.get("source")])
    total = sum(counts.values())
    if total == 0:
        return issues
    source, count = counts.most_common(1)[0]
    percent = round((count / total) * 100)
    if percent > 50:
        issues.append({"type": "low_variety", "source": source, "percent": percent})
    return issues


def find_previous_issue_files(draft_path: str, history_dirs=None):
    history_dirs = history_dirs or []
    draft_dir = os.path.dirname(os.path.abspath(draft_path))
    base_root = os.path.abspath(os.path.join(draft_dir, os.pardir, os.pardir))

    candidates = set()
    if os.path.isdir(draft_dir):
        candidates.add(draft_dir)
    for hd in history_dirs:
        if hd and os.path.isdir(hd):
            candidates.add(os.path.abspath(hd))

    # Common newsletter locations
    for rel in [
        "projects/newsletter/output/drafts",
        "projects/newsletter/output/archive",
        "projects/newsletter/data/history",
    ]:
        path = os.path.join(base_root, rel)
        if os.path.isdir(path):
            candidates.add(path)

    files = []
    for folder in candidates:
        for name in os.listdir(folder):
            if not name.endswith(".md"):
                continue
            path = os.path.join(folder, name)
            if os.path.abspath(path) == os.path.abspath(draft_path):
                continue
            files.append(path)
    return sorted(set(files))


def extract_date_from_filename(path: str):
    match = DATE_REGEX.search(os.path.basename(path))
    return match.group(1) if match else None


def duplicate_detector(draft_text: str, draft_path: str, history_dirs=None):
    issues = []
    items = extract_items_with_sources(draft_text)
    current_urls = {i["url"] for i in items}
    current_titles = {
        i["title"].lower()
        for i in items
        if i["title"].strip().lower() not in GENERIC_LINK_TITLES
    }

    seen = set()
    for prev_path in find_previous_issue_files(draft_path, history_dirs=history_dirs):
        try:
            with open(prev_path, "r", encoding="utf-8") as f:
                prev_text = f.read()
        except OSError:
            continue

        prev_items = extract_items_with_sources(prev_text)
        last_seen = extract_date_from_filename(prev_path) or os.path.basename(prev_path)
        for item in prev_items:
            title_key = item["title"].lower()
            url = item["url"]
            if title_key in GENERIC_LINK_TITLES:
                title_key = ""
            if url in current_urls or (title_key and title_key in current_titles):
                sig = (url, title_key or "-", last_seen)
                if sig in seen:
                    continue
                seen.add(sig)
                issues.append({
                    "type": "duplicate",
                    "headline": item["title"],
                    "url": url,
                    "last_seen": last_seen,
                })
    return issues


# ---------------------------------------------------------------------------
# New validators (placeholder, date format, date consistency, content depth)
# ---------------------------------------------------------------------------

PLACEHOLDER_PATTERNS = [
    re.compile(r"(?<!\w)N/?A(?!\w)", re.IGNORECASE),
    re.compile(r"(?<!\w)TBD(?!\w)", re.IGNORECASE),
    re.compile(r"(?<!\w)TBA(?!\w)", re.IGNORECASE),
    re.compile(r"No\s+(?:summary|data|market data|information)\s+available", re.IGNORECASE),
    re.compile(r"(?<!\w)Coming\s+soon(?!\w)", re.IGNORECASE),
]

DEFAULT_MIN_WORDS = {
    "top_story": 30,
    "market_pulse": 15,
    "demographic_equity_signal": 12,
    "quick_hits": 20,
    "events": 10,
    "the_number": 8,
    "margin_tip": 10,
}


def placeholder_detector(draft_text: str):
    """Flag placeholder text like N/A, TBD, 'No summary available' in draft."""
    issues = []
    sections = parse_sections(draft_text)
    for heading, content in sections:
        section_key = normalize_heading(heading)
        for line_offset, line in enumerate(content.splitlines()):
            for pattern in PLACEHOLDER_PATTERNS:
                match = pattern.search(line)
                if match:
                    issues.append({
                        "type": "placeholder_text",
                        "section": section_key,
                        "text": match.group(0),
                        "line": line.strip()[:120],
                    })
    return issues


def _parse_date_str(text: str):
    """Try common date formats, return datetime or None."""
    text = text.strip()
    for fmt in ["%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"]:
        try:
            return _dt.datetime.strptime(text, fmt)
        except (ValueError, TypeError):
            continue
    return None


def event_date_format_validator(draft_text: str):
    """Extract dates from the events section and validate they parse."""
    issues = []
    sections = parse_sections(draft_text)
    events_content = None
    for heading, content in sections:
        key = normalize_heading(heading)
        if "event" in key:
            events_content = content
            break

    if events_content is None:
        return issues

    # Extract date-like strings from each event line
    for line in events_content.splitlines():
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Look for YYYY-MM-DD
        iso_dates = DATE_REGEX.findall(line)
        for ds in iso_dates:
            dt = _parse_date_str(ds)
            if dt is None:
                issues.append({
                    "type": "event_date_format_invalid",
                    "date_string": ds,
                    "line": line_stripped[:120],
                    "message": f"Date '{ds}' could not be parsed",
                })

        # Look for written dates like "February 20, 2026"
        written = re.findall(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:[-–]\d{1,2})?,?\s*\d{4}",
            line,
            re.IGNORECASE,
        )
        for ws in written:
            # Ranges like "Feb 20-21, 2026" — take the start date
            clean = re.sub(r"[-–]\d{1,2}", "", ws)
            dt = _parse_date_str(clean)
            if dt is None:
                issues.append({
                    "type": "event_date_format_invalid",
                    "date_string": ws,
                    "line": line_stripped[:120],
                    "message": f"Date '{ws}' could not be parsed",
                })

    return issues


def date_consistency_checker(draft_text: str, data_dir):
    """Compare event dates in the draft against the source JSON."""
    issues = []
    if data_dir is None:
        return issues

    data_path = Path(data_dir) / DATASET_FILES["events"]
    if not data_path.exists():
        return issues

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            source_data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return issues

    # Build lookup: normalized name -> source date
    source_events = {}
    for ev in source_data.get("events", []):
        name = ev.get("name", "")
        date = ev.get("date", "")
        norm = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()
        norm = re.sub(r"\s+", " ", norm)
        token_set = {w for w in norm.split() if len(w) >= 4}
        source_events[norm] = {"name": name, "date": date, "tokens": token_set}

    # Extract events from draft
    sections = parse_sections(draft_text)
    events_content = None
    for heading, content in sections:
        key = normalize_heading(heading)
        if "event" in key:
            events_content = content
            break

    if events_content is None:
        return issues

    for line in events_content.splitlines():
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Try to match against source events
        line_lower = re.sub(r"[^a-z0-9\s]", "", line_stripped.lower())
        line_lower = re.sub(r"\s+", " ", line_lower)
        line_tokens = {w for w in line_lower.split() if len(w) >= 4}

        for norm_name, source in source_events.items():
            source_tokens = source.get("tokens", set())
            token_overlap = len(source_tokens & line_tokens) if source_tokens else 0
            overlap_ratio = (token_overlap / len(source_tokens)) if source_tokens else 0

            # Match on strong full-name match or high token overlap.
            if norm_name not in line_lower and not (token_overlap >= 2 and overlap_ratio >= 0.6):
                continue

            # Extract dates from this draft line
            draft_dates = DATE_REGEX.findall(line_stripped)
            if not draft_dates:
                continue

            source_date = source["date"]
            for dd in draft_dates:
                if dd != source_date:
                    issues.append({
                        "type": "date_consistency_mismatch",
                        "event": source["name"],
                        "draft_date": dd,
                        "source_date": source_date,
                        "message": (
                            f"Event '{source['name']}' shows date {dd} in draft "
                            f"but source JSON has {source_date}"
                        ),
                    })

    return issues


def content_threshold_validator(draft_text: str, min_words=None):
    """Ensure sections meet minimum word count thresholds."""
    issues = []
    thresholds = min_words or DEFAULT_MIN_WORDS
    sections = parse_sections(draft_text)
    section_map = {}
    for heading, content in sections:
        key = normalize_heading(heading)
        section_map[key] = content

    for section_key, min_count in thresholds.items():
        content = section_map.get(section_key, "")
        word_count = len(re.findall(r"\w+", content))
        if word_count < min_count:
            issues.append({
                "type": "section_too_sparse",
                "section": section_key,
                "word_count": word_count,
                "minimum": min_count,
                "message": f"Section '{section_key}' has {word_count} words (minimum: {min_count})",
            })

    return issues


# ---------------------------------------------------------------------------
# Status determination
# ---------------------------------------------------------------------------

FAIL_TYPES = {
    "broken_link",
    "missing_section",
    "empty_section",
    "section_missing_links",
    "placeholder_text",
    "date_consistency_mismatch",
    "event_date_format_invalid",
    "section_too_sparse",
}


def determine_status(issues):
    if any(i["type"] in FAIL_TYPES for i in issues):
        return "FAIL"
    if issues:
        return "WARN"
    return "PASS"


def parse_args():
    parser = argparse.ArgumentParser(description="Newsletter quality checker")
    parser.add_argument("--draft", required=True, help="Path to draft markdown")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    parser.add_argument(
        "--required-sections",
        help="Comma-separated list of required section keys (e.g. top_story,market_pulse)",
    )
    parser.add_argument(
        "--history-dir",
        action="append",
        default=[],
        help="Additional directory to search for previous issues (repeatable)",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Path to data directory for date consistency checks",
    )
    parser.add_argument(
        "--skip-link-check",
        action="store_true",
        help="Skip outbound URL checks (useful in restricted network environments).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        with open(args.draft, "r", encoding="utf-8") as f:
            draft_text = f.read()
    except OSError as exc:
        print(f"Failed to read draft: {exc}", file=sys.stderr)
        sys.exit(1)

    required_sections = DEFAULT_REQUIRED_SECTIONS
    if args.required_sections:
        required_sections = [s.strip() for s in args.required_sections.split(",") if s.strip()]

    urls = extract_urls(draft_text)
    issues = []

    if not args.skip_link_check:
        issues.extend(link_validator(urls))

    dupe_issues = duplicate_detector(draft_text, args.draft, history_dirs=args.history_dir)
    issues.extend(dupe_issues)

    items = extract_items_with_sources(draft_text)
    issues.extend(variety_checker(items))

    section_issues, sections_found = section_validator(draft_text, required_sections)
    issues.extend(section_issues)
    issues.extend(section_link_validator(draft_text))

    # New validators
    issues.extend(placeholder_detector(draft_text))
    issues.extend(event_date_format_validator(draft_text))
    issues.extend(date_consistency_checker(draft_text, args.data_dir))
    issues.extend(content_threshold_validator(draft_text))

    status = determine_status(issues)
    report = {
        "checked_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "issues": issues,
        "sections": sections_found,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    if status == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
