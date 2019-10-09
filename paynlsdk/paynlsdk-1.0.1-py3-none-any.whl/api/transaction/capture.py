import json

from marshmallow import Schema, fields, post_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import ErrorSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    """
    Response object for the Transaction::capture API

    :param bool result: Result of the API call
    """
    def __init__(self,
                 *args, **kwargs):
        # we will force a result since we only have the error object
        self.result = kwargs['request'].result
        super().__init__(**kwargs)

    def __repr__(self):
        return self.__dict__.__str__()


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema)

    @post_load
    def create_response(self, data):
        return Response(**data)


class Request(RequestBase):
    """
    Request object for the Transaction::capture API

    :param str transaction_id: transaction ID
    :param dict products: products
    :param str tracktrace: tracktrace code
    """
    def __init__(self, transaction_id: str=None, products: dict={}, tracktrace: str=None):
        self.transaction_id = transaction_id
        self.products = products
        self.tracktrace = tracktrace
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
        return 'capture'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Validation
        ParamValidator.assert_not_empty(self.transaction_id, 'transaction_id')
        # Get default api parameters
        rs = self.get_std_parameters()
        # Add own parameters
        rs['transactionId'] = self.transaction_id
        if self.products.__len__() > 0:
            rs['products'] = self.products
        if ParamValidator.not_empty(self.tracktrace):
            rs['tracktrace'] = self.tracktrace
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
        :rtype: paynlsdk.api.transaction.capture.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response

    def add_product(self, product_id: str, quantity: int):
        if product_id in self.products:
            self.products[product_id] += quantity
        else:
            self.products[product_id] = quantity

