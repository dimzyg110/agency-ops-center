#!/usr/bin/env python3
"""Relevance scoring helpers for MA-first content selection."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable
from urllib.parse import urlparse


MA_KEYWORDS = {
    "massachusetts",
    "ma",
    "ccc",
    "boston",
    "worcester",
    "springfield",
    "cape cod",
}

OPERATOR_KEYWORDS = {
    "license",
    "licensing",
    "compliance",
    "pricing",
    "margin",
    "retail",
    "cultivation",
    "manufacturing",
    "tax",
    "banking",
    "supply",
    "testing",
    "operations",
    "inventory",
}

FEDERAL_OR_POLICY_KEYWORDS = {
    "federal",
    "dea",
    "reschedule",
    "congress",
    "irs",
    "banking",
    "280e",
    "interstate",
}

TRUSTED_DOMAINS = {
    "masscannabiscontrol.com",
    "masslive.com",
    "boston.com",
    "marijuanamoment.net",
    "mjbizdaily.com",
    "reuters.com",
    "apnews.com",
}

GEO_BASE = {
    "ma": 80,
    "nearby_states": 58,
    "national": 40,
    "global": 28,
}


def _clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _contains_any(text: str, words: Iterable[str]) -> int:
    hits = 0
    for word in words:
        if word in text:
            hits += 1
    return hits


def domain_from_url(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    return domain.replace("www.", "").strip()


def score_item(
    item: Dict[str, Any],
    *,
    geo_scope: str,
    quality_weight: float = 1.0,
    relevance_tags: Iterable[str] | None = None,
) -> Dict[str, Any]:
    title = str(item.get("headline") or item.get("title") or item.get("name") or "")
    body = str(item.get("excerpt") or item.get("summary") or item.get("description") or "")
    text = f"{title} {body}".lower()
    tags_blob = " ".join([str(tag).lower() for tag in (relevance_tags or [])])
    combined_text = f"{text} {tags_blob}"

    ma_impact = GEO_BASE.get(geo_scope, GEO_BASE["national"])
    ma_impact += _contains_any(combined_text, MA_KEYWORDS) * 8
    ma_impact += _contains_any(combined_text, FEDERAL_OR_POLICY_KEYWORDS) * 5
    if "massachusetts" in combined_text:
        ma_impact += 8

    operator_actionability = 25 + (_contains_any(combined_text, OPERATOR_KEYWORDS) * 9)
    if any(tag in tags_blob for tag in ("policy", "compliance", "market", "pricing")):
        operator_actionability += 8

    evidence = 35
    url = str(item.get("url") or "")
    if url.startswith("http"):
        evidence += 15
    if item.get("published") or item.get("date"):
        evidence += 10
    if item.get("source"):
        evidence += 8
    if domain_from_url(url) in TRUSTED_DOMAINS:
        evidence += 10
    evidence += int(max(0.0, quality_weight - 1.0) * 8)

    ma_impact_score = _clamp(ma_impact)
    operator_actionability_score = _clamp(operator_actionability)
    evidence_confidence_score = _clamp(evidence)
    composite_relevance_score = _clamp(
        (ma_impact_score * 0.45)
        + (operator_actionability_score * 0.35)
        + (evidence_confidence_score * 0.20)
    )

    item["ma_impact_score"] = ma_impact_score
    item["operator_actionability_score"] = operator_actionability_score
    item["evidence_confidence_score"] = evidence_confidence_score
    item["composite_relevance_score"] = composite_relevance_score
    item["geo_scope"] = geo_scope
    return item


def should_include_item(
    item: Dict[str, Any],
    *,
    ma_threshold: int = 55,
    composite_threshold: int = 62,
) -> bool:
    geo_scope = str(item.get("geo_scope") or "national")
    if geo_scope == "ma":
        return True
    return (
        int(item.get("ma_impact_score", 0)) >= ma_threshold
        and int(item.get("composite_relevance_score", 0)) >= composite_threshold
    )


def ensure_ma_impact_note(item: Dict[str, Any]) -> Dict[str, Any]:
    if str(item.get("geo_scope")) == "ma":
        return item
    title = str(item.get("headline") or item.get("title") or item.get("name") or "this update")
    cleaned = re.sub(r"\s+", " ", title).strip()
    item["why_ma_impact"] = (
        f"Why this matters for MA operators: {cleaned} may affect pricing, compliance, or competitive conditions in Massachusetts."
    )
    return item

