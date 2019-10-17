'''
@author: BBVA
'''

from enum import Enum

__all__ = [
    'ErrorMessageType'
]

class ErrorMessageType(Enum):
  ''' Error Message type - fatal '''
  FATAL = "fatal"
  ''' Error Message type - critical '''
  CRITICAL = "critical"
  ''' Error Message type - error '''
  ERROR = "error"
  ''' Error Message type - warning '''
  WARNING = "warning"
  
  def serialize(inputString):
    
    instance = None

    if inputString == "fatal":
      instance = ErrorMessageType.FATAL
    elif inputString == "critical":
      instance = ErrorMessageType.CRITICAL
    elif inputString == "error":
      instance = ErrorMessageType.ERROR
    elif inputString == "warning":
      instance = ErrorMessageType.WARNING
   
    return instance

  def deserialize(self):
    
    outcome = None
    
    if self == ErrorMessageType.FATAL:
      outcome = "fatal"
    elif self == ErrorMessageType.CRITICAL:
      outcome = "critical"
    elif self == ErrorMessageType.ERROR:
      outcome = "error"
    elif self == ErrorMessageType.WARNING:
      outcome = "warning"

    return outcome