# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = exchanges_info_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Optional, Any, List, Dict, TypeVar, Type, Callable, cast

from cryptocompsdk.general.parse import from_int, from_none, from_union, from_float, from_str, to_float, from_bool, \
    from_dict, to_class, is_type, from_int_or_str, from_na, from_str_number, from_list, from_plain_dict
from cryptocompsdk.response import ResponseAPIBase, ResponseException

T = TypeVar("T")


@dataclass
class GradePointsSplit:
    trade_surveillance: Optional[float] = None
    geography: Optional[float] = None
    legal: Optional[float] = None
    investment: Optional[float] = None
    team: Optional[float] = None
    data: Optional[float] = None
    market_quality: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'GradePointsSplit':
        assert isinstance(obj, dict)
        trade_surveillance = from_union([from_str_number, from_none], obj.get("TradeSurveillance"))
        geography = from_union([from_str_number, from_none], obj.get("Geography"))
        legal = from_union([from_str_number, from_none], obj.get("Legal"))
        investment = from_union([from_str_number, from_none], obj.get("Investment"))
        team = from_union([from_str_number, from_none], obj.get("Team"))
        data = from_union([from_str_number, from_none], obj.get("Data"))
        market_quality = from_union([from_str_number, from_none], obj.get("MarketQuality"))
        return GradePointsSplit(trade_surveillance, geography, legal, investment, team, data, market_quality)

    def to_dict(self) -> dict:
        result: dict = {}
        result["TradeSurveillance"] = from_union([from_float, from_int, from_none], self.trade_surveillance)
        result["Geography"] = from_union([from_float, from_int, from_none], self.geography)
        result["Legal"] = from_union([from_float, from_int, from_none], self.legal)
        result["Investment"] = from_union([from_float, from_int, from_none], self.investment)
        result["Team"] = from_union([from_float, from_int, from_none], self.team)
        result["Data"] = from_union([from_float, from_int, from_none], self.data)
        result["MarketQuality"] = from_union([from_float, from_int, from_none], self.market_quality)
        return result


@dataclass
class Rating:
    one: Optional[int] = None
    two: Optional[int] = None
    three: Optional[int] = None
    four: Optional[int] = None
    five: Optional[int] = None
    avg: Optional[float] = None
    total_users: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Rating':
        assert isinstance(obj, dict)
        one = from_union([from_int, from_none], obj.get("One"))
        two = from_union([from_int, from_none], obj.get("Two"))
        three = from_union([from_int, from_none], obj.get("Three"))
        four = from_union([from_int, from_none], obj.get("Four"))
        five = from_union([from_int, from_none], obj.get("Five"))
        avg = from_union([from_float, from_none], obj.get("Avg"))
        total_users = from_union([from_int, from_none], obj.get("TotalUsers"))
        return Rating(one, two, three, four, five, avg, total_users)

    def to_dict(self) -> dict:
        result: dict = {}
        result["One"] = from_union([from_int, from_none], self.one)
        result["Two"] = from_union([from_int, from_none], self.two)
        result["Three"] = from_union([from_int, from_none], self.three)
        result["Four"] = from_union([from_int, from_none], self.four)
        result["Five"] = from_union([from_int, from_none], self.five)
        result["Avg"] = from_union([to_float, from_none], self.avg)
        result["TotalUsers"] = from_union([from_int, from_none], self.total_users)
        return result


@dataclass
class ExchangeInfo:
    id: Optional[int] = None
    sort_order: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    logo_url: Optional[str] = None
    item_type: Optional[List[str]] = None
    centralization_type: Optional[str] = None
    internal_name: Optional[str] = None
    grade_points: Optional[str] = None
    grade: Optional[str] = None
    grade_points_split: Optional[GradePointsSplit] = None
    affiliate_url: Optional[str] = None
    country: Optional[str] = None
    order_book: Optional[bool] = None
    trades: Optional[bool] = None
    description: Optional[str] = None
    full_address: Optional[str] = None
    fees: Optional[str] = None
    deposit_methods: Optional[str] = None
    withdrawal_methods: Optional[str] = None
    sponsored: Optional[bool] = None
    recommended: Optional[bool] = None
    rating: Optional[Rating] = None
    totalvolume24_h: Optional[Dict[str, int]] = None
    displaytotalvolume24_h: Optional[Dict[str, str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ExchangeInfo':
        assert isinstance(obj, dict)
        id = from_union([from_none, lambda x: int(from_str(x))], obj.get("Id"))
        sort_order = from_union([from_none, lambda x: int(from_str(x))], obj.get("SortOrder"))
        name = from_union([from_str, from_none], obj.get("Name"))
        url = from_union([from_str, from_none], obj.get("Url"))
        logo_url = from_union([from_str, from_none], obj.get("LogoUrl"))
        item_type = from_union([lambda x: from_list(from_str, x), from_none], obj.get("ItemType"))
        centralization_type = from_union([from_str, from_none], obj.get("CentralizationType"))
        internal_name = from_union([from_str, from_none], obj.get("InternalName"))
        grade_points = from_union([from_str, from_none], obj.get("GradePoints"))
        grade = from_union([from_str, from_none], obj.get("Grade"))
        grade_points_split = from_union([GradePointsSplit.from_dict, from_none], obj.get("GradePointsSplit"))
        affiliate_url = from_union([from_str, from_none], obj.get("AffiliateURL"))
        country = from_union([from_str, from_none], obj.get("Country"))
        order_book = from_union([from_bool, from_none], obj.get("OrderBook"))
        trades = from_union([from_bool, from_none], obj.get("Trades"))
        description = from_union([from_str, from_none], obj.get("Description"))
        full_address = from_union([from_str, from_none], obj.get("FullAddress"))
        fees = from_union([from_str, from_none], obj.get("Fees"))
        deposit_methods = from_union([from_str, from_none], obj.get("DepositMethods"))
        withdrawal_methods = from_union([from_str, from_none], obj.get("WithdrawalMethods"))
        sponsored = from_union([from_bool, from_none], obj.get("Sponsored"))
        recommended = from_union([from_bool, from_none], obj.get("Recommended"))
        rating = from_union([Rating.from_dict, from_none], obj.get("Rating"))
        totalvolume24_h = from_union([from_plain_dict, from_none], obj.get("TOTALVOLUME24H"))
        displaytotalvolume24_h = from_union([from_plain_dict, from_none], obj.get("DISPLAYTOTALVOLUME24H"))
        return ExchangeInfo(id, sort_order, name, url, logo_url, item_type, centralization_type, internal_name,
                            grade_points, grade, grade_points_split, affiliate_url, country, order_book, trades,
                            description, full_address, fees, deposit_methods, withdrawal_methods, sponsored,
                            recommended, rating, totalvolume24_h, displaytotalvolume24_h)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Id"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                   lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.id)
        result["SortOrder"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                          lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                         self.sort_order)
        result["Name"] = from_union([from_str, from_none], self.name)
        result["Url"] = from_union([from_str, from_none], self.url)
        result["LogoUrl"] = from_union([from_str, from_none], self.logo_url)
        result["ItemType"] = from_union([lambda x: from_list(from_str, x), from_none], self.item_type)
        result["CentralizationType"] = from_union([from_str, from_none], self.centralization_type)
        result["InternalName"] = from_union([from_str, from_none], self.internal_name)
        result["GradePoints"] = from_union([from_str, from_none], self.grade_points)
        result["Grade"] = from_union([from_str, from_none], self.grade)
        result["GradePointsSplit"] = from_union([lambda x: to_class(GradePointsSplit, x), from_none],
                                                self.grade_points_split)
        result["AffiliateURL"] = from_union([from_str, from_none], self.affiliate_url)
        result["Country"] = from_union([from_str, from_none], self.country)
        result["OrderBook"] = from_union([from_bool, from_none], self.order_book)
        result["Trades"] = from_union([from_bool, from_none], self.trades)
        result["Description"] = from_union([from_str, from_none], self.description)
        result["FullAddress"] = from_union([from_str, from_none], self.full_address)
        result["Fees"] = from_union([from_str, from_none], self.fees)
        result["DepositMethods"] = from_union([from_str, from_none], self.deposit_methods)
        result["WithdrawalMethods"] = from_union([from_str, from_none], self.withdrawal_methods)
        result["Sponsored"] = from_union([from_bool, from_none], self.sponsored)
        result["Recommended"] = from_union([from_bool, from_none], self.recommended)
        result["Rating"] = from_union([lambda x: to_class(Rating, x), from_none], self.rating)
        result["TOTALVOLUME24H"] = from_union([from_plain_dict, from_none], self.totalvolume24_h)
        result["DISPLAYTOTALVOLUME24H"] = from_union([from_plain_dict, from_none], self.displaytotalvolume24_h)
        return result


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
class ExchangesInfo(ResponseAPIBase):
    response: Optional[str] = None
    message: Optional[str] = None
    param_with_error: Optional[str] = None
    has_warning: Optional[bool] = None
    type: Optional[int] = None
    rate_limit: Optional[RateLimit] = None
    data: Optional[Dict[str, ExchangeInfo]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ExchangesInfo':
        assert isinstance(obj, dict)
        response = from_union([from_str, from_none], obj.get("Response"))
        message = from_union([from_str, from_none], obj.get("Message"))
        param_with_error = from_union([from_str, from_none], obj.get("ParamWithError"))
        has_warning = from_union([from_bool, from_none], obj.get("HasWarning"))
        type = from_union([from_int, from_none], obj.get("Type"))
        rate_limit = from_union([RateLimit.from_dict, from_none], obj.get("RateLimit"))
        data = from_union([lambda x: from_dict(ExchangeInfo.from_dict, x), from_none], obj.get("Data"))
        return ExchangesInfo(response, message, param_with_error, has_warning, type, rate_limit, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Response"] = from_union([from_str, from_none], self.response)
        result["Message"] = from_union([from_str, from_none], self.message)
        result["ParamWithError"] = from_union([from_str, from_none], self.param_with_error)
        result["HasWarning"] = from_union([from_bool, from_none], self.has_warning)
        result["Type"] = from_union([from_int, from_none], self.type)
        result["RateLimit"] = from_union([lambda x: to_class(RateLimit, x), from_none], self.rate_limit)
        result["Data"] = from_union([lambda x: from_dict(lambda x: to_class(ExchangeInfo, x), x), from_none], self.data)
        return result


def exchanges_info_from_dict(s: Any) -> ExchangesInfo:
    return ExchangesInfo.from_dict(s)


def exchanges_info_to_dict(x: ExchangesInfo) -> Any:
    return to_class(ExchangesInfo, x)


class CouldNotGetExchangeInfoException(ResponseException):
    pass
