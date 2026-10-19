#!/usr/bin/env python3
"""
Turn admi_fares.csv (one row per flight, from admi_collect.py) into the
per-date JSON documents analysis/admi.py reads, in two versions:

  bags/      cheapest fare WITH 1 carry-on   (price_bag)
  no_bags/   cheapest fare without bags      (price_plain)

The two folders differ only in which price column is used, so comparing
them isolates the effect of the carry-on fee.

    python3 fetch/google_flights/to_raw.py data/googleflights_2026-10-19
"""
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import date

# Destinations searched (admi_collect.py DESTINATIONS), so a route with no
# nonstop on a date is recorded as such instead of silently missing.
SEARCHED = ["BHM", "ANC", "PHX", "LIT", "LAX", "DEN", "BDL", "MCO", "HNL", "BOI",
            "ORD", "IND", "DSM", "ICT", "SDF", "MSY", "PWM", "BWI", "BOS", "DTW",
            "MSP", "JAN", "STL", "BZN", "OMA", "LAS", "MHT", "EWR", "ABQ", "LGA",
            "CLT", "FAR", "CMH", "OKC", "PDX", "PHL", "PVD", "CHS", "FSD", "BNA",
            "DFW", "SLC", "BTV", "DCA", "SEA", "CRW", "MKE", "JAC"]

# Codeshare labels that Google Flights prints for one airline.
SAME_AIRLINE = {"AmericanAlaska": "American"}


def num(x):
    return float(x) if x not in ("", None) else None


def main(folder):
    src = os.path.join(folder, "admi_fares.csv")
    flights = defaultdict(list)
    scraped = None
    with open(src, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            # PHL is searched once; the collector also writes a copy labelled DE.
            if r["dest_state"] == "DE":
                continue
            scraped = r["date_scraped"]
            flights[(r["travel_date"], r["dest"])].append(r)

    dates = sorted({d for d, _ in flights})
    for version, col, other in (("bags", "price_bag", "price_plain"),
                                ("no_bags", "price_plain", "price_bag")):
        out_dir = os.path.join(folder, version)
        os.makedirs(out_dir, exist_ok=True)
        for d in dates:
            ahead = (date.fromisoformat(d) - date.fromisoformat(scraped)).days
            rows = []
            for dest in SEARCHED:
                fl = flights.get((d, dest), [])
                base = dict(origin="ATL", dest=dest, date=d, daysAhead=ahead,
                            provider="googleflights", fetchedAt=scraped,
                            key=f"ATL|{dest}|{d}|googleflights")
                if not fl:
                    rows.append(dict(base, status="no_direct", price=None,
                                     carriers=0, airlines="", cheapest=""))
                    continue
                priced = []
                for f in fl:
                    p = num(f[col]) if num(f[col]) is not None else num(f[other])
                    priced.append((p, SAME_AIRLINE.get(f["carrier"], f["carrier"])))
                price, cheapest = min(priced)
                names = sorted({c for _, c in priced})
                rows.append(dict(base, status="ok", price=price, carriers=len(names),
                                 airlines=", ".join(names), cheapest=cheapest,
                                 bag_check=fl[0]["bag_check"]))
            doc = dict(origin="ATL", date=d, provider="googleflights",
                       collected_on=scraped, price_column=col, n=len(rows), rows=rows)
            with open(os.path.join(out_dir, f"ATL_{d}_googleflights.json"), "w") as fh:
                json.dump(doc, fh, indent=1)
        print(f"{version}: {len(dates)} documents in {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/googleflights_2026-10-19")
