import logging
import time


class StopWatch:
    def __init__(self, logger, pattern=None):
        self.start = None
        self.end = None
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger('stopwatch')
            self.logger.setLevel(logging.INFO)

        if pattern:
            self.pattern = pattern
        else:
            self.pattern = 'Elapsed time: %s ms'

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        self.end = time.time()
        self.logger.info(self.pattern, self.duration)

    @property
    def duration(self):
        return round((self.end - self.start) * 1000, 2)
