"""Scrape the darmanet.ir provider table for one province into an Excel file.

Usage: python scrape_darmanet.py [ostan|all] [output.xlsx]
"""
import sys
import time
from collections import Counter
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

BASE = "https://darmanet.ir/table/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
CACHE = Path(__file__).with_name("cache")


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.cell = None
        self.row = None
        self.headers, self.rows = [], []
        self.last_page = 1

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table" and a.get("id") == "jadval":
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.row = []
        elif self.in_table and tag in ("td", "th"):
            self.cell = []
        elif tag == "a" and "darmanet_page=" in (a.get("href") or ""):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(a["href"]).query)
            try:
                self.last_page = max(self.last_page, int(q["darmanet_page"][0]))
            except (KeyError, ValueError):
                pass

    def handle_endtag(self, tag):
        if not self.in_table:
            return
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            (self.rows if self.headers else self.headers).extend(
                [self.row] if self.headers else self.row)
            self.row = None
        elif tag == "table":
            self.in_table = False

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)


def fetch(ostan, page, cache=CACHE):
    f = cache / f"{ostan}_{page}.html"
    if f.exists():
        return f.read_text(encoding="utf-8")
    query = "" if ostan == "all" else f"ostan={urllib.parse.quote(ostan)}&"
    url = f"{BASE}?{query}darmanet_page={page}"
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8")
            f.write_text(html, encoding="utf-8")
            time.sleep(0.3)
            return html
        except Exception as e:
            print(f"page {page} attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch page {page}")


def parse(html):
    p = TableParser()
    p.feed(html)
    return p


def scrape(ostan, cache=CACHE):
    """Fetch every page for `ostan` ("all" for no filter).

    Returns (headers, {page_number: [row, ...]}).
    """
    cache.mkdir(parents=True, exist_ok=True)
    first = parse(fetch(ostan, 1, cache))
    pages = first.last_page
    print(f"{ostan}: {pages} pages")

    def job(n):
        return n, parse(fetch(ostan, n, cache)).rows

    results = {1: first.rows}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for n, rows in ex.map(job, range(2, pages + 1)):
            results[n] = rows
            if n % 50 == 0:
                print(f"  {n}/{pages}")
    return first.headers, results


def main():
    ostan = sys.argv[1] if len(sys.argv) > 1 else "تهران"
    out = sys.argv[2] if len(sys.argv) > 2 else f"darmanet_{ostan}.xlsx"
    headers, results = scrape(ostan)
    write_excel(out, ostan, headers, results)


def write_excel(out, ostan, headers, results):
    # The site repeats its listing (e.g. Tehran pages 196-390 mirror 1-195),
    # so the main sheet keeps only the first occurrence of each row.
    all_rows = [(n, row) for n in sorted(results) for row in results[n]]
    seen, unique = set(), []
    for n, row in all_rows:
        if tuple(row) not in seen:
            seen.add(tuple(row))
            unique.append((n, row))
    # Drop header rows that were imported into the site's data as records.
    unique = [(n, row) for n, row in unique if row != headers
              and row[2:3] != headers[2:3]]

    wb = Workbook()
    write_sheet(wb.active, "همه استان‌ها" if ostan == "all" else ostan,
                headers, unique)
    if ostan == "all":
        summary = wb.create_sheet("خلاصه")
        summary.sheet_view.rightToLeft = True
        summary.append(["استان", "تعداد مراکز"])
        for c in summary[1]:
            c.font = Font(bold=True)
        for name, count in Counter(row[2] for _, row in unique).most_common():
            summary.append([name, count])
        summary.column_dimensions["A"].width = 25
    write_sheet(wb.create_sheet(), "همه صفحات (خام)", headers, all_rows)
    wb.save(out)
    empty = [n for n in sorted(results) if not results[n]]
    print(f"saved {len(unique)} unique rows ({len(all_rows)} raw) to {out}; "
          f"empty pages: {empty or 'none'}")


def write_sheet(ws, title, headers, rows):
    ws.title = title
    ws.sheet_view.rightToLeft = True
    ws.append(["صفحه"] + headers)
    for c in ws[1]:
        c.font = Font(bold=True)
    for n, row in rows:
        ws.append([n] + row)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for i, w in enumerate([7, 14, 35, 10, 14, 18, 70, 12, 35, 30], 1):
        ws.column_dimensions[get_column_letter(i)].width = w


if __name__ == "__main__":
    main()
