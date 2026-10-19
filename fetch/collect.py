#!/usr/bin/env python3
"""Collect nonstop fares for a set of routes across a set of dates.

    python3 fetch/collect.py --origin ATL --dests data/dests_atl.txt \
        --dates 2026-11-20,2026-12-01 --provider mock --out data/raw

Writes one document per origin per date, named ORIGIN_DATE_provider.json, in the
same shape as the files already in data/raw/, so output drops straight into the
tool's Data tab or into analysis/admi.py.

Every call is cached on disk. Re-running skips what it already has, so an
interrupted run resumes instead of paying for the same searches twice.
"""
import argparse, json, os, sys, time, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import providers, schema


def load_dests(spec):
    if os.path.exists(spec):
        out = []
        for line in open(spec):
            code = line.strip().split("#")[0].strip().upper()
            if len(code) == 3 and code.isalpha():
                out.append(code)
        return out
    return [c.strip().upper() for c in spec.split(",") if c.strip()]


def load_bag_fees(path):
    """{"frontier": 59, ...} added to that carrier's fare. Missing means zero."""
    if not path:
        return None
    fees = {k: v for k, v in json.load(open(path)).items() if not k.startswith("_")}
    bad = [k for k, v in fees.items() if v is None]
    if bad:
        raise SystemExit("bag fee file has unfilled carriers: %s\n"
                         "Put the published one-way carry-on fee in, or delete the line."
                         % ", ".join(sorted(bad)))
    return {k.lower(): float(v) for k, v in fees.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origin", required=True)
    ap.add_argument("--dests", required=True, help="comma list of IATA codes, or a file with one per line")
    ap.add_argument("--dates", required=True, help="comma list of YYYY-MM-DD departure dates")
    ap.add_argument("--provider", default="mock", choices=["amadeus", "serpapi", "mock"])
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--cache", default=".fetch-cache")
    ap.add_argument("--collected-on", default=datetime.date.today().isoformat(),
                    help="the day the search was run; sets daysAhead (default today)")
    ap.add_argument("--sleep", type=float, default=1.0, help="seconds between live calls")
    ap.add_argument("--airline-only", action="store_true",
                    help="ignore offers a reseller is selling")
    ap.add_argument("--bag-fees", help="JSON of carry-on fees to add, by carrier name")
    ap.add_argument("--limit", type=int, help="stop after this many live calls (for a trial run)")
    ap.add_argument("--refresh", action="store_true", help="ignore the cache and search again")
    ap.add_argument("--dry-run", action="store_true", help="list the searches and exit")
    a = ap.parse_args()

    dests = load_dests(a.dests)
    dates = [d.strip() for d in a.dates.split(",") if d.strip()]
    bag_fees = load_bag_fees(a.bag_fees)
    jobs = [(d, dt) for dt in dates for d in dests]

    print("%s  %d destinations x %d dates = %d searches  via %s"
          % (a.origin, len(dests), len(dates), len(jobs), a.provider))
    if bag_fees:
        print("carry-on fees added: " + ", ".join("%s $%g" % kv for kv in sorted(bag_fees.items())))
    if a.dry_run:
        for d, dt in jobs[:20]:
            print("   %s -> %s on %s" % (a.origin, d, dt))
        if len(jobs) > 20:
            print("   ... and %d more" % (len(jobs) - 20))
        return

    os.makedirs(a.cache, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)
    prov = providers.get(a.provider)

    rows_by_date, live, errors = {dt: [] for dt in dates}, 0, []
    for i, (dest, dt) in enumerate(jobs, 1):
        cpath = os.path.join(a.cache, "%s_%s_%s_%s.json" % (a.origin, dest, dt, a.provider))
        res = None
        if os.path.exists(cpath) and not a.refresh:
            raw = json.load(open(cpath))
            res = providers.RouteResult(a.origin, dest, dt,
                                        offers=[providers.Offer(**o) for o in raw["offers"]],
                                        status=raw["status"])
            tag = "cache"
        else:
            if a.limit is not None and live >= a.limit:
                print("   reached --limit %d, stopping" % a.limit)
                break
            res = prov.search(a.origin, dest, dt)
            live += 1
            json.dump({"status": res.status, "offers": [o.__dict__ for o in res.offers]},
                      open(cpath, "w"), indent=1)
            tag = "live"
            time.sleep(a.sleep)

        r = schema.row(res, a.collected_on, a.provider, a.airline_only, bag_fees)
        rows_by_date[dt].append(r)
        if res.status.startswith("error"):
            errors.append("%s %s %s" % (dest, dt, res.status))
        price = ("$%.0f x%d" % (r["price"], r["carriers"])) if r.get("price") else r["status"]
        print("  [%3d/%3d] %-5s %s %-18s %s" % (i, len(jobs), dest, dt, price, tag))

    for dt, rows in rows_by_date.items():
        if not rows:
            continue
        rows.sort(key=lambda x: x["dest"])
        path = os.path.join(a.out, "%s_%s_%s.json" % (a.origin, dt, a.provider))
        json.dump(schema.document(a.origin, dt, a.provider, rows), open(path, "w"), indent=1)
        ok = sum(1 for r in rows if r["status"] == "ok")
        print("wrote %s  (%d rows, %d priced)" % (path, len(rows), ok))

    print("\n%d live call(s), %d cached." % (live, len(jobs) - live))
    if errors:
        print("%d route(s) errored and were stored as errors, not as 'no nonstop':" % len(errors))
        for e in errors[:10]:
            print("   " + e)
    prov.close()


if __name__ == "__main__":
    main()
