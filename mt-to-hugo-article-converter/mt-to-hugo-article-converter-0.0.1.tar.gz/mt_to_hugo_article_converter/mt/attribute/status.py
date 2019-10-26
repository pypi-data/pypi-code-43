import re
from .single_line_attribute import SingleLineAttribute


class Status(SingleLineAttribute):
    regex = re.compile(r'^\s*STATUS:\s*(.*)\s*$')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
