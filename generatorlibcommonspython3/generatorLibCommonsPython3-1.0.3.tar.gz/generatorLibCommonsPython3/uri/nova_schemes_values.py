'''
@author: BBVA
'''

from enum import Enum

__all__ = [
    'NovaSchemesValues'
]

class NovaSchemesValues(Enum):
	''' Schema type - http '''
	http  = 'http'
	''' Schema type - https '''
	https = 'https'
	''' Schema type - ws '''
	ws    = 'ws'
	''' Schema type - wss '''
	wss   = 'wss'