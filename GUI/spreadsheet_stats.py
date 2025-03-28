import openpyxl

FILE_PATH = 'Filament-Logs\\filament_inventory.xlsx'

def load_spreadsheet():
    """Loads the spreadsheet or creates a new one if not found."""
    try:
        workbook = openpyxl.load_workbook(FILE_PATH)
        sheet = workbook.active
    except FileNotFoundError:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['Timestamp', 'Barcode', 'Brand', 'Color', 'Material', 'Attribute 1', 'Attribute 2', 'Filament Amount (g)', 'Location', 'Roll Weight (g)', 'Times Logged Out', 'Is Empty'])
    return sheet