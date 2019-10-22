from copy import deepcopy
from typing import Any, List, Optional

import pandas as pd

from cryptocompsdk.general.parse import from_int, from_none, from_union, from_float, from_str, to_float, from_bool, \
    from_list, to_class
from cryptocompsdk.response import ResponseAPIBase, ResponseException


class HistoryRecord:
    time: Optional[int]
    high: Optional[float]
    low: Optional[float]
    open: Optional[float]
    volumefrom: Optional[float]
    volumeto: Optional[float]
    close: Optional[float]
    conversion_type: Optional[str]
    conversion_symbol: Optional[str]

    def __init__(self, time: Optional[int], high: Optional[float], low: Optional[float], open: Optional[float],
                 volumefrom: Optional[float], volumeto: Optional[float], close: Optional[float],
                 conversion_type: Optional[str], conversion_symbol: Optional[str]) -> None:
        self.time = time
        self.high = high
        self.low = low
        self.open = open
        self.volumefrom = volumefrom
        self.volumeto = volumeto
        self.close = close
        self.conversion_type = conversion_type
        self.conversion_symbol = conversion_symbol

    @staticmethod
    def from_dict(obj: Any) -> 'HistoryRecord':
        assert isinstance(obj, dict)
        time = from_union([from_int, from_none], obj.get("time"))
        high = from_union([from_float, from_none], obj.get("high"))
        low = from_union([from_float, from_none], obj.get("low"))
        open = from_union([from_float, from_none], obj.get("open"))
        volumefrom = from_union([from_float, from_none], obj.get("volumefrom"))
        volumeto = from_union([from_float, from_none], obj.get("volumeto"))
        close = from_union([from_float, from_none], obj.get("close"))
        conversion_type = from_union([from_str, from_none], obj.get("conversionType"))
        conversion_symbol = from_union([from_str, from_none], obj.get("conversionSymbol"))
        return HistoryRecord(time, high, low, open, volumefrom, volumeto, close, conversion_type, conversion_symbol)

    def to_dict(self) -> dict:
        result: dict = {}
        result["time"] = from_union([from_int, from_none], self.time)
        result["high"] = from_union([to_float, from_none], self.high)
        result["low"] = from_union([to_float, from_none], self.low)
        result["open"] = from_union([to_float, from_none], self.open)
        result["volumefrom"] = from_union([to_float, from_none], self.volumefrom)
        result["volumeto"] = from_union([to_float, from_none], self.volumeto)
        result["close"] = from_union([to_float, from_none], self.close)
        result["conversionType"] = from_union([from_str, from_none], self.conversion_type)
        result["conversionSymbol"] = from_union([from_str, from_none], self.conversion_symbol)
        return result

    @property
    def is_empty(self) -> bool:
        is_empty_cols = [
            'high',
            'low',
            'open',
            'volumefrom',
            'volumeto',
            'close',
        ]
        for col in is_empty_cols:
            if getattr(self, col) != 0:
                return False
        return True


class Data:
    aggregated: Optional[bool]
    time_from: Optional[int]
    time_to: Optional[int]
    data: Optional[List[HistoryRecord]]

    def __init__(self, aggregated: Optional[bool], time_from: Optional[int], time_to: Optional[int],
                 data: Optional[List[HistoryRecord]]) -> None:
        self.aggregated = aggregated
        self.time_from = time_from
        self.time_to = time_to
        self.data = data

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        assert isinstance(obj, dict)
        aggregated = from_union([from_bool, from_none], obj.get("Aggregated"))
        time_from = from_union([from_int, from_none], obj.get("TimeFrom"))
        time_to = from_union([from_int, from_none], obj.get("TimeTo"))
        data = from_union([lambda x: from_list(HistoryRecord.from_dict, x), from_none], obj.get("Data"))
        return Data(aggregated, time_from, time_to, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Aggregated"] = from_union([from_bool, from_none], self.aggregated)
        result["TimeFrom"] = from_union([from_int, from_none], self.time_from)
        result["TimeTo"] = from_union([from_int, from_none], self.time_to)
        result["Data"] = from_union([lambda x: from_list(lambda x: to_class(HistoryRecord, x), x), from_none],
                                    self.data)
        return result

    def __add__(self, other):
        out_obj = deepcopy(self)
        out_obj.data += other.data
        out_obj.time_from = min(out_obj.time_from, other.time_from)
        out_obj.time_to = max(out_obj.time_to, other.time_to)
        return out_obj

    def __radd__(self, other):
        out_obj = deepcopy(other)
        out_obj.data += self.data
        out_obj.time_from = min(out_obj.time_from, self.time_from)
        out_obj.time_to = max(out_obj.time_to, self.time_to)
        return out_obj


class RateLimit:
    pass

    def __init__(self, ) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> 'RateLimit':
        assert isinstance(obj, dict)
        return RateLimit()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


class HistoricalData(ResponseAPIBase):
    response: Optional[str]
    message: Optional[str]
    param_with_error: Optional[str]
    has_warning: Optional[bool]
    type: Optional[int]
    rate_limit: Optional[RateLimit]
    data: Optional[Data]

    def __init__(self, response: Optional[str], message: Optional[str], param_with_error: Optional[str],
                 has_warning: Optional[bool], type: Optional[int], rate_limit: Optional[RateLimit],
                 data: Optional[Data]) -> None:
        self.response = response
        self.message = message
        self.param_with_error = param_with_error
        self.has_warning = has_warning
        self.type = type
        self.rate_limit = rate_limit
        self.data = data

    @staticmethod
    def from_dict(obj: Any) -> 'HistoricalData':
        assert isinstance(obj, dict)
        response = from_union([from_str, from_none], obj.get("Response"))
        message = from_union([from_str, from_none], obj.get("Message"))
        param_with_error = from_union([from_str, from_none], obj.get("ParamWithError"))
        has_warning = from_union([from_bool, from_none], obj.get("HasWarning"))
        type = from_union([from_int, from_none], obj.get("Type"))
        rate_limit = from_union([RateLimit.from_dict, from_none], obj.get("RateLimit"))
        data = from_union([Data.from_dict, from_none], obj.get("Data"))
        return HistoricalData(response, message, param_with_error, has_warning, type, rate_limit, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Response"] = from_union([from_str, from_none], self.response)
        result["Message"] = from_union([from_str, from_none], self.message)
        result["ParamWithError"] = from_union([from_str, from_none], self.param_with_error)
        result["HasWarning"] = from_union([from_bool, from_none], self.has_warning)
        result["Type"] = from_union([from_int, from_none], self.type)
        result["RateLimit"] = from_union([lambda x: to_class(RateLimit, x), from_none], self.rate_limit)
        result["Data"] = from_union([lambda x: to_class(Data, x), from_none], self.data)
        return result

    def to_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self.to_dict()['Data']['Data'])
        df['time'] = df['time'].apply(pd.Timestamp.fromtimestamp)
        return df

    # Pagination methods

    @property
    def is_empty(self) -> bool:
        for record in self.data.data:
            if not record.is_empty:
                return False

        return True

    def __add__(self, other):
        out_obj = deepcopy(self)
        out_obj.data += other.data
        return out_obj

    def __radd__(self, other):
        out_obj = deepcopy(other)
        out_obj.data += self.data
        return out_obj

    @property
    def time_from(self) -> int:
        return self.data.time_from

    def delete_record_matching_time(self, time: int):
        times = [record.time for record in self.data.data]
        try:
            idx = times.index(time)
        except ValueError:
            raise CouldNotGetHistoryException(f'tried removing overlapping time {time} but was not in data')
        del self.data.data[idx]

    def trim_empty_records_at_beginning(self):
        self.data.data.reverse()  # now earliest records are at end

        # Delete, starting from end, oldest record
        for i, record in reversed(list(enumerate(self.data.data))):
            if record.is_empty:
                del self.data.data[i]
            else:
                # First non-empty record from end, we have now hit the actual data section, stop deleting
                break

        self.data.data.reverse()  # restore original order, earliest records at beginning



def historical_data_from_dict(s: Any) -> HistoricalData:
    return HistoricalData.from_dict(s)


def historical_data_to_dict(x: HistoricalData) -> Any:
    return to_class(HistoricalData, x)


class CouldNotGetHistoryException(ResponseException):
    pass