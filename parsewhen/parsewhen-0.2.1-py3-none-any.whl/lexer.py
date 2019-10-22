from . import walker, language, errors

from collections.abc import Mapping


Language = language.Language


class Lexer(walker.Walker, errors.LazyErrors):

    _wordmap = language.LANGMAP

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        errors.LazyErrors.__init__(self)

    @property
    def wordmap(self):
        output = {}
        for kind, words in self._wordmap.items():
            if isinstance(words, list):
                output.update({word: kind for word in words})

            elif isinstance(words, Mapping):
                output.update({word: kind|k for k, word in words.items()})
        return output

    def __iter__(self):
        for token in self.lex():
            value = self.group

            if len(value) == 0:
                continue

            if token == Language.WORD:
                token = self.wordmap.get(value.lower(), token)

            yield (token, value)

            self.snap()

        yield (Language.EOF, Language.EOF)

    def lex(self):
        for char in super().__iter__():

            if char.isnumeric():
                yield self.lex_numeric()
                continue

            if char.isalpha():
                self.consume_while(str.isalpha)
                yield Language.WORD
                continue

            if char.isspace():
                self.consume_while(str.isspace)
                yield Language.WORD
                continue

        yield Language.WORD

    def lex_numeric(self):
        self.consume_while(str.isnumeric)

        if self.current == ':' and str(self.peek).isnumeric():
            self.move()
            self.consume_while(str.isnumeric)

        if self.current == '.' and str(self.peek).isnumeric():
            self.move()
            self.consume_while(str.isnumeric)

        if len(self.group) == 4 and self.group.isnumeric():
            return Language.YEAR

        return Language.DIGIT if self.group.isnumeric() else Language.TIME
