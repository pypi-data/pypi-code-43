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
    tec.set_temp(18)
    tec.output(state='ON')
    sleep(5)
    ldc.set_current_mA(0)
    ldc.output(state='ON')
    ldc.slow_start_mA(i=120, step=5, wait=0.1)
