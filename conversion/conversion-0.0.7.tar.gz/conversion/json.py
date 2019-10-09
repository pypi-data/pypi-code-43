import json

from typing import Any


def convert_json(value: str, raise_exceptions=True) -> Any:
    converted = value

    try:
        converted = json.loads(value)
    except Exception as exc:
        if raise_exceptions:
            raise

    return converted
