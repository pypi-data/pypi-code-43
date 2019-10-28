class FutureTradingFrame:
    def __init__(self):
        self._exchanges = []

    @property
    def exchanges(self):
        return self._exchanges

    @exchanges.setter
    def exchanges(self, value):
        self._exchanges = value
