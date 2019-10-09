"""
String to datetime.timedelta conversion
"""
import datetime
import re

__all__ = ["convert_delta"]

DELTA_RE = re.compile(r"(?P<value>\d+)(?P<unit>\w+)?")


def convert_delta(value: str) -> datetime.timedelta:
    """
    Returns the value as a datetime.timedelta
    """
    matches = DELTA_RE.match(value)
    if not matches:
        raise ValueError(f"unrecognized value: {value}")

    # the bare value defaults to seconds
    value = float(matches.group("value"))

    unit = matches.group("unit")
    if unit == "ms":
        value /= 1000
    elif unit == "s":
        pass
    elif unit == "m":
        value *= 60
    elif unit == "h":
        value *= 3600
    elif unit == "d":
        value *= 86400
    elif unit == "w":
        value *= 86400 * 7
    else:
        raise ValueError(f"unrecognized unit: {unit}")

    return datetime.timedelta(seconds=value)
