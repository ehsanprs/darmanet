"""Visitor-oriented categories and services for health centers.

The source only gives a broad "type" (e.g. تصویربرداری). Here every center gets:
  categories  primary category (from its type) + any other category one of its
              detected services belongs to (e.g. a درمانگاه offering اکو also
              appears under قلب و عروق)
  services    specific services found in its name / description
  allDay      open 24 hours (شبانه‌روزی)

Detection is keyword-based on name + description. Rules can be checked with the
report written by update_data.py, and individual centers fixed in overrides.json.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

L = r"(?<![؀-ۿA-Za-z])"  # left word boundary that also works for Persian

# Service fields:
#   key, label, pattern (regex, matched after a word boundary)
#   syn     extra search words for the website
#   within  categories whose centers are checked for it (default: its own)
#   "*"     check every center; a match also lists the center in this category
#   hidden  used for cross-listing only, no filter chip
CATEGORIES = [
    {"key": "dental", "label": "دندانپزشکی", "icon": "tooth", "color": "#0891b2",
     "types": ["دندانپزشکی"],
     "services": [
         {"key": "orthodontics", "label": "ارتودنسی", "pattern": r"ارتودنس", "syn": ["ارتو"]},
         {"key": "implant", "label": "ایمپلنت", "pattern": r"ایمپلنت"},
         {"key": "kids_dentistry", "label": "دندانپزشکی کودکان", "pattern": r"کودک|اطفال"},
         {"key": "oral_surgery", "label": "جراحی دهان و لثه", "pattern": r"جراحی|لثه|پریو", "syn": ["جراح"]},
         {"key": "dentistry", "label": "دندانپزشکی", "pattern": r"دندان", "within": ["clinic"],
          "cross": True, "hidden": True},
     ]},
    {"key": "lab", "label": "آزمایشگاه", "icon": "flask", "color": "#7c3aed",
     "types": ["آزمایشگاه"],
     "services": [
         {"key": "pathology", "label": "پاتولوژی (نمونه‌برداری)", "pattern": r"پاتولوژ|آسیب\s*شناس",
          "syn": ["بیوپسی", "نمونه برداری"]},
         {"key": "genetics", "label": "ژنتیک", "pattern": r"ژنتیک", "syn": ["آزمایش ژنتیک"]},
     ]},
    {"key": "imaging", "label": "تصویربرداری", "icon": "scan", "color": "#2563eb",
     "types": ["تصویربرداری"],
     "services": [
         {"key": "ultrasound", "label": "سونوگرافی", "pattern": r"سونو|سنوگراف", "within": "*",
          "syn": ["سونو", "سنوگرافی", "اولتراسوند"]},
         {"key": "xray", "label": "رادیولوژی", "pattern": r"رادیولوژ|رادیوگراف|ایکس\s*ری|x-?ray",
          "syn": ["عکس", "عکسبرداری", "رادیوگرافی"]},
         {"key": "mri", "label": "MRI", "pattern": r"ام\s*\.?\s*آر\s*\.?\s*آی|ام\s*ار\s*ای|mri|مغناطیس",
          "within": "*", "syn": ["ام آر آی", "ام ار ای", "تصویربرداری مغناطیسی"]},
         {"key": "ct", "label": "سی‌تی‌اسکن", "pattern": r"سی\s*تی(?!ر)|ct(?![a-z])", "within": "*",
          "syn": ["سی تی", "سیتی اسکن", "ct scan"]},
         {"key": "mammography", "label": "ماموگرافی", "pattern": r"ماموگراف", "within": "*"},
         {"key": "bone_density", "label": "تراکم استخوان", "pattern": r"تراکم|دانسیتومتر", "within": "*",
          "syn": ["سنجش تراکم"]},
         {"key": "nuclear", "label": "پزشکی هسته‌ای", "pattern": r"هسته\s*ای|اسکن\s*هسته", "within": "*",
          "syn": ["اسکن استخوان", "هسته ای"]},
         {"key": "dental_imaging", "label": "رادیولوژی دهان و فک",
          "pattern": r"فک|دهان|دندان|opg|cbct|پانورکس|پانورامیک|سفالومتر",
          "syn": ["او پی جی", "opg", "cbct", "عکس دندان", "پانورکس"]},
     ]},
    {"key": "clinic", "label": "درمانگاه و مطب", "icon": "stetho", "color": "#0d9488",
     "types": ["درمانگاه", "کلینیک", "مطب"],
     "services": [
         {"key": "internal", "label": "داخلی", "pattern": r"داخلی"},
         {"key": "women", "label": "زنان و زایمان", "pattern": r"زنان|زایمان|مامایی"},
         {"key": "kids", "label": "کودکان", "pattern": r"کودک|اطفال"},
         {"key": "skin", "label": "پوست و مو", "pattern": r"پوست|زیبایی", "syn": ["لیزر"]},
         {"key": "orthopedics", "label": "ارتوپدی", "pattern": r"ارتوپد"},
         {"key": "psychiatry", "label": "اعصاب و روان", "pattern": r"اعصاب\s*و\s*روان|روانپزشک|روان\s*شناس",
          "syn": ["مشاوره", "روانپزشکی"]},
         {"key": "ent", "label": "گوش و حلق و بینی", "pattern": r"گوش\s*[،,و]?\s*حلق"},
         {"key": "urology", "label": "کلیه و مجاری ادرار", "pattern": r"ارولوژ|اورولوژ|کلیه"},
         {"key": "diabetes", "label": "دیابت", "pattern": r"دیابت"},
         {"key": "addiction", "label": "ترک اعتیاد", "pattern": r"اعتیاد|متادون"},
     ]},
    {"key": "rehab", "label": "فیزیوتراپی و توانبخشی", "icon": "activity", "color": "#16a34a",
     "types": ["فیزیوتراپی"],
     "services": [
         {"key": "physio", "label": "فیزیوتراپی", "pattern": r"فیزیوتراپ"},
         {"key": "occupational", "label": "کاردرمانی", "pattern": r"کار\s*درمان", "within": "*"},
         {"key": "speech", "label": "گفتاردرمانی", "pattern": r"گفتار\s*درمان", "within": "*"},
         {"key": "audiology", "label": "شنوایی‌سنجی", "pattern": r"شنوایی|ادیومتر|ادیولوژیست|سمعک", "within": "*",
          "syn": ["سمعک", "ادیومتری"]},
     ]},
    {"key": "pharmacy", "label": "داروخانه", "icon": "pill", "color": "#db2777",
     "types": ["داروخانه"], "services": []},
    {"key": "hospital", "label": "بیمارستان", "icon": "hospital", "color": "#dc2626",
     "types": ["بیمارستان"],
     "services": []},
    {"key": "heart", "label": "قلب و عروق", "icon": "heart", "color": "#e11d48",
     "types": ["کلینیک قلب"],
     "services": [
         {"key": "heart_visit", "label": "ویزیت متخصص قلب", "pattern": r"قلب\s*و\s*عروق|متخصص\s*قلب|کاردیولوژ",
          "within": ["clinic", "heart"], "cross": True, "syn": ["متخصص قلب", "قلب و عروق"]},
         {"key": "echo", "label": "اکوکاردیوگرافی", "pattern": r"اکو(?!\s*سیستم)|echo", "within": "*",
          "syn": ["اکو", "اکوی قلب"]},
         {"key": "ecg", "label": "نوار قلب", "pattern": r"نوار\s*قلب|ecg|ekg", "within": "*",
          "syn": ["الکتروکاردیوگرام"]},
         {"key": "stress_test", "label": "تست ورزش", "pattern": r"تست\s*ورزش", "within": "*"},
         {"key": "holter", "label": "هولتر", "pattern": r"هولتر", "within": "*"},
     ]},
    {"key": "eye", "label": "چشم و بینایی", "icon": "glasses", "color": "#9333ea",
     "types": ["عینک سازی"],
     "services": [
         {"key": "optician", "label": "عینک‌سازی", "pattern": r"عینک", "syn": ["اپتیک"]},
         {"key": "optometry", "label": "بینایی‌سنجی", "pattern": r"بینایی\s*سنج|اپتومتر", "within": "*"},
         {"key": "ophthalmology", "label": "چشم‌پزشکی", "pattern": r"چشم", "within": "*"},
         {"key": "eye_surgery", "label": "لیزیک و جراحی چشم",
          "pattern": r"لیزیک|لازک|prk|فیکو|کاتاراکت|آب\s*مروارید", "within": "*"},
     ]},
    {"key": "neuro", "label": "مغز و اعصاب", "icon": "bolt", "color": "#0284c7",
     "types": [],
     "services": [
         {"key": "eeg", "label": "نوار مغز", "pattern": r"نوار\s*مغز|eeg", "within": "*"},
         {"key": "emg", "label": "نوار عصب و عضله", "pattern": r"نوار\s*عصب|emg|nCS", "within": "*"},
         {"key": "neurology", "label": "ویزیت مغز و اعصاب", "pattern": r"مغز\s*و\s*اعصاب|نورولوژ", "within": "*"},
     ]},
    {"key": "gi", "label": "گوارش و آندوسکوپی", "icon": "endo", "color": "#ca8a04",
     "types": ["بخش گوارش (آندوسکوپی و کولونوسکوپی)", "بخش گوارش (آندوسکوپی)"],
     "services": [
         {"key": "endoscopy", "label": "آندوسکوپی", "pattern": r"آندوسکوپ|اندوسکوپ", "within": "*"},
         {"key": "colonoscopy", "label": "کولونوسکوپی", "pattern": r"کولونوسکوپ", "within": "*"},
     ]},
    {"key": "surgery", "label": "جراحی محدود", "icon": "scissors", "color": "#475569",
     "types": ["مرکز جراحی محدود"], "services": []},
    {"key": "emergency", "label": "اورژانس", "icon": "siren", "color": "#ea580c",
     "types": ["خدمات اورژانس"], "services": []},
    {"key": "homecare", "label": "پرستاری در منزل", "icon": "homecare", "color": "#65a30d",
     "types": ["خدمات پرستاری در منزل"], "services": []},
]

ALL_DAY = re.compile(L + r"شبانه\s*روز|24\s*ساعت")
GENERAL_IMAGING = re.compile(L + r"سونو|ماموگراف|سی\s*تی(?!ر)|ام\s*آر\s*آی|mri|تراکم|هسته\s*ای", re.I)

TYPE_TO_CATEGORY = {t: c["key"] for c in CATEGORIES for t in c["types"]}
SERVICES = []  # (category_key, service, compiled pattern)
for _cat in CATEGORIES:
    for _svc in _cat["services"]:
        SERVICES.append((_cat["key"], _svc, re.compile(L + "(?:" + _svc["pattern"] + ")", re.I)))


def match_text(c):
    text = f"{c['type']} {c['name']} {c.get('note') or ''}"
    return text.replace("‌", " ").replace("ي", "ی").replace("ك", "ک")


def tag(c):
    """Return (categories, services, all_day) for one center."""
    primary = TYPE_TO_CATEGORY.get(c["type"], "clinic")
    text = match_text(c)
    cats, services = [primary], []
    for cat_key, svc, rx in SERVICES:
        within = svc.get("within", [cat_key])
        if within != "*" and primary not in within:
            continue
        if not rx.search(text):
            continue
        services.append(svc["key"])
        crosses = within == "*" or svc.get("cross")
        if crosses and cat_key not in cats:
            cats.append(cat_key)
    # "رادیولوژی دهان و فک" centers aren't general x-ray centers.
    if "dental_imaging" in services and "xray" in services and not GENERAL_IMAGING.search(text):
        services.remove("xray")
    # Every center of a single-service type gets that service, so its chip is complete.
    defaults = {"فیزیوتراپی": "physio", "عینک سازی": "optician",
                "بخش گوارش (آندوسکوپی)": "endoscopy"}
    if c["type"] in defaults and defaults[c["type"]] not in services:
        services.append(defaults[c["type"]])
    all_day = bool(ALL_DAY.search(text)) or c["type"] == "خدمات اورژانس"
    return cats, services, all_day


def load_overrides(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def apply_tags(centers, overrides_path):
    """Tag every center in place; return a text report for reviewing the rules."""
    overrides = load_overrides(overrides_path)
    for c in centers:
        c["categories"], c["services"], c["allDay"] = tag(c)
        fix = overrides.get(c["id"])
        if fix:
            for field in ("categories", "services", "allDay"):
                if field in fix:
                    c[field] = fix[field]
    return report(centers, overrides)


def taxonomy():
    """Category/service labels for the website (hidden services left out)."""
    return [{
        "key": cat["key"], "label": cat["label"], "icon": cat["icon"], "color": cat["color"],
        "services": [{"key": s["key"], "label": s["label"], "syn": s.get("syn", [])}
                     for s in cat["services"] if not s.get("hidden")],
    } for cat in CATEGORIES]


def report(centers, overrides):
    active = [c for c in centers if not c.get("deleted")]
    labels = {s["key"]: s["label"] for _, s, _ in SERVICES}
    by_cat = Counter(k for c in active for k in c["categories"])
    by_svc = defaultdict(list)
    for c in active:
        for s in c["services"]:
            by_svc[s].append(c)
    lines = [f"Tagging report: {len(active)} active centers, {len(overrides)} overrides", ""]
    for cat in CATEGORIES:
        lines.append(f"## {cat['label']} ({cat['key']}): {by_cat[cat['key']]} centers")
        for svc in cat["services"]:
            found = by_svc.get(svc["key"], [])
            examples = " | ".join(f"{c['name']} [{c['type']}]" for c in found[:4])
            lines.append(f"  - {svc['label']} ({svc['key']}): {len(found)}   e.g. {examples}")
        untagged = [c for c in active if c["categories"][0] == cat["key"]
                    and not any(labels.get(s) and s in {x['key'] for x in cat['services']} for s in c["services"])]
        if cat["services"]:
            lines.append(f"  - no specific service found: {len(untagged)}")
        lines.append("")
    lines.append(f"24-hour (شبانه‌روزی): {sum(1 for c in active if c['allDay'])}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Re-tag the existing database without scraping (e.g. after editing overrides.json).
    from db import load, save
    from update_data import retag
    database = load()
    retag(database)
    save(database)
