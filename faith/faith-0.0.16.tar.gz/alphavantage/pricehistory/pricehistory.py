from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from alphavantage.pricehistory.pricehistoryitem import price_history_item_from_data
from alphavantage.pricehistory.pricehistoryitem import PriceHistoryItem
from alphavantage.pricehistory.pricehistorymetadata import price_history_metadata_from_data
from alphavantage.pricehistory.pricehistorymetadata import PriceHistoryMetadata


class PriceHistory(object):

    def __init__(
        self,
        metadata: PriceHistoryMetadata,
        time_series: 'OrderedDict[str, PriceHistoryItem]',
    ) -> None:
        self._metadata = metadata
        self._time_series = time_series

    @property
    def metadata(self) -> PriceHistoryMetadata:
        return self._metadata

    @property
    def time_series(self) -> 'OrderedDict[str, PriceHistoryItem]':
        return self._time_series


def price_history_from_data(data: Dict[str, Any]) -> PriceHistory:
    metadata = price_history_metadata_from_data(data['Meta Data'])
    time_series_data = data['Time Series (Daily)']
    rows: List[Tuple[str, PriceHistoryItem]] = []
    for ds, data in time_series_data.items():
        rows.append((ds, price_history_item_from_data(data)))

    time_series: OrderedDict[str, PriceHistoryItem] = OrderedDict()
    for ds, price_history_item in sorted(rows, key=lambda x: x[0]):
        time_series[ds] = price_history_item

    return PriceHistory(
        metadata=metadata,
        time_series=time_series,
    )
