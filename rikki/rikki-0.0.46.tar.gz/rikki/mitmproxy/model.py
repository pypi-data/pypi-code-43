from typing import Dict, Optional


class Request:
    def __init__(
            self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            path: Optional[str] = None,
            method: Optional[str] = None,
            params: Optional[Dict[str, object]] = None,
            headers: Optional[Dict[str, str]] = None,
            content: Optional[str] = None
    ) -> None:
        super().__init__()
        self.host: Optional[str] = host
        self.port: Optional[int] = port
        self.path: Optional[str] = path
        self.method: Optional[str] = method
        self.params: Optional[Dict[str, object]] = params
        self.headers: Optional[Dict[str, str]] = headers
        self.content: Optional[str] = content

    def empty(self) -> bool:
        if self.host or self.content or self.params or self.headers or self.port or self.path or self.method:
            return False
        else:
            return True


class Response:
    def __init__(
            self,
            headers: Optional[Dict[str, str]] = None,
            content: Optional[str] = None,
            code: Optional[int] = None
    ) -> None:
        super().__init__()
        self.headers: Optional[Dict[str, str]] = headers
        self.__content: Optional[str] = content
        self.__code: Optional[int] = code

    @property
    def code(self) -> int:
        return self.__code

    @code.setter
    def code(self, value):
        self.__code = int(value)

    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, value):
        self.__content = str(value)

    def empty(self) -> bool:
        if self.code or self.headers or self.content:
            return False
        else:
            return True
