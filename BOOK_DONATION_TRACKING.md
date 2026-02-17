# Book Donation Tracking System

## How It Works

### 1. Check for New Responses
Run this command to scan for new responses to book donation emails:
```bash
# From the repo root
python3 check_donations.py
```

### 2. What the System Does
- Searches gmail for responses to book donation request emails
- Extracts donor info (name, email, book they're donating)
- Logs to `donation_tracker.csv`
- Creates response email drafts in `response_drafts/`
- Notifies board members

### 3. Files Created
- `donation_tracker.csv` - Master list of all donations
- `response_drafts/[timestamp]-response.txt` - Response email drafts for approval
- `notification_drafts/[timestamp]-board-notice.txt` - Board member notifications

### 4. Email Response Template
When a speaker responds willing to donate:
- Thank them for their donation
- Confirm drop-off location at CalABA before Friday night SIG reception
- Mention we'll send book/presentation info
- Await your approval before sending

---

## To Add New Donor Response

Edit `donation_tracker.csv`:
```csv
date,name,email,book,status,notes
2026-02-03,Speaker Name,email@example.com,"Book Title",pending,Speaker confirmed donation
```

---

## Next Steps
1. Review `check_donations.py` script
2. Test with current inbox
3. Approve response drafts before sending
