#!/usr/bin/env python3
"""
Margin Pressure Snapshot Generator

Generates 1-page snapshot-ready data for individual dispensaries/operators.
Each snapshot includes:
- Market context
- 3 pressure signals
- 3 likely margin leaks
- 3 fast wins
- "What I'd change first" recommendation

Usage:
    python3 snapshot_generator.py --name "Dispensary Name"
    python3 snapshot_generator.py --input targets.csv --output-dir ./snapshots

Output:
    - snapshots_ready.csv (batch mode)
    - snapshot_<business_name>.json (single mode)
"""

import argparse
import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
from typing import Optional, List, Dict, Any, Tuple

from ccc_client import build_default_client


# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.environ.get("LEAD_TOOL_OUTPUT_DIR", str(BASE_DIR / "output")))
CCC_CLIENT = build_default_client(BASE_DIR)

# Default output directory
DEFAULT_OUTPUT_DIR = Path(
    os.environ.get("LEAD_TOOL_SNAPSHOT_OUTPUT_DIR", str(OUTPUT_DIR / "snapshots"))
)

# Google Places enrichment directory
ENRICHMENT_DIR = OUTPUT_DIR

# Market context data (2024-2025)
MARKET_CONTEXT = {
    'headline': "Massachusetts Cannabis Market Under Margin Pressure",
    'price_decline': "Wholesale flower prices have dropped ~50% since 2021 ($300/oz → $150/oz)",
    'competition': "1,693 licensed entities competing in a mature market",
    'consolidation': "Small operators struggling; consolidation accelerating",
    'regulatory': "Increasing compliance costs and testing requirements",
    'consumer': "Consumer spending flat; price sensitivity increasing",
}

# Pressure signal definitions with descriptions
PRESSURE_SIGNALS = {
    'stalled_ops': {
        'name': 'Stalled Operations',
        'description': 'Licensed but not yet operational - capital burn without revenue',
        'severity': 'high',
    },
    'expired_licenses': {
        'name': 'Expired/Surrendered Licenses',
        'description': 'Has given up licenses - financial or operational distress indicator',
        'severity': 'high',
    },
    'cultivator_no_mfg': {
        'name': 'Cultivation Without Manufacturing',
        'description': 'Growing product but missing margin capture from value-add processing',
        'severity': 'medium',
    },
    'mfg_no_cultivation': {
        'name': 'Manufacturing Without Cultivation',
        'description': 'Dependent on external supply chain for raw material',
        'severity': 'medium',
    },
    'small_tier_cultivator': {
        'name': 'Small-Tier Cultivation',
        'description': 'Limited scale leading to higher per-unit costs',
        'severity': 'medium',
    },
    'recent_approval': {
        'name': 'Recently Licensed',
        'description': 'New operation facing startup costs in a challenging market',
        'severity': 'low',
    },
    'multiple_license_types': {
        'name': 'Complex License Portfolio',
        'description': 'Multiple license types adding operational complexity',
        'severity': 'low',
    },
}

# Common margin leaks for cannabis operators
MARGIN_LEAKS = {
    'labor_inefficiency': {
        'name': 'Labor Inefficiency',
        'description': 'Manual processes that could be automated',
        'quick_win': 'Implement task tracking and performance metrics',
    },
    'inventory_waste': {
        'name': 'Inventory Waste & Shrinkage',
        'description': 'Product loss from spoilage, damage, or compliance issues',
        'quick_win': 'Tighten inventory controls and FIFO rotation',
    },
    'pricing_leakage': {
        'name': 'Pricing Inconsistency',
        'description': 'Unoptimized pricing leaving money on the table',
        'quick_win': 'Implement dynamic pricing based on velocity',
    },
    'compliance_overhead': {
        'name': 'Compliance Overhead',
        'description': 'Excessive time spent on regulatory requirements',
        'quick_win': 'Streamline seed-to-sale workflows',
    },
    'energy_costs': {
        'name': 'High Energy Costs',
        'description': 'Unoptimized HVAC and lighting for cultivation',
        'quick_win': 'LED upgrade and climate control optimization',
    },
    'marketing_waste': {
        'name': 'Marketing Spend Without ROI',
        'description': 'Advertising without clear customer acquisition cost',
        'quick_win': 'Focus on retention over acquisition',
    },
    'vendor_terms': {
        'name': 'Poor Vendor Terms',
        'description': 'Not leveraging volume for better pricing',
        'quick_win': 'Renegotiate top 5 supplier contracts',
    },
    'staffing_mismatch': {
        'name': 'Staffing Mismatch',
        'description': 'Over or understaffed relative to traffic patterns',
        'quick_win': 'Align scheduling to hourly sales data',
    },
}

# Fast wins based on operator type
FAST_WINS = {
    'cultivator': [
        {'name': 'Yield Optimization', 'description': 'Focus on grams per square foot rather than plant count'},
        {'name': 'Strain Rationalization', 'description': 'Cut underperformers, double down on top 5 sellers'},
        {'name': 'Trim Monetization', 'description': 'Convert trim to concentrates or pre-rolls instead of selling bulk'},
    ],
    'manufacturer': [
        {'name': 'SKU Rationalization', 'description': 'Eliminate slow-moving products draining production time'},
        {'name': 'Batch Size Optimization', 'description': 'Right-size batches to minimize waste and storage'},
        {'name': 'White-Label Capacity', 'description': 'Fill excess capacity with white-label production'},
    ],
    'retailer': [
        {'name': 'Basket Size Optimization', 'description': 'Train staff on upselling and bundling techniques'},
        {'name': 'Loyalty Program', 'description': 'Implement or optimize retention program'},
        {'name': 'Google Business Profile', 'description': 'Optimize GBP for local search visibility'},
    ],
    'microbusiness': [
        {'name': 'Vertical Integration', 'description': 'Maximize margin capture across grow/process/sell'},
        {'name': 'Community Focus', 'description': 'Build local brand loyalty as competitive moat'},
        {'name': 'Operational Efficiency', 'description': 'Document and streamline cross-functional workflows'},
    ],
    'default': [
        {'name': 'Cost Audit', 'description': 'Review top 10 expense line items for reduction opportunities'},
        {'name': 'Process Documentation', 'description': 'Document key workflows to identify bottlenecks'},
        {'name': 'Customer Feedback Loop', 'description': 'Implement systematic customer feedback collection'},
    ],
}


# =============================================================================
# DATA FETCHING
# =============================================================================

def fetch_ccc_licenses() -> List[Dict[str, Any]]:
    """Fetch all MA CCC licenses from the public API."""
    print("Fetching MA CCC license data...")
    try:
        data = CCC_CLIENT.fetch_all("licenses", page_size=1000, use_cache=True, cache_ttl_hours=6)
        print(f"   loaded {len(data)} license records")
        return data
    except Exception as e:
        print(f"   failed to fetch CCC data: {e}")
        return []


def index_licenses_by_business(api_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Index license records by business name."""
    indexed = {}
    
    for record in api_data:
        business_name = record.get('BUSINESS_NAME', '').strip()
        if not business_name:
            continue
        
        key = business_name.lower()
        if key not in indexed:
            indexed[key] = []
        
        indexed[key].append({
            'license_type': record.get('LICENSE_TYPE', ''),
            'license_number': record.get('LICENSE_NUMBER', ''),
            'status': record.get('LIC_STATUS', ''),
            'approved_date': record.get('APPLICATION_APPROVED_DATE', ''),
            'commence_date': record.get('COMMENCE_OPERATIONS_DATE', ''),
            'cultivation_tier': record.get('CULTIVATION_TIER', ''),
            'city': record.get('CITY', '') or record.get('ESTABLISHMENT_CITY', ''),
            'email': record.get('BUSINESS_EMAIL', ''),
            'phone': record.get('BUSINESS_PHONE', ''),
            'address': record.get('FULL_ADDRESS', ''),
        })
    
    return indexed


# =============================================================================
# GOOGLE PLACES VALIDATION
# =============================================================================

_google_cache: Optional[Dict[str, Dict[str, Any]]] = None


def _load_google_data() -> Dict[str, Dict[str, Any]]:
    """Load Google Places + hiring enrichment data for cross-validation."""
    global _google_cache
    if _google_cache is not None:
        return _google_cache

    _google_cache = {}
    places_files = sorted(ENRICHMENT_DIR.glob("places_live_*.csv"), reverse=True)
    if places_files:
        with open(places_files[0], 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                name = row.get('Business Name', '').strip().lower()
                if name:
                    _google_cache[name] = {
                        'google_review_count': int(row.get('google_review_count', '0') or '0'),
                        'google_status': row.get('google_status', ''),
                        'google_rating': row.get('google_rating', ''),
                    }

    hiring_files = sorted(ENRICHMENT_DIR.glob("hiring_signals_*.csv"), reverse=True)
    if hiring_files:
        with open(hiring_files[0], 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                name = row.get('Business Name', '').strip().lower()
                if name:
                    _google_cache.setdefault(name, {}).update({
                        'hiring_signal': row.get('hiring_signal', ''),
                        'active_jobs': int(row.get('active_jobs', '0') or '0'),
                        'job_titles': row.get('job_titles', ''),
                    })

    return _google_cache


def is_actually_operating(business_name: str) -> bool:
    """Check if an operator is actually running despite CCC showing no commence date."""
    data = _load_google_data().get(business_name.lower(), {})
    reviews = data.get('google_review_count', 0)
    status = data.get('google_status', '').lower()
    rating = data.get('google_rating', '')
    hiring = data.get('hiring_signal', '')
    active_jobs = data.get('active_jobs', 0)
    job_titles = data.get('job_titles', '').lower()

    if reviews >= 10:
        return True
    if status == 'operational' and rating and float(rating) > 0:
        return True
    if hiring == 'hiring_warm' and active_jobs > 0:
        ops_roles = ['associate', 'budtender', 'manager', 'cashier', 'driver', 'trimmer', 'grower', 'packager']
        if any(role in job_titles for role in ops_roles):
            return True
    return False


# =============================================================================
# SIGNAL DETECTION
# =============================================================================

def normalize_name(name: str) -> str:
    """Normalize business name for matching."""
    if not name:
        return ''
    name = name.lower()
    name = re.sub(r'\b(llc|inc|corp|corporation|company|co|dispensary|cannabis|marijuana)\b', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    return name


def fuzzy_match_score(name1: str, name2: str) -> float:
    """Calculate similarity ratio between two names."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    return SequenceMatcher(None, n1, n2).ratio()


def find_business(
    search_name: str,
    licenses_by_business: Dict[str, List[Dict[str, Any]]],
    threshold: float = 0.7
) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """Find a business by name with fuzzy matching."""
    
    # Exact match first
    key = search_name.lower()
    if key in licenses_by_business:
        return search_name, licenses_by_business[key]
    
    # Fuzzy match
    best_match = None
    best_score = 0
    best_data = []
    
    for business_name, licenses in licenses_by_business.items():
        score = fuzzy_match_score(search_name, business_name)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = business_name
            best_data = licenses
    
    return best_match, best_data


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats from CCC data."""
    if not date_str:
        return None
    
    formats = ["%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"]
    date_str = date_str.strip()
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def detect_signals(licenses: List[Dict[str, Any]], business_name: str = "") -> List[Dict[str, Any]]:
    """Detect pressure signals for a business.

    Cross-validates CCC stall flags against Google Places and hiring data
    to avoid flagging operators who are clearly running.
    """
    signals = []
    now = datetime.now()

    # Check for stalled operations
    for lic in licenses:
        approved_date = parse_date(lic.get('approved_date', ''))
        commence_date = parse_date(lic.get('commence_date', ''))
        status = lic.get('status', '')

        if approved_date and not commence_date and status == 'Active':
            months_since = (now - approved_date).days / 30
            if months_since >= 12:
                # Validate against Google Places data before claiming they're stalled
                if business_name and is_actually_operating(business_name):
                    signals.append({
                        'type': 'market_pressure',
                        'name': 'Market Margin Pressure',
                        'description': 'Operating in a market where wholesale prices have dropped ~50% since 2021',
                        'severity': 'medium',
                    })
                else:
                    signals.append({
                        'type': 'stalled_ops',
                        'months': int(months_since),
                        **PRESSURE_SIGNALS['stalled_ops'],
                    })
                break
    
    # Check for expired licenses
    expired_count = sum(1 for lic in licenses if lic.get('status', '').lower() in ['expired', 'surrendered'])
    if expired_count > 0:
        signals.append({
            'type': 'expired_licenses',
            'count': expired_count,
            **PRESSURE_SIGNALS['expired_licenses'],
        })
    
    # Check license types
    license_types = set()
    for lic in licenses:
        lic_type = lic.get('license_type', '')
        if 'Cultivator' in lic_type:
            license_types.add('cultivator')
        elif 'Manufacturer' in lic_type or 'Product' in lic_type:
            license_types.add('manufacturer')
        elif 'Retailer' in lic_type:
            license_types.add('retailer')
        elif 'Microbusiness' in lic_type:
            license_types.add('microbusiness')
    
    # Capacity mismatches
    if 'cultivator' in license_types and 'manufacturer' not in license_types:
        signals.append({
            'type': 'cultivator_no_mfg',
            **PRESSURE_SIGNALS['cultivator_no_mfg'],
        })
    
    if 'manufacturer' in license_types and 'cultivator' not in license_types:
        signals.append({
            'type': 'mfg_no_cultivation',
            **PRESSURE_SIGNALS['mfg_no_cultivation'],
        })
    
    # Small tier
    for lic in licenses:
        tier = lic.get('cultivation_tier', '')
        if 'Tier 01' in tier or 'Tier 02' in tier:
            signals.append({
                'type': 'small_tier_cultivator',
                **PRESSURE_SIGNALS['small_tier_cultivator'],
            })
            break
    
    # Multiple license types
    if len(license_types) >= 3:
        signals.append({
            'type': 'multiple_license_types',
            **PRESSURE_SIGNALS['multiple_license_types'],
        })
    
    return signals[:5]  # Limit to 5 signals


def get_operator_type(licenses: List[Dict[str, Any]]) -> str:
    """Determine primary operator type from licenses."""
    types = set()
    for lic in licenses:
        lic_type = lic.get('license_type', '')
        if 'Cultivator' in lic_type:
            types.add('cultivator')
        elif 'Manufacturer' in lic_type or 'Product' in lic_type:
            types.add('manufacturer')
        elif 'Retailer' in lic_type:
            types.add('retailer')
        elif 'Microbusiness' in lic_type:
            types.add('microbusiness')
    
    if 'microbusiness' in types:
        return 'microbusiness'
    elif 'cultivator' in types:
        return 'cultivator'
    elif 'manufacturer' in types:
        return 'manufacturer'
    elif 'retailer' in types:
        return 'retailer'
    return 'default'


def get_likely_leaks(signals: List[Dict[str, Any]], operator_type: str) -> List[Dict[str, str]]:
    """Get likely margin leaks based on signals and operator type."""
    leaks = []
    
    # Signal-based leaks
    signal_types = [s['type'] for s in signals]
    
    if 'stalled_ops' in signal_types:
        leaks.append({
            'name': 'Burn Without Revenue',
            'description': 'Paying rent, utilities, and holding costs without generating income',
            'quick_win': 'Fast-track to operations or consider sublease options',
        })

    if 'market_pressure' in signal_types:
        leaks.append({
            'name': 'Margin Compression',
            'description': 'Wholesale prices down ~50% since 2021 — margins eroding across the board',
            'quick_win': 'Run a cost-per-unit analysis to identify your 3 biggest expense leaks',
        })
    
    if 'small_tier_cultivator' in signal_types:
        leaks.append(MARGIN_LEAKS['energy_costs'])
        leaks.append(MARGIN_LEAKS['labor_inefficiency'])
    
    if 'cultivator_no_mfg' in signal_types:
        leaks.append({
            'name': 'Value-Add Gap',
            'description': 'Selling raw material at commodity prices instead of processed goods',
            'quick_win': 'Partner with manufacturer for toll processing',
        })
    
    if 'mfg_no_cultivation' in signal_types:
        leaks.append({
            'name': 'Supply Chain Vulnerability',
            'description': 'Dependent on external suppliers with variable pricing and availability',
            'quick_win': 'Lock in long-term supply contracts',
        })
    
    # Operator type defaults
    if operator_type == 'retailer' and len(leaks) < 3:
        leaks.extend([MARGIN_LEAKS['pricing_leakage'], MARGIN_LEAKS['staffing_mismatch']])
    elif operator_type == 'cultivator' and len(leaks) < 3:
        leaks.extend([MARGIN_LEAKS['inventory_waste'], MARGIN_LEAKS['energy_costs']])
    elif operator_type == 'manufacturer' and len(leaks) < 3:
        leaks.extend([MARGIN_LEAKS['inventory_waste'], MARGIN_LEAKS['labor_inefficiency']])
    
    # Fill with general leaks if needed
    for leak_key in ['compliance_overhead', 'vendor_terms', 'marketing_waste']:
        if len(leaks) >= 3:
            break
        leaks.append(MARGIN_LEAKS[leak_key])
    
    return leaks[:3]


def get_fast_wins(operator_type: str) -> List[Dict[str, str]]:
    """Get fast wins based on operator type."""
    return FAST_WINS.get(operator_type, FAST_WINS['default'])[:3]


def generate_first_change(signals: List[Dict[str, Any]], operator_type: str) -> str:
    """Generate the 'what I'd change first' recommendation."""
    signal_types = [s['type'] for s in signals]

    if 'stalled_ops' in signal_types:
        return "Focus all resources on getting to revenue. Every month of delay is pure cost. Identify the single biggest blocker and dedicate 80% of your time to removing it."

    if 'market_pressure' in signal_types:
        return "Run a 30-day margin audit. Know your true cost per unit, identify your top 3 expense leaks, and cut them. In a market down 50%, the operators who survive are the ones who know their numbers cold."
    
    if 'cultivator_no_mfg' in signal_types:
        return "Stop selling raw flower at commodity prices. Find a toll processing partner this week. Even at 50/50 splits, you'll capture more margin than wholesale flower."
    
    if 'mfg_no_cultivation' in signal_types:
        return "Lock in a 6-month supply contract with a reliable cultivator. Variable input costs are killing your margins. Sacrifice some upside for predictability."
    
    if 'small_tier_cultivator' in signal_types:
        return "You can't compete on scale, so compete on quality. Focus on premium strains with higher margins rather than chasing volume. Consider seeking higher tier or partnership."
    
    if operator_type == 'retailer':
        return "Your Google Business Profile is your most valuable free marketing asset. Spend 2 hours optimizing it - photos, hours, posts, and responding to every review."
    
    if operator_type == 'cultivator':
        return "Calculate your true cost per gram including labor, energy, and waste. Most cultivators don't know this number, which means they can't improve it."
    
    return "Start with a 30-day expense audit. Categorize every dollar spent and identify the top 3 line items that could be reduced by 10% without impacting operations."


# =============================================================================
# SNAPSHOT GENERATION
# =============================================================================

def generate_snapshot(
    business_name: str,
    licenses: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate a complete snapshot for a business."""
    
    # Detect signals (with Google Places cross-validation)
    signals = detect_signals(licenses, business_name)
    operator_type = get_operator_type(licenses)
    
    # Get city and contact info
    city = ''
    email = ''
    phone = ''
    address = ''
    license_types = set()
    
    for lic in licenses:
        if not city and lic.get('city'):
            city = lic['city']
        if not email and lic.get('email'):
            email = lic['email']
        if not phone and lic.get('phone'):
            phone = lic['phone']
        if not address and lic.get('address'):
            address = lic['address']
        if lic.get('license_type'):
            license_types.add(lic['license_type'])
    
    # Build snapshot
    snapshot = {
        'business_name': business_name.title(),
        'city': city,
        'email': email,
        'phone': phone,
        'address': address,
        'operator_type': operator_type,
        'license_types': list(license_types),
        'generated_date': datetime.now().strftime('%Y-%m-%d'),
        
        'market_context': {
            'headline': MARKET_CONTEXT['headline'],
            'key_points': [
                MARKET_CONTEXT['price_decline'],
                MARKET_CONTEXT['competition'],
                MARKET_CONTEXT['consolidation'],
            ],
        },
        
        'pressure_signals': [
            {
                'name': s['name'],
                'description': s['description'],
                'severity': s.get('severity', 'medium'),
            }
            for s in signals[:3]
        ],
        
        'likely_leaks': get_likely_leaks(signals, operator_type),
        
        'fast_wins': get_fast_wins(operator_type),
        
        'first_change': generate_first_change(signals, operator_type),
    }
    
    return snapshot


# =============================================================================
# OUTPUT
# =============================================================================

def export_single_snapshot(
    snapshot: Dict[str, Any],
    output_dir: Path
) -> Path:
    """Export a single snapshot as JSON."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename from business name
    safe_name = re.sub(r'[^\w\s-]', '', snapshot['business_name']).strip()
    safe_name = re.sub(r'\s+', '_', safe_name).lower()
    
    output_path = output_dir / f"snapshot_{safe_name}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"   ✓ Exported snapshot to {output_path}")
    return output_path


def export_batch_snapshots(
    snapshots: List[Dict[str, Any]],
    output_dir: Path
) -> Path:
    """Export batch snapshots as CSV."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    output_path = output_dir / f"snapshots_ready_{today}.csv"
    
    fieldnames = [
        'Business Name', 'City', 'Email', 'Phone', 'Operator Type',
        'Signal 1', 'Signal 2', 'Signal 3',
        'Leak 1', 'Leak 1 Fix', 'Leak 2', 'Leak 2 Fix', 'Leak 3', 'Leak 3 Fix',
        'Win 1', 'Win 2', 'Win 3',
        'First Change',
        'Generated Date'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for snap in snapshots:
            signals = snap['pressure_signals']
            leaks = snap['likely_leaks']
            wins = snap['fast_wins']
            
            row = {
                'Business Name': snap['business_name'],
                'City': snap['city'],
                'Email': snap['email'],
                'Phone': snap['phone'],
                'Operator Type': snap['operator_type'],
                'Signal 1': signals[0]['name'] if len(signals) > 0 else '',
                'Signal 2': signals[1]['name'] if len(signals) > 1 else '',
                'Signal 3': signals[2]['name'] if len(signals) > 2 else '',
                'Leak 1': leaks[0]['name'] if len(leaks) > 0 else '',
                'Leak 1 Fix': leaks[0].get('quick_win', '') if len(leaks) > 0 else '',
                'Leak 2': leaks[1]['name'] if len(leaks) > 1 else '',
                'Leak 2 Fix': leaks[1].get('quick_win', '') if len(leaks) > 1 else '',
                'Leak 3': leaks[2]['name'] if len(leaks) > 2 else '',
                'Leak 3 Fix': leaks[2].get('quick_win', '') if len(leaks) > 2 else '',
                'Win 1': f"{wins[0]['name']}: {wins[0]['description']}" if len(wins) > 0 else '',
                'Win 2': f"{wins[1]['name']}: {wins[1]['description']}" if len(wins) > 1 else '',
                'Win 3': f"{wins[2]['name']}: {wins[2]['description']}" if len(wins) > 2 else '',
                'First Change': snap['first_change'],
                'Generated Date': snap['generated_date'],
            }
            writer.writerow(row)
    
    print(f"   ✓ Exported {len(snapshots)} snapshots to {output_path}")
    return output_path


def print_snapshot(snapshot: Dict[str, Any]) -> None:
    """Pretty print a snapshot to console."""
    
    print("\n" + "=" * 70)
    print(f"📊 MARGIN PRESSURE SNAPSHOT: {snapshot['business_name']}")
    print("=" * 70)
    
    print(f"\n📍 Location: {snapshot['city']}")
    print(f"📧 Email: {snapshot['email']}")
    print(f"📞 Phone: {snapshot['phone']}")
    print(f"🏷️  Type: {snapshot['operator_type'].title()}")
    
    print(f"\n{'─' * 70}")
    print("🌐 MARKET CONTEXT")
    print(f"{'─' * 70}")
    print(f"   {snapshot['market_context']['headline']}")
    for point in snapshot['market_context']['key_points']:
        print(f"   • {point}")
    
    print(f"\n{'─' * 70}")
    print("⚠️  PRESSURE SIGNALS")
    print(f"{'─' * 70}")
    for i, signal in enumerate(snapshot['pressure_signals'], 1):
        severity = signal.get('severity', 'medium').upper()
        print(f"   {i}. [{severity}] {signal['name']}")
        print(f"      {signal['description']}")
    
    print(f"\n{'─' * 70}")
    print("💸 LIKELY MARGIN LEAKS")
    print(f"{'─' * 70}")
    for i, leak in enumerate(snapshot['likely_leaks'], 1):
        print(f"   {i}. {leak['name']}")
        print(f"      Problem: {leak['description']}")
        print(f"      Quick Win: {leak.get('quick_win', 'N/A')}")
    
    print(f"\n{'─' * 70}")
    print("⚡ FAST WINS")
    print(f"{'─' * 70}")
    for i, win in enumerate(snapshot['fast_wins'], 1):
        print(f"   {i}. {win['name']}")
        print(f"      {win['description']}")
    
    print(f"\n{'─' * 70}")
    print("🎯 WHAT I'D CHANGE FIRST")
    print(f"{'─' * 70}")
    print(f"   {snapshot['first_change']}")
    
    print()


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate Margin Pressure Snapshots for cannabis operators'
    )
    parser.add_argument(
        '--name', '-n',
        type=str,
        help='Business name to generate snapshot for (single mode)'
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        help='CSV file with business names (batch mode, expects "Business Name" column)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON instead of CSV (batch mode only)'
    )
    
    args = parser.parse_args()
    
    if not args.name and not args.input:
        parser.error("Either --name or --input is required")
    
    print("\n📊 Margin Pressure Snapshot Generator")
    print("=" * 55)
    
    # Fetch license data
    license_data = fetch_ccc_licenses()
    if not license_data:
        print("\n❌ Failed to fetch license data. Check network connection.")
        return
    
    licenses_by_business = index_licenses_by_business(license_data)
    print(f"   • Indexed {len(licenses_by_business)} businesses")
    
    if args.name:
        # Single mode
        print(f"\n🔍 Looking for: {args.name}")
        
        matched_name, licenses = find_business(args.name, licenses_by_business)
        
        if not matched_name:
            print(f"\n❌ Business not found: {args.name}")
            print("   Try a different spelling or check the name in the CCC database.")
            return
        
        if matched_name.lower() != args.name.lower():
            print(f"   ✓ Matched to: {matched_name.title()}")
        
        snapshot = generate_snapshot(matched_name, licenses)
        print_snapshot(snapshot)
        
        output_path = export_single_snapshot(snapshot, args.output_dir)
        print(f"\n✅ Snapshot saved to {output_path}")
    
    else:
        # Batch mode
        print(f"\n📂 Loading targets from {args.input}")
        
        if not args.input.exists():
            print(f"\n❌ Input file not found: {args.input}")
            return
        
        # Read input CSV
        business_names = []
        with open(args.input, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Business Name', '') or row.get('business_name', '') or row.get('Name', '')
                if name:
                    business_names.append(name.strip())
        
        print(f"   • Found {len(business_names)} businesses in input file")
        
        snapshots = []
        not_found = []
        
        for name in business_names:
            matched_name, licenses = find_business(name, licenses_by_business)
            if matched_name and licenses:
                snapshot = generate_snapshot(matched_name, licenses)
                snapshots.append(snapshot)
            else:
                not_found.append(name)
        
        print(f"   ✓ Generated {len(snapshots)} snapshots")
        if not_found:
            print(f"   ⚠ Could not find: {', '.join(not_found[:5])}" + 
                  (f" and {len(not_found) - 5} more" if len(not_found) > 5 else ""))
        
        if args.json:
            for snap in snapshots:
                export_single_snapshot(snap, args.output_dir)
        else:
            output_path = export_batch_snapshots(snapshots, args.output_dir)
        
        print(f"\n✅ Done! Snapshots saved to {args.output_dir}")


if __name__ == '__main__':
    main()
