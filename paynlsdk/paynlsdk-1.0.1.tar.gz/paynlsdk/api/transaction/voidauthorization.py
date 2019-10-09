import json

from marshmallow import Schema, fields, post_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import ErrorSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    """
    Response object for the Transaction::voidauthorization API

    :param bool result: Result of the API call
    """
    def __init__(self,
                 result: bool=None,
                 *args, **kwargs):
        self.result = result
        super().__init__(**kwargs)

    def __repr__(self):
        return self.__dict__.__str__()


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema)

    @post_load
    def create_response(self, data):
        #  We will map the result to a Response internal value
        data['result'] = data['request'].result
        return Response(**data)


class Request(RequestBase):
    """
    Request object for the Transaction::voidauthorization API

    :param str transaction_id: transaction ID
    """
    def __init__(self, transaction_id: str=None):
        self.transaction_id = transaction_id
        super().__init__()

    def requires_api_token(self):
        return True

    def requires_service_id(self):
        return False

    def get_version(self):
        return 12

    def get_controller(self):
        return 'Transaction'

    def get_method(self):
        return 'voidAuthorization'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Validation
        ParamValidator.assert_not_empty(self.transaction_id, 'transaction_id')
        # Get default api parameters
        rs = self.get_std_parameters()
        # Add own parameters
        rs['transactionId'] = self.transaction_id
        return rs

    @RequestBase.raw_response.setter
    def raw_response(self, raw_response):
        self._raw_response = raw_response
        # Do error checking.
        rs = json.loads(self.raw_response)
        schema = ResponseSchema(partial=True)
        response, errors = schema.load(rs)
        self.handle_schema_errors(errors)
        self._response = response

    @property
    def response(self) -> Response:
        """
        Return the API :class:`Response` for the validation request

        :return: The API response
        :rtype: paynlsdk.api.transaction.voidauthorization.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response

