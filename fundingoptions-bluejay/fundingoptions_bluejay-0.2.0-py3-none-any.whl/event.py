import datetime
from typing import Dict, List, Union

import attr
from typing_extensions import TypedDict

__all__ = ("AppReceived", "MatchOccurred", "ProductSelected")


@attr.s(slots=True)
class AppReceived:
    event_name = "application_received"

    app_id = attr.ib(type=str)
    occurred_on = attr.ib(type=datetime.datetime)

    def as_dict(self) -> dict:
        return attr.asdict(self)


MatchItem = TypedDict(
    "MatchItem",
    {
        "score": Union[None, int],
        "breakdown": Dict[str, Union[None, int]],
        "criteria": Dict[str, Dict[str, int]],
        "product_id": str,
        "product_name": str,
        "product_lender_name": str,
    },
)


@attr.s(slots=True)
class MatchOccurred:
    event_name = "match_occurred"

    app_id = attr.ib(type=str)
    occurred_on = attr.ib(type=datetime.datetime)
    input = attr.ib(type=Dict)
    matches = attr.ib(type=List[MatchItem])

    def as_dict(self) -> dict:
        return attr.asdict(self)


@attr.s(slots=True)
class ProductSelected:
    event_name = "product_selected"

    app_id = attr.ib(type=str)
    occurred_on = attr.ib(type=datetime.datetime)
    product_id = attr.ib(type=str)
    product_name = attr.ib(type=str)
    product_lender_name = attr.ib(type=str)

    def as_dict(self) -> dict:
        return attr.asdict(self)
