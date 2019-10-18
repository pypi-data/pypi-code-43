#-*- coding:utf-8 -*-
"""
    core

    This software is released under the MIT License.

    http://opensource.org/licenses/mit-license.php
    

"""
import base64
import re
from google.cloud import kms_v1
from google.oauth2 import service_account


class CryptUtil:

    def __init__(self,
                 project_id: str = None, location_id: str = None,
                 key_ring_id: str = None, crypto_key_id: str = None,
                 key_name: str = None, credential_path: str = None):
        """
        init
        :param project_id: GCP project id
        :param location_id: key location id ("global" etc.)
        :param key_ring_id: key ring id
        :param crypto_key_id: crypt key
        :param key_name: full path of key like below,
            'projects/(\S+)/locations/(\S+)/keyRings/(\S+)/cryptoKeys/(\S+)'
        :param credential_path: credential file path for a service account
        """
        if credential_path is not None:
            credentials = service_account.Credentials.from_service_account_file(
                credential_path
            )
        else:
            credentials = None

        if key_name is not None:
            self.__name = key_name
            ids = re.findall(
                'projects/(\S+)/locations/(\S+)/keyRings/(\S+)/cryptoKeys/(\S+)',
                key_name
            )
            if len(ids) != 1:
                raise ValueError("Failed to parse key name")
            else:
                ids = ids[0]
            if len(ids) != 4:
                raise ValueError("Failed to parse key name")
            self.__project_id = ids[0]
            self.__location_id = ids[1]
            self.__key_ring_id = ids[2]
            self.__crypto_key_id = ids[3]
            self.__client = kms_v1.KeyManagementServiceClient(
                credentials=credentials
            )
        else:
            self.__project_id = project_id
            self.__location_id = location_id
            self.__key_ring_id = key_ring_id
            self.__crypto_key_id = crypto_key_id
            self.__client = kms_v1.KeyManagementServiceClient(
                credentials=credentials
            )
            self.__update_key_name()

    @property
    def project_id(self):
        return self.__project_id

    @property
    def location_id(self):
        return self.__location_id

    @property
    def key_ring_id(self):
        return self.__key_ring_id

    @property
    def crypto_key_id(self):
        return self.__crypto_key_id

    @property
    def key_name(self):
        return self.__name

    def __update_key_name(self):
        """
        update context key name
        """
        self.__name = self.__client.crypto_key_path(
            self.__project_id, self.__location_id,
            self.__key_ring_id, self.__crypto_key_id)

    def encrypt(self, data: str, char_code: str = "utf8") -> str:
        """
        encrypt given data(string) with GCP KMS
        :param data: plain text data
        :param char_code: character code
        :return: base64 encoded encrypted data
        """
        data_bytes = data.encode(char_code)
        response = self.__client.encrypt(self.__name, data_bytes)
        return base64.b64encode(response.ciphertext).decode("utf8")

    def decrypt(self, b64_data: str, char_code: str = "utf8") -> str:
        """
        decrypt encrypted data
        :param b64_data: base64 encoded encrypted data
        :param char_code: character code
        :return: plain text
        """
        enc_byes = base64.b64decode(b64_data)
        response = self.__client.decrypt(self.__name, enc_byes)
        return response.plaintext.decode(char_code)


if __name__ == '__main__':
    pass