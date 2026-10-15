"""Load and save the website database (site/data/centers.json + centers.js)."""
import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "site" / "data"
JSON_PATH = DATA_DIR / "centers.json"
JS_PATH = DATA_DIR / "centers.js"


def load():
    if not JSON_PATH.exists():
        return {"meta": {}, "centers": []}
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def save(db):
    centers = db["centers"]
    db["meta"].update({
        "count": sum(1 for c in centers if not c.get("deleted")),
        "deleted": sum(1 for c in centers if c.get("deleted")),
        "geocoded": sum(1 for c in centers if c.get("location")),
    })
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(db, ensure_ascii=False, separators=(",", ":"))
    # Write to temp files first so an interrupted run never leaves a broken database.
    for path, content in ((JSON_PATH, text), (JS_PATH, f"window.DARMANET_DB = {text};\n")):
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)


def today():
    return dt.date.today().isoformat()
