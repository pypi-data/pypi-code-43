import datetime

from . import walker, language, errors


Language = language.Language


class Parser(walker.Walker, errors.LazyErrors):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        errors.LazyErrors.__init__(self)

    def __iter__(self):
        for item in self.parse():
            yield item

            self.snap() # I call it... mercy.

    @property
    def raw(self):
        return ''.join(str(value) for k, value in self.content if k != Language.EOF)

    @property
    def current(self):
        cur = super().current
        if cur == Language.EOF:
            return Language.EOF, Language.EOF
        return cur

    @property
    def kind(self):
        kind, _ = self.current
        return kind

    def size(self, item):
        kind, me = item
        if kind == Language.EOF:
            me = str(me)
        return super().size(me)

    def movewhile(self, expression, direction=1):
        while expression():
            self.move(direction)
        self.move(direction)
        return None

    def backup(self, kind):
        while len(self.group) != 0:
            knd, _ = self.group[-1]
            if knd != kind:
                break
            self.move(-1)
        return None

    def parse(self):
        datetime = Language.DAY | Language.WEEK | Language.MONTH | Language.YEAR | Language.DATE | Language.TIME
        timedelta = Language.DURATION

        for kind, value in super().__iter__():

            if kind == Language.EOF:
                break

            # Unknown digit, it could be a duration or a date / time.
            if kind == Language.DIGIT:
                yield self.parse_digit()

            elif bool(kind & datetime):
                self.move(-1)
                yield self.parse_datetime()

            elif bool(kind & timedelta):
                self.move(-1)
                yield self.parse_duration()

            elif kind == Language.WORD:
                self.movewhile(lambda: self.kind & Language.WORD)
                self.move(-1)
                yield self.group
            else:
                value = branch_values(self.group)
                err = errors.ErrorSource(f'Unknown kind: {str(kind)}',
                                         source=''.join(value))
                self.error(err)

    def parse_digit(self):
        kind = self.kind
        backup = -1

        if kind == Language.WORD:
            nxt, _ = self.peek
            kind = nxt

        if kind == Language.DURATION|Language.SUFFIX:
            self.move(backup)
            return self.parse_duration()

        elif (kind == Language.DATE|Language.SUFFIX
        or kind == Language.TIME|Language.SUFFIX):
            self.move(backup)
            return self.parse_datetime()

        else:
            self.move(backup)
            kind, value = self.current
            self.move()
            
            err = errors.ErrorSource(f'Could not parse digit:', source=value)
            self.error(err)
            return [(kind, value)]
        return None

    def parse_duration(self):
        collection = []
        datetime = Language.DAY | Language.WEEK | Language.MONTH | Language.YEAR | Language.DATE | Language.TIME

        while not self.eof:
            kind, value = self.current
            self.move()

            if kind == Language.EOF or bool(kind & Language.BREAKPOINT):
                break

            if kind == Language.WORD:
                continue

            if (bool(kind & Language.PREFIX) and len(collection) != 0
            or bool(kind & datetime)):
                self.move(-1)
                break

            if kind & Language.SUFFIX and any(value == v for k, v in self.group[:-1] if bool(k & Language.SUFFIX)):
                self.move(-2)
                collection.pop(-1)
                break

            if kind == Language.DIGIT:
                knd, val = self.current

                offset = 1
                if self.kind == Language.WORD:
                    knd, val = self.peek
                    offset += 1

                if (knd in [Language.WORD, Language.EOF, Language.WORD|Language.BREAKPOINT]
                or bool(knd & datetime)):
                    self.move(-1)
                    break

                if bool(knd & Language.SUFFIX) and any(val == v for _, v in self.group[:-1]):
                    self.move(-1)
                    break

                collection.append(((kind|knd) ^ (Language.SUFFIX|Language.PREFIX), [(kind, value), (knd, val)]))
                self.move(offset)
                continue

            collection.append((kind, value))

        self.backup(Language.WORD)
        return collection

    def parse_datetime(self):
        collection = []
        timedelta = Language.DURATION

        while not self.eof:
            kind, value = self.current
            self.move()

            if kind == Language.EOF or bool(kind & Language.BREAKPOINT):
                break

            if kind == Language.WORD:
                continue


            if (kind in [Language.DIGIT, Language.TIME]
            or kind == Language.RELATIVE|Language.DATE|Language.PREFIX):
                knd, val = self.current

                offset = 1
                if self.kind == Language.WORD:
                    knd, val = self.peek
                    offset += 1

                if knd == Language.DAY:
                    knd |= Language.SUFFIX

                if bool(kind & Language.PREFIX) and not bool(knd & Language.SUFFIX):
                    self.move(-1)
                    break

                if (knd in [Language.WORD, Language.EOF, Language.WORD|Language.BREAKPOINT]
                or (kind == Language.DIGIT and (bool(knd & timedelta) and bool(knd & Language.SUFFIX)))):
                    self.move(-1)
                    break

                if ((knd == Language.TIME|Language.SUFFIX and any(knd in [Language.DIGIT, Language.TIME] for knd, _ in self.group[:-1]))
                or bool(knd & Language.SUFFIX) and any(val == v for _, v in self.group[:-1])):
                    self.move(-1)
                    break

                collection.append(((kind|knd) ^ (Language.SUFFIX | Language.PREFIX), [(kind, value), (knd, val)]))
                self.move(offset)
                continue

            elif any(kind == k for k, _ in self.group[:-1]):
                break

            collection.append((kind, value))

        self.backup(Language.WORD)
        return collection


def tree_values(tree):
    for branch in tree:
        yield list(branch_values(branch))


def branch_values(branch):
    for (kind, value) in branch:
        if isinstance(value, list):
            yield list(branch_values(value))
        else:
            yield value
