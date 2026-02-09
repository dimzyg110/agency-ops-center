#!/usr/bin/env python3
"""
Outreach Generator

Creates a ready-to-send CSV with:
- Contact info
- Personalized email subject
- Personalized email body
- Call script notes

Usage:
    python3 outreach_generator.py --input signals_pack.csv --output outreach_ready.csv --limit 25
"""

import csv
import json
import argparse
from datetime import datetime
from pathlib import Path

# Email templates
DISPENSARY_EMAIL_TEMPLATE = """Hey {first_name},

Quick question about {business_name}.

I've been tracking MA dispensary data and noticed {pain_point}. 

Wanted to see if that's something on your radar, or if you've already got it handled.

Either way—no pitch, just curious if the data matches reality.

Randy
Roviq
randy@roviqai.xyz"""

VENDOR_EMAIL_TEMPLATE = """Hey {first_name},

I run market intelligence for the MA cannabis space.

We've mapped 600+ operators and scored them by buying signals—things like menu gaps, hiring activity, and operational status.

If you sell to dispensaries, I can tell you who actually needs what you're selling (vs. who's just on a license list).

Worth a quick call?

Randy
Roviq
randy@roviqai.xyz"""

def extract_first_name(email):
    """Try to extract first name from email."""
    if not email:
        return "there"
    local = email.split('@')[0]
    # Common patterns: first.last, firstlast, first_last
    for sep in ['.', '_']:
        if sep in local:
            return local.split(sep)[0].title()
    # If it looks like a name (not info@, admin@, etc.)
    generic = ['info', 'admin', 'contact', 'hello', 'sales', 'support', 'team']
    if local.lower() not in generic and len(local) > 2:
        return local.title()
    return "there"

def generate_pain_point(row):
    """Generate personalized pain point from signals."""
    signals = row.get('Pressure Signals', '') or row.get('pressure_signals', '')
    why_now = row.get('Why Now', '') or row.get('why_now', '')
    
    if 'stalled_ops' in signals:
        months = signals.split('stalled_ops_')[1].split('mo')[0] if 'stalled_ops_' in signals else '?'
        return f"you've been licensed for {months}+ months without commencing operations—that's a lot of capital sitting idle"
    elif 'expired_licenses' in signals:
        return "you've had some license expirations, which can signal cash flow pressure"
    elif 'small_tier' in signals:
        return "you're running a smaller-tier operation in a market where margins are getting crushed by scale"
    elif why_now:
        return why_now[:100] + "..." if len(why_now) > 100 else why_now
    else:
        return "the MA market has compressed 73% on wholesale pricing since 2021"

def generate_subject(row):
    """Generate personalized subject line."""
    business = row.get('Business Name', '') or row.get('business_name', '')
    city = row.get('City', '') or row.get('city', '')
    
    subjects = [
        f"Quick question about {business}",
        f"{city} dispensary margins - seeing something interesting",
        f"Data on {business} - worth 2 min?",
        f"Noticed something about {business}",
    ]
    # Rotate based on rank
    rank = int(row.get('Rank', 1) or 1)
    return subjects[rank % len(subjects)]

def main():
    parser = argparse.ArgumentParser(description='Generate outreach-ready CSV')
    parser.add_argument('--input', '-i', default='output/ma_operator_signals_pack_2026-02-04.csv',
                        help='Input signals pack CSV')
    parser.add_argument('--output', '-o', default='output/outreach_ready.csv',
                        help='Output CSV path')
    parser.add_argument('--limit', '-l', type=int, default=25,
                        help='Number of leads to generate')
    parser.add_argument('--type', '-t', choices=['dispensary', 'vendor'], default='dispensary',
                        help='Outreach type')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return
    
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= args.limit:
                break
            rows.append(row)
    
    print(f"📧 Generating outreach for {len(rows)} leads...")
    
    outreach_rows = []
    for row in rows:
        email = row.get('Email', '') or row.get('email', '')
        if not email or email == 'None':
            continue
            
        first_name = extract_first_name(email)
        business = row.get('Business Name', '') or row.get('business_name', '')
        pain_point = generate_pain_point(row)
        
        if args.type == 'dispensary':
            body = DISPENSARY_EMAIL_TEMPLATE.format(
                first_name=first_name,
                business_name=business,
                pain_point=pain_point
            )
        else:
            body = VENDOR_EMAIL_TEMPLATE.format(first_name=first_name)
        
        outreach_rows.append({
            'Rank': row.get('Rank', ''),
            'Business Name': business,
            'City': row.get('City', '') or row.get('city', ''),
            'Email': email,
            'Phone': row.get('Phone', '') or row.get('phone', ''),
            'Distress Score': row.get('Distress Score', '') or row.get('distress_score', ''),
            'Subject': generate_subject(row),
            'Email Body': body,
            'Talk Track': row.get('Talk Track', '') or row.get('talk_track', ''),
            'Why Now': row.get('Why Now', '') or row.get('why_now', ''),
            'Status': 'Ready to Send',
            'Sent': '',
            'Response': '',
            'Notes': ''
        })
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        if outreach_rows:
            writer = csv.DictWriter(f, fieldnames=outreach_rows[0].keys())
            writer.writeheader()
            writer.writerows(outreach_rows)
    
    print(f"✅ Generated {len(outreach_rows)} outreach records")
    print(f"📄 Output: {output_path}")

if __name__ == '__main__':
    main()
