__all__ = ["ListExt"]


class ListExt(list):

    def __init__(self, lst):
        self.lst = lst

    def __repr__(self):
        return "[{}]".format(self.join(", "))

    def join(self, delimiter=","):
        _l = [str(x) for x in self.lst]
        return delimiter.join(_l)
