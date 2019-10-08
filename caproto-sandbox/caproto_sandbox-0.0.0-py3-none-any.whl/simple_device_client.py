#!/usr/bin/env python3
from caproto.threading.client import Context
ctx = Context()
dt,t,cpu,memory,battery = ctx.get_pvs('simple:dt','simple:TIME','simple:CPU','simple:MEMORY','simple:BATTERY')
