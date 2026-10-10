"""Reference implementation of the Non-Finite Attributes convention in Python."""

import math
import re

UUID = "2adc9aac-d676-4e93-8feb-903b6ae9e08a"
_AFFECTED = re.compile(r"(?:_str_)*(?:NaN|Infinity|-Infinity)")


def encode(value):
    """Return value as it is written in zarr.json."""
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, str):
        return "_str_" + value if _AFFECTED.fullmatch(value) else value
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    return value


def decode(value):
    """Return the value that an entry of zarr.json stands for."""
    if isinstance(value, str) and _AFFECTED.fullmatch(value):
        return value[len("_str_") :] if value.startswith("_str_") else float(value)
    if isinstance(value, list):
        return [decode(item) for item in value]
    if isinstance(value, dict):
        return {key: decode(item) for key, item in value.items()}
    return value


def declares(attributes):
    """Whether a node's attributes register the convention."""
    conventions = attributes.get("zarr_conventions", [])
    return any(isinstance(entry, dict) and entry.get("uuid") == UUID for entry in conventions)


def encode_attributes(attributes):
    """Encode every attribute of a node except zarr_conventions, which is written as it is."""
    return {key: value if key == "zarr_conventions" else encode(value) for key, value in attributes.items()}


def decode_attributes(attributes):
    """Decode every attribute of a node that registers the convention; return any other node's unchanged."""
    if not declares(attributes):
        return attributes
    return {key: value if key == "zarr_conventions" else decode(value) for key, value in attributes.items()}
