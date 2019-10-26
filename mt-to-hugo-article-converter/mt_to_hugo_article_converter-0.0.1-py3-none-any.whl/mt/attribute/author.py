import re
from .single_line_attribute import SingleLineAttribute


class Author(SingleLineAttribute):
    regex = re.compile(r'^\s*AUTHOR:\s*(.*)\s*$')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
