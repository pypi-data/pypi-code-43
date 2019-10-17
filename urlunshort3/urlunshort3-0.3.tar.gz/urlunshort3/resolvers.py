"""
This module contains resolvers for url shorteners. A resolver takes a netloc
(host[:port] and path) and returns a URL as a string.
"""
import logging
import requests
from urllib.parse import urlparse, urlsplit
from functools import wraps


def handle_tricks(url, tricks):
    # Some URL shorteners don't respond correctly to a head request, this may help
    if tricks == True:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
        }
        r = requests.get(url, headers=headers)
        if r.status_code in [301, 303]:
            logging.info('"{}" returned a {} response'.format(url, r.status_code))
            return r.headers['Location']
        else:
            logging.debug(
                'URL "{}" returned a {} status code'.format(url, r.status_code)
            )
            return r.url
    else:
        return None


def _io_error_handling(fun):
    """
    Catch connection errors for requests
    """

    @wraps(fun)
    def wrapped(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except requests.ConnectionError:
            return None

    return wrapped


@_io_error_handling
def generic_resolver(url, tricks, timeout=None):
    """
    Generic url fetcher that assumes the target service will response sanely
    to a HEAD request for the url.

    returns the full url or None if the url could not be resolved.
    """
    request_error = range(400, 600)

    if timeout:
        r = requests.head(url, timeout=timeout)
    else:
        r = requests.head(url)
    redirect_codes = range(300, 400)

    if r.status_code in request_error:
        logging.info(
            '"{}" returned a {} status code for value {}'.format(
                url, r.status_code, r.url
            )
        )
        if urlsplit(r.url).netloc == urlsplit(url).netloc:
            response = handle_tricks(url, tricks)
            return response
        else:
            return r.url
    elif r.status_code in request_error:
        logging.info('URL "{}" returned an unhandled response'.format(url))
        return None
    elif r.status_code in redirect_codes:
        return r.headers["Location"]
    else:
        logging.error('{} returned a {} response'.format(url, r.status_code))
        return None


    return None
