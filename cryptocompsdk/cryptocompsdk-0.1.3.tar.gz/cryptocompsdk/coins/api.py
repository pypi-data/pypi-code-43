from cryptocompsdk.coins.parse import coins_from_dict, CouldNotGetCoinsException, Coins
from cryptocompsdk.request import APIBase
from cryptocompsdk.urls import COIN_LIST_URL


class CoinsAPI(APIBase):
    _exception_class = CouldNotGetCoinsException

    def get(self) -> Coins:
        return super().get(COIN_LIST_URL)

    def _class_factory(self, data: dict):
        return coins_from_dict(data)
