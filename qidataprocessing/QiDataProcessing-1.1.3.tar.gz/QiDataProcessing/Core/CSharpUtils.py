import datetime


class QiCore:
    @staticmethod
    def convert_c_sharp_ticks_to_linux_ticks(value):
        if value == 0:
            return value
        c_sharp_ticks1970 = 621355968000000000
        linux_ticks = (value - c_sharp_ticks1970) / 10000000
        time_zone = 28800
        linux_ticks = linux_ticks - time_zone
        return linux_ticks

    @staticmethod
    def convert_c_sharp_ticks_to_py_date_time(value):
        py_time = datetime.datetime.fromtimestamp(QiCore.convert_c_sharp_ticks_to_linux_ticks(value))
        return py_time
