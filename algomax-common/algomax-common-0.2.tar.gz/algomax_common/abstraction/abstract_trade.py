from abc import ABC, abstractmethod


class AbstractTrade(ABC):

    @abstractmethod
    def new_order(self, data: dict, query: str = None):
        pass

    @abstractmethod
    def edit_order(self, data: dict, query: str = None):
        pass

    @abstractmethod
    def cancel_order(self, order_id: str):
        pass

    @abstractmethod
    def get_order_list(self, query: str = None):
        pass

    @abstractmethod
    def get_trade_list(self, query: str = None):
        pass

    @abstractmethod
    def get_percentage_value_list(self, data: dict, query: str = None):
        pass

    @abstractmethod
    def get_last_bid_trade_list(self, query: str = None):
        pass

    @abstractmethod
    def get_last_trade_list(self, query: str = None):
        pass
