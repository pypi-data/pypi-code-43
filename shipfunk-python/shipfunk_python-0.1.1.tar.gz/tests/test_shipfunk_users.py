#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `shipfunk_python` package."""


import unittest
import logging
import os
from shipfunk_python.shipfunk import ShipfunkUser

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


class TestShipfunk(unittest.TestCase):
    """ Test for Shipfunk package and it's user account methods. """

    @classmethod
    def setUpClass(cls):
        """ Set up our Shipfunk client for tests. It requires the following environment variables: test_apikey """
        cls._shipfunkClientUser = ShipfunkUser(os.environ.get('APIKEY_USERS'))
        cls._email = os.environ.get('EMAIL')

    def test_001_create_user(self):
        """ Test create_user that a new user account has been created """
        params = {
            "user": {
                "email": self._email,
                "locale": "FI",
                "eshop_name": "Example Store",
                "business_id": "12312345",
                "customs_id": "6543210",
                "contact_person_name": "Test Tester",
                "contact_person_phone": "040 1231234",
                "contact_person_email": self._email,
                "web_address": "real_deal.example.com",
                "customer_contact_info": "<b>Contact us:</b> service@example.com"
            }
        }

        with self.assertRaises(ValueError):
            result = self._shipfunkClientUser.create_user(params)

    def test_002_create_user(self):
        """ Test get_user that user data is returned """
        params = {
            "email": self._email,
        }
        with self.assertRaises(ValueError):
            result = self._shipfunkClientUser.get_user(params)

    def test_003_edit_user(self):
        """ Test edit_user that user data is changed """
        params = {
            "user": {
                "email": self._email,
                "locale": "FI",
                "eshop_name": "DemoShop",
                "business_id": "12312345",
                "customs_id": "6543210",
                "contact_person_name": "Test Tester",
                "contact_person_phone": "040 123456789",
                "contact_person_email": self._email,
                "web_address": "real_deal.example.com",
                "customer_contact_info": "<b>Contact us:</b> service@example.com"
            }
        }
        with self.assertRaises(ValueError):
            result = self._shipfunkClientUser.edit_user(params)

    def test_004_detach_user(self):
        """ Test detach_user that user data is detached from your account """
        params = {
            "email": self._email,
        }
        with self.assertRaises(ValueError):
            result = self._shipfunkClientUser.detach_user(params)

    def test_005_create_invitation(self):
        """ Test create_invitation that invitation is sent to existing user """
        params = {
            "email": self._email,
        }
        result = self._shipfunkClientUser.create_invitation(params)        
        self.assertIsNotNone(result['Code'])
        self.assertIsNotNone(result['Message'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
