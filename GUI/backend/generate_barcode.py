import json
import os

from backend import catalog_normalization
from backend.workbook_store import list_inventory_barcodes

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "data"))


def load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def _flatten_color_mapping(color_mapping: dict) -> dict:
    flattened = {}
    for key, value in color_mapping.items():
        if isinstance(value, dict):
            flattened.update(value)
        else:
            flattened[key] = value
    return flattened


def _mapping_value_to_code(value: str, mapping_name: str, mapping: dict):
    if str(value or "").strip() == "":
        for code, label in mapping.items():
            if catalog_normalization.normalize_space(label) == "":
                return str(code)
        return None

    value_keys = catalog_normalization.iter_lookup_keys(value)
    if not value_keys:
        return None

    code_lookup = catalog_normalization.build_code_lookup(mapping_name, mapping)
    for key in value_keys:
        code = code_lookup.get(key)
        if code is not None:
            return code
    return None


def _sorted_values_from_mapping(mapping: dict):
    def sort_key(item):
        key = str(item[0])
        return (0, int(key)) if key.isdigit() else (1, key)

    return [label for _, label in sorted(mapping.items(), key=sort_key)]


def get_catalog_options():
    brand_mapping = load_json("brand_mapping.json")
    color_mapping = _flatten_color_mapping(load_json("color_mapping.json"))
    material_mapping = load_json("material_mapping.json")
    attribute_mapping = load_json("attribute_mapping.json")

    attributes = _sorted_values_from_mapping(attribute_mapping)
    if "" not in attributes:
        attributes.insert(0, "")

    return {
        "brands": _sorted_values_from_mapping(brand_mapping),
        "colors": _sorted_values_from_mapping(color_mapping),
        "materials": _sorted_values_from_mapping(material_mapping),
        "attributes": attributes,
        "locations": ["Lab", "Storage"],
    }


def generate_filament_barcode(
    brand: str,
    color: str,
    material: str,
    attribute_1: str,
    attribute_2: str,
    location: str,
    sheet=None,
) -> str:
    _ = sheet  # Compatibility with older call sites.

    brand_mapping = load_json("brand_mapping.json")
    color_mapping = _flatten_color_mapping(load_json("color_mapping.json"))
    material_mapping = load_json("material_mapping.json")
    attribute_mapping = load_json("attribute_mapping.json")

    brand_code = _mapping_value_to_code(brand, "brand", brand_mapping)
    color_code = _mapping_value_to_code(color, "color", color_mapping)
    material_code = _mapping_value_to_code(material, "material", material_mapping)
    attribute_1_code = _mapping_value_to_code(attribute_1 or "", "attribute", attribute_mapping)
    attribute_2_code = _mapping_value_to_code(attribute_2 or "", "attribute", attribute_mapping)

    location_map = {"lab": "0", "storage": "1"}
    location_code = location_map.get(str(location).strip().lower())

    missing = []
    if brand_code is None:
        missing.append("brand")
    if color_code is None:
        missing.append("color")
    if material_code is None:
        missing.append("material")
    if attribute_1_code is None:
        missing.append("attribute_1")
    if attribute_2_code is None:
        missing.append("attribute_2")
    if location_code is None:
        missing.append("location")

    if missing:
        raise ValueError("Invalid selection for: " + ", ".join(missing))

    unique_ids = []
    for existing in list_inventory_barcodes():
        if existing.isdigit() and len(existing) == 17:
            try:
                unique_ids.append(int(existing[-5:]))
            except Exception:
                continue

    next_unique_id = max(unique_ids, default=0) + 1
    unique_id_str = f"{next_unique_id:05}"

    return (
        f"{brand_code}{color_code}{material_code}"
        f"{attribute_1_code}{attribute_2_code}{location_code}{unique_id_str}"
    )
