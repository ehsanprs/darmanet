"""Visitor-oriented categories and services for health centers.

The source only gives a broad "type" (e.g. تصویربرداری). Here every center gets:
  categories  primary category (from its type) + any other category one of its
              detected services belongs to (e.g. a درمانگاه offering اکو also
              appears under قلب و عروق)
  services    specific services found in its name / description
  allDay      open 24 hours (شبانه‌روزی)

Detection is keyword-based on name + description. Parts of a description that
exclude something ("به جز لیزیک", "... شامل قرارداد نمی شود") are ignored.
Check the rules with tag_report.txt (written on every update) and
test_categories.py; fix individual centers in overrides.json.
"""
import json
import re
from collections import Counter, defaultdict

# Word start that works for Persian and Latin, also when the two scripts touch
# (e.g. "کبدباMRI"): a Persian word may not continue a Persian word, a Latin
# word may not continue a Latin word.
L = r"(?:(?<![؀-ۿ])(?=[؀-ۿ])|(?<![A-Za-z])(?=[A-Za-z0-9])|(?=[^؀-ۿA-Za-z0-9]))"
END = r"(?![a-z])"  # Latin abbreviations must end there ("ct", not "ctrl")

# Service fields:
#   key, label   id and visible name
#   pattern      regex, matched at a word start
#   syn          extra search words for the website
#   within       primary categories whose centers are checked (default: own
#                category); "*" = every center
#   cross        also list the center under this service's category
#                (default: True when within is "*")
#   hidden       used for cross-listing only, no filter chip
#   field        "name" = match the center's name only, not its description
#   also         other categories to list a matching center under
EVERYWHERE = "*"
CATEGORIES = [
    {"key": "dental", "label": "دندانپزشکی", "icon": "tooth", "color": "#0891b2",
     "types": ["دندانپزشکی"],
     "services": [
         {"key": "orthodontics", "label": "ارتودنسی", "pattern": r"ارتودن[سط]|ناهنجاری\s*(های\s*)?فک",
          "syn": ["ارتو", "سیم کشی دندان"]},
         {"key": "implant", "label": "ایمپلنت", "pattern": r"ایمپلنت", "syn": ["کاشت دندان"]},
         {"key": "prosthodontics", "label": "پروتز و روکش", "pattern": r"پروتز|روکش", "syn": ["دندان مصنوعی"]},
         {"key": "endodontics", "label": "درمان ریشه", "pattern": r"درمان\s*ریشه|عصب\s*کشی|اندودان?ت",
          "syn": ["عصب کشی"]},
         {"key": "kids_dentistry", "label": "دندانپزشکی کودکان", "pattern": r"کودک|اطفال"},
         {"key": "oral_surgery", "label": "جراحی دهان و لثه", "pattern": r"جراحی|لثه|پریودن", "syn": ["جراح"]},
         {"key": "dentistry", "label": "دندانپزشکی", "pattern": r"دندان", "within": ["clinic"],
          "cross": True, "hidden": True},
     ]},
    {"key": "lab", "label": "آزمایشگاه", "icon": "flask", "color": "#7c3aed",
     "types": ["آزمایشگاه"],
     "services": [
         {"key": "pathology", "label": "پاتولوژی (نمونه‌برداری)",
          "pattern": r"پاتولوژ|آسیب\s*شناس|هیستوپاتولوژ|سیتوپاتولوژ", "syn": ["بیوپسی", "نمونه برداری"]},
         {"key": "genetics", "label": "ژنتیک", "pattern": r"ژنتیک|سیتوژنتیک", "syn": ["آزمایش ژنتیک"]},
         {"key": "lab_unit", "label": "آزمایشگاه", "pattern": r"آزمایش(?!\s*ورزش)", "within": ["clinic"],
          "cross": True, "hidden": True},
     ]},
    {"key": "imaging", "label": "تصویربرداری", "icon": "scan", "color": "#2563eb",
     "types": ["تصویربرداری"],
     "services": [
         {"key": "ultrasound", "label": "سونوگرافی", "pattern": r"سونو|سنوگراف|(?<!اکو\s)(?<!اکو)داپلر",
          "within": EVERYWHERE, "syn": ["سونو", "سنوگرافی", "اولتراسوند", "داپلر"]},
         {"key": "xray", "label": "رادیولوژی", "pattern": r"رادیو(?:لو)?لوژ|رادیوگراف|هیستروگراف|ایکس\s*ری|x-?ray",
          "within": EVERYWHERE, "syn": ["عکس", "عکسبرداری", "رادیوگرافی"]},
         {"key": "mri", "label": "MRI", "pattern": r"ام\s*\.?\s*[اآ]ر\s*\.?\s*[اآ]ی|mri" + END + r"|مغناطیس",
          "within": EVERYWHERE, "syn": ["ام آر آی", "ام ار ای", "تصویربرداری مغناطیسی"]},
         {"key": "ct", "label": "سی‌تی‌اسکن", "pattern": r"سی\s*تی(?!ر)|سی\s*اسکن|ct" + END,
          "within": EVERYWHERE, "syn": ["سی تی", "سیتی اسکن", "ct scan", "سی تی آنژیوگرافی"]},
         {"key": "mammography", "label": "ماموگرافی", "pattern": r"مامو", "within": EVERYWHERE},
         {"key": "bone_density", "label": "تراکم استخوان", "pattern": r"تراکم|دانسیتومتر|bmd" + END,
          "within": EVERYWHERE, "syn": ["سنجش تراکم", "دانسیتومتری"]},
         {"key": "nuclear", "label": "پزشکی هسته‌ای",
          "pattern": r"هسته\s*ای|اسپکت|پت\s*اسکن|pet" + END + r"|رادیو\s*ایزوتوپ|گاما\s*کمرا|انواع\s*اسکن"
                     r"|اسکن\s*(?:های\s*)?(?:قلب|تیروئید|استخوان|کلیه|ریه|خون|پرفیوژن|مجاری|لنف|پاراتیروئید)",
          "within": EVERYWHERE, "syn": ["اسکن استخوان", "اسکن قلب", "اسکن تیروئید", "پت اسکن", "اسپکت"]},
         {"key": "dental_imaging", "label": "رادیولوژی دهان و فک",
          "pattern": r"فک|دهان|دندان|opg" + END + r"|cbct" + END + r"|پانورکس|پانورامیک|سفالو|بایت\s*وینگ"
                     r"|پری\s*اپیکال",
          "syn": ["او پی جی", "opg", "cbct", "عکس دندان", "پانورکس"]},
         {"key": "imaging_unit", "label": "تصویربرداری", "pattern": r"تصویربرداری|تصویر\s*برداری",
          "within": ["clinic", "lab"], "cross": True, "hidden": True},
     ]},
    {"key": "clinic", "label": "درمانگاه و مطب", "icon": "stetho", "color": "#0d9488",
     "types": ["درمانگاه", "کلینیک", "مطب"],
     "services": [
         {"key": "visit", "label": "ویزیت پزشک", "pattern": r"ویزی?ت", "syn": ["پزشک عمومی", "ویزیت"]},
         {"key": "internal", "label": "داخلی", "pattern": r"داخلی"},
         {"key": "women", "label": "زنان و زایمان", "pattern": r"زنان|زایمان|مامایی|nst" + END},
         {"key": "kids", "label": "کودکان", "pattern": r"کودک|اطفال"},
         {"key": "skin", "label": "پوست و مو", "pattern": r"پوست|زیبایی", "syn": ["لیزر"]},
         {"key": "orthopedics", "label": "ارتوپدی", "pattern": r"ارتوپد"},
         {"key": "psychiatry", "label": "اعصاب و روان", "pattern": r"اعصاب\s*و\s*روان|روانپزشک|روان\s*شناس",
          "syn": ["مشاوره", "روانپزشکی"]},
         {"key": "ent", "label": "گوش و حلق و بینی", "pattern": r"گوش\s*[،,و]?\s*حلق"},
         {"key": "urology", "label": "کلیه و مجاری ادرار",
          "pattern": r"ارولوژ|اورولوژ|سنگ\s*شکن|نوار\s*مثانه|اورودینامیک|کلیه\s*و\s*مجاری",
          "syn": ["سنگ شکن", "نوار مثانه"]},
         {"key": "spirometry", "label": "اسپیرومتری (تست ریه)", "pattern": r"اسپیرومتر|تست\s*ریه",
          "within": ["clinic", "heart", "neuro"], "syn": ["تست ریه"]},
         {"key": "dialysis", "label": "دیالیز", "pattern": r"دیالیز", "within": EVERYWHERE, "cross": False},
         {"key": "diabetes", "label": "دیابت", "pattern": r"دیابت"},
         {"key": "addiction", "label": "ترک اعتیاد", "pattern": r"اعتیاد|متادون"},
     ]},
    {"key": "rehab", "label": "فیزیوتراپی و توانبخشی", "icon": "activity", "color": "#16a34a",
     "types": ["فیزیوتراپی"],
     "services": [
         {"key": "physio", "label": "فیزیوتراپی", "pattern": r"فیزیوتراپ", "within": EVERYWHERE},
         {"key": "occupational", "label": "کاردرمانی", "pattern": r"کار\s*درمان", "within": EVERYWHERE},
         {"key": "speech", "label": "گفتاردرمانی", "pattern": r"گفتار\s*درمان", "within": EVERYWHERE},
         {"key": "audiology", "label": "شنوایی‌سنجی", "pattern": r"شنوایی|ادیومتر|ادیولوژیست|سمعک",
          "within": EVERYWHERE, "syn": ["سمعک", "ادیومتری"]},
     ]},
    {"key": "pharmacy", "label": "داروخانه", "icon": "pill", "color": "#db2777",
     "types": ["داروخانه"], "services": []},
    {"key": "hospital", "label": "بیمارستان", "icon": "hospital", "color": "#dc2626",
     "types": ["بیمارستان"],
     "services": [
         {"key": "hosp_children", "field": "name", "label": "کودکان", "pattern": r"کودک|اطفال"},
         {"key": "hosp_women", "field": "name", "label": "زنان و زایمان", "pattern": r"زنان|زایمان|مادر"},
         {"key": "hosp_eye", "field": "name", "label": "چشم", "pattern": r"چشم"},
         {"key": "hosp_heart", "field": "name", "label": "قلب", "pattern": r"قلب", "also": ["heart"]},
         {"key": "hosp_psych", "field": "name", "label": "اعصاب و روان", "pattern": r"روانپزشک|اعصاب\s*و\s*روان"},
         {"key": "hosp_trauma", "field": "name", "label": "سوانح و سوختگی", "pattern": r"سوانح|سوختگی|تروما"},
     ]},
    {"key": "heart", "label": "قلب و عروق", "icon": "heart", "color": "#e11d48",
     "types": ["کلینیک قلب"],
     "services": [
         {"key": "heart_visit", "label": "ویزیت متخصص قلب",
          "pattern": r"قلب\s*و\s*عروق|متخصص\s*قلب|کاردیولوژ|بخش\s*(?:سرپایی\s*)?قلب",
          "within": EVERYWHERE, "syn": ["متخصص قلب", "قلب و عروق"]},
         {"key": "echo", "label": "اکوکاردیوگرافی", "pattern": r"اکو(?!\s*سیستم)|echo" + END,
          "within": EVERYWHERE, "syn": ["اکو", "اکوی قلب"]},
         {"key": "ecg", "label": "نوار قلب", "pattern": r"نوار\s*قلب|نوار\s*برق|ecg" + END + "|ekg" + END,
          "within": EVERYWHERE, "syn": ["الکتروکاردیوگرام"]},
         {"key": "stress_test", "label": "تست ورزش", "pattern": r"تست\s*ورزش", "within": EVERYWHERE},
         {"key": "holter", "label": "هولتر", "pattern": r"هولتر|مانیتورینگ", "within": EVERYWHERE},
         {"key": "angiography", "label": "آنژیوگرافی و آنژیوپلاستی",
          "pattern": r"آنژیو\s*پلاست|(?<!تی\s)(?<!تی)آنژیو\s*گرافی(?!\s*چشم)",
          "within": EVERYWHERE, "syn": ["آنژیو", "بالن", "استنت"]},
     ]},
    {"key": "eye", "label": "چشم و بینایی", "icon": "glasses", "color": "#9333ea",
     "types": ["عینک سازی"],
     "services": [
         {"key": "optician", "label": "عینک‌سازی", "pattern": r"عینک", "syn": ["اپتیک", "لنز"]},
         {"key": "ophthalmology", "label": "چشم‌پزشکی", "pattern": r"چشم(?!\s*انداز|ان|ک|ه|یران)",
          "within": ["clinic", "surgery", "hospital"], "cross": True, "syn": ["چشم پزشک"]},
         {"key": "eye_tests", "label": "بینایی‌سنجی و تصویربرداری چشم",
          "pattern": r"بینایی\s*سنج|اپتومتر|oct" + END + r"|پنتاکم|پریمتری|ارب\s*اسکن|اسکن\s*چشم"
                     r"|آنژیوگرافی\s*چشم|عکس\s*برداری\s*چشم",
          "within": EVERYWHERE, "syn": ["oct", "پنتاکم", "پریمتری", "بینایی سنجی"]},
         {"key": "eye_surgery", "label": "لیزیک و جراحی چشم",
          "pattern": r"لیزیک|لازک|prk" + END + r"|فیکو|کاتاراکت|آب\s*مروارید|یاگ\s*لیزر|آواستین",
          "within": EVERYWHERE, "syn": ["لیزیک", "آب مروارید"]},
     ]},
    {"key": "neuro", "label": "مغز و اعصاب", "icon": "bolt", "color": "#0284c7",
     "types": [],
     "services": [
         {"key": "eeg", "label": "نوار مغز", "pattern": r"نو(?:ار|را)\s*مغ[زر]|نقشه\s*مغز|eeg" + END,
          "within": EVERYWHERE, "syn": ["نقشه مغزی"]},
         {"key": "emg", "label": "نوار عصب و عضله", "pattern": r"نو(?:ار|را)\s*عصب|emg" + END + "|ncs" + END,
          "within": EVERYWHERE},
         {"key": "neuro_tests", "label": "نوارنگاری", "pattern": r"نو(?:ار|را|گار)\s*نگاری",
          "within": EVERYWHERE, "hidden": True},
         {"key": "neurology", "label": "ویزیت مغز و اعصاب", "pattern": r"مغز\s*و\s*اعصاب|نورولوژ",
          "within": EVERYWHERE},
     ]},
    {"key": "gi", "label": "گوارش و آندوسکوپی", "icon": "endo", "color": "#ca8a04",
     "types": ["بخش گوارش (آندوسکوپی و کولونوسکوپی)", "بخش گوارش (آندوسکوپی)"],
     "services": [
         {"key": "endoscopy", "label": "آندوسکوپی", "pattern": r"[آا]ندوسکوپ(?!ی?\s*(?:بینی|سینوس))",
          "within": EVERYWHERE},
         {"key": "colonoscopy", "label": "کولونوسکوپی", "pattern": r"کولونوسکوپ", "within": EVERYWHERE},
     ]},
    {"key": "oncology", "label": "سرطان و رادیوتراپی", "icon": "ribbon", "color": "#a21caf",
     "types": [],
     "services": [
         {"key": "radiotherapy", "label": "رادیوتراپی", "pattern": r"رادیوتراپ|پرتو\s*درمان|گاما\s*نایف",
          "within": EVERYWHERE, "syn": ["پرتودرمانی", "گامانایف"]},
         {"key": "chemotherapy", "label": "شیمی‌درمانی", "pattern": r"شیمی\s*درمان", "within": EVERYWHERE},
         {"key": "oncology_visit", "label": "آنکولوژی", "pattern": r"[آا]نکولوژ|سرطان|کانسر",
          "within": EVERYWHERE, "syn": ["سرطان", "انکولوژی"]},
     ]},
    {"key": "surgery", "label": "جراحی محدود", "icon": "scissors", "color": "#475569",
     "types": ["مرکز جراحی محدود"], "services": []},
    {"key": "emergency", "label": "اورژانس", "icon": "siren", "color": "#ea580c",
     "types": ["خدمات اورژانس"],
     "services": [
         {"key": "emergency_unit", "label": "اورژانس", "pattern": r"اورژانس", "within": ["clinic"],
          "cross": True, "hidden": True},
     ]},
    {"key": "homecare", "label": "پرستاری در منزل", "icon": "homecare", "color": "#65a30d",
     "types": ["خدمات پرستاری در منزل"], "services": []},
]

ALL_DAY = re.compile(L + r"(?:شبانه\s*روز|24\s*ساعت)")
GENERAL_IMAGING = re.compile(L + r"(?:سونو|مامو|سی\s*تی(?!ر)|ام\s*[اآ]ر\s*[اآ]ی|mri|تراکم|هسته\s*ای)", re.I)

# Description parts that exclude services: everything after "به جز ..." in a part
# is dropped, and parts saying the service isn't covered are dropped entirely.
NEGATION_START = re.compile(r"به\s*جز|بجز|(?<![؀-ۿ])جز\s|عدم\s*پذیرش")
NEGATED_PART = re.compile(r"شامل\s*قرارداد\s*نمی|پذیرش\s*ندار|انجام\s*نمی|نمی\s*دهند|نمیدهند|قرارداد\s*نداری?م")
PART_SPLIT = re.compile(r"[-–—()\[\]/\n]|\s\.\s")

# Single-service source types: every center of the type gets the service.
TYPE_DEFAULTS = {"فیزیوتراپی": "physio", "عینک سازی": "optician", "بخش گوارش (آندوسکوپی)": "endoscopy"}

TYPE_TO_CATEGORY = {t: c["key"] for c in CATEGORIES for t in c["types"]}
SERVICES = []  # (category_key, service, compiled pattern)
for _cat in CATEGORIES:
    for _svc in _cat["services"]:
        SERVICES.append((_cat["key"], _svc, re.compile(L + "(?:" + _svc["pattern"] + ")", re.I)))


def normalize(text):
    text = (text or "").replace("‌", " ").replace("ي", "ی").replace("ك", "ک")
    return text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))


def positive_note(note):
    """The parts of a description that are not exclusions."""
    keep = []
    for part in PART_SPLIT.split(normalize(note)):
        if NEGATED_PART.search(part):
            continue
        m = NEGATION_START.search(part)
        keep.append(part[:m.start()] if m else part)
    return " - ".join(p for p in keep if p.strip())


def match_text(c):
    return f"{normalize(c['type'])} - {normalize(c['name'])} - {positive_note(c.get('note'))}"


def tag(c):
    """Return (categories, services, all_day) for one center."""
    primary = TYPE_TO_CATEGORY.get(c["type"], "clinic")
    text = match_text(c)
    name_text = f"{normalize(c['type'])} - {normalize(c['name'])}"
    cats, services = [primary], []
    for cat_key, svc, rx in SERVICES:
        within = svc.get("within", [cat_key])
        if within != EVERYWHERE and primary not in within:
            continue
        if not rx.search(name_text if svc.get("field") == "name" else text):
            continue
        services.append(svc["key"])
        crosses = svc.get("cross", within == EVERYWHERE)
        for k in ([cat_key] if crosses else []) + svc.get("also", []):
            if k not in cats:
                cats.append(k)
    # "رادیولوژی دهان و فک" centers aren't general x-ray centers.
    if "dental_imaging" in services and "xray" in services and not GENERAL_IMAGING.search(text):
        services.remove("xray")
    default = TYPE_DEFAULTS.get(c["type"])
    if default and default not in services:
        services.append(default)
    all_day = bool(ALL_DAY.search(text)) or c["type"] == "خدمات اورژانس"
    return cats, services, all_day


def load_overrides(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def apply_tags(centers, overrides_path, new_ids=()):
    """Tag every center in place; return a text report for reviewing the rules."""
    overrides = load_overrides(overrides_path)
    for c in centers:
        c["categories"], c["services"], c["allDay"] = tag(c)
        fix = overrides.get(c["id"])
        if fix:
            for field in ("categories", "services", "allDay"):
                if field in fix:
                    c[field] = fix[field]
    return report(centers, overrides, set(new_ids))


def taxonomy():
    """Category/service labels for the website (hidden services left out)."""
    return [{
        "key": cat["key"], "label": cat["label"], "icon": cat["icon"], "color": cat["color"],
        "services": [{"key": s["key"], "label": s["label"], "syn": s.get("syn", [])}
                     for s in cat["services"] if not s.get("hidden")],
    } for cat in CATEGORIES]


def unmatched_parts(c):
    """Description parts in which no rule found anything (candidates for new rules)."""
    out = []
    for part in positive_note(c.get("note")).split(" - "):
        part = part.strip(" ،,.:")
        if len(part) < 3 or re.fullmatch(r"(ویزی?ت|خدمات|سرپایی|و|انواع|شامل|\s)+", part):
            continue
        if not any(rx.search(part) for _, _, rx in SERVICES):
            out.append(part)
    return out


def describe(c, labels):
    svcs = "، ".join(labels.get(s, s) for s in c["services"]) or "-"
    return f"{c['name']} [{c['type']}] {c['city']} -> {', '.join(c['categories'])} | {svcs}"


def report(centers, overrides, new_ids=frozenset()):
    active = [c for c in centers if not c.get("deleted")]
    labels = {s["key"]: s["label"] for _, s, _ in SERVICES}
    by_cat = Counter(k for c in active for k in c["categories"])
    by_svc = defaultdict(list)
    for c in active:
        for s in c["services"]:
            by_svc[s].append(c)
    lines = [f"Tagging report: {len(active)} active centers, {len(overrides)} overrides", ""]

    new = [c for c in active if c["id"] in new_ids]
    if new:
        lines.append(f"## New centers in this update ({len(new)}): check their tags")
        lines += [f"  - {describe(c, labels)}" for c in new]
        lines.append("")

    for cat in CATEGORIES:
        lines.append(f"## {cat['label']} ({cat['key']}): {by_cat[cat['key']]} centers")
        own = {s["key"] for s in cat["services"]}
        for svc in cat["services"]:
            found = by_svc.get(svc["key"], [])
            examples = " | ".join(f"{c['name']} [{c['type']}]" for c in found[:4])
            lines.append(f"  - {svc['label']} ({svc['key']}): {len(found)}   e.g. {examples}")
        if cat["services"]:
            untagged = [c for c in active if c["categories"][0] == cat["key"] and not own & set(c["services"])]
            lines.append(f"  - no specific service found: {len(untagged)}")
        lines.append("")
    lines.append(f"24-hour (شبانه‌روزی): {sum(1 for c in active if c['allDay'])}")

    gaps = Counter(p for c in active for p in unmatched_parts(c))
    if gaps:
        lines += ["", "## Description parts no rule recognised (consider a new rule or synonym)"]
        lines += [f"  {n:3} × {part}" for part, n in gaps.most_common(60)]
    return "\n".join(lines)


if __name__ == "__main__":
    # Re-tag the existing database without scraping (e.g. after editing overrides.json).
    from db import load, save
    from update_data import retag
    database = load()
    retag(database)
    save(database)
