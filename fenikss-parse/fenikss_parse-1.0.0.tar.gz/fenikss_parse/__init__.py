"""
MIT License

Copyright (c) 2019 Aristarh Deryapa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from email.parser import BytesParser
from typing import Any, Dict
from urllib.parse import urlparse, parse_qs


class URLInformation:
    """
    URL information. For internal usage only.
    """

    def __repr__(self):
        return f'URLInformation["{self.scheme}://{self.server}{self.path}"]'

    server: str = None
    path: str = None
    params: Dict[str, Any] = {}
    is_https: bool = False
    scheme: str = None
    fragment: str = None


class HTTPRequest:
    """
    HTTP request information. For internal usage only.
    """

    def __repr__(self):
        return f'HTTPRequest(url="{self.url}", headers=...)'

    from_addr: str = None
    method: str = None
    url: URLInformation = None
    headers: Dict[str, Any] = {}


def parse_url(url: str) -> dict:
    """
    Parse URL.
    :param url: URL for parsing.
    :returns: URL information.
    """

    parsed = urlparse(url)

    url_info = URLInformation()
    url_info.server = parsed.netloc
    url_info.path = parsed.path
    url_info.params = parse_qs(parsed.query)
    url_info.is_https = (parsed.scheme.lower() == 'https')
    url_info.scheme = parsed.scheme.lower()
    url_info.fragment = parsed.fragment

    return url_info


def parse_request(
    request: str,
    from_addr: str,
    protocol: str = 'http',
    encoding: str = 'UTF-8'
) -> HTTPRequest:
    """
    Parse client HTTP request.
    :param request: Request data.
    :param from_addr: Client address.
    :param protocol: Request protocol.
    :param encoding: Data encoding.
    :returns: HTTPRequest
    """

    request = request.replace('\r\n', '\n').strip()
    url, *headers = request.split('\n')
    method, *url = url.split(' ')
    url = ' '.join(url[:-1])

    headers = '\n'.join(headers).strip()
    headers = BytesParser().parsebytes(headers.encode(encoding))

    url = headers['HOST'] + ' '.join(url)
    url = parse_url(url)
    url.scheme = protocol.lower()

    req = HTTPRequest()
    req.from_addr = from_addr
    req.method = method
    req.url = url
    req.headers = headers

    return req
