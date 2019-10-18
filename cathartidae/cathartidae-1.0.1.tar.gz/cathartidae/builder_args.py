class BuilderArgs(object):
    def __init__(self, operand, default, func):
        self.operand = operand
        self.default = default
        self.func    = func
        if type(self.func) in (classmethod, staticmethod):
            self.func = self.func.__get__(None, self.func.__class__)

    def get(self, builder_key, default=None):
        return getattr(self, builder_key, default)
