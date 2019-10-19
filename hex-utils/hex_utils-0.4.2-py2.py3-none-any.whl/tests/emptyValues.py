'''
Created on 19 Aug 2016

@author: desouslu
'''
from hex_utils.hasc import HASC 

h = HASC()
h.init(2, 2, 3, 3, 4, "empty")
h.save("testGrid.hasc")