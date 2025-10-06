import openpyxl
import data_manipulation
import generate_barcode
import os
from datetime import datetime

# File path for the Excel workbook
FILE_PATH = r"C:\Users\LichKing\Desktop\Programming\Filament-Logs\filament_inventory.xlsx"

# Empty threshold for filament detection
EMPTY_THRESHOLD = 5

# Initialize workbook and sheet
def get_workbook_and_sheet():
    if not os.path.exists(FILE_PATH):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['Timestamp', 'Barcode', 'Brand', 'Color', 'Material', 'Attribute 1', 'Attribute 2',
                      'Filament Amount (g)', 'Location', 'Roll Weight (g)', 'Times Logged Out', 'Is Empty'])
        workbook.save(FILE_PATH)
    workbook = openpyxl.load_workbook(FILE_PATH)
    sheet = workbook.active
    return workbook, sheet

def log_filament_data_web(barcode, filament_amount, roll_weight=None):
    """Logs filament data from the web form and updates Excel."""
    workbook, sheet = get_workbook_and_sheet()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated = False

    for row in sheet.iter_rows(min_row=2):
        if str(row[1].value).strip() == str(barcode).strip():
            row[0].value = timestamp  # Update timestamp
            row[7].value = filament_amount  # Update filament amount
            row[10].value = int(row[10].value) + 1 if row[10].value else 1
            if int(filament_amount) <= EMPTY_THRESHOLD:
                row[11].value = 'True'
            else:
                row[11].value = 'False'
            updated = True
            break

    if updated:
        workbook.save(FILE_PATH)
        print(f"Logged data for barcode {barcode} at {timestamp}")
    else:
        # Optionally, handle case where barcode not found
        print("Update failed")

    return updated

def log_full_filament_data_web(brand, color, material, attr1, attr2, location, starting_weight, roll_weight):
    workbook, sheet = get_workbook_and_sheet()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    barcode = generate_barcode.generate_filament_barcode(brand, color, material, attr1, attr2, location, sheet)
    filament_amount = int(starting_weight) - int(roll_weight)
    sheet.append([timestamp, barcode, brand, color, material, attr1, attr2, filament_amount,
                  location, roll_weight, '0', 'False'])
    workbook.save(FILE_PATH)
    return {
        "timestamp": timestamp,
        "barcode": barcode,
        "brand": brand,
        "color": color,
        "material": material,
        "attributes": " ".join(filter(None, [attr1, attr2])),
        "filament_amount": filament_amount,
        "location": location,
        "roll_weight": roll_weight
    }

if __name__ == "__main__":
    print(FILE_PATH)