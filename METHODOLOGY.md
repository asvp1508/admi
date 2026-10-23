# Methodology

Specification of the Airline Distortion and Market Index, with every assumption stated and the alternatives that were tried and rejected.

Model configuration locked **2026-10-11**.

---

## 1. What the index claims and does not claim

ADMI scores one nonstop route on one date for how far its cheapest fare sits above what distance alone would justify, weighted by how little competition the route has.

It is a **descriptive** index. A high score says that a fare is unusually high for its distance on a thin route. It does not establish that any airline has done anything unlawful, has market power in the legal sense, or is pricing above cost. Costs are not observed anywhere in this project; only prices are.

The unit of analysis is the **route × date** pair. This matters: it is what allows a route's own level to be separated from movement common to every route on a given date.

---

## 2. Fair Price Baseline (FPB)

```
FPB = max(miles × $0.15, $75)
```

What the route would cost if priced on distance alone.

**The $0.15 rate** is now sourced rather than assumed. The US Department of Transportation publishes industry expense per available seat mile (ASM) in Appendix A of its semi-annual Standard Industry Fare Level filing: **15.095 cents**, applicable 1 April 2025. The $0.15 rate matches that figure to within 1%.

The wider $0.15 to $0.20 range is derived rather than asserted. Cost per *available* seat mile assumes every seat sells. At the actual US domestic load factor of **82.4%** (May 2026, BTS), the break-even fare per *sold* seat mile is 15.095 ÷ 0.824 = **18.3 cents**. So the range brackets two real quantities: cost per available seat mile at the low end, break-even per sold seat at the high end. ADMI uses the low end, which is the conservative choice.

One caveat that must travel with this figure: expense per ASM is a system-wide average across short-haul, long-haul and widebody flying. Short-haul operations cost more per mile than the average, so a flat $0.15 understates the fair price on short routes. That is exactly what the fixed-cost floor below is for.

**The $75 floor** exists because a flight has costs that do not shrink with distance: crew, gate, turnaround, ground handling. Without it, the 134-mile Atlanta to Birmingham route has a fair price of $20, and any real fare scores as extreme distortion. Every short monopoly route would then pile up near 1.0 and the index would be measuring distance, not competition. The floor only affects routes shorter than 500 miles, where `miles × 0.15 < 75`.

The structure has federal precedent. DOT's SIFL formula is itself a fixed **terminal charge** plus a per-mile rate, and the terminal charge for the second half of calendar 2026 is **$58.95**. ADMI's $75 floor is the same device at a slightly higher, more conservative value. The specific $75 figure remains a judgement, not an estimate from this data. For a sense of scale, an OLS line through Atlanta fares on routes with 3 or more airlines gives:

```
FPB_fitted = $12.3 + $0.0827 × miles      (n = 74)
```

That implies competitive routes price near $0.083 per mile, roughly half the $0.15 assumption, with a fixed part near $12. The fixed part is poorly identified because there are too few short competitive routes in the sample to pin it down, which is exactly why the floor is set by assumption rather than fitted. Results are reported with the floor on and off, and with the fitted line substituted entirely (see §8).

### An alternative that was tried, and a correction to why

An earlier draft used a **distance-tapered** baseline, `0.15 × (d/900)^−0.5` per mile, so that the per-mile rate fell with distance. It was dropped because it conflates the fixed-cost effect with the distance effect in one term, and because a flat rate plus an explicit floor states the same intuition with one assumption instead of an exponent. **Any figure computed under the tapered baseline is not comparable to the figures in this repository.**

That reasoning stands, but the earlier framing of a taper as unprincipled was wrong. DOT's own SIFL formula bands the per-mile rate by distance — for the second half of 2026, $0.3225 per mile to 500 miles, $0.2459 from 501 to 1,500, and $0.2364 beyond — so a declining per-mile rate is established federal practice, not an invention. A banded variant belongs in `STRESS_TESTS` as a named alternative.

### Why SIFL itself is not used as the baseline

SIFL was tested as a complete substitute for FPB and the result is reported here because it is instructive. Under a full SIFL baseline the structural count collapses from 18 to **3** and mean ADMI falls from 0.372 to 0.083.

That is not evidence against the index; it is evidence that SIFL measures something else. SIFL exists to impute the taxable value of employer-provided and non-commercial aircraft flights, and its per-mile rates sit far above commercial economy fares — $0.3225 per mile for a short hop, against an observed median of $0.090 on competitive routes. Benchmarking scheduled economy fares against a private-aviation valuation formula would make nearly every fare look like a bargain. **Only the expense-per-ASM figure inside the SIFL filing, and the terminal-charge structure, are used here.**

---

## 3. Price Distortion Score (PDS)

```
x   = (net fare − FPB) / FPB
PDS = 1 − e^(−x)        when x > 0
PDS = max(−1, x)        when x ≤ 0
```

The original version clamped `x` to the interval [0, 1]. That version is kept as a stress-test variant, and it had two defects:

- Every fare at or below the fair price scored exactly 0, so a route priced at half the baseline and one priced exactly at it were indistinguishable.
- Every fare above twice the baseline scored exactly 1, so a 2× route and a 5× route were indistinguishable.

The smooth form fixes both. Above the fair price, a fare at 2× scores 0.63, 3× scores 0.86, and the score approaches 1 without reaching it. Below the fair price, the discount is carried through as a negative number, so a genuinely cheap competitive route scores below zero. **ADMI can therefore be negative, and that is informative rather than an error**: 12 Atlanta routes have negative mean ADMI, all of them with 3 or more airlines.

---

## 4. Competition Score (CS)

| Airlines operating the nonstop | CS |
|---:|---:|
| 1 | 1.00 |
| 2 | 0.66 |
| 3 | 0.33 |
| 4 or more | 0.10 |

Deliberately crude, and deliberately the only place competition enters. CS uses the airline **count** alone: not market share, not seat share, not whether a carrier is low-cost, not hub status. Every one of those would be a better measure of competitive structure and every one would require data this project does not have. The count is observable directly from a search result, which means anyone can reproduce it.

The tiers are set by judgement, not fitted. `1 / airlines` (1.00, 0.50, 0.33, 0.25) is carried as a stress-test variant and changes the structural count not at all.

**Known weakness.** Airline groups are counted as separate carriers. Air India and Air India Express appear as two airlines on several Bengaluru routes when commercially they are one group, which inflates those airline counts and lowers their CS. A grouping sensitivity run is written but waits on the full Bengaluru data.

---

## 5. Route Distance Score (RDS)

```
q   = max(0, PDS) × 500 / max(miles, 100)
RDS = 1 − e^(−q)
```

The same proportional overcharge matters more on a short route, where a traveller has realistic alternatives (driving, a bus, a train) and where the absolute fare is small enough that a 3× multiple is striking. The 500-mile reference sets where that effect is at full strength. RDS is bounded below at 0 because a discount should not be amplified by distance; only overcharges are.

Variants at 300 and 1000 miles are in the stress test and move the structural count by at most one route.

---

## 6. Weights and the threshold

```
ADMI = 0.5 · PDS + 0.3 · CS + 0.2 · RDS
```

Price is the thing being measured, so it carries half. Competition is the explanation being tested, so it carries most of the rest. Distance is a modifier, so it carries least. These are judgement calls. Equal weights and a 0.6 / 0.3 / 0.1 split are both in the stress test; the structural count moves from 18 to 16 and 19 respectively.

**Threshold.** A route is a hit on a date when ADMI ≥ 0.60. With CS at 1.00 for a monopoly contributing 0.30 before price enters at all, a monopoly route needs roughly PDS ≥ 0.5 — a fare about 1.7× the fair price — to reach 0.60. A competitive route with CS at 0.10 contributes 0.03 and needs a very large price distortion to qualify, which is the intended asymmetry: the index is built to find expensive thin routes.

**Structural label.** ADMI ≥ 0.60 on at least 80% of dates, with at least 5 dates required. This is what separates a route that is persistently expensive from one that happened to be expensive on a single search. In the Atlanta data the rule turns out not to be doing any work: all 18 structural routes clear the bar on **all five** dates, not four, so the result is not sensitive to where the share is set.

**Distance floor.** Routes under 100 miles are excluded entirely. On a route that short, the fare has almost nothing to do with distance and driving is nearly always an option, so the index's logic does not apply. *The specific 100-mile value needs a source; see LIMITATIONS.md.* In practice no route in either market is excluded by it.

---

## 7. Tax and fee removal

The index compares fares against an operating-cost baseline, so government taxes and airport fees are stripped before scoring. The rule is keyed on the origin airport's country.

**United States** — 7.5% federal excise tax on the base fare, $5.30 domestic segment tax, $5.60 September 11th Security Fee, and $4.50 Passenger Facility Charge. The three flat charges sum to the $15.40 constant:

```
net = (shown − 15.40) / 1.075
```

**India** — 5% GST on economy tickets, ₹300 BLR User Development Fee (effective 1 September 2026), ₹236 Aviation Security Fee, converted at ₹95.58 to the dollar:

```
net = (shown − 5.61) / 1.05
```

Assumptions in this step:

- The flat component is treated as a single charge per itinerary. For a one-way nonstop, which is all this project collects, that is correct. It would be wrong for a connecting itinerary.
- The rupee conversion uses one snapshot exchange rate rather than a date-matched rate.
- The `max(1, …)` clamp in the implementation means an absurdly low displayed fare nets to $1 rather than a negative number. The PHL row at a $14 displayed fare hits this clamp, which is a visible flag that the fare is wrong, not a correction of it.

Scoring with taxes left in is a stress-test variant and moves the Atlanta structural count from 18 to 19.

---

## 8. Stress testing

The question a reviewer should ask is whether the headline number is an artefact of the assumptions. Every variation below is run by `analysis/admi.py` on the Atlanta data.

| Configuration | Structural routes | Mean ADMI |
|---|---:|---:|
| **Locked model** | **18** | 0.372 |
| Fair price $0.175/mile | 14 | 0.330 |
| Fair price $0.20/mile | 11 | 0.292 |
| No minimum fair price | 19 | 0.394 |
| Minimum fair price $100 | 17 | 0.341 |
| Hard 0-to-1 cut-offs, no floor | 20 | 0.545 |
| Equal weights | 16 | 0.391 |
| Weights 0.6 / 0.3 / 0.1 | 19 | 0.369 |
| Competition as 1 / airlines | 18 | 0.366 |
| Taxes left in | 19 | 0.434 |
| Distance reference 300 | 17 | 0.357 |
| Distance reference 1000 | 19 | 0.394 |
| Threshold 0.5 | 20 | — |
| Threshold 0.7 | 14 | — |
| Share 100%, all 5 dates | 18 | — |
| Fitted baseline instead of $0.15 | 24 | 0.514 |

The count ranges from 11 to 24 and the membership of the list is stable at its top. Note the direction of the last row: substituting the baseline fitted from the project's own competitive routes **raises** the count to 24, because that baseline is lower than the $0.15 assumption. The published figure of 18 is therefore the conservative one, and a critic arguing the baseline is too generous is arguing for a larger result.

---

## 9. The date standardizer, and why it is off

The tool implements an optional standardizer. For each date, take the competitive routes (3 or more airlines) and compute the median of fare ÷ FPB, call it `k_d`. Let `k_ref` be the median of `k_d` across dates. Multiply every fare on date `d` by `k_ref / k_d` before scoring, so a typical competitive route costs the same on every date and only route-specific movement survives.

**It is off in the locked configuration**, for three reasons:

1. It assumes lead-time effects move competitive and monopoly routes by the same proportion. That is an empirical claim this project cannot test, and monopoly routes may well be less lead-time sensitive.
2. It uses the same competitive routes the fitted baseline uses, so the two checks are not independent.
3. The result does not need it. The structural routes clear the threshold on all five dates, across a lead-time range of 14 to 45 days and a median fare range of $171 to $259. A correction for date-level movement cannot manufacture that.

Both raw and adjusted fares are kept in the tool's detail export for anyone who wants to run it.

---

## 10. Market comparison

> **Not used in the published study.** The Bengaluru comparison was dropped (README, "Why there is no Bengaluru comparison"). This section describes the method as designed, in case it is restarted with a source that prices every Indian airline.

Comparing two markets in dollars would be meaningless: Indian domestic fares sit far below US ones for reasons that have nothing to do with competitive structure. The comparison therefore uses **ratios and shares only**, never raw prices across markets:

- price per mile by airline count, within each market
- the ratio of thinnest-route to competitive price per mile, compared across markets
- rank correlation between distance and fare, within each market
- distance-band medians, and the short-to-long ratio
- structural counts under each market's own fitted baseline

The headline per-mile yardstick is country-specific: $0.15 with the $75 floor for the US, $0.09 with **no** floor for India. The floor is dropped because the median Bengaluru net fare in the sample is $82; a $75 floor would exceed the fare on short routes and swamp the index. Scored against the US yardstick instead, the 18 Bengaluru routes average −0.027 and nothing clears 0.6, which is an arithmetic consequence of the yardstick rather than a finding about either market.

Both ratios must be computed the same way for the cross-market number to mean anything. The comparison was to be reported as **thinnest airline count vs 3 or more airlines**. The single-date Bengaluru figure (1.15×) is withdrawn and should not be quoted against Atlanta's 4.17× (hand-collected) or 3.18× (scripted, bag-inclusive).

---

## 11. What is measured and what is excluded

**Measured:** cheapest nonstop, one-way, economy fare for one traveller; number of airlines operating that nonstop; great-circle distance between airport coordinates.

**Excluded:** connecting itineraries; round trips; premium cabins; seat and change fees; checked bags; schedule quality and time of day; aircraft type and capacity; seat or market share; load factors; actual airline costs.

**Carry-on bags** are excluded from the hand-collected data and from `no_bags/`, and included in `bags/`, where the scripted collection searched each route a second time with one carry-on added (README, Data collection).

Distance is great-circle, not flown distance. Flown distance is longer and varies with routing and weather, so every per-mile figure here is a slight overstatement, uniformly across routes.

---

## 12. Reproducing the figures

```bash
python3 analysis/admi.py                                          # hand-collected
python3 analysis/admi.py data/googleflights_2026-10-19/bags       # scripted, 1 carry-on
python3 analysis/admi.py data/googleflights_2026-10-19/no_bags    # scripted, no bags
```

No dependencies beyond the Python standard library. The script reads `data/raw/` (or the folder given), recomputes every figure in the README and in this document, and prints the stress-test table. Any discrepancy between a published number and this script's output should be treated as the published number being wrong.

---

## 13. Sources

| Figure used | Value | Source |
|---|---|---|
| US industry expense per available seat mile | 15.095¢, at 1 Apr 2025 | US DOT, *Standard Industry Fare Level Methodology*, Appendix A (Jan–Jun 2025 filing) |
| SIFL terminal charge | $58.95, Jul–Dec 2026 | US DOT SIFL rates, second half of calendar 2026 |
| SIFL per-mile rates | $0.3225 / $0.2459 / $0.2364 by distance band, Jul–Dec 2026 | as above |
| US domestic load factor | 82.4%, May 2026 | Bureau of Transportation Statistics, via FRED series LOADFACTORD |
| Fare effects of losing a route competitor | roughly 1–8% increase | GAO-26-107740, *Airline Competition*, 25 June 2026 |
| Concentration on thin routes | HHI up 5–8% on 4th/5th-quintile routes, 2007–2022; 58% of fifth-quintile routes had no effective low-cost competitor | GAO-26-107740 |
| Long-run fare trend | inflation-adjusted fares ~15% lower in 2024 than 2007; yields down ~19% | GAO-26-107740 |

### What the GAO report means for this project

GAO-26-107740 is the most relevant published work to ADMI's question, and it does not uniformly support the project's framing. It must be engaged with directly rather than cited selectively.

**Where it supports this work.** Concentration has risen specifically on the thinnest routes, and most of them have no low-cost competitor at all. That is the population ADMI's structural routes are drawn from.

**Where it complicates this work.** Inflation-adjusted domestic fares are about 15% lower than in 2007 and yields are down about 19%, so air travel as a whole has become cheaper, not more expensive. And the merger literature finds that removing a direct competitor raises fares by roughly 1 to 8 percent, while ADMI observes a 4.2× gap in price per mile between monopoly and competitive routes.

**These are not contradictory, and the difference must be stated.** The GAO figure is a *causal* estimate of what happens to a given route's fares when it loses a carrier. The ADMI figure is a *cross-sectional* comparison of different routes that differ in many ways besides competition — distance, aircraft size, demand density, seasonality. A route is thin and expensive for reasons that overlap with, but are not identical to, having one airline. Any claim that ADMI has measured the causal effect of monopoly would be contradicted by the published literature, and this project does not make that claim.
