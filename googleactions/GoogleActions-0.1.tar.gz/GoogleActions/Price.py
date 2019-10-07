from PyVoice.MyDict import MyDict, DictProperty
from . import PriceType
from .Money import Money


class Price(MyDict):
    """
    {
      "type": enum(PriceType),
      "amount": {
        object(Money)
      },
    }
    """
    type: PriceType = DictProperty('type', PriceType)
    amount: Money = DictProperty('amount', Money)

    def build(self, price_type: PriceType, amount: Money):

        self.amount = amount
        self.price_type = price_type

        return self
