#!/usr/bin/env python3
"""Send outreach emails via Resend API."""
import re
import json
import time
import subprocess

RESEND_KEY = "re_PZireSU1_8ZzWLcnBek1m3HFzHv31UKnG"
FROM_EMAIL = "randy@roviq.ai"
EMAILS_FILE = "/data/workspace/projects/glass/outreach/emails-batch-1.md"
LOG_FILE = "/data/workspace/projects/glass/outreach/emails-sent-log.json"

def send_email(to_email, subject, html_body):
    """Send email via Resend API using curl."""
    payload = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }
    json_payload = json.dumps(payload)
    
    curl_cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.resend.com/emails",
        "-H", f"Authorization: Bearer {RESEND_KEY}",
        "-H", "Content-Type: application/json",
        "--data-binary", json_payload
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)
        return {"success": True, "response": json.loads(result.stdout)}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr or "Unknown error"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    # Read file
    with open(EMAILS_FILE, 'r') as f:
        content = f.read()
    
    # Parse all email blocks
    # Pattern matches: ## Email #N — Store Name (using em-dash or regular dash)
    pattern = r'## Email #(\d+)[—-] ([^\n]+)\n\n\*\*To:\*\* ([^\n]+)\n\*\*Store:\*\* ([^\n]+)\n\*\*Products tracked:\*\* ([^\n]+)\n\*\*Subject A:\*\* ([^\n]*)\n\*\*Subject B:\*\* ([^\n]*)\n\*\*---\*\*([^\n]+)\n\n([\s\S]+?)\n\*\*---\*\*'
    
    # Find all email blocks using --- delimiters
    email_blocks = []
    # Split by "## Email #" to get chunks
    chunks = content.split('## Email #')
    
    for chunk in chunks[1:]:  # Skip preamble
        # Extract email number and name from first line
        lines = chunk.strip().split('\n')
        if not lines:
            continue
            
        header = lines[0]
        if '⛔ DO NOT SEND' in chunk:
            print(f"Skipping email marked DO NOT SEND")
            continue
        
        # Extract email number from start
        match = re.match(r'(\d+)', header)
        if not match:
            continue
        email_num = int(match.group(1))
        
        # Find To: line
        to_match = re.search(r'To:\*\* ([^\n]+)', chunk)
        if not to_match:
            continue
        to_email = to_match.group(1).strip()
        
        # Find Subject A
        subj_match = re.search(r'Subject A:\*\* ([^\n]+)', chunk)
        if subj_match:
            subject = subj_match.group(1).strip()
        else:
            subject = "Your GLASS Report Card"
        
        # Find body between first --- and next ---
        body_match = re.search(r'---\n\n([\s\S]+?)\n\n---', chunk)
        if body_match:
            body = body_match.group(1).strip()
        else:
            continue
        
        email_blocks.append({
            "num": email_num,
            "to": to_email,
            "subject": subject,
            "body": body
        })
    
    print(f"Found {len(email_blocks)} emails to send")
    
    # Send emails
    results = []
    sent = 0
    failed = 0
    
    for email in email_blocks:
        print(f"\nSending #{email['num']} to {email['to']}...")
        
        # Format HTML body
        html_body = f"""<div style="font-family: Arial, sans-serif; max-width: 600px;">
{email['body'].replace(chr(10), '<br>')}<br><br>
— Randy<br>
Roviq | GLASS<br>
randy@roviq.ai<br><br>
<small>You're receiving this because your dispensary is tracked in the GLASS database. Reply UNSUBSCRIBE to opt out.</small>
</div>"""
        
        result = send_email(email['to'], email['subject'], html_body)
        results.append({
            "email_num": email['num'],
            "to": email['to'],
            "subject": email['subject'],
            "status": "sent" if result['success'] else "failed",
            "details": result.get('response') or result.get('error')
        })
        
        if result['success']:
            sent += 1
            print(f"  ✓ Sent")
        else:
            failed += 1
            print(f"  ✗ Failed: {result.get('error', 'Unknown')}")
        
        time.sleep(2)  # Rate limit
    
    # Save log
    with open(LOG_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n=== SUMMARY ===")
    print(f"Sent: {sent}")
    print(f"Failed: {failed}")
    print(f"Total: {len(email_blocks)}")
    print(f"Log saved to: {LOG_FILE}")

if __name__ == "__main__":
    main()
