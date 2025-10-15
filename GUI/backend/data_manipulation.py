import hid
import struct
import time
import json
import difflib
import os

# Constants
VENDOR_ID = 0x0922
PRODUCT_ID = 0x8003
FILAMENT_AMOUNT = 1000

BASE_DIR = os.path.dirname(__file__)

def read_scale_weight(timeout_sec: int = 5):
    """
    Read a single weight (grams) from the scale. Returns float grams or None on timeout/error.
    """
    device = None
    try:
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        device.set_nonblocking(False)
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            data = device.read(6)
            if data:
                try:
                    weight_raw = struct.unpack('<h', bytes(data[4:6]))[0]
                except Exception:
                    return None
                units = "g" if len(data) > 2 and data[2] == 2 else "oz"
                if units == "oz":
                    return round(weight_raw * 28.3495, 2)
                return float(weight_raw)
            time.sleep(0.1)
        return None
    except Exception:
        return None
    finally:
        try:
            if device:
                device.close()
        except Exception:
            pass

def get_roll_weight(barcode: str, sheet):
    """
    Return roll weight (float) for barcode from the sheet or None if not found / not numeric.
    Safe and tolerant to missing columns.
    """
    if not barcode:
        return None
    for row in sheet.iter_rows(min_row=2, values_only=True):
        row_barcode = str(row[1]) if row and len(row) > 1 and row[1] is not None else ""
        if row_barcode == str(barcode):
            # Prefer index 9 for roll weight, otherwise try nearby numeric columns
            for idx in (9, 7, 8, 10):
                if len(row) > idx and row[idx] is not None:
                    try:
                        return float(row[idx])
                    except Exception:
                        continue
            return None
    return None

def decode_barcode(barcode: str):
    """
    Decode a 17-digit barcode into (brand, color, material, attr1, attr2, location).
    """
    if len(barcode) != 17:
        raise ValueError("Barcode must be exactly 17 digits long.")

    brand_mapping = load_json(os.path.join(BASE_DIR, '..', 'data', 'brand_mapping.json'))
    color_mapping = load_json(os.path.join(BASE_DIR, '..', 'data', 'color_mapping.json'))
    material_mapping = load_json(os.path.join(BASE_DIR, '..', 'data', 'material_mapping.json'))
    attribute_mapping = load_json(os.path.join(BASE_DIR, '..', 'data', 'attribute_mapping.json'))

    # Flatten color mapping
    flat_color_mapping = {}
    for category, colors in color_mapping.items():
        if isinstance(colors, dict):
            flat_color_mapping.update(colors)
        else:
            flat_color_mapping[category] = colors

    brand_code = barcode[:2]
    color_code = barcode[2:5]
    material_code = barcode[5:7]
    attr1_code = barcode[7:9]
    attr2_code = barcode[9:11]
    location_code = barcode[11]

    brand = get_closest_match(brand_code, brand_mapping, "Unknown Brand")
    color = get_closest_match(color_code, flat_color_mapping, "Unknown Color")
    material = get_closest_match(material_code, material_mapping, "Unknown Material")
    attr1 = get_closest_match(attr1_code, attribute_mapping, "Unknown Attribute")
    attr2 = get_closest_match(attr2_code, attribute_mapping, "Unknown Attribute")
    location = 'Lab' if location_code == '0' else 'Storage'

    return brand, color, material, attr1, attr2, location

def get_closest_match(code, mapping, default):
    normalized_input = ' '.join(sorted(str(code).split()))
    normalized_keys = [' '.join(sorted(str(k).split())) for k in mapping.keys()]
    matches = difflib.get_close_matches(normalized_input, normalized_keys, n=1, cutoff=0.6)
    if matches:
        original_key = list(mapping.keys())[normalized_keys.index(matches[0])]
        return mapping[original_key]
    return default

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}