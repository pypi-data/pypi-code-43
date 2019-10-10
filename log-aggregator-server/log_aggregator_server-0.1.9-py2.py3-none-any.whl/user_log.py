import os
import shutil
from functools import wraps


def raise_not_found_error(log_type):
    def wrap(func):
        @wraps(func)
        def wrapped_f(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except FileNotFoundError:
                print('No {0} found. Skip {0} aggregation.'.format(log_type))
        return wrapped_f
    return wrap


@raise_not_found_error('syslog')
def sys_log(path):
    file_path = path + '/syslog'
    shutil.copy('/var/log/syslog', file_path)


@raise_not_found_error('ros log')
def ros_log(path):
    ros_path = os.environ['HOME']
    folder_path = path + '/latest'
    shutil.copytree(ros_path + '/.ros/log/latest', folder_path, symlinks=True)


@raise_not_found_error('console log')
def console_log(path):
    file_path = path + '/console_output.log'
    ros_path = os.environ['HOME']
    console_path = ros_path + '/.ros/log/console_output.log'
    shutil.copy(console_path, file_path)


def user_log_collector(path):
    sys_log(path)
    ros_log(path)
    console_log(path)

