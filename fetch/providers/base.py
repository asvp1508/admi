"""Provider interface.

A provider turns (origin, dest, date) into the nonstop offers on that route.
Everything above this layer is provider-agnostic, so sources can be compared
against each other rather than trusted one at a time.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Offer:
    """One bookable nonstop itinerary."""
    carrier: str                      # marketing airline, display name where known
    carrier_code: str                 # IATA code, e.g. "DL"
    total: float                      # what the passenger pays, taxes included
    base: Optional[float] = None      # fare before tax, when the provider reports it
    tax: Optional[float] = None       # tax and fees, when the provider reports it
    currency: str = "USD"
    seller: str = ""                  # who sells it; "" means the airline itself
    fare_brand: str = ""              # e.g. "BASIC", when reported

    @property
    def sold_by_airline(self) -> bool:
        """True when the operating airline sells it, rather than a reseller."""
        return self.seller == "" or self.seller.lower() in ("airline", self.carrier.lower())


@dataclass
class RouteResult:
    origin: str
    dest: str
    date: str
    offers: List[Offer] = field(default_factory=list)
    status: str = "ok"                # ok | no_direct | error:<reason>
    raw: Optional[dict] = None        # provider payload, kept for auditing


class Provider:
    name = "base"
    #: True when the provider reports the fare/tax split itself, so the
    #: tax model in the index can be switched off for its rows.
    reports_tax_split = False

    def search(self, origin: str, dest: str, date: str) -> RouteResult:
        raise NotImplementedError

    def close(self) -> None:
        pass
