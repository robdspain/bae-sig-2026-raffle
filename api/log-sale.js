// api/log-sale.js — Vercel serverless function
// Logs PayPal raffle purchases to Google Sheet via Apps Script web app

module.exports = async (req, res) => {
  // Allow CORS from raffle site
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const { name, email, amount, tickets, orderId, timestamp } = req.body;

  if (!name || !email || !amount || !tickets) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const APPS_SCRIPT_URL = process.env.SHEETS_WEBHOOK_URL;

  if (!APPS_SCRIPT_URL) {
    console.error('SHEETS_WEBHOOK_URL not set');
    // Don't fail the purchase — just log and return success
    return res.status(200).json({ status: 'logged_locally', message: 'Sheet URL not configured' });
  }

  try {
    const payload = {
      timestamp: timestamp || new Date().toISOString(),
      name,
      email,
      amount,
      tickets,
      orderId: orderId || '',
      method: 'paypal'
    };

    const response = await fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const result = await response.text();
    console.log('Sheet log result:', result);

    return res.status(200).json({ status: 'success', message: 'Purchase logged to sheet' });
  } catch (err) {
    console.error('Failed to log to sheet:', err);
    // Don't block the purchase confirmation — just log the error
    return res.status(200).json({ status: 'partial', message: 'Purchase confirmed, sheet log failed' });
  }
};
