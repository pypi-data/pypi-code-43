from io import IOBase


try:
    from json.decoder import JSONDecodeError
except ImportError:
    # JSONDecodeError is for Python3 only
    JSONDecodeError = ValueError

import requests


class PyQalxAPIException(Exception):
    """
    A generic error for PyQalxAPI
    """
    pass


class BasePyQalxAPI(object):
    def __init__(self, config):
        self.config = config
        self.base_url = self.config.get('BASE_URL', 'https://api.qalx.io/')
        self.token = self.config['TOKEN']
        self._last_response = None

    def _build_request(self, url, method, include_auth_headers=True, **kwargs):
        """
        Handles making the request
        :param url: The url to make the request to
        :param include_auth_headers: Should we include the auth headers
        :param kwargs: kwargs to pass through to the request
        :return: response
        """
        if include_auth_headers:
            # We might not include the headers if we are PUTing to S3
            headers = kwargs.get('headers', {})
            # Don't overwrite existing headers
            headers.update({'Authorization': 'Token {token}'.format(
                token=self.token)})
            kwargs['headers'] = headers

        retry_count = 0
        MAX_RETRIES = self.config['MAX_RETRY_500']
        if MAX_RETRIES < 1:
            raise PyQalxAPIException(f'`MAX_RETRY_500` config setting must '
                                     f'be at least `1`.  Got `{MAX_RETRIES}`')
        while retry_count <= MAX_RETRIES:
            # There may be instances where the API returns a 500 error.  This
            # could be due to many things (network issues, cold starts etc).
            # To avoid terminating workers we retry up to `MAX_RETRIES` times
            # to make our best attempt at completing the request successfully.
            try:
                resp = requests.request(url=url,
                                        method=method,
                                        **kwargs)
                self._last_response = resp
                if resp.status_code < 500:
                    break
            except requests.exceptions.RequestException as exc:
                # RequestException: The base exception that `requests` can raise.
                #                   Catch everything and return to the client
                resp = exc
            # We retry if the response was a 5XX or if there was a requests
            # exception of some sort
            retry_count += 1
        return self._build_response(resp)

    def _build_non_safe_request(self,
                                method,
                                endpoint,
                                **kwargs):
        """
        Helper method for performing non safe requests (POST, PUT, PATCH etc).
        Handles the possibility of a user trying to create or update an item
        that also has a file
        :param method: The HTTP method
        :param endpoint: The endpoint you want to query: 'item`
        :param kwargs: Any data you want to pass to the request.
                      Use `json` key for data you want to post. Anything else
                      will be passed to `requests` as kwargs
                      json={'data': {'some': 'data'}, 'meta': {'some': 'meta'}}
        :return: response
        """
        url = self._get_url(endpoint)
        resp_ok, data = self._build_request(url=url,
                                            method=method,
                                            **kwargs)
        return resp_ok, data

    def _build_response(self, resp):
        """
        Builds the response that gets sent back to the client
        :param resp: The response from `requests` or an instance
                     of `RequestException`
        :return: tuple of `(response_ok:bool, response data:dict)`
        """
        # If it doesn't have `ok` then a `requests` exception was raised
        is_ok = getattr(resp, 'ok', False)
        try:
            data = resp.json()
        except (AttributeError, JSONDecodeError):
            # AttributeError: `resp` is an instance of RequestException
            # JSONDecodeError: `resp` is a normal response but has no data.
            #                   i.e. a 500 or a `delete` response
            data = []
        if is_ok is False:
            # If either of these are missing then a `requests` exception was
            # raised
            status_code = getattr(resp, 'status_code', '')
            reason = getattr(resp, 'reason', resp)
            data = {
                'status_code': status_code,
                'reason': reason,
                'errors': data
            }
        return is_ok, data

    def _get_url(self, endpoint):
        """
        Builds the URL for the request from the base_url and the endpoint
        :param endpoint: The endpoint you want to query: 'item/<item_guid>'
        :return: url
        """
        url = '{base_url}{endpoint}'.format(
            base_url=self.base_url,
            endpoint=endpoint.rstrip('/').lstrip('/')
        )
        return url

    def _upload_to_s3(self, data, input_file):
        """
        Given a response object with a file url in will attempt to
        PUT the file onto S3

        :param data: The data from the api
        :param input_file: The path to the file to upload or the file itself
        :return: response
        """
        url = data['file']['put_url']
        if not self.is_filestream(input_file):
            file_data = open(input_file, "rb").read()
        else:
            file_data = input_file
        return self._build_request(url=url,
                                   method='PUT',
                                   include_auth_headers=False,
                                   data=file_data)

    def is_filestream(self, input_object):
        return isinstance(input_object, IOBase)
