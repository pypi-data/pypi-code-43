import json
from typing import Dict

from marshmallow import Schema, fields, post_load, pre_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import ErrorSchema, Merchant, MerchantSchema, Service, ServiceSchema,\
    CountryOption, CountryOptionSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    """
    Response object for the Transaction::getservice API

    :param Merchant merchant: Merchant details
    :param Service merchant: Service details
    :param dict settings: any relevant settings (key/value)
    :param country_options Dict[str, CountryOption]: country options
    """
    def __init__(self,
                 merchant: Merchant = None,
                 service: Service = None,
                 settings: dict={},
                 country_options: Dict[str, CountryOption]={},
                 *args, **kwargs):
        self.merchant: Merchant = merchant
        self.service: Service = service
        self.settings: dict = settings
        self.country_options: Dict[str, CountryOption] = country_options
        super().__init__(**kwargs)

    def __repr__(self):
        return self.__dict__.__str__()


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema, required=True)
    merchant = fields.Nested(MerchantSchema, required=True)
    service = fields.Nested(ServiceSchema, required=True)
    settings = fields.Dict(allow_none=True, required=False)
    country_options = fields.List(fields.Nested(CountryOptionSchema), allow_none=True, required=False, load_from='countryOptionList')

    @pre_load
    def preprocess(self, data):
        # Fix EMPTY settings
        if ParamValidator.is_empty(data['settings']):
            del data['settings']
        if ParamValidator.is_empty(data['countryOptionList']):
            del data['countryOptionList']
        elif 'countryOptionList' in data and ParamValidator.not_empty(data['countryOptionList']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for i, item in data['countryOptionList'].items():
                list.append(item)
            data['countryOptionList'] = list
        return data

    @post_load
    def create_response(self, data):
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo preprocessing).
        #  This should be fixed in 3.x but that's a pre-release
        if 'country_options' in data:
            rs = {}
            for item in data['country_options']:
                rs[item.id] = item
            data['country_options'] = rs
        return Response(**data)


class Request(RequestBase):
    """
    Request object for the Transaction::getservice API

    :param str payment_method_id: Payment method ID
    """
    def __init__(self, payment_method_id: int=None):
        self.payment_method_id = payment_method_id
        super().__init__()

    def requires_api_token(self):
        return True

    def requires_service_id(self):
        return True

    def get_version(self):
        return 12

    def get_controller(self):
        return 'Transaction'

    def get_method(self):
        return 'getService'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Get default api parameters
        rs = self.get_std_parameters()
        # Add payment_method_id if set
        if ParamValidator.not_empty(self.payment_method_id):
            rs['paymentMethodId'] = self.payment_method_id
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
        :rtype: paynlsdk.api.transaction.getservice.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        self._response = response

    def __repr__(self):
        return self.__dict__.__str__()

