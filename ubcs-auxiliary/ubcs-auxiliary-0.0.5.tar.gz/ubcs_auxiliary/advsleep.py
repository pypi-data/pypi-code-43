"""
advance Sleep functions
author: Valentyn Stadnytskyi
data: 2017 - Nov 17 2018

functions:
psleep - precision sleep takes
intsleep with inputs t, dt and interupt as a function.

The precision sleep class.
functiob:
psleep - sleep specified amount of time with sub milisecond precision
test_sleep - for testing purposes. will print how much time the code waited.
This is important for the Windows platform programs if precise wait is required.
The Windows OS has ~15-17 ms latenct - the shortest time between attentions from OS.
"""
__vesrion__ = '1.0.0'
from time import  time, sleep
import sys
if sys.version_info[0] == 2:
    from time import clock as perf_counter
else:
    from time import perf_counter
import platform



def precision_sleep(t = 0.02, min_time = 0.017):
    """
    sleep for t seconds.
    """
    from time import time, sleep,perf_counter
    import platform
    min_time

    time_start = perf_counter()
    if platform.system() == 'Linux':
        sleep(t)
    #elif platform.system() == 'Darwin':
    #    sleep(t)
    else:
        if t>min_time:
            sleep(t-min_time)
            time_left = t - (perf_counter() - time_start)
            time_while_start = perf_counter()
            while perf_counter() - time_while_start <= time_left:
                pass
        else:
            time_left = t - (perf_counter() - time_start)
            time_while_start = perf_counter()
            while perf_counter() - time_while_start <= time_left:
                pass

def interupt_sleep(t= 0.02,dt = 0.01, interupt = None):
    """precision sleep function with interupt capabilities
    input:t - time to sleep, dt - check intervals, interupt - interupt function that return boolean
    """
    from time import perf_counter,sleep,time
    import types
    if not isinstance(interupt,types.FunctionType):
        precision_sleep(t)
    else:
        time_start = perf_counter()
        while perf_counter() - time_start <= t:
            if interupt(): break
            if (perf_counter() - time_start) >= dt:
                precision_sleep(dt)
            else:
                precision_sleep(perf_counter() - time_start)



if __name__ == '__main__':


    def test_psleep(t = 0.01):
        """
        test_sleep t = 0.01 in seconds
        """
        from time import time, sleep,perf_counter
        t1 =  perf_counter()
        psleep(t)
        t2 = perf_counter()
        dt = t2-t1
        print(dt)

    def test_intsleep(t = 0.1, dt = 0.1, interupt = False):
        """
        test_sleep t = 0.01 in seconds
        """
        from time import time, sleep,perf_counter
        print(t,dt,interupt)
        t1 =  perf_counter()
        intsleep(t = t,dt = dt, interupt = interupt)
        t2 = perf_counter()
        dt = t2-t1
        print(dt)
    def interupt():
        """
        return value of a global variable flag
        """
        global flag
        return flag
    flag = True
    print('test_psleep(0.010) # in seconds')
    print('test_intsleep(0.10,0.01,interupt) # in seconds')
    print('intsleep(0.10,0.1) # in seconds')
