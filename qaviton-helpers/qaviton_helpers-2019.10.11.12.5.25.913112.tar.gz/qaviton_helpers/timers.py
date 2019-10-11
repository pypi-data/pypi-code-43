from time import time, sleep


class DynamicWait:
    """ sleep dynamically by measuring the time passed
    since t started and sleeping the
    remaining of the delay
    """

    def __init__(self, duration=None):
        self.t = time()
        self.d = duration

    def __call__(self, duration=None):
        if duration is None:
            if self.d is None:
                raise ValueError(
                    "missing duration parameter")
            duration = self.d
        t = time() - self.t
        if t < duration:
            sleep(duration - t)
