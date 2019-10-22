import asyncio
from dataclasses import dataclass
from typing import List, Tuple

import aiohttp

from urlspy.opengraph import extract_opengraph


@dataclass
class Response:
    url: str
    response_content: str
    original_response: aiohttp.ClientResponse

    def __repr__(self):
        return f"<Response: {self.url}>"

    @property
    async def opengraph(self):
        return await extract_opengraph(self.response_content)


async def get_from_session(
    session: aiohttp.ClientSession, url: str
) -> Tuple[aiohttp.ClientResponse, str]:

    async with session.get(url) as response:
        text = await response.text()
        return response, text


async def fetch(url: str):
    async with aiohttp.ClientSession() as session:
        return await get_from_session(session, url)


async def spy_url(url: str) -> Response:
    """
    Get information about the given URL.
    """
    response, html = await fetch(url)
    return Response(url, html, response)


async def spy_urls(urls: List[str]):
    """
    Given a list of URLs, concurrently get information using `spy_url`
    function and return the collected results.
    """
    urls = list(set(urls))
    tasks = [asyncio.ensure_future(spy_url(url)) for url in urls]
    return await asyncio.gather(*tasks)
