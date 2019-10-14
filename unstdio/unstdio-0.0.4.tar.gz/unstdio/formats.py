import io
import sys


def direct(*args, **kwargs):
    return args


class DictFormatter(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 0
        self.w = 4

    def __call__(self, *args, **kwargs):
        comma = True
        result = ""
        if len(args) > 0:
            for arg in args:
                for a in arg:
                    if a == "{":
                        self.level += 1
                        Indent = " " * self.level * self.w
                        result += "{\n" + Indent
                    elif a == "}":
                        self.level -= 1
                        Indent = " " * self.level * self.w
                        result += "\n" + Indent
                        result += a
                    elif a == "\n":
                        Indent = " " * self.level * self.w
                        result += Indent
                    elif a == ",":
                        if comma:
                            result += ",\n"
                            Indent = " " * (
                                (self.level * self.w) - 1
                            )
                            result += Indent
                        else:
                            result += a
                    elif a == "(":
                        comma = False
                        result += a
                    elif a == ")":
                        comma = True
                        result += a
                    else:
                        result += a
        return [result]
