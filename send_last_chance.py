#!/usr/bin/env python3
"""Last-chance raffle email blast via Resend."""

import csv, os, time, json
import urllib.request, urllib.error

RESEND_API_KEY = 're_9jS7EXqT_J4sbfJz6aCjBSNRQ2yDijLcu'
FROM_EMAIL = 'BAE SIG <noreply@updates.behaviorschool.com>'
REPLY_TO = 'california.bae.sig@gmail.com'
CSV_FILE = os.path.join(os.path.dirname(__file__), 'campaign', 'sig_members_merged.csv')

SUBJECT = 'Last Chance — BAE SIG Raffle Tonight (New Prize Added!)'

def html_body(first):
    return f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; line-height: 1.7; color: #333; margin: 0; padding: 0; }}
  .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
  .header {{ background: #1e3a5f; color: white; padding: 24px 28px; border-radius: 8px 8px 0 0; }}
  .header h1 {{ margin: 0 0 4px; font-size: 1.5rem; }}
  .header p {{ margin: 0; opacity: 0.85; font-size: 0.95rem; }}
  .content {{ background: #f9fafb; padding: 28px; border: 1px solid #e5e7eb; border-top: none; }}
  .prize-box {{ background: white; border: 2px solid #e4b63d; border-radius: 8px; padding: 18px 20px; margin: 20px 0; }}
  .prize-box h3 {{ margin: 0 0 8px; color: #1e3a5f; font-size: 1rem; }}
  .prize-box p {{ margin: 0 0 6px; font-size: 0.92rem; color: #555; }}
  .cta {{ display: block; background: #1e3a5f; color: white !important; text-decoration: none; text-align: center; padding: 14px 24px; border-radius: 8px; font-size: 1.05rem; font-weight: bold; margin: 24px 0; }}
  .pricing {{ text-align: center; color: #555; font-size: 0.9rem; margin-bottom: 20px; }}
  .footer {{ background: #374151; color: #ccc; padding: 16px; border-radius: 0 0 8px 8px; text-align: center; font-size: 0.82rem; }}
  .footer a {{ color: #93c5fd; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>BAE SIG Book Raffle — Tonight!</h1>
    <p>Bay Area Educators Special Interest Group · CalABA 2026</p>
  </div>
  <div class="content">
    <p>Hi {first},</p>
    <p>If you haven't grabbed your raffle tickets yet — this is your last chance. The drawing is happening in a few hours.</p>

    <p><strong>New prize just added:</strong></p>
    <div class="prize-box">
      <h3>Fieldwork and Supervision for Behavior Analysts: A Handbook (2nd Ed.)</h3>
      <p><em>Ellie Kazemi, PhD, BCBA-D &amp; Peter Adzhyan, PsyD, BCBA-D &amp; Brian Rice, MA, BCBA</em></p>
      <p>The definitive competency-based guide to BACB supervision — 418 pages of strategies, case scenarios, meeting templates, and activities for both supervisors and supervisees. Includes the CourseConnect interactive learning platform. Aligns with the BACB Task List (6th ed.).</p>
      <p><strong>Value: $85</strong></p>
    </div>

    <p>If you tried to buy tickets before and ran into a glitch — everything is working now.</p>

    <a href="https://calaba-sig-raffle.vercel.app/" class="cta">Get Your Tickets →</a>
    <p class="pricing">1 ticket = $10 &nbsp;|&nbsp; 3 tickets = $25 &nbsp;|&nbsp; 5 tickets = $40</p>

    <p>The BAE SIG brings together BCBAs and behavior analysts working in educational settings across California. This raffle supports our mission to build community, share resources, and advance the field.</p>

    <p>Can't wait to see everyone in a few hours!</p>

    <p>— Rob Spain<br>BAE SIG President</p>
  </div>
  <div class="footer">
    <p>CalABA 2026 · BAE SIG</p>
    <p><a href="https://calaba-sig-raffle.vercel.app/">calaba-sig-raffle.vercel.app</a></p>
  </div>
</div>
</body>
</html>"""

def send(to_email, first):
    payload = json.dumps({
        "from": FROM_EMAIL,
        "to": [to_email],
        "reply_to": REPLY_TO,
        "subject": SUBJECT,
        "html": html_body(first)
    }).encode()
    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def main():
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    print(f"Sending to {len(rows)} recipients...")
    sent, failed = 0, 0
    for row in rows:
        email = row.get('email', '').strip()
        if not email:
            continue
        # CSV columns: first=last_name, last=first_name (it's swapped in the data)
        # Use 'last' column as the actual first name
        first = row.get('last', '').strip() or row.get('first', '').strip() or 'there'
        first = first.split()[0] if first else 'there'

        status, resp = send(email, first)
        if status in (200, 201):
            print(f"  ✓ {email}")
            sent += 1
        else:
            print(f"  ✗ {email} — {status}: {resp}")
            failed += 1
        time.sleep(0.15)  # ~6/sec, well within Resend limits

    print(f"\nDone. Sent: {sent} | Failed: {failed}")

if __name__ == '__main__':
    main()
