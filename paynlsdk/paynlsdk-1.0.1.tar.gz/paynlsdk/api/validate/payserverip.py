import json

from marshmallow import Schema, fields, post_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import Error
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    """
    Request object for the Validate::payserverip API

    :param bool result: validation result. True if request was for a valid PayNL server
    """
    def __init__(self,
                 result: bool=None,
                 *args, **kwargs):
        """
        Initialize the Response object

        :param result: Result of the API call.
                       This indicates whether or not the requested ip address is a valid PayNL IP server address
        :type result: bool
        :param args: Unused
        :type args: list
        :param kwargs: The same keyword arguments that :class:`ResponseBase` receives.
        :type kwargs: dict
        """
        self.result = result
        # The result is a pure boolean, so we'll mimic the base's request object
        kwargs['request'] = Error(result=True)  # Set result to be true to prevent an exception being raised!
        super().__init__(**kwargs)

    def __repr__(self):
        return self.__dict__.__str__()


class ResponseSchema(Schema):
    result = fields.Boolean()

    @post_load
    def create_response(self, data):
        """
        create an instance of the :class:`paynlsdk.api.validate.payserverip.Response` class

        :param data: dictionary with which the response object can be created
        :type data: dict
        :return: return generated response class
        :rtype: paynlsdk.api.validate.payserverip.Response
        """
        return Response(**data)


class Request(RequestBase):
    """
    Request object for the Validate::payserverip API

    :param str ip_address: IP address to validate
    """
    def __init__(self, ip_address: str=None):
        """
        Initialize the Request object
        :param ip_address: IP address to validate
        :type ip_address: str
        """
        self.ip_address = ip_address
        super().__init__()

    def requires_api_token(self):
        return False

    def requires_service_id(self):
        return False

    def get_version(self):
        return 1

    def get_controller(self):
        return 'Validate'

    def get_method(self):
        return 'isPayServerIp'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Validation
        ParamValidator.assert_not_empty(self.ip_address, 'ip_address')
        # Get default api parameters
        rs = self.get_std_parameters()
        # Add own parameters
        rs['ipAddress'] = self.ip_address
        return rs

    @RequestBase.raw_response.setter
    def raw_response(self, raw_response):
        self._raw_response = raw_response
        # Do error checking.
        rs = json.loads(self.raw_response)
        schema = ResponseSchema(partial=True)
        self.response, errors = schema.load(rs)
        self.handle_schema_errors(errors)

    @property
    def response(self) -> Response:
        """
        Return the API :class:`Response` for the validation request

        :return: The API response
        :rtype: paynlsdk.api.validate.payserverip.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response

    def __repr__(self):
        return self.__dict__.__str__()


