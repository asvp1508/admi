# fetch — collecting fares with code instead of by hand

> **What was actually used:** the 19 October 2026 re-collection was made with
> `google_flights/admi_collect.py`, which drives Google Flights in a headless
> browser and checks the carry-on by price. That is the collector behind
> `data/googleflights_2026-10-19/`. The API-based `collect.py` below is an
> alternative that has not been run against live APIs.
>
> ```bash
> pip install playwright && playwright install chromium
> python fetch/google_flights/admi_collect.py test   # one route, visible browser
> python fetch/google_flights/admi_collect.py        # full run, resumes if stopped
> python3 fetch/google_flights/to_raw.py data/googleflights_2026-10-19
> ```

Turns (origin, destinations, dates) into the same JSON documents the ADMI tool
stores, so a scripted collection is indistinguishable from a hand-typed one and
drops straight into `analysis/admi.py`.

```bash
# see what it would do, without calling anything
python3 fetch/collect.py --origin ATL --dests data/dests_atl.txt \
  --dates 2026-11-20,2026-12-01 --provider mock --dry-run

# a real run
export AMADEUS_CLIENT_ID=...  AMADEUS_CLIENT_SECRET=...
python3 fetch/collect.py --origin ATL --dests data/dests_atl.txt \
  --dates 2026-11-20,2026-12-01,2026-12-11,2027-01-05,2027-01-30 \
  --provider amadeus --out data/raw --collected-on 2026-11-10
```

Output: `data/raw/ATL_2026-11-20_amadeus.json`, one document per origin per date.

## Why there is more than one provider

No single source is both clean and complete, so the provider is swappable and
the honest move is to run two and compare.

| | `amadeus` | `serpapi` |
|---|---|---|
| Where the fares come from | filed by airlines through the GDS | Google Flights |
| Resellers in the results | none, nothing is for sale | yes, and the cheapest is often one |
| Reports base fare vs tax | **yes** | no |
| Ultra low cost carriers | **often missing** | covered |
| Cost | free self-service tier | paid per search |

**The ULCC gap is the one that matters for this study.** Spirit, Frontier,
Allegiant and others distribute little through the GDS. In the Atlanta dataset
a ULCC appears on 92% of routes with three or more airlines and on 1 of 110
single-airline observations, so anything that misses them lands almost entirely
on the competitive side and makes competitive fares look higher than they are.
Amadeus alone would therefore *understate* the gap the index measures, and
Google Flights alone *overstates* it by including unbundled fares and reseller
listings. Run both. Where they disagree, that disagreement is a finding worth
reporting, not a problem to hide.

## Flags worth knowing

- `--airline-only` drops offers a reseller is selling. Offers whose seller is
  unknown are kept rather than silently dropped, and the row records how many
  were ignored.
- `--bag-fees FILE` adds a published carry-on fee to that carrier's fare, so an
  unbundled fare can be compared with a bundled one. Start from
  `bag_fees.template.json`; it refuses to run while any carrier is still `null`,
  so a guess cannot quietly become data. Record the date you checked the fees.
- `--collected-on` sets `daysAhead`. Pass the day the search actually ran.
- `--limit N` stops after N live calls, for trying a provider before spending a
  quota on 245 searches.
- `--refresh` ignores the cache.

## The cache

Every live search is written to `.fetch-cache/`. Re-running skips anything
already there, so an interrupted run resumes and the same search is never paid
for twice. Delete the directory, or pass `--refresh`, to search again.

## What it records that hand collection could not

When a provider reports the fare and tax separately, the row carries `priceBase`
and `priceTax`. That is worth having: the index currently reconstructs the tax
split from published rates, `(shown − 15.40) ÷ 1.075`, which is an estimate with
an Atlanta-specific constant in it. A provider-reported split replaces that
assumption with a measurement, and makes the constant unnecessary for those rows.

## Status

The pipeline is tested end to end through the `mock` provider, which generates
deterministic synthetic fares offline and marks its rows `provider: "mock"`.
Schema, caching, resume, bag fees and the handoff into `analysis/admi.py` are all
verified that way. **The two live providers are written but have not been run
against their APIs**, so expect to shake out credential and field-shape details
on your first real run. Start with `--limit 5`.
