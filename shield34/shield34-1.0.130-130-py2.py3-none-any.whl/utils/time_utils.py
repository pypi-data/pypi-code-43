import datetime
import time


class TimeUtils():

    @staticmethod
    def get_current_timestamp():
        return int(round(time.time() * 1000.))

    @staticmethod
    def get_timestamp_from_datetime_str(datestr):
        try:
            utc_time = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S.%f%z")
        except Exception as e:
            utc_time = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S.%fZ")

        try:
            epoch_time = int(time.mktime(utc_time.timetuple()) * 1000)
        except:
            epoch_time = int(utc_time.timestamp() * 1000)

        return epoch_time