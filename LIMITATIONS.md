# Limitations

Read this before quoting any figure from this repository.

Everything below is a known defect, stated at the time of publication rather than discovered later. Items marked **open** have not been fixed.

---

## 1. Data provenance

**open** — The Atlanta tables for **12 November** and **25 November 2026** were extracted with AI assistance from search results rather than entered by hand from a live search. They are labelled `VERIFIED` inside the collection tool. **That label is wrong.** Neither table has been checked route by route against a live search, and the number of routes spot-checked and the number corrected are both unrecorded.

Those two dates are 90 of 226 scored Atlanta observations, so they are not a minor share. What protects the headline result is that the 18 structural routes clear the threshold on all five dates: dropping the two unverified dates entirely would still leave three hand-collected dates on which every one of them qualifies. Any figure quoted from those two dates alone should be treated as provisional.

The other four tables (ATL 25 October, 30 October, 3 November, and BLR 25 October) were entered by hand from live searches.

---

## 2. Implausible fares never rechecked

**open** — Three fares looked wrong on entry and were never verified:

| Route | Displayed fare | Why it is suspect |
|---|---|---|
| ATL–PHL | $14 | Below the tax wedge itself; nets to the $1 implementation clamp |
| ATL–IAD | $27 | Implies $0.05 per mile on a 534-mile route |
| ATL–JAC | $221 | Only priced on one of five dates; the other four record no nonstop |

All three are competitive routes scoring negative ADMI, so they pull the competitive median **down** and make the monopoly-to-competitive ratio look larger than it should. Correcting them would reduce the 4.17× figure. The direction of the error is therefore against the result being claimed, which is the safer direction, but the figure is still overstated until they are fixed.

**open** — ATL–CLT needs a second look for a different reason: at 227 miles with 2 airlines it is the only non-monopoly route among the 18 structural ones, and its price per mile of $1.53 is the highest in the dataset.

---

## 3. Uncited assumptions

**Closed** — **$0.15 to $0.20 per mile.** Now sourced. DOT publishes industry expense per available seat mile of 15.095¢ (1 April 2025), and at the May 2026 domestic load factor of 82.4% the break-even fare per sold seat mile is 18.3¢. The range brackets those two figures and ADMI uses the low end. See METHODOLOGY.md §2 and §13.

**Closed** — **The $75 fixed-cost floor.** Still a judgement rather than an estimate, but no longer without precedent: DOT's SIFL formula uses a fixed terminal charge of $58.95 (second half of 2026) in exactly this role.

**open** — **$0.09 per mile as the India figure.** No external source found. It may come from this project's own Bengaluru data, in which case it is a fitted value presented as a yardstick and **must be labelled as such**, because using the data to set its own baseline is circular. This is now the only unsourced rate in the project and it is the one the entire cross-market comparison rests on. It needs either a published Indian cost-per-ASK figure or an explicit statement that it is fitted from this data.

**open** — **The 100-mile exclusion floor.** Chosen by judgement. No route in either market is actually excluded by it, so nothing currently depends on it.

A system-wide caveat applies to the US rate: expense per ASM averages short-haul, long-haul and widebody flying together, and short-haul costs more per mile than the average. A flat $0.15 therefore understates the fair price on short routes, which is what the floor compensates for, imperfectly.

---

## 4. Single source, single moment

**partly addressed** — A second collection on 19 October 2026, scripted, on five different travel dates, reproduces the same 18 structural routes (README, "A second, independent collection"). It is still the same source, Google Flights, so the cross-check below has not been done.

Every fare comes from one search provider. There is no independent cross-check against another source such as ITA Matrix, and no repeat search to establish how much a fare moves within a single day. Roughly ten routes checked against a second source would be enough to establish agreement; this has not been done.

Airfares also change continuously. These are snapshots, and a rerun on another day would produce different numbers. The claim being made is about the *structure* visible across five dates, not about any individual fare.

---

## 5. The Bengaluru market is incomplete

**open** — One date (25 October 2026) of the five planned. **Nothing from Bengaluru can carry a structural label**, since the label requires five dates by definition. All Bengaluru figures are single-date observations.

**open** — 15 of 33 destinations are recorded as having no nonstop: AGX, AJL, ATQ, DMU, HGI, IMF, IXA, IXC, IXL, KUU, PNY, PYG, RPR, SHL, SXR. Several almost certainly do have nonstops from Bengaluru — Amritsar (ATQ), Chandigarh (IXC) and Raipur (RPR) among them. These are also precisely the rows most likely to contain a thin route, which is to say the rows most likely to change the comparison. The finding that Bengaluru has no single-airline routes **cannot be considered established until they are rechecked.**

**open** — The KUU row has a known internal inconsistency and has not been fixed.

**open** — COK, GOI, DED and IXZ need confirmation.

---

## 6. Airline grouping

**open** — Airlines are counted as they appear in search results, so corporate groups are counted as separate carriers. Air India and Air India Express appear as two airlines on several Bengaluru routes when commercially they are one group. Counting them as one would lower the airline count on those routes, raise their CS, and raise their ADMI.

This matters specifically because it works against the Bengaluru finding: if grouping were applied, some two-airline routes would become one-airline routes, and the claim that Bengaluru has no monopoly routes might not survive. A grouping sensitivity run is written and waits only on the full data. **Until it is run, the Bengaluru result should be stated as conditional on counting Air India and Air India Express separately.**

---

## 7. Festival and holiday dates

**open** — Three of the five collection dates fall in India's festival season, when domestic demand and fares rise sharply. The comparison tab supports excluding dates, but with one Bengaluru date collected there is nothing yet to exclude. When the full set exists, the comparison must be run with and without 3, 12 and 25 November, and both results reported.

The Atlanta dates straddle US Thanksgiving in the same way: 25 November 2026 is the day before the holiday. Its median net fare is the same as 12 November's ($171), so there is no visible holiday spike at Atlanta, but this is one date and not a test.

---

## 8. What the index structurally cannot see

These are design boundaries rather than fixable defects:

- **Costs are never observed.** Only prices are. Nothing here shows that any fare is above cost, and the index cannot distinguish a high margin from a high cost.
- **Only the cheapest nonstop one-way economy fare** is captured. Connecting itineraries, round trips, premium cabins, and bag, seat and change fees are all outside the measurement. A route with no nonstop may be served perfectly well by connections at a reasonable price, and this index records it as nothing at all.
- **Competition is measured by airline count alone.** Seat share, market share, frequency and hub position would all be better measures, and none is used.
- **Distance is great-circle,** not flown. Every per-mile figure is slightly overstated, uniformly across routes.
- **49 Atlanta destinations, one per state.** The state is the sampling unit, which has no particular relationship to airline network structure. It makes a clean story and is not a statistically motivated sample.
- **One hub, one quarter, one direction.** All Atlanta routes originate at a single carrier's largest hub, in a single season, outbound only. Return-direction fares are not collected and may differ.

---

## 9. The published literature finds smaller effects

**open** — GAO-26-107740 (25 June 2026) reviewed the empirical literature on six US airline mergers and found that when a merger removed a direct competitor from a route, fares rose by roughly **1 to 8 percent**. ADMI observes a **4.2× gap** in price per mile between monopoly and competitive routes.

These measure different things. The GAO figure is causal: what happens to one route's fares when it loses a carrier. The ADMI figure is cross-sectional: a comparison between different routes that differ in distance, aircraft size, demand density and seasonality as well as in competition. Both can be correct simultaneously.

But the gap is large enough that it must be addressed explicitly in anything published from this work. A reader who knows the literature and sees an unexplained 4.2× will assume the index is broken. The honest framing is that ADMI describes how thin, uncompetitive routes are priced relative to dense ones, not what would happen to a specific route's fares if a carrier left it.

The same report also finds inflation-adjusted domestic fares about 15% lower in 2024 than 2007, and yields down about 19%. Air travel has become cheaper overall. Any framing that implies the opposite is contradicted by published federal data.

## 10. Correlation, not cause

The monopoly-to-competitive price gap is a correlation observed in a snapshot. Thin routes may be expensive because an airline faces no competitor, or because they are thin for reasons that also make them costly to operate: low demand, small aircraft, poor aircraft utilisation, and seasonal traffic. The $75 floor is a crude attempt to absorb the fixed-cost part of this, and it does not separate the two explanations.

Nothing in this project establishes causation, and the write-up should not claim it.

---

## 11. Status of each headline figure

| Figure | Status |
|---|---|
| Competition gradient at Atlanta, $0.368 → $0.084 per mile | Solid. Visible in raw fares, no model needed. Overstated slightly by the three bad fares in §2. |
| Competitive routes price at 59% of DOT's cost per ASM, monopoly routes at 244% | Suggestive, not conclusive. Cost per ASM is a system-wide average and short-haul costs more per mile, so "below cost" overstates it. |
| 18 structural routes of 46 | Solid. Survives 16 model variants (range 11 to 24) and holds on all five dates. Reproduced exactly by the scripted re-collection, with and without bags (range 13 to 22 with bags). |
| Monopoly to competitive ratio 4.17× | Reproduced at 4.40× by the scripted re-collection, so not an artefact of hand collection. Falls to **3.18×** once a carry-on is included, because Frontier and United price it separately; quote both, labelled. Fix §2 first. Also note this is not distance-controlled; any distance-controlled figure will be lower and the two must never appear in the same passage without labels. |
| Fitted baseline $12.3 + $0.0827 × miles | Solid as a description of the 74 competitive observations. Its fixed term is poorly identified. |
| Fares fall with lead time, $254 at 14 days to $171 at 45 days | Solid within this sample. One hub, one quarter; do not generalise. |
| Bengaluru has no single-airline routes | **Provisional.** Depends on §5 and §6. Do not publish as established. |
| Bengaluru gradient 1.15× vs Atlanta 4.17× | **Provisional.** One date, same dependencies. |

---

## 12. The scripted collection (Google Flights, 19 October 2026)

**open** items for `data/googleflights_2026-10-19/`:

- **The first 7 searches ran with a slightly earlier version of the collector.** `admi_search_log.csv` records every attempt: 249 attempts for 240 searches between 01:47 and 02:50 UTC, with 8 bag-check failures and 1 timeout, all of which passed on a retry. Its first 7 entries (01:47–01:49) mention a dialog-closing step that is not in the committed `admi_collect.py`, so the script was edited and restarted after them. Those 7 were judged by the same price test (4 `not_needed`, 3 `yes`), so the data is unaffected, but the committed script is the version that collected the other 233.
- **"bag toggle failed" in the log does not mean the bag was missing.** It means one step of the click sequence timed out. Three such attempts still show the Frontier fare rising, so the bag had been added before the failing step; the verdict comes from the price, not the click.
- **The bag check is judged on Frontier and Spirit only.** United's carry-on fee is captured in `price_bag` and used in the with-bags figures, but a United route without Frontier is marked `not_needed` without its price change being checked.
- **54 flights were saved as two half-rows,** one with only the no-bag price and one with only the bag price, because Google Flights wrote the space in the departure time differently on the two reads. `to_raw.py` fills each half from the other, so no score is affected. The collector should normalise that space before the next run.
- **Philadelphia appears twice in `admi_fares.csv`,** once as PA and once as DE, because the collector copies it for Delaware. `to_raw.py` drops the DE copy.
- **Anchorage and Jackson Hole have one date each,** because both routes are seasonal. Manchester (NH) had no nonstop on any date.
- **The collector depends on Google Flights' page layout** as it was in October 2026. Its selectors will break when the page changes; a broken run shows up as failures in the log, not as wrong data.
- **Automated collection from Google Flights may conflict with Google's terms of service.** The collector is published so the data can be checked and reproduced, not as a recommendation to run it at scale.
- `date_scraped` is in UTC. The run took place on the evening of 18 October US Eastern time.

