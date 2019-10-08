import re
from itertools import chain

def re_one_of(xs):
    """return a regex string that matches one of the xs"""
    # the "a^" thing matches nothing on purpose (not even with re.M).
    # it is necessary in the case where `xs` is empty because then the
    # regex is "" which then matches the empty string -- oops.
    escape = re.escape
    xs = sorted(xs, key=len, reverse=True)
    return '|'.join(escape(x) for x in xs) if xs else 'a^'
