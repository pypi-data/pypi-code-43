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

    def read(self, N = 50):
        from numpy import random
        from time import sleep
        arr = random.random(size = (N,4))
        return arr

    def run_once(self):
        self.buffer.append(daq.read())
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

class Camera(object):
    def __init__(self):
        from circular_buffer_numpy import circular_buffer
        self.buffer = circular_buffer.CircularBuffer(shape = (10,3,1360,1024))
        self.dt = 5
        self.running = True

    def read(self):
        from numpy import random
        from time import sleep
        arr = random.random(size = (1,3,1360,1024))
        return arr

    def run_once(self):
        self.buffer.append(self.read())

    def run(self):
        print('camera.run started in a new thread')
        from time import sleep
        while self.running:
            self.run_once()
            sleep(self.dt)

    def start(self):
        from ubcs_auxiliary.threading import start_new_safe_thread as new_thread
        new_thread(self.run)

    def stop(self):
        self.running = False



class Server(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs

    Scalar PVs
    ----------
    RBV1 (mean value of last second of data for channel 1)
    RBV2 ...
    RBV3 ...
    RBV4 ...


    Vectors PVs
    -----------
    IMAGE (flatten image array)
    CB (flatten Circular Buffer array)
    CBshape (array shape of the CB)
    """

    IMAGE = pvproperty(value=zeros((3,1360,1024)).flatten(), read_only = True, dtype = float)
    CB = pvproperty(value=zeros((1000,4)).flatten(), read_only = True, dtype = float)
    CBshape = pvproperty(value=[1000,4], read_only = True)
    DAQ_dt = pvproperty(value=0.0)

    @DAQ_dt.putter
    async def DAQ_dt(self, instance, async_lib):
        try:
            return await daq.set_dt(value,instance, async_lib)
        except:
            return None

    @DAQ_dt.getter
    async def DAQ_dt(self, instance, async_lib):
        try:
            return await daq.get_dt(instance, async_lib)
        except:
            return await None

    @IMAGE.startup
    async def IMAGE(self, instance, async_lib):
        await self.pull_IMAGE(instance, async_lib)

    @DAQ_dt.startup
    async def DAQ_dt(self, instance, async_lib):
        await instance.write(value=0.0)

    async def pull_IMAGE(self, instance, async_lib):
        'Periodically update the value'
        await instance.write(value=ndarray.flatten(camera.buffer.get_last_value()))

    @CB.startup
    async def CB(self, instance, async_lib):
        await self.pull_CB(instance, async_lib)
    async def pull_CB(self, instance, async_lib):
        'Periodically update the value'
        from time import time, sleep
        await instance.write(value=ndarray.flatten(daq.buffer.get_all()))


    # @string.putter
    # async def string(self, instance, value):
    #     from matplotlib import pyplot as plt
    #     plt.figure()
    #     plt.plot([1,2,3,4],[1,2,3,4],'o')
    #     plt.show()


    def is_start(self):
        return
daq = DAQ()
daq.start()
camera = Camera()
camera.start()
from ubcs_auxiliary.threading import start_new_safe_thread
if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='simple:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)
    run(ioc.pvdb, **run_options)
