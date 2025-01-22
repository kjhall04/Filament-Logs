import random
import time
import openpyxl

# Set up Excel file
file_path = "filament_weights_simulated.xlsx"
try:
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
except FileNotFoundError:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Timestamp", "Barcode", "Weight (g)"])

# Simulated barcode scanner
def simulate_barcode_scanner():
    # Generate a random 12-digit barcode
    return f"{random.randint(100000000000, 999999999999)}"

# Simulated scale
def simulate_scale():
    # Generate a random weight between 100g and 2000g
    return random.randint(100, 2000)

# Main function to simulate logging data
def log_filament_data_simulated():
    print("Simulating barcode scanner and scale...")

    while True:
        try:
            # Simulate barcode scanning
            barcode = simulate_barcode_scanner()
            print(f"Simulated Barcode: {barcode}")

            # Simulate weight measurement
            weight = simulate_scale()
            print(f"Simulated Weight: {weight}g")

            # Log data in Excel
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            sheet.append([timestamp, barcode, weight])
            workbook.save(file_path)

            print(f"Logged: {timestamp}, Barcode: {barcode}, Weight: {weight}g\n")

            # Wait for a short time before next simulation
            time.sleep(2)

        except KeyboardInterrupt:
            print("Simulation stopped.")
            break

if __name__ == "__main__":
    log_filament_data_simulated()
