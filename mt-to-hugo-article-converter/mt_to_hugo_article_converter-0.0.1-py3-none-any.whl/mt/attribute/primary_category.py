import re
from .single_line_attribute import SingleLineAttribute


class PrimaryCategory(SingleLineAttribute):
    regex = re.compile(r'^\s*PRIMARY\s+CATEGORY:\s*(.*)\s*$')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
