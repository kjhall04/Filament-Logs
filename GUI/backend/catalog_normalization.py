import json
import os
import re

from backend.config import DATA_DIR

CATALOG_ALIASES_PATH = os.path.join(DATA_DIR, "catalog_aliases.json")
_VALID_MAPPING_NAMES = ("brand", "color", "material", "attribute")


def normalize_space(value):
    return " ".join(str(value or "").split()).strip()


def lookup_key(value):
    return normalize_space(value).casefold()


def _grey_gray_variants(text):
    variants = [text]
    if "grey" in text:
        variants.append(text.replace("grey", "gray"))
    if "gray" in text:
        variants.append(text.replace("gray", "grey"))
    return variants


def iter_lookup_keys(value):
    base = normalize_space(value)
    if not base:
        return []

    ordered_texts = [
        base,
        base.replace("&", " and "),
        base.replace("&", " "),
    ]

    expanded_texts = []
    seen_texts = set()
    for text in ordered_texts:
        for candidate in (
            text,
            re.sub(r"[-_/+,]+", " ", text),
            re.sub(r"[()'`.]", "", text),
            re.sub(r"[()'`.]", "", re.sub(r"[-_/+,]+", " ", text)),
        ):
            normalized_candidate = normalize_space(candidate)
            if not normalized_candidate:
                continue
            key = normalized_candidate.casefold()
            if key in seen_texts:
                continue
            seen_texts.add(key)
            expanded_texts.append(normalized_candidate)

    final_keys = []
    seen_keys = set()
    for text in expanded_texts:
        normalized = normalize_space(text)
        if not normalized:
            continue
        base_variant = normalized.casefold()
        for variant in _grey_gray_variants(base_variant):
            for key in (lookup_key(variant), lookup_key(variant.replace(" ", ""))):
                if key not in seen_keys:
                    seen_keys.add(key)
                    final_keys.append(key)

    return final_keys


def _empty_alias_config():
    return {name: {} for name in _VALID_MAPPING_NAMES}


def load_alias_config():
    config = _empty_alias_config()
    try:
        with open(CATALOG_ALIASES_PATH, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except Exception:
        return config

    if not isinstance(raw, dict):
        return config

    for mapping_name in _VALID_MAPPING_NAMES:
        section = raw.get(mapping_name, {})
        if not isinstance(section, dict):
            continue
        cleaned = {}
        for canonical, aliases in section.items():
            canonical_label = normalize_space(canonical)
            if not canonical_label:
                continue
            if isinstance(aliases, (list, tuple)):
                alias_list = [normalize_space(item) for item in aliases if normalize_space(item)]
            elif isinstance(aliases, str):
                alias_list = [normalize_space(aliases)] if normalize_space(aliases) else []
            else:
                alias_list = []
            if alias_list:
                cleaned[canonical_label] = alias_list
        config[mapping_name] = cleaned
    return config


def build_label_lookup(mapping_name, mapping):
    lookup = {}
    canonical_by_key = {}
    if not isinstance(mapping, dict):
        return lookup

    for _, label in mapping.items():
        canonical = normalize_space(label)
        if not canonical:
            continue
        canonical_key = lookup_key(canonical)
        canonical_by_key[canonical_key] = canonical
        lookup[canonical_key] = canonical
        for key in iter_lookup_keys(canonical):
            lookup.setdefault(key, canonical)

    aliases = load_alias_config().get(mapping_name, {})
    for canonical_label, alias_values in aliases.items():
        canonical_key = lookup_key(canonical_label)
        canonical = canonical_by_key.get(canonical_key)
        if canonical is None:
            continue
        for alias in alias_values:
            for key in iter_lookup_keys(alias):
                existing = lookup.get(key)
                if existing is None or existing == canonical:
                    lookup[key] = canonical

    return lookup


def build_code_lookup(mapping_name, mapping):
    code_by_canonical_key = {}
    if not isinstance(mapping, dict):
        return {}

    for code, label in mapping.items():
        canonical = normalize_space(label)
        if not canonical:
            continue
        canonical_key = lookup_key(canonical)
        code_by_canonical_key.setdefault(canonical_key, str(code))

    label_lookup = build_label_lookup(mapping_name, mapping)
    code_lookup = {}
    for key, canonical_label in label_lookup.items():
        canonical_key = lookup_key(canonical_label)
        code = code_by_canonical_key.get(canonical_key)
        if code is not None:
            code_lookup[key] = code
    return code_lookup
