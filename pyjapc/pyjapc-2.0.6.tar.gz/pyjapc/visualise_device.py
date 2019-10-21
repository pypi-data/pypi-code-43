import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import datetime
import time

start = datetime.datetime.now()
x_len = datetime.timedelta(seconds=15)
ax = plt.axes(ylim=[-1.1, 1.1], xlim=[start - x_len, start])

xs, ys = [], []
[line] = ax.plot(xs, ys, 'ob')

import threading
import numpy as np

def set_date_every_second():
    global xs, ys
    while True:
        now = datetime.datetime.now()
        xs.append(now)
        t = time.mktime(now.timetuple()) + now.microsecond / 1e6
        ys.append(t)

        # Only use the last 300 datapoints.
        xs = xs[-300:]
        ys = ys[-300:]

        line.set_xdata(xs)
        line.set_ydata(np.sin(ys))
        ax.set_xlim(now - x_len, now)
        plt.draw()
        threading.Event().wait(0.1)



t = threading.Thread(target=set_date_every_second)
t.daemon = True
t.start()

plt.show()