'''
@author: BBVA
'''

__all__ = [
    'NovaImplicitHeadersInput'
]

import re

class NovaImplicitHeadersInput:

  def __init__(self, headersMap):
    
    self.headersMap = headersMap

  def get_rawHeaderBoolean(self, key):
    outcome = None

    # Get the RAW Header as Array
    valuesListString = self.get_rawHeader(key)

    if valuesListString != None:
      outcome = []

      for valueString in valuesListString:
          
        # Remove all blanks
        valueString = re.sub(r"\s+", "", valueString)
        
        # Create the boolean
        valueString = valueString != None and valueString == "true"
        
        # Append to the array
        outcome.append(valueString)

    return outcome

  def get_rawHeaderFloat(self, key):
    outcome = None

    # Get the RAW Header as Array
    valuesListString = self.get_rawHeader(key)

    if valuesListString != None:
      outcome = []

      for valueString in valuesListString:
        outcome.append(float(valueString))

    return outcome

  def get_rawHeaderInt(self, key):
    outcome = None

    # Get the RAW Header as Array
    valuesListString = self.get_rawHeader(key)

    if valuesListString != None:
      outcome = []

      for valueString in valuesListString:
        outcome.append(int(valueString))

    return outcome
  
  def get_rawHeaderString(self, key):
    return self.get_rawHeader(key)

  def get_rawHeader(self, key):
    valuesListString = None
  
    if self.headersMap is not None:
      valuesListString = self.get_rawHeaderInternal(key)
  
    return valuesListString

  def get_rawHeaderInternal(self, key):
    outcome = None
    
    if self.headersMap.has_key(key):

      outcome = self.headersMap.get(key).split(",")
      
    return outcome