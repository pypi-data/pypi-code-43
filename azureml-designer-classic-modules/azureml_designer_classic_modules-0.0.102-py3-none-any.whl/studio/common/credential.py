from uuid import UUID
from hashlib import sha256, pbkdf2_hmac
import base64

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad

from azureml.studio.common.mixins import MetaExtractMixin


class Cipher:
    """
    A class to do the encrypt and decrypt operation.
    """
    _KEY_SIZE = 32  # in bytes
    _BLOCK_SIZE = 16  # in bytes

    def __init__(self, uuid: UUID):
        self._key = self._get_key_bytes(uuid)

    def encrypt(self, to_be_encrypted: str):
        raise NotImplementedError("Not support encrypt for now")

    def decrypt(self, to_be_decrypted: str):
        bytes_to_decrypt = base64.b64decode(to_be_decrypted)

        key, iv = self._init_key_iv()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(bytes_to_decrypt)

        return unpad(decrypted, self._BLOCK_SIZE).decode('utf-8')

    def _init_key_iv(self):
        data = pbkdf2_hmac(
            hash_name='sha1',
            password=self._key,
            salt=self._key,
            iterations=1000,
            dklen=self._KEY_SIZE + self._BLOCK_SIZE
        )
        key = data[:self._KEY_SIZE]
        iv = data[self._KEY_SIZE:]
        return key, iv

    @staticmethod
    def _get_key_bytes(uuid: UUID):
        encoded = uuid.hex.encode('utf-8')
        return sha256(encoded).digest()


class SecureString:
    """
    Used to store string data which is sensitive and should not be displayed in stdout or stderr.
    """
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Failed to create SecureString: Expected str but got {type(value)}.")
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f"<SecureString, content omitted>"


class CredentialDescriptor(MetaExtractMixin):
    """
    The format of the generic credential param is a list of strings:
        1) first part is some name/type that the module developer assigns to the credential
        2) and the rest are the other parameter names that are form the key to credential.
    Credential lookup key is constructed using all the parts together.

    Example credential param declarations:
        Doc DB example: "passwd"("docdbcredential", "username"),
        SQL Azure reader example: "password"("sqlAzure", "user").
    """

    __slots__ = ('_credential_type', '_credential_key_parts')

    def __init__(self, credential_type, key_parts):
        self._credential_type = credential_type
        self._credential_key_parts = list(key_parts)

    @staticmethod
    def parse_from_str(input_str: str):
        """
        CredentialDescriptor is represented as a comma separated string.
        First element is key type, and the following are key parts.
        Example:
            "AzureStorageCredential,Hadoop User Account Name"
            "passwd,docdbcredential,username"
            "passwd,sqlAzure,user"
        """
        parts = input_str.split(',')
        if len(parts) < 2:
            raise ValueError(f"CredentialDescriptor must have at least 2 segments.")

        credential_type = parts[0]
        key_parts = parts[1:]
        return CredentialDescriptor(credential_type, key_parts)

    @property
    def credential_type(self):
        return self._credential_type

    @property
    def credential_key_parts(self):
        return self._credential_key_parts

    def __str__(self):
        parts = ','.join(self.credential_key_parts)
        return f"<CredentialDescriptor {self.credential_type},{parts}>"
