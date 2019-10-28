import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_RETRIES = 4

# This has to be an excellent approximation to the number of milliseconds for
# a round the world ping. CRITICAL. DON'T CHANGE! (jk)
DEFAULT_BACKOFF_FACTOR = 0.267

DEFAULT_RETRY_STATUS_FORCE_LIST = ()

# Excluding delete from this list
ALLOWED_HTTP_METHODS = ['post', 'put', 'patch', 'get']


def requests_retry_session(retries=DEFAULT_RETRIES,
                           backoff_factor=DEFAULT_BACKOFF_FACTOR,
                           status_forcelist=DEFAULT_RETRY_STATUS_FORCE_LIST,
                           raise_on_status=False,
                           session=None):
    """ Get a retryable Python requests session

    See urllib3.util.retry.Retry for a more detailed description of the
    parameters.

    >>> from time import time
    >>> test_url = "https://httpstat.us/418"
    >>>
    >>> # Impatient retrying
    >>> retry_session_impatient = requests_retry_session(backoff_factor=0.01,
    ...                                                  retries=1,
    ...                                                  status_forcelist=(418,),
    ...                                                  raise_on_status=False)
    >>>
    >>> start = time()
    >>> retry_session_impatient.get(test_url)
    <Response [418]>
    >>> duration = time() - start
    >>> duration < 3
    True
    >>>
    >>> # Patient retrying
    >>> retry_session_patient = requests_retry_session(backoff_factor=1.0,
    ...                                                retries=4,
    ...                                                status_forcelist=(418,),
    ...                                                raise_on_status=False)
    >>>
    >>> start = time()
    >>> retry_session_patient.get(test_url)
    <Response [418]>
    >>> duration = time() - start
    >>> duration > 4
    True

    :param int retries: the number of retries
    :param float backoff_factor: the base interval for backing off
    :param tuple[int] status_forcelist: a
    :param bool raise_on_status: when the session is invoked for a request,
        if this is True and the requests fail after the specified number of
        retires, raises a urllib3.exceptions.MaxRetryError
    :param requests.Session session: the initial session to which to attach
        the retrying adapter. If not provided, creates a default
        requests.Session instance
    :return: the session
    :rtype: requests.Session
    :raises: urllib3.exceptions.MaxRetryError
    """
    session = session or requests.Session()
    retry = Retry(total=retries, read=retries, connect=retries,
                  backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist,
                  raise_on_status=raise_on_status)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class MissingIDParameter(Exception):
    def __init__(self):
        super().__init__("The 'id' parameter must be included in the request")


class InvalidBaseUrl(Exception):
    def __init__(self):
        super().__init__("The supplied base URL is not a valid string")


class InvalidToken(Exception):
    def __init__(self):
        super().__init__("The supplied API token is not a valid string")


class DRFClient:
    def __init__(self, base_url, token,
                 retries=DEFAULT_RETRIES,
                 backoff_factor=DEFAULT_BACKOFF_FACTOR,
                 status_forcelist=DEFAULT_RETRY_STATUS_FORCE_LIST,
                 raise_on_status=False):

        # If the base_url is an empty string or None type
        if not isinstance(base_url, str) or not base_url:
            raise InvalidBaseUrl

        if not isinstance(token, str) or not token:
            raise InvalidToken

        session = requests_retry_session(retries=retries,
                                         backoff_factor=backoff_factor,
                                         status_forcelist=status_forcelist,
                                         raise_on_status=raise_on_status)
        self.requests = ApiRequest(base_url, token, session=session)
        self.client = Stage(requester=self.requests)


class ApiRequest:
    def __init__(self, base_url, token, session=None):
        self.base_url = base_url
        self.headers = {'Authorization': str(token)}
        if not session:
            session = requests_retry_session()
        self.session = session

    @staticmethod
    def return_response(request_response):
        try:
            response = {
                'status_code': request_response.status_code,
                'response': request_response.json()
            }
        except:
            response = {
                'status_code': request_response.status_code,
                'response': {'text_response': request_response.text}
            }
        return response

    def get_request(self, request_url):
        r = self.session.get(self.base_url + str(request_url),
                             headers=self.headers)
        return self.return_response(r)

    def post_request(self, request_url, data):
        r = self.session.post(self.base_url + str(request_url),
                              json=data, headers=self.headers)
        return self.return_response(r)

    def put_request(self, request_url, data):
        r = self.session.put(self.base_url + str(request_url),
                             json=data, headers=self.headers)
        return self.return_response(r)

    def patch_request(self, request_url, data):
        r = self.session.patch(self.base_url + str(request_url),
                               json=data, headers=self.headers)
        return self.return_response(r)

    def delete_request(self, request_url):
        r = self.session.delete(self.base_url + str(request_url),
                                headers=self.headers)
        return self.return_response(r)


def convert_kwargs_to_query_params_for_get_request(request_url, kwargs_dict):
    """
    Function to take in a set of kwargs and convert them to query parameters and append them to the request url
    :param request_url:
    :param kwargs_dict:
    :return:
    """
    separator = '?'
    for key in kwargs_dict:
        request_url += '{}{}={}'.format(separator, key, kwargs_dict[key])
        if separator == '?':
            separator = '&'
    return request_url


def get_request_url_for_custom_drf_requests(request_url, full_path):
    """
    Function to dealing with custom (non standard DRF requests such as read, list, partial_update etc) requests.


    >>> request_url = '/root/'
    >>> full_path = 'root_my_function'
    >>>
    >>> get_request_url_for_custom_drf_requests(request_url, full_path)
    '/root/my_function/'

    :param str request_url: The current request url
    :param str full_path: The full path of the url
    :return:
    """
    root_url = full_path.split('_')[0]
    request_url += full_path.replace(root_url, '', 1)[1:] + '/'
    return request_url


class Stage:
    def __init__(self, requester=None, path=None):
        self.path = path
        self.requester = requester

    def __getattr__(self, path):
        self.path = path
        return self.request

    def request(self, *args, **kwargs):
        request_url = '/{}/'.format(self.path.split('_')[0])

        # Determine the request type (currently based on DRF format)
        # -------------------------------------------------------------------------

        # First check to see if a specific http method is requested by the user.
        # This ONLY works if the user has explicitly set a bunch of kwargs, with "override_http_method" present
        http_method = kwargs.get('override_http_method', '').lower()
        if http_method in ALLOWED_HTTP_METHODS:
            request_url = get_request_url_for_custom_drf_requests(request_url=request_url, full_path=self.path)
            # GET methods have to be treated slightly differently because they require a query params in the url
            if http_method == 'get':
                request_url = convert_kwargs_to_query_params_for_get_request(request_url, kwargs)
                return self.requester.get_request(request_url)

            # String match based off the http method to return the desired function
            return getattr(self.requester, '{}_request'.format(http_method))(request_url, kwargs)

        if self.path.endswith('_list'):
            request_url = convert_kwargs_to_query_params_for_get_request(request_url, kwargs)
            return self.requester.get_request(request_url)

        elif self.path.endswith('_read'):
            if 'id' not in kwargs:
                raise MissingIDParameter
            request_url += str(kwargs['id']) + '/'
            return self.requester.get_request(request_url)

        elif self.path.endswith('_create') and not self.path.endswith('_bulk_create'):

            if len(kwargs) == 0 and len(args) == 1:
                return self.requester.post_request(request_url, args[0])
            else:
                return self.requester.post_request(request_url, kwargs)

        elif self.path.endswith('_partial_update'):
            if 'id' not in kwargs:
                raise MissingIDParameter
            request_url += str(kwargs['id']) + '/'
            return self.requester.patch_request(request_url, kwargs)

        elif self.path.endswith('_update') and not self.path.endswith('_bulk_update'):
            if 'id' not in kwargs:
                raise MissingIDParameter
            request_url += str(kwargs['id']) + '/'
            return self.requester.put_request(request_url, kwargs)

        elif self.path.endswith('_delete') and not self.path.endswith('_bulk_delete'):
            if 'id' not in kwargs:
                raise MissingIDParameter
            request_url += str(kwargs['id']) + '/'
            return self.requester.delete_request(request_url)

        request_url = get_request_url_for_custom_drf_requests(request_url=request_url, full_path=self.path)

        if ('id' in kwargs and len(kwargs) == 1) or (
                len(kwargs) == 0 and len(args) == 0):  # A custom GET request (optionally) with an ID field
            if 'id' in kwargs:
                request_url += str(kwargs['id']) + '/'
            return self.requester.get_request(request_url)

        elif len(kwargs) >= 1 and len(args) == 0:  # A custom POST request
            return self.requester.post_request(request_url, kwargs)

        elif len(args) == 1:  # A custom post request with pre-formatted body data
            return self.requester.post_request(request_url, args[0])

        else:
            raise Exception('Unknown request type')
