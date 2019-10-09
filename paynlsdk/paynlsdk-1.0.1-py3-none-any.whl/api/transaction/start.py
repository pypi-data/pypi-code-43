import json

from marshmallow import Schema, fields, pre_load, post_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import TransactionData, TransactionStartStatsData, SalesData, TransactionEndUser, ErrorSchema,\
    TransactionStartEnduser, TransactionStartEnduserSchema, TransactionStartInfo, TransactionStartInfoSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    """
    Response object for the Transaction::start API

    :param TransactionStartEnduser end_user: enduser details
    :param TransactionStartInfo transaction: transaction details
    """
    def __init__(self,
                 end_user: TransactionStartEnduser=None,
                 transaction: TransactionStartInfo=None,
                 *args, **kwargs):
        self.end_user: TransactionStartEnduser = end_user
        self.transaction: TransactionStartInfo = transaction
        super().__init__(**kwargs)

    def get_redirect_url(self):
        return self.transaction.payment_url

    def get_payment_reference(self):
        return self.transaction.payment_reference

    def __repr__(self):
        return str(self.__dict__)


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema)
    end_user = fields.Nested(TransactionStartEnduserSchema, required=False, allow_none=True, load_from='endUser')
    transaction = fields.Nested(TransactionStartInfoSchema, required=False, allow_none=True)

    @pre_load
    def pre_processor(self, data):
        # Again, the API could return an empty string where it SHOULD return null or an empty object.
        if ParamValidator.is_empty(data['endUser']):
            del data['endUser']
        if ParamValidator.is_empty(data['transaction']):
            del data['transaction']
        return data

    @post_load
    def create_response(self, data):
        return Response(**data)


class Request(RequestBase):
    """
    Request object for the Transaction::start API

    :param int amount: transaction amount in cents
    :param str ip_address: IP address of end user
    :param str finish_url: URL where end user will be redirected to
    :param int payment_option_id: payment option ID
    :param int payment_option_sub_id: payment suboption ID
    :param TransactionData transaction: transaction data details
    :param TransactionStartStatsData stats_data: transaction stats data details
    :param TransactionEndUser end_user: transaction end user details
    :param SalesData sale_data: transaction sales details
    :param bool test_mode: True to perform transaction in TEST modus
    :param str transfer_type: transfer type.
                              Use transaction, merchant or alliance to change the benificiary owner of the transaction
    :param str transfer_value: transfer_value. MerchantId (M-xxxx-xxxx) or orderId
    """
    def __init__(self,
                 amount: int=None,
                 ip_address: str=None,
                 finish_url: str=None,
                 payment_option_id: int=None,
                 payment_option_sub_id: int=None,
                 transaction: TransactionData=None,
                 stats_data: TransactionStartStatsData=None,
                 end_user: TransactionEndUser=None,
                 sale_data: SalesData=None,
                 test_mode: bool=False,
                 transfer_type: str=None,
                 transfer_value: str=None,
                 ):
        self.amount = amount
        self.ip_address = ip_address
        self.finish_url = finish_url
        self.payment_option_id = payment_option_id
        self.payment_option_sub_id = payment_option_sub_id
        self.transaction: TransactionData = transaction
        self.stats_data: TransactionStartStatsData = stats_data
        self.end_user: TransactionEndUser = end_user
        self.sale_data: SalesData = sale_data
        self.test_mode = test_mode
        self.transfer_type = transfer_type
        self.transfer_value = transfer_value
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
        return 'start'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Validation
        ParamValidator.assert_not_empty(self.amount, 'amount')
        ParamValidator.assert_not_empty(self.ip_address, 'ip_address')
        ParamValidator.assert_not_empty(self.finish_url, 'finish_url')
        if ParamValidator.not_empty(self.transfer_value) and (self.transfer_type == 'transaction'
                                                              or self.transfer_type == 'merchant'):
            raise ValueError('TransferValue cannot be set without valid TransferType, please fix this.')
        # Default api parameters
        rs = self.get_std_parameters()
        #  Append our own parameters
        rs['amount'] = self.amount
        rs['ipAddress'] = self.ip_address
        rs['finishUrl'] = self.finish_url
        if ParamValidator.not_empty(self.payment_option_id):
            rs['paymentOptionId'] = self.payment_option_id
        if ParamValidator.not_empty(self.payment_option_sub_id):
            rs['paymentOptionSubId'] = self.payment_option_sub_id
        if self.test_mode:
            rs['testMode'] = 1
        else:
            rs['testMode'] = 0
        if ParamValidator.not_empty(self.transfer_type):
            rs['transferType'] = self.transfer_type
        if ParamValidator.not_empty(self.transfer_value):
            rs['transferValue'] = self.transfer_value
        # Now handle complex types
        self._merge_transaction_dict(rs)
        self._merge_stats_data_dict(rs)
        self._merge_sales_data_dict(rs)
        self._merge_end_user_dict(rs)
        return rs

    def _merge_transaction_dict(self, innerdict):
        if ParamValidator.is_null(self.transaction):
            return
        if ParamValidator.not_empty(self.transaction.currency):
            innerdict['transaction[currency]'] = self.transaction.currency
        if ParamValidator.not_empty(self.transaction.costs_vat):
            innerdict['transaction[costsVat]'] = self.transaction.costs_vat
        if ParamValidator.not_empty(self.transaction.order_exchange_url):
            innerdict['transaction[orderExchangeUrl]'] = self.transaction.order_exchange_url
        if ParamValidator.not_empty(self.transaction.description):
            innerdict['transaction[description]'] = self.transaction.description
        if ParamValidator.not_empty(self.transaction.expire_date):
            innerdict['transaction[expireDate]'] = self.transaction.expire_date.strftime('%d-%m-%Y %H:%M:%s')
        if ParamValidator.not_empty(self.transaction.order_number):
            innerdict['transaction[orderNumber]'] = self.transaction.order_number

    def _merge_stats_data_dict(self, innerdict):
        if ParamValidator.is_null(self.stats_data):
            return
        if ParamValidator.not_empty(self.stats_data.promotor_id):
            innerdict['statsData[promotorId]'] = self.stats_data.promotor_id
        if ParamValidator.not_empty(self.stats_data.info):
            innerdict['statsData[info]'] = self.stats_data.info
        if ParamValidator.not_empty(self.stats_data.tool):
            innerdict['statsData[tool]'] = self.stats_data.tool
        if ParamValidator.not_empty(self.stats_data.extra1):
            innerdict['statsData[extra1]'] = self.stats_data.extra1
        if ParamValidator.not_empty(self.stats_data.extra2):
            innerdict['statsData[extra2]'] = self.stats_data.extra2
        if ParamValidator.not_empty(self.stats_data.extra3):
            innerdict['statsData[extra3]'] = self.stats_data.extra3
        if ParamValidator.not_empty(self.stats_data.domain_id):
            innerdict['statsData[domainId]'] = self.stats_data.domain_id

    def _merge_sales_data_dict(self, innerdict):
        if ParamValidator.is_null(self.sale_data):
            return
        if not ParamValidator.is_null(self.sale_data.delivery_date):
            innerdict['saleData[deliveryDate]'] = self.sale_data.delivery_date.strftime('%d-%m-%Y')
        if not ParamValidator.is_null(self.sale_data.invoice_date):
            innerdict['saleData[invoiceDate]'] = self.sale_data.invoice_date.strftime('%d-%m-%Y')
        if ParamValidator.not_empty(self.sale_data.order_data) and len(self.sale_data.order_data) > 0:
            i=0
            for item in self.sale_data.order_data:
                ParamValidator.assert_not_empty(item.product_id, 'sales_data.order_data.product_id')
                ParamValidator.assert_not_empty(item.price, 'sales_data.order_data.price')
                ParamValidator.assert_not_empty(item.quantity, 'sales_data.order_data.quantity')
                innerdict['saleData[orderData][{}][productId]'.format(i)] = item.product_id
                innerdict['saleData[orderData][{}][price]'.format(i)] = item.price
                innerdict['saleData[orderData][{}][quantity]'.format(i)] = item.quantity
                if ParamValidator.not_empty(item.description):
                    innerdict['saleData[orderData][{}][description]'.format(i)] = item.description
                if ParamValidator.not_empty(item.vat_code):
                    innerdict['saleData[orderData][{}][vatCode]'.format(i)] = item.vat_code
                if ParamValidator.not_empty(item.vat_percentage):
                    innerdict['saleData[orderData][{}][vatPercentage]'.format(i)] = item.vat_percentage
                if ParamValidator.not_empty(item.product_type):
                    innerdict['saleData[orderData][{}][productType]'.format(i)] = item.product_type

    def _merge_end_user_dict(self, innerdict):
        if ParamValidator.is_null(self.end_user):
            return
        if ParamValidator.not_empty(self.end_user.access_code):
            innerdict['enduser[accessCode]'] = self.end_user.access_code
        if ParamValidator.not_empty(self.end_user.language):
            innerdict['enduser[language]'] = self.end_user.language
        if ParamValidator.not_empty(self.end_user.initials):
            innerdict['enduser[initials]'] = self.end_user.initials
        if ParamValidator.not_empty(self.end_user.last_name):
            innerdict['enduser[lastName]'] = self.end_user.last_name
        if ParamValidator.not_empty(self.end_user.gender):
            innerdict['enduser[gender]'] = self.end_user.gender
        if ParamValidator.not_empty(self.end_user.dob):
            innerdict['enduser[dob]'] = self.end_user.dob.strftime('%d-%m-%Y')
        if ParamValidator.not_empty(self.end_user.phone_number):
            innerdict['enduser[phoneNumber]'] = self.end_user.phone_number
        if ParamValidator.not_empty(self.end_user.email_address):
            innerdict['enduser[emailAddress]'] = self.end_user.email_address
        if ParamValidator.not_empty(self.end_user.bank_account):
            innerdict['enduser[bankAccount]'] = self.end_user.bank_account
        if ParamValidator.not_empty(self.end_user.iban):
            innerdict['enduser[iban]'] = self.end_user.iban
        if ParamValidator.not_empty(self.end_user.bic):
            innerdict['enduser[bic]'] = self.end_user.bic
        if self.end_user.send_confirm_email:
            innerdict['enduser[sendConfirmMail]'] = 1
        else:
            innerdict['enduser[sendConfirmMail]'] = 0
        if ParamValidator.not_empty(self.end_user.customer_reference):
            innerdict['enduser[customerReference]'] = self.end_user.customer_reference
        if ParamValidator.not_empty(self.end_user.customer_trust):
            innerdict['enduser[customerTrust]'] = self.end_user.customer_trust
        if not ParamValidator.is_null(self.end_user.address):
            if not ParamValidator.is_empty(self.end_user.address.street_name):
                innerdict['enduser[address][streetName]'] = self.end_user.address.street_name
            if not ParamValidator.is_empty(self.end_user.address.street_number):
                innerdict['enduser[address][streetNumber]'] = self.end_user.address.street_number
            if not ParamValidator.is_empty(self.end_user.address.street_number_extension):
                innerdict['enduser[address][streetNumberExtension]'] = self.end_user.address.street_number_extension
            if not ParamValidator.is_empty(self.end_user.address.zip_code):
                innerdict['enduser[address][zipCode]'] = self.end_user.address.zip_code
            if not ParamValidator.is_empty(self.end_user.address.city):
                innerdict['enduser[address][city]'] = self.end_user.address.city
            if not ParamValidator.is_empty(self.end_user.address.region_code):
                innerdict['enduser[address][regionCode]'] = self.end_user.address.region_code
            if not ParamValidator.is_empty(self.end_user.address.country_code):
                innerdict['enduser[address][countryCode]'] = self.end_user.address.country_code
        if not ParamValidator.is_null(self.end_user.invoice_address):
            if not ParamValidator.is_empty(self.end_user.invoice_address.initials):
                innerdict['enduser[invoiceAddress][initials]'] = self.end_user.invoice_address.initials
            if not ParamValidator.is_empty(self.end_user.invoice_address.last_name):
                innerdict['enduser[invoiceAddress][lastName]'] = self.end_user.invoice_address.last_name
            if not ParamValidator.is_empty(self.end_user.invoice_address.gender):
                innerdict['enduser[invoiceAddress][gender]'] = self.end_user.invoice_address.gender
            if not ParamValidator.is_empty(self.end_user.invoice_address.street_name):
                innerdict['enduser[invoiceAddress][streetName]'] = self.end_user.invoice_address.street_name
            if not ParamValidator.is_empty(self.end_user.invoice_address.street_number):
                innerdict['enduser[invoiceAddress][streetNumber]'] = self.end_user.invoice_address.street_number
            if not ParamValidator.is_empty(self.end_user.invoice_address.street_number_extension):
                innerdict['enduser[invoiceAddress][streetNumberExtension]'] = self.end_user.invoice_address.street_number_extension
            if not ParamValidator.is_empty(self.end_user.invoice_address.zip_code):
                innerdict['enduser[invoiceAddress][zipCode]'] = self.end_user.invoice_address.zip_code
            if not ParamValidator.is_empty(self.end_user.invoice_address.city):
                innerdict['enduser[invoiceAddress][city]'] = self.end_user.invoice_address.city
            if not ParamValidator.is_empty(self.end_user.invoice_address.region_code):
                innerdict['enduser[invoiceAddress][regionCode]'] = self.end_user.invoice_address.region_code
            if not ParamValidator.is_empty(self.end_user.invoice_address.country_code):
                innerdict['enduser[invoiceAddress][countryCode]'] = self.end_user.invoice_address.country_code
        if not ParamValidator.is_null(self.end_user.company):
            if not ParamValidator.is_empty(self.end_user.company.name):
                innerdict['enduser[company][name]'] = self.end_user.company.name
            if not ParamValidator.is_empty(self.end_user.company.coc_number):
                innerdict['enduser[company][cocNumber]'] = self.end_user.company.coc_number
            if not ParamValidator.is_empty(self.end_user.company.vat_number):
                innerdict['enduser[company][vatNumber]'] = self.end_user.company.vat_number
            if not ParamValidator.is_empty(self.end_user.company.country_code):
                innerdict['enduser[company][countryCode]'] = self.end_user.company.country_code

    @RequestBase.raw_response.setter
    def raw_response(self, raw_response):
        self._raw_response = raw_response
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
        :rtype: paynlsdk.api.transaction.start.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response

