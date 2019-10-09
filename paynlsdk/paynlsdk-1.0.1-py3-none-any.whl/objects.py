from datetime import datetime
from typing import List, Dict

from marshmallow import Schema, fields, post_load, pre_load
from paynlsdk.validators import ParamValidator


class Error(object):
    """
    This class represents the result of a call to the API.
    It does not necessarily represent a failed call because this implies the result of the call itself
    """
    def __init__(self, result: bool=None, code: str=None, message: str=None):
        """

        :param result: outcome of the result. This indicates whether we have a failed or successful result
        :type result: bool
        :param code: Error code.
                     Do note this is not an integer as in many other languages when e.g. raising exceptions.
                     This code is usually only filled when the result was False
        :type code: str
        :param message: Error message if any. This is usually only filled with a value if the result was False
        :type message: str
        """
        self.result = result
        self.code = code
        self.message = message

    def __repr__(self):
        return self.__dict__.__str__()


class ErrorSchema(Schema):
    result = fields.Boolean()
    code = fields.String(load_from='errorId')
    message = fields.String(load_from='errorMessage')

    @post_load
    def create_error(self, data):
        return Error(**data)


class Address(object):
    """
    Address details structure
    """
    def __init__(self, initials: str=None, last_name: str=None, gender: str=None, street_name: str=None,
                 street_number: str = None, street_number_extension: str=None, zip_code: str=None, city: str=None,
                 region_code: str=None, country_code: str=None, country_name: str=None):
        """
        Create address instance

        :param initials: Initials
        :type initials: str
        :param last_name: Last name
        :type last_name: str
        :param gender: Gender (m or f)
        :type gender: str
        :param street_name: Street name
        :type street_name: str
        :param street_number: Street number
        :type street_number: str
        :param street_number_extension: Street number extension
        :type street_number_extension: str
        :param zip_code: Zip code
        :type zip_code:str
        :param city: City
        :type city: str
        :param region_code:Region code or province
        :type region_code: str
        :param country_code: Country code (ISO)
        :type country_code: str
        :param country_name: Country name
        :type country_name: str
        """
        self.initials = initials
        self.last_name = last_name
        self.gender = gender
        self.street_name = street_name
        self.street_number = street_number
        self.street_number_extension = street_number_extension
        self.zip_code = zip_code
        self.city = city
        self.region_code = region_code
        self.country_code = country_code
        self.country_name = country_name

    def __repr__(self):
        return str(self.__dict__)


class AddressSchema2(Schema):
    initials = fields.String()
    lastName = fields.String(attribute='last_name')
    gender = fields.String()
    streetName = fields.String(attribute='street_name')
    streetNumber = fields.String(attribute='street_number')
    zipCode = fields.String(attribute='zip_code')
    city = fields.String()
    countryCode = fields.String(attribute='country_code')
    countryName = fields.String(attribute='country_name')

    @post_load
    def create_address(self, data):
        return Address(**data)


class AddressSchema(Schema):
    initials = fields.String(required=False)
    last_name = fields.String(required=False, load_from='lastName')
    gender = fields.String(required=False)
    street_name = fields.String(load_from='streetName')
    street_number = fields.String(load_from='streetNumber')
    zip_code = fields.String(load_from='zipCode')
    city = fields.String()
    country_code = fields.String(load_from='countryCode')
    country_name = fields.String(required=False, load_from='countryName')
    street_number_extension = fields.String(required=False, allow_none=True, load_from='streetNumberExtension')
    region_code = fields.String(required=False, allow_none=True, load_from='regionCode')

    @post_load
    def create_address(self, data):
        return Address(**data)


class Company(object):
    """
    Company details structure
    """
    def __init__(self, name: str=None, coc_number: str=None, vat_number: str=None, country_code: str=None):
        """
        Create company details instance

        :param name: company name
        :type name: str
        :param coc_number: Company COC number (KVK)
        :type coc_number: str
        :param vat_number: VAT registration number
        :type vat_number: str
        :param country_code: Company country code
        :type country_code: str
        """
        self.name = name
        self.coc_number = coc_number
        self.vat_number = vat_number
        self.country_code = country_code

    def __repr__(self):
        return str(self.__dict__)


class CompanySchema(Schema):
    name = fields.String()
    coc_number = fields.String(load_from='cocNumber')
    vat_number = fields.String(load_from='vatNumber')
    country_code = fields.String(load_from='countryCode')


class Merchant(object):
    """
    Merchant details structure
    """
    def __init__(self, id: str=None, name: str=None, public_name: str=None, state: int=None):
        """
        Create instance of Merchant details

        :param id: merchant ID (M-xxxx-xxxx)
        :type id: str
        :param name: Merchant name
        :type name: str
        :param public_name: Merchant public name
        :type public_name: str
        :param state: Merchant status (indicates active state: 0 - inactive, 1 - active)
        :type state: int
        """
        self.id = id
        self.name = name
        self.public_name = public_name
        self.state = state  # TODO: active state enum

    def __repr__(self):
        return str(self.__dict__)


class MerchantSchema(Schema):
    id = fields.String()
    name = fields.String()
    public_name = fields.String(load_from='publicName')
    state = fields.Integer()  # TODO: active state enum

    @post_load
    def create_merchant(self, data):
        return Merchant(**data)


class PaymentMethod(object):
    """
    Payment method details structure
    """
    def __init__(self, id: int=None, name: str=None, abbreviation: str=None):
        """
        Create instance of payment method details

        :param id: Payment method ID
        :type id: int
        :param name: Payment method name
        :type name: str
        :param abbreviation: Payment method abbreviation
        :type abbreviation: str
        """
        self.id = id
        self.name = name
        self.abbreviation = abbreviation

    def __repr__(self):
        return str(self.__dict__)


class PaymentMethodSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    abbreviation = fields.String()

    @post_load
    def create_payment_method(self, data):
        return PaymentMethod(**data)


class ServiceCategory(object):
    """
    Service category details structure
    """
    def __init__(self, id: str=None, name: str=None):
        """
        Create service category instance

        :param id: Service category ID
        :type id: str
        :param name: Service category name
        :type name: str
        """
        self.id = id
        self.name = name

    def __repr__(self):
        return str(self.__dict__)


class ServiceCategorySchema(Schema):
    id = fields.String()  # TODO: isn't this an integer?
    name = fields.String()

    @post_load
    def create_service_category(self, data):
        return ServiceCategory(**data)


class OrderData(object):
    """
    Order data details structure
    """
    def __init__(self,
                 product_id=None,
                 description=None,
                 price=None,
                 quantity=None,
                 vat_code=None,
                 vat_percentage=None,
                 product_type=None,
                 ):
        """
        Create instance of Order data details

        .. seealso::
            :class:`paynlsdk.enums.enums.TaxClassCategory` for the :attr:`vat_code` values

            :class:`paynlsdk.enums.enums.ProductType` for the :attr:`product_type` values

        :param product_id: Product ID
        :type product_id: str
        :param description: Product description
        :type description: str
        :param price: Product price (cents)
        :type price: int
        :param quantity: Product quantity
        :type quantity: int
        :param vat_code: VAT code (N, L or H)
        :type vat_code: str
        :param vat_percentage: VAT percentage
        :type vat_percentage: float
        :param product_type: Product type
        :type product_type: str
        """
        self.product_id = product_id
        self.description = description
        self.price = price
        self.quantity = quantity
        self.vat_code = vat_code
        self.vat_percentage = vat_percentage
        self.product_type = product_type

    def __repr__(self):
        return str(self.__dict__)


class OrderDataSchema(Schema):
    product_id = fields.String(load_from='productId')
    description = fields.String(required=False)
    price = fields.Integer()
    quantity = fields.Integer()
    vat_code = fields.String(load_from='vatCode')  # Enum:VAT
    vat_percentage = fields.String(load_from='vatPercentage', required=False, allow_none=True)
    product_type = fields.String(load_from='productType', required=False)  # Enum:productType

    @post_load
    def create_order_data(self, data):
        return OrderData(**data)


class SalesData(object):
    """
    Sales data details structure
    """
    def __init__(self, invoice_date: datetime=None, delivery_date: datetime=None, order_data: List[OrderData]=[]):
        """
        Create instance of SalesData details

        .. seealso::
            :class:`paynlsdk.objects.OrderData` for the order data structure

        :param invoice_date: invoice date
        :type invoice_date: str
        :param delivery_date: delivery date
        :type delivery_date: str
        :param order_data: Order data list
        :type order_data: List[OrderData]
        """
        self.invoice_date = invoice_date
        self.delivery_date = delivery_date
        self.order_data: List[OrderData] = order_data  # TODO: is a LIST

    def __repr__(self):
        return str(self.__dict__)


class SalesDataSchema(Schema):
    invoice_date = fields.DateTime(format='%d-%m-%Y', allow_none=True, load_from='invoiceDate')
    delivery_date = fields.DateTime(format='%d-%m-%Y', allow_none=True, load_from='deliveryDate')
    order_data = fields.List(fields.Nested(OrderDataSchema), allow_none=True, required=False, Partial=True, load_from='orderData')

    @post_load
    def create_sales_data(self, data):
        return SalesData(**data)

    @pre_load
    def pre_processor(self, data):
        if ParamValidator.is_empty(data['invoiceDate']):
            data['invoiceDate'] = None
        if ParamValidator.is_empty(data['deliveryDate']):
            data['deliveryDate'] = None
        if ParamValidator.is_empty(data['orderData']):
            data['orderData'] = None
        # TODO: orderdata probably, yet again, is a DICT of complex...
        return data


class Service(object):
    """
    Service details structure
    """
    def __init__(self, id=None, name=None, description=None, publication=None, base_path=None,
                 module=None, sub_module=None, state=None, success_url=None, error_url=None, secret: str=None):
        """
        Create Service details instance

        .. seealso::
            :class:`paynlsdk.enums.enums.ActiveState.OrderData` for the state attribute

        :param id: Service ID
        :type id: str
        :param name: Service name
        :type name: str
        :param description: Service description
        :type description: str
        :param publication: Service publication
        :type publication: str
        :param base_path: Service base path
        :type base_path: str
        :param module: Service module ID
        :type module: int
        :param sub_module: Service sub module ID
        :type sub_module: int
        :param state: Service status
        :type state: str
        :param success_url: Service callback url on success
        :type success_url: str
        :param error_url: Service callback url on errors
        :type error_url: str
        :param secret: Service secret
        :type secret: str
        """
        self.id = id
        self.name = name
        self.description = description
        self.publication = publication
        self.base_path = base_path
        self.module = module
        self.sub_module = sub_module
        self.state = state  # TODO: Enum ActiveState
        self.success_url = success_url
        self.error_url = error_url
        self.secret = secret

    def __repr__(self):
        return str(self.__dict__)


class ServiceSchema(Schema):
    id = fields.String()
    name = fields.String()
    description = fields.String()
    publication = fields.String()
    base_path = fields.String(load_from='basePath')
    module = fields.Integer()
    sub_module = fields.Integer(load_from='subModule')
    state = fields.Integer()  # TODO: Enum ActiveState
    success_url = fields.Url(load_from='successUrl', allow_none=True, required=False)
    error_url = fields.Url(load_from='errorUrl', allow_none=True, required=False)
    secret = fields.String(allow_none=True, required=False)

    @pre_load
    def pre_process(self, data):
        if ParamValidator.is_empty(data['errorUrl']):
            del data['errorUrl']
        if ParamValidator.is_empty(data['successUrl']):
            del data['successUrl']
        return data

    @post_load
    def create_service(self, data):
        return Service(**data)


class PaymentProfile(object):
    """
    Payment profile details structure
    """
    def __init__(self, id: int=None, name: str=None, parent_id: int=None, public: bool=False,
                 payment_method_id: int=None, country_id: int=None, payment_tariff_id: int=None, noa_id: int=None):
        """
        Create instance of payment profile details

        :param id: Payment profile ID
        :type id: int
        :param name: Payment profile name
        :type name: str
        :param parent_id: Payment profile parent ID
        :type parent_id: int
        :param public: Payment profile status
        :type public: bool
        :param payment_method_id: Payment method ID this payment profile belongs to
        :type payment_method_id: int
        :param country_id: Country ID
        :type country_id: int
        :param payment_tariff_id: Tariff ID
        :type payment_tariff_id: int
        :param noa_id: NOA ID
        :type noa_id: int
        """
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.public = public
        self.payment_method_id = payment_method_id
        self.country_id = country_id
        self.payment_tariff_id = payment_tariff_id
        self.noa_id = noa_id

    def __repr__(self):
        return str(self.__dict__)


class PaymentProfileSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    parent_id = fields.Integer()
    public = fields.Boolean()
    payment_method_id = fields.Integer()
    country_id = fields.Integer()
    payment_tariff_id = fields.Integer()
    noa_id = fields.Integer()

    @post_load
    def create_payment_profile(self, data):
        return PaymentProfile(**data)


class CountryId(object):
    """
    Country details structure
    """
    def __init__(self, id: str=None, name: str=None):
        """
        Create country detail structure

        :param id: Country ID (ISO)
        :type id: str
        :param name: Country name
        :type name: str
        """
        self.id: str = id
        self.name: str = name

    def __repr__(self):
        return str(self.__dict__)


class CountryIdSchema(Schema):
    id = fields.String()
    name = fields.String()

    @post_load
    def create_country(self, data):
        return CountryId(**data)


class ServicePaymentProfile(object):
    """
    Payment profile details structure

    .. seealso::
        :class:`paynlsdk.objects.CountryId` for usage of the :attr:`countries` attribute

        :class:`paynlsdk.api.transaction.getservicepaymentoptions.Response` for usage

        :class:`paynlsdk.client.transaction.get_service_payment_options` for usage

        :class:`paynlsdk.client.paymentmethods.get_list` for usage

    """
    def __init__(self, id: int=None, name: str=None, visible_name: str=None,
                 costs_fixed: int=0, costs_percentage: float=0, countries: List[CountryId]=None):
        """
        Create payment profile details

        .. seealso::
            :class:`paynlsdk.objects.CountryId` for usage of the :attr:`countries` attribute

            :class:`paynlsdk.api.transaction.getservicepaymentoptions.Response` for usage

            :class:`paynlsdk.client.transaction.get_service_payment_options` for usage

            :class:`paynlsdk.client.paymentmethods.get_list` for usage

        :param id: ID
        :type id: int
        :param name: name
        :type name: str
        :param visible_name: visible name
        :type visible_name: str
        :param costs_fixed: fixed cost
        :type costs_fixed: int
        :param costs_percentage: cost percentage
        :type costs_percentage: float
        :param countries: countries
        :type countries: List[CountryId]
        """
        self.id = id
        self.name = name
        self.visible_name = visible_name
        self.costs_fixed: int = costs_fixed
        self.costs_percentage: float = costs_percentage
        self.countries: List[CountryId] = countries

    def __repr__(self):
        return str(self.__dict__)


class ServicePaymentProfileSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    visible_name = fields.String(load_from='visibleName')
    costs_fixed = fields.Integer(load_from='costsFixed')
    costs_percentage = fields.Float(load_from='costsPercentage')
    countries = fields.List(fields.Nested(CountryIdSchema))

    @pre_load
    def pre_processor(self, data):
        if ParamValidator.is_empty(data['countries']):
            del data['countries']
        elif 'countries' in data and ParamValidator.not_empty(data['countries']):
            #  Undo the key-mapping in the source
            list = []
            for i, item in data['countries'].items():
                list.append(item)
            data['countries'] = list
        return data

    @post_load
    def create_service_payment_profile(self, data):
        return ServicePaymentProfile(**data)


class RefundInfo(object):
    """
    Refund info details structure
    """
    def __init__(self, payment_session_id: int=None, amount: int=None, description: str=None,
                 bank_account_holder: str=None, bank_account_number: str=None, bank_account_bic: str=None,
                 status_code: int=None, status_name: str=None, process_date: datetime=None):
        self.payment_session_id = payment_session_id
        self.amount = amount
        self.description = description
        self.bank_account_holder = bank_account_holder
        self.bank_account_number = bank_account_number
        self.bank_account_bic = bank_account_bic
        self.status_code = status_code
        self.status_name = status_name
        self.process_date = process_date

    def __repr__(self):
        return str(self.__dict__)


class RefundInfoSchema(Schema):
    payment_session_id = fields.Integer(required=True, load_from='paymentSessionId')
    amount = fields.Integer(required=True, )
    description = fields.String(required=True, )
    bank_account_holder = fields.String(required=True, load_from='bankAccountHolder')
    bank_account_number = fields.String(required=True, load_from='bankAccountNumber')
    bank_account_bic = fields.String(required=True, load_from='bankAccountBic')
    status_code = fields.Integer(required=True, load_from='statusCode')
    status_name = fields.String(required=True, load_from='statusName')
    process_date = fields.DateTime(format='%Y-%m-%d', required=True, load_from='processDate')

    @post_load
    def create_refund_info(self, data):
        return RefundInfo(**data)


class TransactionStartInfo(object):
    """
    Transaction start info details structure
    """
    def __init__(self, transaction_id: str=None, payment_url: str=None,
                 popup_allowed: bool=False, payment_reference: str=None):
        """
        Transaction start result sructure

        :param transaction_id: transaction ID
        :type transaction_id: str
        :param payment_url: payment URL - use this to redirect the user to the payment screen
        :type payment_url: str
        :param popup_allowed: popup allowed?
        :type popup_allowed: bool
        :param payment_reference: payment reference
        :type payment_reference: str
        """
        self.transaction_id = transaction_id
        self.payment_url = payment_url
        self.popup_allowed = popup_allowed
        self.payment_reference = payment_reference

    def __repr__(self):
        return str(self.__dict__)


class TransactionStartInfoSchema(Schema):
    transaction_id = fields.String(load_from='transactionId', required=False, allow_none=True)
    payment_url = fields.Url(load_from='paymentURL', required=False, allow_none=True)
    popup_allowed = fields.Boolean(load_from='popupAllowed', required=False, allow_none=True)
    payment_reference = fields.String(load_from='paymentReference', required=False, allow_none=True)

    @post_load
    def create_transaction_start_info(self, data):
        return TransactionStartInfo(**data)


class StornoDetails(object):
    """
    Storno information details structure
    """
    def __init__(self,
                 storno_id=None,
                 storno_amount=None,
                 bank_account=None,
                 iban=None,
                 bic=None,
                 city=None,
                 date=None,
                 reason=None,
                 email_address=None
                 ):
        """
        Storno details structure

        :param storno_id: storno ID
        :type storno_id: int
        :param storno_amount: storno amount
        :type storno_amount: int
        :param bank_account: bank account number
        :type bank_account: str
        :param iban: IBAN number
        :type iban: str
        :param bic: BIC number
        :type bic: str
        :param city: city
        :type city: str
        :param date: storno date
        :type date: str
        :param reason: storno reason
        :type reason: str
        :param email_address: consumer email address
        :type email_address: str
        """
        self.storno_id = storno_id
        self.storno_amount = storno_amount
        self.bank_account = bank_account
        self.iban = iban
        self.bic = bic
        self.city = city
        self.date = date
        self.reason = reason
        self.email_address = email_address

    def __repr__(self):
        return str(self.__dict__)


class StornoDetailsSchema(Schema):
    storno_id = fields.Integer(load_from='stornoId')
    storno_amount = fields.Integer(load_from='stornoAmount')
    bank_account = fields.String(load_from='bankAccount')
    iban = fields.String()
    bic = fields.String()
    city = fields.String()
    date = fields.String(load_from='datetime')  # TODO: should be datetime instance
    reason = fields.String()
    email_address = fields.String(load_from='emailAddress')

    @pre_load
    def pre_processor(self, data):
        if type(data['stornoId']) == str and data['stornoId'] == '':
            data['stornoId'] = 0
        if type(data['stornoAmount']) == str and data['stornoAmount'] == '':
            data['stornoAmount'] = 0
        # In case we have empty integers on some objects
        return data

    @post_load
    def create_storno_details(self, data):
        return StornoDetails(**data)


class TransactionStartEnduser(object):
    """
    Transaction start info details structure used at the API response

    .. seealso::
        :class:`paynlsdk.api.transaction.start.Response` for usage details
    """
    def __init__(self, blacklist: int=None):
        """
        Create transaction start user response structure

        .. seealso::
            :class:`paynlsdk.api.transaction.start.Response` for usage details

            :class:`paynlsdk.enums.enums.Blacklist` for possible *blacklist* values

        :param blacklist: blacklist bit (0, 1 or 2)
        :type blacklist: int
        """
        self.blacklist = blacklist

    def __repr__(self):
        return str(self.__dict__)


class TransactionStartEnduserSchema(Schema):
    blacklist = fields.Integer()  # TODO: Enum type Blacklist

    @post_load
    def create_transaction_end_user(self, data):
        return TransactionStartEnduser(**data)


class TransactionData(object):
    """
    Transaction data structure
    """
    def __init__(self, currency=None, costs_vat=None, order_exchange_url=None, description=None, expire_date: datetime=None,
                 order_number=None):
        """
        Transaction data structure

        :param currency: currency
        :type currency: str
        :param costs_vat: costs VAT
        :type costs_vat: int
        :param order_exchange_url: exchange url
        :type order_exchange_url: str
        :param description: description
        :type description: str
        :param expire_date: transaction expiry date
        :type expire_date: datetime
        :param order_number: order number
        :type order_number: str
        """
        self.currency = currency
        self.costs_vat = costs_vat
        self.order_exchange_url = order_exchange_url
        self.description = description
        self.expire_date = expire_date
        self.order_number = order_number

    def __repr__(self):
        return str(self.__dict__)


class TransactionDataSchema(Schema):
    currency = fields.String()
    costs_vat = fields.Integer(load_from='CostsVat')  # optional
    order_exchange_url = fields.String(load_from='orderExchangeUrl')
    description = fields.String()
    expire_date = fields.DateTime(format='%d-%m-%Y %H:%M:%s', load_from='expireDate', allow_none=True, required=False)
    order_number = fields.String(load_from='orderNumber')

    @post_load
    def create_transaction_data(self, data):
        return TransactionData(**data)


class TransactionStats(object):
    """
    Transaction stats data structure
    """
    def __init__(self, id=None, website_name=None, service_name=None, service_code=None, order_amount=None,
                 created=None, internal_status=None, consumer_3d_secure=None, consumer_account_number=None,
                 profile_id=None, profile_name=None):
        """
        Transaction stats structure

        ..seealso::
            :class:`paynlsdk.enums.enums.Secure` for *consumer_3d_secure* possible values

        :param id: ID
        :type id: str
        :param website_name: website name
        :type website_name: str
        :param service_name: service name
        :type service_name: str
        :param service_code: service code
        :type service_code: str
        :param order_amount: order amount (cents)
        :type order_amount: int
        :param created: created on
        :type created: str
        :param internal_status: internal status
        :type internal_status: int
        :param consumer_3d_secure: 3d security
        :type consumer_3d_secure: int
        :param consumer_account_number: account number of consumer
        :type consumer_account_number: str
        :param profile_id: profile ID
        :type profile_id: int
        :param profile_name: profile name
        :type profile_name: str
        """
        self.id = id
        self.website_name = website_name
        self.service_name = service_name
        self.service_code = service_code
        self.order_amount = order_amount
        self.created = created
        self.internal_status = internal_status
        self.consumer_3d_secure = consumer_3d_secure
        self.consumer_account_number = consumer_account_number
        self.profile_id = profile_id
        self.profile_name = profile_name

    def __repr__(self):
        return str(self.__dict__)


class TransactionStatsSchema(Schema):
    id = fields.String()
    website_name = fields.String(load_from='websiteName')
    service_name = fields.String(load_from='serviceName')
    service_code = fields.String(load_from='serviceCode')
    order_amount = fields.String(load_from='orderAmount')
    created = fields.String()  # YMDHIS
    internal_status = fields.Integer(load_from='internalStatus')
    consumer_3d_secure = fields.String(load_from='consumer3dsecure')
    profile_id = fields.Integer(load_from='profileId')
    profile_name = fields.String(load_from='profileName')

    @post_load
    def create_transaction_stats(self, data):
        return TransactionStats(**data)


class Connection(object):
    """
    Connection details data structure
    """
    def __init__(self, trust=None, country=None, city=None, location_lat=None, location_lon=None,
                 browser_data=None, ip_address=None, blacklist=None, host=None, order_ip_address=None,
                 order_return_url=None, merchant_code=None, merchant_name=None):
        """
        Connection details structure

        :param trust: connection trust indication (-10 - 10)
        :type trust: int
        :param country: country
        :type country: str
        :param city: city
        :type city: str
        :param location_lat: location latitude
        :type location_lat: str
        :param location_lon: location longitude
        :type location_lon: str
        :param browser_data: browser data
        :type browser_data: str
        :param ip_address: IP address
        :type ip_address: str
        :param blacklist: blacklist indication
        :type blacklist: int
        :param host: host info
        :type host: str
        :param order_ip_address: order IP address
        :type order_ip_address: str
        :param order_return_url: order return url
        :type order_return_url: str
        :param merchant_code: merchant code (M-xxxx-xxxx)
        :type merchant_code: str
        :param merchant_name: Merchant name
        :type merchant_name: str
        """
        self.trust = trust
        self.country = country
        self.city = city
        self.location_lat = location_lat
        self.location_lon = location_lon
        self.browser_data = browser_data
        self.ip_address = ip_address
        self.blacklist = blacklist
        self.host = host
        self.order_ip_address = order_ip_address
        self.order_return_url = order_return_url
        self.merchant_code = merchant_code
        self.merchant_name = merchant_name

    def __repr__(self):
        return str(self.__dict__)


class ConnectionSchema(Schema):
    trust = fields.Integer()  # optional (-10,10)
    country = fields.String()
    city = fields.String()
    location_lat = fields.String(load_from='locationLat')
    location_lon = fields.String(load_from='locationLon')
    browser_data = fields.String(load_from='browserData')
    ip_address = fields.String(load_from='ipAddress')
    blacklist = fields.String()  #optional; Enum:Blacklist
    host = fields.String()
    order_ip_address = fields.String(load_from='orderIpAddress')
    order_return_url = fields.String(load_from='orderReturnUrl')
    merchant_code = fields.String(load_from='merchantCode')
    merchant_name = fields.String(load_from='merchantName')

    @post_load
    def create_connection(self, data):
        return Connection(**data)


class TransactionStartStatsData(object):
    """
    Transaction stats data structure used at API request

    .. seealso::
        :class:`paynlsdk.api.transaction.start.Request` for usage example
    """
    def __init__(self, promotor_id: int=None, info: str=None, tool: str=None,
                 extra1: str=None, extra2: str=None, extra3: str=None, domain_id=None):
        """
        Create stats details instance

        .. seealso::
            :class:`paynlsdk.api.transaction.start.Request` for usage example

        :param promotor_id: promotor ID
        :type promotor_id: int
        :param info: information
        :type info: str
        :param tool: tool identifiction
        :type tool: str
        :param extra1: extra information field 1
        :type extra1: str
        :param extra2: extra information field 2
        :type extra2: str
        :param extra3: extra information field 3
        :type extra3: str
        :param domain_id: domain ID
        :type domain_id: str
        """
        self.promotor_id = promotor_id
        self.info = info
        self.tool = tool
        self.extra1 = extra1
        self.extra2 = extra2
        self.extra3 = extra3
        self.domain_id = domain_id

    def __repr__(self):
        return str(self.__dict__)


class StatsDetails(object):
    """
    STats details data structure
    """
    def __init__(self, payment_session_id: int=None, tool: str=None, info: str=None, promotor_id: int=None,
                 extra1: str=None, extra2: str=None, extra3: str=None, object: str=None):
        """
        Create stats details instance

        :param payment_session_id: payment session id
        :type payment_session_id: int
        :param tool: tool identifiction
        :type tool: str
        :param info: information
        :type info: str
        :param promotor_id: promotor ID
        :type promotor_id: int
        :param extra1: extra information field 1
        :type extra1: str
        :param extra2: extra information field 2
        :type extra2: str
        :param extra3: extra information field 3
        :type extra3: str
        :param object: object identification
        :type object: str
        """
        self.payment_session_id = payment_session_id
        self.tool = tool
        self.info = info
        self.promotor_id = promotor_id
        self.extra1 = extra1
        self.extra2 = extra2
        self.extra3 = extra3
        self.object = object

    def __repr__(self):
        return str(self.__dict__)


class StatsDetailsSchema(Schema):
    payment_session_id = fields.Integer(load_from='paymentSessionId')  # optional
    tool = fields.String()
    info = fields.String()
    promotor_id = fields.Integer(load_from='promotorId')
    extra1 = fields.String()
    extra2 = fields.String()
    extra3 = fields.String()
    object = fields.String()

    @post_load
    def create_stats_details(self, data):
        return StatsDetails(**data)


class PaymentDetails(object):
    """
    Payment details data structure
    """
    def __init__(self,
                 amount=None,
                 currency_amount=None,
                 paid_amount=None,
                 paid_currency_amount=None,
                 paid_base=None,
                 paid_costs=None,
                 paid_costs_vat=None,
                 paid_currency=None,
                 paid_attempts=None,
                 paid_duration=None,
                 description=None,
                 process_time=None,
                 state=None,
                 state_name=None,
                 state_description=None,
                 exchange=None,
                 storno=None,
                 payment_option_id=None,
                 payment_option_sub_id=None,
                 secure=None,
                 secure_status=None,
                 identifier_name=None,
                 identifier_public=None,
                 identifier_hash=None,
                 service_id=None,
                 service_name=None,
                 service_description=None,
                 created=None,
                 modified=None,
                 payment_method_id=None,
                 payment_method_name=None,
                 payment_method_description=None,
                 payment_profile_name=None,
                 ):
        self.amount = amount
        self.currency_amount = currency_amount
        self.paid_amount = paid_amount
        self.paid_currency_amount = paid_currency_amount
        self.paid_base = paid_base
        self.paid_costs = paid_costs
        self.paid_costs_vat = paid_costs_vat
        self.paid_currency = paid_currency
        self.paid_attempts = paid_attempts
        self.paid_duration = paid_duration
        self.description = description
        self.process_time = process_time
        self.state = state
        self.state_name = state_name
        self.state_description = state_description
        self.exchange = exchange
        self.storno = storno
        self.payment_option_id = payment_option_id
        self.payment_option_sub_id = payment_option_sub_id
        self.secure = secure
        self.secure_status = secure_status
        self.identifier_name = identifier_name
        self.identifier_public = identifier_public
        self.identifier_hash = identifier_hash
        self.service_id = service_id
        self.service_name = service_name
        self.service_description = service_description
        self.created = created
        self.modified = modified
        self.payment_method_id = payment_method_id
        self.payment_method_name = payment_method_name
        self.payment_method_description = payment_method_description
        self.payment_profile_name = payment_profile_name

    def __repr__(self):
        return str(self.__dict__)


class PaymentDetailsSchema(Schema):
    amount = fields.Integer()
    currency_amount = fields.Integer(load_from='currencyAmount')
    paid_amount = fields.Integer(load_from='paidAmount')  # Incorrectly specified in API (should be int, not string)
    paid_currency_amount = fields.Integer(load_from='paidCurrencyAmount')  # Incorrectly specified in API (should be int, not string)
    paid_base = fields.Integer(load_from='paidBase')  # Incorrectly specified in API (should be int, not string)
    paid_costs = fields.Integer(load_from='paidCosts')  # Incorrectly specified in API (should be int, not string)
    paid_costs_vat = fields.String(load_from='paidCostsVat')
    paid_currency = fields.String(load_from='paidCurrency')
    paid_attempts = fields.Integer(load_from='paidAttempts')  # Incorrectly specified in API (should be int, not string)
    paid_duration = fields.String(load_from='paidDuration')  # Incorrectly specified in API (can't be string, can it?)
    description = fields.String()
    process_time = fields.String(load_from='processTime')
    state = fields.Integer(load_from='state')  #Enum,:paymentstatus
    state_name = fields.String(load_from='stateName')
    state_description = fields.String(load_from='stateDescription')
    exchange = fields.String()
    storno = fields.Boolean()
    payment_option_id = fields.Integer()
    payment_option_sub_id = fields.Integer()
    secure = fields.String()  # Enum: Secure
    secure_status = fields.String()
    identifier_name = fields.String(load_from='identifierName')
    identifier_public = fields.String(load_from='identifierPublic')
    identifier_hash = fields.String(load_from='identifierHash')
    service_id = fields.String(load_from='serviceId')
    service_name = fields.String(load_from='serviceName')
    service_description = fields.String(load_from='serviceDescription')
    created = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)
    modified = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)
    payment_method_id = fields.String(load_from='paymentMethodId')  # Incorrectly specified in API (should be Int)?
    payment_method_name = fields.String(load_from='paymentMethodName')
    payment_method_description = fields.String(load_from='paymentMethodDescription')
    payment_profile_name = fields.String(load_from='paymentProfileName')


    @post_load
    def create_payment_details(self, data):
        return PaymentDetails(**data)


class EndUserBase(object):
    """
    End User base details structure
    """
    def __init__(self, customer_reference: str=None, language: str=None, initials: str=None, gender: str=None,
                 last_name: str=None, dob: datetime=None,
                 phone_number: str=None, email_address: str=None, bank_account: str=None, iban: str=None, bic: str=None,
                 send_confirm_email: bool=None,
                 address: Address=None, invoice_address: Address=None, company: Company=None
                 ):
        self.customer_reference = customer_reference
        self.language = language
        self.initials = initials
        self.gender = gender  #optional, Enum
        self.last_name = last_name
        self.dob: datetime = dob
        self.phone_number = phone_number
        self.email_address = email_address
        self.bank_account = bank_account
        self.iban = iban
        self.bic = bic
        self.send_confirm_email = send_confirm_email
        self.company: Company = company
        self.address: Address = address
        self.invoice_address: Address = invoice_address

    def __repr__(self):
        return str(self.__dict__)


class EndUser(EndUserBase):
    """
    End User details structure
    """
    def __init__(self, payment_details: PaymentDetails=None, storno_details: StornoDetails=None,
                 stats_details: StatsDetails=None,
                 *args, **kwargs):
        """
        Create EndUser details

        .. seealso::
            :class:`paynlsdk.objects.EndUserBase` for the base structure

            :class:`paynlsdk.objects.PaymentDetails` for the *payment_details* structure

            :class:`paynlsdk.objects.StornoDetails` for the *storno_details* structure

            :class:`paynlsdk.objects.StatsDetails` for the *stats_details* structure

        :param payment_details: Payment details
        :type payment_details: PaymentDetails
        :param storno_details: Storno details
        :type storno_details: StornoDetails
        :param stats_details: Stats details
        :type stats_details: StatsDetails
        :param args: unused
        :type args: list
        :param kwargs: Any keyword arguments the :class:`paynlsdk.objects.EndUserBase` receives
        :type kwargs: dict
        """
        self.payment_details: PaymentDetails = payment_details
        self.storno_details: StornoDetails = storno_details
        self.stats_details: StatsDetails = stats_details
        super().__init__(**kwargs)

    def __repr__(self):
        return str(self.__dict__)


class EndUserSchema(Schema):
    customer_reference = fields.String()
    language = fields.String()
    initials = fields.String()
    gender = fields.String()
    last_name = fields.String(load_from='lastName')
    dob = fields.DateTime(format='%d-%m-%Y', required=False, allow_none=True)
    phone_number = fields.String(load_from='phoneNumber')
    email_address = fields.String(load_from='emailAddress')
    bank_account = fields.String(load_from='bankAccount')
    iban = fields.String()
    bic = fields.String()
    send_confirm_email = fields.Boolean(load_from='sendConfirmMail')
    address = fields.Nested(AddressSchema)
    invoice_address = fields.Nested(AddressSchema, load_from='invoiceAddress')
    payment_details = fields.Nested(PaymentDetailsSchema, load_from='paymentDetails')
    storno_details = fields.Nested(StornoDetailsSchema, load_from='stornoDetails')
    stats_details = fields.Nested(StatsDetailsSchema, load_from='statsDetails')
    company = fields.Nested(CompanySchema)

    @post_load
    def create_end_user(self, data):
        return EndUser(**data)

    @pre_load
    def pre_process(self, data):
        # In the exceptional case where the boolean is an empty string.
        if data['sendConfirmMail'].strip() == '':
            data['sendConfirmMail'] = False
        if ParamValidator.is_empty(data['dob']):
            data['dob'] = None
        return data


class TransactionEndUser(EndUserBase):
    """
    Transaction End User details structure
    """
    def __init__(self,
                 access_code: str=None, customer_trust: int=None,
                 *args, **kwargs):
        """
        Create TransactionEndUser details

        .. seealso::
            :class:`paynlsdk.objects.EndUserBase` for the base structure

        :param access_code: access code
        :type access_code: str
        :param customer_trust: customer trust bit
        :type customer_trust: int
        :param args: unused
        :type args: list
        :param kwargs: Any keyword arguments the :class:`paynlsdk.objects.EndUserBase` receives
        :type kwargs: dict
        """
        super().__init__(**kwargs)
        self.access_code = access_code
        self.customer_trust = customer_trust

    def __repr__(self):
        return str(self.__dict__)


class TransactionEndUserSchema(Schema):
    customer_reference = fields.String(required=False, allow_none=True)
    language = fields.String()
    initials = fields.String()
    gender = fields.String()
    last_name = fields.String(load_from='lastName')
    dob = fields.DateTime(format='%d-%m-%Y', required=False, allow_none=True)
    phone_number = fields.String(load_from='phoneNumber')
    email_address = fields.String(load_from='emailAddress')
    bank_account = fields.String(load_from='bankAccount')
    iban = fields.String(required=False)
    bic = fields.String(required=False)
    send_confirm_email = fields.Boolean(required=False, load_from='sendConfirmMail')
    address = fields.Nested(AddressSchema, required=False)
    invoice_address = fields.Nested(AddressSchema, required=False, load_from='invoiceAddress')
    company = fields.Nested(CompanySchema, required=False)
    access_code = fields.String(required=False, load_from='accessCode')
    customer_trust = fields.Integer(required=False, load_from='customerTrust')

    @post_load
    def create_end_user(self, data):
        return EndUser(**data)

    @pre_load
    def pre_process(self, data):
        # In the exceptional case where the boolean is an empty string.
        if data['sendConfirmMail'].strip() == '':
            data['sendConfirmMail'] = False
        return data


class TransactionStatusDetails(object):
    """
    Transaction status details structure
    """
    def __init__(self,
                 transaction_id: str=None,
                 order_id: str=None,
                 payment_profile_id: str=None,
                 state: int=None,
                 state_name: str=None,
                 currency: str=None,
                 amount: int=None,
                 currency_amount: int=None,
                 paid_amount: int=None,
                 paid_currency_amount: int=None,
                 refund_amount: int=None,
                 refund_currency_amount: int=None,
                 created: str=None,
                 identifier_name: str=None,
                 identifier_public: str=None,
                 identifier_hash: str=None,
                 start_ip_address: str=None,
                 completed_ip_address: str=None,
                 order_number: str=None,
                 ):
        self.transaction_id = transaction_id
        self.order_id = order_id
        self.payment_profile_id = payment_profile_id
        self.state = state
        self.state_name = state_name
        self.currency = currency
        self.amount = amount
        self.currency_amount = currency_amount
        self.paid_amount = paid_amount
        self.paid_currency_amount = paid_currency_amount
        self.refund_amount = refund_amount
        self.refund_currency_amount = refund_currency_amount
        self.created = created
        self.identifier_name = identifier_name
        self.identifier_public = identifier_public
        self.identifier_hash = identifier_hash
        self.start_ip_address = start_ip_address
        self.completed_ip_address = completed_ip_address
        self.order_number = order_number

    def __repr__(self):
        return str(self.__dict__)


class TransactionStatusDetailsSchema(Schema):
    transaction_id = fields.String(load_from='transactionId', required=True)
    order_id = fields.String(load_from='orderId', required=True)
    payment_profile_id = fields.String(load_from='paymentProfileId', required=True)
    state = fields.Integer(required=True)
    state_name = fields.String(load_from='stateName', required=True)
    currency = fields.String(required=True)
    amount = fields.Integer(required=True)
    currency_amount = fields.Integer(load_from='currenyAmount', required=True)
    paid_amount = fields.Integer(load_from='paidAmount', required=True)
    paid_currency_amount = fields.Integer(load_from='paidCurrenyAmount', required=True)
    refund_amount = fields.Integer(load_from='refundAmount', required=True)
    refund_currency_amount = fields.Integer(load_from='refundCurrenyAmount', required=True)
    created = fields.DateTime(format='%Y-%m-%d %H:%M:%S', required=True)
    identifier_name = fields.String(load_from='identifierName', required=True)
    identifier_public = fields.String(load_from='identifierPublic', required=True)
    identifier_hash = fields.String(load_from='identifierHash', required=True)
    start_ip_address = fields.String(load_from='startIpAddress', required=True)
    completed_ip_address = fields.String(load_from='completedIpAddress', required=True)
    order_number = fields.String(load_from='orderNumber', required=True)

    @post_load
    def create_transaction_status_details(self, data):
        return TransactionStatusDetails(**data)


class RefundSuccessInfo(object):
    """
    Refund success details structure
    """
    def __init__(self,
                 order_id: str=None,
                 amount: int=None,
                 amount_refunded: int=None,
                 voucher_number: str=None,
                 bankaccount_number: str=None,
                 refund_id: str=None,
                 ):
        """
        Create Refund success information structure

        :param order_id: Order ID
        :type order_id: str
        :param amount: amount
        :type amount: int
        :param amount_refunded: Refunded amount
        :type amount_refunded: int
        :param voucher_number: Voucher number
        :type voucher_number: str
        :param bankaccount_number: Bank account number
        :type bankaccount_number: str
        :param refund_id: Refund ID
        :type refund_id: str
        """
        self.order_id = order_id
        self.amount = amount
        self.amount_refunded = amount_refunded
        self.voucher_number = voucher_number
        self.bankaccount_number = bankaccount_number
        self.refund_id = refund_id

    def __repr__(self):
        return str(self.__dict__)


class RefundSuccessInfoSchema(Schema):
    order_id = fields.String(required=True, load_from='orderId')
    amount = fields.Integer(required=True)
    amount_refunded = fields.Integer(required=True, load_from='refundAmount')
    voucher_number = fields.String(load_from='voucherNumber', required=False, allow_none=True)
    bankaccount_number = fields.String(load_from='bankaccountNumber', required=False, allow_none=True)
    refund_id = fields.String(load_from='refundId', required=False, allow_none=True)

    @post_load
    def create_refund_success_info(self, data):
        return RefundSuccessInfo(**data)


class RefundFailInfo(object):
    """
    Refund fail details structure
    """
    def __init__(self,
                 order_id: str=None,
                 amount: int=None,
                 refund_amount: int=None,
                 voucher_number: str=None,
                 bankaccount_number: str=None,
                 reason: str=None,
                 ):
        """
        Create Refund failure information structure

        :param order_id: Order ID
        :type order_id: str
        :param amount: amount
        :type amount: int
        :param refund_amount: Refund amount
        :type refund_amount: int
        :param voucher_number: Voucher number
        :type voucher_number: str
        :param bankaccount_number: Bank account number
        :type bankaccount_number: str
        :param reason: Refund reason
        :type reason: str
        """
        self.order_id = order_id
        self.amount = amount
        self.refund_amount = refund_amount
        self.voucher_number = voucher_number
        self.bankaccount_number = bankaccount_number
        self.reason = reason

    def __repr__(self):
        return str(self.__dict__)


class RefundFailInfoSchema(Schema):
    order_id = fields.String(required=True, load_from='orderId')
    amount = fields.Integer(required=True)
    refund_amount = fields.Integer(required=True, load_from='refundAmount')
    voucher_number = fields.String(load_from='voucherNumber')
    bankaccount_number = fields.String(load_from='bankaccountNumber')
    reason = fields.String()

    @post_load
    def create_refund_fail_info(self, data):
        return RefundFailInfo(**data)


class BankDetails(object):
    """
    Bank details structure
    """
    def __init__(self,
                 id: int=None,
                 name: str=None,
                 issuer_id: str=None,
                 icon: str=None,
                 available: bool=False
                 ):
        """
        Create bank details instance

        :param id: Bank ID
        :type id: int
        :param name: Bank name
        :type name: str
        :param issuer_id: Issue ID
        :type issuer_id: str
        :param icon: Icon
        :type icon: str
        :param available: availability bit
        :type available: bool
        """
        self.id = id
        self.name = name
        self.issuer_id = issuer_id
        self.icon = icon
        self.available = available

    def __repr__(self):
        return self.__dict__.__str__()


class BankDetailsSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    issuer_id = fields.String(required=True, load_from='issuerId')
    icon = fields.Url(required=True)
    available = fields.Boolean(required=True)

    @post_load
    def create_response(self, data):
        return BankDetails(**data)


class PaymentOptionBase(object):
    """
    Payment option base details structure
    """
    def __init__(self, id: int=None, name: str=None, visible_name: str=None,
                 img: str=None, path: str=None, state: int=None):
        """
        Create Payment option details instance

        .. seealso::
            :class:`paynlsdk.enums.enums.ActiveState` for payment option :attr:`state` values

        :param id: ID
        :type id: int
        :param name: name
        :type name: str
        :param visible_name: visible name
        :type visible_name: str
        :param img: image name + ext
        :type img: str
        :param path: relative image path
        :type path: str
        :param state: option status (0: unavailable, 1: available)
        :type state: int
        """
        self.id = id
        self.name = name
        self.visible_name = visible_name
        self.img = img
        self.path = path
        self.state = state ## TODO: Enum Availability

    def __repr__(self):
        return str(self.__dict__)


class PaymentSubOption(PaymentOptionBase):
    """
    Payment suboption details structure
    """
    def __init__(self, *args, **kwargs):
        """
        Create Payment suboption details instance

        .. seealso::
            :func:`paynlsdk.objects.PaymentOptionBase.__init__` for the *kwargs* attribute values

        :param args: unused
        :type args: list
        :param kwargs: Any keyword arguments the :class:`paynlsdk.objects.PaymentOptionBase` receives
        :type kwargs: dict
        """
        super().__init__(**kwargs)

    def __repr__(self):
        return str(self.__dict__)


class PaymentSubOptionSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    visible_name = fields.String(required=True, load_from='visibleName')
    img = fields.String(required=True)
    path = fields.String(required=True)
    state = fields.Integer(required=True)

    @post_load
    def create_payment_sub_option(self, data):
        return PaymentSubOption(**data)


class PaymentOption(PaymentOptionBase):
    """
    Payment option details structure
    """
    def __init__(self, payment_method_id: int=None, use_only_in_store: bool=False,
                 payment_sub_options: Dict[int, PaymentSubOption]={}, *args, **kwargs):
        """
        Create Payment option details instance

        .. seealso::
            :func:`paynlsdk.objects.PaymentOptionBase.__init__` for the *kwargs* attribute values

            :class:`paynlsdk.objects.PaymentSubOption` for the *payment_options* type

        :param payment_method_id: payment method ID
        :type payment_method_id: int
        :param use_only_in_store: can we only use this payment method in a store?
        :type use_only_in_store: bool
        :param payment_sub_options: Payment sub options
        :type payment_sub_options: Dict[int, PaymentSubOption]
        :param args: unused
        :type args: list
        :param kwargs: Any keyword arguments the :class:`paynlsdk.objects.PaymentOptionBase` receives
        :type kwargs: dict
        """
        self.payment_method_id = payment_method_id
        self.use_only_in_store = use_only_in_store
        self.payment_sub_options: Dict[int, PaymentSubOption] = payment_sub_options
        super().__init__(**kwargs)

    def __repr__(self):
        return str(self.__dict__)


class PaymentOptionSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    visible_name = fields.String(required=True, load_from='visibleName')
    img = fields.String(required=True)
    path = fields.String(required=True)
    state = fields.Integer(required=True)
    use_only_in_store = fields.Boolean(required=False, allow_none=True, load_from='useOnlyInStore')
    payment_method_id = fields.Integer(allow_None=True, required=False, load_from='paymentMethodId')
    payment_sub_options = fields.List(fields.Nested(PaymentSubOptionSchema), required=False, allow_none=True,
                                      load_from='paymentOptionSubList')

    @pre_load
    def postprocess(self, data):
        #  This IS rather nasty. Perform some conversion due to fields.Dict NOT taking nesteds in 2.x.
        #  This should be fixed in 3.x but that's a pre-release
        if ParamValidator.is_empty(data['paymentOptionSubList']):
            del data['paymentOptionSubList']
        elif 'paymentOptionSubList' in data and ParamValidator.not_empty(data['paymentOptionSubList']):
            list = []
            for i, item in data['paymentOptionSubList'].items():
                list.append(item)
            data['paymentOptionSubList'] = list
        return data

    @post_load
    def create_payment_option(self, data):
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo pre_processing).
        #  This should be fixed in 3.x but that's a pre-release
        if 'payment_sub_options' in data:
            rs = {}
            for item in data['payment_sub_options']:
                rs[item.id] = item
            data['payment_sub_options'] = rs
        return PaymentOption(**data)


class CountryOption(object):
    """
    Country option details structure
    """
    def __init__(self, id: int=None, name: str=None, visible_name: str=None, in_eu: bool=False,
                 img: str=None, path: str=None, payment_option_list: Dict[int, PaymentOption]={}):
        """
        Create country option instance

        .. seealso::
            :class:`paynlsdk.objects.PaymentOption` for payment option details

        :param id: ID
        :type id: int
        :param name: name
        :type name: str
        :param visible_name: visible name
        :type visible_name: str
        :param in_eu: available in EU?
        :type in_eu: bool
        :param img: image name + ext
        :type img: str
        :param path: relative image path
        :type path: str
        :param payment_option_list: Payment options
        :type payment_option_list: Dict[int, PaymentOption]
        """
        self.id = id
        self.name = name
        self.visible_name = visible_name
        self.in_eu = in_eu
        self.img = img
        self.path = path
        self.payment_option_list: Dict[int, PaymentOption] = payment_option_list

    def __repr__(self):
        return str(self.__dict__)


class CountryOptionSchema(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    visible_name = fields.String(required=True, load_from='visibleName')
    in_eu = fields.Boolean(required=True)
    img = fields.String(required=True)
    path = fields.String(required=True)
    # UGH! Source is dictionary based nested?? Marshmallow/Python does not process this well!
    payment_option_list = fields.List(fields.Nested(PaymentOptionSchema), allow_none=True, load_from='paymentOptionList')

    @pre_load
    def pre_process(self, data):
        #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
        if ParamValidator.is_empty(data['paymentOptionList']):
            del data['paymentOptionList']
        elif 'paymentOptionList' in data and ParamValidator.not_empty(data['paymentOptionList']):
            list = []
            for i, item in data['paymentOptionList'].items():
                list.append(item)
            data['paymentOptionList'] = list
        return data

    @post_load
    def create_country_option(self, data):
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo pre_processing).
        #  This should be fixed in 3.x but that's a pre-release
        rs = {}
        for item in data['payment_option_list']:
            rs[item.id] = item
        data['payment_option_list'] = rs
        return CountryOption(**data)

