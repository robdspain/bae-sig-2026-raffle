// api/log-sale.js — Vercel serverless function
// Logs PayPal raffle purchases to Google Sheet via Apps Script web app

const { ConvexHttpClient } = require("convex/browser");

module.exports = async (req, res) => {
  // ... (CORS headers)
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  // ...

  const { name, email, amount, tickets, orderId, timestamp } = req.body;
  
  const saleData = {
    timestamp: timestamp || new Date().toISOString(),
    name,
    email,
    amount,
    tickets,
    orderId: orderId || '',
    method: 'paypal'
  };

  // --- Log to Google Sheet (existing logic) ---
  const APPS_SCRIPT_URL = process.env.SHEETS_WEBHOOK_URL;
  if (APPS_SCRIPT_URL) {
    fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(saleData),
    }).catch(err => console.error('Sheet log failed:', err));
  }

  // --- Log to Convex DB (new logic) ---
  const CONVEX_URL = process.env.CONVEX_URL;
  if (CONVEX_URL) {
    try {
      const convex = new ConvexHttpClient(CONVEX_URL);
      await convex.mutation("raffle:logSale", saleData);
    } catch (err) {
      console.error('Convex log failed:', err);
    }
  }

  return res.status(200).json({ status: 'success', message: 'Log requests initiated' });
};

