
import re
import json
import time
import subprocess

RESEND_API_KEY = "re_PZireSU1_8ZzWLcnBek1m3HFzHv31UKnG"
FROM_EMAIL = "randy@roviq.ai"
EMAILS_FILE_PATH = "/data/workspace/projects/glass/outreach/emails-batch-1.md"
LOG_FILE_PATH = "/data/workspace/projects/glass/outreach/emails-sent-log.json"

def is_valid_email(email):
    # A basic regex for email validation
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def parse_emails_file(file_path):
    with open(file_path, 'r') as f:
        raw_content = f.read()

    emails_data = []
    
    # Trying a more robust header pattern with a non-greedy match for the store name
    # and using re.M for multiline search. Making the dash matching more flexible.
    header_pattern = r'^## Email #(\\d+)[\\s—]+.*?$'
    headers = list(re.finditer(header_pattern, raw_content, re.MULTILINE))
    
    if not headers:
        print(f"No email headers found with the regex: {header_pattern}")
        print("First 1000 chars of content for inspection:\n" + repr(raw_content[:1000]))
        return []

    # Extract blocks based on header positions
    blocks = []
    for i in range(len(headers)):
        start_index = headers[i].start()
        end_index = headers[i+1].start() if i + 1 < len(headers) else len(raw_content)
        blocks.append(raw_content[start_index:end_index])
    
    # Debug: print the number of blocks found and the first block content
    print(f"Successfully split content into {len(blocks)} blocks.")
    if blocks: 
        print("First block content preview (first 500 chars):\n" + blocks[0][:500])

    for block_content in blocks:
        # Extract email number from the block_content, as the previous finditer only gave start/end indices
        email_number_match = re.search(r'## Email #(\\d+)', block_content)
        current_email_number = int(email_number_match.group(1)) if email_number_match else 0
        
        # Debug print for current email being processed
        print(f"--- Processing Email Block for #{current_email_number} ---")
        
        if "⛔ DO NOT SEND" in block_content:
            print(f"Skipping email #{current_email_number} as marked DO NOT SEND.")
            continue

        to_match = re.search(r'To: (.+)', block_content)
        store_match = re.search(r'Store: (.+)', block_content)
        subject_a_match = re.search(r'Subject A: (.+)', block_content)
        subject_b_match = re.search(r'Subject B: (.+)', block_content)
        body_match = re.search(r'---\\n\\n(.*?)\\n\\n---', block_content, re.DOTALL)

        recipient_email = to_match.group(1).strip() if to_match else None
        store_name = store_match.group(1).strip() if store_match else "N/A"
        subject = subject_a_match.group(1).strip() if subject_a_match else (subject_b_match.group(1).strip() if subject_b_match else "No Subject")
        raw_body_text = body_match.group(1).strip() if body_match else ""
        
        if not recipient_email or not is_valid_email(recipient_email):
            print(f"Skipping email #{current_email_number} due to invalid or missing recipient email: {recipient_email}")
            continue

        formatted_body_text = raw_body_text.replace('\n', '<br>')

        full_body_html = f"""
<html>
<body>
    <p>{formatted_body_text}</p>
    <p>You're receiving this because your dispensary is tracked in the GLASS database. Unsubscribe: reply UNSUBSCRIBE</p>
    <p>— Randy Torres<br>Roviq | GLASS<br>randy@roviq.ai</p>
</body>
</html>
"""
        emails_data.append({
            "email_number": current_email_number,
            "to": recipient_email,
            "store": store_name,
            "subject": subject,
            "body_html": full_body_html
        })
    return emails_data

def send_email_via_curl(to_email, subject, html_body):
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }

    json_payload = json.dumps(payload)

    curl_command = [
        "curl",
        "-X", "POST",
        url,
        "-H", f"Authorization: Bearer {RESEND_API_KEY}",
        "-H", "Content-Type: application/json",
        "--data-binary", json_payload
    ]
    
    try:
        process = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        return {"status": "success", "response": process.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "failed", "error": e.stderr.strip(), "response": e.stdout.strip()}
    except Exception as e:
        return {"status": "failed", "error": str(e), "response": None}

def main():
    parsed_emails = parse_emails_file(EMAILS_FILE_PATH)
    total_emails_to_send = len(parsed_emails)
    sent_count = 0
    failed_count = 0
    results_log = []

    print(f"Attempting to send {total_emails_to_send} emails...")

    for email in parsed_emails:
        print(f"Sending email #{email['email_number']} to {email['to']} with subject: {email['subject']}...")
        result = send_email_via_curl(email['to'], email['subject'], email['body_html'])
        results_log.append({
            "email_number": email['email_number'],
            "to": email['to'],
            "subject": email['subject'],
            "status": result['status'],
            "details": result.get('response') or result.get('error')
        })

        if result['status'] == "success":
            sent_count += 1
            print(f"Successfully sent email #{email['email_number']}.")
        else:
            failed_count += 1
            print(f"Failed to send email #{email['email_number']}: {result.get('error')}")

        time.sleep(2) # Rate limit: 1 email per 2 seconds

    with open(LOG_FILE_PATH, 'w') as f:
        json.dump(results_log, f, indent=4)

    summary = f"Sent {sent_count}/{total_emails_to_send} emails, {failed_count} failed, log saved to {LOG_FILE_PATH}"
    print(summary)
    print(f"SUBAGENT_TASK_SUMMARY: {summary}")

if __name__ == "__main__":
    main()
