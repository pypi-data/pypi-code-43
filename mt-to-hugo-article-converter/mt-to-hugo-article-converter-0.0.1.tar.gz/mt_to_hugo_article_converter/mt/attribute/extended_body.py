import re
from .multi_line_attribute import MultiLineAttribute


class ExtendedBody(MultiLineAttribute):
    regex = re.compile(r'^\s*EXTENDED\s+BODY:\s*$')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
