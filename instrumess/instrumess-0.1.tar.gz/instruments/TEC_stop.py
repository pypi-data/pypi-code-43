# -*- coding: utf-8 -*-
"""
Created on Tuesday 24-July-2018 at 18:27

@author: Rastko Pajković
"""

from time import sleep

from TEC import Tec
from LDC import Ldc

with Tec(address="GPIB0::18::INSTR", online=True) as tec, \
     Ldc(address="GPIB0::18::INSTR", online=True) as ldc:
    ldc.slow_stop(step=5, wait=0.1)
    sleep(1)
    tec.output(state='OFF')
