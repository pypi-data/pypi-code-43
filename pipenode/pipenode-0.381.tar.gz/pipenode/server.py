import os
import functools
import asyncio
import concurrent.futures
from . import endpoints, tasks

try:
    from .model import get_or_create
except:
    pass
try:
    from utils.logger import RotatingLogger
    logger = RotatingLogger().logger
except:
    from .log import logger
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


__all__ = ['Server', 'Group']


class Server(object):
    """
    """

    def __init__(self, run_type=None, max_workers=1, **kwargs):
        if os.environ.get('RUN_MODE') == 'apscheduler':
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        else:
            self._loop = asyncio.get_event_loop()
        self._worker_executor_pool = None
        self._group_map = {}
        self.bloking_tasks = []
        if run_type == "coroutine":
            pass
        elif run_type == "thread":
            if self._worker_executor_pool is None:
                self._worker_executor_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        elif run_type == "process":
            if self._worker_executor_pool is None:
                self._worker_executor_pool = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        else:
            pass

    def add_group(self, name, concurrency, task_queue_size=None):
        """注册一个group
        """
        assert name not in self._group_map, "group '%s' already exist" % name
        if concurrency <= 0:
            raise ValueError("concurrency must be greater than 0")
        self._group_map[name] = Group(concurrency, self._loop, task_queue_size or concurrency)
        return self._group_map[name]

    async def gen_func(self, func, **kwargs):
        try:
            if kwargs.get('job_store'):
                self.job_store = kwargs.pop('job_store')
                get_or_create(self.job_store)
            await self._loop.run_in_executor(self._worker_executor_pool, functools.partial(func, **kwargs))
        except Exception as exc:
            logger.error("Error occur in handle", exc_info=exc)

    def add_worker(self, func, **kwargs):
        self.bloking_tasks.append(self.gen_func(func, **kwargs))

    def add_routine_worker(self, worker, interval=None, immediately=False, day: int = None,
                           weekday: int = None, hour: int = None, minute: int = None, *args, **kw):
        """
        run work with interval
        unit of interval is minute
        day range: 1-31
        weekday range: 0-6
        hour range: 0-23
        minute range: 0-59
        """
        run_type = None
        if interval:
            run_type = 'interval'
            interval = int(interval * 60)
        elif any(map(lambda x: x is not None, [day, weekday, hour, minute])):
            run_type = 'crontab'
        else:
            assert ValueError("must select one of modes: interval, crontab")

        @functools.wraps(worker)
        async def wraper():
            while True:
                if run_type == 'interval':
                    if not immediately:
                        await asyncio.sleep(interval)
                    try:
                        await worker(*args, **kw)
                    except Exception as exc:
                        logger.error("Routine worker error", exc_info=(
                            type(exc), exc, exc.__traceback__))
                        exc.__traceback__ = None
                    if immediately:
                        await asyncio.sleep(interval)
                else:
                    if not immediately:
                        await asyncio.sleep(60)
                    time_now = datetime.now()
                    match = True
                    for _, v in zip(('day', 'weekday', 'hour', 'minute'), (day, weekday, hour, minute)):
                        if v is not None:
                            if _ == 'day' and time_now.day != v:
                                match = False
                                break
                            if _ == 'weekday' and time_now.weekday() != v:
                                match = False
                                break
                            if _ == 'hour' and time_now.hour != v:
                                match = False
                                break
                            if _ == 'minute' and time_now.minute != v:
                                match = False
                                break
                    if match:
                        try:
                            await worker(*args, **kw)
                        except Exception as exc:
                            logger.error("Routine worker error", exc_info=(
                                type(exc), exc, exc.__traceback__))
                            exc.__traceback__ = None
                    if immediately:
                        await asyncio.sleep(60)

        self._loop.create_task(wraper())

    def run_executor(self):
        self._loop.run_until_complete(asyncio.gather(*self.bloking_tasks))

    def run(self, task=None):
        """Start the server
        run_until_complete等到 future 完成，run_until_complete 也就返回了
        run_forever 会一直运行,直到stop被调用
        """
        self._loop.run_forever()
        # self._loop.run_until_complete(asyncio.gather(*task))


class Group(object):
    """
    """
    MAX_INTERVAL = 0.001

    def __init__(self, concurrency, loop, task_queue_size):
        """
        :param concurrency:
        :param loop: server loop
        :param task_queue_size:
        """
        self._loop = loop
        self._concurrency = concurrency
        self._task_q = asyncio.Queue(task_queue_size, loop=self._loop)
        self._running_cnt = 0
        self._bulking_cnt = 0
        self._outendpoint_map = {}
        self._output_name_map = {}
        self._endpoint_map = {}
        self._worker_executor = None

    def stats_running_cnt(self):
        """任务次数
        """
        self._running_cnt += 1
        self._bulking_cnt += 1

    def register_input_endpoint(self, name, input_endpoint, point_name=None, interval=0):
        """group注册输入端点
        :param name: 'input'
        :param input_endpoint: ''
        """
        assert endpoints.isInputEndpoint(input_endpoint), "is not inputendpoint"
        self._add_endpoint(name)
        self._loop.create_task(self.fetch_task(name, input_endpoint, point_name=point_name, interval=interval))

    def register_output_endpoint(self, name, output_endpoint, params=None, buffer_size=None):
        """group注册输出端点
        """
        assert endpoints.isOutputEndpoint(output_endpoint), "is not outputendpoint"
        self._add_endpoint(name)
        if output_endpoint not in self._outendpoint_map:
            self._outendpoint_map[output_endpoint] = {}
        if params not in self._outendpoint_map[output_endpoint]:
            result_q = asyncio.Queue(buffer_size if buffer_size else self._concurrency, loop=self._loop)
            self._outendpoint_map[output_endpoint][params] = result_q
            self._loop.create_task(self.send_result(result_q, output_endpoint))
        self._output_name_map[name] = (params, self._outendpoint_map[output_endpoint][params])

    def _add_endpoint(self, name):
        """添加端点
        """
        assert name not in self._endpoint_map, "endpoint '%s' already exist" % name
        self._endpoint_map[name] = None

    def suspend_endpoint(self, name):
        """暂停端点
        """
        assert name in self._endpoint_map, "corresponding endpoint isn't bound to the group"
        if self._endpoint_map.get(name) is None:
            self._endpoint_map[name] = asyncio.Event()
        self._endpoint_map[name].clear()

    def resume_endpoint(self, name):
        """恢复端点
        """
        assert name in self._endpoint_map, "corresponding endpoint isn't bound to the group"
        if self._endpoint_map.get(name) is not None:
            self._endpoint_map[name].set()
            self._endpoint_map[name] = None

    async def worker_put(self, result):
        for task in result:
            if isinstance(task, tasks.Task):
                name = task.get_to()
                params, result_q = self._output_name_map[name]
                await result_q.put((params, task))
            else:
                for res in task:
                    name = res.get_to()
                    params, result_q = self._output_name_map[name]
                    await result_q.put((params, res))

    def server_side(self):
        while True:
            if self.event.is_set:
                get_or_create(self.job_store)
                self.event.wait()
                self._bulking_cnt = 0

    def gen_func(self, func, run_type="coroutine", **kwargs):
        """将loop中，func将运行
        https://docs.python.org/3/library/asyncio-eventloop.html
        """

        @functools.wraps(func)
        async def worker():
            import threading
            self.event = threading.Event()
            self.event.clear()
            if kwargs.get('job_store'):
                self.job_store = kwargs.pop('job_store')
                thread = threading.Thread(target=self.server_side, daemon=True)
                thread.start()
                self.event.set()
            number = kwargs.get('number', 1)
            if run_type == 'coroutine':
                coro = asyncio.coroutines.coroutine(func)
            while True:
                task_ls = []
                self.event.clear()
                for _ in range(number):
                    task = await self._task_q.get()
                    task_ls.append(task)
                # logger.info('pipenode genfunc task ls: %s' % len(task_ls))
                try:
                    if run_type == 'coroutine':
                        results = await coro(self, task_ls, **kwargs)
                    else:
                        blocking_tasks = []
                        future = await self._loop.run_in_executor(self._worker_executor,
                                                                  functools.partial(func, self, task_ls,
                                                                                    **kwargs))
                        blocking_tasks.append(future)
                        completed, pending = await asyncio.wait(blocking_tasks)
                        results = [t.result() for t in completed]
                except Exception as exc:
                    exc_info = (type(exc), exc, exc.__traceback__)
                    logger.error("Error occur in handle", exc_info=exc_info)
                    exc.__traceback__ = None
                else:
                    if isinstance(results, list):
                        if results:
                            await self.worker_put(results)
                        self.stats_running_cnt()
                        if self._bulking_cnt == 100:
                            logger.info('_bulking_cnt event: %s' % self._bulking_cnt)
                            self.event.set()
        return worker

    def set_handle(self, handle, run_type="coroutine", **kwargs):
        """设置work的group handle,对于每个work，group将使用handle创建工作程序。
        handle：coroutine，thread，process，
        """
        if run_type == "coroutine":
            pass
        elif run_type == "thread":
            if self._worker_executor is None:
                self._worker_executor = concurrent.futures.ThreadPoolExecutor(max_workers=self._concurrency)
        elif run_type == "process":
            if self._worker_executor is None:
                self._worker_executor = concurrent.futures.ProcessPoolExecutor(max_workers=self._concurrency)
        else:
            raise ValueError("the value of run_type is not supported")
        booktest_task = []
        for _ in range(self._concurrency):
            worker = self.gen_func(handle, run_type, **kwargs)
            self._loop.create_task(worker())

    async def fetch_task(self, name, input_endpoint, point_name=None, interval=0):
        """从input_endpoint获取任务，并将其放入任务 _task_q。
                      如果input_endpoint不支持coroutine，则执行者在线程中。
        """
        is_coroutine = endpoints.isCoroutineInputEndpoint(input_endpoint)
        if not is_coroutine:
            executor = concurrent.futures.ThreadPoolExecutor(1)
        while True:
            if self._endpoint_map[name] is not None:
                await self._endpoint_map[name].wait()
            if interval:
                await asyncio.sleep(interval)
            if is_coroutine:
                task = await input_endpoint.get(point_name)
            else:
                future = self._loop.run_in_executor(executor, input_endpoint.get, point_name)
                task = await future
            task.set_from(name)
            await self._task_q.put(task)

    async def send_result(self, result_q, output_endpoint):
        """从results_q 中获取任务，并将其放入output_endpoint。
                      如果output_endpoint不支持coroutine，则执行者在线程中。
        """
        is_coroutine = endpoints.isCoroutineOutputEndpoint(output_endpoint)
        if not is_coroutine:
            executor = concurrent.futures.ThreadPoolExecutor(1)
        while True:
            task_ls = []
            task = await result_q.get()
            task_ls.append(task)

            while not result_q.empty():
                task = await result_q.get()
                task_ls.append(task)
            if is_coroutine:
                await output_endpoint.put(task_ls)
            else:
                for _, task in task_ls:
                    await task.confirm()
                future = self._loop.run_in_executor(executor, output_endpoint.put, task_ls)
                await future
