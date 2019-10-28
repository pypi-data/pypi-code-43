# -*- coding: utf-8 -*-
import asyncio
import time
from collections import deque
import ray
from ray.experimental import async_api
from skydl.ray.experimental.ray_ring_buffer import RayRingBuffer



ray.init()

######
q = RayRingBuffer(2)
print(q)


@ray.remote
def exec_forever():
    try:
        while(True):
            q.put("aaa")
            print("exec_forever put...")
            time.sleep(1)
    except:
        print("exec_forever-***")
    return {'exec_forever-key1': [q.get()]}


@ray.remote
def exec_once():
    try:
        q.put("a1")
        q.put("b")
        q.put("c")
        q.put("d")
    except:
        print("***")
    return {'key1': [q.get()]}

object_id = exec_once.remote()
future = async_api.as_future(object_id)
print(object_id)
result = asyncio.get_event_loop().run_until_complete(future)  # {'key1': ['value']}
print(result)


tm1 = time.time()
rb = deque(maxlen=1000)
for i in range(int(1e6)):
    rb.append(i)
print(list(rb)[:10])
rb.clear()
tm2 = time.time()
print("使用封装的ringbuffer执行时间；{:.2f}seconds".format(tm2 - tm1))
