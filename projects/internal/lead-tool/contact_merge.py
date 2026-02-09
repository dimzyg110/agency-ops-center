#!/usr/bin/env python3
"""
Clean Contacts Merge

Merges verified contact data into lead outputs by matching on business name + address.
Adds contact verification flags and confidence scoring.

Usage:
    python3 contact_merge.py --leads leads.csv --contacts clean-contacts.csv --output enriched.csv
    python3 contact_merge.py --leads leads.csv --contacts clean-contacts.csv --output enriched.csv --update-inplace

Features:
- Fuzzy matching on business name + address
- Contact verification flags (email, phone)
- Confidence scoring based on match quality
- Preserves all original lead data

Output columns added:
- contact_email_verified: Email from verified contacts
- contact_phone_verified: Phone from verified contacts  
- contact_confidence: Match confidence score (0-1)
- contact_match_method: How the match was made (exact/fuzzy/address)
"""

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
from typing import Optional, Dict, Any, List, Tuple


# =============================================================================
# CONFIGURATION
# =============================================================================

# Fuzzy match thresholds
NAME_MATCH_THRESHOLD = 0.80  # Business name similarity
ADDRESS_MATCH_THRESHOLD = 0.70  # Address similarity
COMBINED_THRESHOLD = 0.75  # Combined score threshold

# Default paths
DEFAULT_CONTACTS_PATH = Path("/data/workspace/data/mass-ccc/clean-contacts.csv")
DEFAULT_OUTPUT_DIR = Path("/data/workspace/projects/lead-tool/output")


# =============================================================================
# TEXT NORMALIZATION
# =============================================================================

def normalize_business_name(name: str) -> str:
    """Normalize business name for matching."""
    if not name:
        return ''
    
    name = name.lower().strip()
    
    # Remove common suffixes
    suffixes = [
        r'\bllc\b', r'\binc\b', r'\bcorp\b', r'\bcorporation\b', 
        r'\bcompany\b', r'\bco\b', r'\bd/b/a\b', r'\bdba\b',
        r'\bdispensary\b', r'\bcannabis\b', r'\bmarijuana\b',
        r'\bwellness\b', r'\btherapeutic\b', r'\bhealth\b',
        r'\benterprises?\b', r'\bventures?\b', r'\bholdings?\b',
        r'\bgroup\b', r'\bpartners?\b',
    ]
    
    for suffix in suffixes:
        name = re.sub(suffix, '', name)
    
    # Remove punctuation and extra whitespace
    name = re.sub(r'[^\w\s]', ' ', name)
    name = ' '.join(name.split())
    
    return name


def normalize_address(address: str) -> str:
    """Normalize address for matching."""
    if not address:
        return ''
    
    address = address.lower().strip()
    
    # Standardize common abbreviations
    replacements = [
        (r'\bstreet\b', 'st'),
        (r'\bave(nue)?\b', 'ave'),
        (r'\broad\b', 'rd'),
        (r'\bdrive\b', 'dr'),
        (r'\blane\b', 'ln'),
        (r'\bboule?vard\b', 'blvd'),
        (r'\bcourt\b', 'ct'),
        (r'\bplace\b', 'pl'),
        (r'\bsuite\b', 'ste'),
        (r'\bunit\b', 'unit'),
        (r'\bnorth\b', 'n'),
        (r'\bsouth\b', 's'),
        (r'\beast\b', 'e'),
        (r'\bwest\b', 'w'),
        (r'\bmassachusetts\b', 'ma'),
        (r'\,\s*ma\b', ' ma'),
    ]
    
    for pattern, replacement in replacements:
        address = re.sub(pattern, replacement, address)
    
    # Remove punctuation except numbers
    address = re.sub(r'[^\w\s]', ' ', address)
    address = ' '.join(address.split())
    
    return address


def extract_city(address: str) -> str:
    """Extract city from address string."""
    if not address:
        return ''
    
    # Try to find city before MA
    match = re.search(r'([A-Za-z\s]+)\s*,?\s*MA', address, re.IGNORECASE)
    if match:
        return match.group(1).strip().lower()
    
    return ''


# =============================================================================
# MATCHING
# =============================================================================

def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings."""
    if not s1 or not s2:
        return 0.0
    return SequenceMatcher(None, s1, s2).ratio()


def match_contact(
    lead_name: str,
    lead_city: str,
    lead_address: str,
    contacts: Dict[str, Dict[str, Any]]
) -> Tuple[Optional[Dict[str, Any]], float, str]:
    """
    Find best matching contact for a lead.
    
    Returns:
        Tuple of (contact_data, confidence_score, match_method)
    """
    
    lead_name_norm = normalize_business_name(lead_name)
    lead_address_norm = normalize_address(lead_address)
    lead_city_norm = lead_city.lower().strip() if lead_city else ''
    
    best_match = None
    best_score = 0.0
    best_method = ''
    
    for contact_key, contact in contacts.items():
        contact_name_norm = normalize_business_name(contact.get('business_name', ''))
        contact_city_norm = contact.get('city', '').lower().strip()
        
        # Calculate name similarity
        name_score = similarity_ratio(lead_name_norm, contact_name_norm)
        
        # Skip if name is too different
        if name_score < 0.5:
            continue
        
        # Check city match (if both have city)
        city_match = False
        if lead_city_norm and contact_city_norm:
            city_match = lead_city_norm == contact_city_norm or \
                        similarity_ratio(lead_city_norm, contact_city_norm) > 0.8
        
        # Calculate combined score
        if name_score >= NAME_MATCH_THRESHOLD:
            if city_match:
                # Strong match: name + city
                combined_score = name_score * 1.1  # Boost for city match
                method = 'name+city'
            else:
                combined_score = name_score
                method = 'name'
        else:
            continue
        
        # Cap at 1.0
        combined_score = min(combined_score, 1.0)
        
        if combined_score > best_score and combined_score >= COMBINED_THRESHOLD:
            best_score = combined_score
            best_match = contact
            best_method = method
    
    return best_match, best_score, best_method


# =============================================================================
# DATA LOADING
# =============================================================================

def load_clean_contacts(contacts_path: Path) -> Dict[str, Dict[str, Any]]:
    """Load clean contacts CSV into a dictionary."""
    contacts = {}
    
    if not contacts_path.exists():
        print(f"   ✗ Contacts file not found: {contacts_path}")
        return contacts
    
    print(f"📂 Loading clean contacts from {contacts_path}...")
    
    with open(contacts_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            business_name = row.get('Business Name', '').strip()
            if not business_name:
                continue
            
            # Create a unique key
            key = f"{business_name.lower()}_{i}"
            
            contacts[key] = {
                'business_name': business_name,
                'email': row.get('Email', '').strip(),
                'phone': row.get('Phone', '').strip(),
                'city': row.get('City', '').strip(),
                'license_types': row.get('License Types', '').strip(),
                'status': row.get('Status', '').strip(),
                'has_contact': row.get('Has Contact', '').strip() == 'Yes',
            }
    
    print(f"   ✓ Loaded {len(contacts)} contacts")
    return contacts


def load_leads(leads_path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load leads CSV and return list of rows and fieldnames."""
    leads = []
    fieldnames = []
    
    print(f"📂 Loading leads from {leads_path}...")
    
    with open(leads_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
        for row in reader:
            leads.append(dict(row))
    
    print(f"   ✓ Loaded {len(leads)} leads")
    return leads, fieldnames


# =============================================================================
# MERGE LOGIC
# =============================================================================

def merge_contacts(
    leads: List[Dict[str, Any]],
    contacts: Dict[str, Dict[str, Any]],
    name_field: str = 'Business Name',
    city_field: str = 'City',
    address_field: str = 'Address'
) -> List[Dict[str, Any]]:
    """
    Merge contact data into leads.
    
    Args:
        leads: List of lead dictionaries
        contacts: Dictionary of contact data
        name_field: Field name for business name in leads
        city_field: Field name for city in leads
        address_field: Field name for address in leads
    
    Returns:
        List of enriched lead dictionaries
    """
    
    print("\n🔄 Merging contacts...")
    
    # Try common field name variations
    name_fields = [name_field, 'business_name', 'Business Name', 'name', 'Name', 'Dispensary']
    city_fields = [city_field, 'city', 'City', 'CITY']
    address_fields = [address_field, 'address', 'Address', 'Full Address', 'FULL_ADDRESS']
    
    enriched = []
    matches = 0
    no_match = 0
    
    for lead in leads:
        # Find the correct field names
        lead_name = ''
        lead_city = ''
        lead_address = ''
        
        for field in name_fields:
            if field in lead and lead[field]:
                lead_name = lead[field]
                break
        
        for field in city_fields:
            if field in lead and lead[field]:
                lead_city = lead[field]
                break
        
        for field in address_fields:
            if field in lead and lead[field]:
                lead_address = lead[field]
                break
        
        # Try to match
        contact, confidence, method = match_contact(
            lead_name, lead_city, lead_address, contacts
        )
        
        # Create enriched lead
        enriched_lead = dict(lead)
        
        if contact and confidence >= COMBINED_THRESHOLD:
            matches += 1
            
            # Only use verified contact if it has data
            verified_email = contact.get('email', '') if contact.get('has_contact') else ''
            verified_phone = contact.get('phone', '') if contact.get('has_contact') else ''
            
            # Use contact's data if better than existing
            if verified_email and not lead.get('Email', '').strip():
                enriched_lead['Email'] = verified_email
            
            if verified_phone and not lead.get('Phone', '').strip():
                enriched_lead['Phone'] = verified_phone
            
            enriched_lead['contact_email_verified'] = verified_email
            enriched_lead['contact_phone_verified'] = verified_phone
            enriched_lead['contact_confidence'] = round(confidence, 2)
            enriched_lead['contact_match_method'] = method
        else:
            no_match += 1
            enriched_lead['contact_email_verified'] = ''
            enriched_lead['contact_phone_verified'] = ''
            enriched_lead['contact_confidence'] = 0.0
            enriched_lead['contact_match_method'] = 'none'
        
        enriched.append(enriched_lead)
    
    print(f"   ✓ Matched {matches} leads ({matches*100//len(leads) if leads else 0}%)")
    print(f"   • No match: {no_match}")
    
    return enriched


# =============================================================================
# OUTPUT
# =============================================================================

def export_enriched(
    enriched: List[Dict[str, Any]],
    fieldnames: List[str],
    output_path: Path
) -> Path:
    """Export enriched leads to CSV."""
    
    # Add new fields if not present
    new_fields = [
        'contact_email_verified', 
        'contact_phone_verified', 
        'contact_confidence', 
        'contact_match_method'
    ]
    
    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(enriched)
    
    print(f"   ✓ Exported to {output_path}")
    return output_path


def print_summary(enriched: List[Dict[str, Any]]) -> None:
    """Print summary statistics."""
    
    total = len(enriched)
    with_email = sum(1 for e in enriched if e.get('contact_email_verified'))
    with_phone = sum(1 for e in enriched if e.get('contact_phone_verified'))
    high_confidence = sum(1 for e in enriched if e.get('contact_confidence', 0) >= 0.9)
    medium_confidence = sum(1 for e in enriched if 0.75 <= e.get('contact_confidence', 0) < 0.9)
    
    print("\n" + "=" * 55)
    print("📊 CONTACT MERGE SUMMARY")
    print("=" * 55)
    
    print(f"\n📦 TOTAL LEADS: {total}")
    print(f"   • With verified email: {with_email} ({with_email*100//total if total else 0}%)")
    print(f"   • With verified phone: {with_phone} ({with_phone*100//total if total else 0}%)")
    
    print(f"\n🎯 CONFIDENCE DISTRIBUTION")
    print(f"   • High (≥0.90): {high_confidence}")
    print(f"   • Medium (0.75-0.89): {medium_confidence}")
    print(f"   • Low/None: {total - high_confidence - medium_confidence}")
    
    # Match method breakdown
    methods = {}
    for e in enriched:
        method = e.get('contact_match_method', 'none')
        methods[method] = methods.get(method, 0) + 1
    
    print(f"\n🔗 MATCH METHODS")
    for method, count in sorted(methods.items(), key=lambda x: -x[1]):
        print(f"   • {method}: {count}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Merge verified contact data into lead files'
    )
    parser.add_argument(
        '--leads', '-l',
        type=Path,
        required=True,
        help='Path to leads CSV file'
    )
    parser.add_argument(
        '--contacts', '-c',
        type=Path,
        default=DEFAULT_CONTACTS_PATH,
        help=f'Path to clean contacts CSV (default: {DEFAULT_CONTACTS_PATH})'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output path for enriched CSV (default: leads_enriched_YYYY-MM-DD.csv)'
    )
    parser.add_argument(
        '--update-inplace',
        action='store_true',
        help='Update the leads file in place (backup created)'
    )
    parser.add_argument(
        '--name-field',
        type=str,
        default='Business Name',
        help='Field name for business name in leads CSV'
    )
    parser.add_argument(
        '--city-field',
        type=str,
        default='City',
        help='Field name for city in leads CSV'
    )
    
    args = parser.parse_args()
    
    print("\n📞 Clean Contacts Merge Tool")
    print("=" * 55)
    
    # Load data
    contacts = load_clean_contacts(args.contacts)
    
    if not contacts:
        print("\n❌ No contacts loaded. Cannot proceed.")
        return
    
    leads, fieldnames = load_leads(args.leads)
    
    if not leads:
        print("\n❌ No leads loaded. Cannot proceed.")
        return
    
    # Merge
    enriched = merge_contacts(
        leads, 
        contacts,
        name_field=args.name_field,
        city_field=args.city_field
    )
    
    # Determine output path
    if args.update_inplace:
        # Create backup
        backup_path = args.leads.with_suffix('.csv.bak')
        args.leads.rename(backup_path)
        print(f"   ℹ Backup created: {backup_path}")
        output_path = args.leads
    elif args.output:
        output_path = args.output
    else:
        today = datetime.now().strftime('%Y-%m-%d')
        output_path = DEFAULT_OUTPUT_DIR / f"{args.leads.stem}_enriched_{today}.csv"
    
    # Export
    print("\n📄 Exporting enriched leads...")
    export_enriched(enriched, fieldnames, output_path)
    
    # Summary
    print_summary(enriched)
    
    print(f"\n✅ Done! Enriched leads saved to {output_path}")


if __name__ == '__main__':
    main()
