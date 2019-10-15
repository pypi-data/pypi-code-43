from QiDataProcessing.TradingFrame.TradingFrameHelper import TradingFrameHelper


class FutureExchangeTradingFrame:
    def __init__(self):
        self._id = ""
        self._name = ""
        self._trading_time = ""
        self._products = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def trading_time(self):
        return self._trading_time

    @trading_time.setter
    def trading_time(self, value):
        self._trading_time = value

    @property
    def products(self):
        return self._products

    @products.setter
    def products(self, value):
        self._products = value

    @property
    def trading_time_slices(self):
        return TradingFrameHelper.parse_time_slice(self._trading_time)
