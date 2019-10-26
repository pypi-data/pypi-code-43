import re
from .multi_line_attribute import MultiLineAttribute


class Keywords(MultiLineAttribute):
    # TODO: split ',' and ' ', chomp \n and \"
    regex = re.compile(r'^\s*KEYWORDS:\s*$')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
