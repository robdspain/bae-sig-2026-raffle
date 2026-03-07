#!/usr/bin/env python3
"""
BAE SIG Member Email Campaign — Daily Donor Spotlight Series
Sends one email per day to 242 SIG members via Resend API.
Usage: python3 send_sig_email.py --email-num 1
"""

import os, sys, csv, json, time, argparse
from datetime import datetime
import urllib.request

RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
FROM_EMAIL = 'california.bae.sig@updates.behaviorschool.com'
REPLY_TO = 'california.bae.sig@gmail.com'
CSV_FILE = os.path.join(os.path.dirname(__file__), 'campaign/sig_members.csv')

EMAILS = {
    1: {
        'subject': '🎟️ Win a private session with Dr. Peter Killeen — BAE SIG Raffle is LIVE',
        'body': """Hi {first_name},

The BAE SIG CalABA 2026 raffle is officially open — and we're kicking it off with something special.

🌟 Today's Featured Donor: Dr. Peter Killeen
Professor Emeritus at Arizona State University and one of the most cited behavioral scientists alive, Dr. Killeen has spent decades modeling the mathematics of behavior — his work on reinforcement schedules, behavioral momentum, and the MPR model has shaped how the field understands why behavior happens.

He's donated a 1-hour private Zoom consultation (valued at $200+). That's one hour with one of the brightest minds in behavior analysis — yours to use however you'd like: your research, a tough case, data analysis, philosophy of science. Whatever you need.

🎟️ Tickets start at $10 — and get cheaper the more you grab.
👉 https://calaba-sig-raffle.vercel.app

Every dollar supports SIG programming at CalABA and beyond. Drawing is at the Friday reception (March 7).

See you in Sacramento,

Rob Spain, BCBA, IBA
President, BAE SIG"""
    },
    2: {
        'subject': '🧠 $500 OBM program up for grabs — BAE SIG Raffle',
        'body': """Hi {first_name},

Today's prize might be the most valuable in the raffle.

🌟 Today's Featured Donor: Mellanie Page
Mellanie is an OBM (Organizational Behavior Management) practitioner and educator who has built one of the most respected training programs in the field. OBM applies the science of behavior analysis to real-world organizations — improving performance, culture, and outcomes in ways that make our whole field more credible.

She's donated complete access to her OBM Practitioner Program (valued at $500+). If you've ever wanted to expand your practice into organizational settings, work with businesses, or add OBM credentials — this is your ticket in. Literally.

🎟️ Tickets start at $10 — discounts when you buy more.
👉 https://calaba-sig-raffle.vercel.app

Drawing at the CalABA Friday reception — March 7.

See you there,

Rob Spain, BCBA, IBA
President, BAE SIG"""
    },
    3: {
        'subject': '📚 A book + 20 minutes with Portia James — today\'s raffle prize',
        'body': """Hi {first_name},

If you work in schools or with underserved communities, today's spotlight is for you.

🌟 Today's Featured Donor: Portia C. James, BCBA
Portia is the CEO of Behavior Genius and a leading voice in culturally responsive, community-centered ABA. She's on a mission to make behavior analysis more equitable — and she's doing it. Behavior Genius is actively building the bridge between the science we love and the communities that need it most.

She's donated a signed copy of her book + a 20-minute one-on-one mentor session. Whether you want to talk shop, get career advice, or discuss how to bring culturally responsive practices into your work — this is 20 uninterrupted minutes with someone who's doing the work.

🎟️ Tickets start at $10 — grab a few and stack your odds.
👉 https://calaba-sig-raffle.vercel.app

Every ticket supports all SIGs. Drawing March 7 at the Friday reception.

Talk soon,

Rob Spain, BCBA, IBA
President, BAE SIG"""
    },
    4: {
        'subject': '🌍 ABA + climate action: today\'s featured raffle donor',
        'body': """Hi {first_name},

Here's a prize that makes you think differently about what our field can do.

🌟 Today's Featured Donor: Dr. Caroly Shumway
Caroly is a Ph.D. behavior analyst and a founder of the ABA Climate Coalition — a growing movement applying the science of behavior change to the most pressing issue of our time. Climate action isn't separate from behavior analysis. It is behavior analysis. Caroly is proving that.

She's donated 1 free BACB CEU through an ABACC workshop — a gift certificate for any ABA Climate Coalition training event. CEUs that make you think bigger and earn credit while doing it.

🎟️ Tickets start at $10. Drawing March 7.
👉 https://calaba-sig-raffle.vercel.app

All proceeds support BAE SIG and the broader SIG community.

See you at CalABA,

Rob Spain, BCBA, IBA
President, BAE SIG"""
    },
    5: {
        'subject': '📗 3 copies of Essential for Living — this week\'s raffle prize',
        'body': """Hi {first_name},

Today's prize is one every school-based practitioner should know about.

🌟 Today's Featured Donor: Reginald Ponio & BABAC
Reggie Ponio and the team at BABAC are donating three copies of the Essential for Living user manual — the comprehensive functional skills curriculum and assessment tool for learners with developmental disabilities.

EFL is one of the most practically useful assessment systems in our field, especially for the population most school-based BCBAs serve every day. Three copies. One winner.

🎟️ Tickets start at $10 — discounts when you buy more, so grab a few.
👉 https://calaba-sig-raffle.vercel.app

4 days to CalABA. Drawing March 7.

See you soon,

Rob Spain, BCBA, IBA
President, BAE SIG"""
    },
    6: {
        'subject': '⏰ One week out + a BehaviorSchool prize to close us out',
        'body': """Hi {first_name},

Last spotlight — and yes, this one's from me.

🌟 Today's Featured Donor: BehaviorSchool
I built BehaviorSchool to give BCBAs and RBTs the best possible exam prep — 10,000+ AI-generated practice questions, mock exams, an AI tutor, and adaptive learning that adjusts to how you learn.

I'm donating a 6-month full access subscription (valued at $180) — whether you're sitting for the BCBA, the BCaBA, or mentoring someone who is, this is the tool I wish I'd had.

But more than the prize — this raffle is about us. All the SIGs. Every ticket funds the programming, speakers, and community that makes CalABA worth showing up to.

🎟️ Tickets start at $10 — discounts when you buy more. Drawing Friday, March 7.
👉 https://calaba-sig-raffle.vercel.app

Thank you for being part of this community.

See you in Sacramento,

Rob Spain, BCBA, IBA
President, BAE SIG
california.bae.sig@gmail.com"""
    },
    7: {
        'subject': '🔴 Last chance — raffle closes Friday at CalABA',
        'body': """Hi {first_name},

Quick reminder: the BAE SIG raffle closes at the Friday reception (March 7).

The prizes are incredible — a private session with Dr. Peter Killeen, a $500 OBM program, books, CEUs, and more.

If you haven't grabbed a ticket yet, now's the time:
👉 https://calaba-sig-raffle.vercel.app

Tickets start at $10 — discounts when you buy more. Huge prizes. All SIGs benefit.

See you at CalABA

Rob Spain, BCBA, IBA
President, Behavior Analysts in Education SIG"""
    },
    8: {
        'subject': 'CalABA Special Interest Group Reception — Friday at 6:00 PM',
        'body': """Hi {first_name},

Quick reminder: the CalABA Special Interest Group Reception is Friday night at 6:00 PM — and the raffle closes there.

Today’s donor spotlight: Meghann DeLeon Miller
Meghann is presenting “Unlocking the Potential of Active Engagement” on Friday, March 6 (2:00–3:00 PM, Ballroom A). Her session focuses on practical, research-informed strategies for building active engagement in learners — especially relevant for school-based practitioners.

She also leads a full-day workshop on Trauma-Informed Escape Behaviors (Thu, Mar 5) and appears on a panel about practicing ABA with sudden chronic illness/disability (Fri, Mar 6).

If you haven’t grabbed a ticket yet, now’s the time:
👉 https://calaba-sig-raffle.vercel.app

Tickets start at $10 — and there’s a discount when you buy multiple tickets.

Thank you for supporting all CalABA Special Interest Groups.

Rob Spain, BCBA, IBA
President, Behavior Analysts in Education SIG"""
    }
}


def send_email(to_email, to_name, subject, body):
    first_name = to_name.strip() or 'there'
    text = body.format(first_name=first_name)

    payload = json.dumps({
        'from': f'Rob Spain — BAE SIG <{FROM_EMAIL}>',
        'to': [to_email.strip()],
        'reply_to': REPLY_TO,
        'subject': subject,
        'text': text,
    }).encode()

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; BAE-SIG-Campaign/1.0)',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return False, json.loads(body)
        except Exception:
            return False, {'message': body.decode('utf-8', errors='replace')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--email-num', type=int, required=True, choices=range(1,9))
    parser.add_argument('--dry-run', action='store_true', help='Print first 3 without sending')
    parser.add_argument('--limit', type=int, default=None, help='Only send to first N recipients')
    args = parser.parse_args()

    if not RESEND_API_KEY:
        print('❌ RESEND_API_KEY not set'); sys.exit(1)

    email_cfg = EMAILS[args.email_num]
    subject = email_cfg['subject']
    body = email_cfg['body']

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        members = list(csv.DictReader(f))

    if args.limit:
        members = members[:args.limit]

    print(f"📧 Email #{args.email_num}: {subject}")
    print(f"📋 Recipients: {len(members)}")
    if args.dry_run:
        print("🔍 DRY RUN — first 3:\n")
        for m in members[:3]:
            print(f"  To: {m['first']} {m['last']} <{m['email']}>")
            print(body.format(first_name=m['first'] or 'there')[:200] + '...\n')
        return

    sent = failed = 0
    for i, m in enumerate(members):
        ok, resp = send_email(m['email'], m['first'], subject, body)
        if ok:
            sent += 1
            print(f"  ✅ {i+1}/{len(members)} {m['email']}")
        else:
            failed += 1
            print(f"  ❌ {i+1}/{len(members)} {m['email']} — {resp}")
        if i < len(members) - 1:
            time.sleep(0.6)  # stay under rate limits

    print(f"\n✅ Sent: {sent} | ❌ Failed: {failed}")


if __name__ == '__main__':
    main()
