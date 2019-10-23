#!/usr/bin/env python3
from tqdm import tqdm
import threading, time
import diskcache as dc
from datetime import datetime 
done = False
def go_progress(seconds):
    global done
    with tqdm(total=100, bar_format = "{l_bar}{bar}") as pbar:
        for i in range(0, 101):
            time.sleep(seconds * 0.01)
            if done:
                pbar.update(100 - i)
                time.sleep(1)
                break
            if i < 99:
                pbar.update(1)

def progressor_key(func):
        def wrapper(key):
                global done
                done = False
                cache = dc.Cache('tmp')
                whole_key = func.__name__ + str(key)
                if whole_key in cache:
                        (seconds, times) = cache[whole_key]
                        if seconds > 1:
                                p = threading.Thread(target=go_progress, args=((int(seconds / times)),))
                                p.start()
                else:
                        (seconds, times) = (0, 0)
                start = datetime.now()
                func(key)
                end = datetime.now()
                done = True

                seconds += (end - start).seconds
                times += 1
                        
                cache[whole_key] = (seconds, times)
        return wrapper

def progressor(func):
        def wrapper(*args, **kwargs):
                global done
                done = False
                cache = dc.Cache('tmp')
                whole_key = func.__name__
                if whole_key in cache:
                        x = cache[whole_key]
                        (seconds, times) = x
                        if seconds > 1:
                                p = threading.Thread(target=go_progress, args=((int(seconds / times)),))
                                p.start()
                else:
                        (seconds, times) = (0, 0)
                start = datetime.now()
                func(*args, **kwargs)
                end = datetime.now()
                done = True

                seconds += (end - start).seconds
                times += 1
                        
                cache[whole_key] = (seconds, times)
        return wrapper


@progressor
def long_function(s):
        time.sleep(s)

if __name__ == "__main__":
        long_function(10)
        
