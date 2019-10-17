'''
@author: BBVA
'''

__all__ = [
    'NovaMetadata'
]

class NovaMetadata:

  def __init__(self, novaImplicitHeadersInput=None, novaImplicitHeadersOutput=None):
    
    self.novaImplicitHeadersInput = novaImplicitHeadersInput
    self.novaImplicitHeadersOutput = novaImplicitHeadersOutput

  def get_novaImplicitHeadersInput(self):
    return self.novaImplicitHeadersInput

  def set_novaImplicitHeadersInput(self, novaImplicitHeadersInput):
    self.novaImplicitHeadersInput = novaImplicitHeadersInput

  def get_novaImplicitHeadersOutput(self):
    return self.novaImplicitHeadersOutput

  def set_novaImplicitHeadersOutput(self, novaImplicitHeadersOutput):
    self.novaImplicitHeadersOutput = novaImplicitHeadersOutput