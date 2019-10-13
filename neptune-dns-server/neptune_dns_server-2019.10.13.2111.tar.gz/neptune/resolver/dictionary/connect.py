from .resolver import Resolver


class Connection:

    def __init__(self, loop, dictionary):
        self.loop = loop
        self.dictionary = dictionary
        self.Resolver = Resolver(self)
