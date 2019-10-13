import time
from datetime import datetime

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_RUNNING

from com.fw.base.base_log import logger
from com.fw.utils.time_utils import TimeUtils, DateType


class Task(object):
    '''
    #表示2017年3月22日17时19分07秒执行该程序
    sched.add_job(my_job, 'cron', year=2017,month = 03,day = 22,hour = 17,minute = 19,second = 07)



    #表示任务在6,7,8,11,12月份的第三个星期五的00:00,01:00,02:00,03:00 执行该程序

    sched.add_job(my_job, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')



    #表示从星期一到星期五5:30（AM）直到2014-05-30 00:00:00

    sched.add_job(my_job(), 'cron', day_of_week='mon-fri', hour=5, minute=30,end_date='2014-05-30')



    #表示每5秒执行该程序一次，相当于interval 间隔调度中seconds = 5

    sched.add_job(my_job, 'cron',second = '*/5')




    # The job will be executed on November 6th, 2009

    sched.add_job(my_job, 'date', run_date=date(2009, 11, 6), args=['text'])

    # The job will be executed on November 6th, 2009 at 16:30:05

    sched.add_job(my_job, 'date', run_date=datetime(2009, 11, 6, 16, 30, 5), args=['text'])

    '''

    def __init__(self):
        job_defaults = {
            'coalesce': False,  # 默认情况下关闭新的作业
            'max_instances': 300  # 设置调度程序将同时运行的特定作业的最大实例数3
        }

        self.scheduler = BackgroundScheduler(job_defaults=job_defaults)
        self.scheduler.start()
        logger.info("-----任务中心启动成功------")

    def add_task_interval(self, func, args=[], kwargs={}, year=None, month=None, day=None, hour=None,
                          second=None, id=None):

        self.scheduler.add_job(func, 'cron', args=args, kwargs=kwargs, year=year, month=month, day=day,
                               hour=hour, second=second, id=id, timezone=pytz.timezone('Asia/Shanghai')
                               )

        if self.scheduler.state != STATE_RUNNING:
            logger.info(" apscheduler 重新激活")
            self.scheduler.start()

    def add_task_time(self, func, run_date: datetime, args=[], kwargs={}, id=None):
        self.scheduler.add_job(func, 'date', args=args, kwargs=kwargs, run_date=run_date, id=id,
                               timezone=pytz.timezone('Asia/Shanghai'))

        if self.scheduler.state != STATE_RUNNING:
            logger.info(" apscheduler 重新激活")
            self.scheduler.start()

    def remove_task(self, id):
        try:
            self.scheduler.remove_job(id)
        except Exception as e:
            logger.exception(e)
            logger.error("删除任务出错:{}".format(id))


task = Task()
