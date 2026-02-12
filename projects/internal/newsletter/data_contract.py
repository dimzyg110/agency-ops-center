#!/usr/bin/env python3
"""Canonical file contract for newsletter pipeline data exchange."""

from __future__ import annotations

from typing import Dict


# Canonical dataset filenames produced/consumed by the pipeline.
DATASET_FILES: Dict[str, str] = {
    "news": "news_weekly.json",
    "events": "events_upcoming.json",
    "reddit": "reddit_weekly.json",
    "tools": "tools_weekly.json",
    "market": "market_pulse.json",
    "glass": "glass_data.json",
}

# Optional metadata blocks that can be attached to stage outputs.
OPTIONAL_METADATA_KEYS = (
    "source_health",
    "coverage",
    "freshness",
    "relevance",
)

# Stage name -> output filename mapping.
STAGE_OUTPUT_FILES: Dict[str, str] = {
    "news": DATASET_FILES["news"],
    "events": DATASET_FILES["events"],
    "social": DATASET_FILES["reddit"],
    "tools": DATASET_FILES["tools"],
    "ccc_ingest": "ccc_ingest.json",
    "glass": DATASET_FILES["glass"],
    "market": DATASET_FILES["market"],
    "validate": "content_validation.json",
    "quality": "quality_report.json",
}


# GLASS data schema — expected keys and structure for newsletter sections.
GLASS_SCHEMA = {
    "price_wire": {
        "required_keys": ["category_averages", "biggest_drops", "biggest_increases", "total_observations"],
        "description": "Price data by category with biggest movers",
    },
    "threat_radar": {
        "required_keys": ["new_operators", "new_operator_count", "active_threats", "active_threat_count"],
        "description": "New competitor detection and active threat intelligence",
    },
    "brand_movers": {
        "required_keys": ["top_strains", "total_strains_tracked"],
        "description": "Top strains by shelf presence across MA dispensaries",
    },
    "market_stats": {
        "required_keys": ["total_operators", "total_products", "total_price_observations"],
        "description": "Overall market statistics from GLASS database",
    },
}


def stage_output_filename(stage_name: str) -> str:
    """Return canonical output filename for a stage."""
    return STAGE_OUTPUT_FILES.get(stage_name, f"{stage_name}.json")
