#!/usr/bin/env python3
"""
Simple IOC based on caproto library.
It has
"""
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto
from textwrap import dedent
from pdb import pm

from numpy import random, array, zeros, ndarray, nan, isnan
from time import time,sleep
from pickle import dumps, loads

from circular_buffer_numpy import circular_buffer

class DAQ(object):
    def __init__(self):
        from circular_buffer_numpy import circular_buffer
        self.buffer = circular_buffer.CircularBuffer(shape = (1000,4))
        self.dt = 1
        self.running = True
        self.header = ['cpu','memory','battery']

    def read(self):
        import psutil
        from numpy import zeros
        memory = psutil.virtual_memory().available
        cpu = psutil.cpu_percent()
        battery = psutil.sensors_battery().percent
        arr = zeros((1,4))
        arr[0,0] = time()
        arr[0,1] = cpu
        arr[0,2] = memory
        arr[0,3] = battery
        return arr

    def run_once(self):
        self.buffer.append(self.read())
        sleep(self.dt)

    def run(self):
        from time import sleep
        while self.running:
            self.run_once()
            sleep(self.dt)

    def start(self):
        from ubcs_auxiliary.threading import start_new_safe_thread as new_thread
        new_thread(self.run)

    def stop(self):
        self.running = False

    def set_dt(self,value):
        self.dt = value
    def get_dt(self):
        return self.dt



class Server(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs

    Scalar PVs
    ----------
    CPU
    MEMORY
    BATTERY

    Vectors PVs
    -----------

    """

    CPU = pvproperty(value=0.0, read_only = True)
    MEMORY = pvproperty(value=0.0, read_only = True)
    BATTERY = pvproperty(value=0.0, read_only = True)
    TIME = pvproperty(value=time(), read_only = True, dtype = float, precision = 3)
    dt = pvproperty(value=1.0)

    # @CPU.startup
    # async def CPU(self, instance, async_lib):
    #     await self.pull_IMAGE(instance, async_lib)
    #
    # @MEMORY.startup
    # async def MEMORY(self, instance, async_lib):
    #     await self.pull_IMAGE(instance, async_lib)
    #
    # @BATTERY.startup
    # async def BATTERY(self, instance, async_lib):
    #     await self.pull_IMAGE(instance, async_lib)

daq = DAQ()
daq.start()

from ubcs_auxiliary.threading import start_new_safe_thread
if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='simple:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)
    run(ioc.pvdb, **run_options)
