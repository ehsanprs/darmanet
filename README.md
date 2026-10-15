# درمانت — مراکز طرف قرارداد با بیمه سامان

A fast, Farsi, mobile-friendly website for finding the health centers listed on
[darmanet.ir/table](https://darmanet.ir/table/), with the data stored offline next to the site.

## Open the website

Open `site/index.html` in a browser (double-click works, no server needed).
The data (`site/data/centers.js`) and the Vazirmatn font (`site/assets/fonts/`, SIL OFL)
are stored locally, so the site works fully offline.

## Publishing (GitHub Pages)

Every push to `main` that changes `site/` deploys it automatically via
`.github/workflows/pages.yml`. To publish new data: run `update_data.bat`, then commit and push.

## Update the data

Double-click **`update_data.bat`**, or run:

```
.venv\Scripts\python update_data.py
```

This scrapes all pages again (about 2-3 minutes), cleans the data and rewrites:

| File | Purpose |
|---|---|
| `site/data/centers.json` | The database (clean JSON, one object per center) |
| `site/data/centers.js` | Same data wrapped for `file://` use; loaded by the page |
| `site/data/darmanet_all_provinces.xlsx` | Full Excel export (linked in the site footer) |

Options: `--cached` rebuilds from already-downloaded pages without fetching,
`--force` writes even if far fewer centers come back than last time
(by default the script refuses, to protect against a broken scrape).
Downloaded pages are cached per day under `cache/`; delete old folders freely.

## Data cleaning

- The source repeats every record (about half the pages are duplicates); duplicates are removed.
- Phone numbers are normalized to dialable 11-digit numbers (missing leading 0, area codes
  added to 8-digit numbers, shorthand like `03532347090-9070` expanded). Values the source
  stored as `2.13E+11` cannot be recovered.
- Postal codes are pulled out of addresses; insurers are split into a list
  (`null` = not stated, `[]` = no base-insurance contract).
