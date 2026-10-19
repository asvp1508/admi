"""Offline provider, so the whole pipeline can be exercised without an API key.

Fares are generated from a fixed seed: deterministic, obviously synthetic, and
never to be mistaken for collected data. Rows it writes carry provider "mock".
"""
import hashlib
from .base import Provider, Offer, RouteResult

FLEET = [("Delta", "DL"), ("American", "AA"), ("United", "UA"),
         ("Southwest", "WN"), ("Frontier", "F9"), ("JetBlue", "B6")]


class MockProvider(Provider):
    name = "mock"
    reports_tax_split = False

    def __init__(self, **_):
        pass

    def _rand(self, *parts):
        h = hashlib.sha256("|".join(parts).encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    def search(self, origin, dest, date) -> RouteResult:
        r = self._rand(origin, dest, date)
        if r < 0.06:
            return RouteResult(origin, dest, date, status="no_direct")
        n = 1 + int(self._rand(dest, "n") * 3.99)          # 1 to 4 airlines
        offers = []
        for i in range(n):
            name, code = FLEET[int(self._rand(dest, date, str(i)) * (len(FLEET) - 1))]
            total = round(60 + self._rand(dest, date, "p", str(i)) * 420, 2)
            offers.append(Offer(carrier=name, carrier_code=code, total=total, seller=""))
        return RouteResult(origin, dest, date, offers=offers, status="ok")
