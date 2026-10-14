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

**The $0.15 rate** is an assumption, not a measured value. Published figures for US domestic cost per available seat mile cluster in a range that supports $0.15 to $0.20; $0.15 is chosen as the conservative end, because a lower baseline makes fewer routes look distorted. *This figure still needs a citation; see LIMITATIONS.md.*

**The $75 floor** exists because a flight has costs that do not shrink with distance: crew, gate, turnaround, ground handling. Without it, the 134-mile Atlanta to Birmingham route has a fair price of $20, and any real fare scores as extreme distortion. Every short monopoly route would then pile up near 1.0 and the index would be measuring distance, not competition. The floor only affects routes shorter than 500 miles, where `miles × 0.15 < 75`.

The $75 value is an assumption about what a nonstop costs to operate before distance enters. It is **not** estimated from this data. For a sense of scale, an OLS line through Atlanta fares on routes with 3 or more airlines gives:

```
FPB_fitted = $12.3 + $0.0827 × miles      (n = 74)
```

That implies competitive routes price near $0.083 per mile, roughly half the $0.15 assumption, with a fixed part near $12. The fixed part is poorly identified because there are too few short competitive routes in the sample to pin it down, which is exactly why the floor is set by assumption rather than fitted. Results are reported with the floor on and off, and with the fitted line substituted entirely (see §8).

### An alternative that was tried and rejected

An earlier draft used a **distance-tapered** baseline, `0.15 × (d/900)^−0.5` per mile, so that the per-mile rate fell with distance. It was dropped for two reasons. It conflates the fixed-cost effect with the distance effect in one term, making the result hard to interpret; and a flat rate plus an explicit floor states the same intuition with one assumption instead of an exponent. Anyone wanting to compare should add it to `STRESS_TESTS` rather than to `LOCKED`. **Any figure computed under the tapered baseline is not comparable to the figures in this repository.**

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

**United States** — 7.5% federal excise tax on the base fare, $5.60 September 11th Security Fee per one-way trip, $4.50 Passenger Facility Charge per enplanement:

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

Comparing two markets in dollars would be meaningless: Indian domestic fares sit far below US ones for reasons that have nothing to do with competitive structure. The comparison therefore uses **ratios and shares only**, never raw prices across markets:

- price per mile by airline count, within each market
- the ratio of thinnest-route to competitive price per mile, compared across markets
- rank correlation between distance and fare, within each market
- distance-band medians, and the short-to-long ratio
- structural counts under each market's own fitted baseline

The headline per-mile yardstick is country-specific: $0.15 with the $75 floor for the US, $0.09 with **no** floor for India. The floor is dropped because the median Bengaluru net fare in the sample is $82; a $75 floor would exceed the fare on short routes and swamp the index. Scored against the US yardstick instead, the 18 Bengaluru routes average −0.027 and nothing clears 0.6, which is an arithmetic consequence of the yardstick rather than a finding about either market.

Both ratios must be computed the same way for the cross-market number to mean anything. The reported comparison is **thinnest airline count vs 3 or more airlines**: 4.17× at Atlanta, 1.15× at Bengaluru.

---

## 11. What is measured and what is excluded

**Measured:** cheapest nonstop, one-way, economy fare for one traveller; number of airlines operating that nonstop; great-circle distance between airport coordinates.

**Excluded:** connecting itineraries; round trips; premium cabins; bag, seat and change fees; schedule quality and time of day; aircraft type and capacity; seat or market share; load factors; actual airline costs.

Distance is great-circle, not flown distance. Flown distance is longer and varies with routing and weather, so every per-mile figure here is a slight overstatement, uniformly across routes.

---

## 12. Reproducing the figures

```bash
python3 analysis/admi.py
```

No dependencies beyond the Python standard library. The script reads `data/raw/`, recomputes every figure in the README and in this document, and prints the stress-test table. Any discrepancy between a published number and this script's output should be treated as the published number being wrong.
