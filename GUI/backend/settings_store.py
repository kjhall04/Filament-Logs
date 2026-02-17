import json
import os
from copy import deepcopy

from backend.config import SETTINGS_PATH

THEME_OPTIONS = ("light", "dark")
ALERT_MODE_OPTIONS = ("all", "errors_only", "silent", "browser")

DEFAULT_SETTINGS = {
    "theme": "light",
    "alert_mode": "all",
    "rows_per_page": 20,
    "default_location": "Lab",
    "popular_weeks": 4,
    "filament_amount_g": 1000.0,
    "low_stock_alerts": True,
}


def _ensure_parent_dir():
    parent = os.path.dirname(SETTINGS_PATH) or "."
    os.makedirs(parent, exist_ok=True)


def _to_int(value, default, min_value, max_value):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(min_value, min(max_value, parsed))


def _to_float(value, default, min_value, max_value):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(min_value, min(max_value, parsed))


def sanitize_settings(raw):
    settings = deepcopy(DEFAULT_SETTINGS)
    if isinstance(raw, dict):
        settings.update(raw)

    theme = str(settings.get("theme", DEFAULT_SETTINGS["theme"])).strip().lower()
    settings["theme"] = theme if theme in THEME_OPTIONS else DEFAULT_SETTINGS["theme"]

    alert_mode = str(settings.get("alert_mode", DEFAULT_SETTINGS["alert_mode"])).strip().lower()
    settings["alert_mode"] = (
        alert_mode if alert_mode in ALERT_MODE_OPTIONS else DEFAULT_SETTINGS["alert_mode"]
    )

    settings["rows_per_page"] = _to_int(settings.get("rows_per_page"), 20, 5, 200)
    settings["popular_weeks"] = _to_int(settings.get("popular_weeks"), 4, 0, 104)
    settings["filament_amount_g"] = _to_float(
        settings.get("filament_amount_g"), 1000.0, 100.0, 10000.0
    )

    default_location = str(settings.get("default_location", "Lab")).strip()
    settings["default_location"] = default_location if default_location in ("Lab", "Storage") else "Lab"

    low_stock_raw = settings.get("low_stock_alerts", True)
    if isinstance(low_stock_raw, str):
        settings["low_stock_alerts"] = low_stock_raw.strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
    else:
        settings["low_stock_alerts"] = bool(low_stock_raw)

    return settings


def load_settings():
    _ensure_parent_dir()
    if not os.path.exists(SETTINGS_PATH):
        return deepcopy(DEFAULT_SETTINGS)

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception:
        return deepcopy(DEFAULT_SETTINGS)

    return sanitize_settings(data)


def save_settings(updates):
    current = load_settings()
    if isinstance(updates, dict):
        current.update(updates)
    sanitized = sanitize_settings(current)

    _ensure_parent_dir()
    with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(sanitized, file, indent=2)

    return sanitized
