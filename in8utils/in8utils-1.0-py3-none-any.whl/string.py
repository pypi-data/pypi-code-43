import re


def find_by_regex(pattern: str, target: str) -> list:
    return re.compile(pattern).findall(target)


def replace_all(against: str, regex: str, replacement: str) -> str:
    """
    For Python 3.6 or less.
    :param against: string to lookup on.
    :param regex: pattern.
    :param replacement: replacement value.
    :return:
    """
    return re.sub(regex, replacement, against)


def clean(string: str) -> str:
    return replace_all(string, r'[\r\n\t\s]+', ' ') if string is not None else ""
