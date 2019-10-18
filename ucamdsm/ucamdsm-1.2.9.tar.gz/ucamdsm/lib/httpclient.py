import json
import requests

API_VERSION = '2.0'


class HttpClient:
    """Wrapper class to make Storage Center REST API calls."""

    def __init__(self, host, port, user, password, verify):
        """
        HttpClient handles the REST requests.

        :param host: IP address of the Dell Data Collector.
        :param port: Port the Data Collector is listening on.
        :param user: User account to login with.
        :param password: Password.
        :param verify: Boolean indicating whether certificate verification
                       should be turned on or not.
        """
        self.base_url = 'https://%s:%s/api/rest/' % (host, port)
        self.session = requests.Session()
        self.session.auth = (user, password)

        self.header = {}
        self.header['Content-Type'] = 'application/json; charset=utf-8'
        self.header['Accept'] = 'application/json'
        self.header['x-dell-api-version'] = API_VERSION
        self.verify = verify

        if not verify:
            requests.packages.urllib3.disable_warnings()

    def __enter__(self):
        return self

    def __exit__(self):
        self.session.close()

    def _format_url(self, url):
        """Formats the REST URL to use for API calls."""
        return '%s%s' % (self.base_url, url if url[0] != '/' else url[1:])

    def get(self, url):
        """Perform a REST GET request."""
        return self.session.get(
            self._format_url(url),
            headers=self.header,
            verify=self.verify)

    def post(self, url, payload):
        """Perform a REST POST request."""
        return self.session.post(
            self._format_url(url),
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers=self.header,
            verify=self.verify)

    def put(self, url, payload):
        """Perform a REST PUT request."""
        return self.session.put(
            self._format_url(url),
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers=self.header,
            verify=self.verify)

    def delete(self, url):
        """Perform a REST DELETE request."""
        return self.session.delete(
            self._format_url(url),
            headers=self.header,
            verify=self.verify)
