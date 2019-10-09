'''
@author: BBVA
'''

__all__ = [
    'NovaApiClientResponseTimeoutException'
]

class NovaApiClientResponseTimeoutException(Exception):
    def __init__(self, message):
        super().__init__(message)