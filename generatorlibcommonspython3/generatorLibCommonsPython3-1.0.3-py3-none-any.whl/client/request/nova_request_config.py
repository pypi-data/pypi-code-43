'''
@author: BBVA
'''

from generatorLibCommonsPython3.uri import NovaSchemesValues

__all__ = [
    'NovaRequestConfig'
]

class NovaRequestConfig:
	def __init__(self):
		self.novaSchemesValues = None
		self.timeout = None
    
	def get_novaSchemesValues(self):
		return self.novaSchemesValues

	def set_novaSchemesValues(self, novaSchemesValues):
		self.novaSchemesValues = novaSchemesValues

	def get_timeout(self):
		return self.timeout

	def set_timeout(self, timeout):
		self.timeout = timeout