# ADMI — Airline Distortion and Market Index

A quantitative index that separates how much of an airfare is explained by **distance** from how much is explained by **the absence of an alternative**.

Two markets are measured with the same method: Atlanta (ATL) to one airport in each of the other 49 US states, and Bengaluru (BLR) to domestic Indian destinations.

Everything here is reproducible from the raw data in this repository with the standard library alone:

```bash
python3 analysis/admi.py
```

---

## The headline result

From Atlanta, the median price per mile falls by a factor of four as soon as a route has competition. This is visible in the raw fares before any index is applied.

| Airlines on route | Observations | Median $/mile |
|---|---:|---:|
| 1 | 110 | 0.368 |
| 2 | 42 | 0.129 |
| 3 | 59 | 0.090 |
| 4 or more | 15 | 0.084 |

Scoring with the locked model, **18 of 46 Atlanta routes** clear the structural bar, and all 18 clear it on all five dates rather than the four the rule requires. Across 16 variations of the model the count moves between 11 and 24; the list of routes barely changes, because single-airline routes score high under every baseline tested.

The comparison market produces a different and more interesting answer. **Not one priced nonstop out of Bengaluru is flown by a single airline.** The thinnest route in that sample has two. The same gradient measured the same way is 1.15× at Bengaluru against 4.17× at Atlanta. On the evidence so far the Atlanta pattern is a property of a concentrated hub market rather than of air travel in general — though see the limitations before leaning on this.

---

## The model

```
ADMI = 0.5 · PDS + 0.3 · CS + 0.2 · RDS
```

| Term | Definition |
|---|---|
| **FPB** | Fair price baseline, `max(miles × $0.15, $75)`. The floor exists because a flight has costs that do not shrink with distance. |
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
| United States | 7.5% excise tax, $5.60 security fee, $4.50 passenger facility charge | `(shown − 15.40) / 1.075` |
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
| BLR | 2026-10-25 | 33 | 18 | 14 | manual |

Fares fall as the departure date moves further out: the median net fare is $254 at 14 days ahead and $171 at 45 days. This is the opposite of the usual last-minute story and is reported as found, not corrected for.

---

## The tool

`tool/index.html` is a single file with no build step. Open it in a browser and it works offline, keeping observations in the browser's own storage. It has tabs for entry, the sheet, the scoring rules, the methodology, statistics, the two-market comparison, and raw data export.

Fare lookup is optional. `tool/api/search.js` is a serverless function that proxies a search provider so the API key stays on the server. It reads two environment variables and **no key is stored in this repository**:

- `SERPAPI_KEY` — the search provider key
- `ADMI_ACCESS_CODE` — set this, or strangers can spend your search credits

Without those variables the tool still runs; fares are entered by hand, which is how every row in this repository was collected.

---

## Limitations in one paragraph

Two of the five Atlanta tables were extracted with AI assistance and have not been hand-checked against a live search, though they are labelled verified inside the tool. Three fares are implausible and were never rechecked (PHL at $14, IAD at $27, JAC at $221); the PHL fare nets to the $1 clamp, which is a visible symptom rather than a hidden one. The $0.15–$0.20 per mile range, the $0.09 India figure, and the 100-mile cutoff have no citation yet and are stated as assumptions. All fares come from one provider at one moment with no independent cross-check. The Bengaluru market has one date, so nothing there can carry a structural label, and 15 of its 33 destinations are recorded as having no nonstop when several almost certainly do. Air India and Air India Express are counted as separate carriers, which inflates the airline count on several Bengaluru routes. Full detail in [LIMITATIONS.md](LIMITATIONS.md).

---

## Licence

Code is MIT. Data in `data/` is CC BY 4.0: use it, but say where it came from and keep the caveats attached to it.

Arjun Pathi · [github.com/asvp1508](https://github.com/asvp1508) · [medium.com/@pathiarjun15](https://medium.com/@pathiarjun15)
