# Filament Logs

Flask-based inventory tracking for 3D printer filament rolls.
Data is stored in an Excel workbook with an inventory sheet plus usage event history.

## Features

- Inventory dashboard with search, pagination, favorites, and quick actions
- Log filament usage by barcode with decimal weight support
- Add new rolls with strict mapping-driven dropdowns (brand/color/material/attributes/location)
- Scale integration through `GET /api/scale_weight` (manual entry still supported)
- Event history sheet (`UsageEvents`) for time-window popularity analytics
- Settings page for:
  - General/Advanced sections
  - Light/Dark theme
  - Alert handling (`all`, `errors_only`, `silent`, `browser`)
  - Rows per page
  - Default new-roll location
  - Default roll condition (`new`/`used`)
  - Default popularity window (weeks)
  - Configured filament amount for new-roll calculations
  - Adjustable low/empty thresholds
  - Low-stock warning toggle
  - Used-roll map fallback depth + minimum sample count
  - Scale timeout/retry and auto-read on add-roll weight step
  - Negative-filament policy for used-roll mapped weights
  - Optional workbook auto-backup + retention days
- Optional file locking (`portalocker`) for safer concurrent workbook access

## Quick Start

1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install openpyxl flask python-dotenv hidapi portalocker
   ```
3. Run the app:
   ```powershell
   python GUI/MAIN.py
   ```
4. Open: `http://127.0.0.1:5000`

## Data Files

- Inventory workbook (default): `GUI/data/filament_inventory.xlsx`
- Settings file (default): `GUI/data/settings.json`
- Mapping files:
  - `GUI/data/brand_mapping.json`
  - `GUI/data/color_mapping.json`
  - `GUI/data/material_mapping.json`
  - `GUI/data/attribute_mapping.json`
  - `GUI/data/weight_mapping.json` (used-roll weight map)

## Environment Variables

- `EXCEL_PATH` (optional): override workbook path
- `SETTINGS_PATH` (optional): override settings JSON path
- `EMPTY_THRESHOLD` (optional, default `5`): mark roll empty at/below this amount
- `LOW_THRESHOLD` (optional, default `250`): low-stock threshold used by reports/warnings
- `FLASK_SECRET_KEY` (optional): Flask session secret
- `FLASK_DEBUG` (optional, default `1`)

## Notes

- The Flask server must run on the machine connected to the USB scale.
- If the scale is disconnected or unavailable, the app returns a `503` from `/api/scale_weight` and still allows manual entry.
- Browser alert mode requires notification permission in the browser.
