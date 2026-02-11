import re
import random

def parse_prospects(content):
    cultivators = []
    micros = []
    
    sections = content.split("## ")
    
    cultivator_section = ""
    micro_section = ""
    
    for section in sections:
        if section.startswith("Prime Cultivator Prospects"):
            cultivator_section = section
        elif section.startswith("Microbusiness Prospects"):
            micro_section = section

    # Parse Cultivators
    cult_lines = cultivator_section.strip().split('\n')
    for line in cult_lines:
        if line.startswith('| **'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                company = parts[1].replace('**', '')
                tier_raw = parts[3]
                location = parts[4]
                contact_raw = parts[5]
                
                # Extract Tier Number
                tier_match = re.search(r'Tier (\d+)', tier_raw)
                tier_num = int(tier_match.group(1)) if tier_match else 0
                
                # Extract Name
                name = extract_name(contact_raw, company)
                
                cultivators.append({
                    "company": company,
                    "tier": tier_num,
                    "tier_raw": tier_raw,
                    "location": location,
                    "contact_name": name
                })

    # Parse Micros
    micro_lines = micro_section.strip().split('\n')
    for line in micro_lines:
        if line.startswith('| **'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:
                company = parts[1].replace('**', '')
                location = parts[3]
                contact_raw = parts[4]
                
                name = extract_name(contact_raw, company)
                
                micros.append({
                    "company": company,
                    "location": location,
                    "contact_name": name
                })
                
    return cultivators, micros

def extract_name(contact_raw, company_name):
    # Get email
    email_part = contact_raw.split(' / ')[0].strip()
    if '@' not in email_part:
        return company_name
        
    local_part = email_part.split('@')[0]
    
    # Remove numbers
    local_part_clean = re.sub(r'[0-9]+', '', local_part)
    
    # Check for dot or underscore
    if '.' in local_part_clean:
        candidate = local_part_clean.split('.')[0]
    elif '_' in local_part_clean:
        candidate = local_part_clean.split('_')[0]
    else:
        # No separator
        if len(local_part_clean) > 12: # Threshold for "probably not a first name"
             return company_name
        candidate = local_part_clean
    
    # Filter generics
    generics = ['info', 'contact', 'admin', 'hello', 'support', 'sales', 'grow', 'compliance', 
                'office', 'hr', 'team', 'manager', 'owner', 'inquiries', 'questions', 'mail', 
                'webmaster', 'jobs', 'careers', 'billing', 'accounts', 'press', 'media', 
                'community', 'general', 'ccc', 'application', 'licensing']
                
    if candidate.lower() in generics or len(candidate) < 2:
        return company_name
    
    # Filter by common company suffixes if name is "longish"
    suffixes = ['ma', 'farm', 'farms', 'co', 'inc', 'llc', 'cultivation', 'grow', 'growers', 
                'cannabis', 'green', 'med', 'wellness', 'solutions', 'mechanical', 'group', 
                'holdings', 'gardens', 'leaves', 'botanicals', 'roots', 'harvest']
                
    if len(candidate) > 4:
        for s in suffixes:
            if candidate.lower().endswith(s):
                return company_name
        
    # Check if candidate is close to company name
    clean_company = re.sub(r'[^a-zA-Z]', '', company_name.lower())
    if candidate.lower() in clean_company:
        return company_name
        
    return candidate.capitalize()

def get_subject_line(location):
    options = [
        "Quick question about your flower",
        f"Your {location} grow",
        "Connecting MA cultivators"
    ]
    return random.choice(options)

def generate_email(prospect, type="cultivator"):
    location = prospect['location']
    contact_name = prospect['contact_name']
    subject = get_subject_line(location)
    
    # Determine Tier Details and Phrase
    if type == "micro":
        size_detail = f"a microbusiness in {location}"
        tier_phrase = "No equipment needed on your end—especially good fit for micros who want to maximize what they grow."
    else:
        tier = prospect['tier']
        tier_raw = prospect['tier_raw']
        
        # Clean up tier raw for "Saw you're running..."
        sqft_part = tier_raw.split(': ')[1] if ':' in tier_raw else tier_raw
        
        # Make it flow better: "a [sqft] operation in [location]"
        size_detail = f"a {sqft_part} operation in {location}"
        
        if tier >= 4: # Large (Tier 4-11, 20K+)
            tier_phrase = "They can handle serious volume runs."
        elif tier >= 2: # Mid (Tier 2-3, 5K-20K)
            tier_phrase = "Low MOQs, no need to commit to huge runs."
        else: # Small (Tier 1, <5K)
            tier_phrase = "No equipment needed on your end."

    body = f"""Subject: {subject}

Hey {contact_name},

I work with Advanced Cultivators out of Lowell. They've got manufacturing capacity and are looking for quality flower partners to run prerolls.

Saw you're running {size_detail}. Figured it might be worth connecting you two. {tier_phrase}

Want me to make an intro?

Randy Torres
roviqai.xyz"""

    return body

def main():
    file_path = '/data/workspace/clients/ac/toll-processing/prospects.md'
    with open(file_path, 'r') as f:
        content = f.read()

    cultivators, micros = parse_prospects(content)
    
    output = ""
    
    # Group by Tier Categories for Output
    
    # Large (Tier 4+)
    large_cults = [c for c in cultivators if c['tier'] >= 4]
    if large_cults:
        output += "## Large Operations (Tier 4+, 20K+ sqft)\n\n"
        for c in large_cults:
            output += f"### {c['company']}\n"
            output += generate_email(c, "cultivator") + "\n\n---\n\n"

    # Mid (Tier 2-3)
    mid_cults = [c for c in cultivators if c['tier'] in [2, 3]]
    if mid_cults:
        output += "## Mid Operations (Tier 2-3, 5K-20K sqft)\n\n"
        for c in mid_cults:
            output += f"### {c['company']}\n"
            output += generate_email(c, "cultivator") + "\n\n---\n\n"
            
    # Small (Tier 1)
    small_cults = [c for c in cultivators if c['tier'] <= 1]
    if small_cults:
        output += "## Small Operations (Tier 1, <5K sqft)\n\n"
        for c in small_cults:
            output += f"### {c['company']}\n"
            output += generate_email(c, "cultivator") + "\n\n---\n\n"

    # Micros
    if micros:
        output += "## Microbusinesses\n\n"
        for m in micros:
            output += f"### {m['company']}\n"
            output += generate_email(m, "micro") + "\n\n---\n\n"
            
    with open('/data/workspace/clients/ac/toll-processing/outreach-emails-v2.md', 'w') as f:
        f.write(output)

if __name__ == "__main__":
    main()
