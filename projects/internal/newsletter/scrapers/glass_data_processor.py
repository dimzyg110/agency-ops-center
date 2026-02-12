#!/usr/bin/env python3
"""GLASS Data Processor — Pulls live market data from GLASS database.

Queries the GLASS PostgreSQL database for:
  - Price Wire: Average prices by category, biggest movers
  - Threat Radar: New competitors, active threats, enforcement
  - Strain Movers: Top strains by shelf presence, changes
  - Market Stats: Total operators, products, price observations

Outputs structured JSON matching the newsletter data contract.

Usage:
    python glass_data_processor.py --output ./data/glass_data.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Categories we care about for Price Wire
CORE_CATEGORIES = ["flower", "edible", "vape", "concentrate", "preroll"]


def _get_connection():
    """Create a psycopg2 connection to the GLASS database."""
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)

    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as exc:
        print(f"ERROR: Cannot connect to GLASS database: {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Price Wire
# ---------------------------------------------------------------------------

def fetch_price_wire(conn) -> Dict[str, Any]:
    """Fetch category price averages and biggest movers from GLASS."""
    cur = conn.cursor()
    result: Dict[str, Any] = {
        "category_averages": [],
        "biggest_drops": [],
        "biggest_increases": [],
        "total_observations": 0,
    }

    try:
        # Category averages for core categories (filter out accessories/junk)
        cur.execute("""
            SELECT p2.category,
                   ROUND(AVG(pr.price)::numeric, 2) AS avg_price,
                   ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pr.price)::numeric, 2) AS median_price,
                   COUNT(*) AS observation_count,
                   ROUND(MIN(pr.price)::numeric, 2) AS min_price,
                   ROUND(MAX(pr.price)::numeric, 2) AS max_price
            FROM prices pr
            JOIN products p2 ON pr.product_id = p2.id
            WHERE p2.category IN %s
              AND pr.price > 5
              AND pr.price < 500
              AND pr.scraped_at > NOW() - INTERVAL '7 days'
            GROUP BY p2.category
            ORDER BY observation_count DESC
        """, (tuple(CORE_CATEGORIES),))

        total_obs = 0
        for row in cur.fetchall():
            category, avg_price, median_price, count, min_price, max_price = row
            total_obs += count
            result["category_averages"].append({
                "category": category,
                "avg_price": float(avg_price),
                "median_price": float(median_price),
                "observation_count": count,
                "min_price": float(min_price),
                "max_price": float(max_price),
            })
        result["total_observations"] = total_obs

        # Biggest drops: cheapest real cannabis products (with THC content) vs category avg
        # Using thc_percent > 0 as the primary filter to exclude accessories
        cur.execute("""
            WITH category_avgs AS (
                SELECT p2.category, AVG(pr.price) AS avg_price
                FROM prices pr
                JOIN products p2 ON pr.product_id = p2.id
                WHERE p2.category IN %s
                  AND pr.price > 5 AND pr.price < 500
                  AND pr.scraped_at > NOW() - INTERVAL '7 days'
                GROUP BY p2.category
            )
            SELECT p2.name, p2.brand, p2.category, pr.price, o.name AS operator_name, o.city,
                   ca.avg_price,
                   ROUND(((pr.price - ca.avg_price) / ca.avg_price * 100)::numeric, 1) AS pct_below_avg
            FROM prices pr
            JOIN products p2 ON pr.product_id = p2.id
            JOIN operators o ON pr.operator_id = o.id
            JOIN category_avgs ca ON p2.category = ca.category
            WHERE p2.category IN %s
              AND pr.price > 10 AND pr.price < 200
              AND pr.scraped_at > NOW() - INTERVAL '7 days'
              AND (p2.thc_percent > 0 OR p2.name ILIKE '%%THC%%')
              AND LENGTH(p2.name) > 5
            ORDER BY pct_below_avg ASC
            LIMIT 8
        """, (tuple(CORE_CATEGORIES), tuple(CORE_CATEGORIES)))

        for row in cur.fetchall():
            name, brand, category, price, operator, city, avg_price, pct_diff = row
            clean_name = _clean_product_name(name)
            clean_brand = _clean_product_name(brand, max_len=30) if brand else "Unknown"
            result["biggest_drops"].append({
                "product": clean_name,
                "brand": clean_brand,
                "category": category,
                "price": float(price),
                "operator": _clean_operator_name(operator),
                "city": city or "MA",
                "category_avg": float(round(avg_price, 2)),
                "pct_vs_avg": float(pct_diff),
            })

        # Biggest increases (premium products relative to category average)
        # Using thc_percent > 0 as the primary filter to exclude accessories
        cur.execute("""
            WITH category_avgs AS (
                SELECT p2.category, AVG(pr.price) AS avg_price
                FROM prices pr
                JOIN products p2 ON pr.product_id = p2.id
                WHERE p2.category IN %s
                  AND pr.price > 5 AND pr.price < 500
                  AND pr.scraped_at > NOW() - INTERVAL '7 days'
                GROUP BY p2.category
            )
            SELECT p2.name, p2.brand, p2.category, pr.price, o.name AS operator_name, o.city,
                   ca.avg_price,
                   ROUND(((pr.price - ca.avg_price) / ca.avg_price * 100)::numeric, 1) AS pct_above_avg
            FROM prices pr
            JOIN products p2 ON pr.product_id = p2.id
            JOIN operators o ON pr.operator_id = o.id
            JOIN category_avgs ca ON p2.category = ca.category
            WHERE p2.category IN %s
              AND pr.price > 20 AND pr.price < 300
              AND pr.scraped_at > NOW() - INTERVAL '7 days'
              AND (p2.thc_percent > 0 OR p2.name ILIKE '%%THC%%')
              AND LENGTH(p2.name) > 5
            ORDER BY pct_above_avg DESC
            LIMIT 8
        """, (tuple(CORE_CATEGORIES), tuple(CORE_CATEGORIES)))

        for row in cur.fetchall():
            name, brand, category, price, operator, city, avg_price, pct_diff = row
            clean_name = _clean_product_name(name)
            clean_brand = _clean_product_name(brand, max_len=30) if brand else "Unknown"
            result["biggest_increases"].append({
                "product": clean_name,
                "brand": clean_brand,
                "category": category,
                "price": float(price),
                "operator": _clean_operator_name(operator),
                "city": city or "MA",
                "category_avg": float(round(avg_price, 2)),
                "pct_vs_avg": float(pct_diff),
            })

    except Exception as exc:
        print(f"WARNING: Price wire query failed: {exc}", file=sys.stderr)
    finally:
        cur.close()

    return result


# ---------------------------------------------------------------------------
# Threat Radar
# ---------------------------------------------------------------------------

def fetch_threat_radar(conn) -> Dict[str, Any]:
    """Fetch threat intelligence and new competitors from GLASS."""
    cur = conn.cursor()
    result: Dict[str, Any] = {
        "new_operators": [],
        "new_operator_count": 0,
        "active_threats": [],
        "active_threat_count": 0,
    }

    try:
        # New operators added in the last 7 days (with real names/cities),
        # excluding the initial bulk import day if it exists.
        cur.execute("""
            WITH daily_counts AS (
                SELECT DATE(created_at) AS created_date, COUNT(*) AS cnt
                FROM operators
                GROUP BY DATE(created_at)
            ),
            bulk_import_day AS (
                SELECT created_date
                FROM daily_counts
                ORDER BY cnt DESC, created_date ASC
                LIMIT 1
            )
            SELECT name, city, state, platform, created_at::date
            FROM operators
            WHERE created_at > NOW() - INTERVAL '7 days'
              AND DATE(created_at) != (SELECT created_date FROM bulk_import_day)
              AND name NOT LIKE 'New Operator%%'
              AND city IS NOT NULL
              AND city != 'Unknown'
              AND name NOT LIKE '%%test%%'
            ORDER BY created_at DESC
            LIMIT 20
        """)

        operators_seen = set()
        for row in cur.fetchall():
            name, city, state, platform, created_date = row
            # Deduplicate by name
            if name.lower() in operators_seen:
                continue
            operators_seen.add(name.lower())
            result["new_operators"].append({
                "name": _clean_operator_name(name),
                "city": city.title() if city else "Unknown",
                "state": state or "MA",
                "platform": platform,
                "detected_date": str(created_date),
            })
        result["new_operator_count"] = len(result["new_operators"])

        # Total new operators count in last 7 days, excluding bulk import day
        cur.execute("""
            WITH daily_counts AS (
                SELECT DATE(created_at) AS created_date, COUNT(*) AS cnt
                FROM operators
                GROUP BY DATE(created_at)
            ),
            bulk_import_day AS (
                SELECT created_date
                FROM daily_counts
                ORDER BY cnt DESC, created_date ASC
                LIMIT 1
            )
            SELECT COUNT(*)
            FROM operators
            WHERE created_at > NOW() - INTERVAL '7 days'
              AND DATE(created_at) != (SELECT created_date FROM bulk_import_day)
        """)
        result["new_operator_count_total"] = cur.fetchone()[0]

        # Active threats
        cur.execute("""
            SELECT type, severity, entity_name, description, source_url, created_at::date
            FROM threats
            WHERE resolved_at IS NULL
              AND created_at > NOW() - INTERVAL '14 days'
            ORDER BY 
                CASE severity 
                    WHEN 'critical' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                    WHEN 'low' THEN 4 
                    ELSE 5 
                END,
                created_at DESC
        """)

        for row in cur.fetchall():
            threat_type, severity, entity, description, source_url, created_date = row
            result["active_threats"].append({
                "type": threat_type,
                "severity": severity,
                "entity": entity or "Unknown",
                "description": (description or "")[:200],
                "source_url": source_url,
                "detected_date": str(created_date),
            })
        result["active_threat_count"] = len(result["active_threats"])

    except Exception as exc:
        print(f"WARNING: Threat radar query failed: {exc}", file=sys.stderr)
    finally:
        cur.close()

    return result


# ---------------------------------------------------------------------------
# Brand Movers
# ---------------------------------------------------------------------------

def fetch_strain_movers(conn) -> Dict[str, Any]:
    """Fetch top strains by shelf presence from GLASS."""
    cur = conn.cursor()
    result: Dict[str, Any] = {
        "top_strains": [],
        "total_strains_tracked": 0,
    }

    try:
        # Top strains by number of stores carrying them
        # Filter out junk "brands" that are actually product attributes
        cur.execute("""
            SELECT p2.brand,
                   COUNT(DISTINCT pr.operator_id) AS store_count,
                   COUNT(*) AS product_obs,
                   ROUND(AVG(pr.price)::numeric, 2) AS avg_price
            FROM prices pr
            JOIN products p2 ON pr.product_id = p2.id
            WHERE p2.brand IS NOT NULL
              AND p2.brand != ''
              AND LENGTH(p2.brand) > 3
              AND p2.brand NOT IN ('510', 'TAC', 'THC', 'Unknown', 'Gummies', 'Disposable', 
                                    'Hybrid', 'Indica', 'Sativa', 'None', 'N/A')
              AND p2.brand NOT LIKE '%%Order%%'
              AND p2.brand NOT LIKE '%%Preroll%%'
              AND p2.brand NOT LIKE '%%stock%%'
              AND p2.brand NOT LIKE '%%| %%'
              AND pr.scraped_at > NOW() - INTERVAL '7 days'
              AND pr.price > 5 AND pr.price < 500
            GROUP BY p2.brand
            HAVING COUNT(DISTINCT pr.operator_id) >= 3
            ORDER BY store_count DESC
            LIMIT 15
        """)

        for row in cur.fetchall():
            strain, store_count, product_obs, avg_price = row
            result["top_strains"].append({
                "strain": strain,
                "store_count": store_count,
                "product_observations": product_obs,
                "avg_price": float(avg_price),
            })

        # Total distinct brands
        cur.execute("""
            SELECT COUNT(DISTINCT brand)
            FROM products
            WHERE brand IS NOT NULL AND brand != '' AND LENGTH(brand) > 3
        """)
        result["total_strains_tracked"] = cur.fetchone()[0]

    except Exception as exc:
        print(f"WARNING: Strain movers query failed: {exc}", file=sys.stderr)
    finally:
        cur.close()

    return result


# ---------------------------------------------------------------------------
# Market Stats
# ---------------------------------------------------------------------------

def fetch_market_stats(conn) -> Dict[str, Any]:
    """Fetch overall market statistics from GLASS."""
    cur = conn.cursor()
    result: Dict[str, Any] = {}

    try:
        cur.execute("SELECT COUNT(*) FROM operators")
        result["total_operators"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM operators WHERE status = 'active'")
        result["active_operators"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM products")
        result["total_products"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM prices WHERE scraped_at > NOW() - INTERVAL '7 days'")
        result["price_observations_7d"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM prices")
        result["total_price_observations"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT operator_id) FROM prices WHERE scraped_at > NOW() - INTERVAL '7 days'")
        result["operators_with_prices_7d"] = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT p2.category)
            FROM prices pr
            JOIN products p2 ON pr.product_id = p2.id
            WHERE pr.scraped_at > NOW() - INTERVAL '7 days'
        """)
        result["categories_tracked"] = cur.fetchone()[0]

    except Exception as exc:
        print(f"WARNING: Market stats query failed: {exc}", file=sys.stderr)
    finally:
        cur.close()

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_operator_name(name: str) -> str:
    """Clean up operator names from scraped slugs to readable format."""
    if not name:
        return "Unknown"

    # If it looks like a slug (all lowercase, hyphens), title-case it
    if "-" in name and name == name.lower():
        # Convert slug to readable name
        name = name.replace("-", " ").title()

    return name.strip()


def _clean_product_name(name: str, max_len: int = 50) -> str:
    """Clean up product names from scraped data (often contain duplicated text)."""
    import re as _re
    if not name:
        return "Unknown Product"

    # Remove common duplicated patterns
    parts = name.split(" | ")
    if len(parts) > 1:
        # Take the most descriptive part
        name = max(parts, key=len).strip()

    # Remove duplicated product names (e.g., "Blue Dream Blue Dream Brand...")
    words = name.split()
    if len(words) > 4:
        # Check if first 2-3 words repeat
        for chunk_size in [3, 2]:
            if len(words) >= chunk_size * 2:
                chunk = " ".join(words[:chunk_size])
                rest = " ".join(words[chunk_size:])
                if rest.startswith(chunk):
                    name = chunk + " " + rest[len(chunk):].strip()

    # Remove TAC/THC data from display (it's too noisy)
    name = _re.sub(r'\s*TAC:\s*[\d.]+%', '', name)
    name = _re.sub(r'\s*THC:\s*[\d.]+%?(?:\s*-\s*[\d.]+%)?', '', name)
    name = _re.sub(r'\s*CBD:\s*[\d.]+%?', '', name)

    # Remove trailing metadata
    name = _re.sub(r'\s*Low\s*stock.*$', '', name, flags=_re.IGNORECASE)
    name = _re.sub(r'\s*Order\s*soon.*$', '', name, flags=_re.IGNORECASE)

    # Clean up multiple spaces
    name = _re.sub(r'\s+', ' ', name).strip()

    # Truncate if too long
    if len(name) > max_len:
        name = name[:max_len].rsplit(" ", 1)[0] + "..."

    return name.strip() or "Unknown Product"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def fetch_all_glass_data() -> Dict[str, Any]:
    """Fetch all GLASS data for the newsletter pipeline."""
    conn = _get_connection()
    if conn is None:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": "Cannot connect to GLASS database",
            "price_wire": {},
            "threat_radar": {},
            "brand_movers": {},
            "market_stats": {},
        }

    try:
        print("  Fetching Price Wire data...", file=sys.stderr)
        price_wire = fetch_price_wire(conn)

        print("  Fetching Threat Radar data...", file=sys.stderr)
        threat_radar = fetch_threat_radar(conn)

        print("  Fetching Strain Movers data...", file=sys.stderr)
        brand_movers = fetch_strain_movers(conn)

        print("  Fetching Market Stats...", file=sys.stderr)
        market_stats = fetch_market_stats(conn)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "price_wire": price_wire,
            "threat_radar": threat_radar,
            "brand_movers": brand_movers,
            "market_stats": market_stats,
        }
    except Exception as exc:
        print(f"ERROR: GLASS data fetch failed: {exc}", file=sys.stderr)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(exc),
            "price_wire": {},
            "threat_radar": {},
            "brand_movers": {},
            "market_stats": {},
        }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="GLASS Data Processor for Newsletter")
    parser.add_argument("--output", "-o", required=True, help="Output JSON path")
    args = parser.parse_args()

    print("📊 Fetching GLASS market intelligence...", file=sys.stderr)
    data = fetch_all_glass_data()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    status = data.get("status", "unknown")
    stats = data.get("market_stats", {})
    price_wire = data.get("price_wire", {})

    print(
        json.dumps({
            "event": "glass_data_complete",
            "status": status,
            "output": str(out_path),
            "operators": stats.get("total_operators", 0),
            "price_observations": price_wire.get("total_observations", 0),
            "categories": len(price_wire.get("category_averages", [])),
        }),
        file=sys.stderr,
    )

    return 0 if status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
