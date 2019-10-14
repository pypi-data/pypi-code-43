import time
from functools import wraps
from threading import Lock

_lock_list = dict()


def synchronized(func):
    key = f"{func.__module__}.{func.__name__}"
    _lock_list[key] = Lock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        lock = _lock_list[key]
        lock.acquire()
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()

    return wrapper


def main():
    import threading
    @synchronized
    def test1(*args, **kwargs):
        time.sleep(2)
        print("test1", *args, **kwargs)

    threads = [threading.Thread(target=test1, args=(x, x * x)) for x in range(1, 199)]
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
