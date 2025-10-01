# Filament Logs

A Python-based inventory management system for tracking 3D printer filament rolls. This project uses Excel files for data storage and provides utilities for logging filament usage, generating barcodes, and managing inventory. It includes a modern Flask web application and terminal-based tools.

## Features

- Log filament usage and update inventory in an Excel file
- Add new filament rolls with automatic barcode generation
- Mark rolls as empty based on a configurable threshold
- Modular code for data manipulation and barcode generation
- Barcode and attribute mapping via JSON files
- Modern web interface (Flask) with search, pagination, and stats pages
- Terminal interface for command-line usage
- USB barcode scanner and scale integration (if supported by hardware)

## Requirements

- Python 3.8+
- [openpyxl](https://pypi.org/project/openpyxl/)
- [hidapi](https://pypi.org/project/hidapi/) (for scale integration)
- [Flask](https://pypi.org/project/Flask/) (for web app)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (for environment variables)
- [difflib](https://docs.python.org/3/library/difflib.html) (standard library, for fuzzy matching)

Install dependencies with:
```sh
pip install openpyxl hidapi flask python-dotenv
```

## Project Structure

```
Filament-Logs/
│
├── GUI/
│   ├── MAIN.py
│   ├── backend/
│   │   ├── data_manipulation.py
│   │   ├── generate_barcode.py
│   │   ├── log_data.py
│   │   ├── spreadsheet_stats.py
│   ├── data/
│   │   ├── brand_mapping.json
│   │   ├── color_mapping.json
│   │   ├── material_mapping.json
│   │   └── attribute_mapping.json
│   └── templates/
│       ├── index.html
│       ├── log.html
│       ├── new_roll.html
│       ├── popular.html
│       ├── low_empty.html
│       ├── empty_rolls.html
│
├── Terminal/
│   ├── backend/
│   │   ├── MAIN.py
│   │   ├── log_data.py
│   │   ├── data_manipulation.py
│   │   ├── generate_barcode.py
│   │   └── spreadsheet_stats.py
│   └── data/
│       ├── brand_mapping.json
│       ├── color_mapping.json
│       ├── material_mapping.json
│       └── attribute_mapping.json
│
├── filament_inventory.xlsx  # (auto-generated)
└── README.md
```

## Usage

### Web Application (Recommended)

Run the Flask web app:
```sh
python GUI/MAIN.py
```
- Access the inventory, log usage, add new rolls, and view stats in your browser.
- Use the search bar and pagination to quickly find filament rolls.
- Barcode scanner input works in focused fields; scale integration is available if supported.

### Terminal

Run the terminal menu:
```sh
python Terminal/backend/MAIN.py
```
- When prompted, enter `Admin` for admin functions or any other value for user mode.
- Admins can log new rolls, view stats, and more; users can log filament usage.

### Direct Function Usage

- To log a new filament roll, use the `log_full_filament_data()` function.
- To update an existing roll's usage, use the `log_filament_data()` function.

## Configuration

- The Excel file path is set in `log_data.py` and `MAIN.py` as `filament_inventory.xlsx`.
- The empty threshold (in grams) is configurable via the `EMPTY_THRESHOLD` variable.
- Barcode, color, material, and attribute mappings are stored in JSON files under `GUI/data/` and `Terminal/data/`.
- Environment variables (such as Flask secret key) can be set in a `.env` file.

## Notes

- The Excel file is created automatically if it does not exist.
- Make sure to keep the barcode format consistent with your data manipulation logic.
- The scale integration requires a compatible USB scale (e.g., DYMO M10) and the `hidapi` library.
- Admin/user role selection is supported in the terminal menu.
- The web app provides dynamic search and pagination for all inventory and stats pages.
- All templates display empty cells instead of `None`.

## License

MIT License