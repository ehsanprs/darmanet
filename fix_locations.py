"""Fix missing or doubtful map points by searching the center's NAME in Neshan.

Usage:
    python fix_locations.py --dry-run --limit 20   # show decisions, change nothing
    python fix_locations.py                         # fix every doubtful/missing point
    python fix_locations.py --retry                 # also retry centers searched before
    python fix_locations.py --by-address            # without the search service: look the
                                                    # ADDRESS up again, limited to the
                                                    # neighborhood it names

Which centers: no location, «احتمالاً نادرست» (far from their own neighborhood),
or «تقریبی» (shared point / city-center fallback). Manually fixed points are never
touched.

How a result is chosen (Neshan returns up to 30 places, nearest to the search
point first):
  1. the search starts where the center should be: the middle of the neighborhood
     named in its address if known, otherwise its current point or the city middle;
  2. only real places count (not streets or towns);
  3. the distinctive words of the name must match, after dropping generic words
     such as «کلینیک», «دکتر», «تصویربرداری» and the city name;
  4. the place must be near where the center should be, and the street names of
     our address in its address count in its favour;
  5. it is accepted only when it clearly beats the next candidate; otherwise the
     center is left as it is and listed in location_review.txt with its candidates.

Uses the Neshan search service (40 toman per request at the time of writing) and
the API key from .env (NESHAN_API_KEY=...).
"""
import argparse
import json
import math
import re
import statistics
import sys
import time
import urllib.parse

from db import ROOT, load, save, today
from geocode_data import (StopGeocoding, _norm, api_key, flag_wrong_area, km, learn_areas,
                          median_point, request)

SEARCH = "https://api.neshan.org/v3/search?q="
GEOCODE_V1 = "https://api.neshan.org/geocoding/v1?json="
REVERSE = "https://api.neshan.org/v5/reverse?lat={lat}&lng={lng}"
PAUSE = 0.6

# Words that say what kind of place it is, not which one.
GENERIC = set("""
مرکز کلینیک کلنیک درمانگاه آزمایشگاه تشخیص طبی پزشکی تخصصی فوق و شبانه روزی شبانه‌روزی دکتر
دندانپزشکی دندان پزشکی تصویربرداری رادیولوژی سونوگرافی فیزیوتراپی داروخانه بیمارستان پاتوبیولوژی
پاتولوژی عینک سازی عینکسازی اپتیک خیریه عمومی ع عج ره س حضرت جامع بخش موسسه شرکت مجتمع ساختمان
دهان فک صورت هسته ای ای‌ مطب متخصص اورژانس خدمات پرستاری منزل آندوسکوپی کولونوسکوپی گوارش جراحی محدود
قلب عروق ویژه دیجیتال تهران شعبه
""".split())

# Kinds of Neshan places that can be a health center (others are rejected).
NOT_HEALTH = re.compile(r"مسجد|مدرسه|پارک|بانک|رستوران|هتل|پمپ|اداره|دبستان|دبیرستان|فروشگاه|بازار|"
                        r"ایستگاه|پاسگاه|کلانتری|شهرداری|امامزاده|حسینیه|ورزشگاه|باشگاه")


def words(text):
    text = _norm(text).replace("(", " ").replace(")", " ")
    return [w for w in re.split(r"[\s\-–،,.:/«»\"']+", text) if w]


def core(name, city="", province=""):
    """Distinctive words of a center name."""
    skip = GENERIC | set(words(city)) | set(words(province))
    return [w for w in words(name) if w not in skip and len(w) >= 2 and not w.isdigit()]


def name_score(ours, theirs):
    """Share of our distinctive words found in the candidate's name (0..1)."""
    if not ours:
        return 0.0
    tw = words(theirs)

    def same(a, b):
        # Equal, or a long word with a short suffix ("پاستور"/"پاستوری"); never «آرین» for «آرینا».
        short, long_ = sorted((a, b), key=len)
        return a == b or (len(short) >= 5 and long_.startswith(short) and len(long_) - len(short) <= 2)

    def found(w):
        return any(same(w, t) for t in tw)

    return sum(found(w) for w in ours) / len(ours)


def street_words(address, city, province):
    skip = GENERIC | set(words(city)) | set(words(province)) | set(
        "خیابان خ بلوار میدان کوچه پلاک طبقه واحد نبش جنب روبروی بین بعد قبل از به نرسیده بالاتر "
        "پایین تر اول دوم سوم چهارم ابتدای انتهای شمالی جنوبی شرقی غربی کد پستی تقاطع سه راه چهارراه".split())
    return {w for w in words(address) if w not in skip and len(w) >= 3 and not w.isdigit()}


def where_to_search(c, known, areas_of, city_mid):
    """(point, radius km, how) describing where the center should be."""
    for a in areas_of.get(c["id"], []):
        if (c["province"], c["city"], a) in known:
            mid, spread = known[(c["province"], c["city"], a)]
            return mid, max(2.5, 3 * spread), f"neighborhood «{a}»"
    g = c.get("geocode", {})
    if c.get("location") and not g.get("suspect") and g.get("source") != "city-center":
        return c["location"], 3.0, "current approximate point"
    mid = city_mid.get((c["province"], c["city"]))
    if mid:
        return mid, 20.0 if c["city"] == "تهران" else 10.0, "city"
    return None, None, None


def search(key, term, point):
    body = {"term": term, "center": {"latitude": point["lat"], "longitude": point["lng"]}}
    data = request(key, SEARCH + urllib.parse.quote(json.dumps(body, ensure_ascii=False)))
    return (data or {}).get("items") or []


def judge(c, items, point, radius, how):
    """Pick the matching place, or explain why none was accepted."""
    ours = core(c["name"], c["city"], c["province"])
    streets = street_words(c["address"], c["city"], c["province"])
    cands = []
    for it in items:
        if it.get("category") != "place" or NOT_HEALTH.search(f"{it.get('type', '')} {it.get('title', '')}"):
            continue
        loc = it.get("location") or {}
        if "x" not in loc:
            continue
        p = {"lat": loc["y"], "lng": loc["x"]}
        ns = name_score(ours, it.get("title", ""))
        if ns < 0.75:
            continue
        d = km(p, point)
        addr_hits = len(streets & set(words(f"{it.get('address', '')} {it.get('neighbourhood', '')}")))
        city_level = how == "city"
        if d > radius or (city_level and not addr_hits and ns < 1):
            continue
        score = 2 * ns + min(addr_hits, 3) * 0.5 - d / max(radius, 1)
        cands.append((score, p, it, round(d, 2), addr_hits, ns))
    cands.sort(key=lambda x: -x[0])
    if not cands:
        return None, "no_match", []
    best = cands[0]
    if len(cands) > 1:
        second = cands[1]
        same_place = km(best[1], second[1]) < 0.15
        if not same_place and best[0] - second[0] < 0.5:
            return None, "ambiguous", cands[:3]
    return best, "ok", cands[:3]


# ---------- Address lookup limited to the neighborhood (no search service needed) ----------
def area_box(mid, radius):
    dlat = radius / 111.0
    dlng = radius / (111.0 * math.cos(math.radians(mid["lat"])))
    return {"southWest": {"latitude": mid["lat"] - dlat, "longitude": mid["lng"] - dlng},
            "northEast": {"latitude": mid["lat"] + dlat, "longitude": mid["lng"] + dlng}}


def geocode_in_area(key, c, mid, radius):
    """Neshan address results that lie inside the neighborhood: [(point, item)]."""
    body = {"address": c["address"], "province": c["province"], "city": c["city"],
            "location": {"latitude": mid["lat"], "longitude": mid["lng"]}, "extent": area_box(mid, radius)}
    data = request(key, GEOCODE_V1 + urllib.parse.quote(json.dumps(body, ensure_ascii=False)))
    out = []
    for it in (data or {}).get("items") or []:
        loc = it.get("location") or {}
        if "latitude" in loc:
            p = {"lat": loc["latitude"], "lng": loc["longitude"]}
            if km(p, mid) <= radius:
                out.append((p, it))
    return out


def street_level(c, item, area):
    """True when Neshan matched a street of the address, not just the neighborhood."""
    ours = street_words(c["address"], c["city"], c["province"]) - set(words(area))
    unmatched = set(words(item.get("unMatchedTerm") or ""))
    return any(w not in unmatched for w in ours)


def confirm(key, c, point, area):
    """Ask Neshan which street the point is on; compare with our address.

    Returns "street" if a street of our address is there, "area" if only the
    neighborhood matches, or None if neither does.
    """
    rev = request(key, REVERSE.format(lat=point["lat"], lng=point["lng"])) or {}
    there = set(words(" ".join(str(rev.get(k) or "") for k in
                               ("formatted_address", "route_name", "neighbourhood", "municipality_zone"))))
    ours = street_words(c["address"], c["city"], c["province"]) - set(words(area))
    if ours & there:
        return "street"
    return "area" if set(words(area)) <= there else None


def fix_by_address(args, key, db):
    active = [c for c in db["centers"] if not c.get("deleted")]
    known, areas_of = learn_areas(db)

    def area_of(c):
        for a in areas_of.get(c["id"], []):
            if (c["province"], c["city"], a) in known:
                return a, known[(c["province"], c["city"], a)]
        return None, None

    def eligible(c):
        g = c.get("geocode", {})
        if g.get("source") in ("manual", "neshan-search", "neshan-area"):
            return False
        if g.get("area_search") and not args.retry:
            return False
        bad = not c.get("location") or g.get("suspect") or g.get("approx")
        return bool(bad) and area_of(c)[0] is not None

    groups = {}
    for c in active:
        if eligible(c):
            groups.setdefault((c["province"], c["city"], c["address"]), []).append(c)

    def priority(group):  # worst first: misplaced, missing, city center, approximate
        g = group[0].get("geocode", {})
        return (0 if g.get("suspect") else 1 if not group[0].get("location")
                else 2 if g.get("source") == "city-center" else 3)

    ordered = sorted(groups.values(), key=priority)
    todo = ordered[: args.limit] if args.limit else ordered
    print(f"{len(todo)} addresses to look up inside their neighborhood (about {len(todo)} Neshan requests).")

    street = hood = kept = none = 0
    try:
        for i, group in enumerate(todo, 1):
            c = group[0]
            g = c.get("geocode", {})
            area, (mid, spread) = area_of(c)
            radius = max(2.5, 3 * spread)
            results = geocode_in_area(key, c, mid, radius)
            best = next(((p, it) for p, it in results if street_level(c, it, area)), None) or \
                (results[0] if results else None)
            # Neshan sometimes reports a full match for the wrong street, so every new
            # point is checked by asking which street it is actually on.
            found = confirm(key, c, best[0], area) if best else None
            badly_placed = g.get("suspect") or not c.get("location") or g.get("source") == "city-center"
            if found == "street":
                level = "street"
            elif best and found == "area" and badly_placed:
                # Only the neighborhood is right: still far better than a point in another
                # district, but not worth replacing a point that is already nearby.
                level = "neighborhood"
            elif g.get("suspect"):
                # Nothing confirmed: use the middle of the neighborhood the address names
                # (learned from the other centers there) instead of another unverified point.
                best = (mid, {})
                level = "neighborhood"
                found = "area-middle"
            else:
                best = None
                level = None
            moved = round(km(c["location"], best[0]), 2) if best and c.get("location") else None
            if args.dry_run:
                why = ("suspect" if g.get("suspect") else "missing" if not c.get("location")
                       else "city-center" if g.get("source") == "city-center" else "approximate")
                if best:
                    msg = f"FIX ({level}, confirmed: {found or 'no'}) moved {moved} km"
                else:
                    msg = "KEEP (not confirmed)" if results else "NO RESULT in neighborhood"
                print(f"[{i}] {c['name']} | {why} | «{area}» | {c['address'][:60]} | {msg}")
            if best:
                street += level == "street"
                hood += level != "street"
                if not args.dry_run:
                    for x in group:
                        x["location"] = {"lat": round(best[0]["lat"], 6), "lng": round(best[0]["lng"], 6)}
                        x["geocode"] = {"source": "neshan-area", "at": today(), "area": area,
                                        "approx": level != "street"}
            else:
                kept += bool(results)
                none += not results
                if not args.dry_run:
                    for x in group:
                        x.setdefault("geocode", {})["area_search"] = {
                            "at": today(), "result": "neighborhood_only" if results else "no_result"}
            if i % 50 == 0 and not args.dry_run:
                save(db)
                print(f"  {i}/{len(todo)} done")
            time.sleep(PAUSE)
    except StopGeocoding as e:
        print(f"\nStopped: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        if not args.dry_run:
            flag_wrong_area(db)
            save(db)
    print(f"Street-level fixes {street}, neighborhood-level fixes {hood}, kept as they were {kept}, "
          f"no result {none}.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, help="handle at most this many addresses")
    ap.add_argument("--dry-run", action="store_true", help="print decisions without saving")
    ap.add_argument("--retry", action="store_true", help="also retry centers searched before")
    ap.add_argument("--by-address", action="store_true",
                    help="look addresses up again inside their neighborhood (no search service needed)")
    args = ap.parse_args()
    key = api_key()
    db = load()
    if args.by_address:
        return fix_by_address(args, key, db)
    active = [c for c in db["centers"] if not c.get("deleted")]
    known, areas_of = learn_areas(db)
    by_city = {}
    for c in active:
        if c.get("location") and not c["geocode"].get("approx") and not c["geocode"].get("suspect"):
            by_city.setdefault((c["province"], c["city"]), []).append(c["location"])
    city_mid = {k: median_point(v) for k, v in by_city.items() if len(v) >= 3}

    def needs_fix(c):
        g = c.get("geocode", {})
        if g.get("source") in ("manual", "neshan-search"):
            return False
        if g.get("source") == "neshan-area" and not g.get("approx"):
            return False
        if g.get("search") and not args.retry:
            return False
        return not c.get("location") or g.get("suspect") or g.get("approx")

    groups = {}
    for c in active:
        if needs_fix(c) and core(c["name"], c["city"], c["province"]):
            groups.setdefault((c["province"], c["city"], c["name"], c["address"]), []).append(c)
    todo = list(groups.values())[: args.limit] if args.limit else list(groups.values())
    print(f"{len(todo)} centers to search (≈ {len(todo)} Neshan search requests).")

    fixed = unresolved = 0
    review = []
    try:
        for i, group in enumerate(todo, 1):
            c = group[0]
            point, radius, how = where_to_search(c, known, areas_of, city_mid)
            if not point:
                continue
            items = search(key, c["name"], point)
            best, verdict, top = judge(c, items, point, radius, how)
            moved = round(km(c["location"], best[1]), 2) if best and c.get("location") else None
            if args.dry_run or verdict != "ok":
                status = (f"FIX  -> «{best[2]['title']}» ({best[2].get('address', '')[:50]}) moved {moved} km"
                          if verdict == "ok" else verdict.upper())
                print(f"[{i}] {c['name']} | {c['city']} | search near {how} | {status}")
            if verdict == "ok":
                fixed += 1
                if not args.dry_run:
                    for x in group:
                        x["location"] = {"lat": round(best[1]["lat"], 6), "lng": round(best[1]["lng"], 6)}
                        x["geocode"] = {"source": "neshan-search", "at": today(), "match": best[2]["title"]}
            else:
                unresolved += 1
                review.append((c, verdict, top, how))
                if not args.dry_run:
                    for x in group:
                        x.setdefault("geocode", {})["search"] = {"at": today(), "result": verdict}
            if i % 50 == 0 and not args.dry_run:
                save(db)
                print(f"  {i}/{len(todo)} searched, {fixed} fixed")
            time.sleep(PAUSE)
    except StopGeocoding as e:
        print(f"\nStopped: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        if not args.dry_run:
            flag_wrong_area(db)
            save(db)
            lines = [f"Centers whose point could not be fixed automatically ({today()}):", ""]
            for c, verdict, top, how in review:
                lines.append(f"- {c['name']} | {c['type']} | {c['city']} | {c['address']} | id={c['id']} | {verdict}")
                for score, p, it, d, hits, ns in top:
                    lines.append(f"    candidate: «{it.get('title')}» {it.get('address', '')} "
                                 f"({p['lat']:.6f}, {p['lng']:.6f}) {d} km from expected")
            (ROOT / "location_review.txt").write_text("\n".join(lines), encoding="utf-8")
        print(f"Fixed {fixed}, not fixed {unresolved} (see location_review.txt).")


if __name__ == "__main__":
    sys.exit(main())
