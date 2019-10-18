'''
@author: BBVA
'''

__all__ = [
    'NovaApiClientResponseException'
]

class NovaApiClientResponseException(Exception):
    def __init__(self, message):
        super().__init__(message)