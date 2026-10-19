"""SerpApi, Google Flights engine.

Why this one: coverage. Google Flights sees the ultra low cost carriers that
the GDS feeds miss, so it is the honest counterweight to Amadeus on exactly the
routes where Amadeus is weakest.

What it costs you in return: the headline price can come from a reseller rather
than the airline, and some of those listings are not real fares. This provider
therefore records who is selling, and `--airline-only` in the collector drops
anything not sold by the operating carrier. It reports no fare/tax split, so
rows from here still need the index's tax model.

  export SERPAPI_KEY=...
"""
import os, json, urllib.parse, urllib.request
from .base import Provider, Offer, RouteResult


class SerpApiProvider(Provider):
    name = "serpapi"
    reports_tax_split = False

    def __init__(self, api_key=None, currency="USD", timeout=40, **_):
        self.key = api_key or os.environ.get("SERPAPI_KEY")
        self.currency, self.timeout = currency, timeout
        if not self.key:
            raise SystemExit("set SERPAPI_KEY")

    def search(self, origin, dest, date) -> RouteResult:
        q = urllib.parse.urlencode({
            "engine": "google_flights", "departure_id": origin, "arrival_id": dest,
            "outbound_date": date, "type": "2", "stops": "1",   # 2 = one way, 1 = nonstop only
            "currency": self.currency, "hl": "en", "api_key": self.key})
        try:
            with urllib.request.urlopen("https://serpapi.com/search.json?" + q, timeout=self.timeout) as r:
                js = json.load(r)
        except Exception as e:
            return RouteResult(origin, dest, date, status="error:%s" % e)

        if js.get("error") and not (js.get("best_flights") or js.get("other_flights")):
            msg = js["error"]
            bad = "no_direct" if "hasn't returned any results" in msg or "no results" in msg.lower() else "error:" + msg
            return RouteResult(origin, dest, date, status=bad, raw=js)

        offers = []
        for o in (js.get("best_flights") or []) + (js.get("other_flights") or []):
            legs = o.get("flights") or []
            if len(legs) != 1 or (o.get("layovers") or []):
                continue
            price = o.get("price")
            if not price:
                continue
            air = legs[0].get("airline") or "?"
            offers.append(Offer(
                carrier=air, carrier_code=(legs[0].get("flight_number") or "  ")[:2].strip(),
                total=float(price), currency=self.currency,
                # Google Flights does not name the seller in this payload. Treat it as
                # unknown rather than claiming the airline sold it.
                seller="unknown"))
        return RouteResult(origin, dest, date, offers=offers,
                           status="ok" if offers else "no_direct", raw=js)
