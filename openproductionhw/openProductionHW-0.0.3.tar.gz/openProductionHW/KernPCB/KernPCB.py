# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 10:29:39 2019

@author: Produktion
"""

import serial
import time

class Scale:
    def __init__(self, ser="COM28"):
        self.ser = serial.Serial(ser, 9600, timeout=1, parity=serial.PARITY_NONE)
    
    def getWeight(self, sendCmd=True):
        if sendCmd:
            self.ser.write(b"s")
        x = self.ser.read(18)
        if len(x) == 18:
            weight = float(x[1:12].decode().replace(" ",""))
            unit = x[13:16].decode().strip()
            return weight, unit
        else:
            raise RuntimeError("length of retval=%d"%len(x))
    
    def close(self):
        self.ser.close()
    
if __name__ == "__main__":
    scale = Scale()
    print(scale.getWeight())