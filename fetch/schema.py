"""Turn provider results into the exact row shape the ADMI tool stores.

Importing a file written here into the tool's Data tab must be indistinguishable
from having typed the rows by hand, so the field names and types match what the
tool writes: see data/raw/*.json in this repository.
"""
from datetime import date as _date, datetime, timezone

MAX_AIRLINES_LISTED = 12


def days_ahead(dep: str, collected: str) -> int:
    a = _date.fromisoformat(collected)
    b = _date.fromisoformat(dep)
    return (b - a).days


def row(result, collected_on, provider_name, airline_only=False, bag_fee=None):
    """One result -> one stored row.

    airline_only : drop offers a reseller is selling. Offers whose seller is
                   unknown are kept, because dropping them would silently
                   remove whole providers; the caller is told how many.
    bag_fee      : {carrier_name_lowercase: fee} added to that carrier's fare,
                   so an unbundled fare can be compared with a bundled one.
    """
    key = "|".join([result.origin, result.dest, result.date, provider_name])
    base = dict(
        key=key, origin=result.origin, dest=result.dest, date=result.date,
        provider=provider_name, daysAhead=days_ahead(result.date, collected_on),
        fetchedAt=datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    )

    if result.status != "ok" or not result.offers:
        note = "" if result.status in ("ok", "no_direct") else result.status
        return dict(base, status="no_direct" if result.status == "ok" else result.status,
                    price=None, carriers=0, airlines="", cheapest="", others="",
                    **({"note": note} if note else {}))

    offers = list(result.offers)
    dropped = 0
    if airline_only:
        kept = [o for o in offers if o.seller != "reseller"]
        dropped = len(offers) - len(kept)
        offers = kept or offers           # never return an empty route because of a filter

    priced = []
    for o in offers:
        total = o.total
        if bag_fee:
            total += bag_fee.get(o.carrier.lower(), 0.0)
        priced.append((total, o))
    priced.sort(key=lambda t: t[0])

    cheapest_total, cheapest_offer = priced[0]
    # Airline count is what the index uses: distinct carriers flying it nonstop.
    names, seen = [], set()
    for _, o in priced:
        k = o.carrier.lower()
        if k not in seen:
            seen.add(k)
            names.append(o.carrier)
    others = [n for n in names if n.lower() != cheapest_offer.carrier.lower()]

    out = dict(base, status="ok",
               price=round(cheapest_total, 2),
               carriers=len(names),
               airlines=", ".join(names[:MAX_AIRLINES_LISTED]),
               cheapest=cheapest_offer.carrier,
               others=", ".join(others[:MAX_AIRLINES_LISTED]))
    if cheapest_offer.base is not None:
        out["priceBase"] = round(cheapest_offer.base, 2)
        out["priceTax"] = round(cheapest_offer.tax or 0.0, 2)
    if cheapest_offer.fare_brand:
        out["fareBrand"] = cheapest_offer.fare_brand
    if dropped:
        out["note"] = "%d reseller offer(s) ignored" % dropped
    return out


def document(origin, date, provider_name, rows):
    """The per-origin-per-date document the tool keeps, id ORIGIN_DATE_provider."""
    return dict(origin=origin, date=date, provider=provider_name, n=len(rows), rows=rows,
                updatedAt=datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"))
