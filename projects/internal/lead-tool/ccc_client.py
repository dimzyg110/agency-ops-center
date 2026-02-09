#!/usr/bin/env python3
"""MA CCC Open Data client with slug-first endpoint fallback and cache."""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


ENDPOINT_ALIASES = {
    "licenses": ["l_licenses", "hmwt-yiqy"],
    "commence_ops": ["l_licenses_commenceops", "vsvr-ti6r", "comm-ops"],
    "commence_ops_legacy": ["vsvr-ti6r", "l_licenses_commenceops"],
    "au_pending": ["l_applications_pending", "piib-tj3f"],
    "all_licenses": ["l_licenses_aumtc", "l_licenses", "hmwt-yiqy"],
    "itd_sales": ["l_itdretaildeliverysalesreport", "dt9b-i6ds"],
    "weekly_sales": ["l_weeklysales", "rqtv-uenj"],
    "avg_price": ["l_averageprice", "g5mj-5pg3"],
    "plant_activity": ["l_auplantsactivityvolume", "fren-z7jq"],
    "facility_sales": ["l_aufacilitysalesstats", "hhjg-atjk"],
    "testing_results": ["l_testingresults", "pt2c-wb44"],
    "equity_demographics": ["4fcd-yu53"],
    "eea_demographics": ["7bkc-njjs"],
    "industry_demographics": ["ss4i-7vyi"],
    "county_report": ["cmmn-f6x2"],
    "total_dbe": ["5dkg-e39p"],
    "applications_rollup": ["meau-plav"],
}


def build_default_client(base_dir: Path) -> "CccClient":
    cache_dir = Path(os.environ.get("CCC_CACHE_DIR", str(base_dir / "data" / "cache" / "ccc")))
    base_url = os.environ.get("CCC_BASE_URL", "https://masscannabiscontrol.com/resource")
    min_interval_sec = float(os.environ.get("CCC_MIN_INTERVAL_SEC", "0.3"))
    return CccClient(base_url=base_url, cache_dir=cache_dir, min_interval_sec=min_interval_sec)


class CccClient:
    def __init__(
        self,
        base_url: str,
        cache_dir: Path,
        timeout_sec: int = 90,
        max_retries: int = 4,
        min_interval_sec: float = 0.3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.cache_dir = cache_dir
        self.timeout_sec = timeout_sec
        self.max_retries = max_retries
        self.min_interval_sec = max(0.0, min_interval_sec)
        self._last_request_monotonic: Optional[float] = None
        self.user_agent = "LeadTool/3.1"
        self.last_fetch_meta: dict[str, Any] = {}
        self._metrics: dict[str, int] = defaultdict(int)
        self._host_attempts: dict[str, int] = defaultdict(int)
        self._host_retries: dict[str, int] = defaultdict(int)
        self._host_failures: dict[str, int] = defaultdict(int)
        self._host_rate_limited: dict[str, int] = defaultdict(int)

    def reset_metrics(self) -> None:
        self._metrics.clear()
        self._host_attempts.clear()
        self._host_retries.clear()
        self._host_failures.clear()
        self._host_rate_limited.clear()

    def snapshot_metrics(self, top_n: int = 10) -> dict[str, Any]:
        hotspots = []
        hosts = set(self._host_attempts) | set(self._host_retries) | set(self._host_failures)
        for host in hosts:
            hotspots.append(
                {
                    "host": host,
                    "attempts": int(self._host_attempts.get(host, 0)),
                    "retries": int(self._host_retries.get(host, 0)),
                    "failures": int(self._host_failures.get(host, 0)),
                    "rate_limited": int(self._host_rate_limited.get(host, 0)),
                }
            )
        hotspots.sort(key=lambda row: (row["attempts"], row["retries"], row["failures"]), reverse=True)
        payload = dict(self._metrics)
        payload["request_hotspots"] = hotspots[: max(1, top_n)]
        return payload

    def endpoint_candidates(self, name_or_id: str) -> list[str]:
        aliases = ENDPOINT_ALIASES.get(name_or_id)
        if aliases:
            return aliases
        return [name_or_id]

    def endpoint_id(self, name_or_id: str) -> str:
        return self.endpoint_candidates(name_or_id)[0]

    def endpoint_url(self, endpoint_id: str) -> str:
        return f"{self.base_url}/{endpoint_id}.json"

    def fetch_all(
        self,
        name_or_id: str,
        page_size: int = 1000,
        max_rows: Optional[int] = None,
        use_cache: bool = True,
        cache_ttl_hours: int = 6,
        where: Optional[str] = None,
        select: Optional[str] = None,
        order: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        page_size = max(1, min(page_size, 50000))
        candidates = self.endpoint_candidates(name_or_id)
        last_error: Optional[Exception] = None

        for endpoint in candidates:
            cache_key = self._cache_key(endpoint, page_size, max_rows, where, select, order)
            if use_cache:
                cached = self._read_cache(cache_key, cache_ttl_hours)
                if cached is not None:
                    self.last_fetch_meta = {
                        "endpoint": endpoint,
                        "cache_key": cache_key,
                        "cache_hit": True,
                        "row_count": len(cached),
                    }
                    return cached

            try:
                rows = self._fetch_endpoint(
                    endpoint=endpoint,
                    page_size=page_size,
                    max_rows=max_rows,
                    where=where,
                    select=select,
                    order=order,
                )
                if use_cache:
                    self._write_cache(cache_key, rows)
                self.last_fetch_meta = {
                    "endpoint": endpoint,
                    "cache_key": cache_key,
                    "cache_hit": False,
                    "row_count": len(rows),
                }
                return rows
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code in (400, 404):
                    continue
                raise
            except urllib.error.URLError as exc:
                last_error = exc
                continue
            except TimeoutError as exc:
                last_error = exc
                continue

        self.last_fetch_meta = {
            "endpoint": None,
            "cache_key": None,
            "cache_hit": False,
            "row_count": 0,
            "error": str(last_error) if last_error else "unknown_error",
        }
        if last_error is not None:
            raise last_error
        return []

    def _fetch_endpoint(
        self,
        endpoint: str,
        page_size: int,
        max_rows: Optional[int],
        where: Optional[str],
        select: Optional[str],
        order: Optional[str],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        offset = 0
        while True:
            params = {"$limit": str(page_size), "$offset": str(offset)}
            if where:
                params["$where"] = where
            if select:
                params["$select"] = select
            if order:
                params["$order"] = order

            self._apply_rate_limit()
            batch = self._request_json(self.endpoint_url(endpoint), params)
            if not isinstance(batch, list):
                break
            rows.extend(batch)
            if len(batch) < page_size:
                break
            if max_rows and len(rows) >= max_rows:
                rows = rows[:max_rows]
                break
            offset += page_size
        return rows

    def _apply_rate_limit(self) -> None:
        if self.min_interval_sec <= 0:
            return
        now = time.monotonic()
        if self._last_request_monotonic is not None:
            elapsed = now - self._last_request_monotonic
            sleep_for = self.min_interval_sec - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
        self._last_request_monotonic = time.monotonic()

    def _request_json(self, url: str, params: dict[str, str]) -> Any:
        query = urllib.parse.urlencode(params)
        request_url = f"{url}?{query}" if query else url
        host = urllib.parse.urlparse(request_url).netloc.lower()
        for attempt in range(1, self.max_retries + 1):
            self._metrics["request_count"] += 1
            if host:
                self._host_attempts[host] += 1
            try:
                req = urllib.request.Request(request_url, headers={"User-Agent": self.user_agent})
                with urllib.request.urlopen(req, timeout=self.timeout_sec) as response:
                    payload = response.read().decode("utf-8-sig")
                    return json.loads(payload)
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    self._metrics["rate_limited_count"] += 1
                    if host:
                        self._host_rate_limited[host] += 1
                if attempt >= self.max_retries:
                    self._metrics["failure_count"] += 1
                    if host:
                        self._host_failures[host] += 1
                    raise
                self._metrics["retry_count"] += 1
                if host:
                    self._host_retries[host] += 1
                time.sleep(min(2**attempt, 16))
            except (urllib.error.URLError, TimeoutError):
                if attempt >= self.max_retries:
                    self._metrics["failure_count"] += 1
                    if host:
                        self._host_failures[host] += 1
                    raise
                self._metrics["retry_count"] += 1
                if host:
                    self._host_retries[host] += 1
                time.sleep(min(2**attempt, 16))
        return []

    def _cache_key(
        self,
        endpoint: str,
        page_size: int,
        max_rows: Optional[int],
        where: Optional[str],
        select: Optional[str],
        order: Optional[str],
    ) -> str:
        payload = {
            "endpoint": endpoint,
            "page_size": page_size,
            "max_rows": max_rows,
            "where": where,
            "select": select,
            "order": order,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        return f"{endpoint}_{digest}"

    def _cache_path(self, cache_key: str) -> Path:
        return self.cache_dir / f"{cache_key}.json"

    def _read_cache(self, cache_key: str, cache_ttl_hours: int) -> Optional[list[dict[str, Any]]]:
        path = self._cache_path(cache_key)
        if not path.exists():
            self._metrics["cache_miss_count"] += 1
            return None
        age_seconds = time.time() - path.stat().st_mtime
        if age_seconds > cache_ttl_hours * 3600:
            self._metrics["cache_miss_count"] += 1
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows = payload.get("rows", [])
            if isinstance(rows, list):
                self._metrics["cache_hit_count"] += 1
                return rows
            self._metrics["cache_miss_count"] += 1
            return None
        except Exception:
            self._metrics["cache_miss_count"] += 1
            return None

    def _write_cache(self, cache_key: str, rows: list[dict[str, Any]]) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path = self._cache_path(cache_key)
        payload = {
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "row_count": len(rows),
            "rows": rows,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
