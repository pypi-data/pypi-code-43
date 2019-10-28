class TimeUtils():

    @staticmethod
    def convert_timestamp_to_millis(timestamp):
        return int(round(timestamp * 1000.))