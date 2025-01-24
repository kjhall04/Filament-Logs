import openpyxl
import time
import log_modules

# File path for the Excel workbook
FILE_PATH = 'filament_weights.xlsx'

# Initialize workbook and sheet
try:
    workbook = openpyxl.load_workbook(FILE_PATH)
    sheet = workbook.active
except FileNotFoundError:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Timestamp', 'Barcode', 'Brand', 'Material', 'Color', 'Weight (g)'])  # Add headers

def log_filament_data():
    """
    Main loop to log filament data, including barcode, weight, and decoded filament name.
    Saves the data to an Excel file and handles user interruptions gracefully.
    """
    print("Press Ctrl+C to exit the program.")
    while True:
        try:
            # Gather data
            barcode = log_modules.get_barcode()
            material, color, brand = log_modules.decode_barcode(barcode)

            # Display log info
            print(f'Logging weight for filament: {brand} {color} {material}')

            weight = log_modules.get_weight()

            # Append data to the sheet
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

            sheet.append([timestamp, barcode, brand, material, color, weight])
            workbook.save(FILE_PATH)

            print(f'Logged: {timestamp}, Barcode: {barcode}, Brand: {brand}, Color: {color}, Material: {material}, Weight: {weight}')

        except KeyboardInterrupt:
            print('\nExiting program. Goodbye!')
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    log_filament_data()