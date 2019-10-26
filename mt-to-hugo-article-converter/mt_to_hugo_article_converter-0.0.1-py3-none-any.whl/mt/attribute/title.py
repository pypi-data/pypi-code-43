import re
from .single_line_attribute import SingleLineAttribute


class Title(SingleLineAttribute):
    regex = re.compile(r'^\s*TITLE:\s*(.*)\s*$')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
