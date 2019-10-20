from typing import Optional

from cryptocompsdk.exchanges.symbols.parse import ExchangesSymbols, CouldNotGetExchangeSymbolsException, exchanges_symbols_from_dict
from cryptocompsdk.request import APIBase
from cryptocompsdk.urls import ALL_EXCHANGE_URL


class ExchangeSymbolsAPI(APIBase):
    _exception_class = CouldNotGetExchangeSymbolsException

    def get(self, from_symbol: Optional[str] = None, exchange: Optional[str] = None, top_tier_only: bool = False
            ) -> ExchangesSymbols:

        payload = dict(
            fsym=from_symbol,
            e=exchange,
            topTier=top_tier_only
        )

        return super().get(ALL_EXCHANGE_URL, payload)

    def _class_factory(self, data: dict) -> ExchangesSymbols:
        return exchanges_symbols_from_dict(data)
