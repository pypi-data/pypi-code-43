import difflib
from typing import List

import chardet


def get_differ(a: List[str], b: List[str]):
    return difflib.unified_diff(a, b)


def read_file_with_chardet(file):
    with open(file, 'rb') as f:
        raw = f.read()
    d = chardet.detect(raw)
    raw = raw.decode(d['encoding'])
    return raw


def get_line_breaker(lines: List[str]):
    if len(lines) == 1:
        line_break = '\n'
    else:
        line_break = lines[0][-1]
    return line_break
