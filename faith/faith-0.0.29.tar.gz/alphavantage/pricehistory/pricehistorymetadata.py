from typing import Any
from typing import Dict


class PriceHistoryMetadata(object):

    def __init__(
        self,
        information: str,
        symbol: str,
        output_size: str,
        last_refreshed: str,
        timezone: str,
    ) -> None:
        self._symbol = symbol
        self._information = information
        self._output_size = output_size
        self._last_refreshed = last_refreshed
        self._timezone = timezone

    @property
    def information(self) -> str:
        return self._information


def price_history_metadata_from_data(data: Dict[str, Any]) -> PriceHistoryMetadata:
    return PriceHistoryMetadata(
        information=data['1. Information'],
        symbol=data['2. Symbol'],
        last_refreshed=data['3. Last Refreshed'],
        output_size=data['4. Output Size'],
        timezone=data['5. Time Zone'],
    )
