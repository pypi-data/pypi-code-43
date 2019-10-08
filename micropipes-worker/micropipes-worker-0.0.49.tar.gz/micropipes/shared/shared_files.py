from enum import Enum
import os

'''
hourDir="${SHARED_DIR}"/h
dayDir="${SHARED_DIR}"/d
weekDir="${SHARED_DIR}"/w
monthDir="${SHARED_DIR}"/m
permanentDir="${SHARED_DIR}"/p
'''

ENV_SHARED_DIR = "SHARED_DIR"

class Duration(Enum):
    HOUR = "h"
    DAY = "d"
    WEEK = "w"
    MONTH = "m"
    PERMANENT = "p"


STR_TO_DURATION = {
    'h': Duration.HOUR,
    'd': Duration.DAY,
    'w': Duration.WEEK,
    'm': Duration.MONTH,
    'p': Duration.PERMANENT
}


def get_shared_dir(duration, job_id):
    if not isinstance(duration,Duration):
        raise TypeError('duration must be an instance of Duration Enum')
    if not ENV_SHARED_DIR in os.environ:
        raise EnvironmentError('{} must be set as environemt variable'.format(ENV_SHARED_DIR))
    base =  os.environ[ENV_SHARED_DIR]
    return os.path.join(base,duration.value, job_id)


if __name__ == "__main__":

    values = ["nic", Duration.HOUR, Duration.PERMANENT]
    for v in values:
        try:
            print(get_shared_dir(v, '1'))
        except Exception as e:
            print(e)
    os.environ[ENV_SHARED_DIR] = "c:\\users\\tmp"
    for v in values:
        try:
            print(get_shared_dir(v,'2'))
        except Exception as e:
            print(e)
