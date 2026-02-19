# BAE SIG Email Campaign (Resend)

## Quick Start

### 1. Set your Resend API key
```bash
export RESEND_API_KEY='re_xxxxxxxxxxxx'
```

### 2. Update the FROM_EMAIL
Edit `email_campaign.py` line 14:
```python
FROM_EMAIL = 'raffle@yourdomain.com'  # Must be verified in Resend
```

Or use the Resend test domain for now:
```python
FROM_EMAIL = 'onboarding@resend.dev'  # Works immediately, sends to your own email only
```

---

## Commands

### List available templates
```bash
python3 email_campaign.py templates
```

### Send single email
```bash
# Donation request
python3 email_campaign.py send --to author@example.com --template donation_request --name "Dr. Smith"

# Thank you
python3 email_campaign.py send --to author@example.com --template thank_you --name "Dr. Smith" --book "The Book Title"

# Raffle promo
python3 email_campaign.py send --to attendee@example.com --template raffle_promo --name "Jane"
```

### Dry run (preview without sending)
```bash
python3 email_campaign.py send --to test@example.com --template donation_request --dry-run
```

### Batch send from CSV
```bash
# Create a CSV with columns: name, email, book_title (optional)
python3 email_campaign.py batch --csv contacts.csv --template donation_request

# Preview first
python3 email_campaign.py batch --csv contacts.csv --template donation_request --dry-run
```

### Test all templates
```bash
python3 email_campaign.py test --to your@email.com
```

---

## Templates

| Template | Purpose |
|----------|---------|
| `donation_request` | Ask authors/speakers to donate books |
| `thank_you` | Confirm donation received |
| `raffle_promo` | Promote raffle to attendees |

---

## CSV Format

```csv
name,email,book_title
Dr. Jane Smith,jane@university.edu,Applied Behavior Analysis
John Doe,john@example.com,
```

- `name` - Required
- `email` - Required
- `book_title` - Optional (for thank_you template)

---

## Sent emails are logged to `campaign_tracker.csv`
