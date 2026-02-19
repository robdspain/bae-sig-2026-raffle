#!/usr/bin/env python3
"""
BAE SIG Book Raffle Email Campaign
Uses Resend API for reliable email delivery.
"""

import os
import sys
import json
import csv
import subprocess
from datetime import datetime
from typing import Optional

# Configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'onboarding@resend.dev')  # Update with your verified domain
REPLY_TO = 'california.bae.sig@gmail.com'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKER_FILE = os.path.join(BASE_DIR, 'campaign_tracker.csv')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'email_templates')

# Ensure directories exist
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Email Templates
TEMPLATES = {
    'donation_request': {
        'subject': 'Book Donation Request - CalABA 2026 BAE SIG Raffle',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .content { background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }
        .footer { background: #374151; color: white; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; }
        .button { display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
        .sig-logos { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 CalABA 2026 Book Raffle</h1>
            <p>Bay Area Educators Special Interest Group</p>
        </div>
        <div class="content">
            <p>Dear {name},</p>
            
            <p>We hope this message finds you well! The <strong>Bay Area Educators Special Interest Group (BAE SIG)</strong> 
            is hosting our annual <strong>Book Raffle</strong> at CalABA 2026 in Long Beach, and we'd be honored if you 
            would consider donating a signed copy of your book.</p>
            
            <p>Your work has made a significant impact on our field, and having your book in our raffle would be 
            a wonderful opportunity for attendees to take home something meaningful.</p>
            
            <h3>📍 Drop-off Details</h3>
            <ul>
                <li><strong>Where:</strong> CalABA Conference - BAE SIG Booth or Registration</li>
                <li><strong>When:</strong> Before the Friday Night SIG Reception</li>
                <li><strong>Alternative:</strong> We can arrange shipping if needed</li>
            </ul>
            
            <p>All proceeds support educator resources and professional development in the Bay Area.</p>
            
            <p>Would you be willing to donate a signed copy? Simply reply to this email to let us know!</p>
            
            <p>Thank you for considering our request. We truly appreciate your contribution to our community.</p>
            
            <p>Warm regards,<br>
            <strong>BAE SIG Board</strong><br>
            Bay Area Educators Special Interest Group</p>
        </div>
        <div class="footer">
            <p>CalABA 2026 | Long Beach, CA | March 2026</p>
            <p>🎲 <a href="https://calaba-sig-raffle.vercel.app" style="color: #93c5fd;">View Raffle Prizes</a></p>
        </div>
    </div>
</body>
</html>
''',
    },
    'thank_you': {
        'subject': 'Thank You for Your Book Donation! - BAE SIG',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #059669; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .content { background: #f0fdf4; padding: 20px; border: 1px solid #bbf7d0; }
        .footer { background: #374151; color: white; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; }
        .highlight { background: #dcfce7; padding: 15px; border-radius: 6px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Thank You!</h1>
            <p>Your generosity makes a difference</p>
        </div>
        <div class="content">
            <p>Dear {name},</p>
            
            <p>Thank you so much for agreeing to donate <strong>"{book_title}"</strong> to the BAE SIG Book Raffle!</p>
            
            <div class="highlight">
                <h3>📍 Drop-off Information</h3>
                <p><strong>Location:</strong> CalABA Conference, Long Beach<br>
                <strong>Deadline:</strong> Friday evening before the SIG Reception<br>
                <strong>Contact:</strong> Look for the BAE SIG booth or any board member</p>
            </div>
            
            <p>Your contribution will help support educator resources and professional development 
            for behavior analysts throughout the Bay Area.</p>
            
            <p>We'll be sure to showcase your book prominently at the raffle!</p>
            
            <p>See you at CalABA 2026! 🎊</p>
            
            <p>With gratitude,<br>
            <strong>BAE SIG Board</strong></p>
        </div>
        <div class="footer">
            <p>🎲 <a href="https://calaba-sig-raffle.vercel.app" style="color: #93c5fd;">View All Raffle Prizes</a></p>
        </div>
    </div>
</body>
</html>
''',
    },
    'raffle_promo': {
        'subject': '🎲 Win Amazing Books at CalABA 2026 - BAE SIG Raffle!',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #7c3aed, #2563eb); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }
        .content { background: #faf5ff; padding: 20px; border: 1px solid #e9d5ff; }
        .footer { background: #374151; color: white; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; }
        .prize-box { background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #7c3aed; }
        .button { display: inline-block; background: #7c3aed; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎲 BAE SIG Book Raffle</h1>
            <p>CalABA 2026 | Long Beach, CA</p>
        </div>
        <div class="content">
            <p>Hi {name}!</p>
            
            <p>The Bay Area Educators SIG is hosting our annual <strong>Book Raffle</strong> at CalABA 2026, 
            and we have some incredible prizes this year!</p>
            
            <h3>📚 Featured Prizes Include:</h3>
            <div class="prize-box">
                <strong>Dr. Peter Killeen</strong> - "Mechanics of the Mind" (Signed!)
            </div>
            <div class="prize-box">
                <strong>Multiple Author Donations</strong> - OBM, School-Based ABA, and more
            </div>
            <div class="prize-box">
                <strong>CEU Certificates</strong> - Free CEU opportunities
            </div>
            
            <p style="text-align: center; margin: 25px 0;">
                <a href="https://calaba-sig-raffle.vercel.app" class="button">🎟️ Get Your Tickets</a>
            </p>
            
            <p>All proceeds support educator resources and professional development in the Bay Area!</p>
            
            <p>See you at CalABA! 🎊</p>
            
            <p>— BAE SIG Board</p>
        </div>
        <div class="footer">
            <p>Bay Area Educators Special Interest Group</p>
        </div>
    </div>
</body>
</html>
''',
    }
}


def send_email(to: str, template: str, variables: dict, dry_run: bool = False) -> bool:
    """Send email using Resend API."""
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY not set. Export it first:")
        print("   export RESEND_API_KEY='re_xxxxxxxxxxxx'")
        return False
    
    if template not in TEMPLATES:
        print(f"❌ Unknown template: {template}")
        print(f"   Available: {', '.join(TEMPLATES.keys())}")
        return False
    
    tmpl = TEMPLATES[template]
    subject = tmpl['subject']
    html = tmpl['html'].format(**variables)
    
    payload = {
        'from': FROM_EMAIL,
        'to': [to],
        'reply_to': REPLY_TO,
        'subject': subject,
        'html': html
    }
    
    if dry_run:
        print(f"📧 [DRY RUN] Would send to: {to}")
        print(f"   Subject: {subject}")
        print(f"   Template: {template}")
        return True
    
    cmd = [
        'curl', '-s', '-X', 'POST',
        'https://api.resend.com/emails',
        '-H', f'Authorization: Bearer {RESEND_API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"✅ Sent to {to} (ID: {response['id']})")
            log_send(to, template, response['id'])
            return True
        else:
            print(f"❌ Failed: {response}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Response: {result.stdout}")
        return False


def log_send(to: str, template: str, email_id: str):
    """Log sent email to tracker."""
    file_exists = os.path.exists(TRACKER_FILE)
    
    with open(TRACKER_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'email', 'template', 'resend_id', 'status'])
        writer.writerow([datetime.now().isoformat(), to, template, email_id, 'sent'])


def send_batch(csv_file: str, template: str, dry_run: bool = False):
    """Send emails to list from CSV file."""
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"📬 Sending {len(rows)} emails using template: {template}")
    print(f"   {'[DRY RUN]' if dry_run else '[LIVE]'}")
    print()
    
    success = 0
    for row in rows:
        email = row.get('email', row.get('Email', ''))
        name = row.get('name', row.get('Name', row.get('first_name', 'there')))
        book_title = row.get('book_title', row.get('book', 'your book'))
        
        if not email:
            print(f"⚠️  Skipping row (no email): {row}")
            continue
        
        variables = {
            'name': name,
            'book_title': book_title,
        }
        
        if send_email(email, template, variables, dry_run):
            success += 1
    
    print()
    print(f"📊 Results: {success}/{len(rows)} sent successfully")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='BAE SIG Email Campaign')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Single email
    single = subparsers.add_parser('send', help='Send single email')
    single.add_argument('--to', required=True, help='Recipient email')
    single.add_argument('--template', required=True, choices=TEMPLATES.keys())
    single.add_argument('--name', default='there', help='Recipient name')
    single.add_argument('--book', default='your book', help='Book title')
    single.add_argument('--dry-run', action='store_true')
    
    # Batch send
    batch = subparsers.add_parser('batch', help='Send to CSV list')
    batch.add_argument('--csv', required=True, help='CSV file with name,email columns')
    batch.add_argument('--template', required=True, choices=TEMPLATES.keys())
    batch.add_argument('--dry-run', action='store_true')
    
    # List templates
    subparsers.add_parser('templates', help='List available templates')
    
    # Test
    test = subparsers.add_parser('test', help='Send test email to yourself')
    test.add_argument('--to', required=True, help='Your email for testing')
    
    args = parser.parse_args()
    
    if args.command == 'templates':
        print("📧 Available Templates:")
        for name, tmpl in TEMPLATES.items():
            print(f"  • {name}: {tmpl['subject']}")
    
    elif args.command == 'send':
        send_email(args.to, args.template, {
            'name': args.name,
            'book_title': args.book
        }, args.dry_run)
    
    elif args.command == 'batch':
        send_batch(args.csv, args.template, args.dry_run)
    
    elif args.command == 'test':
        print("🧪 Sending test emails...")
        for template in TEMPLATES.keys():
            send_email(args.to, template, {
                'name': 'Test User',
                'book_title': 'The Test Book'
            })
            print()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
