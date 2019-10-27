import abc

__author__ = 'Bartosz Kościów'

"""Interface for cryptor"""


class CryptorInterface(metaclass=abc.ABCMeta):
    def encrypt(self, message):
        """encrypts Message"""
        pass

    def decrypt(self, message):
        """decrypt Message"""
        pass
