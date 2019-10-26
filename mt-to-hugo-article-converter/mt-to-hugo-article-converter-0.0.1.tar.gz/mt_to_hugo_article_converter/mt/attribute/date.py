import re
from dateutil.parser import parse
from .single_line_attribute import SingleLineAttribute


class Date(SingleLineAttribute):
    regex = re.compile(r'^\s*DATE:\s*(.*)\s*$')

    def value(self):
        v = super(Date, self).value()
        if v:
            return parse(v)
        return None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
