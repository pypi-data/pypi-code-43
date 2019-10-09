import json

from marshmallow import Schema, fields, post_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import ErrorSchema, TransactionStatusDetails, TransactionStatusDetailsSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    """
    Response object for the Transaction::status API

    :param TransactionStatusDetails payment_details: payment details
    """
    def __init__(self,
                 payment_details: TransactionStatusDetails=None,
                 *args, **kwargs):
        self.payment_details = payment_details
        super().__init__(**kwargs)

    def get_transaction_id(self):
        """
        Get EX-code of transaction
        :return: EX-code of the transaction
        :rtype: string
        """
        return self.payment_details.transaction_id

    def get_order_id(self):
        """
        Get order ID of transaction
        :return: the order ID
        :rtype: string
        """
        return self.payment_details.order_id

    def get_payment_profile_id(self):
        """
        Get payment profile ID
        :return: payment profile ID
        :rtype: int
        """
        return self.payment_details.payment_profile_id

    def get_state(self):
        """
        Get transaction status
        :return: transaction state
        :rtype: int
        """
        return self.payment_details.state

    def get_state_name(self):
        """
        Get transaction status name
        :return: transaction status name
        :rtype: string
        """
        return self.payment_details.state_name

    def get_currency(self):
        """
        Get currency of transaction
        :return: currency
        :rtype: string
        """
        return self.payment_details.currency

    def get_amount(self):
        """
        Get transaction amount in EURO
        :return: transaction amount in EURO
        :rtype: float
        """
        return self.payment_details.amount / 100

    def get_currency_amount(self):
        """
        Get transaction amount in payment currency
        :return: transaction amount in payment currency
        :rtype: float
        """
        return self.payment_details.currency_amount / 100

    def get_paid_amount(self):
        """
        Get paid transaction amount in EURO
        :return: paid transaction amount in EURO
        :rtype: float
        """
        return self.payment_details.paid_amount / 100

    def get_paid_currency_amount(self):
        """
        Get paid transaction amount in payment currency
        :return: paid transaction amount in payment currency
        :rtype: float
        """
        return self.payment_details.paid_currency_amount / 100

    def get_refunded_amount(self):
        """
        Get refunded transaction amount in EURO
        :return: refunded transaction amount in EURO
        :rtype: float
        """
        return self.payment_details.refund_amount / 100

    def get_refunded_currency_amount(self):
        """
        Get refunded transaction amount in payment currency
        :return: refunded transaction amount in payment currency
        :rtype: float
        """
        return self.payment_details.refund_currency_amount / 100

    def __repr__(self):
        return str(self.__dict__)


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema)
    payment_details = fields.Nested(TransactionStatusDetailsSchema, load_from='paymentDetails')

    @post_load
    def create_response(self, data):
        return Response(**data)


class Request(RequestBase):
    """
    Response object for the Transaction::status API

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
        return 'status'

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
        :rtype: paynlsdk.api.transaction.status.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response

