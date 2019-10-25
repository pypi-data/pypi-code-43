"""
Unofficial library, still in progress

Author:
    Fraser Langton <fraserbasil@gmail.com>

GitHub:
    github.com/fraser-langton/Quandoo

Quandoo API docs:
    docs.quandoo.com
"""

import json

import requests

from quandoo import config
from quandoo.Customer import Customer
from quandoo.Error import PoorResponse
from quandoo.Merchant import Merchant
from quandoo.QuandooModel import urljoin, PrettyClass
from quandoo.Reservation import Reservation
from quandoo.ReservationEnquiry import ReservationEnquiry


class Agent(PrettyClass):
    headers = {
        "accept": "application/json",
        "X-Quandoo-AuthToken": None
    }

    def __init__(self, oauth_token, agent_id, test=False):
        self.oauth_token = oauth_token
        self.agent_id = agent_id

        self.url = urljoin(config.base_url_test, config.version) if test else urljoin(config.base_url, config.version)

        self.headers["X-Quandoo-AuthToken"] = oauth_token

    def get_merchant(self, merchant_id):
        request = urljoin(self.url, "merchants", merchant_id)
        response = requests.get(request, headers=self.headers)

        if response.status_code == 200:
            return Merchant(json.loads(response.text), self)

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def get_customer(self, customer_id):
        request = urljoin(self.url, "customers", customer_id)
        response = requests.get(request, headers=self.headers)

        if response.status_code == 200:
            return Customer(json.loads(response.text), self)

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def get_reservation(self, reservation_id):
        request = urljoin(self.url, "reservations", reservation_id)
        response = requests.get(request, headers=self.headers)

        if response.status_code == 200:
            return Reservation(json.loads(response.text), self)

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def get_reservation_enquiry(self, reservation_enquiry_id):
        request = urljoin(self.url, "reservation-enquiries", reservation_enquiry_id)
        response = requests.get(request, headers=self.headers)

        if response.status_code == 200:
            return ReservationEnquiry(json.loads(response.text), self)

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def merchants(self, params=None):
        request = urljoin(self.url, 'merchants')
        response = requests.get(request, headers=self.headers, params=params)

        if response.status_code == 200:
            return [Merchant(i, self) for i in json.loads(response.text)['merchants']]

        raise PoorResponse(response.status_code, json.loads(response.text), request)


def status():
    request = urljoin(config.base_url, config.version, "status")
    response = requests.get(request)

    return response.status_code


def status_test():
    request = urljoin(config.base_url_test, config.version, "status")
    response = requests.get(request)

    return response.status_code
