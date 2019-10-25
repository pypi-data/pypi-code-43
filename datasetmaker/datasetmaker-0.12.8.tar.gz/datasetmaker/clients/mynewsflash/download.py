import os
import datetime
import requests


class NewsFetcher():
    """ Simple wrapper around the Mynewsflash API.

    Parameters
    ----------
    domains : list
        List of news domains to include in search.
    """

    DEFAULT_DOMAINS = [
        'dn.se',
        'svt.se',
        'aftonbladet.se',
        'expressen.se',
        'sydsvenskan.se',
        'gp.se',
        'svd.se',
        'sr.se']
    API_KEY = os.environ.get('MYNEWSFLASH_TOKEN')
    URL = 'https://api.mynewsflash.se/v1/search.json'

    def __init__(self, domains: list = None) -> None:
        self.domains = self.DEFAULT_DOMAINS if domains is None else domains

    def fetch_hour(self, hour: datetime.datetime) -> list:
        """ Fetches all results for a given hour.

        Parameters
        ----------
        hour : datetime.datetime
            Hour to search.
        """

        params = {
            'key': self.API_KEY,
            'require_domains': ','.join(self.domains),
            'unique': 'true',
            'indexed_from': hour.isoformat(),
            'indexed_to': (hour+datetime.timedelta(hours=1)).isoformat(),
            'q': '"*"',
            'limit': 500}

        r = requests.get(self.URL, params=params)  # type: ignore

        return r.json().get('result')

    def fetch_period(self, start: datetime.datetime, end: datetime.datetime) -> list:
        """ Fetches all results between start and end.

        Parameters
        ----------
        start : datetime.datetime
            Start of time period.
        end : datetime.datetime
            End of time period.
        """

        results = list()
        for hour in range(int((end - start).total_seconds() / 60 / 60)):
            offset = datetime.timedelta(hours=hour)
            results.extend(self.fetch_hour(start + offset))
        return results
