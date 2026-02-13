import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_EXCEL_PATH = os.path.join(BASE_DIR, "data", "filament_inventory.xlsx")

EXCEL_PATH = os.getenv("EXCEL_PATH", DEFAULT_EXCEL_PATH)
EMPTY_THRESHOLD = int(os.getenv("EMPTY_THRESHOLD", "5"))
LOW_THRESHOLD = float(os.getenv("LOW_THRESHOLD", "250"))