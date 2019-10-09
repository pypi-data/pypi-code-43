"""
delimited list conversion
"""

__all__ = ["convert_list"]


def convert_list(value: str, delimiter=",", raise_exceptions=True) -> list:
    converted = value

    if not value:
        return []

    try:
        converted = [x.strip() for x in value.split(delimiter)]
    except Exception as exc:
        if raise_exceptions:
            raise

    return converted
