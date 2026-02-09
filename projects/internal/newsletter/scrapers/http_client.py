#!/usr/bin/env python3
"""Shared HTTP fetch helpers with per-host RPS throttling and retries."""

from __future__ import annotations

import email.utils
import os
import random
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from typing import Optional

try:
    import requests as _requests  # type: ignore
except Exception:  # pragma: no cover
    _requests = None


DEFAULT_TIMEOUT_SEC = int(os.getenv("NEWSLETTER_FETCH_TIMEOUT_SEC", "20"))
DEFAULT_RETRIES = int(os.getenv("NEWSLETTER_FETCH_RETRIES", "3"))
DEFAULT_MIN_INTERVAL_SEC = float(os.getenv("NEWSLETTER_FETCH_MIN_INTERVAL_SEC", "1.2"))
DEFAULT_CIRCUIT_FAILURES = int(os.getenv("NEWSLETTER_FETCH_CIRCUIT_FAILURES", "3"))
DEFAULT_CIRCUIT_COOLDOWN_SEC = float(os.getenv("NEWSLETTER_FETCH_CIRCUIT_COOLDOWN_SEC", "45"))

_METRICS_LOCK = threading.Lock()
_METRICS = defaultdict(int)


def _inc_metric(name: str, value: int = 1) -> None:
    with _METRICS_LOCK:
        _METRICS[name] += value


def snapshot_metrics() -> dict[str, int]:
    with _METRICS_LOCK:
        return dict(_METRICS)


def reset_metrics() -> None:
    with _METRICS_LOCK:
        _METRICS.clear()


class HostRateLimiter:
    def __init__(self, min_interval_sec: float = DEFAULT_MIN_INTERVAL_SEC) -> None:
        self.min_interval_sec = max(0.0, min_interval_sec)
        self._last_request_by_host: dict[str, float] = {}
        self._lock = threading.Lock()

    def wait(self, url: str, min_interval_sec: Optional[float] = None) -> None:
        interval = self.min_interval_sec if min_interval_sec is None else max(0.0, min_interval_sec)
        if interval <= 0:
            return
        host = urllib.parse.urlparse(url).netloc.lower()
        if not host:
            return
        with self._lock:
            now = time.monotonic()
            last = self._last_request_by_host.get(host)
            if last is not None:
                sleep_for = interval - (now - last)
                if sleep_for > 0:
                    time.sleep(sleep_for)
            self._last_request_by_host[host] = time.monotonic()


_RATE_LIMITER = HostRateLimiter()


class HostCircuitBreaker:
    def __init__(self, max_failures: int, cooldown_sec: float) -> None:
        self.max_failures = max(1, max_failures)
        self.cooldown_sec = max(1.0, cooldown_sec)
        self._failures_by_host: dict[str, int] = {}
        self._open_until_by_host: dict[str, float] = {}
        self._lock = threading.Lock()

    def _host(self, url: str) -> str:
        return urllib.parse.urlparse(url).netloc.lower()

    def is_open(self, url: str) -> bool:
        host = self._host(url)
        if not host:
            return False
        now = time.monotonic()
        with self._lock:
            open_until = self._open_until_by_host.get(host, 0.0)
            if open_until > now:
                return True
            if open_until:
                self._open_until_by_host.pop(host, None)
            return False

    def record_success(self, url: str) -> None:
        host = self._host(url)
        if not host:
            return
        with self._lock:
            self._failures_by_host[host] = 0
            self._open_until_by_host.pop(host, None)

    def record_failure(self, url: str) -> bool:
        host = self._host(url)
        if not host:
            return False
        with self._lock:
            failures = self._failures_by_host.get(host, 0) + 1
            self._failures_by_host[host] = failures
            if failures >= self.max_failures:
                self._failures_by_host[host] = 0
                self._open_until_by_host[host] = time.monotonic() + self.cooldown_sec
                return True
            return False


_CIRCUIT_BREAKER = HostCircuitBreaker(
    max_failures=DEFAULT_CIRCUIT_FAILURES,
    cooldown_sec=DEFAULT_CIRCUIT_COOLDOWN_SEC,
)


def _parse_retry_after_seconds(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    try:
        seconds = float(stripped)
        if seconds >= 0:
            return seconds
    except ValueError:
        pass
    try:
        retry_dt = email.utils.parsedate_to_datetime(stripped)
        now = time.time()
        seconds = retry_dt.timestamp() - now
        if seconds > 0:
            return seconds
    except Exception:
        return None
    return None


def _sleep_backoff(attempt: int, retry_after_seconds: Optional[float]) -> None:
    if retry_after_seconds is not None:
        time.sleep(min(max(retry_after_seconds, 0.0), 90.0))
        return
    backoff = min(2 ** (attempt - 1), 8) + random.uniform(0, 0.25)
    time.sleep(backoff)


def fetch_text(
    url: str,
    *,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
    retries: int = DEFAULT_RETRIES,
    headers: Optional[dict[str, str]] = None,
    min_interval_sec: Optional[float] = None,
    logger=None,
) -> Optional[str]:
    headers = headers or {}
    retries = max(1, retries)
    last_error = None

    if _CIRCUIT_BREAKER.is_open(url):
        _inc_metric("circuit_open_count")
        if logger:
            logger.info(
                '{"event":"fetch_circuit_open","url":"%s"}'
                % url
            )
        return None

    for attempt in range(1, retries + 1):
        _RATE_LIMITER.wait(url, min_interval_sec=min_interval_sec)
        _inc_metric("request_count")
        try:
            if _requests:
                resp = _requests.get(url, headers=headers, timeout=timeout_sec)
                if resp.status_code == 429:
                    _inc_metric("rate_limited_count")
                    retry_after_seconds = _parse_retry_after_seconds(resp.headers.get("Retry-After"))
                    raise RuntimeError(f"HTTP 429|retry_after={retry_after_seconds}")
                if resp.status_code >= 400:
                    raise RuntimeError(f"HTTP {resp.status_code}")
                _CIRCUIT_BREAKER.record_success(url)
                _inc_metric("success_count")
                return resp.text

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                status = getattr(resp, "status", resp.getcode())
                if status == 429:
                    _inc_metric("rate_limited_count")
                    retry_after_seconds = _parse_retry_after_seconds(resp.headers.get("Retry-After"))
                    raise RuntimeError(f"HTTP 429|retry_after={retry_after_seconds}")
                if status >= 400:
                    raise RuntimeError(f"HTTP {status}")
                _CIRCUIT_BREAKER.record_success(url)
                _inc_metric("success_count")
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            retry_after_seconds = _parse_retry_after_seconds(exc.headers.get("Retry-After"))
            if exc.code == 429:
                _inc_metric("rate_limited_count")
                last_error = RuntimeError(f"HTTP 429|retry_after={retry_after_seconds}")
            else:
                last_error = exc
            opened = _CIRCUIT_BREAKER.record_failure(url)
            if opened:
                _inc_metric("circuit_open_count")
            if logger:
                logger.info(
                    '{"event":"fetch_retry","url":"%s","attempt":%s,"error":"%s"}'
                    % (url, attempt, str(last_error).replace('"', "'"))
                )
            if attempt < retries:
                _inc_metric("retry_count")
                _sleep_backoff(attempt, retry_after_seconds)
            continue
        except Exception as exc:
            last_error = exc
            opened = _CIRCUIT_BREAKER.record_failure(url)
            if opened:
                _inc_metric("circuit_open_count")
            if logger:
                logger.info(
                    '{"event":"fetch_retry","url":"%s","attempt":%s,"error":"%s"}'
                    % (url, attempt, str(exc).replace('"', "'"))
                )
            if attempt < retries:
                _inc_metric("retry_count")
                retry_after_seconds = None
                if "retry_after=" in str(exc):
                    try:
                        retry_after_seconds = float(str(exc).split("retry_after=", 1)[1])
                    except Exception:
                        retry_after_seconds = None
                _sleep_backoff(attempt, retry_after_seconds)

    if logger and last_error:
        logger.info(
            '{"event":"fetch_failed","url":"%s","error":"%s"}'
            % (url, str(last_error).replace('"', "'"))
        )
    _inc_metric("failure_count")
    return None
