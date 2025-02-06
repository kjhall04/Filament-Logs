import json
import difflib

def get_barcode() -> str:
    """
    Prompt the user to scan a barcode and validate it as a 13-digit numeric string.
    Returns:
        str: The valid barcode.
    """
    while True:
        barcode = input('Ready to scan barcode: ').strip()
        if len(barcode) == 13 and barcode.isdigit():
            return barcode
        print('Invalid barcode. Please scan a valid 13-digit numeric barcode.')

def get_weight() -> str:
    """
    Prompt the user to input the weight of filament and validate it as a numeric value.
    Returns:
        str: The weight with 'g' appended.
    """
    while True:
        weight = input('Enter weight of filament: ').strip()
        if weight.isdigit():
            return f'{weight} g'
        print('Invalid weight. Please enter a numeric value.')

def decode_barcode(barcode: str) -> str:
    """
    Decode a 13-digit barcode into a description using JSON mappings with fuzzy matching.

    Args:
        barcode (str): The 13-digit barcode.

    Returns:
        tuple: The decoded brand, color, material, and location.
    """
    if len(barcode) != 13:
        raise ValueError("Barcode must be exactly 13 digits long.")
    
    brand_mapping = load_json('brand_mapping.json')
    color_mapping = load_json('color_mapping.json')
    material_mapping = load_json('material_mapping.json')

    # Split the barcode into segments for material, color, and brand
    brand_code = barcode[:2]
    color_code = barcode[2:5]
    material_code = barcode[5:7]
    location_code = barcode[7]

    # Decode each segment using the mappings with fuzzy matching
    brand = get_closest_match(brand_code, brand_mapping, "Unknown Brand")
    color = get_closest_match(color_code, color_mapping, "Unknown Color")
    material = get_closest_match(material_code, material_mapping, "Unknown Material")
    location = 'Lab' if location_code == 0 else 'Storage'

    return brand, color, material, location

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
    try:
        barcode = input('Enter a barcode: ').strip()
        decoded = decode_barcode(barcode)
        print(f"Decoded Barcode: Material={decoded[0]}, Color={decoded[1]}, Brand={decoded[2]}, Location={decoded[3]}")
    except Exception as e:
        print(f"Error: {e}")
