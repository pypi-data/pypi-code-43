import requests
import json

from io import BytesIO

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from .util import api_login, logger

__all__ = ['AutoseederLister',
           'AutoseederScreenshotDownloader',
           'AutoseederSearcher',
           'AutoseederSubmitter',
           'AutoseederTokenGetter',
           'AutoseederURLViewer'
           ]


class AbstractAutoseederAction(object):
    user = None
    password = None
    base_url = None
    token = None

    def __init__(self, *args, **kwargs):
        logger.debug(kwargs)
        self.user = kwargs.pop('user', None)
        self.password = kwargs.pop('password', None)
        self.token = kwargs.pop('token', None)
        self.base_url = kwargs.pop('base_url', None)
        logger.debug("Token: {}".format(self.token))
        if not self.token and self.user and self.password:
            self.token = api_login(self.base_url, self.user, self.password)
            logger.debug("Fetched token as {}".format(self.token))
        elif self.token:
            pass
        else:
            raise ValueError('Error logging you into {}, check your environment credentials'.format(self.base_url))


class AutoseederLister(AbstractAutoseederAction):
    limit = None

    def __init__(self, *args, **kwargs):
        super(AutoseederLister, self).__init__(*args, **kwargs)

    def get_url_list(self):
        logger.debug("using token {}".format(self.token))
        path = urljoin(self.base_url, 'api/v0/urls/')
        h = {'Authorization': 'Token ' + self.token,
             'Accept': 'application/json; indent=2'}
        r = requests.get(path, headers=h)
        logger.debug(r)

        if r.status_code == 401:
            raise RuntimeError('Invalid token, could not authenticate')
        elif r.status_code != 200:
            logger.debug(r.status_code)
            logger.debug(r.content)
            raise RuntimeError('Unhandled response from URL list API endpoint')

        return r.json()

    def format_report(self, limit):
        report = self.get_url_list()
        report.reverse()
        return json.dumps(report[:limit], indent=2)


class AutoseederSearcher(AbstractAutoseederAction):
    """
    AutoseederSearcher lets you find the UUIDs of particular URLs
    so you can perform other operations on them.

    NOTE: This is a highly inefficient stand-in at the moment for
    a proper search API. It gets full list, then returns UUID from
    first match.
    """

    def __init__(self, *args, **kwargs):
        super(AutoseederSearcher, self).__init__(*args, **kwargs)
        self.lister = AutoseederLister(base_url=self.base_url, token=self.token)

    def find_urls(self, url_term):
        """
        Return the UUID for the first URL matching the <url_term>.
        """
        url_list = self.lister.get_url_list()
        found = False

        for url in url_list:
            if url.get("url", "").find(url_term) >= 0:
                found = True
                yield url.get("uuid")

        if not found:
            raise ValueError("Couldn't find any URL containing '{}'".format(url_term))


class AutoseederSubmitter(AbstractAutoseederAction):
    def __init__(self, *args, **kwargs):
        super(AutoseederSubmitter, self).__init__(*args, **kwargs)

    def submit_url(self, url, seed_regions_str=None):
        """
        :param url: URL string to be submitted
        :param seed_regions_str: string containing comma-separated list of
                                 seeding regions (e.g. "AU,NZ")
        """
        path = urljoin(self.base_url, 'api/v0/submit/')
        h = {'Authorization': 'Token ' + self.token, 'Content-Type': 'application/json'}
        d = {'url': url}

        if seed_regions_str:
            d['proxy_constraints'] = {'countries': seed_regions_str.split(',')}

        logger.debug("Submitting with HTTP params: {}".format(d))

        r = requests.post(path, json=d, headers=h)
        logger.debug(r.status_code)
        logger.debug(r.content)

        if r.status_code == 401:
            raise RuntimeError('Invalid token, could not authenticate')
        elif r.status_code == 409:
            raise ValueError('URL appears to be a duplicate')
        elif r.status_code != 201:
            logger.debug("Error submitting to API: {}".format(r.content))
            raise RuntimeError('Unexpected response from URL submission API endpoint')

        return r.json()


class AutoseederURLViewer(AbstractAutoseederAction):
    def __init__(self, *args, **kwargs):
        super(AutoseederURLViewer, self).__init__(*args, **kwargs)

    def get_url_data(self, uuid):
        path = urljoin(self.base_url, 'api/v0/urls/{}'.format(uuid))
        h = {'Authorization': 'Token ' + self.token,
             'Accept': 'application/json; indent=2'}
        r = requests.get(path, headers=h)

        if r.status_code == 401:
            raise ValueError('Invalid token')
        elif r.status_code == 404:
            raise Exception('Error from API endpoint: No such UUID ({}) exists'.format(uuid))
        elif r.status_code != 200:
            logger.debug(r.status_code)
            logger.debug(r.content)
            raise Exception('Unhandled response from URL list API endpoint')

        return json.dumps(r.json(), indent=2)


class AutoseederTokenGetter(AbstractAutoseederAction):
    def __init__(self, *args, **kwargs):
        super(AutoseederTokenGetter, self).__init__(*args, **kwargs)

    def get_token(self):
        return self.token


class AutoseederScreenshotDownloader(AbstractAutoseederAction):
    def __init__(self, *args, **kwargs):
        super(AutoseederScreenshotDownloader, self).__init__(*args, **kwargs)

    def get_screenshot(self, uuid):
        path = urljoin(self.base_url, 'api/v0/urls/screenshot/{}'.format(uuid))
        h = {'Authorization': 'Token ' + self.token}
        r = requests.get(path, headers=h, stream=True)

        if r.status_code == 401:
            raise ValueError('Invalid token')
        elif r.status_code == 404:
            raise Exception('Error from API endpoint: No such UUID ({}) exists'.format(uuid))
        elif r.status_code != 200:
            logger.debug(r.status_code)
            logger.debug(r.content)
            raise Exception('Unhandled response from screenshot API endpoint.')
        with BytesIO() as stream:
            for chunk in r:
                stream.write(chunk)
            return stream.getvalue()
