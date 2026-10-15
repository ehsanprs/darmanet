# درمانت — مراکز طرف قرارداد با بیمه سامان

A fast, Farsi, mobile-friendly website for finding the health centers listed on
[darmanet.ir/table](https://darmanet.ir/table/), with the data stored offline next to the site.

## Open the website

Open `site/index.html` in a browser (double-click works, no server needed).
The data (`site/data/centers.js`) and the Vazirmatn font (`site/assets/fonts/`, SIL OFL)
are stored locally, so the site works fully offline.

## Publishing (GitHub Pages)

Every push to `main` that changes `site/` deploys it automatically via
`.github/workflows/pages.yml`. To publish new data: run the two steps below, then commit and push.

## Update the data

### Step 1: new and removed centers — `update_data.bat`

Scrapes all pages again (about 2-3 minutes), cleans the data and **merges** it into the
existing database:

- centers already in the database are refreshed but **keep their coordinates**;
- new centers are added **without coordinates** (with an `addedAt` date);
- centers no longer on darmanet.ir stay in the file with `"deleted": true` and a `deletedAt`
  date (the website hides them); if they come back they are restored.

Options: `--cached` rebuilds from already-downloaded pages without fetching,
`--force` writes even if far fewer centers come back than last time
(by default the script refuses, to protect against a broken scrape).
Downloaded pages are cached per day under `cache/`; delete old folders freely.

### Step 2: coordinates — `geocode_data.bat`

Looks up coordinates only for active centers that have none, using the Neshan
"address to point" API (one request per unique address; centers sharing an address reuse it).
Progress is saved every 50 addresses, so it can be stopped and re-run safely; if the Neshan
credit runs out it stops and the next run continues where it left off.
Addresses Neshan cannot find are marked `not_found` and skipped next time
(use `--retry-failed` to try them again). `--limit N` looks up at most N addresses.

The API key is read from a local **`.env`** file (`NESHAN_API_KEY=...`) that is git-ignored,
or from the `NESHAN_API_KEY` environment variable.

### Files

| File | Purpose |
|---|---|
| `site/data/centers.json` | The database (one object per center; `location: {lat, lng}` once geocoded) |
| `site/data/centers.js` | Same data wrapped for `file://` use; loaded by the page |
| `site/data/darmanet_all_provinces.xlsx` | Full Excel export (linked in the site footer) |

## Categories and services

The source's broad types are mapped to visitor-oriented categories in `categories.py`
(دندانپزشکی, آزمایشگاه, تصویربرداری, درمانگاه و مطب, فیزیوتراپی و توانبخشی, داروخانه,
بیمارستان, قلب و عروق, چشم و بینایی, مغز و اعصاب, گوارش و آندوسکوپی, جراحی محدود,
اورژانس, پرستاری در منزل). Specific services (سونوگرافی, MRI, اکو, نوار عصب, ارتودنسی, ...)
are detected from each center's name and description with keyword rules, and a center can
appear in several categories (e.g. a درمانگاه offering اکو is also under قلب و عروق).
"شبانه‌روزی" centers are flagged too.

- Tags are rebuilt on every `update_data.bat` run; review `tag_report.txt` (counts and
  examples per service) after changing rules.
- Fix individual centers in `overrides.json` (by `id`), then re-tag without scraping:
  `.venv\Scripts\python categories.py`.
- The website reads the category/service labels and search synonyms from `taxonomy`
  in `centers.json`, so new services only need a rule in `categories.py`.

## Data cleaning

- The source repeats every record (about half the pages are duplicates); duplicates are removed.
- Phone numbers are normalized to dialable 11-digit numbers (missing leading 0, area codes
  added to 8-digit numbers, shorthand like `03532347090-9070` expanded). Values the source
  stored as `2.13E+11` cannot be recovered.
- Postal codes are pulled out of addresses; insurers are split into a list
  (`null` = not stated, `[]` = no base-insurance contract).
