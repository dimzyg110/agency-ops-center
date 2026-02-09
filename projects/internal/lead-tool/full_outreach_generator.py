#!/usr/bin/env python3
"""
Full Outreach Sequence Generator

Creates 100+ leads with:
- Initial email
- Follow-up email (3 days later)
- Second follow-up (7 days later)
- SMS/text message
- Call script notes

Usage:
    python3 full_outreach_generator.py --limit 100 --output output/full_outreach.csv
"""

import csv
import argparse
from datetime import datetime
from pathlib import Path

# Email templates
EMAIL_1_TEMPLATE = """Subject: {subject_1}

Hey {first_name},

Quick question about {business_name}.

I've been tracking MA dispensary data and noticed {pain_point}.

Wanted to see if that's something on your radar, or if you've already got it handled.

Either way—no pitch, just curious if the data matches reality.

— Roviq Team
team@roviqai.xyz"""

EMAIL_2_TEMPLATE = """Subject: {subject_2}

Hey {first_name},

Following up on my note about {business_name}.

Quick context: We track margin pressure signals across 600+ MA operators. Your profile flagged a few things worth a 5-minute look.

Happy to send over a free snapshot if helpful—no strings.

— Roviq Team"""

EMAIL_3_TEMPLATE = """Subject: {subject_3}

{first_name} —

Last try. We built a 1-page Margin Pressure Snapshot for {business_name}.

Shows where you're likely leaking profit vs. local competitors.

Want it? Just reply "send it" and it's yours. Free.

If not, no worries—I'll stop bugging you.

— Roviq"""

SMS_TEMPLATE = """Hey {first_name}, this is Roviq. We track MA dispensary margins. Noticed some signals on {business_name}. Worth a quick look? Can send a free snapshot. Text back if interested."""

CALL_SCRIPT = """INTRO: "Hey {first_name}, this is [name] from Roviq. We do margin intelligence for MA dispensaries. Got 60 seconds?"

HOOK: "I've been tracking your market and noticed {pain_point_short}. Wanted to see if that matches what you're seeing."

PIVOT: "We built a free 1-page snapshot that shows where you might be leaking profit. Can I send it over?"

CLOSE: "What's the best email for that?"

OBJECTION - NO TIME: "Totally get it. Can I just email the snapshot? Takes 2 min to review."

OBJECTION - NOT INTERESTED: "No problem. Quick question though—is it because things are going well, or because you're drowning and can't think about it right now?"
"""

def extract_first_name(email):
    """Try to extract first name from email."""
    if not email:
        return "there"
    local = email.split('@')[0]
    for sep in ['.', '_']:
        if sep in local:
            return local.split(sep)[0].title()
    generic = ['info', 'admin', 'contact', 'hello', 'sales', 'support', 'team']
    if local.lower() not in generic and len(local) > 2:
        return local.title()
    return "there"

def generate_pain_point(row):
    """Generate personalized pain point from signals."""
    signals = row.get('Pressure Signals', '') or row.get('pressure_signals', '')
    
    if 'stalled_ops' in signals:
        months = signals.split('stalled_ops_')[1].split('mo')[0] if 'stalled_ops_' in signals else '?'
        return f"you've been licensed for {months}+ months without commencing operations—capital sitting idle"
    elif 'expired_licenses' in signals:
        return "you've had some license expirations, which can signal cash flow pressure"
    elif 'small_tier' in signals:
        return "you're running a smaller-tier operation in a margin-compressed market"
    else:
        return "the MA market has compressed 73% on wholesale pricing"

def generate_pain_point_short(row):
    """Short version for calls/SMS."""
    signals = row.get('Pressure Signals', '') or ''
    if 'stalled_ops' in signals:
        return "stalled operations for a while"
    elif 'expired_licenses' in signals:
        return "some license pressure"
    elif 'small_tier' in signals:
        return "margin pressure on smaller ops"
    else:
        return "some margin signals"

def generate_subjects(row, rank):
    """Generate subject lines for email sequence."""
    business = row.get('Business Name', '')
    city = row.get('City', '')
    
    subjects_1 = [
        f"Quick question about {business}",
        f"{city} dispensary margins - seeing something",
        f"Data on {business}",
        f"Noticed something about {business}",
        f"{business} - 2 min question",
    ]
    
    subjects_2 = [
        f"Following up - {business}",
        f"Re: {business} margin data",
        f"Quick follow-up",
        f"Did you see my note about {business}?",
    ]
    
    subjects_3 = [
        f"Free snapshot for {business}",
        f"Last try - {business}",
        f"Your margin report (free)",
        f"Closing the loop - {business}",
    ]
    
    return (
        subjects_1[rank % len(subjects_1)],
        subjects_2[rank % len(subjects_2)],
        subjects_3[rank % len(subjects_3)]
    )

def main():
    parser = argparse.ArgumentParser(description='Generate full outreach sequence')
    parser.add_argument('--input', '-i', default='output/ma_operator_signals_pack_2026-02-04.csv')
    parser.add_argument('--output', '-o', default='output/full_outreach_100.csv')
    parser.add_argument('--limit', '-l', type=int, default=100)
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"❌ Input not found: {input_path}")
        return
    
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= args.limit:
                break
            rows.append(row)
    
    print(f"📧 Generating full outreach for {len(rows)} leads...")
    
    outreach_rows = []
    for i, row in enumerate(rows):
        email = row.get('Email', '')
        phone = row.get('Phone', '')
        
        if not email or email == 'None':
            continue
        
        first_name = extract_first_name(email)
        business = row.get('Business Name', '')
        city = row.get('City', '')
        pain_point = generate_pain_point(row)
        pain_short = generate_pain_point_short(row)
        rank = int(row.get('Rank', i+1) or i+1)
        
        subj1, subj2, subj3 = generate_subjects(row, rank)
        
        email_1 = EMAIL_1_TEMPLATE.format(
            subject_1=subj1,
            first_name=first_name,
            business_name=business,
            pain_point=pain_point
        )
        
        email_2 = EMAIL_2_TEMPLATE.format(
            subject_2=subj2,
            first_name=first_name,
            business_name=business
        )
        
        email_3 = EMAIL_3_TEMPLATE.format(
            subject_3=subj3,
            first_name=first_name,
            business_name=business
        )
        
        sms = SMS_TEMPLATE.format(
            first_name=first_name,
            business_name=business
        )
        
        call_script = CALL_SCRIPT.format(
            first_name=first_name,
            pain_point_short=pain_short
        )
        
        outreach_rows.append({
            'Rank': rank,
            'Business Name': business,
            'City': city,
            'Email': email,
            'Phone': phone,
            'Distress Score': row.get('Distress Score', ''),
            'Email 1 (Day 0)': email_1,
            'Email 2 (Day 3)': email_2,
            'Email 3 (Day 7)': email_3,
            'SMS Text': sms if phone else '(no phone)',
            'Call Script': call_script,
            'Why Now': row.get('Why Now', ''),
            'Talk Track': row.get('Talk Track', ''),
            'Email 1 Sent': '',
            'Email 2 Sent': '',
            'Email 3 Sent': '',
            'SMS Sent': '',
            'Called': '',
            'Response': '',
            'Status': 'Ready',
            'Notes': ''
        })
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        if outreach_rows:
            writer = csv.DictWriter(f, fieldnames=outreach_rows[0].keys())
            writer.writeheader()
            writer.writerows(outreach_rows)
    
    print(f"✅ Generated {len(outreach_rows)} complete outreach sequences")
    print(f"📄 Output: {output_path}")
    print(f"\nEach row includes:")
    print(f"  • Email 1 (initial)")
    print(f"  • Email 2 (3-day follow-up)")
    print(f"  • Email 3 (7-day last try)")
    print(f"  • SMS text message")
    print(f"  • Call script with objection handlers")

if __name__ == '__main__':
    main()
