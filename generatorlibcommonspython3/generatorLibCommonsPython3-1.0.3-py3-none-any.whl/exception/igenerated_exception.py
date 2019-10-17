'''
@author: BBVA
'''

__all__ = [
    'IGeneratedException'
]

class IGeneratedException:

  def __init__(self):
    pass

  def getStatus(self):
    raise NotImplementedError("getStatus method must be implemented")

  def serialize(inputJson):
    raise NotImplementedError("serialize method must be implemented")

  def deserialize(self):
  	raise NotImplementedError("deserialize method must be implemented")