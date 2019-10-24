# -*- coding: utf-8 -*-
"""
requests_google.utils
"""

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus

# Reference: 
# https://stackoverflow.com/questions/51537063/url-format-for-google-news-rss-feed
URL_LOCATION = 'https://news.google.com/news/rss/headlines/section/geo/{location}'


def get_location_url(city, state):
    """Generate url for the given location"""
    location = '{}, {}, {}'.format(city, state, 'United States')
    return URL_LOCATION.format(location=quote_plus(location))