import json
import difflib
import hid
import struct
import time

def get_barcode() -> str:
    """
    Prompt the user to scan a barcode and validate it as a 16-digit numeric string.
    Returns:
        str: The valid barcode.
    """
    while True:
        barcode = input('Ready to scan barcode: ').strip()
        if len(barcode) == 16 and barcode.isdigit():
            return barcode
        print('Invalid barcode. Please scan a valid 16-digit numeric barcode.')

def get_starting_weight() -> str:
    """
    Prompt the user to place filament on the scale to get the starting weight of filament.
    The scale is a DYMO M10.
    Returns:
        str: The weight with 'g' appended.
    """
    VENDOR_ID = 0x0922
    PRODUCT_ID = 0x8003

    try:
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        device.set_nonblocking(False)

        print("\n--- Scale Ready ---")
        input("Place the filament on the scale and press Enter to continue...")

        retries = 5
        weight_raw = None

        for _ in range(retries):
            data = device.read(6)
            if data:
                weight_raw = struct.unpack('<h', bytes(data[4:6]))[0]
                units = "g" if data[2] == 2 else "oz"
                
                if units == "oz":
                    # Convert ounces to grams
                    weight_grams = round(weight_raw * 28.3495, 2)
                    filament_amount = 1000
                    roll_weight = weight_grams - filament_amount
                    return f"{roll_weight} g", f"{filament_amount} g"
                else:
                    filament_amount = 1000
                    roll_weight = weight_raw - filament_amount
                    return f"{roll_weight} g", f"{filament_amount} g"

            time.sleep(0.5)

        if weight_raw is None:
            return "Failed to read weight. Please try again."

    except Exception as e:
        return f"Error: {e}"
    finally:
        device.close()

def get_current_weight(roll_weight: str) -> str:
    """
    Prompt the user to place filament on the scale to get the current weight of filament.
    The scale is a DYMO M10.
    Returns:
        str: The weight with 'g' appended.
    """
    VENDOR_ID = 0x0922
    PRODUCT_ID = 0x8003

    try:
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        device.set_nonblocking(False)

        print("\n--- Scale Ready ---")
        input("Place the filament on the scale and press Enter to continue...")

        retries = 5
        weight_raw = None

        for _ in range(retries):
            data = device.read(6)
            if data:
                weight_raw = struct.unpack('<h', bytes(data[4:6]))[0]
                units = "g" if data[2] == 2 else "oz"
                
                if units == "oz":
                    # Convert ounces to grams
                    weight_grams = round(weight_raw * 28.3495, 2)
                    filament_amount = weight_grams - roll_weight
                    return f"{filament_amount} g"
                else:
                    filament_amount = weight_raw - roll_weight
                    return f"{filament_amount} g"

            time.sleep(0.5)

        if weight_raw is None:
            return "Failed to read weight. Please try again."

    except Exception as e:
        return f"Error: {e}"
    finally:
        device.close()


def decode_barcode(barcode: str) -> str:
    """
    Decode a 17-digit barcode into a description using JSON mappings with fuzzy matching.

    Args:
        barcode (str): The 17-digit barcode.

    Returns:
        tuple: The decoded brand, color, material, and location.
    """
    if len(barcode) != 17:
        raise ValueError("Barcode must be exactly 17 digits long.")
    
    brand_mapping = load_json('brand_mapping.json')
    color_mapping = load_json('color_mapping.json')
    material_mapping = load_json('material_mapping.json')
    attribute_mapping = load_json('attribute_mapping.json')

    # Flatten the nested color mapping dynamically
    flat_color_mapping = {}
    for category, colors in color_mapping.items():
        if isinstance(colors, dict):
            flat_color_mapping.update(colors)
        else:
            flat_color_mapping[category] = colors

    # Split the barcode into segments for material, color, and brand
    brand_code = barcode[:2]
    color_code = barcode[2:5]
    material_code = barcode[5:7]
    attribute_code_1 = barcode[7:9]
    attribute_code_2 = barcode[9:11]
    location_code = barcode[11]

    # Decode each segment using the mappings with fuzzy matching
    brand = get_closest_match(brand_code, brand_mapping, "Unknown Brand")
    color = get_closest_match(color_code, flat_color_mapping, "Unknown Color")
    material = get_closest_match(material_code, material_mapping, "Unknown Material")
    attribute_1 = get_closest_match(attribute_code_1, attribute_mapping, "Unknown Attribute")
    attribute_2 = get_closest_match(attribute_code_2, attribute_mapping, "Unknown Attribute")
    location = 'Lab' if location_code == '0' else 'Storage'

    return brand, color, material, attribute_1, attribute_2, location

def get_closest_match(code, mapping, default):
    """
    Find the closest match for a code in a given mapping using fuzzy matching.

    Args:
        code (str): The code to match.
        mapping (dict): The mapping dictionary to search in.
        default (str): The default value if no close match is found.

    Returns:
        str: The matched value or the default.
    """
    keys = list(mapping.keys())
    matches = difflib.get_close_matches(code, keys, n=1, cutoff=0.6)
    if matches:
        return mapping[matches[0]]
    return default

def load_json(filename):
    """
    Load a JSON file and return its content.

    Args:
        filename (str): The name of the JSON file.

    Returns:
        dict: The content of the JSON file.
    """
    with open(filename, 'r') as file:
        return json.load(file)

if __name__ == '__main__':
    while True:
        try:
            barcode = input('Enter the barcode: ')
            brand, color, material, attribute_1, attribute_2, location = decode_barcode(barcode)
            print(f'Brand: {brand}, Color: {color}, Material: {material}, Attribute 1: {attribute_1}, Attribute 2: {attribute_2}, Location: {location}')
        except KeyboardInterrupt:
            print('Exiting...')
            break