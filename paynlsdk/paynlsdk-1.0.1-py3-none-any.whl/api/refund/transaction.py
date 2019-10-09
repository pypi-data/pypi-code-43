import json

from marshmallow import Schema, fields, post_load, pre_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import ErrorSchema, RefundFailInfoSchema, RefundSuccessInfoSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    """
    Response object for the Refund::transaction API

    :param dict refunded_transactions: refunded transactions information
    :param dict failed_transactions: failed refunds information
    :param dict products: product info (keys: productid; values: quantity)
    :param int amount_refunded: amount that was refunded
    :param str description: refunds description
    :param str refund_id: Refund ID. Please note this is NOT guaranteed. Value is only returned for IBAN based payments
    """
    def __init__(self,
                 refunded_transactions: dict={},  # Should probably be typehinted with Dict[str, RefundSuccessInfoSchema]
                 failed_transactions: dict={},  # Should probably be typehinted with Dict[str, RefundFailInfoSchema]
                 amount_refunded: int=None,
                 description: str=None,
                 refund_id: str=None,
                 *args, **kwargs):
        self.refunded_transactions = refunded_transactions
        self.failed_transactions = failed_transactions
        self.amount_refunded = amount_refunded
        self.description = description
        self.refund_id = refund_id
        super().__init__(**kwargs)

    def __repr__(self):
        return str(self.__dict__)

    def get_refunded_amount(self):
        """
        Get refunded amount
        :return: refunded amount
        :rtype: float
        """
        return self.response.amount_refunded / 100



class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema)
    refunded_transactions = fields.List(fields.Nested(RefundSuccessInfoSchema), load_from='refundedTransactions')
    failed_transactions = fields.List(fields.Nested(RefundFailInfoSchema), load_from='failedTransactions')
    amount_refunded = fields.Integer(load_from='amountRefunded')
    description = fields.String()
    refund_id = fields.String(load_from='refundId', allow_none=True, required=False)

    @pre_load
    def pre_processor(self, data):
        # Again, the API returns an empty string where it SHOULD return null or an empty list.
        if 'refundedTransactions' in data and ParamValidator.is_empty(data['refundedTransactions']):
            data['refundedTransactions'] = []
        elif 'refundedTransactions' in data and ParamValidator.not_empty(data['refundedTransactions']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for i, item in data['refundedTransactions'].items():
                list.append(item)
            data['refundedTransactions'] = list
        if 'failedTransactions' in data and ParamValidator.is_empty(data['failedTransactions']):
            data['failedTransactions'] = []
        elif 'failedTransactions' in data and ParamValidator.not_empty(data['failedTransactions']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for i, item in data['failedTransactions'].items():
                list.append(item)
            data['failedTransactions'] = list
        return data

    @post_load
    def create_response(self, data):
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo preprocessing).
        #  This should be fixed in 3.x but that's a pre-release
        if 'refunded_transactions' in data:
            rs = {}
            for item in data['refunded_transactions']:
                print(item)
                rs[item.order_id] = item
            data['refunded_transactions'] = rs
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo preprocessing).
        #  This should be fixed in 3.x but that's a pre-release
        if 'failed_transactions' in data:
            rs = {}
            for item in data['failed_transactions']:
                rs[item.order_id] = item
            data['failed_transactions'] = rs
        return Response(**data)


class Request(RequestBase):
    """
    Request object for the Refund::transaction API

    :param str transaction_id: Refund ID
    :param int amount: refund amount
    :param str description: refunds description
    :param str process_date: process date
    :param dict products: product info (keys: productid; values: quantity)
    :param float vat_percentage: vat percentage
    :param str exchange_url: exchange url
    """
    def __init__(self,
                 transaction_id: str=None,
                 amount: int=None,
                 description: str=None,
                 process_date: str=None,
                 products: dict={},
                 vat_percentage: float=None,
                 exchange_url: str=None,
                 ):
        self.transaction_id = transaction_id
        self.amount = amount
        self.description = description
        self.process_date = process_date
        self.products = products
        self.vat_percentage = vat_percentage
        self.exchange_url = exchange_url
        super().__init__()

    def requires_api_token(self):
        return True

    def requires_service_id(self):
        return False

    def get_version(self):
        return 3

    def get_controller(self):
        return 'Refund'

    def get_method(self):
        return 'transaction'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Validation
        ParamValidator.assert_not_empty(self.transaction_id, 'transaction_id')
        # Get default api parameters
        rs = self.get_std_parameters()
        # Add own parameters
        rs['transactionId'] = self.transaction_id
        if ParamValidator.not_empty(self.amount):
            rs['amount'] = self.amount
        if ParamValidator.not_empty(self.description):
            rs['description'] = self.description
        if ParamValidator.not_empty(self.process_date):
            rs['processDate'] = self.process_date
        if ParamValidator.not_empty(self.products):
            rs['products'] = self.products
        if ParamValidator.not_empty(self.vat_percentage):
            rs['fVatPercentage'] = self.vat_percentage
        if ParamValidator.not_empty(self.exchange_url):
            rs['exchangeUrl'] = self.exchange_url
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
        :rtype: paynlsdk.api.refund.transaction.Response
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

