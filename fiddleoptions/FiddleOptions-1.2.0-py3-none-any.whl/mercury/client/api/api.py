
# todo: placeholder

class Api(object):

    def __init__(self):
        self.marketdata_api = None
        self.fiddle_api = None
        self.tradeservice_api = None

    @property
    def market(self):
        return self.marketdata_api

    @property
    def fiddle(self):
        return self.fiddle_api

    @property
    def trade(self):
        return self.tradeservice_api