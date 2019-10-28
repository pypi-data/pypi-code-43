#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `shipfunk_python` package."""


import unittest
import logging
import os
from shipfunk_python.shipfunk import Shipfunk

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client

# logging
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class TestShipfunk_python(unittest.TestCase):
    """Tests for `shipfunk_python` package."""

    @classmethod
    def setUpClass(cls):
        """ Set up our Shipfunk client for tests. It requires the following environment variables: test_apikey """
        cls._shipfunkClient = Shipfunk('test_apikey', '1234')

    def test_000_create_object_with_defaults(self):
        """ Test creating a new object with default values """
        self.assertTrue(self._shipfunkClient.language == 'FI' and self._shipfunkClient.currency == "EUR")

    def test_001_create_object_wrong_language(self):
        """ Test creating a new object with wrong language, so default language should be used """
        language = 'FI'
        shipfunk_client = Shipfunk('test_apikey', '1234', 'suomi')
        self.assertEqual(shipfunk_client.language, language)

        shipfunk_client = Shipfunk('test_apikey', '1234', 'f4')
        self.assertEqual(shipfunk_client.language, language)

    def test_002_create_object_language_lower(self):
        """ Test creating a new object with language in lower case """
        shipfunk_client = Shipfunk('test_apikey', '1234', 'en')
        self.assertEqual(shipfunk_client.language, 'EN')

    def test_003_create_object_wrong_currency(self):
        """ Test creating a new object with wrong currency, so default currency should be used """
        currency = 'EUR'
        shipfunk_client = Shipfunk('test_apikey', '1234', 'fi', 'eurot')
        self.assertEqual(shipfunk_client.currency, currency)

        shipfunk_client = Shipfunk('test_apikey', '1234', 'fi', 'er5')
        self.assertEqual(shipfunk_client.currency, currency)

    def test_004_create_object_currency_lower(self):
        """ Test creating a new object with currency in lower case """
        shipfunk_client = Shipfunk('test_apikey', '1234', 'fi', 'eur')
        self.assertEqual(shipfunk_client.currency, 'EUR')

    def test_005_endpoint(self):
        """ Test that endpoint is returned and updated """
        self.assertIsNotNone(self._shipfunkClient.endpoint)

        newendpoint = 'uusi'
        self._shipfunkClient.endpoint = newendpoint
        self.assertEqual(self._shipfunkClient.endpoint, newendpoint)

        newendpoint = 'https://shipfunkservices.com/api/1.2/'
        self._shipfunkClient.endpoint = newendpoint
        self.assertEqual(self._shipfunkClient.endpoint, newendpoint)

        with self.assertRaises(ValueError):
            self._shipfunkClient.endpoint = ''

    def test_006_get_apikey(self):
        """ Test that api key is returned and upated """
        self.assertIsNotNone(self._shipfunkClient.apikey)

        neweapikey = "uusi"
        self._shipfunkClient.apikey = neweapikey
        self.assertEqual(self._shipfunkClient.apikey, neweapikey)

        with self.assertRaises(ValueError):
            self._shipfunkClient.apikey = ''

    def test_007_update_language(self):
        """ Test that language is updated """
        newvalue = "EN"
        self._shipfunkClient.language = newvalue
        self.assertEqual(self._shipfunkClient.language, newvalue)

        with self.assertRaises(ValueError):
            self._shipfunkClient.language = "English"

        with self.assertRaises(ValueError):
            self._shipfunkClient.language = ""

        with self.assertRaises(ValueError):
            self._shipfunkClient.language = "f3"

        newvalue = "fi"
        self._shipfunkClient.language = newvalue
        self.assertEqual(self._shipfunkClient.language, newvalue.upper())

    def test_008_update_currency(self):
        """ Test that currency is updated """
        newvalue = "SEK"
        self._shipfunkClient.currency = newvalue
        self.assertEqual(self._shipfunkClient.currency, newvalue)

        with self.assertRaises(ValueError):
            self._shipfunkClient.currency = "Euro"

        with self.assertRaises(ValueError):
            self._shipfunkClient.currency = ""

        with self.assertRaises(ValueError):
            self._shipfunkClient.currency = "kr3"

        newvalue = "eur"
        self._shipfunkClient.currency = newvalue
        self.assertEqual(self._shipfunkClient.currency, newvalue.upper())

    def test_009_get_prices(self):
        """ Test get_price that min and max prices are returned """
        self._shipfunkClient.apikey = os.environ.get('APIKEY')

        params = {
            'postal_code': 30100,
            'country': 'fi',
            'products': [{
                "amount": 1,
                "code": "lt_0401107001[1]",
                "name": "lt_0401107001[1]",
                "weight": {
                    "amount": 1,
                    "unit": "kg"
                },
                "dimensions": {
                    "unit": "cm",
                    "width": "25",
                    "depth": "15",
                    "height": "3"
                },
                "additional_services": [{
                    "code": "10028",
                    "packing_group": "",
                    "quantity": 0.04,
                    "quantity_unit": "kg",
                    "shipping_name": "",
                    "tunnel_restriction_code": "",
                    "un_code": "",
                    "warning_label_numbers": ""
                }]
            }]
        }
        prices = self._shipfunkClient.get_price(params)
        self.assertIsNotNone(prices['min_price'] and prices['max_price'])

        with self.assertRaises(ValueError):
            self._shipfunkClient.get_price()

    def test_010_add_product(self):
        """ Test add product to object """
        alias = 'Product1'
        weight = 2.3
        product = self._shipfunkClient.add_product(alias, weight)
        self.assertIsNotNone(product)
        self.assertEqual(product.productno, alias)
        self.assertEqual(product.weight, weight)

        alias = 'Product2'
        weight = 2
        product = self._shipfunkClient.add_product(alias, weight)
        self.assertIsNotNone(product)
        self.assertEqual(product.productno, alias)
        self.assertEqual(product.weight, weight)
        self.assertEqual(product.amount, 1)

    def test_011_add_product_weight(self):
        """ Test add product to object if weight is less or equal than 0 or is string """
        with self.assertRaises(ValueError):
            self._shipfunkClient.add_product('Product3', -6)
        with self.assertRaises(ValueError):
            self._shipfunkClient.add_product('Product3', 0)
        with self.assertRaises(TypeError):
            self._shipfunkClient.add_product('Product3', '2 kg')

    def test_012_add_product_amount(self):
        """ Test add product to object if amount is less or equal than 0 or is string """
        with self.assertRaises(ValueError):
            self._shipfunkClient.add_product('Product3', 1, -3)
        with self.assertRaises(ValueError):
            self._shipfunkClient.add_product('Product3', 1, 0)
        with self.assertRaises(TypeError):
            self._shipfunkClient.add_product('Product3', 1, '2pcs')

    def test_013_add_product(self):
        """ Test to add product with all data """
        alias = 'Product3'
        weight = 1000
        amount = 2
        name = 'Test product'
        weight_unit = 'g'
        dimensions = {
            "unit": "cm",
            "width": "30",
            "depth": "5",
            "height": "5"
        }
        product = self._shipfunkClient.add_product(alias, weight, amount, name, weight_unit, dimensions)
        self.assertIsNotNone(product)
        self.assertEqual(product.productno, alias)
        self.assertEqual(product.weight, weight)
        self.assertEqual(product.amount, amount)
        self.assertEqual(product.name, name)
        self.assertEqual(product.weightunit, weight_unit)
        self.assertEqual(len(product.additional_services), 0)

        service = {
            "code": "10028",
            "packing_group": "",
            "quantity": 0.04,
            "quantity_unit": "kg",
            "shipping_name": "",
            "tunnel_restriction_code": "",
            "un_code": "",
            "warning_label_numbers": ""
        }
        product.add_additional_service(service)
        self.assertEqual(len(product.additional_services), 1)

        service = {
            "code": "22334",
            "packing_group": "Test",
            "quantity": 4,
            "quantity_unit": "g",
            "shipping_name": "Product 1",
            "tunnel_restriction_code": "1234",
            "un_code": "5678",
            "warning_label_numbers": "4"
        }
        product.add_additional_service(service)
        self.assertEqual(len(product.additional_services), 2)

        with self.assertRaises(TypeError):
            product.additional_services = service

        services = [
            {
                "code": "44",
                "packing_group": "Test",
                "quantity": 4,
                "quantity_unit": "g",
                "shipping_name": "Product 2",
                "tunnel_restriction_code": "123456",
                "un_code": "567856",
                "warning_label_numbers": "2"
            },
            {
                "code": "66",
                "packing_group": "Test",
                "quantity": 4,
                "quantity_unit": "g",
                "shipping_name": "Product 6",
                "tunnel_restriction_code": "66",
                "un_code": "666",
                "warning_label_numbers": "6"
            }
        ]
        product.additional_services = services
        self.assertEqual(len(product.additional_services), 2)

        data = product.get_data()
        self.assertIsNotNone(data["additional_services"])

        new_product = self._shipfunkClient.add_product(alias, weight, amount, name, weight_unit, dimensions, services)
        self.assertEqual(len(new_product.additional_services), 2)

        data = new_product.get_data()
        self.assertIsNotNone(data["additional_services"])

    def test_014_add_product_dimensions(self):
        """ Test to add product with wrong dimensions """
        alias = 'Product4'
        weight = 1
        dimensions = {
            "unit": "cm",
            "width": "-25",
            "depth": "-15",
            "height": "-3"
        }
        with self.assertRaises(ValueError):
            self._shipfunkClient.add_product(alias, weight, dimensions=dimensions)

        dimensions = {
            "unit": "cm",
            "width": "25",
            "depth": "0",
            "height": "-3"
        }
        with self.assertRaises(ValueError):
            self._shipfunkClient.add_product(alias, weight, dimensions=dimensions)

        dimensions = {
            "unit": "cm",
            "width": "25",
            "depth": "23.8",
            "height": "4cm"
        }
        with self.assertRaises(ValueError):
            self._shipfunkClient.add_product(alias, weight, dimensions=dimensions)

    def test_015_get_products(self):
        """ Test to get products data """
        products = self._shipfunkClient.products
        for product in products:
            data = product.get_data()
            self.assertIsNotNone(data)

    def test_016_add_address(self):
        """ Test adding address data to object """
        new_country = 'fi'
        new_postal_code = '20100'
        self._shipfunkClient.add_address(country=new_country, postal_code=new_postal_code)

        data = self._shipfunkClient.get_address_data('country')
        self.assertTrue(data == new_country)

        data = self._shipfunkClient.get_address_data('postal_code')
        self.assertTrue(data == new_postal_code)

    def test_017_get_address_data(self):
        """ Test getting address data from the object address """
        data = self._shipfunkClient.get_address_data('country')
        self.assertIsNotNone(data)

        data = self._shipfunkClient.get_address_data('nameofthestreet')
        self.assertIsNone(data)

    def test_018_get_prices(self):
        """ Test get_price without parameters when data has been saved to object """
        prices = self._shipfunkClient.get_price()
        self.assertIsNotNone(prices['min_price'] and prices['max_price'])

    def test_019_get_orderid(self):
        """ Test getting order id """
        self.assertIsNotNone(self._shipfunkClient.orderid)

    def test_020_set_orderid(self):
        """ Test saving a new order id """
        neworderid = '23456'
        self._shipfunkClient.orderid = neworderid
        self.assertTrue(self._shipfunkClient.orderid == neworderid)

        with self.assertRaises(ValueError):
            self._shipfunkClient.orderid = ''

    def test_021_get_delivery_options(self):
        """ Test get_delivery_options that delivery options are returned """
        params = {
            "order": {
                "language": "FI",
                "monetary": {
                    "currency": "EUR",
                    "value": 8.9
                },
                "products": [
                    {
                        "amount": 1,
                        "code": "B53756b6174",
                        "name": "Deodorant",
                        "category": "Parfumes and cosmetics",
                        "weight": {
                            "unit": "kg",
                            "amount": 0.2
                        },
                        "dimensions": {
                            "unit": "cm",
                            "width": "15",
                            "depth": "10",
                            "height": "3"
                        },
                        "monetary_value": 8.9,
                        "toppleable": 1,
                        "stackable": 1,
                        "nestable": 0,
                        "additional_services": [
                            {
                                "code": "10004"
                            },
                            {
                                "code": "10025",
                                "count": 1,
                                "add_fee": 1
                            },
                            {
                                "code": "59010",
                                "count": 1,
                                "add_fee": 1
                            },
                            {
                                "code": "10028",
                                "packing_group": "",
                                "quantity": 0.2,
                                "quantity_unit": "kg",
                                "shipping_name": "",
                                "tunnel_restriction_code": "",
                                "un_code": "",
                                "warning_label_numbers": ""
                            }
                        ]
                    }
                ],
                "parcels": [
                    {
                        "code": 0,
                        "contents": "Parfumes and cosmetics",
                        "weight": {
                            "unit": "kg",
                            "amount": 0.2
                        },
                        "dimensions": {
                            "unit": "cm",
                            "width": "15",
                            "depth": "10",
                            "height": "3"
                        },
                        "monetary_value": 8.9,
                        "toppleable": 1,
                        "stackable": 1,
                    }
                ]
            },
            "customer": {
                "first_name": "Jaana",
                "last_name": "Sarajärvi",
                "street_address": "Testikatu 3",
                "postal_code": "30100",
                "city": "Forssa",
                "country": "FI",
                "postal_box": "",
                "company": "",
                "phone": "040 1231234",
                "email": "jaana@vilkas.fi"
            }
        }
        deliveryoptions = self._shipfunkClient.get_delivery_options(params)
        self.assertIsNotNone(deliveryoptions)

        params = {
            'value': 12
        }
        deliveryoptions = self._shipfunkClient.get_delivery_options(params)
        self.assertIsNotNone(deliveryoptions)

    def test_022_get_customer_address(self):
        """ Test getting customer address dictionary when only one address key is defined """
        params = {
            "customer": {
                "first_name": "Test",
                "last_name": "Tester",
                "street_address": "Testikatu 3",
                "postal_code": "30100",
                "city": "Forssa",
                "country": "FI",
                "postal_box": "",
                "company": "",
                "phone": "040 1231234",
                "email": "test@test.test"
            }
        }
        address_keys = 'postal_code'
        customer_address = self._shipfunkClient.get_customer_address_data(address_keys, params)
        self.assertIsNotNone(customer_address['postal_code'])
        self.assertEqual(customer_address['postal_code'], params['customer']['postal_code'])

        customer_address = self._shipfunkClient.get_customer_address_data(address_keys)
        with self.assertRaises(KeyError):
            self.assertIsNone(customer_address['first_name'])
        self.assertNotEqual(customer_address['postal_code'], params['customer']['postal_code'])

    def test_023_get_delivery_options(self):
        """ Test get_delivery_options without parameters when data is saved to object """
        self._shipfunkClient.add_address(city='Turku', first_name='Test', last_name='Tester',
                                         street_address='Test Street')

        deliveryoptions = self._shipfunkClient.get_delivery_options()
        self.assertIsNotNone(deliveryoptions)

    def test_024_get_delivery_options(self):
        """ Test get_delivery_options without any data """
        shipfunkclient2 = Shipfunk(os.environ.get('APIKEY'), '3456')
        with self.assertRaises(ValueError):
            shipfunkclient2.get_delivery_options()

    def test_025_get_pickups(self):
        """ Test get_pickups """
        params = {
            'postal_code': 30100,
            'country': 'fi',
            'carriercode': '02000201',
            'return_count': 6
        }
        pickupoffices = self._shipfunkClient.get_pickups(params)
        self.assertIsNotNone(pickupoffices)

    def test_026_get_pickups(self):
        """ Test get_pickups without optional params """
        params = {
            'carriercode': '02000201',
        }
        pickupoffices = self._shipfunkClient.get_pickups(params)
        self.assertIsNotNone(pickupoffices)

    def test_027_send_selected_deliver(self):
        """ Test send_selected_deliver so that prices are returned """
        params = {
            "selected_option": {
                "carriercode": "02000201",
                "pickupid": "701003200",
                "calculated_price": "5.55",
                "customer_price": "6.90",
                "return_prices": "1"
            }
        }
        prices = self._shipfunkClient.send_selected_delivery(params)
        self.assertIsNotNone(prices['customers_price'] and prices['calculated_price'])

    def test_028_set_order_status(self):
        """ Test set_order_status """
        params = {
            "status": "placed",
            "final_orderid": "23456"
        }
        result = self._shipfunkClient.set_order_status(params)
        self.assertEqual(result['Message'], 'OK')

    def test_029_set_order_status(self):
        """ Test set_order_status with wrong status """
        params = {
            "status": "test_status",
            "final_orderid": "23456"
        }
        with self.assertRaises(ValueError):
            self._shipfunkClient.set_order_status(params)

    def test_030_set_customer_details(self):
        """ Test set_customer_details so customer data is changed """
        params = {
            "return_cards": "1",
            "customer": {
                # "first_name": "MrFirstname",
                # "last_name": "Lastname",
                # "street_address": "Teststreet 10 A 35",
                # "postal_code": "20100",
                # "city": "Turku",
                # "country": "FI",
                "phone": "040 1231234",
                # "email": "example@example.com",
                # "PL": "0",
                # "company": ""
            }
        }
        result = self._shipfunkClient.set_customer_details(params)
        self.assertIsNotNone(result['parcels'])

    def test_031_create_new_package_cards(self):
        """ Test create_new_package_cards """
        params = {
            "order": {
                "return_cards": 1,
                "sendmail": 0,
                "send_edi": 0,
                "package_card": {
                    "direction": "both",
                    "format": "pdf",
                    "dpi": "300",
                    "size": "A4",
                    "reversed": 0
                },
                "additional_services": [
                    {
                        "code": "10001",
                        "bank_account": "FI2350000110000238",
                        "bic": "OKOYFIHH",
                        "monetary_value": 4,
                        "reference": "1000342"
                    },
                    {
                        "code": "10009",
                        "monetary_value": 4
                    }
                ],
                "parcels": [
                    {
                        #"product_codes": [
                        #    "B53756b6174"
                        #],
                        "weight": {
                            "unit": "kg",
                            "amount": 0.1
                        },
                        "tracking_codes": {
                            "send": "JJFI12340000000000004",
                            "return": "JJFI12340000000000005"
                        },
                        # "warehouse": "Varasto1"
                    }
                ]
            },
            "customer": {
                "first_name": "MrFirstname",
                "last_name": "Lastname",
                "street_address": "Teststreet 10 A 35",
                "postal_code": "20100",
                "city": "Turku",
                "country": "FI",
                "phone": "040 1231234",
                "email": "example@example.com",
                "PL": "0",
                "company": ""
            }
        }
        result = self._shipfunkClient.create_new_package_cards(params)
        self.assertIsNotNone(result['orderid'])

    def test_032_create_new_package_cards(self):
        """ Test create_new_package_cards without optional parameters """
        params = {
            "order": {
                "return_cards": 1,
                "sendmail": 0,
                "send_edi": 0,
                "package_card": {
                    "direction": "both",
                    "format": "pdf",
                    "dpi": "300",
                    "size": "A4",
                    "reversed": 0
                },
                "additional_services": [
                    {
                        "code": "10001",
                        "bank_account": "FI2350000110000238",
                        "bic": "OKOYFIHH",
                        "monetary_value": 4,
                        "reference": "1000342"
                    },
                    {
                        "code": "10009",
                        "monetary_value": 4
                    }
                ],
                "parcels": [
                    {
                        #"product_codes": [
                        #    "B53756b6174"
                        #],
                        "weight": {
                            "unit": "kg",
                            "amount": 0.1
                        },
                        "tracking_codes": {
                            "send": "JJFI12340000000000004",
                            "return": "JJFI12340000000000005"
                        },
                    }
                ]
            }
        }
        result = self._shipfunkClient.create_new_package_cards(params)
        self.assertIsNotNone(result['orderid'])

    def test_033_create_new_tracking_codes(self):
        """ Test create_new_tracking_codes so new tracking code are created """
        params = {
            "code_amount": "2"
        }
        result = self._shipfunkClient.create_new_tracking_codes(params)
        self.assertIsNotNone(result['tracking_codes'])

        params = {
            "carriercode": "02000201"
        }
        result = self._shipfunkClient.create_new_tracking_codes(params)
        self.assertIsNotNone(result['tracking_codes'])

    def test_034_get_package_cards(self):
        """ Test get_package_cards that package cards are returned """
        params = {
            "card_direction": "palautus"
        }
        with self.assertRaises(ValueError):
            self._shipfunkClient.get_package_cards(params)

        params = {
            "card_direction": "both",
        }
        result = self._shipfunkClient.get_package_cards(params)
        self.assertIsNotNone(result['orderid'])
        self.assertIsNotNone(result['parcel'])

        params = {
            "card_direction": "both",
            "tracking_code": "testi"
        }
        with self.assertRaises(ValueError):
            self._shipfunkClient.get_package_cards(params)

        params = {
            "card_direction": "both",
            "sendmail": 0
        }
        self._shipfunkClient.get_package_cards(params)
        self.assertIsNotNone(result['orderid'])
        self.assertIsNotNone(result['parcel'])

    def test_035_get_tracking_codes(self):
        """ Test get_tracking_codes that tracking codes are returned """
        params = {
            "card_direction": "palautus"
        }
        with self.assertRaises(ValueError):
            self._shipfunkClient.get_tracking_codes(params)

        params = {
            "card_direction": "send",
        }
        result = self._shipfunkClient.get_tracking_codes(params)
        self.assertIsNotNone(result['parcel'])

    def test_036_get_tracking_events(self):
        """ Test get_tracking_events that tracking events are returned """
        params = {
            "tracking_code": "testi"
        }
        with self.assertRaises(ValueError):
            self._shipfunkClient.get_tracking_events(params)

        params['transport_company'] = "Posti"
        with self.assertRaises(ValueError):
            self._shipfunkClient.get_tracking_events(params)

        params['carriercode'] = "1234567"
        with self.assertRaises(ValueError):
            self._shipfunkClient.get_tracking_events(params)

    def test_037_get_parcels(self):
        """ Test get_parcels that parcels are returned """
        result = self._shipfunkClient.get_parcels()
        self.assertIsNotNone(result['parcels'])

    def test_038_edit_parcels(self):
        """ Test edit_parcels that parcels are edited """
        params = {
            "return_parcels": 1,
            "parcels": [
                {
                    "id": "791281665",
                    "code": "",
                    "contents": "Clothing",
                    "weight": {
                        "unit": "kg",
                        "amount": "0.1"
                    },
                    "dimensions": {
                        "unit": "cm",
                        "width": "15",
                        "depth": "10",
                        "height": "3"
                    },
                    "monetary_value": "0",
                    # "warehouse": "Warehouse1",
                    "fragile": "0"
                }
            ]
        }
        result = self._shipfunkClient.edit_parcels(params)
        self.assertIsNotNone(result['parcels'])

    def test_039_remove_parcels(self):
        """ Test remove_parcel that parcels are removed """
        params = {
            "return_parcels": 1,
            "parcels": [
                {
                    "id": "791281665",
                    "parcel_code": "",
                    "tracking_code": "",
                }
            ]
        }
        result = self._shipfunkClient.delete_parcels(params)
        self.assertIsNotNone(result['parcels'])

        params = {
            "remove_all_parcels": 1
        }
        result = self._shipfunkClient.delete_parcels(params)
        self.assertIsNotNone(result['Code'])
        self.assertIsNotNone(result['Message'])

    def test_040_test_orderid(self):
        """ Test test_orderid that order id is checked """
        result = self._shipfunkClient.test_orderid()
        self.assertIsNotNone(result['Code'])
        self.assertIsNotNone(result['Message'])

    def test_041_change_product_no(self):
        """ Test for changing product number of the saved product """
        products = self._shipfunkClient.products
        product = products[0]
        self.assertIsNotNone(product.productno)

        with self.assertRaises(ValueError):
            product.productno = ''

        new_productno = 'NewProduct1'
        product.productno = new_productno
        self.assertEqual(product.productno, new_productno)

    def test_042_change_product_weight(self):
        """ Test for changing weight of the saved product """
        products = self._shipfunkClient.products
        product = products[0]
        self.assertIsNotNone(product.weight)
        self.assertIsNotNone(product.weightunit)

        with self.assertRaises(TypeError):
            product.weight = ''

        with self.assertRaises(TypeError):
            product.weight = '2 kg'

        with self.assertRaises(TypeError):
            product.weight = '-3.9'

        with self.assertRaises(ValueError):
            product.weight = 0

        new_weight = 3000
        new_unit = 'g'
        product.weight = new_weight
        self.assertEqual(product.weight, new_weight)

        product.weightunit = new_unit
        self.assertEqual(product.weightunit, new_unit)

    def test_043_change_product_amount(self):
        """ Test for changing amount of the saved product """
        products = self._shipfunkClient.products
        product = products[0]
        self.assertIsNotNone(product.amount)

        with self.assertRaises(TypeError):
            product.amount = ''

        with self.assertRaises(TypeError):
            product.amount = '2 pcs'

        with self.assertRaises(TypeError):
            product.amount = '-3.9'

        with self.assertRaises(ValueError):
            product.amount = 0

        new_amount = 4
        product.amount = new_amount
        self.assertEqual(product.amount, new_amount)

    def test_044_change_product_dimensions(self):
        """ Test for changing dimensions of the saved product """
        products = self._shipfunkClient.products
        product = products[0]

        dimensions = {
            "unit": "cm",
            "width": 25,
            "depth": 23.8,
            "height": 4
        }
        product.dimensions = dimensions
        self.assertEqual(product.dimensions['unit'], dimensions['unit'])

        dimensions['depth'] = 0
        with self.assertRaises(ValueError):
            product.dimensions = dimensions

        dimensions['depth'] = -3
        with self.assertRaises(ValueError):
            product.dimensions = dimensions

        dimensions['depth'] = '3cm'
        with self.assertRaises(ValueError):
            product.dimensions = dimensions

        dimensions['depth'] = ''
        with self.assertRaises(ValueError):
            product.dimensions = dimensions

        dimensions['unit'] = "testi"
        self.assertNotEqual(product.dimensions['unit'], dimensions['unit'])

        dimensions = {
            "unit": "cm",
            "width": 25,
            "depth": 23.8,
            "height": 4,
            "test": 4
        }
        with self.assertRaises(ValueError):
            product.dimensions = dimensions

    def test_045_change_warehouse(self):
        """ Test for changing warehouse of the saved product """
        products = self._shipfunkClient.products
        product = products[0]

        new_warehouse = 'Warehouse 100'
        product.warehouse = new_warehouse
        self.assertEqual(product.warehouse, new_warehouse)

        data = product.get_data()
        self.assertEqual(product.warehouse, data["warehouse"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
