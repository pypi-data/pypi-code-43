"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from datetime import datetime
from katena_chain_sdk_py.crypto.ed25519.private_key import PrivateKey
from katena_chain_sdk_py.api.handler import Handler
from katena_chain_sdk_py.crypto.ed25519.public_key import PublicKey as PublicKeyEd25519
from katena_chain_sdk_py.crypto.nacl.public_key import PublicKey as PublicKeyX25519
from katena_chain_sdk_py.entity.api.tx_status import TxStatus
from katena_chain_sdk_py.entity.api.tx_wrapper import TxWrapper
from katena_chain_sdk_py.entity.api.tx_wrappers import TxWrappers
from katena_chain_sdk_py.entity.certify.common import format_bcid
from katena_chain_sdk_py.entity.certify.certificate import CertificateRawV1, CertificateEd25519V1
from katena_chain_sdk_py.entity.certify.secret import SecretNaclBoxV1
from katena_chain_sdk_py.entity.tx import Tx
from katena_chain_sdk_py.entity.tx_data_interface import TxData
from katena_chain_sdk_py.entity.tx_data_state import TxDataState, TxDataStateSchema
from katena_chain_sdk_py.exceptions.client_exception import ClientException


class Transactor:
    """ Transactor provides helper methods to hide the complexity of Tx creation, signature and API dialog. """

    def __init__(self, api_url: str, chain_id: str = "", company_chain_id: str = "", tx_signer: PrivateKey = None):
        """ Transactor constructor. """
        self.api_handler = Handler(api_url)
        self.chain_id = chain_id
        self.company_chain_id = company_chain_id
        self.tx_signer = tx_signer
        self.tx_data_state_schema = TxDataStateSchema()

    def send_certificate_raw_v1(self, uuid: str, value: bytes) -> TxStatus:
        """ Creates a CertificateRaw (V1), wraps in a tx and sends it to the API. """
        certificate = CertificateRawV1(format_bcid(self.company_chain_id, uuid), value)
        tx = self.get_tx(certificate)
        return self.api_handler.send_certificate(tx)

    def send_certificate_ed25519_v1(self, uuid: str, signer: PublicKeyEd25519, signature: bytes) -> TxStatus:
        """ Creates a CertificateEd25519 (V1), wraps in a tx and sends it to the API. """
        certificate = CertificateEd25519V1(format_bcid(self.company_chain_id, uuid), signer, signature)
        tx = self.get_tx(certificate)
        return self.api_handler.send_certificate(tx)

    def retrieve_certificate(self, company_chain_id: str, uuid: str) -> TxWrapper:
        """ Fetches the API to find the corresponding tx and return a tx wrapper. """
        return self.api_handler.retrieve_certificate(format_bcid(company_chain_id, uuid))

    def retrieve_certificates_history(self, company_chain_id: str, uuid: str) -> TxWrappers:
        """ Fetches the API to find the corresponding txs and returns tx wrappers or an error. """
        return self.api_handler.retrieve_certificates_history(format_bcid(company_chain_id, uuid))

    def send_secret_nacl_box_v1(self, uuid: str, sender: PublicKeyX25519, nonce: bytes, content: bytes) -> TxStatus:
        """ Creates a SecretNaclBox (V1), wraps in a tx and sends it to the API. """
        secret = SecretNaclBoxV1(format_bcid(self.company_chain_id, uuid), content, nonce, sender)
        tx = self.get_tx(secret)
        return self.api_handler.send_secret(tx)

    def retrieve_secrets(self, company_chain_id: str, uuid: str) -> TxWrappers:
        """ Fetches the API to find the corresponding txs and returns tx wrappers. """
        return self.api_handler.retrieve_secrets(format_bcid(company_chain_id, uuid))

    def get_tx(self, tx_data: TxData) -> Tx:
        """ Signs a tx data and returns a new tx ready to be sent. """
        if self.tx_signer is None or self.company_chain_id == "":
            raise ClientException("impossible to create txs without a private key or company chain id")
        nonce_time = datetime.utcnow()
        tx_data_state = self.get_tx_data_state(nonce_time, tx_data)
        tx_signature = self.tx_signer.sign(tx_data_state)
        return Tx(nonce_time, tx_data, self.tx_signer.get_public_key(), tx_signature)

    def get_tx_data_state(self, nonce_time: datetime, tx_data: TxData) -> bytes:
        """ Returns the sorted and marshaled json representation of a TxData ready to be signed. """
        tx_data_state = TxDataState(self.chain_id, nonce_time, tx_data)
        return self.tx_data_state_schema.dumps(tx_data_state).encode("utf-8")
