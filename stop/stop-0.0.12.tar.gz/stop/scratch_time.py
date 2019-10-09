import time

class Time:
    def __init__(self):
        self._timer = time.time()

    def timer(self):
        return time.time() - self._timer()

    def reset_timer(self):
        self._timer = time.time()

    def days_since_2000(self):
        pass

    def year(self):
        return self._get_time('year')

    def month(self):
        return self._get_time('month')

    def day(self):
        return self._get_time('day')

    def hour(self):
        return self._get_time('hour')

    def minute(self):
        return self._get_time('minute')

    def second(self):
        return self._get_time('second')

    def _get_time(self, option):
        keys = {
            'year': '%Y',
            'month': '%m',
            'day': '%d',
            'hour': '%H',
            'minute': '%M',
            'second': '%S'
        }
        return time.strftime(keys[option])