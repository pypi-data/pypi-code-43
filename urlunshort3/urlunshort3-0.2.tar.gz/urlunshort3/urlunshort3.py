import logging
import requests
from urllib.parse import urlparse, urlsplit
from .resolvers import generic_resolver


class UrlUnshortener:
    def __init__(self, tricks=False):
        self.services = ["bit.ly", "is.gd", "t.co", "tinyurl.com", "tiny.cc"]
        if tricks == False:
            self.tricks = False
        else:
            self.tricks = True

    def resolve_short(self, url, imeout=None):
        """
        Resolve shortened URL to a target URL. If the URL could not be resolved,
        return None. It would be good to validate that this is actually a url
        here, but I can't seem to easily get that done without some other
        dependencies and I'm trying to keep this simple.

        :argument url: the url to resolve

        :argumet timeout: the max tix to wait for the URL to resolve in seconds
            There's currently no way of telling if a request failed due to
            a timeout or because the URL could not be resolved!

        :returns: the resolved URL. None if URL could not be resolved

        """

        parts = urlsplit(url)
        if not parts.scheme and not parts.hostname:
            parts = urlsplit("https://" + url)
            url = parts.join()
        result = generic_resolver(url, self.tricks)
        return result

    def is_shortened(self, url):
        """Check if the url appears to be shortened, based on the services
        whitelist. **Note:** This will be a best-effort thing, as the list
        if services has to be kept up to date. Also note that valid URLs on
        shortening services (like bit.ly/apidocs) will be assumed to be a
        shortened url.

        :argument url: The URL to check

        :returns: true or false
        """
        parts = urlsplit(url)
        if parts.hostname in self.services:
            if not parts.scheme and not parts.hostname:
                parts = urlsplit("http://" + url)
            return bool(parts.hostname in self.services and parts.path)
        else:
            logging.debug('[-] Service at {} is not supported by this function, but may resolve'.format(url))
            try:
                r = requests.head(url)
                if r.headers['Location'] != url:
                    return True
            except:
                return False

