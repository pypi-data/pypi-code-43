from PyVoice.MyDict import MyDict, DictProperty


class TimeOfDay(MyDict):
    nanos: int = DictProperty('nanos', int)
    minutes: int = DictProperty('minutes', int)
    hours: int = DictProperty('hours', int)
    seconds: int = DictProperty('seconds', int)

    def build(self, nanos: int=0, minutes: int=0, hours: int=0, seconds: int=0):
        self.nanos = nanos
        self.minutes = minutes
        self.hours = hours
        self.seconds = seconds
        return self
