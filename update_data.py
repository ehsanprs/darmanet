"""Refresh the website's offline database from darmanet.ir.

Usage:
    python update_data.py            # scrape fresh data (cached per day)
    python update_data.py --cached   # rebuild from the last downloaded pages
    python update_data.py --force    # write even if the row count drops a lot

Writes:
    site/data/centers.json   canonical database
    site/data/centers.js     same data as a script, so index.html works offline
                             when opened directly from disk (file://)
    site/data/darmanet_all_provinces.xlsx  (download link on the site)
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

from scrape_darmanet import BASE, CACHE, scrape, write_excel

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "site" / "data"

# The source data has a few city names in the province column.
PROVINCE_FIX = {"تبریز": "آذربایجان شرقی"}

AREA_CODES = {
    "آذربایجان شرقی": "041", "آذربایجان غربی": "044", "اردبیل": "045",
    "اصفهان": "031", "البرز": "026", "ایلام": "084", "بوشهر": "077",
    "تهران": "021", "چهارمحال و بختیاری": "038", "خراسان جنوبی": "056",
    "خراسان رضوی": "051", "خراسان شمالی": "058", "خوزستان": "061",
    "زنجان": "024", "سمنان": "023", "سیستان و بلوچستان": "054",
    "فارس": "071", "قزوین": "028", "قم": "025", "کردستان": "087",
    "کرمان": "034", "کرمانشاه": "083", "کهگیلویه و بویراحمد": "074",
    "گلستان": "017", "گیلان": "013", "لرستان": "066", "مازندران": "011",
    "مرکزی": "086", "هرمزگان": "076", "همدان": "081", "یزد": "035",
}

INSURERS = ["تامین اجتماعی", "خدمات درمانی", "نیروهای مسلح"]

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
POSTAL_RE = re.compile(r"[،,\-\s]*کد\s*پستی\s*[:：]?\s*(\d{10})")


def norm(text):
    if text is None:
        return ""
    text = text.replace("ي", "ی").replace("ك", "ک").translate(DIGITS)
    return " ".join(text.split())


def parse_phones(raw, province):
    """Turn messy phone text into a list of dialable 11-digit numbers.

    Handles missing leading zeros ("2122888011"), 8-digit local numbers,
    and suffix shorthand ("03532347090-9070" -> 03532349070).
    Excel-mangled values like "2.13E+11" are unrecoverable and give [].
    """
    if not raw or re.search(r"\d[.,]\d*E\+?\d", raw, re.I):
        return []
    numbers, prev, area = [], None, None
    for tok in re.findall(r"\d+", raw):
        if len(tok) == 3 and tok[0] == "0":
            area = tok
            continue
        if len(tok) == 10 and tok[0] != "0":
            tok = "0" + tok
        if len(tok) == 11 and tok[0] == "0":
            num = tok
        elif len(tok) == 8:
            code = area or (prev[:3] if prev and not prev.startswith("09") else None)
            code = code or AREA_CODES.get(province)
            if not code:
                continue
            num = code + tok
        elif prev and 1 <= len(tok) < 8:
            num = prev[:-len(tok)] + tok
        else:
            continue
        area = None
        if num not in numbers:
            numbers.append(num)
        prev = num
    return numbers[:5]


def parse_insurance(raw):
    """None = not stated, [] = accepts none, else list of insurer names."""
    raw = norm(raw).replace("نیرو های", "نیروهای")
    if not raw:
        return None
    if raw == "ندارد":
        return []
    return [i for i in INSURERS if i in raw]


def clean(headers, results):
    seen = {}
    for n in sorted(results):
        for row in results[n]:
            row = [norm(c) for c in row] + [""] * (9 - len(row))
            kind, name, province, city, phone, address, referral, ins, note = row[:9]
            if row[:9] == [norm(h) for h in headers][:9] or province == norm(headers[2]):
                continue
            if not name:
                continue
            province = PROVINCE_FIX.get(province, province)
            postal = None
            m = POSTAL_RE.search(address)
            if m:
                postal = m.group(1)
                address = POSTAL_RE.sub("", address).strip(" -،,")
            key = (kind, name, city, address)
            phones = parse_phones(phone, province)
            # The site lists most records twice; keep the copy with usable phones.
            if key in seen and len(seen[key]["phones"]) >= len(phones):
                continue
            seen[key] = {
                "id": hashlib.sha1("|".join(key).encode()).hexdigest()[:10],
                "type": kind,
                "name": name,
                "province": province,
                "city": city or province,
                "phones": phones,
                "phoneText": phone,
                "address": address,
                "postalCode": postal,
                "onlineReferral": {"دارد": True, "ندارد": False}.get(referral),
                "insurance": parse_insurance(ins),
                "note": note or None,
            }
    return sorted(seen.values(), key=lambda c: (c["province"], c["city"], c["type"], c["name"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cached", action="store_true",
                    help="reuse pages already in the cache folder")
    ap.add_argument("--force", action="store_true",
                    help="write even if far fewer centers were found than before")
    args = ap.parse_args()

    cache = CACHE if args.cached else CACHE / dt.date.today().isoformat()
    headers, results = scrape("all", cache)
    centers = clean(headers, results)

    json_path = DATA_DIR / "centers.json"
    if json_path.exists() and not args.force:
        old = json.loads(json_path.read_text(encoding="utf-8"))["meta"]["count"]
        if len(centers) < old * 0.7:
            sys.exit(f"Only {len(centers)} centers found (previously {old}). "
                     "The source site may have changed; nothing was written. "
                     "Re-run with --force to write anyway.")

    db = {
        "meta": {
            "updated": dt.datetime.now().isoformat(timespec="minutes"),
            "source": BASE,
            "count": len(centers),
        },
        "centers": centers,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(db, ensure_ascii=False, separators=(",", ":"))
    json_path.write_text(text, encoding="utf-8")
    (DATA_DIR / "centers.js").write_text(
        f"window.DARMANET_DB = {text};\n", encoding="utf-8")
    write_excel(DATA_DIR / "darmanet_all_provinces.xlsx", "all", headers, results)
    print(f"Database updated: {len(centers)} centers -> {json_path}")


if __name__ == "__main__":
    main()
