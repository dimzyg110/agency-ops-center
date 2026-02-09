#!/usr/bin/env python3
"""Market Data Processor for newsletter sections."""

import argparse
import csv
import json
import logging
import os
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def first_existing(candidates: List[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def resolve_default_signals_dir() -> Path:
    env = os.getenv("NEWSLETTER_SIGNALS_DIR")
    if env:
        return Path(env)

    base = Path(__file__).resolve()
    candidates = [
        Path("/data/workspace/projects/lead-tool/output"),
        base.parents[3] / "claude" / "projects" / "lead-tool" / "output",
        base.parents[4] / "claude" / "projects" / "lead-tool" / "output",
        base.parents[3] / "lead-tool" / "output",
        base.parents[3] / "projects" / "lead-tool" / "output",
        Path.cwd() / "projects" / "lead-tool" / "output",
    ]
    return first_existing(candidates)


def resolve_default_snapshot_dir() -> Path:
    env = os.getenv("NEWSLETTER_SNAPSHOT_DIR")
    if env:
        return Path(env)

    base = Path(__file__).resolve()
    candidates = [
        Path("/data/workspace/projects/lead-tool/data/snapshots"),
        base.parents[3] / "claude" / "projects" / "lead-tool" / "data" / "snapshots",
        base.parents[4] / "claude" / "projects" / "lead-tool" / "data" / "snapshots",
        base.parents[3] / "lead-tool" / "data" / "snapshots",
        base.parents[3] / "projects" / "lead-tool" / "data" / "snapshots",
        Path.cwd() / "projects" / "lead-tool" / "data" / "snapshots",
    ]
    return first_existing(candidates)


def resolve_default_ccc_dir() -> Path:
    env = os.getenv("NEWSLETTER_CCC_DIR")
    if env:
        return Path(env)
    base = Path(__file__).resolve()
    return base.parents[1] / "data" / "ccc"


DEFAULT_SIGNALS_DIR = resolve_default_signals_dir()
DEFAULT_SNAPSHOT_DIR = resolve_default_snapshot_dir()
DEFAULT_CCC_DIR = resolve_default_ccc_dir()


def log_event(logger: logging.Logger, event: str, **fields):
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, ensure_ascii=False))


def parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    value = str(value).strip()
    if not value:
        return None

    try:
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except Exception:
        pass

    patterns = ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"]
    for pattern in patterns:
        try:
            return datetime.strptime(value, pattern)
        except Exception:
            continue
    return None


def find_latest_files(pattern: str, directory: Path) -> List[Path]:
    files = list(directory.glob(pattern))
    if not files:
        return []

    def sort_key(path: Path) -> Tuple[int, float]:
        match = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
        if match:
            try:
                dt = datetime.strptime(match.group(1), "%Y-%m-%d")
                return (0, dt.timestamp())
            except Exception:
                pass
        return (1, path.stat().st_mtime)

    files.sort(key=sort_key, reverse=True)
    return files


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def compute_total_operators(rows: List[Dict[str, str]]) -> int:
    names = {row.get("Business Name", "").strip() for row in rows if row.get("Business Name")}
    return len({name for name in names if name})


def compute_avg_distress(rows: List[Dict[str, str]]) -> Optional[float]:
    scores = []
    for row in rows:
        value = row.get("Distress Score")
        if value in (None, ""):
            continue
        try:
            scores.append(float(value))
        except Exception:
            continue
    if not scores:
        return None
    return sum(scores) / len(scores)


def compute_distress_trend(latest: List[Dict[str, str]], previous: List[Dict[str, str]]) -> Optional[float]:
    latest_avg = compute_avg_distress(latest)
    prev_avg = compute_avg_distress(previous)
    if latest_avg is None or prev_avg is None:
        return None
    if prev_avg == 0:
        return None
    return ((latest_avg - prev_avg) / prev_avg) * 100


def compute_hiring_hot(rows: List[Dict[str, str]]) -> List[str]:
    scored = []
    for row in rows:
        name = row.get("Business Name", "").strip()
        if not name:
            continue
        try:
            active_jobs = int(float(row.get("active_jobs") or 0))
        except Exception:
            active_jobs = 0
        hiring_signal = (row.get("hiring_signal") or "").lower()
        if active_jobs <= 0 and hiring_signal not in {"hiring_hot", "hiring_warm"}:
            continue
        try:
            distress = float(row.get("Distress Score") or 0)
        except Exception:
            distress = 0
        scored.append((active_jobs, distress, name))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [item[2] for item in scored[:3]]


def compute_menu_gaps(rows: List[Dict[str, str]]) -> List[str]:
    gaps = Counter()
    for row in rows:
        gap_field = row.get("menu_gaps") or ""
        if not gap_field:
            continue
        parts = [part.strip().lower() for part in re.split(r"[,;]", gap_field) if part.strip()]
        gaps.update(parts)
    return [item for item, _ in gaps.most_common(3)]


def compute_review_velocity_leaders(rows: List[Dict[str, str]]) -> List[str]:
    candidates = []
    has_velocity = any((row.get("review_velocity") or "").strip() for row in rows)
    metric_field = "review_velocity" if has_velocity else "google_review_count"
    for row in rows:
        name = row.get("Business Name", "").strip()
        if not name:
            continue
        value = row.get(metric_field)
        if value in (None, ""):
            continue
        try:
            metric = float(value)
        except Exception:
            continue
        candidates.append((metric, name))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in candidates[:3]]


def compute_new_licenses_from_snapshot(snapshot_path: Path) -> int:
    data = json.loads(snapshot_path.read_text())
    licenses = data.get("licenses", {})
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    count = 0
    for item in licenses.values():
        approved_date = parse_date(item.get("approved_date"))
        if not approved_date:
            continue
        if approved_date.tzinfo is None:
            approved_date = approved_date.replace(tzinfo=timezone.utc)
        if approved_date >= cutoff:
            count += 1
    return count


def compute_active_operators_from_snapshot(snapshot_path: Path) -> int:
    """Count active operators from the CCC snapshot — the real number, not the lead-tool pack."""
    data = json.loads(snapshot_path.read_text())
    licenses = data.get("licenses", {})
    active = sum(1 for lic in licenses.values() if (lic.get("status") or "").lower() == "active")
    return active


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_demographic_trend_card(ccc_dir: Path) -> Optional[Dict[str, Any]]:
    normalized = ccc_dir / "normalized_snapshot.json"
    if normalized.exists():
        payload = load_json(normalized)
        card = payload.get("demographic_trend_card")
        if isinstance(card, dict):
            return card
    return None


def select_the_number(
    total_operators: int,
    distress_rows: List[Dict[str, str]],
    hiring_hot: Optional[List[str]] = None,
    new_licenses: int = 0,
    review_leaders: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Pick the most interesting statistic for THE NUMBER section.

    Rotates through available data to always show something meaningful
    and MA-specific rather than defaulting to a boring percentage.
    """
    candidates: List[Dict[str, str]] = []

    # ── Candidate 1: New licenses (only if interesting) ──
    if new_licenses > 0:
        candidates.append({
            "value": str(new_licenses),
            "context": f"new cannabis license{'s' if new_licenses != 1 else ''} approved in Massachusetts this week",
        })

    # ── Candidate 2: Hiring activity ──
    if hiring_hot:
        hiring_count = 0
        for row in distress_rows:
            try:
                jobs = int(float(row.get("active_jobs") or 0))
                if jobs > 0:
                    hiring_count += 1
            except Exception:
                pass
        if hiring_count > 0:
            candidates.append({
                "value": str(hiring_count),
                "context": f"MA operators are actively hiring — led by {hiring_hot[0]}",
            })

    # ── Candidate 3: Total operator count ──
    if total_operators > 0:
        candidates.append({
            "value": str(total_operators),
            "context": "licensed cannabis operators tracked across Massachusetts this week",
        })

    # ── Candidate 4: Distress count (only if meaningful) ──
    if distress_rows and total_operators > 0:
        high_distress = sum(
            1 for row in distress_rows
            if float(row.get("Distress Score") or 0) >= 150
        )
        if high_distress >= 5:
            candidates.append({
                "value": str(high_distress),
                "context": f"of {total_operators} MA operators are showing elevated distress signals",
            })

    # ── Candidate 5: Review momentum ──
    if review_leaders:
        candidates.append({
            "value": str(len(review_leaders)),
            "context": f"operators leading in review momentum — {review_leaders[0]} is #1",
        })

    if not candidates:
        return {"value": str(total_operators or "N/A"), "context": "operators tracked"}

    # Rotate weekly so the number changes each issue
    week = datetime.now(timezone.utc).isocalendar()[1]
    return candidates[week % len(candidates)]


def main():
    parser = argparse.ArgumentParser(description="Market data processor")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "--signals-dir",
        default=str(DEFAULT_SIGNALS_DIR),
        help="Directory containing operator signal CSV files",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=str(DEFAULT_SNAPSHOT_DIR),
        help="Directory containing CCC snapshot JSON files",
    )
    parser.add_argument(
        "--ccc-dir",
        default=str(DEFAULT_CCC_DIR),
        help="Directory containing normalized CCC ingest outputs",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("market_data_processor")

    signals_dir = Path(args.signals_dir)
    snapshot_dir = Path(args.snapshot_dir)
    ccc_dir = Path(args.ccc_dir)

    signals_files = (
        find_latest_files("ma_operator_signals_full_*.csv", signals_dir)
        or find_latest_files("ma_operator_signals_pack_*.csv", signals_dir)
        or find_latest_files("ma_operator_signals_top150_*.csv", signals_dir)
    )
    places_files = find_latest_files("places_enriched_*.csv", signals_dir) or find_latest_files(
        "places_live_*.csv", signals_dir
    )
    hiring_files = find_latest_files("hiring_signals_*.csv", signals_dir)
    menu_files = find_latest_files("menu_analysis_*.csv", signals_dir)
    snapshot_files = find_latest_files("ccc_snapshot_*.json", snapshot_dir)

    if not signals_files:
        raise FileNotFoundError(
            "No operator signal files found "
            f"in {signals_dir}"
        )

    signals_latest = load_csv(signals_files[0])
    signals_prev = load_csv(signals_files[1]) if len(signals_files) > 1 else []

    places_latest = load_csv(places_files[0]) if places_files else []
    hiring_latest = load_csv(hiring_files[0]) if hiring_files else []
    menu_latest = load_csv(menu_files[0]) if menu_files else []

    total_operators = compute_total_operators(signals_latest)
    
    # Use CCC snapshot for real operator count (not the lead-tool's top-150 pack)
    if snapshot_files:
        ccc_active_count = compute_active_operators_from_snapshot(snapshot_files[0])
        if ccc_active_count > 0:
            total_operators = ccc_active_count
    
    distress_trend = compute_distress_trend(signals_latest, signals_prev)
    hiring_hot = compute_hiring_hot(hiring_latest)
    top_menu_gaps = compute_menu_gaps(menu_latest)
    review_velocity_leaders = compute_review_velocity_leaders(places_latest)
    demographic_trend_card = load_demographic_trend_card(ccc_dir)

    new_licenses = compute_new_licenses_from_snapshot(snapshot_files[0]) if snapshot_files else 0

    market_pulse = []
    if snapshot_files:
        market_pulse.append(f"{new_licenses} new licenses approved in the last 7 days")
    if distress_trend is not None:
        trend_word = "up" if distress_trend >= 0 else "down"
        market_pulse.append(
            f"Average distress score {trend_word} {abs(distress_trend):.1f}% vs prior pack"
        )
    if top_menu_gaps:
        market_pulse.append(f"{top_menu_gaps[0].title()} remains the top menu gap category")
    if hiring_hot:
        market_pulse.append(f"Hiring heat led by {', '.join(hiring_hot)}")
    if review_velocity_leaders:
        market_pulse.append(f"Review momentum leaders: {', '.join(review_velocity_leaders)}")
    if demographic_trend_card and demographic_trend_card.get("insight"):
        market_pulse.append(str(demographic_trend_card["insight"]))

    market_pulse = market_pulse[:5]

    source_health = [
        {
            "dataset": "signals",
            "status": "success" if signals_files else "failed",
            "source_file": signals_files[0].name if signals_files else None,
            "row_count": len(signals_latest),
        },
        {
            "dataset": "ccc_demographics",
            "status": "success" if demographic_trend_card else "empty",
            "source_file": "normalized_snapshot.json" if demographic_trend_card else None,
            "row_count": 1 if demographic_trend_card else 0,
        },
    ]

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "the_number": select_the_number(
            total_operators, signals_latest,
            hiring_hot=hiring_hot,
            new_licenses=new_licenses,
            review_leaders=review_velocity_leaders,
        ),
        "market_pulse": market_pulse,
        "demographic_trend_card": demographic_trend_card,
        "source_health": source_health,
        "coverage": {
            "dataset_count": 2,
            "successful_datasets": len([x for x in source_health if x["status"] == "success"]),
        },
        "freshness": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        "relevance": {
            "demographic_signal_included": bool(demographic_trend_card),
        },
        "insights": {
            "total_operators": total_operators,
            "new_licenses": new_licenses,
            "average_distress_trend_pct": round(distress_trend, 2) if distress_trend is not None else None,
            "hiring_hot": hiring_hot,
            "top_menu_gaps": top_menu_gaps,
            "review_velocity_leaders": review_velocity_leaders,
            "source_files": {
                "signals_latest": signals_files[0].name if signals_files else None,
                "signals_previous": signals_files[1].name if len(signals_files) > 1 else None,
                "places_latest": places_files[0].name if places_files else None,
                "hiring_latest": hiring_files[0].name if hiring_files else None,
                "menu_latest": menu_files[0].name if menu_files else None,
                "snapshot_latest": snapshot_files[0].name if snapshot_files else None,
                "ccc_normalized": "normalized_snapshot.json" if demographic_trend_card else None,
            },
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))

    log_event(logger, "output_written", output=str(output_path))


if __name__ == "__main__":
    main()
