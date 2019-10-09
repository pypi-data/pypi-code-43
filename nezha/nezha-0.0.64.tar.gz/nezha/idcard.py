import re

PATTERN_PHONE = re.compile(
    r'^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$|^[1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}$')


def is_valid_idcard(value: str) -> bool:
    if not isinstance(value, str):
        raise ValueError("value {} type must be string".format(value))
    return PATTERN_PHONE.match(value) is not None
