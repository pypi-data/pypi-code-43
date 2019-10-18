'''
@author: BBVA
'''

from generatorLibCommonsPython3.exception.error_message import ErrorMessage
from generatorLibCommonsPython3.utils.nova_translator import NovaTranslator

__all__ = [
    'Errors'
]

class Errors(Exception):
  novaMetadatasErrors = [
                          { "name": "status", "required": "true", "type": "simple", "typeOf": int},
                          { "name": "messages", "required": "true", "type": "array", "typeOf": ErrorMessage, "depth": 1}
                        ] ;


  def __init__(self, status=590, messages=None):
    
    self.status = status
    self.messages = messages

  def get_status(self):
    return self.status

  def set_status(self, status):
    self.status = status

  def get_messages(self):
    return self.messages

  def set_messages(self, messages):
    self.messages = messages

  def serialize(inputJson):
    # New Constructor
    instance = Errors()

    # Internal call
    NovaTranslator.serialize(instance, Errors.novaMetadatasErrors, inputJson)

    # Return the filled instance
    return instance

  def deserialize(self):

  	return NovaTranslator.deserialize(self, Errors.novaMetadatasErrors, {})