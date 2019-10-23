#!/usr/bin/env python3
from tqdm import tqdm
import threading, time
import diskcache as dc
from datetime import datetime 
done = False
def go_progress(seconds):
    global done
    with tqdm(total=400, bar_format = "{l_bar}{bar}") as pbar:
        for i in range(0, 401):
            time.sleep(seconds * 0.0025)
            if done:
                break
            if i < 396:
                pbar.update(1)
        pbar.update(400 - i - 1)
        time.sleep(1)

def common(whole_key, func, *args, **kwargs):
        global done
        done = False
        cache = dc.Cache('tmp')
        
        try:
                (seconds, times) = cache[whole_key]
                if seconds > 1:
                        p = threading.Thread(target=go_progress, args=((int(seconds / times)),))
                        p.start()
        except:
                (seconds, times) = (0, 0)
                
        start = datetime.now()
        func(*args, **kwargs)
        end = datetime.now()
        done = True

        seconds += (end - start).seconds
        times += 1
                
        cache[whole_key] = (seconds, times)

def progressor(func):
        def wrapper(*args, **kwargs):
             whole_key = func.__name__
             common(whole_key, func, *args, **kwargs)
        return wrapper


@progressor
def long_function(s):
        time.sleep(s)

if __name__ == "__main__":
        long_function(3)
        
