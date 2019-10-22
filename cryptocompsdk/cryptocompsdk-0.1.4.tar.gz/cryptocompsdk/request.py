import time
from typing import Optional, Dict, Any, Callable
import requests

from cryptocompsdk.config import MAX_LIMIT_PER_API_CALL
from cryptocompsdk.response import ResponseException


class Request:

    def __init__(self, url: str, payload: Optional[Dict[str, Any]], response: requests.Response):
        self.url = url
        self.payload = payload
        self.response = response

    @property
    def json(self) -> dict:
        return self.response.json()


class APIBase:
    _exception_class = ResponseException

    def __init__(self, api_key: str, throttle: Optional[float] = None):
        self.api_key = api_key
        self.throttle = throttle

    def request(self, url: str, payload: Optional[Dict[str, Any]] = None) -> Request:
        api_key_dict = {'api_key': self.api_key}
        payload = self.filter_payload(payload)
        if payload is not None:
            payload.update(api_key_dict)
        else:
            payload = api_key_dict

        result = requests.get(url, params=payload)
        return Request(url, payload, result)

    def filter_payload(self, payload: Optional[Dict[str, Any]]):
        if payload is None:
            return payload

        # Remove None values as they were just defaults
        without_none = {key: value for key, value in payload.items() if value is not None}

        # Convert booleans into boolean strings that API is expecting
        with_str_bools = {key: _bool_to_str_if_bool(value) for key, value in without_none.items()}

        return with_str_bools

    def get(self, url: str, payload: Optional[Dict[str, Any]] = None, max_api_calls: Optional[int] = None):
        if payload is not None and payload.get('limit') == 0:
            return self._get_with_pagination(url, payload=payload, max_api_calls=max_api_calls)
        return self._get(url, payload=payload)

    def _get(self, url: str, payload: Optional[Dict[str, Any]] = None):
        if self.throttle is not None:
            time.sleep(self.throttle)
        data = self.request(url, payload)
        obj = self._class_factory(data.json)
        # isinstance dict added for development of api where class has not been set yet
        if isinstance(obj, dict):
            return obj
        if obj.has_error:
            if payload is not None:
                payload_str = f'payload {payload}'
            else:
                payload_str = 'no payload'
            raise self._exception_class(f'Requested {url} with {payload_str}, '
                                            f'got {data.json} as response')
        obj._request = data
        return obj

    def _get_with_pagination(self, url: str, payload: Optional[Dict[str, Any]] = None,
                             max_api_calls: Optional[int] = None):
        if max_api_calls is None:
            # TODO: less hackish
            max_api_calls = 10000000

        payload['limit'] = MAX_LIMIT_PER_API_CALL

        end_time = None
        i = -1
        while i + 1 < max_api_calls:
            i += 1
            payload['toTs'] = end_time
            data = self._get(url, payload)
            if i == 0:
                all_data = data
            if data.is_empty:
                break
            if i != 0:
                # chop off matching record. The end_time observation will be included in both responses
                data.delete_record_matching_time(end_time)
                all_data = data + all_data
            end_time = data.time_from

        all_data.trim_empty_records_at_beginning()

        return all_data

    def _class_factory(self, data: dict):
        raise NotImplementedError('must implement in subclass')


def _bool_to_str(boolean: bool) -> str:
    if not isinstance(boolean, bool):
        raise ValueError(f'non-boolean {boolean} passed to _bool_to_str')

    if boolean:
        return 'true'

    return 'false'


def _bool_to_str_if_bool(obj: Any) -> Any:
    if not isinstance(obj, bool):
        return obj
    return _bool_to_str(obj)
