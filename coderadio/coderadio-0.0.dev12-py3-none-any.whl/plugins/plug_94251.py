import logging
import requests

logger = logging.getLogger(__name__)

url = "https://www.1.fm/stplaylist/atr"


def run():
    try:
        resp = requests.get(url)
        obj = resp.json()
        service = "1.FM - Amsterdam Trance Radio"
        artist = obj["nowplaying"][0]["artist"]
        title = obj["nowplaying"][0]["title"]
        return service, artist, title
    except Exception as exc:
        logger.debug(exc)
        return "(*_*)", "(*_*)", "(*_*)"
