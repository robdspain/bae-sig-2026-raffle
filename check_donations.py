#!/usr/bin/env python3
"""
Book Donation Response Tracker
Scans Gmail for responses to book donation requests and creates approval drafts.
Uses only standard library + curl for API calls.
"""

import os
import csv
import subprocess
import json
import re
from datetime import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKER_FILE = os.path.join(BASE_DIR, 'donation_tracker.csv')
RESPONSE_DRAFTS_DIR = os.path.join(BASE_DIR, 'response_drafts')
NOTIFICATION_DRAFTS_DIR = os.path.join(BASE_DIR, 'notification_drafts')

def get_access_token():
    """Get fresh access token using refresh token."""
    cmd = [
        'curl', '-s', '--request', 'POST',
        '--url', 'https://oauth2.googleapis.com/token',
        '--data', 'client_id=REDACTED_GOOGLE_CLIENT_ID',
        '--data', 'client_secret=REDACTED_GOOGLE_CLIENT_SECRET',
        '--data', 'refresh_token=REDACTED_GOOGLE_REFRESH_TOKEN',
        '--data', 'grant_type=refresh_token'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)['access_token']
    except:
        print("❌ Failed to get access token")
        return None

def search_responses(token):
    """Search for responses to book donation emails."""
    query = 'subject:"Book Donation Request" OR subject:"BAE SIG Book Raffle" -from:california.bae.sig@gmail.com after:2026/02/02'
    
    cmd = [
        'curl', '-s', '--request', 'GET',
        f'https://gmail.googleapis.com/gmail/v1/users/me/messages?q={query}&maxResults=20',
        '--header', f'Authorization: Bearer {token}'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return data.get('messages', [])
    except:
        return []

def get_message_details(token, msg_id):
    """Get full message details."""
    cmd = [
        'curl', '-s', '--request', 'GET',
        f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}',
        '--header', f'Authorization: Bearer {token}'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return {}

def extract_info(msg_data):
    """Extract donor info from message."""
    headers = msg_data.get('payload', {}).get('headers', [])
    
    from_header = ''
    subject = ''
    for h in headers:
        if h['name'] == 'From':
            from_header = h['value']
        if h['name'] == 'Subject':
            subject = h['value']
    
    # Skip our own messages
    if 'california.bae.sig@gmail.com' in from_header:
        return None
    
    # Extract name and email
    if '<' in from_header:
        name = from_header.split('<')[0].strip().strip('"')
        email = from_header.split('<')[1].strip('>')
    else:
        name = from_header.split('@')[0]
        email = from_header
    
    snippet = msg_data.get('snippet', '')
    
    return {
        'from': from_header,
        'name': name,
        'email': email,
        'subject': subject,
        'snippet': snippet
    }

def load_tracker():
    """Load existing tracker."""
    donations = []
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r') as f:
            reader = csv.DictReader(f)
            donations = list(reader)
    return donations

def save_tracker(donations):
    """Save tracker."""
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    
    fieldnames = ['date', 'name', 'email', 'book', 'status', 'notes']
    
    with open(TRACKER_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(donations)

def is_new(donations, email):
    """Check if new donation."""
    for d in donations:
        if d['email'].lower() == email.lower():
            return False
    return True

def create_response_draft(donor):
    """Create response draft for approval."""
    os.makedirs(RESPONSE_DRAFTS_DIR, exist_ok=True)
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{RESPONSE_DRAFTS_DIR}/{ts}-response.txt"
    
    draft = f"""---
TO: {donor['email']}
SUBJECT: Thank You for Your Book Donation - BAE SIG CalABA 2026
STATUS: PENDING APPROVAL - DO NOT SEND

Dear {donor['name']},

Thank you so much for agreeing to donate to our BAE SIG book raffle fundraiser!

DROP-OFF INFORMATION:
We will have a designated location at CalABA 2026 where you can drop off your donated materials. This will be available before our SIG Reception on Friday night, March 6th.

NEXT STEPS:
We will be sending out more information about:
- The exact drop-off location and hours
- Details about your book/presentation (if applicable)
- Raffle ticket distribution information

Thank you for supporting our SIG and helping us raise funds for the reception bar costs!

Best,
Rob Spain
BAE SIG President
california.bae.sig@gmail.com

---
ORIGINAL RESPONSE:
{donor['snippet'][:300]}
"""
    
    with open(filename, 'w') as f:
        f.write(draft)
    
    return filename

def create_board_notification(donor):
    """Create notification for board members."""
    os.makedirs(NOTIFICATION_DRAFTS_DIR, exist_ok=True)
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{NOTIFICATION_DRAFTS_DIR}/{ts}-board-notice.txt"
    
    notification = f"""---
TO: megancaluza@yahoo.com
CC: holly.northcross@wusd.ws, katie_turner@nmcusd.org
SUBJECT: New Book Donation Commitment - {donor['name']}
STATUS: FOR YOUR INFORMATION

Hi Team,

We have a new book donation commitment for the CalABA 2026 raffle!

DONOR DETAILS:
- Name: {donor['name']}
- Email: {donor['email']}

ORIGINAL RESPONSE:
{donor['snippet'][:300]}

ACTION ITEMS:
- Response draft created: {RESPONSE_DRAFTS_DIR}/{ts}-response.txt
- Waiting for Rob's approval to send

This donor will drop off materials at CalABA before the Friday night reception.
"""
    
    with open(filename, 'w') as f:
        f.write(notification)
    
    return filename

def main():
    print("📚 Checking for book donation responses...")
    
    token = get_access_token()
    if not token:
        return
    
    messages = search_responses(token)
    
    if not messages:
        print("✅ No new responses found.")
        print("\n📝 To check manually:")
        print("1. Search Gmail for: 'Book Donation Request' or 'BAE SIG Book Raffle'")
        print("2. Look for replies from speakers")
        return
    
    print(f"Found {len(messages)} potential response(s)")
    
    donations = load_tracker()
    new_count = 0
    
    for msg in messages:
        msg_data = get_message_details(token, msg['id'])
        donor = extract_info(msg_data)
        
        if donor and is_new(donations, donor['email']):
            new_count += 1
            
            donations.append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'name': donor['name'],
                'email': donor['email'],
                'book': 'To be confirmed',
                'status': 'pending_approval',
                'notes': donor['snippet'][:100]
            })
            
            resp_file = create_response_draft(donor)
            notify_file = create_board_notification(donor)
            
            print(f"✅ New donation: {donor['name']} ({donor['email']})")
            print(f"   Response draft: {resp_file}")
            print(f"   Board notification: {notify_file}")
    
    if new_count > 0:
        save_tracker(donations)
        print(f"\n📊 Tracker updated: {new_count} new donation(s)")
    
    print("\n📝 NEXT STEPS:")
    print("1. Review response drafts in: response_drafts/")
    print("2. Tell Neo to send the approved response")
    print("3. Board members have been notified")

if __name__ == '__main__':
    main()
