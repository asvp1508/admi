// Vercel serverless function: looks up nonstop one-way fares via SerpApi (Google Flights).
// The API key stays on the server (env var SERPAPI_KEY); the browser never sees it.
// Set ADMI_ACCESS_CODE so strangers cannot spend your search credits.

function parse(js) {
  if (js.error && !(js.best_flights || js.other_flights)) {
    return { status: /no results|hasn't returned any results/i.test(js.error) ? 'no_direct' : 'error: ' + js.error, price: null, airlines: [] };
  }
  const opts = [...(js.best_flights || []), ...(js.other_flights || [])];
  const direct = opts.filter(o => (o.flights || []).length === 1 && !(o.layovers && o.layovers.length));
  if (!direct.length) return { status: 'no_direct', price: null, airlines: [] };
  const prices = direct.map(o => o.price).filter(Boolean);
  const airlines = [...new Set(direct.map(o => o.flights[0].airline || '?'))].sort();
  return { status: 'ok', price: prices.length ? Math.min(...prices) : null, airlines };
}

async function handler(req, res) {
  const need = process.env.ADMI_ACCESS_CODE;
  if (need && req.headers['x-access-code'] !== need) return res.status(401).json({ status: 'unauthorized' });
  const key = process.env.SERPAPI_KEY;
  if (!key) return res.status(503).json({ status: 'not_configured' });
  const { origin, dest, date } = req.query || {};
  if (!/^[A-Z]{3}$/.test(origin || '') || !/^[A-Z]{3}$/.test(dest || '') || !/^\d{4}-\d{2}-\d{2}$/.test(date || '')) {
    return res.status(400).json({ status: 'bad_request' });
  }
  const q = new URLSearchParams({ engine: 'google_flights', departure_id: origin, arrival_id: dest,
    outbound_date: date, type: '2', stops: '1', currency: 'USD', hl: 'en', api_key: key });
  try {
    const r = await fetch('https://serpapi.com/search.json?' + q);
    const js = await r.json();
    res.setHeader('Cache-Control', 'private, max-age=3600');
    return res.status(200).json(parse(js));
  } catch (e) {
    return res.status(502).json({ status: 'error: ' + e.message, price: null, airlines: [] });
  }
}
module.exports = handler;
module.exports.parse = parse;
