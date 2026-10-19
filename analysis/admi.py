#!/usr/bin/env python3
"""
ADMI reference implementation and analysis.

Reproduces every published figure from the raw observations in data/raw/.
Standard library only. Run from the repository root:

    python3 analysis/admi.py                                          # hand-collected data
    python3 analysis/admi.py data/googleflights_2026-10-19/bags       # scraped, with 1 carry-on
    python3 analysis/admi.py data/googleflights_2026-10-19/no_bags    # scraped, no bags

The model configuration below was locked on 2026-10-11, after the Atlanta
data was collected and before any result was published. Do not change it
to improve a result; add a variant to STRESS_TESTS instead.
"""

import csv
import json
import math
import os
import statistics as st
import sys

# --------------------------------------------------------------------------
# Locked model configuration
# --------------------------------------------------------------------------

LOCKED = dict(
    rate=0.15,        # fair price, dollars per mile
    min_fpb=75.0,     # fixed cost floor, dollars per nonstop
    smooth=True,      # PDS = 1 - e^-x rather than a hard 0-1 clamp
    remove_tax=True,  # strip the tax wedge before scoring
    w_pds=0.5,
    w_cs=0.3,
    w_rds=0.2,
    ref=500.0,        # distance reference for RDS, miles
    floor=100.0,      # routes shorter than this are excluded
    threshold=0.6,    # ADMI at or above this counts as a hit
    share=0.8,        # share of dates that must be hits to call a route structural
    min_dates=5,      # a route needs at least this many dates to be labelled
)

# Competition score by number of airlines on the route.
CS_TIERS = {1: 1.00, 2: 0.66, 3: 0.33}
CS_DEFAULT = 0.10  # 4 or more

# Tax and fee wedge, by origin country. Net fare = (shown - flat) / (1 + pct/100).
#   United States: 7.5% excise, $5.60 security fee, $4.50 passenger facility charge
#   India: 5% GST, Rs 300 BLR user development fee, Rs 236 security fee, at Rs 95.58/$
TAX_RULES = {
    "United States": dict(pct=7.5, flat=15.40),
    "India": dict(pct=5.0, flat=5.61),
}

# Headline yardstick per market: the per-mile rate quoted in the write-up.
# India uses no fixed floor because domestic Indian fares sit far below the
# $75 figure, which would otherwise swamp every short route.
YARDSTICKS = {
    "ATL": dict(rate=0.15, min_fpb=75.0, label="US $0.15/mi + $75 floor"),
    "BLR": dict(rate=0.09, min_fpb=0.0, label="India $0.09/mi, no floor"),
}

EARTH_RADIUS_MI = 3958.8


# --------------------------------------------------------------------------
# Core model
# --------------------------------------------------------------------------

def haversine(a, b):
    """Great circle distance in miles between two (lat, lon) pairs."""
    p = math.pi / 180
    dlat = (b[0] - a[0]) * p
    dlon = (b[1] - a[1]) * p
    h = (math.sin(dlat / 2) ** 2
         + math.cos(a[0] * p) * math.cos(b[0] * p) * math.sin(dlon / 2) ** 2)
    return 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(h))


def net_fare(shown, country, remove_tax=True):
    """Strip the tax and fee wedge from a displayed fare."""
    if not remove_tax or shown is None:
        return shown
    rule = TAX_RULES.get(country)
    if rule is None:
        return shown
    return max(1.0, (shown - rule["flat"]) / (1 + rule["pct"] / 100))


def competition_score(airlines, tiers=None, default=None):
    tiers = CS_TIERS if tiers is None else tiers
    default = CS_DEFAULT if default is None else default
    return tiers.get(airlines, default)


def score_route(miles, fare, airlines, cfg=None, fpb_override=None,
                cs_tiers=None, cs_default=None):
    """Score one route on one date. Returns the full component breakdown."""
    c = dict(LOCKED)
    if cfg:
        c.update(cfg)

    fpb = fpb_override if fpb_override is not None else max(miles * c["rate"], c["min_fpb"])
    fpb = max(fpb, 1.0)
    x = (fare - fpb) / fpb
    cs = competition_score(airlines, cs_tiers, cs_default)

    if c["smooth"]:
        pds = 1 - math.exp(-x) if x > 0 else max(-1.0, x)
        q = max(0.0, pds) * (c["ref"] / max(miles, c["floor"]))
        rds = 1 - math.exp(-q)
    else:
        pds = min(1.0, max(0.0, x))
        rds = min(1.0, max(0.0, pds * c["ref"] / max(miles, c["floor"])))

    admi = c["w_pds"] * pds + c["w_cs"] * cs + c["w_rds"] * rds
    return dict(fpb=fpb, pds_raw=x, pds=pds, cs=cs, rds=rds, admi=admi)


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

def load_airports(path="data/airports.csv"):
    out = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            out[row["iata"]] = dict(
                lat=float(row["lat"]), lon=float(row["lon"]),
                country=row["country"], city=row["city"],
            )
    return out


def load_observations(path="data/raw"):
    """Read the database documents. Returns {origin: {date: [rows]}}."""
    out = {}
    for name in sorted(os.listdir(path)):
        if not name.endswith(".json"):
            continue
        doc = json.load(open(os.path.join(path, name)))
        doc = doc.get("data", doc)
        origin, date, _provider = name[:-5].split("_")
        out.setdefault(origin, {})[date] = doc["rows"]
    return out


def build(origin, obs, airports, cfg=None, exclude_dates=(), fit_baseline=False):
    """Score every usable observation for one origin. Returns (rows, fit)."""
    c = dict(LOCKED)
    if cfg:
        c.update(cfg)
    country = airports[origin]["country"]
    here = (airports[origin]["lat"], airports[origin]["lon"])

    rows = []
    for date, raw in obs[origin].items():
        if date in exclude_dates:
            continue
        for r in raw:
            if r.get("status") != "ok" or r.get("price") is None:
                continue
            dest = r["dest"]
            if dest not in airports:
                continue
            miles = haversine(here, (airports[dest]["lat"], airports[dest]["lon"]))
            if miles < c["floor"]:
                continue
            rows.append(dict(
                origin=origin, dest=dest, date=date, miles=miles,
                shown=r["price"],
                fare=net_fare(r["price"], country, c["remove_tax"]),
                airlines=r.get("carriers") or 0,
                airline_names=r.get("airlines") or "",
            ))

    # Optional empirical baseline: OLS through fares on competitive routes.
    fit = None
    if fit_baseline:
        pts = [(r["miles"], r["fare"]) for r in rows if r["airlines"] >= 3]
        if len(pts) < 8:
            pts = [(r["miles"], r["fare"]) for r in rows if r["airlines"] >= 2]
        n = len(pts)
        sx = sum(p[0] for p in pts)
        sy = sum(p[1] for p in pts)
        sxx = sum(p[0] ** 2 for p in pts)
        sxy = sum(p[0] * p[1] for p in pts)
        b = (n * sxy - sx * sy) / (n * sxx - sx * sx)
        a = (sy - b * sx) / n
        fit = dict(intercept=a, slope=b, n=n)

    for r in rows:
        override = None
        if fit:
            override = fit["intercept"] + fit["slope"] * max(r["miles"], c["floor"])
        r.update(score_route(r["miles"], r["fare"], r["airlines"], cfg,
                             override,
                             (cfg or {}).get("cs_tiers"),
                             (cfg or {}).get("cs_default")))
    return rows, fit


def structural_routes(rows, cfg=None):
    """Routes scoring at or above the threshold on enough of the dates."""
    c = dict(LOCKED)
    if cfg:
        c.update(cfg)
    by_route = {}
    for r in rows:
        by_route.setdefault(r["dest"], []).append(r["admi"])
    n_dates = len({r["date"] for r in rows})
    summary = {}
    for dest, scores in by_route.items():
        hits = sum(1 for v in scores if v >= c["threshold"])
        summary[dest] = dict(hits=hits, n=len(scores), mean=st.mean(scores))
    labelled = {
        d: v for d, v in summary.items()
        if n_dates >= c["min_dates"] and v["n"] >= n_dates and v["hits"] / v["n"] >= c["share"]
    }
    return labelled, summary, n_dates


# --------------------------------------------------------------------------
# Stress tests
# --------------------------------------------------------------------------

STRESS_TESTS = [
    ("Locked model", {}),
    ("Fair price $0.175/mile", dict(rate=0.175)),
    ("Fair price $0.20/mile", dict(rate=0.20)),
    ("No minimum fair price", dict(min_fpb=0.0)),
    ("Minimum fair price $100", dict(min_fpb=100.0)),
    ("Hard 0-to-1 cut-offs, no floor", dict(smooth=False, min_fpb=0.0)),
    ("Equal weights", dict(w_pds=1 / 3, w_cs=1 / 3, w_rds=1 / 3)),
    ("Weights 0.6 / 0.3 / 0.1", dict(w_pds=0.6, w_cs=0.3, w_rds=0.1)),
    ("Competition as 1 / airlines", dict(cs_tiers={1: 1.0, 2: 0.5, 3: 1 / 3}, cs_default=0.25)),
    ("Taxes left in", dict(remove_tax=False)),
    ("Distance reference 300", dict(ref=300.0)),
    ("Distance reference 1000", dict(ref=1000.0)),
    ("Threshold 0.5", dict(threshold=0.5)),
    ("Threshold 0.7", dict(threshold=0.7)),
    ("Share 100 percent", dict(share=1.0)),
]


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def band(miles):
    if miles < 500:
        return "under 500 mi"
    if miles < 1000:
        return "500 to 1000 mi"
    return "over 1000 mi"


def report(data_dir="data/raw"):
    airports = load_airports()
    obs = load_observations(data_dir)

    print("=" * 74)
    print("ADMI  |  locked model, 2026-10-11  |  data: %s" % data_dir)
    print("=" * 74)
    print("FPB  = max(miles x $%.2f, $%.0f)" % (LOCKED["rate"], LOCKED["min_fpb"]))
    print("PDS  = 1 - e^-x   where x = (net fare - FPB) / FPB   [x itself if x <= 0]")
    print("CS   = 1 airline 1.00 | 2 airlines 0.66 | 3 airlines 0.33 | 4+ 0.10")
    print("RDS  = 1 - e^-q   where q = max(0, PDS) x %.0f / max(miles, %.0f)"
          % (LOCKED["ref"], LOCKED["floor"]))
    print("ADMI = %.1f PDS + %.1f CS + %.1f RDS" % (LOCKED["w_pds"], LOCKED["w_cs"], LOCKED["w_rds"]))
    print("structural = ADMI >= %.2f on at least %.0f%% of at least %d dates"
          % (LOCKED["threshold"], LOCKED["share"] * 100, LOCKED["min_dates"]))

    for origin in sorted(obs):
        yard = YARDSTICKS.get(origin, {})
        cfg = {k: v for k, v in yard.items() if k in ("rate", "min_fpb")}
        rows, _ = build(origin, obs, airports, cfg)
        labelled, summary, n_dates = structural_routes(rows, cfg)

        print()
        print("-" * 74)
        print("%s  |  %d dates  |  yardstick: %s" % (origin, n_dates, yard.get("label", "default")))
        print("-" * 74)

        for date in sorted(obs[origin]):
            raw = obs[origin][date]
            priced = [r for r in raw if r.get("status") == "ok" and r.get("price") is not None]
            print("  %s   rows %3d   priced %3d   no nonstop %2d"
                  % (date, len(raw), len(priced), len(raw) - len(priced)))

        print()
        print("  scored observations      %d" % len(rows))
        print("  routes scored            %d" % len(summary))
        print("  mean ADMI                %.3f" % st.mean(r["admi"] for r in rows))
        print("  median ADMI              %.3f" % st.median(r["admi"] for r in rows))
        if n_dates >= LOCKED["min_dates"]:
            print("  structural routes        %d" % len(labelled))
        else:
            print("  structural routes        not labelled, needs %d dates" % LOCKED["min_dates"])

        print()
        print("  price per mile by airline count (net fares)")
        for label, test in (("1", lambda k: k == 1), ("2", lambda k: k == 2),
                            ("3", lambda k: k == 3), ("4+", lambda k: k >= 4)):
            v = [r["fare"] / r["miles"] for r in rows if test(r["airlines"])]
            if v:
                print("    %-3s airline(s)  n=%3d   median $%.3f   mean $%.3f"
                      % (label, len(v), st.median(v), st.mean(v)))
            else:
                print("    %-3s airline(s)  none in sample" % label)
        thin = [r["fare"] / r["miles"] for r in rows if r["airlines"] == min(x["airlines"] for x in rows)]
        thick = [r["fare"] / r["miles"] for r in rows if r["airlines"] >= 3]
        if thin and thick:
            print("    thinnest vs 3+ airlines ratio   %.2fx" % (st.median(thin) / st.median(thick)))

        print()
        print("  distance bands")
        for label in ("under 500 mi", "500 to 1000 mi", "over 1000 mi"):
            sel = [r for r in rows if band(r["miles"]) == label]
            if sel:
                print("    %-15s n=%3d   $/mile %.3f   mean ADMI %.3f"
                      % (label, len(sel),
                         st.median(r["fare"] / r["miles"] for r in sel),
                         st.mean(r["admi"] for r in sel)))

        print()
        print("  by date")
        for date in sorted(obs[origin]):
            sel = [r for r in rows if r["date"] == date]
            print("    %s   n=%2d   median net $%-4.0f   median ADMI %6.3f   ADMI >= %.1f on %d"
                  % (date, len(sel), st.median(r["fare"] for r in sel),
                     st.median(r["admi"] for r in sel), LOCKED["threshold"],
                     sum(1 for r in sel if r["admi"] >= LOCKED["threshold"])))

        _, fit = build(origin, obs, airports, cfg, fit_baseline=True)
        print()
        print("  empirical baseline on routes with 3+ airlines")
        print("    FPB = $%.1f + $%.4f x miles   (n=%d)"
              % (fit["intercept"], fit["slope"], fit["n"]))

        print()
        print("  every route, mean ADMI across dates")
        print("    %-5s %7s %5s %10s %8s %7s %8s"
              % ("dest", "miles", "airl", "net range", "$/mile", "hits", "mean"))
        for dest, v in sorted(summary.items(), key=lambda kv: -kv[1]["mean"]):
            sel = [r for r in rows if r["dest"] == dest]
            fares = sorted(r["fare"] for r in sel)
            mark = "*" if dest in labelled else (" " if v["mean"] >= 0 else "-")
            print("  %s %-5s %7.0f %5d %10s %8.3f %4d/%-2d %8.3f"
                  % (mark, dest, sel[0]["miles"], sel[0]["airlines"],
                     "$%.0f-%.0f" % (fares[0], fares[-1]),
                     st.median(r["fare"] / r["miles"] for r in sel),
                     v["hits"], v["n"], v["mean"]))
        print("    * structural   - prices below what distance alone justifies")

        unpriced = sorted({r["dest"] for date in obs[origin] for r in obs[origin][date]
                           if r.get("status") != "ok" or r.get("price") is None})
        if unpriced:
            print()
            print("  recorded as no nonstop or unpriced (%d): %s"
                  % (len(unpriced), ", ".join(unpriced)))

        if n_dates >= LOCKED["min_dates"]:
            print()
            print("  stress test: structural count under each variation")
            for label, variant in STRESS_TESTS:
                merged = dict(cfg)
                merged.update(variant)
                v_rows, _ = build(origin, obs, airports, merged)
                v_lab, _, _ = structural_routes(v_rows, merged)
                print("    %-34s %2d   mean ADMI %.3f"
                      % (label, len(v_lab), st.mean(r["admi"] for r in v_rows)))
            merged = dict(cfg)
            f_rows, f_fit = build(origin, obs, airports, merged, fit_baseline=True)
            f_lab, _, _ = structural_routes(f_rows, merged)
            print("    %-34s %2d   mean ADMI %.3f"
                  % ("Fitted baseline instead of rate", len(f_lab),
                     st.mean(r["admi"] for r in f_rows)))

    print()
    print("=" * 74)
    print("Figures above are reproduced from %s/. See LIMITATIONS.md before" % data_dir)
    if data_dir == "data/raw":
        print("quoting any of them: the 12 and 25 November Atlanta tables are not")
        print("hand-verified, and the Bengaluru market has one date only.")
    else:
        print("quoting any of them.")
    print("=" * 74)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(os.path.join(root, "data")):
        os.chdir(root)
    data_dir = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "data/raw"
    if not os.path.isdir(data_dir):
        sys.exit("no such folder: %s  (run from the repository root)" % data_dir)
    report(data_dir)
