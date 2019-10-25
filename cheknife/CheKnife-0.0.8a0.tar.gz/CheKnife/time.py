import time


class Timer(object):
    def __init__(self):
        self.start_time = time.time()
        self.end_time = None

    def stop(self):
        self.end_time = time.time()

    def start(self):
        self.start_time = time.time()
        self.end_time = None

    @property
    def elapsed(self):
        if self.end_time:
            return self.end_time - self.start_time

    @property
    def seconds(self):
        return self.elapsed

    @property
    def minutes(self):
        return self.elapsed/60.0

    @property
    def hours(self):
        return self.elapsed/60.0

    @property
    def days(self):
        return self.elapsed/60.0
