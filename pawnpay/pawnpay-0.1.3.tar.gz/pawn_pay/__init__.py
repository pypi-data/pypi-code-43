"""The Official Pawn Payment Solutions API Client"""

#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification

import json
import logging
from collections import namedtuple, UserList
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import requests
import sentry_sdk
from loguru import logger
from ratelimit import limits, sleep_and_retry
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.serverless import serverless_function
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .Exceptions import *


class Customer(object):
    @classmethod
    def do_nothing(cls, key_val):
        pass

    def __init__(self, data=None, name=None, email=None, phone=None):
        if data is not None and not isinstance(data, dict):
            raise ValueError("Customer data must be supplied as a JSON array!")
        for x in [name, email, phone]:
            if x is not None and not isinstance(x, str):
                raise ValueError("Customer data must be strings when supplied via explicit keyword values!")
        if data is not None and isinstance(data, dict) and name is None and email is None and phone is None:
            super(Customer, self).__setattr__("name", data["name"])
            super(Customer, self).__setattr__("email", data["email"])
            super(Customer, self).__setattr__("phone", "".join(x if x.isnumeric() else "" for x in data["phone"]))
        elif data is None and name is not None and email is not None and phone is not None:
            super(Customer, self).__setattr__("name", name)
            super(Customer, self).__setattr__("email", email)
            super(Customer, self).__setattr__("phone", "".join(x if x.isnumeric() else "" for x in phone))
        elif data is not None and any([name is not None, email is not None, phone is not None]):
            raise AttributeError(
                "Customer objects must be instantiated with a JSON array -OR- explicit keyword values, NOT both"
            )
        elif data is None and any([name is None, email is None, phone is None]):
            raise AttributeError(
                "Customer objects must be instantiated with either a JSON array or explicit keyword values"
            )

    def __setattr__(self, key, value):
        raise NotImplementedError("Customer objects are immutable!")

    def __iter__(self):
        yield from self.__dict__.items()

    def __getitem__(self, item):
        return (
            list(self.__dict__.values())[list(self.__dict__.keys()).index(item)]
            if isinstance(item, str)
            else list(self.__dict__.values())[item]
            if isinstance(item, int)
            else ValueError
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self.name + " (" + self.email + ")")


class Ticket(object):
    @classmethod
    def do_nothing(cls, key_val):
        pass

    def __init__(self, data: dict):
        from re import match

        for key, attr in data.items():
            super(Ticket, self).__setattr__(key, attr) if key in [
                "number",
                "amount",
                "status",
                "renewal_period",
                "renew_from_payment",
                "layaway",
                "layaway_total",
                "layaway_payment",
            ] else super(Ticket, self).__setattr__(
                "due_date",
                datetime.strptime(attr, "%Y/%m/%d %H:%M:%S %z")
                if isinstance(attr, str)
                else attr
                if isinstance(attr, datetime)
                else datetime.now() + timedelta(days=30),
            ) if key == "due_date" else super(
                Ticket, self
            ).__setattr__(
                "customer_email", attr
            ) if (
                (key == "customer_email") and (bool(match(r"(\w|\d|\s)*@(\w|\d|\s)*\.(\w|\d|\s){2,4}", str(attr))))
            ) else self.do_nothing(
                key_val=key
            )

    def __iter__(self):
        yield from self.__dict__.items()

    def __getitem__(self, item):
        return (
            list(self.__dict__.values())[list(self.__dict__.keys()).index(item)]
            if isinstance(item, str)
            else list(self.__dict__.values())[item]
            if isinstance(item, int)
            else ValueError
        )

    def __repr__(self):
        return str(
            "Ticket "
            + self.number
            + " (${owe:.2f}".format(owe=float(int(self.amount) / 100))
            + " due "
            + self.due_date.strftime("%m-%d-%Y")
            + ")"
        )


class Payment(object):
    @classmethod
    def do_nothing(cls, key_val):
        pass

    def __init__(self, data: dict):
        class PaymentMethod(object):
            def __init__(self, m_data: dict):
                class Address(object):
                    def __init__(self, a_data: dict):
                        [super(Address, self).__setattr__(k, v) for k, v in a_data.items()]

                    def __setattr__(self, key, value):
                        raise NotImplementedError("Address objects are immutable!")

                    def __iter__(self):
                        yield from self.__dict__.items()

                    def __getitem__(self, item):
                        return (
                            list(self.__dict__.values())[list(self.__dict__.keys()).index(item)]
                            if isinstance(item, str)
                            else list(self.__dict__.values())[item]
                            if isinstance(item, int)
                            else ValueError
                        )

                    def __str__(self):
                        return str(
                            self.street + ", " + self.city + ", " + self.state + " " + self.zip + " " + self.country
                        )

                    def __repr__(self):
                        return str(self.__dict__)

                [
                    super(PaymentMethod, self).__setattr__(
                        k,
                        (
                            v
                            if k not in ["address", "expired", "created_at", "updated_at"]
                            else Address(a_data=v)
                            if k == "address"
                            else datetime.strptime(v, "%Y/%m/%d %H:%M:%S %z")
                            if k in ["created_at", "updated_at"]
                            else v
                        ),
                    )
                    for k, v in m_data.items()
                ]

            def __setattr__(self, key, value):
                raise NotImplementedError("PaymentMethod objects are immutable!")

            def __iter__(self):
                yield from self.__dict__.items()

            def __getitem__(self, item):
                return (
                    list(self.__dict__.values())[list(self.__dict__.keys()).index(item)]
                    if isinstance(item, str)
                    else list(self.__dict__.values())[item]
                    if isinstance(item, int)
                    else ValueError
                )

            def __str__(self):
                return (
                    str(self.sub_type.title() + " Card ending in " + self.last_four)
                    if self.type == "credit"
                    else str("ACH Account ending in " + self.last_four)
                )

            def __repr__(self):
                return str({k: (v if k != "address" else self.address.__dict__) for k, v in self.__dict__.items()})

        [
            super(Payment, self).__setattr__(
                k,
                (
                    v
                    if k not in ["created_at", "payment_method", "recorded"]
                    else datetime.strptime(v, "%Y/%m/%d %H:%M:%S %z")
                    if k == "created_at"
                    else PaymentMethod(m_data=v)
                    if k == "payment_method"
                    else True
                    if k == "recorded" and v == "true"
                    else False
                    if k == "recorded" and v == "false"
                    else v
                ),
            )
            for k, v in data.items()
        ]

    def __setattr__(self, key, value):
        raise NotImplementedError("Payment objects are immutable!")

    def __iter__(self):
        yield from self.__dict__.items()

    def __getitem__(self, item):
        return (
            list(self.__dict__.values())[list(self.__dict__.keys()).index(item)]
            if isinstance(item, str)
            else list(self.__dict__.values())[item]
            if isinstance(item, int)
            else ValueError
        )

    def __repr__(self):
        return str(
            "$"
            + str(float(int(self.amount) / 100))
            + " paid against ticket "
            + str(self.ticket_number)
            + " (Ref #: "
            + self.number
            + ")"
        )


class CustomerList(UserList):
    def __init__(self, data: list):
        if isinstance(data, type(None)):
            super(CustomerList, self).__init__([])
        elif len(data) < 1:
            super(CustomerList, self).__init__([])
        else:
            super(CustomerList, self).__init__(self)
            try:
                for customer in data:
                    self.append(customer=customer)
            except KeyError:
                raise CatastrophicPhaseVariance("Customers must be passed as a list of JSON arrays")

    def append(self, customer: any([dict, Customer])):
        try:
            super(CustomerList, self).append(
                Customer(name=customer["name"], email=customer["email"], phone=customer["phone"])
                if isinstance(customer, dict)
                else customer
            )
        except KeyError:
            raise CatastrophicPhaseVariance(
                "Customers must be passed as either a <class 'pawn_pay.helpers.Customer'> "
                + 'object or a JSON array like: {"name": "Johnny Appleseed", '
                + '"email": "johnny@appleseed.com", "phone": "4045559818"}'
            )

    @property
    def for_pawnpay(self):
        cl = [x.email.lower() for x in self]

        return {
            "customers": list(
                filter(
                    lambda x: cl.count(x["email"]) == 1 and "@" in x["email"],
                    list(
                        filter(
                            lambda x: all(
                                [
                                    list(["name", "email", "phone"]) == list(x.keys()),
                                    len(list(filter(lambda y: y is None, list(x.values())))) == 0,
                                ]
                            ),
                            [x.__dict__ for x in self],
                        )
                    ),
                )
            )
        }


class TicketList(UserList):
    def __init__(self, data: list):
        if isinstance(data, type(None)):
            super(TicketList, self).__init__([])
        elif len(data) < 1:
            super(TicketList, self).__init__([])
        else:
            super(TicketList, self).__init__()
            try:
                for ticket in data:
                    self.append(ticket_data=ticket)
            except KeyError:
                raise CatastrophicPhaseVariance("Tickets must be passed as a list of JSON arrays")

    def append(self, ticket_data: any([dict, Ticket])):
        try:
            super(TicketList, self).append(Ticket(data=ticket_data) if isinstance(ticket_data, dict) else ticket_data)
        except KeyError:
            raise CatastrophicPhaseVariance(
                "Tickets must be passed as either a <class 'pawn_pay.helpers.Payment'> object or a JSON array"
            )

    @property
    def for_pawnpay(self):
        return [
            {k: v for k, v in list(filter(lambda x: all([x[1] is not None, str(x[1]) != ""]), ticket.items()))}
            for ticket in [
                {k: (v if k != "due_date" else v.strftime("%m-%d-%Y")) for k, v in item.__dict__.items()}
                for item in self
            ]
        ]


class PaymentList(UserList):
    def __init__(self, data: list):
        if isinstance(data, type(None)):
            super(PaymentList, self).__init__([])
        elif len(data) < 1:
            super(PaymentList, self).__init__([])
        else:
            super(PaymentList, self).__init__()
            try:
                for pay in data:
                    self.append(pay_data=pay)
            except KeyError:
                raise CatastrophicPhaseVariance("Payments must be passed as a list of JSON arrays")

    def append(self, pay_data: any([dict, Payment])):
        try:
            super(PaymentList, self).append(Payment(data=pay_data) if isinstance(pay_data, dict) else pay_data)
        except KeyError:
            raise CatastrophicPhaseVariance(
                "Payments must be passed as either a <class 'pawn_pay.helpers.Payment'> object or a JSON array"
            )

    @property
    def for_pawnpay(self):
        return {"payments": [x.number for x in self]}


class TemporalSubspaceHolocapacitor(object):
    """Creates a connection to the Pawn-Pay server

    The Pawn-Pay API can be broken down into three major parts - Customers, Tickets, and Payments.
    The Pawn-Pay client supplies methods for interacting with each part, and simple-to-use functions
    to perform all the actions the API allows.

    Attributes:
        authcheck (bool): A boolean indicating if the supplied Pawn-Pay API credentials are valid

    Functions:
        create_customers: Creates one or more customer records
        create_tickets: Creates one or more ticket records
        get_customers: Returns either all of a store's customers or just the specified customer
        get_tickets: Returns either all of a store's tickets or just the specified ticket
        get_new_payments: Returns all payments not marked as recorded on Pawn-Pay
        mark_payments_recorded: Marks the specified payment(s) recorded
        update_customer: Updates the name, email address, or phone number one or more customer records
        update_tickets: Updates the due date, payment amount, or active status of one or more ticket records
    """

    def __init__(self, store_id: str, api_key: str, testing=False):
        """Sets up a Pawn-Pay client instance and validates the supplied credentials

        Args:
            store_id (str): Store ID to access Pawn-Pay with
            api_key (str): API Key to access Pawn-Pay with

        Raises:
            CatastrophicPhaseVariance: Raised if the supplied Pawn-Pay
                credentials don't pass an authentication check
            RuinousMicroFluctuation: Raised if there is an error in
                communicating with Pawn-Pay in general
        """
        # First thing, setup useful logging

        # The rather odd looking if-then below ensures that the first two lines
        # of the log file contain the right strings to allow the log to be read
        # as a Markdown-formatted table instead of a traditional "log" file
        if Path("pps_sync_log.md").resolve().exists():
            with Path("pps_sync_log.md").resolve().open() as log_lines:
                log_head = [next(log_lines) for x in range(2)]
            if {"| Date / Time | Level | Message |\n", "| :---------- | :---: | :------ |\n"} != set(log_head):
                log_contents = ["| Date / Time | Level | Message |\n", "| :---------- | :---: | :------ |\n"]
                [log_contents.append(line) for line in Path("pps_sync_log.md").resolve().open().readlines()]
                with Path("pps_sync_log.md").resolve().open("w") as new_log:
                    [new_log.write(line) for line in log_contents]
                del log_contents
            del log_head
        else:
            with Path("pps_sync_log.md").resolve().open("w") as new_log:
                [
                    new_log.write(line)
                    for line in ["| Date / Time | Level | Message |\n", "| :---------- | :---: | :------ |\n"]
                ]

        self.logger = logger
        self.logger.add(
            Path("pps_sync_log.md").resolve(),
            format="{time:| YYYY-MM-DD at HH:mm:ss} | {level} | {message} | ",
            retention="60 days",
            backtrace=True,
            diagnose=True,
        )

        # Make sure that any errors are reported to Sentry, even if they occur
        # during initialization of the Pawn-Pay connection
        self.sentry = sentry_sdk

        # Technically, all of this is already happening
        # by default in sentry, but just to be pedantic...
        self.__sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        self.sentry.init(
            dsn="https://999ed128c1f348f08be04770dd1e60b0@sentry.io/1764324",
            integrations=[SqlalchemyIntegration(), self.__sentry_logging],
        )

        # The client only returns named tuples
        self.__api_response = namedtuple(
            typename="ApiResponse",
            field_names=["success", "content", "status_code"],
            defaults=[False, None, None],
            module="pawn_pay",
        )

        # Set the authorization check to False until we actually check that we're authorized
        self.authcheck = False

        # Setup a connection to Pawn-Pay
        self._store_id = store_id
        self._api_key = api_key

        # Set up the request headers the way Pawn-Pay expects them to be

        self._headers = {
            r"Accept": r"application/json",
            r"Content-Type": r"application/json",
            r"User-Agent": r"pawn-pay_TemporalSubspaceHolocapacitor v0.1",
            r"X-Api-Key": self._api_key,
        }

        # The base URL for the Pawn-Pay Store
        self._baseurl = (r"https://staging." if testing else r"https://") + r"pawn-pay.com/api/v1/{storeId}".format(
            storeId=self._store_id
        )

        # Customer URIs
        self._customer_create = self._baseurl + r"/customer"  # [POST]
        self._customers_list = self._baseurl + r"/customers"  # [GET]
        self._customer = self._customer_create + r"/{email_address}"  # [GET]
        self._customers_sync = self._customers_list + r"/sync"  # [POST]

        # Ticket URIs
        self._ticket_create = self._baseurl + r"/ticket"  # [POST]
        self._tickets_batch = self._ticket_create + r"s"  # [GET] - List / [PATCH] - Update
        self._ticket = self._ticket_create + r"/{ticket}"  # [GET] - Details / [PATCH] - Update
        self._tickets_sync = self._tickets_batch + r"/sync"  # [POST]

        # Payment URIs
        self._payments = self._baseurl + r"/payments"
        self._payment = self._payments + r"/{number}"
        self._payments_new = self._payments + r"/new"  # [GET]
        self._payments_rec = self._payments + r"/recorded"  # [POST]
        self._payments_since = self._payments + r"?since={date}"  # [GET]
        self._payment_show = self._payment + r"/show"  # [GET]
        self._payment_refund = self._payment + r"/refund"  # [POST]

        # Check that the supplied credentials are viable
        try:
            auth = self.__get(url=self._baseurl)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            raise RuinousMicroFluctuation(err)

        # Pawn-Pay returns status code '418: I am a teapot' upon successful authentication
        # but it will also return 429 for authenticated requests that have exceeded the rate limit
        # which means we can consider a 429 response status_code as a successful auth check too
        if auth.status_code in (418, 429):
            self.authcheck = True
        else:
            raise CatastrophicPhaseVariance("Authorization check failed! Bad store ID or API Key")

    @sleep_and_retry
    @limits(calls=60, period=60)  # The Pawn-Pay API limits the request rate to 60 requests per minute
    def __get(self, url: str):
        """Makes a [GET] request to the supplied URL using pre-made Pawn-Pay
        headers

        Args:
            url (str): The URL to make the [GET] request to

        Returns:
            requests.models.Response: The API response Requests object
        """
        r = requests.get(url, headers=self._headers)
        if r.status_code == 429:
            sleep(int(r.headers['Retry-After']) + 1)
        return requests.get(url, headers=self._headers) if r.status_code == 429 else r

    @sleep_and_retry
    @limits(calls=60, period=60)  # The Pawn-Pay API limits the request rate to 60 requests per minute
    def __post(self, url: str, data: dict):
        """Makes a [POST] request to the supplied URL using pre-made Pawn-Pay
        headers

        Args:
            url (str): The URL to make the [POST] request to
            data (dict): The request body to send

        Returns:
            requests.models.Response: The API response Requests object
        """
        r = requests.post(url=url, headers=self._headers, data=json.dumps(data))
        if r.status_code == 429:
            sleep(int(r.headers['Retry-After']) + 1)
        return requests.post(url=url, headers=self._headers, data=json.dumps(data)) if r.status_code == 429 else r

    @sleep_and_retry
    @limits(calls=60, period=60)  # The Pawn-Pay API limits the request rate to 60 requests per minute
    def __patch(self, url: str, data: dict):
        """Makes a [PATH] request to the supplied URL using pre-made Pawn-Pay
        headers

        Args:
            url (str): The URL to make the [PATCH] request to
            data (dict): The request body to send

        Returns:
            requests.models.Response: The API response Requests object
        """
        r = requests.patch(url=url, headers=self._headers, data=json.dumps(data))
        if r.status_code == 429:
            sleep(int(r.headers['Retry-After']) + 1)
        return requests.patch(url=url, headers=self._headers, data=json.dumps(data)) if r.status_code == 429 else r

    # noinspection DuplicatedCode
    def create_customers(self, customers: any([list, CustomerList])):
        """Create one or more customer records

        Args:
            customers (str): A list of dicts like [{"name": (str), "email": (str), "phone": (str, 10 digits)}, ...]

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response (JSON), status_code (int)]
        """
        data = customers.for_pawnpay if not isinstance(customers, list) else {"customers": customers}

        try:
            create = self.__post(url=self._customers_sync, data=data)
            return self.__api_response(
                True if create.status_code == 200 else False,
                create.json() if create.status_code == 200 else json.loads(create.content),
                create.status_code,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            sentry_sdk.capture_exception(err)
            return self.__api_response(False, {"errors": str(err)}, 500)

    def update_customer(self, email: str, update: any([dict, Customer])):
        """Update an individual customer record

        Args:
            email (str): The customer's email address
            update (dict): The new customer information

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response_body (JSON), status_code]
        """
        try:
            customer_update = self.__patch(
                url=str(self._customer.format(email_address=email)),
                data=update.__dict__ if not isinstance(update, dict) else update,
            )
            return self.__api_response(
                True if customer_update.status_code == 200 else False,
                customer_update.json() if customer_update.status_code == 200 else json.loads(customer_update.content),
                customer_update.status_code,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            sentry_sdk.capture_exception(err)
            return self.__api_response(False, {"errors": str(err)}, 500)

    # noinspection DuplicatedCode
    def create_tickets(self, data: any([list, TicketList])):
        """Creates one or more new ticket records

        Args:
            data (list): A list of dicts like:
            [
              {
                "number": (str) [omit if `ticket` is supplied,
                "amount": (int),
                "due_date": (str),
                "status": (str, [active || inactive]),
                "autobill": (bool),
                "renewal_period": (int),
                "renew_from_payment": (str)
              },
              ...
            ]

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response_body (JSON), status_code (int)]
        """
        created = list()
        errors = list()
        for ticket in (data.for_pawnpay) if not isinstance(data, list) else (data):
            try:
                creator = self.__post(url=self._ticket_create, data=ticket)
                created.append(ticket["number"]) if creator.status_code == 200 else errors.append(
                    tuple([ticket["number"], json.loads(creator.content)])
                )
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.SSLError,
                requests.exceptions.HTTPError,
                requests.exceptions.RequestException,
            ) as err:
                sentry_sdk.capture_exception(err)
                errors.append(tuple([ticket["number"], str(err)]))
        return self.__api_response(
            True if len(errors) < 1 else False,
            {"new_count": len(created), "error_count": len(errors), "created": created, "errors": errors},
            418,
        )

    def update_tickets(self, data: any([list, Ticket, TicketList]), ticket=None):
        """Update one or more ticket records

        Args:
            data (list): A list of dicts like:
            [
              {
                "number": (str) [omit if `ticket` is supplied,
                "amount": (int),
                "due_date": (str),
                "status": (str, [active || inactive]),
                "autobill": (bool),
                "renewal_period": (int),
                "renew_from_payment": (str)
              },
              ...
            ]
            ticket (str): The ticket number to update

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response_body (JSON), status_code (int)]
        """
        try:
            ticket_update = self.__patch(
                url=self._ticket.format(ticket=str(data.number))
                if isinstance(data, type(Ticket))
                else self._ticket.format(ticket=ticket)
                if ticket is not None
                else self._tickets_batch,
                data=data.__dict__
                if isinstance(data, type(Ticket))
                else data.for_pawnpay
                if isinstance(data, type(TicketList))
                else data[0]
                if ticket is not None and isinstance(data, list)
                else {"tickets": data}
                if ticket is None and isinstance(data, list)
                else {},
            )
            return self.__api_response(
                True if ticket_update.status_code == 200 else False,
                ticket_update.json() if ticket_update.status_code == 200 else json.loads(ticket_update.content),
                ticket_update.status_code,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            sentry_sdk.capture_exception(err)
            return self.__api_response(False, {"errors": str(err)}, 500)

    def get_customers(self, email=None):
        """Retrieves customers from Pawn-Pay

        If `email` is not supplied returns the complete customer list, otherwise
        only the specified customer is returned

        Args:
            email (str): [Optional] Retrieve the specified customer record

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response (JSON), status_code (int)]
        """
        try:
            response = self.__get(
                self._customer.format(email_address=str(email.email if isinstance(email, Customer) else str(email)))
                if email is not None
                else self._customers_list
            )
            return self.__api_response(
                True if response.status_code == 200 else False,
                CustomerList(response.json())
                if response.status_code == 200 and isinstance(response.json(), list)
                else Customer(response.json())
                if response.status_code == 200 and isinstance(response.json(), dict)
                else json.loads(response.content),
                response.status_code,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            sentry_sdk.capture_exception(err)
            return self.__api_response(False, {"errors": str(err)}, 500)

    # noinspection DuplicatedCode
    def get_tickets(self, ticket=None):
        """Retrieves tickets from Pawn-Pay

        If `ticket` is not supplied returns the complete ticket list, otherwise
        only the specified ticket is returned

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response (JSON), status_code (int)]
        """
        try:
            tickets = self.__get(
                self._ticket.format(ticket=str(ticket.number if isinstance(ticket, Ticket) else ticket))
                if ticket is not None
                else self._tickets_batch
            )
            return self.__api_response(
                True if tickets.status_code == 200 else False,
                TicketList(tickets.json())
                if tickets.status_code == 200 and ticket is None
                else Ticket(tickets.json())
                if tickets.status_code == 200 and ticket is not None
                else json.loads(tickets.content),
                tickets.status_code,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            sentry_sdk.capture_exception(err)
            return self.__api_response(False, {"errors": str(err)}, 500)

    # noinspection DuplicatedCode
    def get_payments(self, new=False, payment=None, since=None):
        """Retrieves a list of payments that have not been marked as processed
        from Pawn-Pay

        Args:
            new (bool): Only return payments not marked as `recorded` on Pawn-Pay
            payment (str): Return on the specified payment
            since (str): Only return payments made on or after the specified date, format: MMDDYYYY

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response (JSON array), status_code (int)]
        """
        try:
            payments = self.__get(
                self._payments_new
                if new
                else self._payment_show.format(number=str(payment))
                if payment is not None
                else self._payments_since.format(date=str(since))
                if since is not None
                else None
            )
            return self.__api_response(
                True if payments.status_code == 200 else False,
                Payment(payments.json())
                if payments.status_code == 200 and payment is not None
                else PaymentList(payments.json())
                if payments.status_code == 200 and payment is None
                else json.loads(payments.content),
                payments.status_code,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            sentry_sdk.capture_exception(err)
            return self.__api_response(False, {"errors": str(err)}, 500)

    # noinspection DuplicatedCode
    def mark_payments_recorded(self, payments: any([str, list, PaymentList])):
        """Mark a list of payments as recorded Pawn-Pay

        Args:
            payments (list): The payments which have been recorded

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response (JSON), status_code (int)]
        """
        try:
            recorded_payments = self.__post(
                url=self._payments_rec,
                data=payments.for_pawnpay
                if isinstance(payments, PaymentList)
                else {"payments": payments if isinstance(payments, list) else [payments]},
            )
            return self.__api_response(
                True if recorded_payments.status_code == 200 else False,
                recorded_payments.json()
                if recorded_payments.status_code == 200
                else json.loads(recorded_payments.content),
                recorded_payments.status_code,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            sentry_sdk.capture_exception(err)
            return self.__api_response(False, {"errors": str(err)}, 500)

    # noinspection DuplicatedCode
    def refund_payment(self, payment: any([str, Payment])):
        """Mark a list of payments as recorded Pawn-Pay

        Args:
            payment (str): The payment to refund

        Returns:
            pawn_pay.ApiResponse (tuple): [success (bool), response (JSON), status_code (int)]
        """
        try:
            refund = self.__post(
                url=self._payment_refund.format(number=payment.number if isinstance(payment, Payment) else payment),
                data={"payment": payment.number if isinstance(payment, Payment) else payment},
            )
            return self.__api_response(
                True if refund.status_code == 200 else False,
                refund.json() if refund.status_code == 200 else json.loads(refund.content),
                refund.status_code,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as err:
            sentry_sdk.capture_exception(err)
            return self.__api_response(False, {"errors": str(err)}, 500)

    @serverless_function
    def sync_tickets(self, local_tickets: type(TicketList)):
        pps_tickets = TicketList(list(filter(lambda x: x.status == "active", self.get_tickets().content)))
        to_delete = TicketList(
            [
                Ticket(
                    {
                        "number": t.number,
                        "amount": t.amount,
                        "due_date": t.due_date.strftime("%Y/%m/%d %H:%M:%S %z"),
                        "status": "inactive",
                    }
                )
                for t in list(filter(lambda x: x.number not in [y.number for y in local_tickets], pps_tickets))
            ]
        )
        to_create = TicketList(
            list(
                filter(
                    lambda x: x.number not in (([y.number for y in pps_tickets]) if len(local_tickets) > 0 else ([])),
                    local_tickets,
                )
            )
        )

        to_update = TicketList([])

        for ticket in list(
            filter(
                lambda x: all(
                    [(x.number not in [y.number for y in to_delete]), (x.number not in [z.number for z in to_create])]
                ),
                local_tickets,
            )
        ):
            if (
                ticket.due_date.date()
                < next(filter(lambda x: x.number == ticket.number, pps_tickets)).due_date.date()
            ):
                if "customer_email" in ticket.__dict__.keys():
                    temp = ticket.__dict__
                    temp.__delitem__("customer_email")
                    ticket = Ticket(temp)
                to_update.append(ticket)

        return {
            "delete": ((self.update_tickets(to_delete.for_pawnpay)) if len(to_delete) > 0 else ([])),
            "create": ((self.create_tickets(to_create.for_pawnpay)) if len(to_create) > 0 else ([])),
            "update": ((self.update_tickets(to_update.for_pawnpay)) if len(to_update) > 0 else ([])),
        }


# Copyright (c) 2019 | Advancing Technology Systems, LLC
# See LICENSE for any grants of usage, distribution, or modification
