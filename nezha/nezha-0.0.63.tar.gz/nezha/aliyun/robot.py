from collections.abc import Iterable
from typing import Tuple, Union, Mapping

import requests


class Robot:

    def __init__(self, url: Union[str, Tuple[str, ...]]):
        self.url: Tuple[str, ...] = tuple([url, ]) if isinstance(url, str) else url

    def _send(self, data: Mapping) -> None:
        if isinstance(self.url, str):
            raise TypeError(f'data {data} must be iterable and not str')
        if not isinstance(self.url, Iterable):
            raise TypeError(f'data {data} must be iterable and not str')
        for url in self.url:
            requests.post(url, json=data)

    def send_text(self, text: str) -> None:
        data = {"msgtype": "text",
                "text": {
                    "content": f"{text}"
                }
                }
        self._send(data)

    def send_markdown(self, title: str, text: str) -> None:
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"{title}",
                "text": f"{text}"
            }
        }
        self._send(data)


class LogRot(Robot):

    def info(self, text: str) -> None:
        self.send_text(text)

    def error(self, text: str) -> None:
        self.send_text(text)
