# -*- coding: UTF-8 -*-
import datetime
import time
import types
import random

from apscheduler.executors.gevent import GeventExecutor
from apscheduler.executors.asyncio import AsyncIOExecutor
from decorator import decorator
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

"""
    异步重复执行单次原子操作，直到没有错误发生或通过了验证函数
    适用于flask，提供了对app上下文的完整支持
    使用实例：
    from APSmission import asyn_repeat

    def test_aps():
        my_cache.sadd('aps test', str(time.time()) + str(random.random()))

    def test_verify():
        return True

    asyn_repeat(test_aps, app=app, verification=test_verify)
    详细的使用说明见下面的参数说明
"""


def async_retry(verification=None, listener=None, interval=5, count=10, app=None):
    """
    action函数会重复执行count次，每次间隔interval秒，直到最大运行次数结束，或通过检验
    如果verification函数为None，则检验标准为是否出错
    如果verification函数不为None，则检验标准为verification函数的返回值
    执行action时会忽略一切错误（有错误也不打印出来），需要自己在action或者verification函数中添加日志，verification出错会直接报出来
    :param verification:验证函数，应该是一个只会返回True or False的函数，与被装饰函数共用参数
    :param listener: 监听函数，如果函数最后都没有通过验证，则执行这个。与被装饰函数共用参数
    :param interval:函数运行的时间间隔，默认为5s
    :param count:函数运行的最大次数，默认为10
    :param app:flask中的app
    :return:None
    """

    class APSMission:

        def __init__(self=None, action=None, verification=None, listener=None, interval=5, count=10, args=None, kwargs=None,
                     app=None):
            self.interval = interval
            self.count = count
            self.action = action
            self.verification = verification
            self.listener = listener
            self.args = args or tuple()
            self.kwargs = kwargs or dict()
            self.app = app
            self.job_id = str(time.time()) + str(random.random())

            if not hasattr(self.app, 'apscheduler'):
                # print 'app don\'t has apscheduler'
                self._init_aps()

        def _init_aps(self):
            scheduler = GeventScheduler(timezone='Asia/Shanghai',
                                        executors={
                                            'default': GeventExecutor(),
                                        },
                                        job_defaults={
                                            'coalesce': False,
                                            'max_instances': 1000000,
                                            'misfire_grace_time': 10000
                                        })
            scheduler.start()
            self.app.apscheduler = scheduler

        def run(self):
            self._add_job_to_aps()

        def _add_job_to_aps(self):
            self.app.apscheduler.add_job(func=self._repeat_job, trigger='date', id=self.job_id)
            """
            For dev
            trigger=None, args=None, kwargs=None, id=None, name=None,
                misfire_grace_time=undefined, coalesce=undefined, max_instances=undefined,
                next_run_time=undefined, jobstore='default', executor='default',
                replace_existing=False
            """

        def _repeat_job(self):  # 重复job
            finish = False
            for i in range(self.count):
                with self.app.app_context():
                    if self._run_action():  # _no_error/_pass_verify
                        finish = True
                        break
                time.sleep(self.interval)
            if not finish:
                print('**asyn repeat fail** function "{}" with args {} kwargs {} finally failed'.
                      format(self.action.__name__, self.args, self.kwargs))
                self.listener(*self.args, **self.kwargs)

        def _run_action(self):  # 执行action
            finish = False
            try:
                self.action(*self.args, **self.kwargs)
            except Exception as e:
                pass
            else:
                if self.verification:
                    if self.verification(*self.args, **self.kwargs):
                        finish = True
                else:
                    finish = True
            return finish

    @decorator
    def inner(func, *args, **kwargs):
        if app is None:
            raise Exception('The "app" parameter is best to be given')
        controller = APSMission(action=func, verification=verification, listener=listener, args=args, kwargs=kwargs,
                                interval=interval, count=count, app=app)
        controller.run()
        del controller

    return inner
