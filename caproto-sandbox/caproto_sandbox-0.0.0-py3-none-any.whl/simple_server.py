#!/usr/bin/env python3
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
from textwrap import dedent

class SimpleIOC(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs

    Scalar PVs
    ----------
    A (int)
    B (float)

    Vectors PVs
    -----------
    C (vector of int)
    """
    from numpy import random
    from time import time,sleep
    from pickle import dumps
    t = pvproperty(value=time())
    dt = pvproperty(value=0.015)
    integer = pvproperty(value=1)
    float = pvproperty(value=2.0)
    vector = pvproperty(value=[0.0]*3*1360*1024)
    string = pvproperty(value='0'*3*1360*1024)
    pickle = pvproperty(value=dumps(random.random((3,1360,1024))))
    i = 0

    @t.startup
    async def t(self, instance, async_lib):
        'Periodically update the value'
        from time import time, sleep
        print(self.t.value)
        #print(instance.read(data_type = '<ChannelType.DOUBLE: 6>'))
        while True:
            # compute next value
            # Let the async library wait for the next iteration
            t1 = time()
            await async_lib.library.sleep(self.dt.value)
            t2 = time()
            # update the ChannelData instance and notify any subscribers
            await instance.write(value=(t2-t1))

    @float.startup
    async def float(self, instance, async_lib):
        'Periodically update the value'
        from time import time, sleep
        print(self.float.value)
        while True:
            # compute next value
            # Let the async library wait for the next iteration
            t1 = time()
            await async_lib.library.sleep(self.dt.value)
            t2 = time()
            # update the ChannelData instance and notify any subscribers
            await instance.write(value=self.t.value)


from ubcs_auxiliary.threading import start_new_safe_thread
if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='simple:',
        desc=dedent(SimpleIOC.__doc__))
    ioc = SimpleIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
