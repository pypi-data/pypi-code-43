import re
from .single_line_attribute import SingleLineAttribute


class Category(SingleLineAttribute):
    regex = re.compile(r'^\s*CATEGORY:\s*(.*)\s*$')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lines = set([])

    def is_empty(self):
        '''
        >>> Category().is_empty()
        True
        '''
        return len(self.lines) == 0

    def set(self, line):
        super(Category, self).set(line)
        if self.value_:
            self.lines.add(self.value_)
        return self

    def value(self):
        return list(self.lines)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
