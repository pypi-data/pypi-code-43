import json
from os import environ
from time import sleep
from time import time
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from urllib.parse import urlencode
from urllib.request import urlopen

from alphavantage.pricehistory.pricehistory import price_history_from_data
from alphavantage.pricehistory.pricehistory import PriceHistory


class AlphaVantageClient(object):

    def __init__(self) -> None:
        self._cool_down_window = self._get_cool_down_window()
        self._last_request_time: Optional[float] = None

    def get_price_history(
        self,
        symbol: str,
        time_window: str,
        output_size: str,
    ) -> PriceHistory:
        symbol = symbol.upper()

        time_window = self._check_str_parameter_in_range(
            parameter_name='time_window',
            parameter_value=time_window,
            allowed_values={'daily', 'weekly', 'monthly'},
            enforce_upper_case=True,
        )

        output_size = self._check_str_parameter_in_range(
            parameter_name='output_size',
            parameter_value=output_size,
            allowed_values={'compact', 'full'},
            enforce_upper_case=False,
        )

        end_point = self._get_price_history_end_point(
            symbol=symbol,
            time_window=time_window,
            output_size=output_size,
        )

        data = self._get_url(url=end_point)
        price_history = price_history_from_data(data=data)

        return price_history

    def _get_url(self, url: str) -> Dict[str, Any]:
        self._cool_off()
        data: Dict[str, Any] = json.loads(urlopen(url).read().decode('utf-8'))
        return data

    def _get_price_history_end_point(
        self,
        symbol: str,
        time_window: str,
        output_size: str,
    ) -> str:
        parameters = {
            'function': f'TIME_SERIES_{time_window}_ADJUSTED',
            'symbol': symbol,
            'outputsize': output_size,
            'apikey': self._get_api_key(),
        }

        return self._get_end_point(url_parameters=parameters)

    def _get_end_point(self, url_parameters: Dict[str, str]) -> str:
        return 'https://www.alphavantage.co/query?' + urlencode(url_parameters)

    def _get_cool_down_window(self) -> int:
        key = 'ALPHAVANTAGE_COOL_DOWN_WINDOW'
        cool_down_window = environ.get(key)
        if cool_down_window is None:
            raise ValueError(
                f'Failed to get the Alphavantage Cool Down Window from the '
                f'environment variable `{key}`.',
            )
        return int(cool_down_window)

    def _get_api_key(self) -> str:
        key = 'ALPHAVANTAGE_API_KEY'
        api_key = environ.get(key)
        if api_key is None:
            raise ValueError(
                f'Failed to get the Alphavantage API Key from the environment '
                f'variable `{key}`.',
            )

        return api_key

    def _check_str_parameter_in_range(
        self,
        parameter_name: str,
        parameter_value: str,
        allowed_values: Set[str],
        enforce_upper_case: bool,
    ) -> str:
        allowed_value_list: List[str] = list(allowed_values)
        if parameter_value.lower() not in allowed_values:
            allowed_values_str = ', '.join([
                f'`{value}`'
                for value in allowed_value_list[:-1]
            ])
            last_value = allowed_value_list[-1]
            allowed_values_str = f'{allowed_values_str} or `{last_value}`'
            raise ValueError(
                f'Invalid value for the parameter `{parameter_name}` - only '
                f'{allowed_values_str} is accepted.',
            )

        if enforce_upper_case:
            parameter_value = parameter_value.upper()
        else:
            parameter_value = parameter_value.lower()

        return parameter_value

    def _cool_off(self) -> None:
        if self._last_request_time is not None:
            time_elapsed = time() - self._last_request_time
            if time_elapsed < self._cool_down_window:
                sleep(self._cool_down_window - time_elapsed)
        self._last_request_time = time()


avc = AlphaVantageClient()
