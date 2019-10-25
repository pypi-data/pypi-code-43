import httpx
import enum

from telegram_bot_sdk.controller import controller


class HttpVerbs(enum.Enum):
    GET = 1
    POST = 2
    PUT = 3
    PATCH = 4
    DELETE = 5
    HEAD = 6
    CONNECT = 7
    OPTIONS = 8
    TRACE = 9


class Network:
    def make_request(self, *, verb, call, params=None, data=None):
        pass


class NetworkAsync(Network):
    def __init__(self, my_config):
        self.config = my_config
        self.async_client = httpx.AsyncClient()

    async def make_request(self, *, verb, call, params=None, data=None):
        response = None

        if verb == HttpVerbs.GET:
            response = await self.async_client.get(self.config.vars["URL"] + call, params=params)
        if verb == HttpVerbs.POST:
            response = await self.async_client.post(self.config.vars["URL"] + call, params=params, data=data)

        print(response.text)
        return controller.control_response_level_network(response)


class NetworkInternalAsync(Network):
    def __init__(self, my_config):
        self.config = my_config
        self.client = httpx.Client()

    def make_request(self, *, verb, call, params=None, data=None):
        response = None

        if verb == HttpVerbs.GET:
            response = self.client.get(self.config.vars["URL"] + call, params=params)
        if verb == HttpVerbs.POST:
            response = self.client.post(self.config.vars["URL"] + call, params=params, data=data)

        print(response.text)
        return controller.control_response_level_network(response)
