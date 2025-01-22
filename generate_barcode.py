import json

# Load the JSON files into Python dictionaries
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

MATERIAL_MAPPING = load_json('material_mapping.json')
COLOR_MAPPING = load_json('color_mapping.json')
BRAND_MAPPING = load_json('brand_mapping.json')


def generate_filament_barcode(material: str, color: str, brand: str, unique_id: int = None) -> str:
    """
    Generate a barcode for a new filament roll based on the provided information.
    
    Args:
        material (str): The material name (e.g., "PLA").
        color (str): The color name (e.g., "White").
        brand (str): The brand name (e.g., "Brand A").
        unique_id (int): Optional unique ID for the roll. If not provided, starts from 1.
    
    Returns:
        str: A 13-digit numeric barcode.
    """
    # Reverse mapping to find codes from names
    material_code = next((code for code, name in MATERIAL_MAPPING.items() if name == material), None)
    color_code = next((code for code, name in COLOR_MAPPING.items() if name == color), None)
    brand_code = next((code for code, name in BRAND_MAPPING.items() if name == brand), None)

    # Validate inputs
    if not material_code:
        raise ValueError(f"Invalid material: {material}. Please use a valid material name.")
    if not color_code:
        raise ValueError(f"Invalid color: {color}. Please use a valid color name.")
    if not brand_code:
        raise ValueError(f"Invalid brand: {brand}. Please use a valid brand name.")
    
    # Assign a unique ID if not provided
    if unique_id is None:
        unique_id = 1  # Start with 1 for new rolls; this can be replaced with a database query.

    # Format unique ID as zero-padded string (up to 6 digits)
    unique_id_str = f"{unique_id:06}"

    # Construct the barcode
    barcode = f"{material_code}{color_code}{brand_code}{unique_id_str}"
    return barcode