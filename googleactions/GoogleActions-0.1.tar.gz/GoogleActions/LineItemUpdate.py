from PyVoice.MyDict import MyDict, DictProperty
from .OrderState import OrderState
from .Price import Price
from .Extension import Extension
from .Money import Money
from . import PriceType


class LineItemUpdate(MyDict):
    """
    {
      "orderState": {
        object(OrderState)
      },
      "price": {
        object(Price)
      },
      "reason": string,
      "extension": {
        "@type": string,
        field1: ...,
        ...
      },
    }
    """
    order_state: OrderState = DictProperty('orderState', OrderState)
    price: Price = DictProperty('price', Price)
    reason: str = DictProperty('reason', str)
    extension: Extension = DictProperty('extension', Extension)

    def build(self, reason: str=None, price: Price=None, order_state: OrderState=None, extension: Extension=None):
        if reason is not None:
            self.reason = reason

        if price is not None:
            self.price = price

        if order_state is not None:
            self.order_state = order_state

        if extension is not None:
            self.extension = extension

        return self

    def add_order_state(self, state:str, label:str) -> OrderState:
        self.order_state = OrderState().build(state=state,label=label)
        return self.order_state

    def add_price(self, price_type:PriceType, amount, currency_code) -> Price:
        self.total_price = Price().build(price_type=price_type, amount=Money().build(amount=amount,
                                                                                     currency_code=currency_code))

        return self.price

    def add_extension(self, type:str, **kwargs) -> Extension:
        self.extension = Extension().build(type, **kwargs)
        return self.extension
