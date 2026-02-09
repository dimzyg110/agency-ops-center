#!/usr/bin/env python3
"""Fetch and normalize CCC datasets for downstream newsletter stages."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


BASE_URL = "https://masscannabiscontrol.com/resource"
USER_AGENT = "newsletter-ccc-ingest/1.0"

DATASET_ALIASES: Dict[str, List[str]] = {
    "licenses": ["l_licenses", "hmwt-yiqy"],
    "pending_applications": ["l_applications_pending", "piib-tj3f"],
    "commence_operations": ["l_licenses_commenceops", "vsvr-ti6r"],
    "weekly_sales": ["l_weeklysales", "rqtv-uenj"],
    "average_price": ["l_averageprice", "g5mj-5pg3"],
    "plant_activity": ["l_auplantsactivityvolume", "fren-z7jq"],
    "facility_sales": ["l_aufacilitysalesstats", "hhjg-atjk"],
    "testing_results": ["l_testingresults", "pt2c-wb44"],
    "equity_demographics": ["4fcd-yu53", "l_socialequitydemographics"],
    "eea_demographics": ["7bkc-njjs", "l_eeademographics"],
    "industry_demographics": ["ss4i-7vyi", "l_industrydemographics"],
    "county_report": ["cmmn-f6x2", "l_countyreport"],
    "total_dbe": ["5dkg-e39p", "l_totaldbe"],
    "applications_rollup": ["meau-plav", "l_totalapplicationssubmitted"],
}

CORE_DATASETS = [
    "licenses",
    "pending_applications",
    "commence_operations",
    "weekly_sales",
    "average_price",
    "plant_activity",
    "facility_sales",
    "testing_results",
]

DEMOGRAPHIC_DATASETS = [
    "equity_demographics",
    "eea_demographics",
    "industry_demographics",
    "county_report",
    "total_dbe",
    "applications_rollup",
]


@dataclass
class DatasetResult:
    dataset_key: str
    endpoint: Optional[str]
    status: str
    row_count: int
    error: Optional[str]
    rows: List[Dict[str, Any]]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _request_json(url: str, params: Dict[str, str], timeout_sec: int, retries: int) -> Any:
    query = urllib.parse.urlencode(params)
    request_url = f"{url}?{query}" if query else url
    last_error: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(request_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                payload = response.read().decode("utf-8-sig")
                return json.loads(payload)
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2 ** attempt, 8))
    if last_error:
        raise last_error
    return []


def _fetch_endpoint_rows(
    endpoint: str,
    *,
    page_size: int,
    max_rows: int,
    timeout_sec: int,
    retries: int,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    offset = 0
    while True:
        batch = _request_json(
            f"{BASE_URL}/{endpoint}.json",
            {"$limit": str(page_size), "$offset": str(offset)},
            timeout_sec=timeout_sec,
            retries=retries,
        )
        if not isinstance(batch, list):
            break
        rows.extend(batch)
        if len(batch) < page_size or len(rows) >= max_rows:
            break
        offset += page_size
    return rows[:max_rows]


def fetch_dataset(
    dataset_key: str,
    *,
    page_size: int,
    max_rows: int,
    timeout_sec: int,
    retries: int,
) -> DatasetResult:
    endpoints = DATASET_ALIASES.get(dataset_key, [])
    for endpoint in endpoints:
        try:
            rows = _fetch_endpoint_rows(
                endpoint,
                page_size=page_size,
                max_rows=max_rows,
                timeout_sec=timeout_sec,
                retries=retries,
            )
            return DatasetResult(
                dataset_key=dataset_key,
                endpoint=endpoint,
                status="success" if rows else "empty",
                row_count=len(rows),
                error=None,
                rows=rows,
            )
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 400):
                continue
            return DatasetResult(
                dataset_key=dataset_key,
                endpoint=endpoint,
                status="failed",
                row_count=0,
                error=f"HTTP {exc.code}",
                rows=[],
            )
        except Exception as exc:
            return DatasetResult(
                dataset_key=dataset_key,
                endpoint=endpoint,
                status="failed",
                row_count=0,
                error=str(exc),
                rows=[],
            )
    return DatasetResult(
        dataset_key=dataset_key,
        endpoint=None,
        status="failed",
        row_count=0,
        error="No viable endpoint alias resolved",
        rows=[],
    )


def _parse_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    raw = str(value).strip().replace(",", "").replace("$", "")
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _extract_period(row: Dict[str, Any]) -> Optional[str]:
    candidates = [
        "year",
        "report_year",
        "date",
        "report_date",
        "week",
        "month",
        "period",
    ]
    for key in candidates:
        if key in row and str(row[key]).strip():
            return str(row[key]).strip()
    for key, value in row.items():
        key_l = key.lower()
        if any(token in key_l for token in candidates):
            value_s = str(value).strip()
            if value_s:
                return value_s
    return None


def _numeric_keys(rows: Iterable[Dict[str, Any]]) -> List[str]:
    keys: Dict[str, int] = {}
    for row in rows:
        for key, value in row.items():
            if _parse_number(value) is not None:
                keys[key] = keys.get(key, 0) + 1
    ordered = sorted(keys.items(), key=lambda item: item[1], reverse=True)
    return [item[0] for item in ordered]


def derive_demographic_trends(results: Dict[str, DatasetResult]) -> List[Dict[str, Any]]:
    trends: List[Dict[str, Any]] = []
    for dataset_key in DEMOGRAPHIC_DATASETS:
        result = results.get(dataset_key)
        if not result or not result.rows:
            continue
        numeric_keys = _numeric_keys(result.rows)
        if not numeric_keys:
            continue
        value_key = numeric_keys[0]
        grouped: Dict[str, float] = {}
        for row in result.rows:
            period = _extract_period(row) or "current"
            value = _parse_number(row.get(value_key))
            if value is None:
                continue
            grouped[period] = grouped.get(period, 0.0) + value

        if len(grouped) >= 2:
            periods = sorted(grouped.keys())
            prior_period = periods[-2]
            latest_period = periods[-1]
            prior_value = grouped[prior_period]
            latest_value = grouped[latest_period]
            change_pct = None
            if prior_value:
                change_pct = ((latest_value - prior_value) / prior_value) * 100
            trends.append(
                {
                    "dataset_key": dataset_key,
                    "metric": value_key,
                    "latest_period": latest_period,
                    "latest_value": round(latest_value, 2),
                    "prior_period": prior_period,
                    "prior_value": round(prior_value, 2),
                    "change_pct": round(change_pct, 2) if change_pct is not None else None,
                    "source_endpoint": result.endpoint,
                    "source_url": f"{BASE_URL}/{result.endpoint}" if result.endpoint else None,
                }
            )
        else:
            only_period = next(iter(grouped.keys()))
            trends.append(
                {
                    "dataset_key": dataset_key,
                    "metric": value_key,
                    "latest_period": only_period,
                    "latest_value": round(grouped[only_period], 2),
                    "prior_period": None,
                    "prior_value": None,
                    "change_pct": None,
                    "source_endpoint": result.endpoint,
                    "source_url": f"{BASE_URL}/{result.endpoint}" if result.endpoint else None,
                }
            )
    return trends


def build_demographic_trend_card(trends: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not trends:
        return None
    # Prefer rows with computed change percentages.
    sorted_trends = sorted(
        trends,
        key=lambda row: (
            row.get("change_pct") is not None,
            abs(float(row.get("change_pct") or 0)),
        ),
        reverse=True,
    )
    selected = sorted_trends[0]
    change_pct = selected.get("change_pct")
    if change_pct is None:
        insight = (
            f"{selected['dataset_key']} reports {selected['latest_value']} for {selected['metric']} in {selected['latest_period']}."
        )
    else:
        direction = "up" if float(change_pct) >= 0 else "down"
        insight = (
            f"{selected['dataset_key']} is {direction} {abs(float(change_pct)):.1f}% "
            f"({selected['prior_period']} -> {selected['latest_period']}) for {selected['metric']}."
        )
    implication = (
        "MA operator implication: demographic and equity shifts can change competitive intensity, "
        "licensing pathways, and local demand strategy."
    )
    return {
        "insight": insight,
        "ma_operator_implication": implication,
        "metric": selected["metric"],
        "source_dataset": selected["dataset_key"],
        "source_url": selected.get("source_url"),
    }


def persist_dataset_rows(ccc_dir: Path, result: DatasetResult) -> str:
    path = ccc_dir / f"{result.dataset_key}.json"
    payload = {
        "dataset_key": result.dataset_key,
        "endpoint": result.endpoint,
        "status": result.status,
        "row_count": result.row_count,
        "generated_at": utc_now_iso(),
        "rows": result.rows,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return path.name


def main() -> int:
    parser = argparse.ArgumentParser(description="CCC ingest and normalization stage")
    parser.add_argument("--output", required=True, help="Path for stage output JSON")
    parser.add_argument("--page-size", type=int, default=1000, help="Rows per request page")
    parser.add_argument("--max-rows", type=int, default=50000, help="Max rows per dataset")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds")
    parser.add_argument("--retries", type=int, default=3, help="HTTP retries")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ccc_dir = output_path.parent / "ccc"
    ccc_dir.mkdir(parents=True, exist_ok=True)

    requested = CORE_DATASETS + DEMOGRAPHIC_DATASETS
    results: Dict[str, DatasetResult] = {}
    source_health: List[Dict[str, Any]] = []
    files_written: Dict[str, str] = {}

    for key in requested:
        started = time.perf_counter()
        result = fetch_dataset(
            key,
            page_size=args.page_size,
            max_rows=args.max_rows,
            timeout_sec=args.timeout,
            retries=args.retries,
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        results[key] = result
        files_written[key] = persist_dataset_rows(ccc_dir, result)
        source_health.append(
            {
                "dataset_key": key,
                "endpoint": result.endpoint,
                "status": result.status,
                "row_count": result.row_count,
                "latency_ms": elapsed_ms,
                "error": result.error,
            }
        )

    demographic_trends = derive_demographic_trends(results)
    demographic_trend_card = build_demographic_trend_card(demographic_trends)

    normalized_payload = {
        "generated_at": utc_now_iso(),
        "core_datasets": {key: {"row_count": results[key].row_count, "status": results[key].status} for key in CORE_DATASETS},
        "demographic_datasets": {
            key: {"row_count": results[key].row_count, "status": results[key].status}
            for key in DEMOGRAPHIC_DATASETS
        },
        "demographic_trends": demographic_trends,
        "demographic_trend_card": demographic_trend_card,
    }
    (ccc_dir / "normalized_snapshot.json").write_text(json.dumps(normalized_payload, ensure_ascii=False, indent=2))

    failed = [row for row in source_health if row["status"] == "failed"]
    status = "success" if not failed else "warn"
    output_payload = {
        "generated_at": utc_now_iso(),
        "status": status,
        "source_health": source_health,
        "coverage": {
            "dataset_count": len(requested),
            "successful_datasets": len([row for row in source_health if row["status"] == "success"]),
            "empty_datasets": len([row for row in source_health if row["status"] == "empty"]),
            "failed_datasets": len(failed),
        },
        "freshness": {"generated_at": utc_now_iso()},
        "relevance": {"demographic_trends_count": len(demographic_trends)},
        "demographic_trends": demographic_trends,
        "demographic_trend_card": demographic_trend_card,
        "storage": {"ccc_dir": str(ccc_dir), "files": files_written},
    }
    output_path.write_text(json.dumps(output_payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
