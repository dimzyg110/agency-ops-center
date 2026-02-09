#!/usr/bin/env python3
"""Load per-section source registry entries from config files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


TIER_RANK = {
    "primary": 0,
    "fallback": 1,
    "last_resort": 2,
}

VALID_GEO_SCOPE = {"ma", "nearby_states", "national", "global"}


def _registry_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "config" / "sources"


def _load_document(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {"sources": []}
    data = json.loads(text)
    if isinstance(data, list):
        return {"sources": data}
    if isinstance(data, dict):
        return data
    return {"sources": []}


def _normalize_source(raw: Dict[str, Any], section: str) -> Dict[str, Any]:
    source = dict(raw)
    source.setdefault("section", section)
    source.setdefault("source_id", source.get("name", "unknown").lower().replace(" ", "_"))
    source.setdefault("geo_scope", "national")
    source.setdefault("priority_tier", "fallback")
    source.setdefault("relevance_tags", [])
    source.setdefault("quality_weight", 1.0)
    source.setdefault("freshness_window_hours", 72)
    source.setdefault("timeout", 20)
    source.setdefault("retries", 3)
    source.setdefault("rps_limit", 1.0)
    source.setdefault("enabled", True)

    if source["geo_scope"] not in VALID_GEO_SCOPE:
        source["geo_scope"] = "national"
    if source["priority_tier"] not in TIER_RANK:
        source["priority_tier"] = "fallback"
    if not isinstance(source.get("relevance_tags"), list):
        source["relevance_tags"] = []
    return source


def load_section_sources(section: str) -> List[Dict[str, Any]]:
    path = _registry_dir() / f"{section}_sources.yaml"
    if not path.exists():
        return []
    doc = _load_document(path)
    raw_sources = doc.get("sources", [])
    normalized = [
        _normalize_source(entry, section)
        for entry in raw_sources
        if isinstance(entry, dict) and entry.get("enabled", True)
    ]
    normalized.sort(
        key=lambda src: (
            TIER_RANK.get(src.get("priority_tier", "fallback"), 99),
            -float(src.get("quality_weight", 1.0)),
        )
    )
    return normalized

