"""Find coordinates for centers that don't have them yet (Neshan geocoding).

Usage:
    python geocode_data.py                 # locate every center without coordinates
    python geocode_data.py --limit 50      # only 50 addresses (for a quick test)
    python geocode_data.py --retry-failed  # also retry addresses Neshan couldn't find before

The Neshan API key is read from the NESHAN_API_KEY environment variable or
from a local `.env` file (NESHAN_API_KEY=...), which is git-ignored.
Each address costs one "address to point" request (40 toman at the time of
writing); centers sharing an address reuse one result. Progress is saved
regularly, so the script can be stopped and re-run safely.
"""
import argparse
import json
import math
import statistics
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from db import ROOT, load, save, today

API = "https://api.neshan.org/v4/geocoding?address="
API_V1 = "https://api.neshan.org/geocoding/v1?json="
# A result farther than this from the other centers of its city is treated as a
# wrong match (Neshan sometimes picks a same-named street in another city).
MAX_KM = {"تهران": 40}
DEFAULT_MAX_KM = 25
PROVINCE_MAX_KM = 200
SHARED_POINT_MIN = 4  # this many different addresses on one point => approximate
IRAN = (24.5, 40.5, 43.5, 64.0)  # lat min/max, lng min/max
SAVE_EVERY = 50
PAUSE = 0.6


def api_key():
    key = os.environ.get("NESHAN_API_KEY")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "NESHAN_API_KEY":
                key = value.strip().strip('"').strip("'")
    if not key:
        sys.exit("No Neshan API key. Put NESHAN_API_KEY=your-key in a .env file next to this script.")
    return key


class StopGeocoding(Exception):
    pass


def request(key, url):
    """GET a Neshan URL; returns parsed JSON, or None when nothing is usable."""
    for _ in range(60):
        req = urllib.request.Request(url, headers={"Api-Key": key})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code == 482:  # short-term rate limit: wait and retry
                time.sleep(5)
                continue
            if e.code in (404, 470):  # nothing usable for this address
                return None
            raise StopGeocoding(f"Neshan returned HTTP {e.code}: {body}")
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  network error ({e}); retrying in 10s")
            time.sleep(10)
    raise StopGeocoding("Rate limit did not clear after several minutes.")


def in_iran(lat, lng):
    return IRAN[0] <= lat <= IRAN[1] and IRAN[2] <= lng <= IRAN[3]


def geocode(key, query):
    """Return (lat, lng), or None when Neshan finds nothing."""
    data = request(key, API + urllib.parse.quote(query))
    loc = (data or {}).get("location")
    if not loc or not in_iran(loc["y"], loc["x"]):
        return None
    return loc["y"], loc["x"]


def geocode_in_city(key, c):
    """Second attempt with the city and province given separately (geocoding v1)."""
    body = {"address": c["address"], "province": c["province"], "city": c["city"]}
    data = request(key, API_V1 + urllib.parse.quote(json.dumps(body, ensure_ascii=False)))
    for item in (data or {}).get("items") or []:
        loc = item.get("location") or {}
        if item.get("city") == c["city"] and in_iran(loc.get("latitude", 0), loc.get("longitude", 0)):
            return loc["latitude"], loc["longitude"]
    return None


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a["lat"], a["lng"], b["lat"], b["lng"]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def median_point(points):
    return {"lat": round(statistics.median(p["lat"] for p in points), 6),
            "lng": round(statistics.median(p["lng"] for p in points), 6)}


def validate(db, key):
    """Fix results that landed far from their city, and flag approximate points."""
    active = [c for c in db["centers"] if not c.get("deleted") and c.get("location")]
    by_city, by_province = {}, {}
    for c in active:
        by_city.setdefault((c["province"], c["city"]), []).append(c)
        by_province.setdefault(c["province"], []).append(c)
    city_mid = {k: median_point([c["location"] for c in g]) for k, g in by_city.items() if len(g) >= 3}
    prov_mid = {k: median_point([c["location"] for c in g]) for k, g in by_province.items()}

    def misplaced(c, loc):
        mid = city_mid.get((c["province"], c["city"]))
        if mid:
            return km(loc, mid) > MAX_KM.get(c["city"], DEFAULT_MAX_KM)
        return km(loc, prov_mid[c["province"]]) > PROVINCE_MAX_KM

    groups = {}
    for c in active:
        if c.get("geocode", {}).get("source") == "neshan" and misplaced(c, c["location"]):
            groups.setdefault(address_key(c), []).append(c)
    if groups:
        print(f"Re-checking {len(groups)} addresses that landed outside their city "
              f"(≈ {len(groups)} requests)...")
    fixed = fallback = 0
    for group in groups.values():
        result = geocode_in_city(key, group[0])
        loc = {"lat": round(result[0], 6), "lng": round(result[1], 6)} if result else None
        good = loc is not None and not misplaced(group[0], loc)
        for c in group:
            if good:
                c["location"] = loc
                c["geocode"] = {"source": "neshan-city", "at": today()}
            else:
                c["location"] = city_mid.get((c["province"], c["city"])) or prov_mid[c["province"]]
                c["geocode"] = {"source": "city-center", "approx": True, "at": today()}
        fixed += good
        fallback += not good
        time.sleep(PAUSE)

    # Many different addresses on one exact point: Neshan only matched a street or area.
    addresses = {}
    for c in active:
        addresses.setdefault((c["location"]["lat"], c["location"]["lng"]), set()).add(c["address"])
    approx = 0
    for c in active:
        if len(addresses[(c["location"]["lat"], c["location"]["lng"])]) >= SHARED_POINT_MIN:
            c["geocode"]["approx"] = True
        approx += bool(c["geocode"].get("approx"))
    print(f"Validation: {fixed} wrong-city results fixed, {fallback} moved to their city center, "
          f"{approx} centers marked approximate.")


def address_key(c):
    return (c["province"], c["city"], c["address"])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, help="geocode at most this many addresses")
    ap.add_argument("--retry-failed", action="store_true",
                    help="retry addresses that were not found in a previous run")
    args = ap.parse_args()
    key = api_key()
    db = load()
    centers = db["centers"]

    known = {}
    for c in centers:
        if c.get("location"):
            known.setdefault(address_key(c), c["location"])

    def wanted(c):
        if c.get("deleted") or c.get("location"):
            return False
        return args.retry_failed or c.get("geocode", {}).get("status") != "not_found"

    groups = {}
    for c in centers:
        if wanted(c):
            groups.setdefault(address_key(c), []).append(c)

    reused = 0
    for k in [k for k in groups if k in known]:
        for c in groups.pop(k):
            c["location"] = known[k]
            c["geocode"] = {"source": "reused", "at": today()}
            reused += 1

    todo = list(groups.items())[: args.limit] if args.limit else list(groups.items())
    print(f"{len(todo)} addresses to look up (≈ {len(todo)} Neshan requests); "
          f"{reused} centers reused an existing location.")

    found = missing = 0
    started = time.time()
    try:
        for i, ((province, city, address), group) in enumerate(todo, 1):
            query = address if city in address else f"{city} {address}"
            if province not in query:
                query = f"{province} {query}"
            result = geocode(key, query)
            for c in group:
                if result:
                    c["location"] = {"lat": round(result[0], 6), "lng": round(result[1], 6)}
                    c["geocode"] = {"source": "neshan", "at": today()}
                else:
                    c["geocode"] = {"status": "not_found", "at": today()}
            found += bool(result)
            missing += not result
            if i % SAVE_EVERY == 0:
                save(db)
                rate = i / (time.time() - started)
                eta = (len(todo) - i) / rate / 60
                print(f"  {i}/{len(todo)} done ({found} found, {missing} not found), ~{eta:.0f} min left")
            time.sleep(PAUSE)
        validate(db, key)
    except StopGeocoding as e:
        print(f"\nStopped: {e}")
        print("Progress so far is saved. Top up the Neshan credit or check the key, then run again.")
    except KeyboardInterrupt:
        print("\nInterrupted; saving progress.")
    finally:
        save(db)
        active = [c for c in centers if not c.get("deleted")]
        located = sum(1 for c in active if c.get("location"))
        print(f"This run: {found} found, {missing} not found, {reused} reused. "
              f"Total located: {located}/{len(active)} active centers.")


if __name__ == "__main__":
    main()
