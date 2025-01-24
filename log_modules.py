import json

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
    Decode a 13-digit barcode into a description using JSON mappings.

    Args:
        barcode (str): The 13-digit barcode.

    Returns:
        str: The decoded description.
    """
    if len(barcode) != 13:
        raise ValueError("Barcode must be exactly 13 digits long.")
    
    material_mapping = load_json('material_mapping.json')
    color_mapping = load_json('color_mapping.json')
    brand_mapping = load_json('brand_mapping.json')

    # Split the barcode into segments for material, color, and brand
    material_code = barcode[5:7]
    color_code = barcode[2:5]
    brand_code = barcode[:2]

    # Decode each segment using the mappings
    material = material_mapping.get(material_code, "Unknown Material")
    color = color_mapping.get(color_code, "Unknown Color")
    brand = brand_mapping.get(brand_code, "Unknown Brand")

    # Combine the decoded segments into a full description
    return material, color, brand

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)


if __name__ == '__main__':

    decoded = decode_barcode(input('Enter in a barcode: '))
    print(decoded)
