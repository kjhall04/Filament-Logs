import openpyxl
import time
import log_modules
import generate_barcode

# File path for the Excel workbook
FILE_PATH = 'filament_inventory.xlsx'

# Initialize workbook and sheet
try:
    workbook = openpyxl.load_workbook(FILE_PATH)
    sheet = workbook.active
except FileNotFoundError:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Timestamp', 'Barcode', 'Brand', 'Color', 'Material', 'Weight (g)', 'Location'])  # Add headers

def log_filament_data(generate):
    """
    Main loop to log filament data, including barcode, weight, and decoded filament name.
    Saves the data to an Excel file and handles user interruptions gracefully.
    """
    print("Press Ctrl+C to exit the program.")

    if not generate:
        while True:
            try:
                # Gather data
                barcode = log_modules.get_barcode()
                brand, color, material, location = log_modules.decode_barcode(barcode)

                # Display log info
                print(f'Logging weight for filament: {brand} {color} {material}')

                weight = log_modules.get_weight()

                # Append data to the sheet
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

                sheet.append([timestamp, barcode, brand, color, material, weight, location])
                workbook.save(FILE_PATH)

                print(f'Logged: {timestamp}, Barcode: {barcode}, Brand: {brand}, Color: {color}, Material: {material}, Weight: {weight}, Location: {location}')

            except KeyboardInterrupt:
                print('\nExiting program. Goodbye!')
                break
            except Exception as e:
                print(f"An error occurred: {e}")

    else:
        while True:
            try:
                brand = input('Enter the brand: ')  # Brand first
                color = input('Enter the color: ')
                material = input('Enter the material: ')  # Material last
                location = input('Enter the location of the filament: ')

                barcode = generate_barcode.generate_filament_barcode(brand, color, material, location, sheet)
                brand, color, material, location = log_modules.decode_barcode(barcode)
                print(f'New barcode for {brand} {color} {material} in {location} is {barcode}')
            except KeyboardInterrupt:
                print('\nExiting program. Goodbye!')
                break
            except ValueError as e:
                print(e)


if __name__ == '__main__':
    log_filament_data(generate=False)