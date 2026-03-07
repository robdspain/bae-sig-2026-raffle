export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { name, email, tickets, amount } = req.body || {};
  if (!name) return res.status(400).json({ error: 'Missing name' });

  const RESEND_API_KEY = 're_9jS7EXqT_J4sbfJz6aCjBSNRQ2yDijLcu';

  try {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'raffle@updates.behaviorschool.com',
        to: ['robspain@gmail.com', 'california.bae.sig@gmail.com'],
        subject: `🎟️ New Raffle Sale: ${name} — ${tickets} ticket${tickets > 1 ? 's' : ''} ($${amount})`,
        html: `
          <h2>New Raffle Ticket Purchase</h2>
          <table style="border-collapse:collapse;width:100%;max-width:400px;">
            <tr><td style="padding:8px;font-weight:bold;background:#f1f5f9;">Name</td><td style="padding:8px;">${name}</td></tr>
            <tr><td style="padding:8px;font-weight:bold;background:#f1f5f9;">Email</td><td style="padding:8px;">${email || '(not provided)'}</td></tr>
            <tr><td style="padding:8px;font-weight:bold;background:#f1f5f9;">Tickets</td><td style="padding:8px;">${tickets}</td></tr>
            <tr><td style="padding:8px;font-weight:bold;background:#f1f5f9;">Amount</td><td style="padding:8px;">$${amount}</td></tr>
            <tr><td style="padding:8px;font-weight:bold;background:#f1f5f9;">Time</td><td style="padding:8px;">${new Date().toLocaleString('en-US', { timeZone: 'America/Los_Angeles' })} PT</td></tr>
          </table>
          <p style="margin-top:16px;color:#64748b;font-size:14px;">Add to drawing tool: <a href="https://calaba-sig-raffle.vercel.app/drawing-tool.html">drawing-tool.html</a></p>
        `
      })
    });

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Failed to send notification' });
  }
}
