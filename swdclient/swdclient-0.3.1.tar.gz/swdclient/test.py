from swdclient import *
# swd = SwdClient()
# swd.start("192.168.30.185")
# print(swd.get_data())
# swd.control(speed=1.2)

start("192.168.30.185")

import time
time.sleep(1)
print(get_data())
# control(speed=1.2)