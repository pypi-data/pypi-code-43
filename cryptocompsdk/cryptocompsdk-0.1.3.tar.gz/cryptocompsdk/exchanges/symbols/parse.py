from dataclasses import dataclass
from typing import List, Any, TypeVar, Callable, Type, cast, Optional, Dict, Union
import pandas as pd

from cryptocompsdk.general.parse import from_int, from_str, from_bool, from_list, to_class, from_union, from_none, \
    from_dict, from_plain_dict
from cryptocompsdk.response import ResponseException, ResponseAPIBase


@dataclass
class RateLimit:
    pass

    @staticmethod
    def from_dict(obj: Any) -> 'RateLimit':
        assert isinstance(obj, dict)
        return RateLimit()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


@dataclass
class ExchangesSymbols(ResponseAPIBase):
    response: Optional[str] = None
    message: Optional[str] = None
    has_warning: Optional[bool] = None
    param_with_error: Optional[str] = None
    type: Optional[int] = None
    rate_limit: Optional[RateLimit] = None
    data: Optional[dict] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ExchangesSymbols':
        assert isinstance(obj, dict)
        response = from_union([from_str, from_none], obj.get("Response"))
        message = from_union([from_str, from_none], obj.get("Message"))
        has_warning = from_union([from_bool, from_none], obj.get("HasWarning"))
        param_with_error = from_union([from_str, from_none], obj.get("ParamWithError"))
        type = from_union([from_int, from_none], obj.get("Type"))
        rate_limit = from_union([RateLimit.from_dict, from_none], obj.get("RateLimit"))
        data = from_union([from_plain_dict, from_none], obj.get("Data"))
        return ExchangesSymbols(response, message, has_warning, param_with_error, type, rate_limit, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Response"] = from_union([from_str, from_none], self.response)
        result["Message"] = from_union([from_str, from_none], self.message)
        result["HasWarning"] = from_union([from_bool, from_none], self.has_warning)
        result["ParamWithError"] = from_union([from_str, from_none], self.param_with_error)
        result["Type"] = from_union([from_int, from_none], self.type)
        result["RateLimit"] = from_union([lambda x: to_class(RateLimit, x), from_none], self.rate_limit)
        result["Data"] = from_union([from_plain_dict, from_none], self.data)
        return result

    def to_df(self) -> pd.DataFrame:
        df_list = []
        for exchange_name, exchange_dict in self.data.items():
            df_list.append(
                _exchange_dict_to_df(exchange_dict, exchange_name)
            )
        df = pd.concat(df_list, axis=0)
        return df.reset_index(drop=True)

    def to_history_query_dicts(self) -> List[Dict[str, str]]:
        df = self.to_df()
        query_dicts = []
        for idx, row in df.iterrows():
            query_dicts.append(dict(
                from_symbol=row['From Symbol'],
                to_symbol=row['To Symbol'],
                exchange=row['Exchange']
            ))
        return query_dicts


def exchanges_symbols_from_dict(s: Any) -> ExchangesSymbols:
    return ExchangesSymbols.from_dict(s)


def exchanges_symbols_to_dict(x: ExchangesSymbols) -> Any:
    return to_class(ExchangesSymbols, x)


class CouldNotGetExchangeSymbolsException(ResponseException):
    pass


def _exchange_dict_to_df(exchange_dict: Dict[str, Union[List[str], str]], exchange_name: str) -> pd.DataFrame:
    pairs_dict = exchange_dict['pairs']
    df = _pairs_dict_to_df(pairs_dict)
    df['Exchange'] = exchange_name
    df['Exchange is Active'] = exchange_dict.get('isActive')
    df['Exchange is Top Tier'] = exchange_dict.get('isTopTier')
    return df


def _pairs_dict_to_df(pairs_dict: Dict[str, List[str]]) -> pd.DataFrame:
    data_list = []
    for from_symbol, to_symbols in pairs_dict.items():
        for to_symbol in to_symbols:
            data_list.append(
                (from_symbol, to_symbol)
            )
    df = pd.DataFrame(data_list, columns=['From Symbol', 'To Symbol'])
    return df