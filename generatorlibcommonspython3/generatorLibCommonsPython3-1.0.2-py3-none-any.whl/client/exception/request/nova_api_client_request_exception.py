'''
@author: BBVA
'''

__all__ = [
    'NovaApiClientRequestException'
]

class NovaApiClientRequestException(Exception):
    def __init__(self, message):
        super().__init__(message)