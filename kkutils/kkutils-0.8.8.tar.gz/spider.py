#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-05 17:21:17
'''
import asyncio
import collections
import copy
import hashlib
import inspect
import pickle
import sys
import types
import urllib.parse
from asyncio import Queue
from asyncio.locks import Lock
from concurrent.futures._base import CancelledError
from functools import partial
from importlib import import_module
from signal import SIGINT
from signal import SIGTERM

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import Config
from utils import Logger
from utils import Redis
from utils import Request


def sched(trigger, **trigger_kwargs):
    def wrapper(func):
        func._trigger = trigger
        func._trigger_kwargs = trigger_kwargs
        return func
    return wrapper


class BaseChecker:

    def __init__(self, retries=3):
        self.retries = retries
        self.lock = Lock()

    def __getattr__(self, key):
        def func(*args, **kwargs):
            return False
        return func

    async def __call__(self, key):
        with await self.lock:
            if self.check('succeed', key) or self.check('failed', key) or self.check('running', key):
                return False
            if self.incr(key) < self.retries:
                self.add('running', key)
                return True
            else:
                self.add('failed', key)
                return False


class MemoryChecker(BaseChecker):

    def __init__(self, retries=3):
        super().__init__(retries=retries)
        self.cache = collections.defaultdict(int)
        self.storage = collections.defaultdict(set)

    def incr(self, key):
        self.cache[key] += 1
        return self.cache[key]

    def add(self, name, key):
        self.storage[name].add(key)

    def remove(self, name, key):
        if key in self.storage[name]:
            self.storage[name].remove(key)

    def check(self, name, key):
        return key in self.storage[name]


class RedisChecker(BaseChecker):

    def __init__(self, retries=3, prefix='spider'):
        super().__init__(retries=retries)
        self.prefix = prefix
        self.rd = Redis()

    def incr(self, key):
        return self.rd.hincrby(f'{self.prefix}_count', key, 1)

    def add(self, name, key):
        self.rd.sadd(f'{self.prefix}_{name}', key)

    def remove(self, name, key):
        self.rd.srem(f'{self.prefix}_{name}', key)

    def check(self, name, key):
        return self.rd.sismember(f'{self.prefix}_{name}', key)


class SpiderMeta(type):

    def __new__(cls, name, bases, attrs):
        sched_jobs = []
        for job in attrs.values():
            if inspect.isfunction(job) and getattr(job, '_trigger', None):
                sched_jobs.append(job)
        newcls = type.__new__(cls, name, bases, attrs)
        newcls._sched_jobs = sched_jobs
        return newcls


class Spider(metaclass=SpiderMeta):

    urls = [f'https://www.baidu.com']

    def __init__(self,
                 workers=50,
                 timeout=60,
                 retries=3,
                 checker='MemoryChecker',
                 prefix='spider',
                 splash=False,
                 splash_url='http://localhost:8050/render.html',
                 **kwargs):
        self.workers = workers
        self.splash = splash
        self.splash_url = splash_url
        self.logger = Logger(name='tornado.application')
        self.http = Request(lib='tornado', retry=3, max_clients=workers, timeout=timeout)
        self.queue = Queue()
        if checker == 'RedisChecker':
            self.checker = RedisChecker(retries=retries, prefix=prefix)
        elif checker == 'MemoryChecker':
            self.checker = MemoryChecker(retries=retries)
        else:
            self.checker = BaseChecker()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.sched = AsyncIOScheduler()
        self.loop = asyncio.get_event_loop()
        if hasattr(self, 'init'):
            ret = self.init()
            if isinstance(ret, types.CoroutineType):
                self.loop.run_until_complete(ret)

    def key(self, *args):
        return hashlib.md5(pickle.dumps(args)).hexdigest()

    async def crawl(self, url, callback, *args, **kwargs):
        if await self.checker(self.key(url, args, kwargs)):
            await self.queue.put((url, callback, args, kwargs))

    async def parse(self, resp):
        self.logger.info(f'{resp.code}: {resp.url}')

    # @sched('interval', seconds=3)
    async def producer(self):
        for url in self.urls:
            await self.crawl(url, self.parse)

    async def consumer(self):
        while True:
            try:
                url, callback, args, kwargs = await self.queue.get()
                if self.splash:
                    data = copy.deepcopy(kwargs)
                    data['url'] = url
                    data.setdefault('http_method', data.pop('method', 'GET'))
                    data.setdefault('wait', 1)
                    if 'lua_source' in data:
                        ret = urllib.parse.urlparse(self.splash_url)
                        splash_url = f'{ret.scheme}://{ret.netloc}/execute'
                        resp = await self.http.post(splash_url, data=data, json=True)
                    else:
                        resp = await self.http.post(self.splash_url, data=data, json=True)
                else:
                    resp = await self.http.request(url, **kwargs)
                self.logger.info(f'queue: {self.queue.qsize()}, url: {url} {resp.code} {resp.reason}')

                key = self.key(url, args, kwargs)
                self.checker.remove('running', key)

                codes = kwargs.get('codes', [])
                if (codes and resp.code in codes) or (not codes and 200 <= resp.code < 300):
                    try:
                        doc = callback(resp, *args)
                        if isinstance(doc, types.CoroutineType):
                            doc = await doc
                        self.checker.add('succeed', key)
                    except Exception as e:
                        self.logger.exception(e)
                        await self.crawl(url, callback, *args, **kwargs)
                else:
                    if 400 <= resp.code < 500:
                        self.checker.add('failed', key)
                    else:
                        await self.crawl(url, callback, *args, **kwargs)
            except CancelledError:
                return self.logger.error(f'Cancelled consumer')
            except Exception as e:
                self.logger.exception(f'{url}: {e}')
                self.queue.task_done()
            else:
                self.queue.task_done()

    async def shutdown(self, sig):
        self.logger.warning('caught {0}'.format(sig.name))
        while not self.queue.empty():
            await self.queue.get()
        tasks = list(filter(lambda task: task is not asyncio.tasks.Task.current_task(),
                            asyncio.Task.all_tasks()))
        self.logger.info(f'finished awaiting cancelled tasks: {len(tasks)}')
        list(map(lambda task: task.cancel(), tasks))
        # await asyncio.gather(*tasks, return_exceptions=True)
        self.loop.stop()

    def start(self):
        for _ in range(self.workers):
            self.loop.create_task(self.consumer())

        for sig in (SIGINT, SIGTERM):
            self.loop.add_signal_handler(sig, partial(self.loop.create_task, self.shutdown(sig)))

        if self._sched_jobs:
            self.checker = BaseChecker()
            for func in self._sched_jobs:
                function = func.__get__(self, self.__class__)
                self.sched.add_job(function, func._trigger, **func._trigger_kwargs)
                self.loop.create_task(function())
            self.sched.start()
            self.loop.run_forever()
        else:
            self.loop.run_until_complete(self.producer())
            self.loop.run_until_complete(self.queue.join())
            if hasattr(self, 'finish'):
                ret = self.finish()
                if isinstance(ret, types.CoroutineType):
                    self.loop.run_until_complete(ret)


def main():
    opt = Config({
        'workers': 30,
        'timeout': 60,
        'retries': 3,
        'checker': 'MemoryChecker',
        'prefix': 'spider',
        'splash': False,
        'splash_url': 'http://localhost:8050/render.html'
    })
    module_name, app_name = sys.argv[1].split('.')
    module = import_module(module_name)
    app = getattr(module, app_name)(**opt)
    app.start()


if __name__ == '__main__':
    main()
