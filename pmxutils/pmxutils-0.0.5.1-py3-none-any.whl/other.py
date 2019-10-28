"""Non-Mathematical Functions and Classes"""
import itertools
import threading
import time
import sys

def profile(function):
    """Time profiler. Prints out the elapsed time during function execution"""
    start_time = time.time()
    def wrapper(*args):
        result = function(*args)
        elapsed_time = round(time.time() - start_time, 4)
        print(f"""____________________
{function.__name__}
    Time Elapsed: {elapsed_time}""")
        return result
    return wrapper

class loading():
    """Loading class"""
    def start(self, flavor="loading"):
        """Starts a loading sequence"""
        self.done=False
        self.flavor = flavor
        t = threading.Thread(target=self.animate, daemon=True)
        t.start()

    def stop(self):
        "Stops a loading sequence"
        self.done=True
        time.sleep(0.2)

    def animate(self):
        "DO NOT USE, internal function"
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self.done:
                break
            sys.stdout.write(f'\r{self.flavor} ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rDone!     ')
        sys.stdout.flush()
        sys.stdout.write("\n")

