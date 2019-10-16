# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 16:37:06 2019

@author: jazzn
"""

import u12
d = u12.U12()
try:
    x=d.eDigitalIn(0)
    print(f"devide detected name={d.deviceName} ... id={d.id}")
except:
    print("no U12 device detected")

HIGH = 1
LOW = 0
AI0,AI1,AI2,AI3,AI4 =0,1,2,3,4
IO0,IO1,IO2,IO3 = 0,1,2,3

def analog_read(n):
    if not isinstance(n,int) or n<0 or n>4:
        print("l'argument n'est pas un entier compris entre 0 et 4")
        return None
    return d.eAnalogIn(n)['voltage']

def digital_read(n):
    if not isinstance(n,int) or n<0 or n>3:
        print("l'argument n'est pas un entier compris entre 0 et 3")
        return None
    return d.eDigitalIn(n)['state']

def digital_write(n,state):
    if not isinstance(n,int) or n<0 or n>3:
        print("l'argument n'est pas un entier compris entre 0 et 3")
        return None
    d.eDigitalOut(n,state)

def analog_write(value0,value1):
    d.eAnalogOut(analogOut0=value0,analogOut1=value1)
    
def analog_stream(channel,rate=200,sample=1000):
    rate = max(min(rate,8000),20)
    sample=max(min(rate,8000),20)
    timeout = rate*sample*5
    
