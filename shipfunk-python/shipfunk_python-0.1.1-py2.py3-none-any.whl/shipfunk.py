# -*- coding: utf-8 -*-

"""Main module."""
import requests
import logging
import json

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

logs = logging.getLogger(__name__)


class Shipfunk(object):
    """ Class for Shipfunk logistics API.

    Following packages need to be installed:
     - requests

    :param apikey: API key, string
    :param orderid: order id, string
    :param language: default language is FI, in two letter 'ISO 639-1'-format
    :param currency: default currency is EUR, with three letters
    :rtype: object
    """
    _default_language = 'FI'
    _default_currency = 'EUR'

    def __init__(self, apikey, orderid='', language=_default_language, currency=_default_currency):
        """ Initialize Shipfunk client. """
        self._apikey = apikey

        language = self.check_language(language)
        currency = self.check_currency(currency)

        self._language = language
        self._currency = currency
        self._endpoint = 'https://shipfunkservices.com/api/1.2/'
        self._products = []
        self._address = {}
        self._orderid = orderid

    @property
    def endpoint(self):
        """ Return endpoint.

        :return: endpoint, string
        """
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value):
        """ Method saves a new endpoint if value is defined.

        :param value: new endpoint url, string

        :return: None
        """
        if not value:
            logs.debug("Mandatory endpoint can not be empty.")
            raise ValueError("Mandatory endpoint can not be empty")
        self._endpoint = value

    @property
    def apikey(self):
        """ Return api key.

        :return: api key, string
        """
        return self._apikey

    @apikey.setter
    def apikey(self, value):
        """ Method saves a new API key if value is defined

        :param value: new API key, string

        :return: None
        """
        if not value:
            logs.debug("Mandatory API key can not be empty.")
            raise ValueError("Mandatory API key can not be empty")
        self._apikey = value

    @property
    def language(self):
        """ Method returns language code.

        :return: language, in two letter 'ISO 639-1'-format
        """
        return self._language

    @language.setter
    def language(self, value):
        """ Method saves a new language code if value is defined and it is in a correct format.

        :param value: new language code, in two letter 'ISO 639-1'-format

        :return: None
        """
        if not value:
            logs.debug("Mandatory language can not be empty.")
            raise ValueError("Mandatory language can not be empty")
        elif len(value) != 2:
            logs.debug("The length of the language code is not 2.")
            raise ValueError("The length of the language code is not 2")
        elif not value.isalpha():
            logs.debug("Only letters are allowed.")
            raise ValueError("Only letters are allowed")
        self._language = value.upper()

    @property
    def currency(self):
        """ Method returns currency code.

        :return: currency, with three letters
        """
        return self._currency

    @currency.setter
    def currency(self, value):
        """ Method saves a new currency code if value is defined and it is in a correct format.

        :param value: new currency code, with three letters

        :return: None
        """
        if not value:
            logs.debug("Mandatory currency can not be empty.")
            raise ValueError("Mandatory currency can not be empty")
        elif len(value) != 3:
            logs.debug("The length of the currency code is not 3.")
            raise ValueError("The length of the currency code is not 3")
        elif not value.isalpha():
            logs.debug("Only letters are allowed.")
            raise ValueError("Only letters are allowed")

        self._currency = value.upper()

    @property
    def orderid(self):
        """ Return order id.

        :return: order id, string
        """
        return self._orderid

    @orderid.setter
    def orderid(self, value):
        """ Method saves a new order id.

        :param value: order id, string

        :return: None
        """
        if not value:
            logs.debug("Mandatory order id can not be empty.")
            raise ValueError("Mandatory order id can not be empty")

        self._orderid = value

    @property
    def products(self):
        """ Method returns product objects.

        :return: product objects, list
        """
        return self._products

    def check_language(self, language):
        """ Method checks that language is a valid language code. If not then
        default language code is used.

        :param language: new language code, in two letter 'ISO 639-1'-format

        :return: language code, in two letter 'ISO 639-1'-format
        """
        if (not language) or (len(language) != 2) or (not language.isalpha()):
            logs.debug("Default language is used.")
            language = self._default_language

        return language.upper()

    def check_currency(self, currency):
        """ Method checks that currency is a valid currency code. If not then
        default currency code is used.

        :param currency: new currency code, with three letters

        :return: currency code, with three letters
        """
        if (not currency) or (len(currency) != 3) or (not currency.isalpha()):
            logs.debug("Default currency is used.")
            currency = self._default_currency

        return currency.upper()

    def add_product(self, productno, weight, amount=1, name='', weightunit='kg', dimensions=None, add_services=None):
        """ Method saves product data. If data is saved then that data is used when getting
        data from Shipfunk if parameters are not defined in method calls.

        :param productno: product number, string
        :param weight: the weight of the product, float
        :param amount: the amount of the product, default is 1, float
        :param name: the name of the product, default is product number, string
        :param weightunit: used weight unit, default is kg, string
        :param dimensions: dimensions, dictionary
               - used keys are: unit, width, depth and height
        :param add_services: used additional services, dictionary

               - used keys are:
                   * code
                   * packing_group
                   * quantity
                   * quantity_unit
                   * shipping_name
                   * tunnel_restriction_code
                   * un_code
                   * warning_label_numbers

        :return: added product, ShipfunkProduct
        """
        new_product = ShipfunkProduct(productno, weight, amount, weightunit, name, dimensions)

        if add_services:
            new_product.additional_services = add_services

        self._products.append(new_product)
        return new_product

    def add_address(self, **kwargs):
        """ Method saves customer's address data. If data is saved then that data is used when getting
        data from Shipfunk if parameters are not defined in method calls.

        :param first_name: first name, string, optional
        :param last_name: last name, string, optional
        :param street_address: street, string, optional
        :param postal_code: postal code, string, optional
        :param city: city, string, optional
        :param country: country code, string, optional
        :param postal_box: postal box, string, optional
        :param company: company, string, optional
        :param phone: phone, string, optional
        :param email: email, string, optional

        :return: None
        """
        logs.debug("Data for address: " + str(kwargs))

        for key in kwargs:
            self._address[key] = kwargs[key]

        logs.debug("Saved address " + str(self._address))

    def get_address_data(self, keyname):
        """ Method returns data from address dictionary if it is saved to object.

        :param keyname: the key name of the returned data, string
               - used keys are:
                   * first_name
                   * last_name
                   * street_address
                   * postal_code
                   * city
                   * country
                   * postal_box
                   * company
                   * phone
                   * email

        :return: one value from address dictionary, string
        """
        if keyname in self._address:
            return self._address[keyname]

        return None

    @staticmethod
    def get_urlvariables():
        """ Method returns url variables: /real_http_code/request_type/return_type/

        :return: variables for url, string
        """
        return '/true/json/json/'

    def get_product_data(self):
        """ Method returns list from saved products

        :return: product data dictionaries, list
        """
        product_lines = []

        saved_products = self.products
        logs.debug("tempproducts" + str(saved_products))

        for oneproduct in saved_products:
            logs.debug("tempproducts" + str(oneproduct.weight))
            product = oneproduct.get_data()
            product_lines.append(product)

        return product_lines

    def get_customer_address_data(self, address_keys, params=None):
        """ Method returns customer's address data. If params dictionary is defined then
        try first take data from it. If key is not in the params dictionary then try to get
        saved value from object.

        :param address_keys: which customer data fields are wanted to return, dictionary
        :param params: request params, dictionary, optional
               - used keys are:
                   * first_name
                   * last_name
                   * street_address
                   * postal_code
                   * city
                   * country
                   * postal_box
                   * company
                   * phone
                   * email

        :return: customer data, dictionary
        """
        customer_data = {}

        # Check if only one field is wanted to return
        if type(address_keys) == str:
            address_keys = [address_keys]

        # Take customer data if defined
        if params and 'customer' in params:
            params = params['customer']

        for key in address_keys:
            if params and key in params:
                value = params[key]
            else:
                value = self.get_address_data(key)

            if value:
                if key == 'country':
                    value = value.upper()

                customer_data[key] = value

        return customer_data

    @staticmethod
    def check_card_direction(direction):
        """ Method to check that card direction is valid value. Value can be 'send', 'return' or 'both'.

        :param direction: card direction, string

        :return: 1 if value is valid, boolean
        """
        valid_values = ('send', 'return', 'both')

        if direction in valid_values:
            return 1
        else:
            raise ValueError("Wrong card_direction")

    def get_price(self, params=None):
        """ Method returns the minimum and maximum prices of the delivery,
        but without the actual delivery options, only prices are returned.

        If params are not defined, uses saved products and customers data.

        :param params: send values for request, dictionary, optional

               - postal_code: customer's postal code (optional)
               - country: customer's country (optional)
               - products: (optional)
                   * weight: the weight of the product
                       - amount, unit (default is kg)
                   * dimensions: dimensions of the product (optional)
                       - unit, width, depth, height
                   * warehouse: the warehouse where this product resides (optional)
                   * additional_services: used additional services (optional)
                       - code, packing_group, quantity, quantity_unit, shipping_name,
                         tunnel_restriction_code, un_code, warning_label_numbers

        :return: min and max prices, dictionary
        """
        if params and 'products' in params:
            product_lines = params['products']
        else:
            product_lines = self.get_product_data()

        address_keys = ('country', 'postal_code')
        customer_data = self.get_customer_address_data(address_keys, params)

        if not product_lines:
            logs.debug("No product lines.")
            raise ValueError("No product lines found")

        data = {
            "query": {
                "order": {
                    "language": self.language,
                    "monetary": {
                        "currency": self.currency
                    },
                    "products": product_lines
                },
                "customer": customer_data
            }
        }

        content = {
            'sf_get_price': data
        }
        logs.debug(content)

        return self.send_request('get_price', content)

    def get_delivery_options(self, params=None):
        """ Method gets and returns the suitable delivery options for the given
        shopping basket and customer info.

        If params are not defined, uses saved data from object.

        :param params: send values for request, dictionary, optional

               - order: order information (optional)
                   * language: language for the texts in the delivery options (optional, default is FI)
                   * monetary: (optional)
                       - currency: prices in the order are in this currency, default is EUR
                       - value: total value of the order
                   * discounts: (optional)
                       - type: type of discounts, 0=percentage (default), 1=money
                       - all: discount amount for every delivery option
                       - home: discount amount for home deliveries only
                       - normal: discount amount for normal deliveries only
                       - express: discount amount for express deliveries only
                   * additions: (optional)
                       - delivery_prices, delivery_times, delivery_times_store_pickups, warehouse_leadtime
                   * get_pickups: (optional)
                       - store, store_only, transport_company
                   * tags: (optional)
                   * additional_services
                       - code, bank_account, bic, monetary_value, reference
                   * products
                   * parcels
               - customer: customer information (optional)
                   * first_name, last_name, street_address, postal_code, city, country,
                     postal_box, company, phone, email
               - value: total value of the order, float (optional, not needed of order key is defined)

        :return: delivery options, dictionary
        """
        if params and 'order' in params:
            order_data = params['order']
        else:
            order_data = {
                "language": self.language,
                "monetary": {
                    "currency": self.currency,
                },
                "products": self.get_product_data()
            }

            if params and 'value' in params:
                order_data["monetary"]["value"] = params["value"]

        address_keys = ('first_name', 'last_name', 'street_address', 'postal_code', 'city', 'country', 'postal_box',
                        'company', 'phone', 'email')
        customer_data = self.get_customer_address_data(address_keys, params)

        data = {
            "query": {
                "order": order_data,
                "customer": customer_data,
            }
        }
        logs.debug(data)

        content = {
            'sf_get_delivery_options': data
        }
        logs.debug(content)

        return self.send_request('get_delivery_options', content)

    def get_pickups(self, params):
        """ Method gets and returns the pickup points for the chosen delivery company and it’s delivery option.
        Shipfunk's API will return 20 nearest pickup points by default, or as much as the transport company
        can give through their apis.

        If all needed params are not defined, uses saved data from object.

        :param params: send values for request, dictionary

               - carriercode: Shipfunk's id for the transport company and its delivery option
               - postal_code: customers postal code (optional)
               - country: customers country (optional)
               - return_count: the amount of the pickup points that Shipfunk returns if possible (default is 20)

        :return: pick up points, dictionary
        """
        if params and 'return_count' in params:
            return_count = params['return_count']
        else:
            return_count = 20

        address_keys = ('postal_code', 'country')
        customer_data = self.get_customer_address_data(address_keys, params)

        data = {
            "query": {
                "order": {
                    "carriercode": params['carriercode'],
                    "language": self.language,
                    "return_count": return_count
                },
                "customer": {
                    "postal_code": customer_data['postal_code'],
                    "country": customer_data['country']
                },
            }
        }
        logs.debug(data)

        content = {
            'sf_get_pickups': data
        }
        logs.debug(content)

        return self.send_request('get_pickups', content)

    def send_selected_delivery(self, params):
        """ Method sends the selected delivery method to Shipfunk.
        They need this information in order to create the correct package cards.

        :param params: send values for request, dictionary

               - selected_option
                   * orderid: order id
                   * carriercode: Shipfunk's id for the transport company and it's delivery option
                   * calculated_price: Shipfunk system's calculated price of the delivery
                   * customer_price: the discounted price of the delivery
                   * pickupid: tranport company's pickup points id (optional if no pickups)
                   * return_prices: this will tell the service to return the calculated_price and
                     the customers price as an answer. (optional)

        :return: prices for customer and for shop, if return_prices is 1;
                 otherwise OK message, dictionary
        """
        data = {
            "query": {
                "order": {
                    "selected_option": params['selected_option'],
                }
            }
        }
        logs.debug(data)

        content = {
            'sf_selected_delivery': data
        }
        logs.debug(content)

        return self.send_request('selected_delivery', content)

    def set_order_status(self, params):
        """ Method sets the orders status. Status can be 'placed' or 'cancelled'.
        The order status should be set 'placed' always when the customer finished the order.

        :param params: send values for request, dictionary

               - status: status of the order. Value can be 'placed' or 'cancelled'.
               - final_orderid: if you has used temporary order id before the order has been paid,
                 you need to give the real order id

        :return: code 1 and message 'OK', dictionary
        """
        valid_values = ('placed', 'cancelled')

        if not params['status'] in valid_values:
            logs.debug("Wrong status: " + params['status'])
            raise ValueError("Wrong status")

        data = {
            "query": {
                "order": {
                    "status": params['status'],
                    "final_orderid": params['final_orderid'],
                }
            }
        }
        logs.debug(data)

        content = {
            'sf_set_order_status': data
        }
        logs.debug(content)

        return self.send_request('set_order_status', content)

    def set_customer_details(self, params):
        """ Method sets and updates the customer details on a order. The customer details can be changed before creating
        the package card. When updating customer information only updated fields can be sent. If the field is empty or
        the field doesn't exists at all in the request, field is not updated on Shipfunk's system.

        Only fields company and PL can be emptied by giving 0 as a value, all other fields are mandatory. If other
        fields are give a zero or an empty string, those fields will not be updated.

        :param params: send values for request, dictionary

               - return_cards: return the updated package cards or not
               - customer: customer information
                   * first_name
                   * last_name
                   * street_address
                   * postal_code
                   * city
                   * country
                   * postal_box
                   * company
                   * phone
                   * email

        :return: card info if return_cards is 1; otherwise ok message, dictionary
        """
        data = {
            "query": {
                "order": {
                    "return_cards": params['return_cards'],
                },
                "customer": params['customer']
            }
        }
        logs.debug(data)

        content = {
            'sf_set_customer_details': data
        }
        logs.debug(content)

        return self.send_request('set_customer_details', content)

    def create_new_package_cards(self, params):
        """ Method creates the package cards and tracking codes for the order previously given in the methods
        get_delivery_options and send_selected_delivery.

        :param params: send values for request, dictionary

               - order: order information
                   * return_cards: if value is 1 then return the tracking codes and package cards in the return message,
                     (optional, default is 0)
                   * sendmail: if value is 1: Shipfunk will send an notification email to the customer
                    (optional, default is 0)
                   * send_edi: if value is 1, the service will send the EDI-message (optional, default is 1)
                   * package_card: (optional)
                       - direction: direction of the card. Value can be 'send', 'return' or 'both'
                         (optional, default is 'both')
                       - format: format of the card. Example: "zpl", "pdf" or "html" (optional, default is 'pdf')
                       - dpi: Dpi of the package card, only for zpl format
                       - size: size of the package card (optional, defaults is 'A5' for pdf and html and '4x6' for zpl)
                       - reversed: turn the package card upside down for printing, only for zpl-format
                         (optional, default is 0)
                   * additional_services: additional services for the order (optional)
                   * parcels: you may give all the parcel information in this element or you can give only the product
                     codes for each parcel.
                       - for example: product_codes, tracking_codes, warehouse
               - customer: customer information (optional)
                   * first_name, last_name, street_address, postal_code, city, country,
                     postal_box, company, phone, email

        :return: parcels info if return_cards is 1; otherwise ok message, dictionary
        """
        address_keys = ('first_name', 'last_name', 'street_address', 'postal_code', 'city', 'country', 'postal_box',
                        'company', 'phone', 'email')
        customer_data = self.get_customer_address_data(address_keys, params)

        data = {
            "query": {
                "order": params['order'],
                "customer": customer_data
            }
        }
        logs.debug(data)

        content = {
            'sf_create_new_package_cards': data
        }
        logs.debug(content)

        return self.send_request('create_new_package_cards', content)

    def create_new_tracking_codes(self, params):
        """ Method creates new tracking codes for the parcels. Then you can assign created tracking codes to the
        parcels with method create_new_package_cards. Shipfunk creates tracking codes also automatically so this
        method is not necessary to use. It is not recommended to create tracking codes unless you really need them.

        :param params: send values for request, dictionary

               - code_amount: amount of the tracking codes (optional, default is 1),
               - carriercode: Shipfunk's id for the transport company and it's delivery option (optional)

        :return: tracking codes, dictionary
        """
        carriercode = ''
        code_amount = 1

        if params:
            if 'code_amount' in params:
                code_amount = params['code_amount']
            if 'carriercode' in params:
                carriercode = params['carriercode']

        data = {
            "query": {
                "order": {
                    "code_amount": code_amount
                }
            }
        }

        if carriercode:
            data["query"]["order"]["carriercode"] = carriercode

        logs.debug(data)

        content = {
            'sf_create_new_tracking_codes': data
        }
        logs.debug(content)

        return self.send_request('create_new_tracking_codes', content)

    def get_package_cards(self, params):
        """ Method gets the created package cards from Shipfunk. This service doesn’t create any cards,
        but only returns already created cards. You can fetch the package cards using only the order id. Then all
        the package cards for the order will be returned. If you give the tracking code as a parameter, then
        only the cards of the defined tracking code will be returned.

        :param params: send values for request, dictionary

               - card_direction: direction of the card. Value can be 'send', 'return' or 'both'.
               - sendmail: value is 1: Shipfunk will send an notification email to the customer (optional, default is 0)
               - tracking_code: tracking code associated with the parcel (optional)

        :return: package cards, dictionary
        """
        self.check_card_direction(params['card_direction'])

        data = {
            "query": {
                "order": {
                    "package_card": {
                        "card_direction": params['card_direction']
                    }
                }
            }
        }

        if 'sendmail' in params:
            data["query"]["order"]["sendmail"] = params['sendmail']
        if 'tracking_code' in params:
            data["query"]["order"]["tracking_code"] = params['tracking_code']
        logs.debug(data)

        content = {
            'sf_get_package_cards': data
        }
        logs.debug(content)

        return self.send_request('get_package_cards', content)

    def get_tracking_codes(self, params):
        """ Method gets all created tracking codes of the order. The method doesn’t create any tracking codes,
         only returns the tracking codes that are already created.

        :param params: send values for request, dictionary

               - direction: direction of the card. Value can be 'send', 'return' or 'both'

        :return: package cards, dictionary
        """
        self.check_card_direction(params['card_direction'])

        data = {
            "query": {
                "order": {
                    "package_card": {
                        "card_direction": params['card_direction']
                    }
                }
            }
        }
        logs.debug(data)

        content = {
            'sf_get_tracking_codes': data
        }
        logs.debug(content)

        return self.send_request('get_tracking_codes', content)

    def get_tracking_events(self, params):
        """ Method gets the tracking events for the given tracking code and transport company.

        :param params: send values for request, dictionary

               - tracking_code: tracking code of the parcel
               - transport_company: name of the transport company (optional)
               - carriercode: carriercode of the transport company's delivery option (option)

        :return: tracking events, dictionary
        """
        data = {
            "query": {
                "order": {
                    "tracking_code": params['tracking_code'],
                    "language": self.language,
                }
            }
        }

        carrier = {}
        if 'transport_company' in params:
            carrier["transport_company"] = params['transport_company']
        if 'carriercode' in params:
            carrier["carriercode"] = params['carriercode']

        if carrier:
            data["query"]["carrier"] = carrier
        logs.debug(data)

        content = {
            'sf_get_tracking_events': data
        }
        logs.debug(content)

        return self.send_request('get_tracking_events', content)

    def get_parcels(self):
        """ Method gets all parcels which have been created in Shipfunk the given order.

        :return: parcels data, dictionary
        """
        return self.send_request('get_parcels', {})

    def edit_parcels(self, params):
        """ Method edits the parcels details.

        If you want to empty a field, set value to be "NULL" if the field is a string field,
        and -1 if the field is a float or integer field.

        :param params: send values for request, dictionary

               - return_parcels: if value is 1 then all parcels for the order are returned (optional, defauls is 0)
               - parcels: parcel data
                   * id: identifying code of the parcel. Shipfunk generated the id and it can not be edited
                   * code: identifying code of the parcel. This is the code generated by you.
                     If you use this, it must be unique for the order (optional)
                   * contents: contents of the parcel (optional)
                   * weight: the weight of the product
                       - unit, amount
                   * dimensions: dimensions of the product (optional)
                       - unit, width, depth, height
                   * monetary_value: monetary value of the parcel (optional)
                   * warehouse: the warehouse where this product resides (optional)
                   * fragile: "Fragile/Handle with care" -additional service, 1 = true, 0 = false (optional)

        :return: parcels info if return_parcels is 1; otherwise ok message, dictionary
        """
        data = {
            "query": {
                "order": {
                    "parcels": params['parcels']
                }
            }
        }

        if 'return_parcels' in params:
            data["query"]["order"]["return_parcels"] = params['return_parcels']

        content = {
            'sf_edit_parcels': data
        }
        logs.debug(content)

        return self.send_request('edit_parcels', content)

    def delete_parcels(self, params):
        """ Method removes the defined parcels from the order. Removing a parcel also removes the package card and
        the tracking code.

        You can remove parcels by giving the parcel codes or the tracking codes of the parcels.

        :param params: send values for request, dictionary

               - return_parcels: if value is 1 then all parcels for the order are returned (optional, defauls is 0)
               - remove_all_parcels: if value is 1 then all parcels are deleted (optional, default is 0)
               - parcels: parcel data
                   * id: identifying code of the parcel. Shipfunk generated the id and it can not be edited (optional)
                   * parcel_code: identifying code of the parcel generated by you (optional)
                   * tracking_code: tracking code for the parcel (optional)

        :return: parcels info if return_parcels is 1; otherwise ok message, dictionary
        """
        data = {
            "query": {
                "order": {
                }
            }
        }

        if 'parcels' in params:
            data["query"]["order"]["parcels"] = params['parcels']

        if 'return_parcels' in params:
            data["query"]["order"]["return_parcels"] = params['return_parcels']

        if 'remove_all_parcels' in params:
            data["query"]["order"]["remove_all_parcels"] = params['remove_all_parcels']

        content = {
            'sf_delete_parcels': data
        }
        logs.debug(content)

        return self.send_request('delete_parcels', content)

    def test_orderid(self):
        """ Method tests if the orderid is already in use by another of your orders in Shipfunk.

        :return: code and message, is order id already in use, dictionary
        """
        return self.send_request('test_order_id', {}, '/true/rest/json/')

    def send_request(self, apiname, content, call_params='', add_orderid=1):
        """ Method sends request to rest server and returns response.

        :param apiname: name of the Shipfunk's API, string
        :param content: content which is sent to Shipfunk, dictionary
        :param call_params: params for url if default type is not used, string (optional)
        :param add_orderid: if 1 then order id is added to url, boolean (optional, default is 1)

        :return: response from rest server, dictionary
        """
        if not call_params:
            call_params = self.get_urlvariables()

        url = self.endpoint + apiname + call_params

        if add_orderid:
            url += self.orderid

        logs.debug(url)

        headers = {
            'Authorization': self.apikey,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        logs.debug(content)

        # code %27 (character ') doesn't work but code %22 (character ") works so use json to get it
        content = urlencode({d: json.dumps(content[d]) for d in content})
        logs.debug(content)

        response = requests.post(url, headers=headers, data=content)
        response = response.json()
        logs.debug('Response ' + str(response))

        if 'response' in response:
            return response['response']
        else:
            raise ValueError(str(response))


class ShipfunkUser(Shipfunk):
    """ Class for Shipfunk logistics API for handling user accounts.

    :param apikey: API key, string
    :rtype: object
    """

    def __init__(self, apikey):
        """ Initialize ShipfunkUser client. """
        super(ShipfunkUser, self).__init__(apikey)

    @staticmethod
    def get_urlvariables():
        """ Method returns url variables: /real_http_code/request_type/return_type

        :return: variables for url, string
        """
        return '/true/json/json'

    def create_user(self, params):
        """ Method creates new user accounts into Shipfunk under your own account.

        :param params: send values for request, dictionary

               - user: user information
                   * email: email of the new user account
                   * locale: locale of the new user account in two letter ISO 639-1-format (optional, default is fi)
                   * eshop_name: name of the shop
                   * business_id: business id of the shop
                   * customs_id: customs id of the shop (optional)
                   * contact_person_name: contact persons name. This is needed by the transport companies
                   * contact_person_phone: contact persons phone number. This is needed by the transport companies
                   * contact_person_email: contact persons email. This is needed by the transport companies
                   * web_address: web address of the shop (optional)
                   * customer_contact_info: the customer contact info of the shop. This will be added to the emails
                     which Shipfunk sends to customers concerning the delivery. This can contain html-marking (optional)

        :return: user account data, dictionary
        """
        data = {
            "query": {
                "user": params['user']
            }
        }

        content = {
            'sf_create_user': data
        }
        logs.debug(content)

        call_params = self.get_urlvariables()

        return self.send_request('create_user', content, call_params, 0)

    def get_user(self, params):
        """ Method gets the user that is attached to defined account.

        :param params: send values for request, dictionary
               - email: email of the user account

        :return: user account data, dictionary
        """
        data = {
            "query": {
                "user": {
                    "email": params['email']
                }
            }
        }

        content = {
            'sf_get_user': data
        }
        logs.debug(content)

        call_params = self.get_urlvariables()

        return self.send_request('get_user', content, call_params, 0)

    def edit_user(self, params):
        """ Method modifies the existing user.

        :param params: send values for request, dictionary

               - user: user information
                   * email: email of the new user account
                   * locale: locale of the new user account in two letter ISO 639-1-format (optional, default is fi)
                   * eshop_name: name of the shop
                   * business_id: business id of the shop
                   * customs_id: customs id of the shop (optional)
                   * contact_person_name: contact persons name. This is needed by the transport companies
                   * contact_person_phone: contact persons phone number. This is needed by the transport companies
                   * contact_person_email: contact persons email. This is needed by the transport companies
                   * web_address: web address of the shop (optional)
                   * customer_contact_info: the customer contact info of the shop. This will be added to the emails
                     which Shipfunk sends to customers concerning the delivery. This can contain html-marking (optional)

        :return: user account data, dictionary
        """
        data = {
            "query": {
                "user": params['user']
            }
        }

        content = {
            'sf_edit_user': data
        }
        logs.debug(content)

        call_params = self.get_urlvariables()

        return self.send_request('edit_user', content, call_params, 0)

    def detach_user(self, params):
        """ Method detaches the user from your account.

        :param params: send values for request, dictionary
               - email: email of the user account

        :return: code and message, dictionary
        """
        data = {
            "query": {
                "user": {
                    "email": params['email']
                }
            }
        }

        content = {
            'sf_delete_user': data
        }
        logs.debug(content)

        call_params = self.get_urlvariables()

        return self.send_request('delete_user', content, call_params, 0)

    def create_invitation(self, params):
        """ Method sends an invitation to the user to attach itself under your account.
        This method can be used if you tried to create a new user when the user already existed.

        :param params: send values for request, dictionary

               - email: email of the user account

        :return: code and message, dictionary
        """
        data = {
            "query": {
                "user": {
                    "email": params['email']
                }
            }
        }

        content = {
            'sf_create_invitation': data
        }
        logs.debug(content)

        call_params = self.get_urlvariables()

        return self.send_request('create_invitation', content, call_params, 0)


class ShipfunkProduct(object):
    """ Class for Shipfunk product

    :param productno: product number, string
    :param weight: weight, float
    :param amount: amount, default is 1, float
    :param weightunit: weight unit, default is kg, string
    :param name: name of the product, string
    :param dimensions: dimensions of the product, dictionary
           - used keys are: unit, width, depth and height
    :rtype: object
    """

    def __init__(self, productno, weight, amount=1, weightunit='kg', name='', dimensions=None):
        self.check_value(weight)
        self.check_value(amount)

        self._productno = productno
        self._weight = weight
        self.weightunit = weightunit
        self._amount = amount
        self._warehouse = None
        self._dimensions = {}
        self._additional_services = []

        if not name:
            name = productno
        self.name = name

        if dimensions:
            self.check_dimensions(dimensions)
            self.dimensions = dimensions.copy()

    @property
    def productno(self):
        """ Method returns product number.

        :return: productno, string
        """
        return self._productno

    @productno.setter
    def productno(self, value):
        """ Method saves the product number of the product.

        :param value: the weight of the product, float

        :return: None
        """
        if not value:
            logs.debug("Mandatory product number can not be empty.")
            raise ValueError("Mandatory product number can not be empty")

        self._productno = value

    @property
    def weight(self):
        """ Method returns weight.

        :return: weight, float
        """
        return self._weight

    @weight.setter
    def weight(self, value):
        """ Method saves the weight of the product.

        :param value: the weight of the product, float

        :return: None
        """
        self.check_value(value)

        self._weight = value

    @property
    def amount(self):
        """ Method returns amount.

        :return: amount, float
        """
        return self._amount

    @amount.setter
    def amount(self, value):
        """ Method saves the amount of the product.

        :param value: the amount of the product, float

        :return: None
        """
        self.check_value(value)

        self._amount = value

    @property
    def dimensions(self):
        """ Method returns dimensions.

        :return: dimensions, dictionary

                 - used keys are: unit, width, depth and height
        """
        return self._dimensions

    @dimensions.setter
    def dimensions(self, values):
        """ Method saves the amount of the product.

        :param values: dimensions of the product, dictionary

               - used keys are: unit, width, depth and height

        :return: None
        """
        self.check_dimensions(values)

        self._dimensions = values.copy()

    @property
    def additional_services(self):
        """ Method returns additional services.

        :return: additional services, dictionary
        """
        return self._additional_services

    @additional_services.setter
    def additional_services(self, services):
        """ Method saves additional services for the product.

        :param services: additional services, dictionary
               - used keys are:
                   * code
                   * packing_group
                   * quantity
                   * quantity_unit
                   * shipping_name
                   * tunnel_restriction_code
                   * un_code
                   * warning_label_numbers

        :return: None
        """
        if type(services) != list:
            logs.debug("Value of the services has to be a list.")
            raise TypeError("Value has to be a list")

        self._additional_services = []

        for one_service in services:
            self.add_additional_service(one_service)

    @property
    def warehouse(self):
        """ Method returns warehouse.

        :return: warehouse, string
        """
        return self._warehouse

    @warehouse.setter
    def warehouse(self, value):
        """ Method saves the warehouse of the product.

        :param value: the warehouse of the product, string

        :return: None
        """

        self._warehouse = value

    @staticmethod
    def check_value(value):
        """ Method checks that the value is valid. The value has to be bigger than 0 and a number

        :param value: value, type can be any

        :return: None
        """
        if type(value) != int and type(value) != float:
            logs.debug("Value has to be number.")
            raise TypeError("Value has to be number")
        elif value <= 0:
            logs.debug("Value has to be bigger than 0.")
            raise ValueError("Value has to be bigger than 0")

    def check_dimensions(self, dimensions):
        """ Method checks that dimension values are valid. The value has to be bigger than 0 and a number

        :param dimensions: dimensions, dictionary

               - used keys are: unit, width, depth and height

        :return: None
        """
        valid_keys = ('unit', 'width', 'depth', 'height')
        for keys in dimensions:
            if keys in valid_keys:
                if keys != 'unit':
                    self.check_value(float(dimensions[keys]))
            else:
                logs.debug("Invalid key: " + keys)
                raise ValueError("Invalid key")

    def get_data(self):
        """ Method returns saved data in dictionary.

        :return: saved product data, dictionary
        """
        product_data = {
            "amount": self.amount,
            "code": self.productno,
            "name": self.name,
            "weight": {
                "amount": self.weight,
                "unit": self.weightunit
            },
        }

        if self.dimensions:
            product_data["dimensions"] = self.dimensions

        if self.warehouse:
            product_data["warehouse"] = self.warehouse

        if self.additional_services:
            product_data["additional_services"] = self.additional_services

        logs.debug("Product data: " + str(product_data))

        return product_data

    def add_additional_service(self, values):
        """ Method saves a additional service to object.

        :param values: data of the additional service, dictionary
               - used keys are:
                   * code
                   * packing_group
                   * quantity
                   * quantity_unit
                   * shipping_name
                   * tunnel_restriction_code
                   * un_code
                   * warning_label_numbers

        :return: None
        """
        self._additional_services.append(values)
