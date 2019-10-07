import os
import time
import portalocker

flags = portalocker.LOCK_EX

path = "/tmp"

file_desc = os.open(path, os.O_RDONLY)
print(file_desc)

lock = portalocker.Lock(filename=path)
lock.acquire()

while True:
    print(f"lock")
    time.sleep(1)
