import re
from .single_line_attribute import SingleLineAttribute


class Tags(SingleLineAttribute):
    regex = re.compile(r'^\s*TAGS:\s*(.*)\s*$')

    def value(self):
        v = super(Tags, self).value()
        if v:
            return v.replace('"', '').split(" ")
        return None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
