from typing import Sequence, Optional

from cryptocompsdk.history.parse import HistoricalData, historical_data_from_dict, CouldNotGetHistoryException
from cryptocompsdk.request import APIBase
from cryptocompsdk.urls import DAILY_HISTORY_URL, HOURLY_HISTORY_URL, MINUTE_HISTORY_URL


class HistoryAPI(APIBase):
    _exception_class = CouldNotGetHistoryException

    def get(self, from_symbol: str = 'BTC', to_symbol: Sequence[str] = 'USD', freq: str = 'd',
            exchange: Optional[str] = None, aggregate: Optional[int] = None, end_time: Optional[int] = None,
            limit: int = 100, max_api_calls: Optional[int] = None) -> HistoricalData:
        url = self._get_api_url_from_freq(freq)

        payload = dict(
            fsym=from_symbol,
            tsym=to_symbol,
            e=exchange,
            aggregate=aggregate,
            limit=limit,
            toTs=end_time,
        )

        return super().get(url, payload, max_api_calls=max_api_calls)

    def _get_api_url_from_freq(self, freq: str) -> str:
        parsed_freq = freq.lower().strip()[0]
        if parsed_freq == 'd':
            return DAILY_HISTORY_URL
        elif parsed_freq == 'h':
            return HOURLY_HISTORY_URL
        elif parsed_freq == 'm':
            return MINUTE_HISTORY_URL
        else:
            raise ValueError(f'could not parse frequency {freq}, pass one of d, h, m')

    def _class_factory(self, data: dict):
        return historical_data_from_dict(data)
