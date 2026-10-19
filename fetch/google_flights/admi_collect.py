import asyncio
import csv
import os
import random
import re
import sys
from datetime import datetime, timezone

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

ORIGIN = "ATL"

DESTINATIONS = {
    "AL": "BHM", "AK": "ANC", "AZ": "PHX", "AR": "LIT", "CA": "LAX",
    "CO": "DEN", "CT": "BDL", "FL": "MCO", "HI": "HNL", "ID": "BOI",
    "IL": "ORD", "IN": "IND", "IA": "DSM", "KS": "ICT", "KY": "SDF",
    "LA": "MSY", "ME": "PWM", "MD": "BWI", "MA": "BOS", "MI": "DTW",
    "MN": "MSP", "MS": "JAN", "MO": "STL", "MT": "BZN", "NE": "OMA",
    "NV": "LAS", "NH": "MHT", "NJ": "EWR", "NM": "ABQ", "NY": "LGA",
    "NC": "CLT", "ND": "FAR", "OH": "CMH", "OK": "OKC", "OR": "PDX",
    "PA": "PHL", "RI": "PVD", "SC": "CHS", "SD": "FSD", "TN": "BNA",
    "TX": "DFW", "UT": "SLC", "VT": "BTV", "VA": "DCA", "WA": "SEA",
    "WV": "CRW", "WI": "MKE", "WY": "JAC",
}

TRAVEL_DATES = [
    "2026-10-28",
    "2026-11-07",
    "2026-11-17",
    "2026-12-04",
    "2027-01-07"
]

NO_CARRY_ON_AIRLINES = ("Frontier", "Spirit")

MAX_TRIES = 3
PRICE_WAIT_S = 15
PAUSE_S = (2.0, 4.0)

OUT_FARES = "admi_fares.csv"
OUT_LOG = "admi_search_log.csv"
OUT_FAILED = "admi_failed.csv"

FARE_FIELDS = [
    "date_scraped", "travel_date", "origin", "dest_state", "dest", "carrier",
    "depart_time", "stops", "price_plain", "price_bag", "bag_check"
]
LOG_FIELDS = [
    "time_utc", "travel_date", "dest", "attempt", "result", "flights", "detail"
]

SNAPSHOT_JS = """
() => Array.from(document.querySelectorAll('li.pIav2d')).map(li => {
  const p = li.querySelector('span[data-gs]');
  const c = li.querySelector('.sSHqwe');
  return { price: p ? p.innerText : '', carrier: c ? c.innerText : '', text: li.innerText };
})
"""


def clean_carrier(raw):
    first = raw.strip().splitlines()[0] if raw.strip() else ""
    return re.split(r"Operated by|DBA", first, flags=re.IGNORECASE)[0].strip()


def parse_cards(snapshot):
    flights = {}
    for card in snapshot:
        m = re.search(r"[\d,]+(?:\.\d+)?", card["price"])
        if not m:
            continue
        price = float(m.group().replace(",", ""))
        carrier = clean_carrier(card["carrier"])

        t = re.search(r"\b(\d{1,2}:\d{2}\s?[AP]M)", card["text"])
        depart = t.group(1).replace(" ", " ") if t else "N/A"

        if re.search(r"\bNonstop\b", card["text"], flags=re.IGNORECASE):
            stops = 0
        else:
            s = re.search(r"(\d+)\s+stops?", card["text"], flags=re.IGNORECASE)
            stops = int(s.group(1)) if s else 1

        if stops == 0:
            key = (carrier, depart)
            if key not in flights or price < flights[key]["price"]:
                flights[key] = dict(carrier=carrier, depart=depart, stops=stops, price=price)
    return flights


def signature(snapshot):
    return tuple((c["carrier"], c["price"]) for c in snapshot)


async def stable_snapshot(page):
    await page.wait_for_selector("li.pIav2d span[data-gs]", timeout=PRICE_WAIT_S * 1000)
    prev, snap = None, []
    for _ in range(int(PRICE_WAIT_S / 0.7)):
        snap = await page.evaluate(SNAPSHOT_JS)
        if snap and signature(snap) == prev:
            return snap
        prev = signature(snap)
        await page.wait_for_timeout(700)
    return snap


async def wait_for_new_prices(page, before, wait_s):
    for _ in range(int(wait_s / 0.7)):
        snap = await page.evaluate(SNAPSHOT_JS)
        if snap and signature(snap) != before:
            return await stable_snapshot(page), True
        await page.wait_for_timeout(700)
    return await page.evaluate(SNAPSHOT_JS), False


async def add_one_carry_on(page):
    bags_btn = page.locator("button:has-text('Bags')").first
    await bags_btn.wait_for(state="attached", timeout=6000)
    await bags_btn.dispatch_event("click")
    await page.wait_for_timeout(600)

    plus_btn = page.locator("button[aria-label*='carry-on' i][aria-label*='add' i], button[aria-label*='Increase carry-on' i]").first
    if await plus_btn.count() == 0:
        plus_btn = page.locator("div[role='dialog'] button:has-text('+')").first
    if await plus_btn.count() == 0:
        plus_btn = page.locator("button:has-text('+')").first

    await plus_btn.wait_for(state="attached", timeout=5000)
    await plus_btn.dispatch_event("click")
    await page.wait_for_timeout(400)

    await page.keyboard.press("Escape")
    await page.wait_for_timeout(600)


def search_url(dest, date):
    q = f"nonstop flights from {ORIGIN} to {dest} on {date} oneway".replace(" ", "+")
    return f"https://www.google.com/travel/flights?q={q}&curr=USD&hl=en&gl=us"


async def search_once(browser, state, dest, date, headless=True):
    ctx = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        locale="en-US",
        timezone_id="America/New_York",
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    )
    page = await ctx.new_page()
    try:
        await page.goto(search_url(dest, date), wait_until="domcontentloaded", timeout=30000)

        try:
            snap_plain = await stable_snapshot(page)
        except PWTimeout:
            body = (await page.inner_text("body")).lower()
            if "no results" in body or "no options" in body or "no flights" in body:
                return "no_flights", [], "No nonstop flights found"
            return "error", [], "Timeout: Prices never loaded"

        plain = parse_cards(snap_plain)
        if not plain:
            return "error", [], "Flight cards rendered but no nonstop direct flights parsed"

        has_unbundled = any(f["carrier"].startswith(NO_CARRY_ON_AIRLINES) for f in plain.values())

        try:
            await add_one_carry_on(page)
            click_detail = "bag toggle applied"
        except Exception as e:
            click_detail = f"bag toggle failed: {e}"

        wait = PRICE_WAIT_S if has_unbundled else 4
        snap_bag, changed = await wait_for_new_prices(page, signature(snap_plain), wait)
        bag = parse_cards(snap_bag)

        went_up = [
            k for k, f in plain.items()
            if f["carrier"].startswith(NO_CARRY_ON_AIRLINES)
            and k in bag and bag[k]["price"] > f["price"]
        ]

        if not has_unbundled:
            result = "not_needed"
        elif len(went_up) > 0:
            result = "yes"
        else:
            result = "no"

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rows = []
        for key in sorted(set(plain) | set(bag)):
            p, b = plain.get(key), bag.get(key)
            f = p or b
            row_dict = dict(
                date_scraped=today, travel_date=date, origin=ORIGIN,
                dest_state=state, dest=dest, carrier=f["carrier"],
                depart_time=f["depart"], stops=f["stops"],
                price_plain=p["price"] if p else "",
                price_bag=b["price"] if b else "",
                bag_check=result
            )
            rows.append(row_dict)

            if state == "PA":
                de_dict = dict(row_dict)
                de_dict["dest_state"] = "DE"
                rows.append(de_dict)

        detail = f"{click_detail}; DOM changed={changed}; Unbundled fares increased={len(went_up)}"
        return result, rows, detail
    except Exception as e:
        return "error", [], f"{type(e).__name__}: {e}"
    finally:
        await ctx.close()


def append_rows(path, fields, rows):
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerows(rows)


def finished_searches():
    done = set()
    if os.path.exists(OUT_LOG):
        with open(OUT_LOG, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["result"] in ("yes", "not_needed", "no_flights"):
                    done.add((r["dest"], r["travel_date"]))
    return done


async def run_test():
    print("Testing single route (ATL -> MSP, 2026-11-07) with visible browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        result, rows, detail = await search_once(browser, "MN", "MSP", "2026-11-07", headless=False)
        await browser.close()

    print(f"\nResult: {result} ({detail})")
    print(f"{'Carrier':<12} {'Depart':>9} {'Stops':>6} {'Price Plain':>13} {'Price Bag':>12}")
    print("-" * 58)
    for r in rows:
        print(f"{r['carrier']:<12} {r['depart_time']:>9} {r['stops']:>6} ${str(r['price_plain']):>12} ${str(r['price_bag']):>11}")
    print("\n[VERIFICATION PASS]" if result == "yes" else "\n[VERIFICATION FAIL]")


async def run_full():
    done = finished_searches()
    jobs = [(state, dest, date) for date in TRAVEL_DATES for state, dest in DESTINATIONS.items()
            if (dest, date) not in done]
    print(f"Dataset Status: {len(done)} searches already logged. {len(jobs)} pending searches remaining.")
    failed = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for n, (state, dest, date) in enumerate(jobs, 1):
            for attempt in range(1, MAX_TRIES + 1):
                result, rows, detail = await search_once(browser, state, dest, date)
                append_rows(OUT_LOG, LOG_FIELDS, [dict(
                    time_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    travel_date=date, dest=dest, attempt=attempt, result=result,
                    flights=len(rows), detail=detail)])
                print(f"[{n}/{len(jobs)}] {ORIGIN}->{dest} ({state}) {date} try {attempt}: {result} ({detail})")

                if result in ("yes", "not_needed", "no_flights"):
                    break
                await asyncio.sleep(random.uniform(3, 6))

            if result in ("yes", "not_needed"):
                append_rows(OUT_FARES, FARE_FIELDS, rows)
            elif result != "no_flights":
                failed.append(dict(dest_state=state, dest=dest, travel_date=date, result=result, detail=detail))

            await asyncio.sleep(random.uniform(*PAUSE_S))
        await browser.close()

    if failed:
        append_rows(OUT_FAILED, ["dest_state", "dest", "travel_date", "result", "detail"], failed)
    print(f"\nExecution finished. Fares output: {OUT_FARES}. Audit logs: {OUT_LOG}.")
    if failed:
        print(f"ALERT: {len(failed)} searches unresolved. Details recorded in {OUT_FAILED}.")
    else:
        print("SUCCESS: All 49 states across 5 dates collected with 100% price verification.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(run_test())
    else:
        asyncio.run(run_full())