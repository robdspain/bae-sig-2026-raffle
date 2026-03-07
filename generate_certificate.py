#!/usr/bin/env python3
"""
BAE SIG Raffle Certificate Generator + Emailer
Usage: python3 generate_certificate.py

Prompts for:
  - Winner name + email
  - Prize name
  - Donor name + email

Generates a personalized certificate HTML, then emails it to:
  - The winner
  - The donor
  - california.bae.sig@gmail.com (BCC archive)
"""

import base64
import json
import os
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, 'certificate_template.html')

# ── Gmail OAuth ──────────────────────────────────────────────────────────────
client_id     = os.environ.get('GMAIL_CLIENT_ID')
client_secret = os.environ.get('GMAIL_CLIENT_SECRET')
refresh_token = os.environ.get('GMAIL_REFRESH_TOKEN')

def get_access_token():
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Missing Gmail OAuth env vars: GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET / GMAIL_REFRESH_TOKEN")
        sys.exit(1)
    result = subprocess.run([
        'curl', '-s', '--request', 'POST',
        '--url', 'https://oauth2.googleapis.com/token',
        '--data', f'client_id={client_id}',
        '--data', f'client_secret={client_secret}',
        '--data', f'refresh_token={refresh_token}',
        '--data', 'grant_type=refresh_token'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)['access_token']

# ── Certificate generator ────────────────────────────────────────────────────
def generate_cert(winner_name, prize_name, donor_name):
    with open(TEMPLATE_PATH, 'r') as f:
        html = f.read()
    date_str = datetime.now().strftime('%B %d, %Y')
    html = html.replace('{{WINNER_NAME}}', winner_name)
    html = html.replace('{{PRIZE_NAME}}', prize_name)
    html = html.replace('{{DONOR_NAME}}', donor_name)
    html = html.replace('{{DATE}}', date_str)
    return html

# ── Email sender ─────────────────────────────────────────────────────────────
def send_email(token, to_email, to_name, subject, html_body, cc=None):
    headers = f"To: {to_name} <{to_email}>\n"
    headers += f"Subject: {subject}\n"
    if cc:
        headers += f"Cc: {cc}\n"
    headers += "MIME-Version: 1.0\nContent-Type: text/html; charset=\"UTF-8\"\n\n"

    raw_msg = headers + html_body
    raw_b64 = base64.urlsafe_b64encode(raw_msg.encode()).decode().rstrip('=')

    result = subprocess.run([
        'curl', '-s', '--request', 'POST',
        '--url', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
        '--header', f'Authorization: Bearer {token}',
        '--header', 'Content-Type: application/json',
        '--data', json.dumps({'raw': raw_b64})
    ], capture_output=True, text=True)

    resp = json.loads(result.stdout)
    if 'id' in resp:
        print(f"  ✅ Sent to {to_email} (id: {resp['id']})")
    else:
        print(f"  ❌ Failed to send to {to_email}: {result.stdout}")

# ── Wrapper email bodies ─────────────────────────────────────────────────────
def winner_email(cert_html, winner_name, prize_name, donor_name):
    return f"""
<div style="font-family:Inter,sans-serif;max-width:600px;margin:0 auto;color:#1e293b;">
  <div style="background:#1e3a5f;padding:1.5rem 2rem;border-bottom:4px solid #c9a84c;">
    <h1 style="color:#fff;margin:0;font-size:1.25rem;">BAE SIG · CalABA 2026</h1>
  </div>
  <div style="padding:2rem;">
    <p>Congratulations, <strong>{winner_name}</strong>! 🎉</p>
    <p style="margin-top:1rem;">
      You won <strong>{prize_name}</strong>, generously donated by <strong>{donor_name}</strong>,
      in the BAE SIG Raffle at the CalABA 2026 Conference.
    </p>
    <p style="margin-top:1rem;">Your official certificate is below. We'll be in touch about prize pickup/delivery.</p>
    <p style="margin-top:1rem;color:#64748b;font-size:0.9rem;">
      Thank you for supporting behavior analysis in education!<br>
      — The BAE SIG Board
    </p>
  </div>
  <hr style="border:none;border-top:1px solid #e2e8f0;margin:0 2rem;">
  <div style="padding:1rem 2rem 2rem;">
    <p style="font-size:0.75rem;color:#94a3b8;margin-bottom:1rem;">Your certificate:</p>
    {cert_html}
  </div>
</div>
"""

def donor_email(cert_html, winner_name, prize_name, donor_name):
    return f"""
<div style="font-family:Inter,sans-serif;max-width:600px;margin:0 auto;color:#1e293b;">
  <div style="background:#1e3a5f;padding:1.5rem 2rem;border-bottom:4px solid #c9a84c;">
    <h1 style="color:#fff;margin:0;font-size:1.25rem;">BAE SIG · CalABA 2026</h1>
  </div>
  <div style="padding:2rem;">
    <p>Dear <strong>{donor_name}</strong>,</p>
    <p style="margin-top:1rem;">
      We wanted to let you know that your generous donation of <strong>{prize_name}</strong>
      was awarded to <strong>{winner_name}</strong> in tonight's BAE SIG Raffle!
    </p>
    <p style="margin-top:1rem;">
      Your contribution makes a real difference in supporting behavior analysis in education.
      Thank you so much for being part of this.
    </p>
    <p style="margin-top:1rem;color:#64748b;font-size:0.9rem;">
      With gratitude,<br>
      — The BAE SIG Board
    </p>
  </div>
  <hr style="border:none;border-top:1px solid #e2e8f0;margin:0 2rem;">
  <div style="padding:1rem 2rem 2rem;">
    <p style="font-size:0.75rem;color:#94a3b8;margin-bottom:1rem;">Winner's certificate (for your records):</p>
    {cert_html}
  </div>
</div>
"""

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n🏆 BAE SIG Certificate Generator\n" + "─"*40)

    winner_name  = input("Winner name:   ").strip()
    winner_email_ = input("Winner email:  ").strip()
    prize_name   = input("Prize name:    ").strip()
    donor_name   = input("Donor name:    ").strip()
    donor_email_ = input("Donor email:   ").strip()

    print("\nGenerating certificate...")
    cert_html = generate_cert(winner_name, prize_name, donor_name)

    # Save locally too
    out_path = os.path.join(BASE_DIR, f'cert_{winner_name.replace(" ","_")}.html')
    with open(out_path, 'w') as f:
        f.write(cert_html)
    print(f"  📄 Saved: {out_path}")

    print("\nFetching Gmail token...")
    token = get_access_token()

    subject = f"BAE SIG Raffle — Your Prize Certificate | {prize_name}"

    print(f"\nSending to winner ({winner_email_})...")
    send_email(token, winner_email_, winner_name, subject,
               winner_email(cert_html, winner_name, prize_name, donor_name),
               cc='california.bae.sig@gmail.com')

    print(f"Sending to donor ({donor_email_})...")
    send_email(token, donor_email_, donor_name,
               f"Your donation was awarded! | BAE SIG Raffle",
               donor_email(cert_html, winner_name, prize_name, donor_name))

    print("\n✅ Done! Both emails sent.")

if __name__ == '__main__':
    main()
