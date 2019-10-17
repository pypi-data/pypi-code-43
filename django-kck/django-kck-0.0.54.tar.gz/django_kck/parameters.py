class BaseParameter(object):
    name = None

    def __init__(self, name):
        self.name = name

    def to_str(self, v):
        return str(v)

    def from_str(self, s):
        return s


class StringParameter(BaseParameter):
    pass


class IntegerParameter(BaseParameter):
    def from_str(self, s):
        return int(s)


