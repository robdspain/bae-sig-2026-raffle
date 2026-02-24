# Raffle Purchases → Google Sheet Setup

One-time setup. Takes ~5 minutes.

---

## Step 1 — Open the Purchases Sheet

Open: https://docs.google.com/spreadsheets/d/1umiLYHYtszRFaInsq17RJR2XpzLs1v9H89yBOP8cjLI

Add these headers to Row 1:
```
Timestamp | Name | Email | Amount | Tickets | PayPal Order ID | Method
```

---

## Step 2 — Create the Apps Script

1. In the sheet: **Extensions → Apps Script**
2. Delete any existing code and paste this:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);

    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.name || '',
      data.email || '',
      data.amount || '',
      data.tickets || '',
      data.orderId || '',
      data.method || 'paypal'
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

3. Click **Save** (name the project anything, e.g. "Raffle Logger")

---

## Step 3 — Deploy as Web App

1. Click **Deploy → New deployment**
2. Click the gear icon ⚙️ next to "Type" → select **Web app**
3. Set:
   - **Execute as:** Me (california.bae.sig@gmail.com)
   - **Who has access:** Anyone
4. Click **Deploy**
5. Copy the **Web app URL** — looks like:
   `https://script.google.com/macros/s/XXXXX/exec`

---

## Step 4 — Add URL to Vercel

In the Vercel dashboard for the raffle site:
**Settings → Environment Variables → Add:**
```
SHEETS_WEBHOOK_URL = [paste the web app URL here]
```

Then **redeploy** the site.

---

## Done!
Every PayPal purchase will now auto-log to the sheet with:
- Timestamp
- Buyer name + email
- Amount paid
- Number of tickets
- PayPal Order ID
