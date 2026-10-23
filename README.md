# ADMI — Airline Distortion and Market Index

A quantitative index that separates how much of an airfare is explained by **distance** from how much is explained by **the absence of an alternative**.

The market measured is Atlanta (ATL) to one airport in each of the other 49 US states. A second market, Bengaluru (BLR), was planned as a comparison and has been dropped; the reason is below.

Everything here is reproducible from the raw data in this repository with the standard library alone:

```bash
python3 analysis/admi.py                                          # hand-collected data
python3 analysis/admi.py data/googleflights_2026-10-19/bags       # scripted re-collection, 1 carry-on included
python3 analysis/admi.py data/googleflights_2026-10-19/no_bags    # same re-collection, no bags
```

---

## The headline result

From Atlanta, a route with one airline costs about three times as much per mile as a route with three or more, even after the carry-on that Frontier and United charge separately is priced in. These are the bag-inclusive figures, the ones quoted in Part 5 of the write-up:

| Airlines on route | Observations | Median $/mile |
|---|---:|---:|
| 1 | 114 | 0.371 |
| 2 | 38 | 0.174 |
| 3 | 60 | 0.118 |
| 4 or more | 15 | 0.113 |

**18 routes are structural**, and all 18 clear the bar on all five dates rather than the four the rule requires. 17 of them are flown only by Delta; the 18th, Charlotte, has two airlines. Across 16 variations of the model the count moves between 13 and 22, and 12 routes are structural under every one of them. Seven routes score below zero (Orlando, Dallas, Denver, Las Vegas, Los Angeles, Philadelphia, Phoenix), and every one of them has a budget airline on it.

The first, hand-collected dataset (no bags) finds the same 18 routes out of 46 scored. Its medians are $0.368, $0.129, $0.090 and $0.084 a mile, a 4.17× gap, and its stress-test range is 11 to 24, with 10 routes structural under every variation.

### A second, independent collection

The Atlanta fares were collected a second time on 19 October 2026, by a script instead of by hand, on five different travel dates. Each search was run twice, once with no bags and once with one carry-on added, and the script only accepted a search when the Frontier fare actually rose with the bag. It also showed that United's cheapest fares exclude a carry-on (71 of 72 rose by $50–55).

| Collection | Structural routes | 1 airline vs 3+, per mile |
|---|---:|---:|
| By hand (Oct 11–13), no bags | 18 | 4.17× |
| Script (Oct 19), no bags | 18 | 4.40× |
| Script (Oct 19), **1 carry-on included** | **18** | **3.18×** |

All three produce the **same 18 routes**. The gap also reproduces without bags (4.17× by hand, 4.40× by script). Adding the carry-on fee that Frontier and United charge separately lowers it to 3.18×, so a little over a quarter of the raw gap comes from fares that leave the bag out, not from competition. The bag-inclusive figure is the fairer comparison and should be quoted next to the other.

### Why there is no Bengaluru comparison

Bengaluru was meant to show whether the Atlanta pattern belongs to a concentrated hub or to air travel in general. One date was collected by hand (25 October 2026, kept in `data/raw/` for the record). The five-date scripted collection on 19 October failed: during the run, Google Flights showed IndiGo, India's largest airline, as "Price unavailable", so no IndiGo fare was captured, and routes flown mostly by IndiGo came back empty. A Bengaluru dataset without its largest airline would get both the airline counts and the cheapest fares wrong, so **no Bengaluru figure is reported** and the earlier single-date comparison (1.15× against 4.17×) is withdrawn. Every result in this repository is about Atlanta.

---

## The model

```
ADMI = 0.5 · PDS + 0.3 · CS + 0.2 · RDS
```

| Term | Definition |
|---|---|
| **FPB** | Fair price baseline, `max(miles × $0.15, $75)`. The $0.15 matches DOT's published industry expense per available seat mile of 15.095¢. The floor exists because a flight has costs that do not shrink with distance, mirroring the fixed terminal charge in DOT's own SIFL formula. |
| **PDS** | Price distortion, `1 − e^(−x)` where `x = (net fare − FPB) / FPB`. Below the fair price PDS is `x` itself, down to −1, so cheap competitive routes score negative instead of piling up at zero. |
| **CS** | Competition, from the airline count alone: 1 airline = 1.00, 2 = 0.66, 3 = 0.33, 4 or more = 0.10. |
| **RDS** | Route distance, `1 − e^(−q)` where `q = max(0, PDS) × 500 / max(miles, 100)`, so the same overcharge counts for more on a short route. |
| **Structural** | ADMI ≥ 0.60 on at least 80% of at least 5 dates. In practice, 4 of 5. |

Routes under 100 miles are excluded. Negative ADMI means the fare sits below what distance alone would justify.

**Worked example.** Atlanta to Little Rock, 452 miles, 1 airline, shown fare $331. Taxes out: $293. FPB = max(452 × 0.15, 75) = $67.80. x = 3.32, so PDS = 0.96, CS = 1.00, RDS = 1 − e^(−1.07) = 0.66, **ADMI = 0.912**.

Full derivation, every assumption, and the rejected alternatives are in [METHODOLOGY.md](METHODOLOGY.md).

### The model is locked

The configuration was fixed on **2026-10-11**, after the Atlanta data was collected and before any result was published. The `LOCKED` dictionary at the top of `analysis/admi.py` is that configuration. Changing a parameter after seeing the output would make every result here unpublishable. New ideas go into `STRESS_TESTS` as named variants, never into `LOCKED`.

---

## Taxes and fees

Fares are collected as displayed, which includes tax. The index compares fares against an operating-cost baseline, so the tax wedge is removed first. The rule is keyed on the origin airport's country.

| Market | Components | Net fare |
|---|---|---|
| United States | 7.5% excise tax, $5.30 domestic segment tax, $5.60 security fee, $4.50 passenger facility charge | `(shown − 15.40) / 1.075` |
| India | 5% GST on economy, ₹300 BLR user development fee (from 1 Sep 2026), ₹236 aviation security fee, at ₹95.58/$ | `(shown − 5.61) / 1.05` |
| Elsewhere | no rule written | unchanged |

---

## What is in this repository

```
data/
  admi_raw_observations.csv   278 observations exactly as collected
  admi_scored.csv             244 scored rows with every intermediate column
  airports.csv                84 airports with coordinates, for distances
  raw/                        the six source documents as JSON
  googleflights_2026-10-19/
    admi_fares.csv            scripted re-collection, one row per flight, both prices
    admi_search_log.csv       every search attempt, with the reason it passed or failed
    bags/  no_bags/           the same data as JSON documents for analysis/admi.py
fetch/
  google_flights/
    admi_collect.py           the collector that produced googleflights_2026-10-19
    to_raw.py                 turns admi_fares.csv into the bags/ and no_bags/ documents
analysis/
  admi.py                     reference implementation; reproduces every figure
tool/
  index.html                  the single-file collection and scoring tool
  airports.js                 airport table the tool loads
  build_data.py               builds airports.js from the source airport data
  api/search.js               optional serverless fare lookup
METHODOLOGY.md                full specification and every assumption
LIMITATIONS.md                read this before quoting any number
```

### Data dictionary

`admi_raw_observations.csv` — one row per route per date, as collected.

| Column | Meaning |
|---|---|
| `origin`, `dest` | IATA codes |
| `date` | departure date searched |
| `status` | `ok` if a nonstop fare was found, otherwise no nonstop was offered |
| `fare_shown_usd` | cheapest nonstop one-way economy fare as displayed, taxes included |
| `carriers` | number of airlines operating the nonstop |
| `airlines` | their names, comma separated |
| `cheapest_carrier` | airline offering the cheapest fare |
| `other_carriers` | airlines offering connecting service where no nonstop exists |
| `days_ahead` | lead time between the search and departure |
| `source` | how the row was obtained |
| `note` | collection notes, including fares typed for routes with no nonstop |

`admi_scored.csv` adds `miles`, `fare_net_usd`, `fpb_usd`, `pds_raw`, `pds`, `cs`, `rds`, `admi` and the `yardstick` used. Atlanta rows are scored at $0.15 per mile with the $75 floor; Bengaluru rows at $0.09 per mile with no floor, since Indian domestic fares sit far below the floor and it would otherwise swamp every short route.

---

## Data collection

Every fare is the cheapest **nonstop, one-way, economy** fare for a single traveller. All five dates for a market are searched on the same day, so each date carries a different lead time and the lead-time effect can be separated from a route's own level.

| Origin | Date | Rows | Priced | Days ahead | Source |
|---|---|---:|---:|---:|---|
| ATL | 2026-10-25 | 49 | 45 | 14 | manual |
| ATL | 2026-10-30 | 49 | 45 | 19 | manual |
| ATL | 2026-11-03 | 49 | 46 | 23 | manual |
| ATL | 2026-11-12 | 49 | 45 | 32 | Gemini-assisted, **not hand-verified** |
| ATL | 2026-11-25 | 49 | 45 | 45 | Gemini-assisted, **not hand-verified** |
| BLR | 2026-10-25 | 33 | 18 | 14 | manual, not used (Bengaluru dropped) |
| ATL | 2026-10-28 | 48 | 45 | 9 | script, Google Flights |
| ATL | 2026-11-07 | 48 | 46 | 19 | script, Google Flights |
| ATL | 2026-11-17 | 48 | 45 | 29 | script, Google Flights |
| ATL | 2026-12-04 | 48 | 45 | 46 | script, Google Flights |
| ATL | 2027-01-07 | 48 | 46 | 80 | script, Google Flights |

The scripted collection (`fetch/google_flights/admi_collect.py`) searches every route twice on the same page, first with no bags and then with one carry-on added, and saves both prices for every flight. A search is accepted only if a Frontier or Spirit fare went up when the bag was added, or if neither airline flies the route; otherwise it is retried, up to three times, and recorded as failed. The check is made on prices, not on page text, so the script cannot mark a bag as added when it was not. All 77 route-dates with Frontier passed. `admi_search_log.csv` records all 249 attempts: 8 bag checks failed on the first try and passed on a retry, and 13 searches found no nonstop (Manchester on every date, Anchorage and Jackson Hole on four).

Fares fall as the departure date moves further out: the median net fare is $254 at 14 days ahead and $171 at 45 days. This is the opposite of the usual last-minute story and is reported as found, not corrected for.

---

## The tool

`tool/index.html` is a single file with no build step. Open it in a browser and it works offline, keeping observations in the browser's own storage. It is the same file as the hosted copy at [arjun-pathi-portfolio.vercel.app/admi-tool](https://arjun-pathi-portfolio.vercel.app/admi-tool/), with both Atlanta datasets built in and about 300 airports. It has tabs for entry, the sheet, the scoring rules, the methodology, statistics, the two-market comparison, and raw data export.

Fare lookup is optional. `tool/api/search.js` is a serverless function that proxies a search provider so the API key stays on the server. It reads two environment variables and **no key is stored in this repository**:

- `SERPAPI_KEY` — the search provider key
- `ADMI_ACCESS_CODE` — set this, or strangers can spend your search credits

Without those variables the tool still runs; fares are entered by hand, which is how every row in this repository was collected.

---

## How this sits against the published evidence

Measured against DOT's industry expense per available seat mile of 15.095¢, Atlanta's competitive routes price at **59%** of that figure and its single-airline routes at **244%**. Cost per ASM is a system-wide average and short-haul flying costs more per mile, so this is suggestive rather than conclusive, but the spread is large.

The relevant federal study, [GAO-26-107740](https://files.gao.gov/reports/GAO-26-107740/index.html) (June 2026), cuts both ways and is engaged with directly in METHODOLOGY.md §13. It supports the premise in one respect: concentration has risen specifically on the thinnest routes, and 58% of the least-travelled routes have no effective low-cost competitor. It complicates the premise in two others: inflation-adjusted domestic fares are about 15% *lower* than in 2007, and the merger literature finds that losing a route competitor raises fares by roughly 1 to 8 percent, not several hundred.

Those are different quantities — a causal effect on one route versus a cross-sectional comparison between routes — and this project claims only the second. It does not claim to have measured what would happen to a route's fares if a carrier left it.

## Limitations in one paragraph

Two of the five Atlanta tables were extracted with AI assistance and have not been hand-checked against a live search, though they are labelled verified inside the tool. Three fares are implausible and were never rechecked (PHL at $14, IAD at $27, JAC at $221); the PHL fare nets to the $1 clamp, which is a visible symptom rather than a hidden one. The $0.15–$0.20 per mile range is now sourced to DOT cost data, but the 100-mile cutoff remains uncited. The scripted re-collection reproduces the 18 structural routes on five different dates, but both collections come from Google Flights, so there is still no cross-check against a second source. Bengaluru was dropped because Google Flights did not price IndiGo during the scripted run. Full detail in [LIMITATIONS.md](LIMITATIONS.md).

---

## Write-up

The project is written up as a series on Medium:

1. [I Checked Flights From Atlanta to 49 States. Some of the Prices Made No Sense.](https://pathiarjun15.medium.com/part-1-introducing-admi-what-49-flights-out-of-atlanta-taught-me-about-fake-prices-abf5ec600b3f): the idea and the three questions
2. [What Makes a Plane Ticket "Expensive"? Building a Way to Measure It](https://pathiarjun15.medium.com/part-2-building-the-admi-model-484d3f06cc0b): the model in words
3. [The Math Behind a $422 Ticket to Wichita](https://pathiarjun15.medium.com/part-3-the-admi-math-d3ac2b16ca34): every formula, worked through one fare, and how to read a score
4. [I Automated 240 Google Flights Searches. The Bugs Taught Me More Than the Code.](https://pathiarjun15.medium.com/part-4-the-tool-that-automated-admi-5f30f1b519b3): the tool and the collector
5. [Flying 322 Miles From Atlanta Costs More Than Flying 404. The Difference Is One Airline.](https://pathiarjun15.medium.com/part-5-the-results-18-routes-and-almost-all-of-them-belong-to-one-airline-a5c8779d803d): the results

A sixth part, comparing the hand and scripted collections, is planned. The numbers in the posts are the ones this repository reproduces; if they ever disagree, the repository is the record.

---

## Licence

Code is MIT. Data in `data/` is CC BY 4.0: use it, but say where it came from and keep the caveats attached to it.

Arjun Pathi · [github.com/asvp1508](https://github.com/asvp1508) · [medium.com/@pathiarjun15](https://medium.com/@pathiarjun15)
