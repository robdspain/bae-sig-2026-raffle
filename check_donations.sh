#!/bin/bash
# Book Donation Response Tracker - Shell version
# Uses curl to interact with Gmail API directly

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACKER_FILE="$SCRIPT_DIR/donation_tracker.csv"
RESPONSE_DRAFTS_DIR="$SCRIPT_DIR/response_drafts"
NOTIFICATION_DRAFTS_DIR="$SCRIPT_DIR/notification_drafts"

# Get access token
get_token() {
    curl -s --request POST \
        --url "https://oauth2.googleapis.com/token" \
        --data "client_id=REDACTED_GOOGLE_CLIENT_ID" \
        --data "client_secret=REDACTED_GOOGLE_CLIENT_SECRET" \
        --data "refresh_token=REDACTED_GOOGLE_REFRESH_TOKEN" \
        --data "grant_type=refresh_token" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])"
}

echo "📚 Checking for book donation responses..."
TOKEN=$(get_token)

# Search for responses
RESPONSES=$(curl -s --request GET \
    --url "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=subject:\"Book+Donation+Request\"+OR+subject:\"BAE+SIG+Book+Raffle\"+after:2026/02/02" \
    --header "Authorization: Bearer $TOKEN")

MESSAGE_COUNT=$(echo $RESPONSES | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('messages',[])))")

if [ "$MESSAGE_COUNT" = "0" ]; then
    echo "✅ No new responses found."
    exit 0
fi

echo "Found $MESSAGE_COUNT potential response(s)"
echo ""
echo "📝 NEXT STEPS:"
echo "1. Manual review needed - check Gmail for responses to book donation emails"
echo "2. When you see a response, tell Neo to:"
echo "   - Draft a thank you email"
echo "   - Create board notification"
echo ""
echo "Or run: python3 check_donations.py (when dependencies are installed)"
