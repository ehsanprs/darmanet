"""Download Tehran's 22 municipal district boundaries from OpenStreetMap.

Writes site/data/tehran_districts.json (GeoJSON, simplified to ~20 m) used to find
each center's district from its map point. Run again only if OSM boundaries change:
    .venv\\Scripts\\python make_districts.py

Uses OpenStreetMap's Nominatim service, which returns ready-made outlines for the
22 boundary relations «منطقه N شهر تهران» (admin_level 9) in one request.
Data: © OpenStreetMap contributors, ODbL.
"""
import json
import re
import urllib.request

from db import DATA_DIR

# OSM relation id of each district (منطقه ۱ ... منطقه ۲۲ شهر تهران).
RELATIONS = {
    1: 6728830, 2: 6728896, 3: 6728897, 4: 6728863, 5: 6729507, 6: 6729037, 7: 6729036,
    8: 6729035, 9: 6729508, 10: 6729501, 11: 6729111, 12: 6729112, 13: 6729034, 14: 6729033,
    15: 6729032, 16: 6729110, 17: 6729502, 18: 6729503, 19: 6729109, 20: 6729031, 21: 6729505,
    22: 6729506,
}
LOOKUP = "https://nominatim.openstreetmap.org/lookup?format=geojson&polygon_geojson=1&osm_ids="
TOLERANCE = 0.0002  # degrees (~20 m) for simplifying the outlines
FA = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")


def simplify(points, tol):
    """Douglas-Peucker line simplification."""
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = (dx * dx + dy * dy) ** 0.5 or 1e-12
    dists = [abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm for x, y in points[1:-1]]
    i = max(range(len(dists)), key=dists.__getitem__)
    if dists[i] <= tol:
        return [points[0], points[-1]]
    left = simplify(points[: i + 2], tol)
    return left[:-1] + simplify(points[i + 1:], tol)


def simplify_ring(ring, tol):
    """Simplify a closed ring: split it at its farthest point from the start, so the
    line-based simplification never sees a segment that starts and ends at one point."""
    x0, y0 = ring[0]
    k = max(range(len(ring)), key=lambda i: (ring[i][0] - x0) ** 2 + (ring[i][1] - y0) ** 2)
    return simplify(ring[: k + 1], tol)[:-1] + simplify(ring[k:], tol)


def main():
    url = LOOKUP + ",".join(f"R{r}" for r in RELATIONS.values())
    req = urllib.request.Request(url, headers={"User-Agent": "darmanet-site (github.com/ehsanprs/darmanet)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    features = []
    for f in data["features"]:
        n = int(re.search(r"منطقه\s*([۰-۹0-9]+)", f["properties"]["name"]).group(1).translate(FA))
        geom = f["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        polys = [[[[round(x, 5), round(y, 5)] for x, y in simplify_ring(ring, TOLERANCE)] for ring in poly]
                 for poly in polys]
        features.append({"type": "Feature", "properties": {"n": n, "name": f"منطقه {n}"},
                         "geometry": {"type": "MultiPolygon", "coordinates": polys}})
    features.sort(key=lambda f: f["properties"]["n"])
    assert [f["properties"]["n"] for f in features] == list(range(1, 23)), "expected districts 1-22"
    out = {"type": "FeatureCollection", "attribution": "© OpenStreetMap contributors, ODbL",
           "features": features}
    path = DATA_DIR / "tehran_districts.json"
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    pts = sum(len(r) for f in features for poly in f["geometry"]["coordinates"] for r in poly)
    print(f"{len(features)} districts, {pts} points, {path.stat().st_size // 1024} KB -> {path}")


if __name__ == "__main__":
    main()
