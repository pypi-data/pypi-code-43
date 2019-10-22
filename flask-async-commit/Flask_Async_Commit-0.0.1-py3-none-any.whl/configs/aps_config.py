# -*- coding: UTF-8 -*-
from apscheduler.executors.gevent import GeventExecutor
from flask_apscheduler import APScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from common.model_helper import CacheSave
from app.log.models import DeviceManager
import os
import atexit
import fcntl

class APSConfig:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'

    SCHEDULER_SCHEDULER = {
        'default': GeventScheduler()
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 10000,
        'misfire_grace_time': 10000,
        'timezone': 'Asia/Shanghai',  # 定义时区
    }

    SCHEDULER_EXECUTORS = {
        'default': GeventExecutor()
    }

    JOBS = [
        {
            'id': 'commit_db_cache',                            # 不重复的标识
            'func': __name__ + ':CacheSave.commit_db_cache',    # 定时执行的 模块：函数
            # 'args': (1, 2),                                   # 函数的参数
            'timezone': 'Asia/Shanghai',                        # 定义时区
            'trigger': 'interval',                              # 循环调度
            'seconds': 5
        }
        # {
        #     'id': 'check_log_tables',  # 不重复的标识
        #     'func':  __name__ + ':DeviceManager.daily_check_build',  # 定时执行的 模块：函数
        #     # 'args': (1, 2),          # 函数的参数
        #     'timezone': 'Asia/Shanghai',  # 定义时区
        #     'trigger': 'interval',      # 定时执行
        #     'start_date': '2019-01-01 10:53:00',
        #     'end_date': '2020-01-01 01:00:00',
        #     'days': 1
        # }
        # {
        #     'id': 'dev test',   # 不重复的标识
        #     'func': __name__ + ':print_pid',     # 定时执行的 模块：函数
        #     # 'args': (1, 2),                 # 函数的参数
        #     'timezone': 'Asia/Shanghai',  # 定义时区
        #     'trigger': 'interval',  # 循环调度
        #     'seconds': 5,
        #     'max_instances': 100000     # 最大允许同时运行的线程数
        # }
    ]

def print_pid():
    print(os.getpid())


scheduler = APScheduler()       # 定时任务实例化
aps_config = APSConfig          # 定时任务的配置文件

def start_cache_save():
    # 解决多进程下，aps重复运行的问题
    f = open("scheduler.lock", "wb")
    print('file:', f)
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print('start aps')
        scheduler.add_job(id='commit_db_cache', func=CacheSave.commit_db_cache, trigger='interval', seconds=5, timezone='Asia/Shanghai')   # 关键就这个东西
    except Exception as e:
        print(e)
        pass

    def unlock():
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
    atexit.register(unlock)


start_cache_save()


