import requests
from json import JSONDecodeError
from time import time
from difflib import SequenceMatcher

from .exceptions import ComagicException

VALID_ENDPOINTS = (
    "account",
    "calls_report",
    "communications_report",
    "virtual_numbers",
    "available_virtual_numbers",
    "sip_line_virtual_numbers",
    "sip_lines",
    "sip_line_password",
    "scenarios",
    "media_files",
    "campaigns",
    "campaign_available_phone_numbers",
    "campaign_available_redirection_phone_numbers",
    "campaign_parameter_weights",
    "sites",
    "site_blocks",
    "call_legs_report",
    "goals_report",
    "chats_report",
    "chat_messages_report",
    "offline_messages_report",
    "visitor_sessions_report",
    "financial_call_legs_report",
    "tags",
    "employees",
    "customers",
    "campaign_daily_stat",
    "customer_users",
    "tag_communications",
    "tag_sales",
)

VALID_METHODS = ("get", "delete", "create", "update", "upload", "enable", "disable", "set", "unset")


class _Session(object):
    def __init__(self, login: str = "",
                 password: str = "", token: str = "",
                 api_url: str = "https://dataapi.comagic.ru/v2.0"
                 ) -> None:
        """
        :param login: str
        :param password: str
        :param token: str
        :param api_url: str
        """
        if (login and password) or token:
            self.login = login
            self.password = password
            self.API_URL = api_url
            self._session = requests.Session()
            self._session.headers.update({"Content-Type": "application/json"})
            self.access_token = self._create_access_token() if not token else token
        else:
            raise ValueError("miss auth params login and password or token")

    def _send_api_request(self, params: dict, counter: int = 0) -> any:
        """
        :param params: dict (params for comagic request)
        :param counter: int
        :return: any (data or raise ComagicException)
        """
        if counter > 3:
            raise ComagicException({"code": -32001, "message": "Invalid login or password"})
        try:
            resp = self._session.post(self.API_URL, json=params).json()
        except (JSONDecodeError, requests.ConnectionError) as e:
            raise ComagicException({"code": 502, "message": f"{e}"})
        if "error" in resp:
            if resp["error"]["code"] == -32001:
                counter += 1
                return self._send_api_request(params, counter)
            raise ComagicException(resp["error"])
        return resp["result"]["data"]

    def _create_access_token(self) -> str:
        params = {
            "jsonrpc": "2.0",
            "id": f"req_call{int(time())}",
            "method": "login.user",
            "params": {"login": self.login, "password": self.password},
        }

        resp = self._send_api_request(params)
        self.comagic_app_id = resp["app_id"]
        return resp["access_token"]

    def _get_endpoint(self, method: str, endpoint: str, user_id: any = None,
                      date_form: str = "", date_to: str = "", **kwargs) -> any:
        """
        :param method: str
        :param endpoint: str
        :param user_id: any (int or None)
        :param date_form: str
        :param date_to: str
        :return: any
        """
        default_params = {
            "jsonrpc": "2.0",
            "id": f"req_call{time()}",
            "method": f"{method}.{endpoint}",
            "params": {"access_token": self.access_token},
        }
        if date_form and date_to:
            default_params["params"].update({"date_from": date_form, "date_till": date_to})
        if user_id:
            default_params["params"].update({"user_id": user_id})
        if kwargs:
            params = {key: value for key, value in kwargs.items() if value or isinstance(value, (bool, int))}
            default_params["params"].update(**params)
        # print(default_params)
        return self._send_api_request(default_params)


class Comagic(object):
    def __init__(self, login: str = "", password: str = "", token: str = "", uis: bool = False) -> None:
        """
        :param login: str (login from comagic account)
        :param password: str (password from comagic account)
        :param token: str (token from comagic if needed.)
        :param uis: bool (if you wanna use uis api)
        """
        self.login = login
        self.password = password
        if uis:
            api_url = "https://dataapi.uiscom.ru/v2.0"
        else:
            api_url = "https://dataapi.comagic.ru/v2.0"
        self._session = _Session(login, password, token, api_url)
        self.access_token = self._session.access_token

    @property
    def comagic_app_id(self) -> any:
        try:
            return self._session.comagic_app_id
        except AttributeError:
            return None

    def __getattr__(self, endpoint: str) -> any:
        """
        :param endpoint: str
        :return: _Request instance or raise ValueError
        """
        if endpoint not in VALID_ENDPOINTS:
            mean_endpoints = [
                e for e in VALID_ENDPOINTS if SequenceMatcher(None, endpoint, e).ratio() >= 0.8
            ]
            raise ValueError(f"invalid endpoint - {endpoint}, mb you mean - {mean_endpoints}")
        return _Request(self, endpoint)

    def __call__(self, endpoint: str, method_kwargs: dict = {}) -> any:
        """
        :param endpoint: str
        :param method_kwargs: dict
        :return: any (comagic response or raise ComagicException)
        """
        return getattr(self, endpoint)(method_kwargs)


class _Request(object):
    __slots__ = ("_api", "_params")

    def __init__(self, api: Comagic, params: any) -> None:
        """
        :param api: instance of Comagic
        :param method_name: dict or str
        """
        self._api = api
        self._params = params

    def __getattr__(self, method_name):
        if method_name not in VALID_METHODS:
            raise ValueError(f"{method_name} - invalid method, must be in {VALID_METHODS}")
        return _Request(self._api, {"endpoint": self._params, "method": method_name})

    def __call__(self, user_id: any = None, date_from: str = '', date_to: str = '',
                 fields: list = [], sort: list = [], **kwargs) -> any:
        if not isinstance(fields, list) or not isinstance(sort, list):
            raise ValueError("fields or sort must be instance of list")

        return self._api._session._get_endpoint(
            endpoint=self._params["endpoint"],
            method=self._params["method"],
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            fields=fields,
            **kwargs
        )



