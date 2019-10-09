'''
@author: BBVA
'''

import random
import math

__all__ = [
    'RandomUtils'
]

class RandomUtils:

  def __init__(self):
  	pass

  def generateRandomBoolean():
    return random.random() >= 0.5
	
  def generateRandomInt():
    return math.floor((random.random() * 10) + 1)

  def generateRandomFloat():
    return (random.random() * 10) + 1

  def generateRandomString():
    randomString = "" ;
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    for x in range(6):
      randomString += possible[math.floor(random.random() * len(possible))]
	
    return randomString ;
	
  def generateRandomFile():
    return "dummyLocation"