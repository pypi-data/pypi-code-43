"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from http import HTTPStatus
from katena_chain_sdk_py.api.client import Client
from katena_chain_sdk_py.entity.api.tx_status import TxStatusSchema, TxStatus
from katena_chain_sdk_py.entity.api.tx_wrapper import TxWrapperSchema, TxWrapper
from katena_chain_sdk_py.entity.api.tx_wrappers import TxWrappersSchema, TxWrappers
from katena_chain_sdk_py.entity.tx import Tx
from katena_chain_sdk_py.entity.tx import TxSchema
from katena_chain_sdk_py.exceptions.api_exception import ApiExceptionSchema


class Handler:
    """ Handler provides helper methods to send and retrieve tx without directly interacting with the HTTP Client. """
    ROUTE_CERTIFICATES = "certificates"
    ROUTE_SECRETS = "secrets"
    PATH_CERTIFY = "certify"
    PATH_HISTORY = "history"

    def __init__(self, api_url: str):
        """ Handler constructor """
        self.api_client = Client(api_url)
        self.tx_schema = TxSchema()
        self.tx_status_schema = TxStatusSchema()
        self.tx_wrapper_schema = TxWrapperSchema()
        self.tx_wrappers_schema = TxWrappersSchema()
        self.api_exception_schema = ApiExceptionSchema()

    def send_certificate(self, tx: Tx) -> TxStatus:
        """ Accepts a tx and sends it to the appropriate certificate API route. """
        return self.send_tx("{}/{}".format(self.ROUTE_CERTIFICATES, self.PATH_CERTIFY), tx)

    def retrieve_certificate(self, bcid: str) -> TxWrapper:
        """ Fetches the API and returns a tx wrapper. """
        response = self.api_client.get("{}/{}".format(self.ROUTE_CERTIFICATES, bcid))
        json_body = response.get_body().decode("utf-8")
        if response.get_status_code() == HTTPStatus.OK:
            return self.tx_wrapper_schema.loads(json_body)
        else:
            raise self.api_exception_schema.loads(json_body, unknown="EXCLUDE")

    def retrieve_certificates_history(self, bcid: str) -> TxWrappers:
        """ Fetches the API and returns a tx wrappers. """
        response = self.api_client.get("{}/{}/{}".format(self.ROUTE_CERTIFICATES, bcid, self.PATH_HISTORY))
        json_body = response.get_body().decode("utf-8")
        if response.get_status_code() == HTTPStatus.OK:
            return self.tx_wrappers_schema.loads(json_body)
        else:
            raise self.api_exception_schema.loads(json_body, unknown="EXCLUDE")

    def send_secret(self, tx: Tx) -> TxStatus:
        """ Accepts a tx and sends it to the appropriate API route. """
        return self.send_tx("{}/{}".format(self.ROUTE_SECRETS, self.PATH_CERTIFY), tx)

    def retrieve_secrets(self, bcid: str) -> TxWrappers:
        """ Fetches the API and returns a tx wrapper list. """
        response = self.api_client.get("{}/{}".format(self.ROUTE_SECRETS, bcid))
        json_body = response.get_body().decode("utf-8")
        if response.get_status_code() == HTTPStatus.OK:
            return self.tx_wrappers_schema.loads(json_body)
        else:
            raise self.api_exception_schema.loads(json_body, unknown="EXCLUDE")

    def send_tx(self, route: str, tx: Tx) -> TxStatus:
        """ Tries to send a tx to the API and returns a tx status or throws an api error. """
        data = self.tx_schema.dumps(tx)
        response = self.api_client.post(route, body=data)
        json_body = response.get_body().decode("utf-8")
        if response.get_status_code() == HTTPStatus.ACCEPTED:
            return self.tx_status_schema.loads(json_body)
        else:
            raise self.api_exception_schema.loads(json_body, unknown="EXCLUDE")
