#!/usr/bin/env python3
"""
Change Log Snapshot Generator

Tracks weekly changes in MA CCC license data:
- New licenses issued
- Status changes (Active → Expired, etc.)
- Commence operations changes
- License tier changes

Usage:
    python3 change_log.py                      # Run snapshot and generate delta
    python3 change_log.py --snapshot-only      # Just save current snapshot
    python3 change_log.py --compare 2026-01-01 # Compare to specific date

Output:
    - snapshots/ccc_snapshot_YYYY-MM-DD.json   (weekly state snapshots)
    - change_log_YYYY-MM-DD.csv                (delta report)
"""

import argparse
import csv
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Set

from ccc_client import build_default_client


# =============================================================================
# CONFIGURATION
# =============================================================================

# Storage paths
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = Path(
    os.environ.get("LEAD_TOOL_CHANGELOG_DATA_DIR", str(BASE_DIR / "data"))
)
SNAPSHOT_DIR = DEFAULT_DATA_DIR / "snapshots"
OUTPUT_DIR = Path(
    os.environ.get("LEAD_TOOL_OUTPUT_DIR", str(BASE_DIR / "output"))
)

CCC_CLIENT = build_default_client(BASE_DIR)

# Fields to track for changes
TRACKED_FIELDS = [
    'LIC_STATUS',
    'COMMENCE_OPERATIONS_DATE',
    'CULTIVATION_TIER',
    'LICENSE_TYPE',
]

# License types we care about
TARGET_LICENSE_TYPES = {
    'Marijuana Cultivator',
    'Marijuana Product Manufacturer',
    'Marijuana Microbusiness',
    'Marijuana Retailer',
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


def normalize_license(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a license record for consistent comparison."""
    return {
        'license_number': record.get('LICENSE_NUMBER', '').strip(),
        'business_name': record.get('BUSINESS_NAME', '').strip(),
        'license_type': record.get('LICENSE_TYPE', '').strip(),
        'status': record.get('LIC_STATUS', '').strip(),
        'city': record.get('CITY', '').strip() or record.get('ESTABLISHMENT_CITY', '').strip(),
        'email': record.get('BUSINESS_EMAIL', '').strip(),
        'phone': record.get('BUSINESS_PHONE', '').strip(),
        'approved_date': record.get('APPLICATION_APPROVED_DATE', '').strip(),
        'commence_date': record.get('COMMENCE_OPERATIONS_DATE', '').strip(),
        'cultivation_tier': record.get('CULTIVATION_TIER', '').strip(),
        'address': record.get('FULL_ADDRESS', '').strip(),
    }


# =============================================================================
# SNAPSHOT MANAGEMENT
# =============================================================================

def save_snapshot(licenses: List[Dict[str, Any]], snapshot_path: Path) -> None:
    """Save current license state to a JSON snapshot."""
    
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Normalize and index by license number
    snapshot = {}
    for lic in licenses:
        normalized = normalize_license(lic)
        key = normalized['license_number']
        if key:
            snapshot[key] = normalized
    
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump({
            'snapshot_date': datetime.now().isoformat(),
            'license_count': len(snapshot),
            'licenses': snapshot,
        }, f, indent=2)
    
    print(f"   ✓ Saved snapshot with {len(snapshot)} licenses to {snapshot_path}")


def load_snapshot(snapshot_path: Path) -> Optional[Dict[str, Dict[str, Any]]]:
    """Load a license snapshot from JSON."""
    
    if not snapshot_path.exists():
        return None
    
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   ✓ Loaded snapshot from {snapshot_path.name} ({data.get('license_count', 0)} licenses)")
    return data.get('licenses', {})


def find_latest_snapshot(before_date: Optional[datetime] = None) -> Optional[Path]:
    """Find the most recent snapshot file before a given date."""
    
    if not SNAPSHOT_DIR.exists():
        return None
    
    snapshots = sorted(SNAPSHOT_DIR.glob("ccc_snapshot_*.json"), reverse=True)
    
    for snap_path in snapshots:
        # Extract date from filename
        try:
            date_str = snap_path.stem.replace("ccc_snapshot_", "")
            snap_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            if before_date is None or snap_date < before_date:
                return snap_path
        except ValueError:
            continue
    
    return None


def find_snapshot_for_date(target_date: str) -> Optional[Path]:
    """Find snapshot for a specific date."""
    
    snapshot_path = SNAPSHOT_DIR / f"ccc_snapshot_{target_date}.json"
    
    if snapshot_path.exists():
        return snapshot_path
    
    return None


# =============================================================================
# CHANGE DETECTION
# =============================================================================

def detect_changes(
    current: Dict[str, Dict[str, Any]],
    previous: Dict[str, Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Compare two snapshots and detect changes.
    
    Returns:
        Dictionary with keys: 'new', 'removed', 'status_changed', 
        'commenced', 'tier_changed'
    """
    
    changes = {
        'new': [],
        'removed': [],
        'status_changed': [],
        'commenced': [],
        'tier_changed': [],
    }
    
    current_keys = set(current.keys())
    previous_keys = set(previous.keys())
    
    # New licenses
    for key in current_keys - previous_keys:
        lic = current[key]
        changes['new'].append({
            'license_number': key,
            'business_name': lic['business_name'],
            'license_type': lic['license_type'],
            'city': lic['city'],
            'status': lic['status'],
            'change_type': 'NEW_LICENSE',
            'old_value': '',
            'new_value': lic['status'],
        })
    
    # Removed licenses (rare, but possible)
    for key in previous_keys - current_keys:
        lic = previous[key]
        changes['removed'].append({
            'license_number': key,
            'business_name': lic['business_name'],
            'license_type': lic['license_type'],
            'city': lic['city'],
            'status': lic['status'],
            'change_type': 'REMOVED',
            'old_value': lic['status'],
            'new_value': '',
        })
    
    # Changes in existing licenses
    for key in current_keys & previous_keys:
        curr = current[key]
        prev = previous[key]
        
        # Status change
        if curr['status'] != prev['status']:
            changes['status_changed'].append({
                'license_number': key,
                'business_name': curr['business_name'],
                'license_type': curr['license_type'],
                'city': curr['city'],
                'status': curr['status'],
                'change_type': 'STATUS_CHANGE',
                'old_value': prev['status'],
                'new_value': curr['status'],
            })
        
        # Commenced operations
        if curr['commence_date'] and not prev['commence_date']:
            changes['commenced'].append({
                'license_number': key,
                'business_name': curr['business_name'],
                'license_type': curr['license_type'],
                'city': curr['city'],
                'status': curr['status'],
                'change_type': 'COMMENCED_OPS',
                'old_value': '',
                'new_value': curr['commence_date'],
            })
        
        # Cultivation tier change
        if curr['cultivation_tier'] != prev['cultivation_tier']:
            if curr['cultivation_tier'] or prev['cultivation_tier']:  # Skip if both empty
                changes['tier_changed'].append({
                    'license_number': key,
                    'business_name': curr['business_name'],
                    'license_type': curr['license_type'],
                    'city': curr['city'],
                    'status': curr['status'],
                    'change_type': 'TIER_CHANGE',
                    'old_value': prev['cultivation_tier'],
                    'new_value': curr['cultivation_tier'],
                })
    
    return changes


# =============================================================================
# OUTPUT
# =============================================================================

def export_change_log(
    changes: Dict[str, List[Dict[str, Any]]],
    output_path: Path,
    previous_date: str
) -> Path:
    """Export changes to CSV."""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Flatten all changes
    all_changes = []
    for change_type, items in changes.items():
        for item in items:
            all_changes.append(item)
    
    # Sort by change type, then business name
    all_changes.sort(key=lambda x: (x['change_type'], x['business_name']))
    
    fieldnames = [
        'Change Type', 'License Number', 'Business Name', 'License Type',
        'City', 'Current Status', 'Previous Value', 'New Value', 'Notes'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in all_changes:
            writer.writerow({
                'Change Type': item['change_type'],
                'License Number': item['license_number'],
                'Business Name': item['business_name'],
                'License Type': item['license_type'],
                'City': item['city'],
                'Current Status': item['status'],
                'Previous Value': item['old_value'],
                'New Value': item['new_value'],
                'Notes': '',
            })
    
    print(f"   ✓ Exported {len(all_changes)} changes to {output_path}")
    return output_path


def print_summary(
    changes: Dict[str, List[Dict[str, Any]]],
    previous_date: str,
    current_date: str
) -> None:
    """Print change summary."""
    
    total_changes = sum(len(items) for items in changes.values())
    
    print("\n" + "=" * 60)
    print("📊 CCC LICENSE CHANGE LOG")
    print("=" * 60)
    
    print(f"\n📅 Comparing: {previous_date} → {current_date}")
    print(f"📈 Total changes: {total_changes}")
    
    print(f"\n{'─' * 60}")
    print("CHANGE BREAKDOWN")
    print(f"{'─' * 60}")
    print(f"   • New licenses:        {len(changes['new'])}")
    print(f"   • Removed licenses:    {len(changes['removed'])}")
    print(f"   • Status changes:      {len(changes['status_changed'])}")
    print(f"   • Commenced operations:{len(changes['commenced'])}")
    print(f"   • Tier changes:        {len(changes['tier_changed'])}")
    
    # Show new licenses
    if changes['new']:
        print(f"\n{'─' * 60}")
        print("🆕 NEW LICENSES (Top 10)")
        print(f"{'─' * 60}")
        for item in changes['new'][:10]:
            print(f"   • {item['business_name'][:35]:<35} ({item['license_type'][:20]})")
    
    # Show commenced operations
    if changes['commenced']:
        print(f"\n{'─' * 60}")
        print("🎉 COMMENCED OPERATIONS")
        print(f"{'─' * 60}")
        for item in changes['commenced'][:10]:
            print(f"   • {item['business_name'][:35]:<35} ({item['new_value']})")
    
    # Show status changes (esp. to Expired/Surrendered)
    status_to_inactive = [
        c for c in changes['status_changed'] 
        if c['new_value'] in ('Expired', 'Surrendered', 'Revoked')
    ]
    if status_to_inactive:
        print(f"\n{'─' * 60}")
        print("⚠️  LICENSES GONE INACTIVE")
        print(f"{'─' * 60}")
        for item in status_to_inactive[:10]:
            print(f"   • {item['business_name'][:35]:<35} ({item['old_value']} → {item['new_value']})")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Track weekly changes in MA CCC license data'
    )
    parser.add_argument(
        '--snapshot-only',
        action='store_true',
        help='Only save snapshot, do not generate change log'
    )
    parser.add_argument(
        '--compare',
        type=str,
        help='Compare to snapshot from specific date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=OUTPUT_DIR,
        help=f'Output directory for change log (default: {OUTPUT_DIR})'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f'Data directory for snapshots (default: {DEFAULT_DATA_DIR})'
    )
    
    args = parser.parse_args()
    
    # Update paths based on args
    global SNAPSHOT_DIR
    SNAPSHOT_DIR = args.data_dir / "snapshots"
    
    print("\n📋 CCC License Change Log Generator")
    print("=" * 55)
    
    # Fetch current data
    license_data = fetch_ccc_licenses()
    
    if not license_data:
        print("\n❌ Failed to fetch license data. Cannot proceed.")
        return
    
    # Normalize current data
    current = {}
    for lic in license_data:
        normalized = normalize_license(lic)
        key = normalized['license_number']
        if key:
            current[key] = normalized
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_dt = datetime.now()
    
    # Save current snapshot
    snapshot_path = SNAPSHOT_DIR / f"ccc_snapshot_{today}.json"
    
    if args.snapshot_only:
        save_snapshot(license_data, snapshot_path)
        print(f"\n✅ Snapshot saved. Run without --snapshot-only to generate change log.")
        return
    
    # Find previous snapshot to compare
    print("\n🔍 Looking for previous snapshot...")
    
    if args.compare:
        previous_path = find_snapshot_for_date(args.compare)
        if not previous_path:
            print(f"   ✗ No snapshot found for {args.compare}")
            print("   Available snapshots:")
            for snap in sorted(SNAPSHOT_DIR.glob("ccc_snapshot_*.json")):
                print(f"      • {snap.name}")
            return
        previous_date = args.compare
    else:
        previous_path = find_latest_snapshot(before_date=today_dt)
        if previous_path:
            previous_date = previous_path.stem.replace("ccc_snapshot_", "")
        else:
            print("   ℹ No previous snapshot found. Saving initial snapshot.")
            save_snapshot(license_data, snapshot_path)
            print(f"\n✅ Initial snapshot saved. Run again later to detect changes.")
            return
    
    # Load previous snapshot
    previous = load_snapshot(previous_path)
    
    if not previous:
        print(f"   ✗ Failed to load previous snapshot")
        return
    
    # Detect changes
    print("\n🔄 Detecting changes...")
    changes = detect_changes(current, previous)
    
    total_changes = sum(len(items) for items in changes.values())
    
    if total_changes == 0:
        print("   ℹ No changes detected since last snapshot.")
        # Still save today's snapshot
        save_snapshot(license_data, snapshot_path)
        return
    
    # Save current snapshot
    save_snapshot(license_data, snapshot_path)
    
    # Export change log
    print("\n📄 Exporting change log...")
    output_path = args.output_dir / f"change_log_{today}.csv"
    export_change_log(changes, output_path, previous_date)
    
    # Print summary
    print_summary(changes, previous_date, today)
    
    print(f"\n✅ Done! Change log saved to {output_path}")


if __name__ == '__main__':
    main()
