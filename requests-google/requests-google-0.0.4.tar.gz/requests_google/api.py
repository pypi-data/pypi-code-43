# -*- coding: utf-8 -*-
"""
requests_google.api
"""

import feedparser
import requests

from .utils import get_location_url


def _gen_item(item):
    return {
        'title': item.title,
        'link': item.link,
        'description': item.description,
        # 'published': item.publishhed,
    }


def get_location_googlenews(city, state):
    """Generate google news for a given location.

    Parameters
    ----------
    city : string
        city name
    state : string
        state name
    """
    url = get_location_url(city, state)
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError('requests status_code={}'.format(status_code))
    d = feedparser.parse(r.text)
    result = [_gen_item(item) for item in d.entries]
    return result