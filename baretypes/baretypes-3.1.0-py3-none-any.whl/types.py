"""Types for bareASGI and bareClient"""

from abc import ABCMeta, abstractmethod
from typing import (
    AbstractSet,
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union
)


class ParseError(Exception):
    """Exception raised on a parse error"""


class HttpInternalError(Exception):
    """Exception raised for an internal error"""


class HttpDisconnectError(Exception):
    """Exception raise on HTTP disconnect"""


class WebSocketInternalError(Exception):
    """Exception raised for a WebSocket internal error"""


Scope = Mapping[str, Any]
Message = Mapping[str, Any]
Context = Optional[Mapping[str, Any]]
Info = Optional[MutableMapping[str, Any]]

Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

ASGIInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIInstance]

LifespanHandler = Callable[[Scope, Info, Message], Awaitable[None]]

Header = Tuple[bytes, bytes]
Headers = List[Header]

RouteMatches = Mapping[str, Any]
Content = AsyncIterable[bytes]
PushResponse = Tuple[str, Headers]
PushResponses = Iterable[PushResponse]


class WebSocket(metaclass=ABCMeta):
    """The interface for a server side WebSocket."""

    @abstractmethod
    async def accept(
            self,
            subprotocol: Optional[str] = None,
            headers: Optional[List[Header]] = None
    ) -> None:
        """Accept the socket.

        This must be done before any other action is taken.

        :param subprotocol: An optional subprotocol sent by the client.
        :type subprotocol: Optional[str], optional
        :param headers: Optional headers to send, defaults to None
        :type headers: Optional[List[Header]], optional
        """
        ...

    @abstractmethod
    async def receive(self) -> Optional[Union[bytes, str]]:
        """Receive data from the WebSocket.

        :return: Either bytes of a string depending on the client.
        """
        ...

    @abstractmethod
    async def send(self, content: Union[bytes, str]) -> None:
        """Send data to the client.

        :param content: Either bytes or a string.
        :type content: Union[bytes, str]
        """
        ...

    @abstractmethod
    async def close(self, code: int = 1000) -> None:
        """Closes the WebSocket.

        :param code: The reason code (defaults to 1000).
        :type code: Optional[int], optional
        """
        ...


HttpResponse = Union[
    int,
    Tuple[int, Optional[Headers]],
    Tuple[int, Optional[Headers], Optional[Content]],
    Tuple[int, Optional[Headers], Optional[Content], Optional[PushResponses]]
]
HttpRequestCallback = Callable[[Scope, Info,
                                RouteMatches, Content], Awaitable[HttpResponse]]
WebSocketRequestCallback = Callable[[
    Scope, Info, RouteMatches, WebSocket], Awaitable[None]]
HttpMiddlewareCallback = Callable[[
    Scope, Info, RouteMatches, Content, HttpRequestCallback], Awaitable[HttpResponse]]


class HttpRouter(metaclass=ABCMeta):
    """The interface for an HTTP router"""

    @property  # type: ignore
    @abstractmethod
    def not_found_response(self) -> HttpResponse:
        """The response when a handler could not be found for a method/path"""

    @not_found_response.setter  # type: ignore
    @abstractmethod
    def not_found_response(self, value: HttpResponse) -> None:
        """The response when a handler could not be found for a method/path

        :param value: The handler for an un-routable request
        :type value: HttpResponse
        """

    @abstractmethod
    def add(
            self,
            methods: AbstractSet[str],
            path: str,
            callback: HttpRequestCallback
    ) -> None:
        """Add a handler

        :param methods: The supported HTTP methods
        :type methods: AbstractSet[str]
        :param path: The path
        :type path: str
        :param callback: The request handler
        :type callback: HttpRequestCallback
        """

    @abstractmethod
    def resolve(
            self,
            method: str,
            path: str
    ) -> Tuple[Optional[HttpRequestCallback], Optional[RouteMatches]]:
        """Resolve a request to a handler with the route matches

        :param method: The HTTP method.
        :type method: str
        :param path: The path
        :type path: str
        :return: A handler and the optional route matches.
        :rtype: Tuple[Optional[HttpRequestCallback], Optional[RouteMatches]]
        """


class WebSocketRouter(metaclass=ABCMeta):
    """The interface for a WebSocket router"""

    @abstractmethod
    def add(
            self,
            path: str,
            callback: WebSocketRequestCallback
    ) -> None:
        """Add the handler for a route

        :param path: The path.
        :type path: str
        :param callback: The handler
        :type callback: WebSocketRequestCallback
        """

    @abstractmethod
    def resolve(
            self,
            path: str
    ) -> Tuple[Optional[HttpRequestCallback], Optional[RouteMatches]]:
        """Resolve a route to a handler

        :param path: The path
        :type path: str
        :return: A handler and possible route matches
        :rtype: Tuple[Optional[HttpRequestCallback], Optional[RouteMatches]]
        """
