#!/usr/bin/env python3
"""
AC Unified Market Intelligence

Merges three data sources:
1. Lead Tool (leads.db) - Cultivators/Manufacturers with pressure signals
2. Apex CRM Export - Dispensary buyers with order history
3. MA CCC Dispensary Licenses - All licensed retailers

Creates segmented lists for:
- Superbowl Event (dispensaries, prioritized by relationship + geography)
- Wholesale/White-label (B2B operators needing toll/bulk)
- Branded Products (dispensaries for AC Certified)

Usage:
    python3 unified_intel.py /path/to/apex_buyer_activity.csv

Output:
    - unified_intel_YYYY-MM-DD.csv (master list)
    - superbowl_targets.csv
    - b2b_prospects.csv
    - ac_certified_candidates.csv
"""

import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher
import sys
import re

from ccc_client import build_default_client

# =============================================================================
# CONFIGURATION
# =============================================================================

# Paths (use environment variables or defaults)
import os
BASE_DIR = Path(__file__).resolve().parent
LEADS_DB_PATH = Path(os.environ.get("LEADS_DB_PATH", "./data/leads.db"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "./output"))
CCC_CLIENT = build_default_client(BASE_DIR)

# Geographic priority (Boston metro for Superbowl in Woburn)
BOSTON_METRO_CITIES = {
    'boston', 'cambridge', 'somerville', 'chelsea', 'everett', 'malden',
    'medford', 'woburn', 'burlington', 'lexington', 'arlington', 'belmont',
    'watertown', 'newton', 'brookline', 'quincy', 'braintree', 'weymouth',
    'dorchester', 'roxbury', 'jamaica plain', 'hyde park', 'mattapan',
    'charlestown', 'south boston', 'east boston', 'revere', 'lynn', 'salem',
    'peabody', 'danvers', 'beverly', 'marblehead', 'saugus', 'melrose',
    'stoneham', 'reading', 'wakefield', 'brockton', 'randolph', 'milton',
    'dedham', 'needham', 'wellesley', 'natick', 'framingham', 'waltham'
}

# Fuzzy match threshold (0-1, higher = stricter)
MATCH_THRESHOLD = 0.7

# =============================================================================
# DATA FETCHING
# =============================================================================

def fetch_ccc_licenses():
    """Fetch all MA CCC licenses."""
    print("Fetching MA CCC license data...")
    try:
        data = CCC_CLIENT.fetch_all("licenses", page_size=1000, use_cache=True, cache_ttl_hours=6)
        print(f"   loaded {len(data)} license records")
        return data
    except Exception as e:
        print(f"   failed to fetch CCC data: {e}")
        return []


def load_leads_db():
    """Load B2B leads from leads.db."""
    if not LEADS_DB_PATH.exists():
        print(f"   ⚠ leads.db not found at {LEADS_DB_PATH}")
        return []

    print(f"📂 Loading leads from {LEADS_DB_PATH}...")
    conn = sqlite3.connect(LEADS_DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.execute("""
        SELECT * FROM leads
        WHERE bucket IN ('A', 'B')
        ORDER BY bucket, signal_strength DESC
    """)

    leads = [dict(row) for row in cursor.fetchall()]
    conn.close()

    print(f"   ✓ Loaded {len(leads)} B2B leads (Bucket A/B)")
    return leads


def load_apex_export(apex_path):
    """Load Apex buyer activity export."""
    print(f"📂 Loading Apex export from {apex_path}...")

    buyers = {}

    with open(apex_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Handle both raw activity exports and pre-processed lists
            buyer_name = row.get('Buyer') or row.get('Dispensary') or row.get('buyer')
            if not buyer_name:
                continue

            buyer_name = buyer_name.strip()

            if buyer_name not in buyers:
                buyers[buyer_name] = {
                    'name': buyer_name,
                    'contact': row.get('Contact Name') or row.get('Contact') or '',
                    'email': row.get('Contact Email') or row.get('Email') or '',
                    'phone': row.get('Contact Number') or row.get('Phone') or '',
                    'city': extract_city(row.get('Location') or row.get('City') or ''),
                    'activity_count': 0,
                    'orders': 0,
                    'flags': row.get('Flags') or '',
                    'tier': row.get('Tier') or '',
                    'last_activity': None
                }

            buyers[buyer_name]['activity_count'] += 1

            # Try to get order count if available
            if row.get('Orders'):
                try:
                    buyers[buyer_name]['orders'] = int(row.get('Orders'))
                except:
                    pass

    print(f"   ✓ Loaded {len(buyers)} unique buyers from Apex")
    return list(buyers.values())


# =============================================================================
# DATA PROCESSING
# =============================================================================

def extract_city(location):
    """Extract city from address string."""
    if not location:
        return ''
    # Try to match "City, MA" or "City MA"
    match = re.search(r'([A-Za-z\s]+)(?:,\s*)?MA', location, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return location.strip()


def normalize_name(name):
    """Normalize business name for matching."""
    if not name:
        return ''
    # Remove common suffixes and clean up
    name = name.lower()
    name = re.sub(r'\b(llc|inc|corp|corporation|company|co|dispensary|cannabis|marijuana)\b', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    return name


def fuzzy_match(name1, name2):
    """Calculate similarity ratio between two names."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    return SequenceMatcher(None, n1, n2).ratio()


def is_boston_metro(city):
    """Check if city is in Boston metro area."""
    if not city:
        return False
    return city.lower().strip() in BOSTON_METRO_CITIES


def extract_dispensary_licenses(ccc_data):
    """Filter CCC data to just dispensary licenses."""
    dispensaries = []

    retailer_types = {
        "Marijuana Retailer",
        "Marijuana Retailer Delivery Only",
        "Social Consumption Establishment"
    }

    for record in ccc_data:
        license_type = record.get("LICENSE_TYPE", "")
        status = record.get("LIC_STATUS", "")

        if license_type in retailer_types and status in ("Active", ""):
            dispensaries.append({
                'license_number': record.get("LICENSE_NUMBER", ""),
                'license_type': license_type,
                'business_name': record.get("BUSINESS_NAME", ""),
                'city': record.get("CITY", ""),
                'address': record.get("FULL_ADDRESS", ""),
                'email': record.get("BUSINESS_EMAIL", ""),
                'phone': record.get("BUSINESS_PHONE", ""),
                'approved_date': record.get("APPLICATION_APPROVED_DATE", ""),
                'license_start': record.get("LIC_ORIGINAL_START_DATE", ""),
                'commence_date': record.get("COMMENCE_OPERATIONS_DATE", ""),
            })

    print(f"   ✓ Found {len(dispensaries)} active dispensary licenses")
    return dispensaries


def detect_new_dispensary(record):
    """Check if dispensary is newly licensed (last 6 months)."""
    license_start = record.get('license_start', '')
    if not license_start:
        return False

    try:
        start_date = datetime.strptime(license_start.strip(), "%m/%d/%Y")
        return (datetime.now() - start_date) < timedelta(days=180)
    except:
        return False


def merge_data(apex_buyers, b2b_leads, dispensary_licenses):
    """
    Merge all data sources into unified records.

    Returns list of unified records with:
    - source: apex, b2b_lead, ccc_dispensary
    - match_status: customer, prospect, cold
    - recommended_pitch: retail, b2b, toll, white_label
    """

    print("\n🔄 Merging data sources...")

    unified = []
    matched_apex = set()
    matched_b2b = set()

    # Step 1: Process Apex buyers (known customers)
    for buyer in apex_buyers:
        record = {
            'name': buyer['name'],
            'contact': buyer['contact'],
            'email': buyer['email'],
            'phone': buyer['phone'],
            'city': buyer['city'],
            'source': 'apex',
            'match_status': 'customer',
            'orders': buyer.get('orders', 0),
            'activity_count': buyer.get('activity_count', 0),
            'apex_tier': buyer.get('tier', ''),
            'apex_flags': buyer.get('flags', ''),
            'is_boston_metro': is_boston_metro(buyer['city']),
            # B2B fields (to be filled if matched)
            'bucket': '',
            'pressure_signals': '',
            'capacity_signals': '',
            'suspected_buyer_type': '',
            'why_now': '',
            # Dispensary fields
            'is_new_dispensary': False,
            'license_type': '',
            # Scoring
            'superbowl_score': 0,
            'b2b_score': 0,
            'retail_score': 0,
            'recommended_pitch': 'retail',  # Default for apex buyers
        }

        # Try to match with B2B leads (some customers may also be cultivators/manufacturers)
        for lead in b2b_leads:
            if fuzzy_match(buyer['name'], lead['business_name']) >= MATCH_THRESHOLD:
                record['bucket'] = lead['bucket']
                record['pressure_signals'] = lead['pressure_signals']
                record['capacity_signals'] = lead['capacity_signals']
                record['suspected_buyer_type'] = lead['suspected_buyer_type']
                record['why_now'] = lead['why_now']
                record['recommended_pitch'] = 'b2b_upsell'  # Customer with B2B potential
                matched_b2b.add(lead['lead_id'])
                break

        # Try to match with dispensary licenses
        for disp in dispensary_licenses:
            if fuzzy_match(buyer['name'], disp['business_name']) >= MATCH_THRESHOLD:
                record['license_type'] = disp['license_type']
                record['is_new_dispensary'] = detect_new_dispensary(disp)
                break

        matched_apex.add(buyer['name'])
        unified.append(record)

    # Step 2: Add unmatched B2B leads (cold prospects for toll/wholesale)
    for lead in b2b_leads:
        if lead['lead_id'] in matched_b2b:
            continue

        record = {
            'name': lead['business_name'],
            'contact': '',
            'email': lead['email'],
            'phone': lead['phone'],
            'city': lead['city'],
            'source': 'b2b_lead',
            'match_status': 'cold_b2b',
            'orders': 0,
            'activity_count': 0,
            'apex_tier': '',
            'apex_flags': '',
            'is_boston_metro': is_boston_metro(lead['city']),
            'bucket': lead['bucket'],
            'pressure_signals': lead['pressure_signals'],
            'capacity_signals': lead['capacity_signals'],
            'suspected_buyer_type': lead['suspected_buyer_type'],
            'why_now': lead['why_now'],
            'is_new_dispensary': False,
            'license_type': lead['license_type'],
            'superbowl_score': 0,
            'b2b_score': 0,
            'retail_score': 0,
            'recommended_pitch': determine_b2b_pitch(lead),
        }
        unified.append(record)

    # Step 3: Add unmatched dispensary licenses (cold retail prospects)
    for disp in dispensary_licenses:
        # Skip if already matched to Apex buyer
        already_matched = False
        for buyer in apex_buyers:
            if fuzzy_match(buyer['name'], disp['business_name']) >= MATCH_THRESHOLD:
                already_matched = True
                break

        if already_matched:
            continue

        record = {
            'name': disp['business_name'],
            'contact': '',
            'email': disp['email'],
            'phone': disp['phone'],
            'city': disp['city'],
            'source': 'ccc_dispensary',
            'match_status': 'cold_retail',
            'orders': 0,
            'activity_count': 0,
            'apex_tier': '',
            'apex_flags': '',
            'is_boston_metro': is_boston_metro(disp['city']),
            'bucket': '',
            'pressure_signals': '',
            'capacity_signals': '',
            'suspected_buyer_type': '',
            'why_now': 'New dispensary prospect' if detect_new_dispensary(disp) else '',
            'is_new_dispensary': detect_new_dispensary(disp),
            'license_type': disp['license_type'],
            'superbowl_score': 0,
            'b2b_score': 0,
            'retail_score': 0,
            'recommended_pitch': 'retail',
        }
        unified.append(record)

    print(f"   ✓ Created {len(unified)} unified records")
    print(f"      - {len(apex_buyers)} from Apex (customers)")
    print(f"      - {len(b2b_leads) - len(matched_b2b)} unmatched B2B leads")
    print(f"      - {len([r for r in unified if r['source'] == 'ccc_dispensary'])} cold dispensary prospects")

    return unified


def determine_b2b_pitch(lead):
    """Determine best pitch for B2B lead."""
    buyer_type = lead.get('suspected_buyer_type', '')

    if 'toll_rolling' in buyer_type:
        return 'toll_processing'
    elif 'bulk_material' in buyer_type:
        return 'wholesale'
    elif 'contract_production' in buyer_type:
        return 'white_label'
    else:
        return 'b2b_general'


def score_records(unified):
    """Add priority scores for each use case."""

    print("\n📊 Scoring records...")

    for record in unified:
        # Superbowl Score (prioritize customers + Boston metro)
        sb_score = 0
        if record['match_status'] == 'customer':
            sb_score += 50
            sb_score += min(record.get('orders', 0) * 10, 50)  # Up to 50 for orders
            sb_score += min(record.get('activity_count', 0) * 2, 20)  # Up to 20 for activity
        if record['is_boston_metro']:
            sb_score += 30
        if record['is_new_dispensary']:
            sb_score += 15
        if 'WANTS_ORDER' in record.get('apex_flags', ''):
            sb_score += 10
        if 'B2B_POTENTIAL' in record.get('apex_flags', ''):
            sb_score += 10
        record['superbowl_score'] = sb_score

        # B2B Score (prioritize pressure signals + buyer type)
        b2b_score = 0
        if record['bucket'] == 'A':
            b2b_score += 50
        elif record['bucket'] == 'B':
            b2b_score += 30
        if record['pressure_signals']:
            b2b_score += len(record['pressure_signals'].split(',')) * 10
        if record['capacity_signals']:
            b2b_score += len(record['capacity_signals'].split(',')) * 10
        if record['match_status'] == 'customer':
            b2b_score += 20  # Existing customer = warmer
        record['b2b_score'] = b2b_score

        # Retail Score (AC Certified candidates)
        retail_score = 0
        if record['match_status'] == 'customer':
            retail_score += 40
            retail_score += min(record.get('orders', 0) * 15, 60)
        if record['is_boston_metro']:
            retail_score += 20
        if 'POP-UP' in record.get('apex_flags', ''):
            retail_score += 15
        if 'VISITED' in record.get('apex_flags', ''):
            retail_score += 10
        if record['is_new_dispensary']:
            retail_score += 10
        record['retail_score'] = retail_score

        # Distress Score (for Intel product - operators under pressure)
        distress_score = 0
        
        # Stalled operations (major indicator)
        pressure = record.get('pressure_signals', '')
        if 'stalled' in pressure.lower():
            # Extract months if possible
            import re
            stalled_matches = re.findall(r'stalled[_\s]*ops?[_\s]*(\d+)', pressure.lower())
            if stalled_matches:
                months = max(int(m) for m in stalled_matches)
                distress_score += min(months * 2, 60)  # Up to 60 for stalled ops
            else:
                distress_score += 30
        
        # Pressure signals count
        if pressure:
            signal_count = len([s for s in pressure.split(',') if s.strip()])
            distress_score += signal_count * 10
        
        # Capacity mismatch signals
        capacity = record.get('capacity_signals', '')
        if capacity:
            cap_count = len([s for s in capacity.split(',') if s.strip()])
            distress_score += cap_count * 15
        
        # Bucket A/B boost
        if record.get('bucket') == 'A':
            distress_score += 20
        elif record.get('bucket') == 'B':
            distress_score += 10
        
        # Expired license penalty (indicates past distress)
        if 'expired' in pressure.lower() or 'surrendered' in pressure.lower():
            distress_score += 25
        
        record['distress_score'] = distress_score

    return unified


# =============================================================================
# OUTPUT
# =============================================================================

def export_unified(unified, output_path):
    """Export master unified list."""

    fieldnames = [
        'name', 'contact', 'email', 'phone', 'city',
        'source', 'match_status', 'recommended_pitch',
        'superbowl_score', 'b2b_score', 'retail_score', 'distress_score',
        'orders', 'activity_count', 'apex_tier', 'apex_flags',
        'is_boston_metro', 'is_new_dispensary', 'license_type',
        'bucket', 'pressure_signals', 'capacity_signals',
        'suspected_buyer_type', 'why_now'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(unified)

    print(f"   ✓ Exported unified list to {output_path}")


def export_superbowl_list(unified, output_path):
    """Export Superbowl event target list."""

    # Filter: customers OR Boston metro dispensaries
    targets = [r for r in unified if r['superbowl_score'] >= 30]
    targets.sort(key=lambda x: -x['superbowl_score'])

    fieldnames = [
        'Priority', 'Score', 'Name', 'Contact', 'Email', 'Phone', 'City',
        'Boston Metro', 'Status', 'Orders', 'Flags', 'Pitch', 'Why Now',
        'Invited', 'RSVP', 'Budtenders', 'Notes'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, r in enumerate(targets, 1):
            # Assign priority tier
            if r['superbowl_score'] >= 80:
                priority = 'T1-VIP'
            elif r['superbowl_score'] >= 50:
                priority = 'T2-PRIORITY'
            elif r['superbowl_score'] >= 30:
                priority = 'T3-INVITE'
            else:
                priority = 'T4-MAYBE'

            writer.writerow({
                'Priority': priority,
                'Score': r['superbowl_score'],
                'Name': r['name'],
                'Contact': r['contact'],
                'Email': r['email'],
                'Phone': r['phone'],
                'City': r['city'],
                'Boston Metro': 'Yes' if r['is_boston_metro'] else 'No',
                'Status': r['match_status'],
                'Orders': r['orders'],
                'Flags': r['apex_flags'],
                'Pitch': r['recommended_pitch'],
                'Why Now': r['why_now'],
                'Invited': '',
                'RSVP': '',
                'Budtenders': '',
                'Notes': ''
            })

    print(f"   ✓ Exported {len(targets)} Superbowl targets to {output_path}")


def export_b2b_list(unified, output_path):
    """Export B2B prospect list (toll, wholesale, white-label)."""

    # Filter: B2B pitch recommended
    targets = [r for r in unified if r['b2b_score'] >= 20]
    targets.sort(key=lambda x: -x['b2b_score'])

    fieldnames = [
        'Bucket', 'Score', 'Name', 'Email', 'Phone', 'City',
        'Pitch', 'Pressure Signals', 'Capacity Signals', 'Why Now',
        'Customer Status', 'Contacted', 'Response', 'Notes'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in targets:
            writer.writerow({
                'Bucket': r['bucket'] or 'N/A',
                'Score': r['b2b_score'],
                'Name': r['name'],
                'Email': r['email'],
                'Phone': r['phone'],
                'City': r['city'],
                'Pitch': r['recommended_pitch'],
                'Pressure Signals': r['pressure_signals'],
                'Capacity Signals': r['capacity_signals'],
                'Why Now': r['why_now'],
                'Customer Status': 'Existing' if r['match_status'] == 'customer' else 'Cold',
                'Contacted': '',
                'Response': '',
                'Notes': ''
            })

    print(f"   ✓ Exported {len(targets)} B2B prospects to {output_path}")


def export_ac_certified_list(unified, output_path):
    """Export AC Certified candidate list."""

    # Filter: retail focused, ordered before
    targets = [r for r in unified if r['retail_score'] >= 30]
    targets.sort(key=lambda x: -x['retail_score'])

    fieldnames = [
        'Priority', 'Score', 'Name', 'Contact', 'Email', 'Phone', 'City',
        'Orders', 'Flags', 'New Store', 'B2B Upsell',
        'Pitched', 'Response', 'Pilot Status', 'Notes'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, r in enumerate(targets, 1):
            # Assign priority
            if r['retail_score'] >= 80:
                priority = 'T1-HOT'
            elif r['retail_score'] >= 50:
                priority = 'T2-WARM'
            else:
                priority = 'T3-PROSPECT'

            writer.writerow({
                'Priority': priority,
                'Score': r['retail_score'],
                'Name': r['name'],
                'Contact': r['contact'],
                'Email': r['email'],
                'Phone': r['phone'],
                'City': r['city'],
                'Orders': r['orders'],
                'Flags': r['apex_flags'],
                'New Store': 'Yes' if r['is_new_dispensary'] else 'No',
                'B2B Upsell': 'Yes' if r['recommended_pitch'] == 'b2b_upsell' else 'No',
                'Pitched': '',
                'Response': '',
                'Pilot Status': '',
                'Notes': ''
            })

    print(f"   ✓ Exported {len(targets)} AC Certified candidates to {output_path}")


def export_distressed_list(unified, output_path):
    """Export top 100 distressed operators list."""

    # Filter: has distress score > 0
    targets = [r for r in unified if r.get('distress_score', 0) > 0]
    targets.sort(key=lambda x: -x.get('distress_score', 0))
    
    # Limit to top 100
    targets = targets[:100]

    fieldnames = [
        'Rank', 'Distress Score', 'Name', 'Email', 'Phone', 'City',
        'Bucket', 'Pressure Signals', 'Capacity Signals', 'Why Now',
        'License Type', 'Source', 'Contacted', 'Response', 'Notes'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, r in enumerate(targets, 1):
            writer.writerow({
                'Rank': i,
                'Distress Score': r.get('distress_score', 0),
                'Name': r['name'],
                'Email': r['email'],
                'Phone': r['phone'],
                'City': r['city'],
                'Bucket': r.get('bucket', 'N/A'),
                'Pressure Signals': r.get('pressure_signals', ''),
                'Capacity Signals': r.get('capacity_signals', ''),
                'Why Now': r.get('why_now', ''),
                'License Type': r.get('license_type', ''),
                'Source': r.get('source', ''),
                'Contacted': '',
                'Response': '',
                'Notes': ''
            })

    print(f"   ✓ Exported {len(targets)} distressed operators to {output_path}")


def print_summary(unified):
    """Print summary statistics."""

    customers = [r for r in unified if r['match_status'] == 'customer']
    cold_b2b = [r for r in unified if r['match_status'] == 'cold_b2b']
    cold_retail = [r for r in unified if r['match_status'] == 'cold_retail']
    b2b_upsell = [r for r in unified if r['recommended_pitch'] == 'b2b_upsell']
    boston_metro = [r for r in unified if r['is_boston_metro']]
    new_stores = [r for r in unified if r['is_new_dispensary']]

    print(f"\n{'='*60}")
    print("📊 UNIFIED INTELLIGENCE SUMMARY")
    print(f"{'='*60}")

    print(f"\n📦 DATA SOURCES")
    print(f"   • Existing customers (Apex):     {len(customers)}")
    print(f"   • Cold B2B prospects (Scraper):  {len(cold_b2b)}")
    print(f"   • Cold retail prospects (CCC):   {len(cold_retail)}")
    print(f"   • TOTAL:                         {len(unified)}")

    print(f"\n🎯 KEY SEGMENTS")
    print(f"   • Boston metro area:             {len(boston_metro)}")
    print(f"   • New dispensaries (6mo):        {len(new_stores)}")
    print(f"   • Customers with B2B potential:  {len(b2b_upsell)}")

    # Top prospects per category
    print(f"\n{'─'*60}")
    print("🏈 TOP 10 SUPERBOWL TARGETS")
    print(f"{'─'*60}")
    sb_targets = sorted(unified, key=lambda x: -x['superbowl_score'])[:10]
    for i, r in enumerate(sb_targets, 1):
        status = "★ Customer" if r['match_status'] == 'customer' else "○ Prospect"
        boston = "📍" if r['is_boston_metro'] else "  "
        print(f"   {i:2}. {boston} {r['name'][:35]:<35} {status}")

    print(f"\n{'─'*60}")
    print("🏭 TOP 10 B2B PROSPECTS")
    print(f"{'─'*60}")
    b2b_targets = sorted(unified, key=lambda x: -x['b2b_score'])[:10]
    for i, r in enumerate(b2b_targets, 1):
        pitch = r['recommended_pitch'].replace('_', ' ').title()
        bucket = f"[{r['bucket']}]" if r['bucket'] else "[?]"
        print(f"   {i:2}. {bucket} {r['name'][:30]:<30} → {pitch}")

    print(f"\n{'─'*60}")
    print("🏪 TOP 10 AC CERTIFIED CANDIDATES")
    print(f"{'─'*60}")
    retail_targets = sorted(unified, key=lambda x: -x['retail_score'])[:10]
    for i, r in enumerate(retail_targets, 1):
        orders = f"{r['orders']} orders" if r['orders'] else "0 orders"
        new = "🆕" if r['is_new_dispensary'] else "  "
        print(f"   {i:2}. {new} {r['name'][:35]:<35} {orders}")

    print(f"\n{'─'*60}")
    print("⚠️  TOP 10 DISTRESSED OPERATORS")
    print(f"{'─'*60}")
    distressed_targets = sorted(unified, key=lambda x: -x.get('distress_score', 0))[:10]
    for i, r in enumerate(distressed_targets, 1):
        score = r.get('distress_score', 0)
        bucket = f"[{r['bucket']}]" if r.get('bucket') else "[?]"
        print(f"   {i:2}. [{score:3}] {bucket} {r['name'][:35]:<35}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n🌿 AC Unified Market Intelligence")
    print("=" * 55)

    # Check for Apex export path
    if len(sys.argv) < 2:
        print("\nUsage: python3 unified_intel.py /path/to/apex_export.csv")
        print("\nThis script merges:")
        print("  1. Apex CRM export (your customers)")
        print("  2. Lead tool database (B2B prospects)")
        print("  3. MA CCC dispensary licenses (cold retail)")
        print("\nOutputs segmented lists for Superbowl, B2B, and AC Certified.")
        sys.exit(1)

    apex_path = Path(sys.argv[1])
    if not apex_path.exists():
        print(f"\n❌ Apex export not found: {apex_path}")
        sys.exit(1)

    # Create output directory if needed
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')

    # Load data sources
    apex_buyers = load_apex_export(apex_path)
    b2b_leads = load_leads_db()
    ccc_licenses = fetch_ccc_licenses()
    dispensary_licenses = extract_dispensary_licenses(ccc_licenses)

    # Merge data
    unified = merge_data(apex_buyers, b2b_leads, dispensary_licenses)

    # Score records
    unified = score_records(unified)

    # Export outputs
    print("\n📄 Exporting lists...")
    export_unified(unified, OUTPUT_DIR / f"unified_intel_{today}.csv")
    export_superbowl_list(unified, OUTPUT_DIR / f"superbowl_targets_{today}.csv")
    export_b2b_list(unified, OUTPUT_DIR / f"b2b_prospects_{today}.csv")
    export_ac_certified_list(unified, OUTPUT_DIR / f"ac_certified_candidates_{today}.csv")
    export_distressed_list(unified, OUTPUT_DIR / f"distressed_top_100_{today}.csv")

    # Print summary
    print_summary(unified)

    print(f"\n✅ Done! Check {OUTPUT_DIR} for output files.")


if __name__ == '__main__':
    main()
