import re
from .attribute import Attribute


class MultiLineAttribute(Attribute):
    delimiter_regex = re.compile(r'^-----$')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.open = False
        self.lines = []
        self.current_line_is_delimiter = False
        self.last_line_was_delimiter = False

    def is_empty(self):
        '''
        >>> MultiLineAttribute().is_empty()
        True
        '''
        return len(self.lines) == 0

    def probe_delimiter(self, line):
        # save last status
        self.last_line_was_delimiter = self.current_line_is_delimiter

        match = self.delimiter_regex.match(line)
        self.current_line_is_delimiter = match != None

    def snag_on(self, line):
        if not self.last_line_was_delimiter:
            return
        match = self.regex.match(line)
        if match != None:
            self.open = True
            # print("snag on: {}".format(line))

    def snag_off(self, line):
        if self.open and self.current_line_is_delimiter:
            self.open = False
            # print("snag off: {}".format(line))

    def set(self, line):
        super(MultiLineAttribute, self).set(line)
        self.probe_delimiter(line)
        self.snag_off(line)
        if self.open:
            self.lines.append(line)
            # print("snagging: {}".format(line))
        self.snag_on(line)
        return self

    def value(self):
        return "".join(self.lines)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
