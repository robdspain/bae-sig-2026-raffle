#!/usr/bin/env python3
"""Send gift certificate to email"""

import base64
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Get token
result = subprocess.run([
    'curl', '-s', '--request', 'POST',
    '--url', 'https://oauth2.googleapis.com/token',
    '--data', 'client_id=REDACTED_GOOGLE_CLIENT_ID',
    '--data', 'client_secret=REDACTED_GOOGLE_CLIENT_SECRET',
    '--data', 'refresh_token=REDACTED_GOOGLE_REFRESH_TOKEN',
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
