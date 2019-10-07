from PyVoice.MyDict import MyDict, DictProperty


class DateTime(MyDict):

    date: str = DictProperty('date', str)
    time: str = DictProperty('time', str)

    def build(self, time:str, date:str):
        self.time = time
        self.date = date

        return self