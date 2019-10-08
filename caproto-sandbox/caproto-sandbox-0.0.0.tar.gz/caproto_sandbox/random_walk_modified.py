#!/usr/bin/env python3
import random
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run

class RandomWalk(object):

    def __init__(self):
        self.x = 0.0
        self.dt = 3.0
        self.running = True

    def compute_new_x(self,x):
        from numpy import random
        return x + 2 * random.random() - 1

    def run_once(self):
        from numpy import random
        self.x = self.compute_new_x(self.x)
        from time import time
        self.t = time()
        self.push_to_IO(dict = {'x':self.x,'t':self.t})

    def run(self):
        from time import sleep
        while self.running:
            self.run_once()
            sleep(self.dt)

    def start(self):
        from threading import Thread
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
        return thread

    def push_to_IO(self,dict = {}):
        """
        updates PV if it matches with the key name in the input dictionary(dict).
        """
        pass

class RandomWalkIO(PVGroup):
    dt = pvproperty(value=3.0)
    x = pvproperty( value=0.0,
                    precision = 3,
                    units="mm",
                    upper_alarm_limit=2.0,
                    lower_alarm_limit=-2.0,
                    upper_warning_limit=1.0,
                    lower_warning_limit=-1.0
                    )
    t = pvproperty(value='')

    @x.startup
    async def x(self, instance, async_lib):
        'Periodically update the value'
        while True:
            # compute next value

            # update the ChannelData instance and notify any subscribers
            await instance.write(value=device.x)

            # Let the async library wait for the next iteration
            await async_lib.library.sleep(self.dt.value)

    @t.startup
    async def t(self, instance, async_lib):
        'Periodically update the value'
        while True:
            from datetime import datetime

            date_time = datetime.fromtimestamp(device.t)
            t = date_time.strftime("%m/%d/%Y, %H:%M:%S")

            await instance.write(value=t)

            # Let the async library wait for the next iteration
            await async_lib.library.sleep(self.dt.value)


device = RandomWalk()
device.start()

if __name__ == '__main__':
    from pdb import pm
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='random_walk:',
        desc='Run an IOC with a random-walking value.')
    ioc = RandomWalkIO(**ioc_options)
    run(ioc.pvdb, **run_options)
