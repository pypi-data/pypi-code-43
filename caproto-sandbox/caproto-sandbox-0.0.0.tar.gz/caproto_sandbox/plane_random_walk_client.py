#!/usr/bin/env python3
from caproto.threading.client import Context
from caproto.sync.client import read
ctx = Context()  # a client Context used to explore the servers below
#a, b, c = ctx.get_pvs('simple:A', 'simple:B', 'simple:C')
#mocka, mockb, mockc = ctx.get_pvs('mock:A', 'mock:B', 'mock:C')
#integer ,float ,vector, string, dict, t, dt = ctx.get_pvs('simple:integer', 'simple:float', 'simple:vector', 'simple:string','simple:pickle','simple:t','simple:dt')
from caproto.threading.client import Context
ctx = Context()
dt,x,y = ctx.get_pvs('2d_random_walk:dt','2d_random_walk:x','2d_random_walk:y')
