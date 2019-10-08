import aiohttp
from .logger import logger

EXAMPLE_URL_HTTP = "https://www.instagram.com"
EXAMPLE_URL_HTTPS = "https://www.instagram.com"


async def check(
    url,
    http=True,
    https=True,
    EXAMPLE_URL_HTTP=EXAMPLE_URL_HTTP,
    EXAMPLE_URL_HTTPS=EXAMPLE_URL_HTTPS,
):
    try:
        async with aiohttp.ClientSession(raise_for_status=True) as client_session:
            if http:
                resp = await client_session.get(EXAMPLE_URL_HTTP, proxy=url)
                async with resp:
                    assert resp.status == 200
            if https:
                resp = await client_session.get(EXAMPLE_URL_HTTPS, proxy=url)
                async with resp:
                    assert resp.status == 200
    except Exception as e:
        logger.warn(e)
        return False, e
    else:
        return True, ''

