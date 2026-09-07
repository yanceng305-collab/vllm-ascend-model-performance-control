"""Strict JSON loading helpers for the D-026 candidate tooling lane."""

import io
import json


class DuplicateJSONKey(ValueError):
    """Raised when a JSON object contains a duplicate key."""


def _reject_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise DuplicateJSONKey("DUPLICATE_JSON_KEY: %s" % key)
        obj[key] = value
    return obj


def load_json(path):
    """Load UTF-8 JSON without accepting duplicate object keys."""
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=_reject_duplicates)
