#!/usr/bin/env python3
import termios
import fcntl
import sys
import os
import threading
import atexit
from time import time,sleep
from datetime import datetime

from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
from numpy import zeros
class Device(object):
    dt1 = 1
    dt2 = 1

    def start_io_interrupt_monitor(self,new_value_callback):
        '''
        This function monitors the terminal it was run in for keystrokes.
        On each keystroke, it calls new_value_callback with the given keystroke.

        This is used to simulate the concept of an I/O Interrupt-style signal from
        the EPICS world. Those signals depend on hardware to tell EPICS when new
        values are available to be read by way of interrupts - whereas we use
        callbacks here.
        '''
        while True:
            date_time = datetime.fromtimestamp(time())
            t = time()#date_time.strftime("%m/%d/%Y, %H:%M:%S.%f")
            new_value_callback({'t1':t})
            sleep(self.dt1)

    def start_io_interrupt_monitor2(self,new_value_callback2):
        '''
        This function monitors the terminal it was run in for keystrokes.
        On each keystroke, it calls new_value_callback with the given keystroke.

        This is used to simulate the concept of an I/O Interrupt-style signal from
        the EPICS world. Those signals depend on hardware to tell EPICS when new
        values are available to be read by way of interrupts - whereas we use
        callbacks here.
        '''
        while True:
            date_time = datetime.fromtimestamp(time())
            t = time()#date_time.strftime("%m/%d/%Y, %H:%M:%S.%f")
            new_value_callback2({'t2':t})
            sleep(self.dt2)


class IOInterruptIOC(PVGroup):
    t1 = pvproperty(value=2.0)
    dt1 = pvproperty(value=0.9, dtype = float, precision = 3)
    t2 = pvproperty(value=2.0)
    dt2 = pvproperty(value=0.9, dtype = float, precision = 3)
    arr = zeros((3,3960,3960))
    f_arr = arr.flatten()
    image = pvproperty(value = f_arr, dtype = float)

    # NOTE the decorator used here:
    #@dt1.startup
    #async def dt1(self, instance, async_lib):

    #@dt2.startup
    #async def dt2(self, instance, async_lib):

    @t1.startup
    async def t1(self, instance, async_lib):
        # This method will be called when the server starts up.
        print('* keypress method called at server startup')
        queue = async_lib.ThreadsafeQueue()

        # Start a separate thread that monitors keyboard input, telling it to
        # put new values into our async-friendly queue
        thread = threading.Thread(target=device.start_io_interrupt_monitor,
                                  daemon=True,
                                  kwargs=dict(new_value_callback=queue.put))
        device.dt1 = 1.1
        thread.start()

        # Loop and grab items from the queue one at a time
        while True:
            value = await queue.async_get()
            if 't1' in list(value.keys()):
                await self.t1.write(value['t1'])

    @t2.startup
    async def t2(self, instance, async_lib):
        # This method will be called when the server starts up.
        print('* keypress method called at server startup')
        queue = async_lib.ThreadsafeQueue()

        # Start a separate thread that monitors keyboard input, telling it to
        # put new values into our async-friendly queue
        thread = threading.Thread(target=device.start_io_interrupt_monitor2,
                                  daemon=True,
                                  kwargs=dict(new_value_callback2=queue.put))
        device.dt2 = 1.2
        thread.start()

        # Loop and grab items from the queue one at a time
        while True:
            value = await queue.async_get()
            if 't2' in list(value.keys()):
                await self.t2.write(value['t2'])

device = Device()

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='io_device:',
        desc='Run an IOC that updates via I/O interrupt on key-press events.')

    ioc = IOInterruptIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
