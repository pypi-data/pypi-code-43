from numpy import zeros, array_equal

from ubcs_auxiliary import precision_sleep, interupt_sleep
from time import time
import random

# def test_precision_sleep():
#     """ runs multiple tests with fixed maximum allowed error (1 ms) """
#     precision = 10.0e-4
#     for i in range(100):
#         sleep_t = random.randint(1,20)/1000.0
#         t1 = time(); precision_sleep(sleep_t); t2 = time(); dt = t2-t1
#         # run tests
#         assert ((dt - sleep_t) < precision)
