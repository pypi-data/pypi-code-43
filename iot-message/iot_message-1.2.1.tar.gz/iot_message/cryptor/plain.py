from iot_message.abstract.cryptor_interface import CryptorInterface


class Cryptor(CryptorInterface):
    name = "message.plain"

    def encrypt(self, message):
        return message

    def decrypt(self, message):
        return message

