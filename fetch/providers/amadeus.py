"""Amadeus Self-Service: Flight Offers Search.

Why this one: Amadeus returns fares filed by the airlines through the GDS, so
there is no reseller markup and nothing is trying to sell you anything. It also
reports the base fare and the tax separately, which means the index does not
have to reconstruct the tax split from published rates.

Known gap, and it matters for this study: several ultra low cost carriers
(Spirit, Frontier, Allegiant and others) distribute little or nothing through
the GDS. On a route where the cheapest nonstop is a ULCC, Amadeus may miss it
and report a higher fare than a traveller would actually pay. Those are mostly
competitive routes, so the gap does not fall evenly. Cross-check against a
second provider before trusting a competitive route's fare.

Credentials: free self-service keys from developers.amadeus.com.
  export AMADEUS_CLIENT_ID=...
  export AMADEUS_CLIENT_SECRET=...
  export AMADEUS_ENV=test        # or "production"
"""
import os, time, json, urllib.parse, urllib.request
from .base import Provider, Offer, RouteResult

HOSTS = {"test": "https://test.api.amadeus.com", "production": "https://api.amadeus.com"}


class AmadeusProvider(Provider):
    name = "amadeus"
    reports_tax_split = True

    def __init__(self, client_id=None, client_secret=None, env=None, currency="USD", timeout=30, **_):
        self.id = client_id or os.environ.get("AMADEUS_CLIENT_ID")
        self.secret = client_secret or os.environ.get("AMADEUS_CLIENT_SECRET")
        self.host = HOSTS[(env or os.environ.get("AMADEUS_ENV") or "test").lower()]
        self.currency, self.timeout = currency, timeout
        self._token, self._expires = None, 0
        if not self.id or not self.secret:
            raise SystemExit("set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET")

    # -- auth ---------------------------------------------------------------
    def _auth(self):
        if self._token and time.time() < self._expires - 60:
            return self._token
        body = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": self.id, "client_secret": self.secret}).encode()
        req = urllib.request.Request(self.host + "/v1/security/oauth2/token", data=body,
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            js = json.load(r)
        self._token = js["access_token"]
        self._expires = time.time() + int(js.get("expires_in", 1799))
        return self._token

    # -- search -------------------------------------------------------------
    def search(self, origin, dest, date) -> RouteResult:
        q = urllib.parse.urlencode({
            "originLocationCode": origin, "destinationLocationCode": dest,
            "departureDate": date, "adults": 1, "nonStop": "true",
            "currencyCode": self.currency, "travelClass": "ECONOMY", "max": 50})
        req = urllib.request.Request(self.host + "/v2/shopping/flight-offers?" + q,
                                     headers={"Authorization": "Bearer " + self._auth()})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                js = json.load(r)
        except Exception as e:
            detail = ""
            if hasattr(e, "read"):
                try:
                    detail = " " + e.read().decode()[:200]
                except Exception:
                    pass
            return RouteResult(origin, dest, date, status="error:%s%s" % (e, detail))

        carriers = (js.get("dictionaries") or {}).get("carriers") or {}
        offers = []
        for o in js.get("data", []):
            its = o.get("itineraries") or []
            # nonStop=true should guarantee this, but never trust a filter you did not apply yourself
            if len(its) != 1 or len(its[0].get("segments") or []) != 1:
                continue
            seg = its[0]["segments"][0]
            code = seg.get("carrierCode", "?")
            price = o.get("price") or {}
            brand = ""
            for tp in o.get("travelerPricings") or []:
                for fd in tp.get("fareDetailsBySegment") or []:
                    brand = fd.get("brandedFare") or fd.get("cabin") or ""
                    break
                break
            offers.append(Offer(
                carrier=carriers.get(code, code), carrier_code=code,
                total=float(price.get("grandTotal") or price.get("total") or 0),
                base=float(price["base"]) if price.get("base") else None,
                tax=(float(price.get("grandTotal") or price.get("total") or 0) - float(price["base"]))
                    if price.get("base") else None,
                currency=price.get("currency", self.currency),
                seller="", fare_brand=brand))
        return RouteResult(origin, dest, date, offers=offers,
                           status="ok" if offers else "no_direct", raw=js)
