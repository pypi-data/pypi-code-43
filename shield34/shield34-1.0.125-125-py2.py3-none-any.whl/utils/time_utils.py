import time


class TimeUtils():

    @staticmethod
    def get_current_timestamp():
        return int(round(time.time() * 1000.))