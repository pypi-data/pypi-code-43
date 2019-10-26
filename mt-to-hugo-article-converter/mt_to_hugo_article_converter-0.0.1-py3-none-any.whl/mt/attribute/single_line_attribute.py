import re
from .attribute import Attribute


class SingleLineAttribute(Attribute):
    def set(self, line):
        match = self.regex.search(line)
        if match:
            groups = match.groups()
            if len(groups) == 1:
                self.value_ = groups[0]
                self.open = False
        return self


if __name__ == '__main__':
    import doctest
    doctest.testmod()
