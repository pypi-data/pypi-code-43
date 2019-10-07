from PyVoice.MyDict import MyDict, DictProperty


class Date(MyDict):

    year: int = DictProperty('year', int)
    month: int = DictProperty('month', int)
    day: int = DictProperty('day', int)

    def build(self, year: int=None, month: int=None, day: int=None):
        self.year = year
        self.month = month
        self.day = day

        return self
