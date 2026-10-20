"""Which Tehran municipal district (منطقه ۱ تا ۲۲) a point is in.

Uses the OpenStreetMap boundaries in site/data/tehran_districts.json (make_districts.py).
"""
import json
from functools import lru_cache

from db import DATA_DIR

PATH = DATA_DIR / "tehran_districts.json"


@lru_cache(maxsize=1)
def _districts():
    if not PATH.exists():
        return []
    data = json.loads(PATH.read_text(encoding="utf-8"))
    out = []
    for f in data["features"]:
        polys = f["geometry"]["coordinates"]
        xs = [x for poly in polys for ring in poly for x, _ in ring]
        ys = [y for poly in polys for ring in poly for _, y in ring]
        out.append((f["properties"]["n"], polys, (min(xs), min(ys), max(xs), max(ys))))
    return out


def _inside(x, y, ring):
    """Ray casting: is (x, y) inside the ring?"""
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def district_of(lat, lng):
    """District number 1-22, or None if the point is outside Tehran's districts."""
    for n, polys, (x0, y0, x1, y1) in _districts():
        if not (x0 <= lng <= x1 and y0 <= lat <= y1):
            continue
        for poly in polys:
            if _inside(lng, lat, poly[0]) and not any(_inside(lng, lat, hole) for hole in poly[1:]):
                return n
    return None


def is_tehran_city(c):
    return c.get("province") == "تهران" and c.get("city") == "تهران"


def assign(centers):
    """Set c["district"] for centers in the city of Tehran from their map point."""
    if not _districts():
        return
    for c in centers:
        if is_tehran_city(c) and c.get("location"):
            c["district"] = district_of(c["location"]["lat"], c["location"]["lng"])
        else:
            c.pop("district", None)


def review(db):
    """Tehran centers whose district is doubtful, for checking in admin mode."""
    from collections import Counter

    from geocode_data import _norm, address_areas

    teh = [c for c in db["centers"] if not c.get("deleted") and is_tehran_city(c)]
    city_names = {_norm(c["city"]) for c in db["centers"]} | {_norm(c["province"]) for c in db["centers"]}
    by_area = {}
    for c in teh:
        if c.get("district"):
            for a in address_areas(c, city_names)[:1]:
                by_area.setdefault(a, Counter())[c["district"]] += 1
    rows = []
    for c in teh:
        g = c.get("geocode") or {}
        if g.get("source") == "manual" and c.get("district"):
            continue
        why = None
        if not c.get("location"):
            why = "no map point"
        elif not c.get("district"):
            why = "point is outside Tehran's 22 districts"
        elif g.get("suspect"):
            why = f"point possibly misplaced (far from «{g['suspect']['area']}»)"
        else:
            area = next(iter(address_areas(c, city_names)[:1]), None)
            votes = by_area.get(area)
            if votes and sum(votes.values()) >= 5:
                top, n = votes.most_common(1)[0]
                if top != c["district"] and n / sum(votes.values()) >= 0.75:
                    why = f"address says «{area}», where most centers are in district {top}"
        if why:
            rows.append(f"- {c['name']} | {c['address']} | district {c.get('district') or '-'} | {why} | id={c['id']}")
    return rows


if __name__ == "__main__":
    from db import ROOT, load

    rows = review(load())
    (ROOT / "district_review.txt").write_text(
        "Tehran centers whose district should be checked (fix the point in admin mode):\n\n" + "\n".join(rows),
        encoding="utf-8")
    print(f"{len(rows)} centers to check -> district_review.txt")
