import re


def select_keys(m, *keys):
    return {k: m[k] for k in keys if k in m}


def is_write_mode(mode):
    return bool(re.match(r"w[+a-z]*", mode))
