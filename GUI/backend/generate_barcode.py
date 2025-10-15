import os
import json
import difflib

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "data"))

def load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def get_closest_match(name: str, mapping: dict, default=None):
    """
    Fuzzy-match `name` against mapping values and return the matching key.
    """
    if not mapping:
        return default
    values = list(mapping.values())
    matches = difflib.get_close_matches(name, values, n=1, cutoff=0.6)
    if matches:
        matched_value = matches[0]
        for k, v in mapping.items():
            if v == matched_value:
                return k
    return default

def generate_filament_barcode(brand: str, color: str, material: str,
                              attribute_1: str, attribute_2: str,
                              location: str, sheet) -> str:
    """
    Generate a 17-digit barcode based on mappings and existing sheet entries.
    """
    brand_mapping = load_json("brand_mapping.json")
    color_mapping = load_json("color_mapping.json")
    material_mapping = load_json("material_mapping.json")
    attribute_mapping = load_json("attribute_mapping.json")

    # Flatten color mapping
    flat_color_mapping = {}
    for k, v in color_mapping.items():
        if isinstance(v, dict):
            flat_color_mapping.update(v)
        else:
            flat_color_mapping[k] = v

    brand_code = get_closest_match(brand, brand_mapping, None)
    color_code = get_closest_match(color, flat_color_mapping, None)
    material_code = get_closest_match(material, material_mapping, None)
    attribute_1_code = get_closest_match(attribute_1, attribute_mapping, None)
    attribute_2_code = get_closest_match(attribute_2, attribute_mapping, None)
    location_code = "0" if str(location).strip().lower() == "lab" else "1"

    # validate
    if None in (brand_code, color_code, material_code, attribute_1_code, attribute_2_code):
        raise ValueError("One or more inputs couldn't be matched to a mapping.")

    # collect existing barcodes (robust to cell objects / values_only)
    barcodes = []
    for row in sheet.iter_rows(min_row=2):
        try:
            cell = row[1]
            val = cell.value if hasattr(cell, "value") else cell
            if val:
                barcodes.append(str(val))
        except Exception:
            continue

    # Extract unique numeric suffixes from valid 17-digit numeric barcodes
    unique_ids = []
    for b in barcodes:
        if isinstance(b, str) and b.isdigit() and len(b) == 17:
            try:
                unique_ids.append(int(b[-5:]))
            except Exception:
                continue

    next_unique_id = max(unique_ids, default=0) + 1
    unique_id_str = f"{next_unique_id:05}"

    barcode = f"{brand_code}{color_code}{material_code}{attribute_1_code}{attribute_2_code}{location_code}{unique_id_str}"
    return barcode