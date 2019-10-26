import re
from .single_line_attribute import SingleLineAttribute


class Basename(SingleLineAttribute):
    regex = re.compile(r'^\s*BASENAME:\s*(.*)\s*$')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
