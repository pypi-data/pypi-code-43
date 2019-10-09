import json
import sys
import requests
import base64
from paynlsdk.api.requestbase import RequestBase
from paynlsdk.exceptions import ErrorException
from paynlsdk.validators import ParamValidator

PAYNL_END_POINT = "https://rest-api.pay.nl"
PAYNL_CLIENT_VERSION = "1.0.0"


class APIAuthentication(object):
    """
    API Authentication details

    :cvar str api_token: API token
    :cvar str service_id: service ID in the form of SL-xxxx-xxxx
    :cvar str token_code: service ID in the form of AT-xxxx-xxxx
    :cvar bool use_http_auth: whether we use basic HTTP authentication or not.
                               You should never really change this: Basic HTTP auth should be used by default!
    """
    api_token: str = None
    service_id: str = None
    token_code: str = None
    use_http_auth: bool = True


class APIClient(object):
    print_debug = False

    def __init__(self):
        self.__supported_status_codes = [200]
        self.end_point = PAYNL_END_POINT
        self.client_version = PAYNL_CLIENT_VERSION
        self.api_token = None
        self.service_id = None

    def get_auth(self, as_string: bool=True):
        """
        Get Basic HTTP auth string to use in header
        :param as_string: whether to return as string. If False, returns bytes
        :type as_string: bool
        :return: generated auth
        :rtype: str
        """
        enc = base64.b64encode('{}:{}'.format(APIAuthentication.token_code, APIAuthentication.api_token).encode())
        if as_string:
            return enc.decode()
        else:
            return enc

    def user_agent(self):
        """
        Get user agent string (will be used when calling the API)
        :return: API user agent
        :rtype: str
        """
        version = '{0}.{1}.{2}'.format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
        return "PAYNL/SDK/{0} Python/{1} ({2})".format(self.client_version, version, sys.hexversion)

    def perform_request(self,
                        request: RequestBase,
                        method: str='POST'
                        ):
        """
        Performs the actual call to the API and fill the responses.

        This method will basically verify the given :class:`paynlsdk.api.requestbase.RequestBase` class,
        perform the call to the API, interpret the result and fill the request's
        :ivar:`paynlsdk.api.requestbase.RequestBase.response`.
        Interpreting the result is done by evaluating the returned JSON using marshmallow.
        When validation is complete, the request class will internally set the response, which is always an instance
        of a :class:`paynlsdk.api.responsebase.ResponseBase` instance

        .. seealso::
            :class:`paynlsdk.api.requestbase.RequestBase` and all it's derived classes

            :class:`paynlsdk.api.responsebase.ResponseBase` and all it's derived classes

        :param request: the generic request to perform
        :type request: paynlsdk.api.requestbase.RequestBase
        :param method: HTTP method (stick to POST!)
        :type method: str
        :return: void
        :rtype: void
        :raise paynlsdk.exceptions.ErrorException: generic error occurred
        :raise paynlsdk.exceptions.SchemaException: error occurred during result parsing (schema load/validation failure)
        """
        headers = {
          'Accept': 'application/json',
          'User-Agent': self.user_agent()
        }
        if APIAuthentication.use_http_auth:
            headers['Authorization'] = 'Basic {auth}'.format(auth=self.get_auth())

        # Lazy loader for api credentials.
        if request.requires_api_token() and ParamValidator.is_empty(request.api_token)\
                and ParamValidator.not_empty(APIAuthentication.api_token):
            request.api_token = APIAuthentication.api_token
        if request.requires_service_id() and ParamValidator.is_empty(request.service_id)\
                and ParamValidator.not_empty(APIAuthentication.service_id):
                request.service_id = APIAuthentication.service_id

        # Build url
        url = "{0}/{1}".format(PAYNL_END_POINT, request.get_url())
        parameters = request.get_parameters()
        if APIAuthentication.use_http_auth and 'token' in parameters:
            del parameters['token']

        if self.print_debug:
            print("Calling {} using {}".format(url, method))
            print("HTTP Headers: {}".format(json.dumps(headers)))
            print("Params: {}".format(json.dumps(parameters)))

        if method.upper() == 'GET':
            response = requests.get(url, verify=True, headers=headers, params=parameters)
        else:
            response = requests.post(url, verify=True, headers=headers, data=parameters)

        if response.status_code not in self.__supported_status_codes:
            response.raise_for_status()

        if self.print_debug:
            print("Response object: {}".format(response))
            print("Raw response: {}".format(response.text))

        # Now the we have a response, let the request class handle the response.
        request.raw_response = response.text

        if self.print_debug:
            print(type(request.response))

        if request.response.is_error():
            raise ErrorException(request.response.request)
