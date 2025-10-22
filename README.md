# Filament Logs

A Python-based inventory management system for tracking 3D printer filament rolls. Uses an Excel file for storage and provides a Flask web UI plus terminal tools.

## Features

- Log filament usage and update inventory in an Excel file
- Add new filament rolls with automatic barcode generation
- Mark rolls as empty based on a configurable threshold
- Mark and display favorite filament groups (deduplicated by brand/color/attributes)
- "Get Weight" button reads a connected USB scale (if available)
- Amazon search links for favorites (generated from brand/color/material)
- Modular backend for data manipulation, barcode generation, and stats
- Barcode/attribute mappings stored as JSON for easy editing

## Quick Start

1. Create a virtual env and install dependencies:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Run the web app:
   ```powershell
   python GUI/MAIN.py
   ```
3. Open your browser at http://127.0.0.1:5000

## Requirements

- Python 3.8+
- See requirements.txt (recommended). Core packages:
  - flask
  - openpyxl
  - python-dotenv
  - hidapi (only required for scale integration)
  - portalocker (optional — file locking for safe concurrent writes)

Install single-shot:
```powershell
pip install openpyxl flask python-dotenv hidapi portalocker
```
or
```powershell
pip install -r requirements.txt
```

## Project Layout

```
Filament-Logs/
├── GUI/
│   ├── MAIN.py
│   ├── backend/ (data_manipulation.py, generate_barcode.py, log_data.py, spreadsheet_stats.py)
│   ├── data/ (mapping jsons)
│   └── templates/ + static/
├── filament_inventory.xlsx  # auto-created
└── README.md
```

## Web App Notes

- The web UI templates (log/new_roll/favorites/etc.) include:
  - "Get Weight" button which calls /api/scale_weight to read the scale and prefill weight fields.
  - Barcode scanner handling: barcode input suppresses Enter submission and moves focus to the weight field to avoid accidental submits.
  - Autofill reduced by using nonstandard autocomplete tokens.

- Scale integration:
  - Endpoint: GET /api/scale_weight — returns JSON { "weight": <grams> } or an error (503) if no scale/read failure.
  - The Flask server must run on the machine that has the USB scale attached.
  - Requires hidapi; if no scale is present the UI still allows manual weight entry.

## Favorites page

- Favorites are deduplicated by brand + color + attributes (only one row per unique combination shown).
- For each favorite group the page shows:
  - Brand, Color, Material, Attribute 1, Attribute 2
  - Total count of rolls matching that group
  - Count marked low/empty (uses configured threshold)
  - A generated Amazon search link (opens Amazon search for brand/color/material filament)

## Stats and Time-window filtering

- Most-popular function can be filtered by recent weeks (example: last 4 weeks) — this filters rows by the sheet's last-logged timestamp.
- If you need per-event counts in a timeframe, consider enabling an "events" sheet that appends a row per usage and aggregate from that.

## Config & Constants

- Excel file path and thresholds:
  - FILE_PATH and EMPTY_THRESHOLD are defined in backend modules (log_data/spreadsheet_stats).
- Recommendation: centralize the spreadsheet column indices (COL_TIMESTAMP, COL_BARCODE, COL_BRAND, etc.) in a constants file to avoid indexing bugs.