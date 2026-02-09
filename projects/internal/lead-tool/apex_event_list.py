#!/usr/bin/env python3
"""
Apex Event List Generator

Generates scored, tiered invite lists from Apex Buyer Activity exports.
Designed for event outreach (Superbowl, AC Certified launches, etc.)

Usage:
    python3 apex_event_list.py /path/to/Buyer_Activity_Logs.csv

Output:
    - event_invite_list_YYYY-MM-DD.csv (in current directory)
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict

# =============================================================================
# CONFIGURATION - Modify these for different events
# =============================================================================

# Geographic bonus cities (accounts in these areas get +10 score)
# Modify based on event location
PRIORITY_CITIES = [
    'Boston', 'Cambridge', 'Chelsea', 'Somerville', 'Woburn', 'Medford',
    'Malden', 'Everett', 'Revere', 'Lynn', 'Newton', 'Brookline',
    'Quincy', 'Brockton', 'Abington', 'Hyde Park', 'Dorchester',
    'Charlestown', 'South Boston', 'Roxbury', 'Allston', 'Brighton'
]

# Scoring weights
ACTIVITY_WEIGHT = 2      # Multiplied by activity count (capped at 50)
GEO_BONUS = 10           # Added if in priority city

# Tier thresholds
TIER_1_MIN = 40  # Top priority
TIER_2_MIN = 25  # Strong candidates
TIER_3_MIN = 15  # Worth inviting
# Below TIER_3_MIN = Tier 4 (low priority)

# =============================================================================
# MAIN SCRIPT
# =============================================================================

def extract_city(location):
    """Extract city name from address string."""
    if not location:
        return ''
    match = re.search(r',\s*([A-Za-z\s]+)\s+MA', location)
    return match.group(1).strip() if match else ''


def is_priority_city(city):
    """Check if city is in priority list."""
    city_lower = city.lower()
    return any(pc.lower() in city_lower for pc in PRIORITY_CITIES)


def process_apex_export(input_path):
    """Process Apex buyer activity export and generate scored list."""

    buyers = defaultdict(lambda: {
        'contact_name': '',
        'contact_email': '',
        'contact_phone': '',
        'location': '',
        'city': '',
        'activity_count': 0,
        'last_updated': None
    })

    print(f"Reading: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            buyer = row.get('Buyer', '').strip()
            if not buyer:
                continue

            buyers[buyer]['activity_count'] += 1

            # Get first contact info found
            if not buyers[buyer]['contact_name']:
                buyers[buyer]['contact_name'] = row.get('Contact Name', '').strip()
                buyers[buyer]['contact_email'] = row.get('Contact Email', '').strip()
                buyers[buyer]['contact_phone'] = row.get('Contact Number', '').strip()

            # Get location
            location = row.get('Location', '').strip()
            if location and not buyers[buyer]['location']:
                buyers[buyer]['location'] = location
                buyers[buyer]['city'] = extract_city(location)

            # Track last updated
            date_str = row.get('Last Updated', '').strip()
            if date_str:
                try:
                    date = datetime.strptime(date_str.split(',')[0], '%m/%d/%y')
                    if not buyers[buyer]['last_updated'] or date > buyers[buyer]['last_updated']:
                        buyers[buyer]['last_updated'] = date
                except:
                    pass

    print(f"Found {len(buyers)} unique accounts")

    # Score and tier
    results = []
    for buyer, info in buyers.items():
        activity_score = min(info['activity_count'], 50) * ACTIVITY_WEIGHT
        geo_score = GEO_BONUS if is_priority_city(info['city']) else 0
        total_score = activity_score + geo_score

        # Determine tier
        if total_score >= TIER_1_MIN:
            tier = "TIER 1"
        elif total_score >= TIER_2_MIN:
            tier = "TIER 2"
        elif total_score >= TIER_3_MIN:
            tier = "TIER 3"
        else:
            tier = "TIER 4"

        results.append({
            'tier': tier,
            'score': total_score,
            'buyer': buyer,
            'contact_name': info['contact_name'],
            'contact_email': info['contact_email'],
            'contact_phone': info['contact_phone'],
            'city': info['city'],
            'activity': info['activity_count'],
            'priority_area': 'Yes' if geo_score > 0 else 'No',
            'location': info['location'],
            'last_updated': info['last_updated'].strftime('%Y-%m-%d') if info['last_updated'] else ''
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def write_output(results, output_path):
    """Write scored results to CSV."""

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Tier', 'Score', 'Dispensary', 'Contact Name', 'Email', 'Phone',
            'City', 'Activity Count', 'Priority Area', 'Last Activity', 'Full Address',
            'Invited', 'Budtender Ask', 'RSVP Status', 'Budtender Names', 'Notes'
        ])
        writer.writeheader()

        for r in results:
            writer.writerow({
                'Tier': r['tier'],
                'Score': r['score'],
                'Dispensary': r['buyer'],
                'Contact Name': r['contact_name'],
                'Email': r['contact_email'],
                'Phone': r['contact_phone'],
                'City': r['city'],
                'Activity Count': r['activity'],
                'Priority Area': r['priority_area'],
                'Last Activity': r['last_updated'],
                'Full Address': r['location'],
                'Invited': '',
                'Budtender Ask': '',
                'RSVP Status': '',
                'Budtender Names': '',
                'Notes': ''
            })

    print(f"Written: {output_path}")


def print_summary(results):
    """Print summary statistics."""

    tier_counts = {'TIER 1': 0, 'TIER 2': 0, 'TIER 3': 0, 'TIER 4': 0}
    priority_count = 0

    for r in results:
        tier_counts[r['tier']] += 1
        if r['priority_area'] == 'Yes':
            priority_count += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total accounts:        {len(results)}")
    print(f"Tier 1 (Top Priority): {tier_counts['TIER 1']}")
    print(f"Tier 2 (Strong):       {tier_counts['TIER 2']}")
    print(f"Tier 3 (Worth it):     {tier_counts['TIER 3']}")
    print(f"Tier 4 (Low priority): {tier_counts['TIER 4']}")
    print(f"Priority area:         {priority_count}")

    print("\n" + "-" * 60)
    print("TOP 20 ACCOUNTS")
    print("-" * 60)

    for i, r in enumerate(results[:20], 1):
        print(f"{i:>2}. [{r['tier']}] {r['buyer'][:35]:<35} | {r['contact_name'][:15]:<15} | {r['city'][:12]}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 apex_event_list.py /path/to/Buyer_Activity_Logs.csv")
        print("\nThis script generates a scored invite list from Apex exports.")
        print("Modify PRIORITY_CITIES at the top of the script for different event locations.")
        sys.exit(1)

    input_path = sys.argv[1]
    today = datetime.now().strftime('%Y-%m-%d')
    output_path = f"event_invite_list_{today}.csv"

    results = process_apex_export(input_path)
    write_output(results, output_path)
    print_summary(results)

    print(f"\n✅ Done! Open {output_path} to start outreach.")


if __name__ == '__main__':
    main()
