# -*- coding:utf-8 -*-
# @Author cc
# @TIME 2019/10/15 23:12
from gevent.pool import Pool
from gevent import monkey
import time
monkey.patch_all()

class GeventPoolExecutor(Pool):
    def __init__(self, size=None, greenlet_class=None):
        super().__init__(size, greenlet_class)

    def submit(self, *args, **kwargs):
        self.spawn(*args, **kwargs)

    def shutdown(self):
        self.join()

def print_msg(a):
    print(a)
    time.sleep(5)

if __name__ == '__main__':
    gevent_pool = GeventPoolExecutor(50)
    for i in range(1000):
        gevent_pool.submit(print_msg,i)
    gevent_pool.shutdown()