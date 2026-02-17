import json
import os
import struct
import time

try:
    import hid
except Exception:
    hid = None

VENDOR_ID = 0x0922
PRODUCT_ID = 0x8003
FILAMENT_AMOUNT = 1000.0

BASE_DIR = os.path.dirname(__file__)


def read_scale_weight(timeout_sec: int = 5):
    """
    Read a single weight (grams) from the scale.
    Returns float grams or None on timeout/error.
    """
    if hid is None:
        return None

    device = None
    try:
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        device.set_nonblocking(False)

        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            data = device.read(6)
            if not data:
                time.sleep(0.1)
                continue

            try:
                weight_raw = struct.unpack("<h", bytes(data[4:6]))[0]
            except Exception:
                return None

            units = "g" if len(data) > 2 and data[2] == 2 else "oz"
            if units == "oz":
                return round(weight_raw * 28.3495, 2)
            return float(weight_raw)

        return None
    except Exception:
        return None
    finally:
        try:
            if device is not None:
                device.close()
        except Exception:
            pass


def get_starting_weight(timeout_sec: int = 5):
    """
    Compatibility wrapper used by web flow.
    Returns (weight, "g") where weight can be None.
    """
    return read_scale_weight(timeout_sec=timeout_sec), "g"


def get_roll_weight(barcode: str, sheet):
    """
    Return roll weight (float) for barcode from the sheet.
    Returns None when no numeric value can be found.
    """
    if not barcode:
        return None

    needle = str(barcode).strip()
    for row in sheet.iter_rows(min_row=2, values_only=True):
        row_barcode = ""
        if row and len(row) > 1 and row[1] is not None:
            row_barcode = str(row[1]).strip()
        if row_barcode != needle:
            continue

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
    Decode a 17-digit barcode into
    (brand, color, material, attr1, attr2, location).
    """
    if len(barcode) != 17 or not barcode.isdigit():
        raise ValueError("Barcode must be exactly 17 digits long.")

    brand_mapping = _load_json(os.path.join(BASE_DIR, "..", "data", "brand_mapping.json"))
    color_mapping = _load_json(os.path.join(BASE_DIR, "..", "data", "color_mapping.json"))
    material_mapping = _load_json(os.path.join(BASE_DIR, "..", "data", "material_mapping.json"))
    attribute_mapping = _load_json(os.path.join(BASE_DIR, "..", "data", "attribute_mapping.json"))

    flat_color_mapping = {}
    for _, value in color_mapping.items():
        if isinstance(value, dict):
            flat_color_mapping.update(value)

    brand_code = barcode[:2]
    color_code = barcode[2:5]
    material_code = barcode[5:7]
    attr1_code = barcode[7:9]
    attr2_code = barcode[9:11]
    location_code = barcode[11]

    brand = brand_mapping.get(brand_code, "Unknown Brand")
    color = flat_color_mapping.get(color_code, "Unknown Color")
    material = material_mapping.get(material_code, "Unknown Material")
    attr1 = attribute_mapping.get(attr1_code, "Unknown Attribute")
    attr2 = attribute_mapping.get(attr2_code, "Unknown Attribute")
    location = "Lab" if location_code == "0" else "Storage"

    return brand, color, material, attr1, attr2, location


def _load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}
