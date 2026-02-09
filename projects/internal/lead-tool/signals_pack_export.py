#!/usr/bin/env python3
"""
MA Operator Signals Pack Export

Generates the "MA Operator Signals Pack" - a curated list of the Top N
Massachusetts cannabis operators ranked by composite opportunity pressure.
"""

import argparse
import csv
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
from typing import Optional, List, Dict, Any

from ccc_client import build_default_client


# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.environ.get("LEAD_TOOL_OUTPUT_DIR", str(BASE_DIR / "output")))
DATA_DIR = Path(
    os.environ.get("LEAD_TOOL_DATA_DIR", str(BASE_DIR / "data" / "mass-ccc"))
)

CLEAN_CONTACTS_PATH = DATA_DIR / "clean-contacts.csv"
GOOGLE_PLACES_DIR = OUTPUT_DIR
DEFAULT_OUTPUT_DIR = OUTPUT_DIR
DEFAULT_OPERATOR_DB_PATH = Path(
    os.environ.get("LEAD_TOOL_OPERATOR_DB_PATH", str(OUTPUT_DIR / "lead_intel.db"))
)

CCC_CLIENT = build_default_client(BASE_DIR)


SIGNAL_WEIGHTS = {
    "stalled_ops": 25,
    "no_commenced_ops": 20,
    "pressure_signals_count": 10,
    "capacity_mismatch": 15,
    "recent_license": 5,
    "multiple_licenses": 5,
}

MARKET_CONTEXT = {
    "price_collapse_pct": 50,
    "avg_price_per_oz_flower_2021": 300,
    "avg_price_per_oz_flower_2024": 150,
    "total_licensed_entities": 1693,
    "active_cultivators": 450,
    "active_manufacturers": 380,
    "license_to_ops_avg_months": 18,
}


# =============================================================================
# HELPERS
# =============================================================================

def normalize_name(name: str) -> str:
    if not name:
        return ""
    value = name.lower()
    value = re.sub(
        r"\b(llc|inc|corp|corporation|company|co|dispensary|cannabis|marijuana)\b",
        "",
        value,
    )
    value = re.sub(r"[^\w\s]", "", value)
    return " ".join(value.split())


def fuzzy_match(name1: str, name2: str) -> float:
    return SequenceMatcher(None, normalize_name(name1), normalize_name(name2)).ratio()


def parse_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None

    cleaned = date_str.strip()
    if not cleaned:
        return None

    if "GMT" in cleaned:
        try:
            parts = cleaned.split()
            month_map = {
                "Jan": 1,
                "Feb": 2,
                "Mar": 3,
                "Apr": 4,
                "May": 5,
                "Jun": 6,
                "Jul": 7,
                "Aug": 8,
                "Sep": 9,
                "Oct": 10,
                "Nov": 11,
                "Dec": 12,
            }
            if len(parts) >= 4:
                return datetime(int(parts[3]), month_map[parts[1]], int(parts[2]))
        except Exception:
            pass

    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def parse_float(value: Any) -> Optional[float]:
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


def get_first(record: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for key in keys:
        value = record.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def normalize_license_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "business_name": get_first(
            record,
            [
                "BUSINESS_NAME",
                "business_name",
                "establishment_name",
                "applicant_name",
                "applicant_business_name",
            ],
        ),
        "license_type": get_first(record, ["LICENSE_TYPE", "license_type"]),
        "license_number": get_first(record, ["LICENSE_NUMBER", "license_number", "license_no"]),
        "status": get_first(record, ["LIC_STATUS", "status", "application_status"]),
        "approved_date": get_first(
            record,
            [
                "APPLICATION_APPROVED_DATE",
                "application_approved_date",
                "approved_date",
                "approval_date",
            ],
        ),
        "commence_date": get_first(
            record,
            [
                "COMMENCE_OPERATIONS_DATE",
                "commence_operations_date",
                "commence_date",
                "operations_start_date",
            ],
        ),
        "cultivation_tier": get_first(record, ["CULTIVATION_TIER", "cultivation_tier"]),
        "city": get_first(
            record,
            ["CITY", "city", "ESTABLISHMENT_CITY", "establishment_city", "municipality", "town"],
        ),
        "email": get_first(record, ["BUSINESS_EMAIL", "business_email", "email"]),
        "phone": get_first(record, ["BUSINESS_PHONE", "business_phone", "phone"]),
        "address": get_first(record, ["FULL_ADDRESS", "full_address", "address"]),
        "lic_start_date": get_first(
            record, ["LIC_START_DATE", "lic_start_date", "LIC_ORIGINAL_START_DATE", "lic_original_start_date"]
        ),
    }


def index_licenses_by_business(api_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    indexed: Dict[str, List[Dict[str, Any]]] = {}
    for record in api_data:
        normalized = normalize_license_record(record)
        business_name = normalized["business_name"]
        if not business_name:
            continue
        key = normalize_name(business_name)
        indexed.setdefault(key, []).append(normalized)
    return indexed


def latest_file(directory: Path, pattern: str) -> Optional[Path]:
    candidates = sorted(
        directory.glob(pattern),
        key=lambda p: p.stat().st_mtime if p.exists() else 0,
        reverse=True,
    )
    return candidates[0] if candidates else None


def metric_from_row(
    row: Dict[str, Any], includes: List[str], excludes: Optional[List[str]] = None
) -> Optional[float]:
    excludes = excludes or []
    for key, value in row.items():
        key_l = key.lower()
        if not any(token in key_l for token in includes):
            continue
        if any(token in key_l for token in excludes):
            continue
        number = parse_float(value)
        if number is not None:
            return number
    return None


# =============================================================================
# DATA LOADING
# =============================================================================

def fetch_ccc_licenses() -> List[Dict[str, Any]]:
    print("Fetching MA CCC license data...")
    try:
        rows = CCC_CLIENT.fetch_all("licenses", page_size=1000, use_cache=True, cache_ttl_hours=6)
        print(f"   loaded {len(rows)} license records")
        return rows
    except Exception as exc:
        print(f"   failed to fetch licenses: {exc}")
        return []


def fetch_commenced_ops() -> List[Dict[str, Any]]:
    print("Fetching commenced operations data...")
    for endpoint in ("commence_ops", "commence_ops_legacy"):
        try:
            rows = CCC_CLIENT.fetch_all(endpoint, page_size=1000, use_cache=True, cache_ttl_hours=12)
            if rows:
                print(f"   loaded {len(rows)} commenced-ops records ({endpoint})")
                return rows
        except Exception:
            continue
    print("   commenced-ops dataset unavailable, using license commence dates only")
    return []


def fetch_pending_applications() -> List[Dict[str, Any]]:
    print("Fetching pending application data...")
    try:
        rows = CCC_CLIENT.fetch_all("au_pending", page_size=1000, use_cache=True, cache_ttl_hours=12)
        print(f"   loaded {len(rows)} pending application records")
        return rows
    except Exception:
        print("   pending dataset unavailable")
        return []


def fetch_optional_dataset(name_or_id: str, ttl_hours: int = 12) -> List[Dict[str, Any]]:
    try:
        return CCC_CLIENT.fetch_all(name_or_id, page_size=1000, use_cache=True, cache_ttl_hours=ttl_hours)
    except Exception:
        return []


def load_clean_contacts() -> Dict[str, Dict[str, Any]]:
    contacts: Dict[str, Dict[str, Any]] = {}
    if not CLEAN_CONTACTS_PATH.exists():
        print(f"   clean contacts not found at {CLEAN_CONTACTS_PATH}, continuing without it")
        return contacts

    print(f"Loading clean contacts from {CLEAN_CONTACTS_PATH}...")
    with open(CLEAN_CONTACTS_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            business_name = row.get("Business Name", "").strip()
            if not business_name:
                continue
            contacts[normalize_name(business_name)] = {
                "email": row.get("Email", "").strip(),
                "phone": row.get("Phone", "").strip(),
                "city": row.get("City", "").strip(),
                "license_types": row.get("License Types", "").strip(),
                "status": row.get("Status", "").strip(),
                "has_contact": row.get("Has Contact", "").strip() == "Yes",
            }
    print(f"   loaded {len(contacts)} contacts")
    return contacts


# =============================================================================
# GOOGLE PLACES VALIDATION
# =============================================================================

_google_data_cache: Optional[Dict[str, Dict[str, Any]]] = None


def load_google_places_data() -> Dict[str, Dict[str, Any]]:
    global _google_data_cache
    if _google_data_cache is not None:
        return _google_data_cache

    _google_data_cache = {}
    places_file = latest_file(GOOGLE_PLACES_DIR, "places_live_*.csv") or latest_file(
        GOOGLE_PLACES_DIR, "places_enriched_*.csv"
    )
    if not places_file:
        return _google_data_cache

    print(f"Loading Google Places data from {places_file.name}...")
    with open(places_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = normalize_name(row.get("Business Name", ""))
            if not name:
                continue
            _google_data_cache[name] = {
                "google_status": row.get("google_status", ""),
                "google_rating": row.get("google_rating", ""),
                "google_review_count": int(row.get("google_review_count", "0") or "0"),
                "review_velocity": row.get("review_velocity", ""),
            }

    hiring_file = latest_file(GOOGLE_PLACES_DIR, "hiring_signals_*.csv")
    if hiring_file:
        with open(hiring_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = normalize_name(row.get("Business Name", ""))
                if not name:
                    continue
                _google_data_cache.setdefault(name, {}).update(
                    {
                        "hiring_signal": row.get("hiring_signal", ""),
                        "active_jobs": int(row.get("active_jobs", "0") or "0"),
                        "job_titles": row.get("job_titles", ""),
                    }
                )

    return _google_data_cache


def is_actually_operating(business_name: str) -> bool:
    data = load_google_places_data().get(normalize_name(business_name), {})
    reviews = data.get("google_review_count", 0)
    status = data.get("google_status", "").lower()
    rating = data.get("google_rating", "")
    hiring = data.get("hiring_signal", "")
    active_jobs = data.get("active_jobs", 0)
    job_titles = data.get("job_titles", "").lower()

    if reviews >= 10:
        return True
    if status == "operational" and rating:
        try:
            if float(rating) > 0:
                return True
        except ValueError:
            pass
    if hiring == "hiring_warm" and active_jobs > 0:
        ops_roles = ["associate", "budtender", "manager", "cashier", "driver", "trimmer", "grower", "packager"]
        if any(role in job_titles for role in ops_roles):
            return True
    return False


# =============================================================================
# SCORING CONTEXT
# =============================================================================

def index_pending_by_business(pending_rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for row in pending_rows:
        name = get_first(
            row,
            [
                "BUSINESS_NAME",
                "business_name",
                "applicant_name",
                "applicant_business_name",
                "establishment_name",
            ],
        )
        if not name:
            continue
        key = normalize_name(name)
        submitted = parse_date(
            get_first(
                row,
                [
                    "APPLICATION_DATE",
                    "application_date",
                    "SUBMITTED_DATE",
                    "submitted_date",
                    "RECEIVED_DATE",
                    "received_date",
                ],
            )
        )
        state = index.setdefault(key, {"pending_count": 0, "oldest_pending_date": None})
        state["pending_count"] += 1
        if submitted and (state["oldest_pending_date"] is None or submitted < state["oldest_pending_date"]):
            state["oldest_pending_date"] = submitted
    return index


def build_market_context(license_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    context = dict(MARKET_CONTEXT)
    context["city_sales"] = {}

    avg_price_rows = fetch_optional_dataset("avg_price", ttl_hours=24)
    if avg_price_rows:
        price_points: List[tuple[datetime, float]] = []
        for row in avg_price_rows:
            value = metric_from_row(row, ["price", "ounce", "oz"], excludes=["id"])
            date_text = get_first(row, ["date", "report_date", "week", "month", "period"])
            date_obj = parse_date(date_text) or datetime(1970, 1, 1)
            if value is not None:
                price_points.append((date_obj, value))
        if len(price_points) >= 2:
            price_points.sort(key=lambda pair: pair[0])
            start_price = price_points[0][1]
            latest_price = price_points[-1][1]
            if start_price > 0:
                collapse_pct = ((start_price - latest_price) / start_price) * 100
                context["price_collapse_pct"] = round(max(collapse_pct, 0), 1)
                context["avg_price_per_oz_flower_2021"] = round(start_price, 2)
                context["avg_price_per_oz_flower_2024"] = round(latest_price, 2)

    city_sales: Dict[str, float] = {}
    for dataset in ("itd_sales", "weekly_sales"):
        rows = fetch_optional_dataset(dataset, ttl_hours=12)
        for row in rows:
            city = get_first(row, ["CITY", "city", "municipality", "town"])
            total_sales = metric_from_row(row, ["sales", "revenue", "gross"], excludes=["id", "count", "license"])
            if not city or total_sales is None:
                continue
            city_key = city.strip().lower()
            city_sales[city_key] = city_sales.get(city_key, 0.0) + total_sales
    context["city_sales"] = city_sales

    normalized = [normalize_license_record(record) for record in license_data]
    context["total_licensed_entities"] = len(
        [row for row in normalized if row.get("license_number")]
    )
    context["active_cultivators"] = len(
        [row for row in normalized if "Cultivator" in row["license_type"] and row["status"] == "Active"]
    )
    context["active_manufacturers"] = len(
        [row for row in normalized if "Manufacturer" in row["license_type"] and row["status"] == "Active"]
    )
    return context


def build_capacity_context() -> Dict[str, Any]:
    plant_rows = fetch_optional_dataset("plant_activity", ttl_hours=12)
    sales_rows = fetch_optional_dataset("facility_sales", ttl_hours=12)

    plant_total = 0.0
    for row in plant_rows:
        value = metric_from_row(
            row,
            ["plant", "flower", "volume", "biomass", "inventory", "harvest"],
            excludes=["id", "count", "price"],
        )
        if value is not None:
            plant_total += value

    sales_total = 0.0
    for row in sales_rows:
        value = metric_from_row(
            row,
            ["sales", "sold", "revenue", "weight", "volume"],
            excludes=["id", "count", "price"],
        )
        if value is not None:
            sales_total += value

    ratio = 1.0
    if plant_total > 0 and sales_total > 0:
        ratio = plant_total / sales_total

    statewide_pressure = int(max(0, min((ratio - 1.0) * 35 + 10, 45)))
    return {
        "plant_total": plant_total,
        "sales_total": sales_total,
        "supply_demand_ratio": ratio,
        "statewide_pressure": statewide_pressure,
    }


def calculate_license_funnel_score(
    licenses: List[Dict[str, Any]],
    pending_meta: Dict[str, Any],
) -> int:
    score = 0
    now = datetime.now()

    pending_count = int(pending_meta.get("pending_count", 0) or 0)
    score += min(pending_count * 8, 24)

    approved_to_commenced_days: List[int] = []
    for license_row in licenses:
        approved_date = parse_date(license_row.get("approved_date", ""))
        commence_date = parse_date(license_row.get("commence_date", ""))
        status = license_row.get("status", "")

        if approved_date and not commence_date and status == "Active":
            months_waiting = (now - approved_date).days / 30
            if months_waiting >= 6:
                score += min(int(months_waiting // 6) * 4, 24)

        if approved_date and commence_date and commence_date > approved_date:
            approved_to_commenced_days.append((commence_date - approved_date).days)

    if approved_to_commenced_days:
        average_days = sum(approved_to_commenced_days) / len(approved_to_commenced_days)
        if average_days > 540:
            score += 20
        elif average_days > 365:
            score += 12
        elif average_days > 240:
            score += 6

    return min(score, 100)


def calculate_market_pressure_score(
    city: str,
    city_operator_count: int,
    market_context: Dict[str, Any],
) -> int:
    score = int(min((market_context.get("price_collapse_pct", 50) / 2), 35))
    score += min(city_operator_count * 2, 25)

    city_sales = market_context.get("city_sales", {})
    if city and city_sales:
        city_key = city.strip().lower()
        values = sorted(city_sales.values())
        if city_key in city_sales:
            city_value = city_sales[city_key]
            rank = sum(1 for value in values if value <= city_value)
            percentile = rank / max(len(values), 1)
            if percentile <= 0.25:
                score += 20
            elif percentile <= 0.50:
                score += 12
            else:
                score += 5
        else:
            score += 8
    else:
        score += 8

    return min(score, 100)


def calculate_capacity_pressure_score(
    licenses: List[Dict[str, Any]],
    capacity_signals: List[str],
    capacity_context: Dict[str, Any],
) -> int:
    score = int(capacity_context.get("statewide_pressure", 10))
    score += min(len(capacity_signals) * 12, 36)

    license_types = {row.get("license_type", "") for row in licenses}
    if any("Cultivator" in value for value in license_types):
        score += 8
    if any("Microbusiness" in value for value in license_types):
        score += 4
    if any(
        "Tier 01" in row.get("cultivation_tier", "") or "Tier 02" in row.get("cultivation_tier", "")
        for row in licenses
    ):
        score += 8

    return min(score, 100)


# =============================================================================
# SIGNAL DETECTION
# =============================================================================

def detect_pressure_signals(
    licenses: List[Dict[str, Any]],
    commenced_ops: List[Dict[str, Any]],
    business_name: str = "",
) -> List[str]:
    signals: List[str] = []
    now = datetime.now()

    commenced_license_numbers = {
        row.get("license_number", "")
        for row in commenced_ops
        if row.get("license_number", "") and (row.get("commence_date") or row.get("status") == "Active")
    }

    for license_row in licenses:
        approved_date = parse_date(license_row.get("approved_date", ""))
        has_commence_date = bool(parse_date(license_row.get("commence_date", "")))
        if not has_commence_date and license_row.get("license_number"):
            has_commence_date = license_row["license_number"] in commenced_license_numbers
        status = license_row.get("status", "")

        if approved_date and not has_commence_date and status == "Active":
            months_since_approval = (now - approved_date).days / 30
            if months_since_approval >= 12:
                if business_name and is_actually_operating(business_name):
                    if "market_pressure" not in signals:
                        signals.append("market_pressure")
                else:
                    signals.append(f"stalled_ops_{int(months_since_approval)}mo")
            elif months_since_approval >= 6:
                signals.append(f"slow_ramp_{int(months_since_approval)}mo")

    for license_row in licenses:
        approved_date = parse_date(license_row.get("approved_date", ""))
        if approved_date:
            months_since = (now - approved_date).days / 30
            if months_since <= 6:
                signals.append("recent_approval")
                break

    expired_count = sum(
        1 for license_row in licenses if license_row.get("status", "").lower() in ["expired", "surrendered"]
    )
    if expired_count > 0:
        signals.append(f"expired_licenses_{expired_count}")

    return signals


def detect_capacity_signals(licenses: List[Dict[str, Any]]) -> List[str]:
    signals: List[str] = []
    license_types = set()
    for license_row in licenses:
        license_type = license_row.get("license_type", "")
        if "Cultivator" in license_type:
            license_types.add("cultivator")
        elif "Manufacturer" in license_type or "Product" in license_type:
            license_types.add("manufacturer")
        elif "Retailer" in license_type:
            license_types.add("retailer")
        elif "Microbusiness" in license_type:
            license_types.add("microbusiness")

    if "cultivator" in license_types and "manufacturer" not in license_types:
        signals.append("cultivator_no_mfg")
    if "manufacturer" in license_types and "cultivator" not in license_types:
        signals.append("mfg_no_cultivation")

    for license_row in licenses:
        tier = license_row.get("cultivation_tier", "")
        if "Tier 01" in tier or "Tier 02" in tier:
            signals.append("small_tier_cultivator")
            break

    return signals


def generate_why_now(
    pressure_signals: List[str],
    capacity_signals: List[str],
) -> str:
    narratives: List[str] = []

    stalled = [value for value in pressure_signals if value.startswith("stalled_ops")]
    if stalled:
        months = stalled[0].split("_")[-1].replace("mo", "")
        narratives.append(f"Licensed {months} months ago but not yet operational, indicating prolonged capital burn.")
    if "market_pressure" in pressure_signals:
        narratives.append("Operating in a highly competitive market with severe wholesale price compression.")
    if "recent_approval" in pressure_signals:
        narratives.append("Recently approved and likely carrying startup and compliance cost pressure.")
    if any(value.startswith("expired_licenses") for value in pressure_signals):
        narratives.append("Has expired or surrendered licenses, a common distress signal.")
    if "cultivator_no_mfg" in capacity_signals:
        narratives.append("Grows product but lacks in-house manufacturing, limiting margin capture.")
    if "mfg_no_cultivation" in capacity_signals:
        narratives.append("Manufactures without cultivation and depends on external feedstock pricing.")
    if "small_tier_cultivator" in capacity_signals:
        narratives.append("Small-tier cultivation footprint is vulnerable in a scale-heavy market.")

    if not narratives:
        narratives.append("Operating in a structurally difficult market with persistent margin pressure.")
    return " ".join(narratives[:3])


def generate_talk_track(capacity_signals: List[str], pressure_signals: List[str]) -> str:
    if "cultivator_no_mfg" in capacity_signals:
        return "TOLL PROCESSING: Capture more margin by converting raw output into finished products."
    if "mfg_no_cultivation" in capacity_signals:
        return "BULK SUPPLY: Stabilize production with predictable feedstock contracts."
    if "small_tier_cultivator" in capacity_signals:
        return "EFFICIENCY: Focus on yield, strain mix, and per-unit cost discipline."
    if any(value.startswith("stalled_ops") for value in pressure_signals):
        return "ACTIVATION: Prioritize the fastest path from licensing to revenue."
    if "market_pressure" in pressure_signals:
        return "MARGIN DEFENSE: Run a rapid leak audit and fix top loss points first."
    if "recent_approval" in pressure_signals:
        return "LAUNCH SUPPORT: Build a first-year operating model that protects cash."
    return "MARGIN DEFENSE: Improve gross margin through cost and mix optimization."


def calculate_distress_score(
    pressure_signals: List[str],
    capacity_signals: List[str],
    licenses: List[Dict[str, Any]],
) -> int:
    score = 0
    stalled = [value for value in pressure_signals if value.startswith("stalled_ops")]
    for value in stalled:
        try:
            months = int(value.split("_")[-1].replace("mo", ""))
            score += min(months * 2, 50)
        except Exception:
            score += SIGNAL_WEIGHTS["stalled_ops"]

    if "market_pressure" in pressure_signals:
        score += 15
    if any(value.startswith("slow_ramp") for value in pressure_signals):
        score += 15
    if "recent_approval" in pressure_signals:
        score += SIGNAL_WEIGHTS["recent_license"]

    for value in pressure_signals:
        if value.startswith("expired_licenses"):
            try:
                count = int(value.split("_")[-1])
                score += count * 10
            except Exception:
                score += 10

    for _ in capacity_signals:
        score += SIGNAL_WEIGHTS["capacity_mismatch"]

    if len(licenses) >= 3:
        score += SIGNAL_WEIGHTS["multiple_licenses"]
    return score


# =============================================================================
# OPERATOR PROCESSING
# =============================================================================

def process_operators(
    license_data: List[Dict[str, Any]],
    commenced_data: List[Dict[str, Any]],
    clean_contacts: Dict[str, Dict[str, Any]],
    pending_index: Dict[str, Dict[str, Any]],
    market_context: Dict[str, Any],
    capacity_context: Dict[str, Any],
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    print("Processing operators...")

    licenses_by_business = index_licenses_by_business(license_data)
    commenced_by_business = index_licenses_by_business(commenced_data)
    print(f"   indexed {len(licenses_by_business)} businesses from license data")

    target_types = {
        "Marijuana Cultivator",
        "Marijuana Product Manufacturer",
        "Marijuana Microbusiness",
    }

    city_operator_counts: Dict[str, int] = {}
    for _, licenses in licenses_by_business.items():
        if not any(any(target in row.get("license_type", "") for target in target_types) for row in licenses):
            continue
        city = next((row.get("city", "") for row in licenses if row.get("city")), "").strip().lower()
        if city:
            city_operator_counts[city] = city_operator_counts.get(city, 0) + 1

    operators: List[Dict[str, Any]] = []
    for business_key, licenses in licenses_by_business.items():
        has_target = any(
            any(target in row.get("license_type", "") for target in target_types)
            for row in licenses
        )
        if not has_target:
            continue

        commenced = commenced_by_business.get(business_key, [])
        pressure_signals = detect_pressure_signals(licenses, commenced, business_key)
        capacity_signals = detect_capacity_signals(licenses)
        if not pressure_signals and not capacity_signals:
            continue

        business_name = licenses[0].get("business_name", "")
        pending_meta = pending_index.get(business_key, {})
        distress_score = calculate_distress_score(pressure_signals, capacity_signals, licenses)

        contact = clean_contacts.get(business_key, {})
        best_email = contact.get("email", "")
        best_phone = contact.get("phone", "")

        if not best_email:
            best_email = next((row.get("email", "") for row in licenses if row.get("email")), "")
        if not best_phone:
            best_phone = next((row.get("phone", "") for row in licenses if row.get("phone")), "")

        city = contact.get("city", "")
        if not city:
            city = next((row.get("city", "") for row in licenses if row.get("city")), "")

        city_count = city_operator_counts.get(city.strip().lower(), 0)

        license_funnel_score = calculate_license_funnel_score(licenses, pending_meta)
        market_pressure_score = calculate_market_pressure_score(city, city_count, market_context)
        capacity_pressure_score = calculate_capacity_pressure_score(licenses, capacity_signals, capacity_context)
        composite_score = (
            distress_score
            + license_funnel_score
            + market_pressure_score
            + capacity_pressure_score
        )

        license_types = sorted({row.get("license_type", "") for row in licenses if row.get("license_type")})
        why_now = generate_why_now(pressure_signals, capacity_signals)
        talk_track = generate_talk_track(capacity_signals, pressure_signals)

        operators.append(
            {
                "rank": 0,
                "business_name": business_name.title() if business_name else business_key.title(),
                "normalized_business_name": business_key,
                "city": city,
                "city_operator_count": city_count,
                "email": best_email,
                "phone": best_phone,
                "license_types": "; ".join(license_types),
                "distress_score": distress_score,
                "license_funnel_score": license_funnel_score,
                "market_pressure_score": market_pressure_score,
                "capacity_pressure_score": capacity_pressure_score,
                "composite_score": composite_score,
                "pending_count": int(pending_meta.get("pending_count", 0) or 0),
                "pressure_signals": ", ".join(pressure_signals),
                "capacity_signals": ", ".join(capacity_signals),
                "signal_count": len(pressure_signals) + len(capacity_signals),
                "why_now": why_now,
                "talk_track": talk_track,
                "has_email": "Yes" if best_email else "No",
                "has_phone": "Yes" if best_phone else "No",
            }
        )

    operators.sort(key=lambda row: (row["composite_score"], row["distress_score"]), reverse=True)
    for index, operator in enumerate(operators, 1):
        operator["rank"] = index

    print(f"   found {len(operators)} operators with signals")
    if limit is None:
        print("   returning full operator universe")
        return operators
    print(f"   returning top {min(limit, len(operators))}")
    return operators[:limit]


# =============================================================================
# OUTPUT GENERATION
# =============================================================================

def export_signals_pack(
    operators: List[Dict[str, Any]],
    output_dir: Path,
    filename_prefix: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = output_dir / f"{filename_prefix}_{today}.csv"

    fieldnames = [
        "Rank",
        "Business Name",
        "City",
        "Email",
        "Phone",
        "License Types",
        "Distress Score",
        "License Funnel Score",
        "Market Pressure Score",
        "Capacity Pressure Score",
        "Composite Score",
        "Pending Count",
        "City Operator Count",
        "Signal Count",
        "Pressure Signals",
        "Capacity Signals",
        "Why Now",
        "Talk Track",
        "Has Email",
        "Has Phone",
        "Contacted",
        "Response",
        "Notes",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for operator in operators:
            writer.writerow(
                {
                    "Rank": operator["rank"],
                    "Business Name": operator["business_name"],
                    "City": operator["city"],
                    "Email": operator["email"],
                    "Phone": operator["phone"],
                    "License Types": operator["license_types"],
                    "Distress Score": operator["distress_score"],
                    "License Funnel Score": operator["license_funnel_score"],
                    "Market Pressure Score": operator["market_pressure_score"],
                    "Capacity Pressure Score": operator["capacity_pressure_score"],
                    "Composite Score": operator["composite_score"],
                    "Pending Count": operator["pending_count"],
                    "City Operator Count": operator["city_operator_count"],
                    "Signal Count": operator["signal_count"],
                    "Pressure Signals": operator["pressure_signals"],
                    "Capacity Signals": operator["capacity_signals"],
                    "Why Now": operator["why_now"],
                    "Talk Track": operator["talk_track"],
                    "Has Email": operator["has_email"],
                    "Has Phone": operator["has_phone"],
                    "Contacted": "",
                    "Response": "",
                    "Notes": "",
                }
            )

    print(f"   exported {filename_prefix} to {output_path}")
    return output_path


def persist_dim_operator(
    license_data: List[Dict[str, Any]],
    operators: List[Dict[str, Any]],
    pending_index: Dict[str, Dict[str, Any]],
    db_path: Path,
) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS dim_operator (
            license_number TEXT NOT NULL,
            normalized_business_name TEXT NOT NULL,
            business_name TEXT,
            city TEXT,
            license_type TEXT,
            status TEXT,
            approved_date TEXT,
            commence_date TEXT,
            cultivation_tier TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            pending_count INTEGER DEFAULT 0,
            distress_score INTEGER DEFAULT 0,
            license_funnel_score INTEGER DEFAULT 0,
            market_pressure_score INTEGER DEFAULT 0,
            capacity_pressure_score INTEGER DEFAULT 0,
            composite_score INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (license_number, normalized_business_name)
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_dim_operator_business
        ON dim_operator (normalized_business_name)
        """
    )

    operator_lookup = {
        row["normalized_business_name"]: row
        for row in operators
    }

    now_iso = datetime.now().isoformat()
    for raw_record in license_data:
        license_row = normalize_license_record(raw_record)
        license_number = license_row.get("license_number", "")
        business_name = license_row.get("business_name", "")
        normalized_business_name = normalize_name(business_name)
        if not license_number or not normalized_business_name:
            continue

        operator_row = operator_lookup.get(normalized_business_name, {})
        pending_count = pending_index.get(normalized_business_name, {}).get("pending_count", 0)

        connection.execute(
            """
            INSERT INTO dim_operator (
                license_number, normalized_business_name, business_name, city, license_type,
                status, approved_date, commence_date, cultivation_tier, email, phone, address,
                pending_count, distress_score, license_funnel_score, market_pressure_score,
                capacity_pressure_score, composite_score, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(license_number, normalized_business_name) DO UPDATE SET
                business_name = excluded.business_name,
                city = excluded.city,
                license_type = excluded.license_type,
                status = excluded.status,
                approved_date = excluded.approved_date,
                commence_date = excluded.commence_date,
                cultivation_tier = excluded.cultivation_tier,
                email = excluded.email,
                phone = excluded.phone,
                address = excluded.address,
                pending_count = excluded.pending_count,
                distress_score = excluded.distress_score,
                license_funnel_score = excluded.license_funnel_score,
                market_pressure_score = excluded.market_pressure_score,
                capacity_pressure_score = excluded.capacity_pressure_score,
                composite_score = excluded.composite_score,
                updated_at = excluded.updated_at
            """,
            (
                license_number,
                normalized_business_name,
                business_name,
                license_row.get("city", ""),
                license_row.get("license_type", ""),
                license_row.get("status", ""),
                license_row.get("approved_date", ""),
                license_row.get("commence_date", ""),
                license_row.get("cultivation_tier", ""),
                license_row.get("email", ""),
                license_row.get("phone", ""),
                license_row.get("address", ""),
                int(pending_count or 0),
                int(operator_row.get("distress_score", 0)),
                int(operator_row.get("license_funnel_score", 0)),
                int(operator_row.get("market_pressure_score", 0)),
                int(operator_row.get("capacity_pressure_score", 0)),
                int(operator_row.get("composite_score", 0)),
                now_iso,
            ),
        )

    connection.commit()
    connection.close()
    print(f"   upserted dim_operator rows into {db_path}")
    return db_path


def generate_readme(
    operators: List[Dict[str, Any]],
    output_dir: Path,
    market_context: Dict[str, Any],
    capacity_context: Dict[str, Any],
) -> Path:
    output_path = output_dir / "signals_pack_readme.txt"
    today = datetime.now().strftime("%Y-%m-%d")

    with_email = sum(1 for row in operators if row["has_email"] == "Yes")
    with_phone = sum(1 for row in operators if row["has_phone"] == "Yes")
    avg_composite = (
        sum(row["composite_score"] for row in operators) / len(operators) if operators else 0
    )
    avg_distress = (
        sum(row["distress_score"] for row in operators) / len(operators) if operators else 0
    )

    content = f"""MA OPERATOR SIGNALS PACK
Generated: {today}

MARKET CONTEXT
- Wholesale flower price collapse estimate: {market_context.get("price_collapse_pct", 50)}%
- Approx price baseline: ${market_context.get("avg_price_per_oz_flower_2021", 300)}/oz
- Approx latest price: ${market_context.get("avg_price_per_oz_flower_2024", 150)}/oz
- Total licensed entities: {market_context.get("total_licensed_entities", 0)}
- Active cultivators: {market_context.get("active_cultivators", 0)}
- Active manufacturers: {market_context.get("active_manufacturers", 0)}

CAPACITY CONTEXT
- Plant activity aggregate: {int(capacity_context.get("plant_total", 0))}
- Facility sales aggregate: {int(capacity_context.get("sales_total", 0))}
- Supply/Demand ratio proxy: {capacity_context.get("supply_demand_ratio", 1.0):.3f}
- Statewide capacity pressure contribution: {capacity_context.get("statewide_pressure", 0)}

PACK SUMMARY
- Operators: {len(operators)}
- With email: {with_email}
- With phone: {with_phone}
- Average composite score: {avg_composite:.1f}
- Average distress score: {avg_distress:.1f}

SCORING MODEL
- Distress Score: legacy pressure + capacity model
- License Funnel Score: pending volume + approval-to-commence lag
- Market Pressure Score: price collapse + city density + optional city sales percentile
- Capacity Pressure Score: statewide supply-demand proxy + operator capacity mismatch
- Composite Score: sum of all four

DATA SOURCES
- MA CCC licenses
- MA CCC commence operations dataset (or license commence fields)
- MA CCC pending applications dataset
- Optional MA CCC sales, pricing, plant activity datasets
- Google Places + hiring enrichment (if available)
"""

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"   generated readme at {output_path}")
    return output_path


def print_summary(operators: List[Dict[str, Any]]) -> None:
    print("\nMA Operator Signals Pack Summary")
    print("=" * 50)
    print(f"Total operators: {len(operators)}")
    with_email = sum(1 for row in operators if row["has_email"] == "Yes")
    with_phone = sum(1 for row in operators if row["has_phone"] == "Yes")
    print(f"With email: {with_email}")
    print(f"With phone: {with_phone}")

    print("\nTop 10 by composite score")
    print("-" * 50)
    for row in operators[:10]:
        name = row["business_name"][:35]
        city = row["city"][:12] if row["city"] else "Unknown"
        score = row["composite_score"]
        print(f"{row['rank']:2}. [{score:3}] {name:<35} {city}")


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate MA Operator Signals Pack with multi-factor scoring",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=150,
        help="Number of operators to include in ranked outreach slices (default: 150)",
    )
    parser.add_argument(
        "--contacts-file",
        "-c",
        type=Path,
        default=None,
        help="Path to clean contacts CSV for enrichment",
    )
    parser.add_argument(
        "--operator-db",
        type=Path,
        default=DEFAULT_OPERATOR_DB_PATH,
        help=f"SQLite path for dim_operator table (default: {DEFAULT_OPERATOR_DB_PATH})",
    )
    args = parser.parse_args()

    print("\nMA Operator Signals Pack Generator")
    print("=" * 45)

    license_data = fetch_ccc_licenses()
    if not license_data:
        print("\nFailed to fetch license data from CCC API.")
        return

    commenced_data = fetch_commenced_ops()
    pending_data = fetch_pending_applications()

    global CLEAN_CONTACTS_PATH
    if args.contacts_file:
        CLEAN_CONTACTS_PATH = args.contacts_file
    clean_contacts = load_clean_contacts()

    pending_index = index_pending_by_business(pending_data)
    market_context = build_market_context(license_data)
    capacity_context = build_capacity_context()

    operators_all = process_operators(
        license_data=license_data,
        commenced_data=commenced_data,
        clean_contacts=clean_contacts,
        pending_index=pending_index,
        market_context=market_context,
        capacity_context=capacity_context,
        limit=None,
    )
    if not operators_all:
        print("\nNo operators found with actionable signals.")
        return

    operators_top = operators_all[: max(1, args.limit)]

    print("\nGenerating outputs...")
    csv_full_path = export_signals_pack(operators_all, args.output_dir, "ma_operator_signals_full")
    csv_top_path = export_signals_pack(operators_top, args.output_dir, "ma_operator_signals_top150")
    csv_legacy_path = export_signals_pack(operators_top, args.output_dir, "ma_operator_signals_pack")
    readme_path = generate_readme(operators_all, args.output_dir, market_context, capacity_context)
    db_path = persist_dim_operator(license_data, operators_all, pending_index, args.operator_db)

    print_summary(operators_all)

    print(f"\nDone. Files saved to {args.output_dir}")
    print(f" - {csv_full_path.name}")
    print(f" - {csv_top_path.name}")
    print(f" - {csv_legacy_path.name}")
    print(f" - {readme_path.name}")
    print(f" - {db_path.name}")


if __name__ == "__main__":
    main()
