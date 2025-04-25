# Filament Logs

A Python-based inventory management system for tracking 3D printer filament rolls. This project uses Excel files for data storage and provides utilities for logging filament usage, generating barcodes, and managing inventory. It includes both a GUI (with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)) and terminal-based tools.

## Features

- Log filament usage and update inventory in an Excel file
- Add new filament rolls with barcode generation
- Mark rolls as empty based on a configurable threshold
- Modular code for data manipulation and barcode generation
- Barcode and attribute mapping via JSON files
- GUI and terminal interfaces

## Requirements

- Python 3.8+
- [openpyxl](https://pypi.org/project/openpyxl/)
- [hidapi](https://pypi.org/project/hidapi/) (for scale integration)
- [CustomTkinter](https://pypi.org/project/customtkinter/) (for GUI)
- [difflib](https://docs.python.org/3/library/difflib.html) (standard library, for fuzzy matching)

Install dependencies with:
```sh
pip install openpyxl hidapi customtkinter
```

## Project Structure

```
Filament-Logs/
│
├── GUI/
│   ├── MAIN.py
│   ├── GUI.py
│   ├── log_data.py
│   ├── data_manipulation.py
│   ├── generate_barcode.py
│   ├── spreadsheet_stats.py
│   ├── data/
│   │   ├── brand_mapping.json
│   │   ├── color_mapping.json
│   │   ├── material_mapping.json
│   │   └── attribute_mapping.json
│   └── screens/
│       ├── __init__.py
│       ├── admin_screen.py
│       ├── user_screen.py
│       ├── update_current_weight_screen.py
│       ├── new_roll_screen.py
│       └── new_weight_screen.py
│
├── Terminal/
│   ├── backend/
│   │   ├── log_data.py
│   │   ├── data_manipulation.py
│   │   └── generate_barcode.py
│   └── data/
│       ├── brand_mapping.json
│       ├── color_mapping.json
│       ├── material_mapping.json
│       └── attribute_mapping.json
│
├── Filament-Logs/
│   └── filament_inventory.xlsx  # (auto-generated)
├── .gitignore
├── .gitattributes
├── .vscode/
│   └── settings.json
└── README.md
```

## Usage

### GUI

Run the GUI application:
```sh
python GUI/MAIN.py
```

### Terminal

Run the terminal logger:
```sh
python Terminal/backend/log_data.py
```

- To log a new filament roll, use the `log_full_filament_data(barcode)` function.
- To update an existing roll's usage, use the `log_filament_data(barcode, filament_amount)` function.

## Configuration

- The Excel file path is set in `log_data.py` as `Filament-Logs/filament_inventory.xlsx`.
- The empty threshold (in grams) is configurable via the `EMPTY_THRESHOLD` variable.
- Barcode, color, material, and attribute mappings are stored in JSON files under `GUI/data/` and `Terminal/data/`.

## Notes

- The Excel file is created automatically if it does not exist.
- Make sure to keep the barcode format consistent with your data manipulation logic.
- The scale integration requires a compatible USB scale (e.g., DYMO M10) and the `hidapi` library.

## License

MIT License