'''
@author: BBVA
'''

__all__ = [
    'NovaImplicitHeadersOutput'
]

class NovaImplicitHeadersOutput:

  def __init__(self):
    
    self.headersMap = {}

  def set_rawHeader(self, key, valuesList):
    valuesListString = None

    if (valuesList != None):

      # Check if the element is a list
      if isinstance(valuesList, list):
        
        # Join as string separated by comma
        valuesListString = ",".join( str(value) for value in valuesList )

      else:

        valuesListString = valuesList

      # Set the Raw Header as array of str
      self.set_rawHeaderInternal(key, valuesListString)
  
  def set_rawHeaderInternal(self, key, valuesList):
    
    if valuesList != None:
      
      self.headersMap[key] = valuesList
  
  def get_output(self):    
      
    return self.headersMap