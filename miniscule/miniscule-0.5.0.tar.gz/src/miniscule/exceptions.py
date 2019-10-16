from yaml.parser import ParserError


class MinisculeError(ParserError):
    def __init__(self, tag, message):
        super().__init__()
        self.tag = tag
        self.message = message

    def __repr__(self):
        return "<{}(!{}, {})>".format(self.__class__.__name__, self.tag, self.message)
