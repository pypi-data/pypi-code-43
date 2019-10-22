from . import language


Language = language.Language


class Walker:

    def __init__(self, content):
        self.content = content
        self.position = 0
        self.cursor = 0

    def __iter__(self):
        while not self.eof:
            item = self.content[self.cursor]
            self.cursor += 1
            yield item

    @property
    def length(self):
        return len(self.content)

    @property
    def eof(self):
        return self.cursor >= self.length

    @property
    def raw(self):
        return self.content

    @property
    def group(self):
        return self.content[self.position:self.cursor]

    @property
    def current(self):
        if self.eof:
            return Language.EOF
        if self.cursor < 0:
            self.cursor = 0
        return self.content[self.cursor]

    @property
    def peek(self):
        self.move()
        cur = self.current
        self.move(-1)
        return cur

    def size(self, item):
        return len(str(item))

    def snap(self):
        content = self.group
        self.position = self.cursor
        return content

    def move(self, spaces=1):
        self.cursor += spaces
        return None

    def consume_while(self, expression):
        while expression(self.current):
            self.move()
            if self.eof:
                break
        return None


class VerboseWalker(Walker):

    _padd = ' '
    _tokn = '+'

    def __str__(self):
        length = sum(map(self.size, self.group))
        padding = sum(map(self.size, self.content[:self.position]))
        line = self._padd * padding + self._tokn * length
        return f'{self.raw}\n{line}'
