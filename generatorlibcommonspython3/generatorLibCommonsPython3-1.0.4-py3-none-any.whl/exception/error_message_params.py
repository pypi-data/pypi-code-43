'''
@author: BBVA
'''

from generatorLibCommonsPython3.utils.nova_translator import NovaTranslator

__all__ = [
    'ErrorMessageParams'
]

class ErrorMessageParams:
  novaMetadatasErrorMessageParams = [
                                      { "name": "name", "required": "true", "type": "simple", "typeOf": str}
                                    ] ;

  def __init__(self, name=None):

    self.name = name

  def get_name(self):
    return self.name

  def set_name(self, name):
    self.name = name

  def serialize(inputJson):

    # New Constructor
    instance = ErrorMessageParams()

    # Internal call
    NovaTranslator.serialize(instance, ErrorMessageParams.novaMetadatasErrorMessageParams, inputJson)

    # Return the filled instance
    return instance

  def deserialize(self):

    return NovaTranslator.deserialize(self, ErrorMessageParams.novaMetadatasErrorMessageParams, {})