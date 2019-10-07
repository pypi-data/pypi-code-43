from math import modf
from PyVoice.MyDict import MyDict, DictProperty


class Money(MyDict):

    units: str = DictProperty('units', str)
    currency_code: str = DictProperty('currencyCode', str)
    nanos: int = DictProperty('nanos', int)

    def build(self, amount:float, currency_code: str):
        nanos, self.units = modf(amount)
        self.nanos = int(nanos * pow(10,9))
        self.currency_code = currency_code
        return self
