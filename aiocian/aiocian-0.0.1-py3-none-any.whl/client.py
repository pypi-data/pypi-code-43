from .constants import *
from .exceptions import IncorrectPlaces
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Sequence, Union


class Search:
    API_HOST = "https://api.cian.ru"
    # COUNT_URL = "/cian-api/site/v1/offers/search/meta/"
    SEARCH_URL = "/search-offers/v2/search-offers-desktop/"

    def __init__(self, session: aiohttp.ClientSession, region: str, action: str,
                 places: Sequence[str], offer_owner: Union[str, None]=None, rooms: Sequence[str]=(),
                 min_bedrooms: Union[int, None]=None, max_bedrooms: Union[int, None]=None,
                 building_status: Union[str, None]=None, min_price: Union[float, None]=None,
                 max_price: Union[float, None]=None, currency: Union[str, None]=None,
                 square_meter_price: bool=False, min_square: Union[float, None]=None,
                 max_square: Union[float, None]=None,  by_homeowner: bool=False,
                 start_page: int=1, end_page: Union[int, None]=None, limit: Union[int, None]=None):
        self.session = session
        self.region = region
        self.action = action
        self.places = places
        self.offer_owner = offer_owner
        self.rooms = rooms
        self.min_bedrooms = min_bedrooms
        self.max_bedrooms = max_bedrooms
        self.building_status = building_status
        self.min_price = min_price
        self.max_price = max_price
        self.currency = currency
        self.square_meter_price = square_meter_price
        self.min_square = min_square
        self.max_square = max_square
        self.by_homeowner = by_homeowner
        self.start_page = start_page
        self.end_page = end_page
        self.limit = limit
        self._count = None
        self._page = start_page - 1
        self._results_count = 0 
        self._results = []

    def __len__(self):
        return self._count

    def __iter__(self):
        return self

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.limit is not None and self.limit < self._results_count:
            raise StopAsyncIteration
        self._results_count += 1

        if self._results:
            return self._results.pop(0)

        self._page += 1
        if self.end_page is not None and self._page == self.end_page:
            raise StopAsyncIteration  

        request_data = {
            "url": self.API_HOST + self.SEARCH_URL,
            "json": {"jsonQuery": self._search_data()},
        }
        async with self.session.post(**request_data) as response:
            data = (await response.json())["data"]

        self._count = data["offerCount"]
        self._results = data["offersSerialized"]

        return self._results.pop(0)

    def _search_data(self):
        places_set = set(self.places)
        
        data = {
            "region": {"type": "terms", "value": [REGIONS[self.region]]},
            "engine_version": {"type": "term", "value": 2},
        }

        if self.action == BUY and places_set <= {FLAT}:
            data["_type"] = "flatsale"
            if self.building_status is not None:
                data["building_status"] = {"type": "terms", "value": USED[self.building_status]}
            if self.square_meter_price:
                data["price_sm"] = {"type": "term", "value": True}
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == BUY and places_set <= {ROOM, PART}:
            data["_type"] = "flatsale"
            data["room"] = {"type": "terms", "value": []}
            while places_set:
                data["room"]["value"].append(PLACES[places_set.pop()])
            if self.square_meter_price:
                data["price_sm"] = {"type": "term", "value": True}
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == BUY and places_set <= {HOUSE, HOUSE_PART, HOMESTEAD, TOWNHOUSE}:
            data["_type"] = "suburbansale"
            data["object_type"] = {"type": "terms", "value": []}
            while places_set:
                data["object_type"]["value"].append(PLACES[places_set.pop()])
            if self.offer_owner is not None:
                data["suburban_offer_filter"] = {"type": "term", "value": self.offer_owner}
            if self.min_square is not None and self.max_square is not None:
                data["total_area"] = {"type": "range", "value": {}}
            if self.min_square is not None:
                data["total_area"]["value"]["gte"] = self.min_square
            if self.max_square is not None:
                data["total_area"]["value"]["lte"] = self.max_square
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == BUY and places_set <= {OFFICE, TRADE_AREA, STOCK, PUBLIC_CATERING,
                                                   FREE_SPACE, GARAGE, MANUFACTURE, CAR_SERVICE,
                                                   BUSINESS, BUILDING, DOMESTIC_SERVICES}:
            data["_type"] = "commercialsale"
            data["office_type"] = {"type": "terms", "value": []}
            while places_set:
                data["office_type"]["value"].append(PLACES[places_set.pop()])
            if self.currency is not None:
                data["currency"] = {"type": "term", "value": CURRENCIES[self.currency]}
            if self.square_meter_price:
                data["price_sm"] = {"type": "term", "value": True}
            if self.min_square is not None and self.max_square is not None:
                data["total_area"] = {"type": "range", "value": {}}
            if self.min_square is not None:
                data["total_area"]["value"]["gte"] = self.min_square
            if self.max_square is not None:
                data["total_area"]["value"]["lte"] = self.max_square
            if self.by_homeowner:
                data["from_offrep"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == BUY and places_set <= {COMMERCIAL_LAND}:
            data["_type"] = "commercialsale"
            data["category"] = {"type": "terms", "value": ["commercialLandSale"]}
            if self.currency is not None:
                data["currency"] = {"type": "term", "value": CURRENCIES[self.currency]}
            if self.square_meter_price:
                data["price_sm"] = {"type": "term", "value": True}
            if self.min_square is not None:
                data["site"]["value"]["gte"] = self.min_square
            if self.max_square is not None:
                data["site"]["value"]["lte"] = self.max_square
            # IT IS NOT ALL
        elif self.action == AREND_MONTHLY and places_set <= {FLAT}:
            data["_type"] = "flatrent"
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == AREND_MONTHLY and places_set <= {ROOM, BED}:
            data["_type"] = "flatrent"
            data["room"] = {"type": "terms", "value": []}
            while places_set:
                data["room"]["value"].append(PLACES[places_set.pop()])
            if self.min_price is not None or self.max_price is not None:
                data["price"] = {"type": "range", "value": {}}
            if self.min_price is not None:
                data["price"]["value"]["gte"] = self.min_price
            if self.max_price is not None:
                data["price"]["value"]["lte"] = self.max_price
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == AREND_MONTHLY and places_set <= {HOUSE, HOUSE_PART, TOWNHOUSE}:
            data["_type"] = "suburbanrent"
            data["object_type"] = {"type": "terms", "value": []}
            while places_set:
                data["object_type"]["value"].append(PLACES[places_set.pop()])
            if self.min_square is not None and self.max_square is not None:
                data["total_area"] = {"type": "range", "value": {}}
            if self.min_square is not None:
                data["total_area"]["value"]["gte"] = self.min_square
            if self.max_square is not None:
                data["total_area"]["value"]["lte"] = self.max_square
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == AREND_MONTHLY and places_set <= {OFFICE, TRADE_AREA, STOCK,
                                                             PUBLIC_CATERING, FREE_SPACE, GARAGE,
                                                             MANUFACTURE, CAR_SERVICE, BUSINESS,
                                                             BUILDING, DOMESTIC_SERVICES}:
            data["_type"] = "commercialrent"
            data["office_type"] = {"type": "terms", "value": []}
            while places_set:
                data["office_type"]["value"].append(PLACES[places_set.pop()])
            if self.currency is not None:
                data["currency"] = {"type": "term", "value": CURRENCIES[self.currency]}
            if self.square_meter_price:
                data["price_sm"] = {"type": "term", "value": True}
            if self.min_square is not None and self.max_square is not None:
                data["total_area"] = {"type": "range", "value": {}}
            if self.min_square is not None:
                data["total_area"]["value"]["gte"] = self.min_square
            if self.max_square is not None:
                data["total_area"]["value"]["lte"] = self.max_square
            if self.by_homeowner:
                data["from_offrep"] = {"type": "term", "value": True}
        elif self.action == AREND_MONTHLY and places_set <= {COMMERCIAL_LAND}:
            data["_type"] = "commercialrent"
            data["category"] = {"type": "terms", "value": ["commercialLandSale"]}
            if self.currency is not None:
                data["currency"] = {"type": "term", "value": CURRENCIES[self.currency]}
            if self.square_meter_price:
                data["price_sm"] = {"type": "term", "value": True}
            if self.min_square is not None:
                data["site"]["value"]["gte"] = self.min_square
            if self.max_square is not None:
                data["site"]["value"]["lte"] = self.max_square
            # IT IS NOT ALL
        elif self.action == AREND_DAILY and places_set <= {FLAT}:
            data["_type"] = "flatrent"
            if self.rooms:
                data["room"] = {"type": "terms", "value": [ROOMS[room] for room in self.rooms]}
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == AREND_DAILY and places_set <= {ROOM, BED}:
            data["_type"] = "flatrent"
            while places_set:
                data["room"]["value"].append(PLACES[places_set.pop()])
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        elif self.action == AREND_DAILY and places_set <= {HOUSE}:
            data["_type"] = "suburbanrent"
            data["object_type"] = {"type": "terms", "value": PLACES[HOUSE]}
            if self.min_bedrooms is not None and self.max_bedrooms is not None:
                data["bedroom_total"] = {"type": "range", "value": {}}
            if self.min_bedrooms is not None:
                data["bedroom_total"]["value"]["gte"] = self.min_bedrooms
            if self.max_bedrooms is not None:
                data["bedroom_total"]["value"]["lte"] = self.max_bedrooms
            if self.min_square is not None and self.max_square is not None:
                data["total_area"] = {"type": "range", "value": {}}
            if self.min_square is not None:
                data["total_area"]["value"]["gte"] = self.min_square
            if self.max_square is not None:
                data["total_area"]["value"]["lte"] = self.max_square
            if self.by_homeowner:
                data["is_by_homeowner"] = {"type": "term", "value": True}
            # IT IS NOT ALL
        else:
            raise IncorrectPlaces(action=self.action, places=self.places)

        if self._page > 1:
            data["page"] = {"type": "term", "value": self._page}
        if self.action == AREND_MONTHLY:
            data["for_day"] = {"type": "term", "value": "!1"}
        elif self.action == AREND_DAILY:
            data["for_day"] = {"type": "term", "value": "1"}
        if self.min_price is not None or self.max_price is not None:
            data["price"] = {"type": "range", "value": {}}
        if self.min_price is not None:
            data["price"]["value"]["gte"] = self.min_price
        if self.max_price is not None:
            data["price"]["value"]["lte"] = self.max_price
        if places_set <= {FLAT} and self.rooms:
            data["room"] = {"type": "terms", "value": [ROOMS[room] for room in self.rooms]}

        print(data)
        return data


class CianClient:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    def search(self, region: str, action: str, places: Sequence[str],
               offer_owner: Union[str, None]=None, rooms: Sequence[str]=(),
               min_bedrooms: Union[int, None]=None, max_bedrooms: Union[int, None]=None,
               building_status: Union[str, None]=None, min_price: Union[float, None]=None,
               max_price: Union[float, None]=None, currency: Union[str, None]=None,
               square_meter_price: bool=False, min_square: Union[float, None]=None,
               max_square: Union[float, None]=None, by_homeowner: bool=False, start_page: int=1,
               end_page: Union[int, None]=None, limit: Union[int, None]=None):
        return Search(
            session=self.session,
            region=region,
            action=action,
            places=places,
            offer_owner=offer_owner,
            rooms=rooms,
            min_bedrooms=min_bedrooms,
            max_bedrooms=max_bedrooms,
            building_status=building_status,
            min_price=min_price,
            max_price=max_price,
            currency=currency,
            square_meter_price=square_meter_price,
            min_square=min_square,
            max_square=max_square,
            by_homeowner=by_homeowner,
            start_page=start_page,
            end_page=end_page,
            limit=limit,
        )
