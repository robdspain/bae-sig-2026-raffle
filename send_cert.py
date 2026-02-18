#!/usr/bin/env python3
"""Send gift certificate to email"""

import base64
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

client_id = os.environ.get('GMAIL_CLIENT_ID')
client_secret = os.environ.get('GMAIL_CLIENT_SECRET')
refresh_token = os.environ.get('GMAIL_REFRESH_TOKEN')

if not client_id or not client_secret or not refresh_token:
    print("Missing Gmail OAuth env vars (GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET / GMAIL_REFRESH_TOKEN)")
    sys.exit(1)

# Get token
result = subprocess.run([
    'curl', '-s', '--request', 'POST',
    '--url', 'https://oauth2.googleapis.com/token',
    '--data', f'client_id={client_id}',
    '--data', f'client_secret={client_secret}',
    '--data', f'refresh_token={refresh_token}',
    '--data', 'grant_type=refresh_token'
], capture_output=True, text=True)

TOKEN = json.loads(result.stdout)['access_token']

# Read HTML
with open(os.path.join(BASE_DIR, 'gift_certificate_preview.html'), 'r') as f:
    html_content = f.read()

# Create email
email_msg = f"""To: california.bae.sig@gmail.com
Subject: Gift Certificate - Dr. Peter Killeen (for Google Drive)
MIME-Version: 1.0
Content-Type: text/html; charset="UTF-8"

{html_content}

---
Save this HTML and upload to Google Drive.
"""

raw = base64.urlsafe_b64encode(email_msg.encode()).decode().rstrip('=')

# Send
send_result = subprocess.run([
    'curl', '-s', '--request', 'POST',
    '--url', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
    '--header', f'Authorization: Bearer {TOKEN}',
    '--header', 'Content-Type: application/json',
    '--data', json.dumps({"raw": raw})
], capture_output=True, text=True)

print("Result:", send_result.stdout if send_result.returncode == 0 else send_result.stderr)
msg_id = json.loads(send_result.stdout).get('id', 'Error')
print("Message ID:", msg_id)
