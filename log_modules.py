from CustomMapping import MATERIAL_MAPPING, COLOR_MAPPING, BRAND_MAPPING

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
    Decode a 13-digit barcode into a word.
    Assumes letters are encoded as their alphabet positions (1-26),
    followed by zeroes as padding if needed.

    Args:
        barcode (str): The 13-digit barcode.

    Returns:
        str: The decoded word.
    """
    # Split the barcode into chunks of two digits
    chunks = [barcode[i:i+2] for i in range(0, len(barcode), 2)]
    
    # Filter valid chunks (1-26) and ignore padding (00)
    valid_chunks = [chunk for chunk in chunks if chunk != "00" and 1 <= int(chunk) <= 26]
    
    # Convert each valid chunk to its corresponding letter
    decoded = ''.join(chr(int(chunk) + 64) for chunk in valid_chunks)
    return decoded