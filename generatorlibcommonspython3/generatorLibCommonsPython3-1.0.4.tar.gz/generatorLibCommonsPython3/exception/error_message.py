'''
@author: BBVA
'''

from generatorLibCommonsPython3.exception.error_message_type import ErrorMessageType
from generatorLibCommonsPython3.exception.error_message_params import ErrorMessageParams
from generatorLibCommonsPython3.utils.nova_translator import NovaTranslator

__all__ = [
    'ErrorMessage'
]

class ErrorMessage:
  novaMetadatasErrorMessage = [
                                { "name": "code", "required": "true", "type": "simple", "typeOf": str},
                                { "name": "message", "required": "true", "type": "simple", "typeOf": str},
                                { "name": "type", "required": "true", "type": "object", "typeOf": ErrorMessageType},
                                { "name": "parameters", "required": "true", "type": "array", "typeOf": ErrorMessageParams, "depth": 1}
                              ] ;

  def __init__(self, code=None, message=None, typeInput=None, parameters=None):

    self.code = code
    self.message = message
    self.type = typeInput
    self.parameters = parameters

  def get_code(self):
    return self.code

  def set_code(self, code):
    self.code = code

  def get_message(self):
    return self.message

  def set_message(self, message):
    self.message = message

  def get_type(self):
    return self.type

  def set_type(self, typeInput):
    self.type = typeInput

  def get_parameters(self):
    return self.parameters

  def set_parameters(self, parameters):
    self.parameters = parameters

  def serialize(inputJson):

    # New Constructor
    instance = ErrorMessage()

    # Internal call
    NovaTranslator.serialize(instance, ErrorMessage.novaMetadatasErrorMessage, inputJson)

    # Return the filled instance
    return instance

  def deserialize(self):

    return NovaTranslator.deserialize(self, ErrorMessage.novaMetadatasErrorMessage, {})