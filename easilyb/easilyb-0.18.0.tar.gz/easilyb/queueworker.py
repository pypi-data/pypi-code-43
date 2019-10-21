import queue as Queue
import threading
import logging
import time

logger = logging.getLogger(__name__)


def _worker_wraper(i, queue_worker):
    while True:
        try:
            arg = queue_worker.get()
            logger.debug('_worker wraper i=%s arg=%s', i, arg)
            queue_worker.workerfunc(*arg)
        except KeyboardInterrupt:
            logger.info('Keyboard Interrupt', exc_info=True)
        except Exception:
            logger.exception('Exception while executing %s(%s)', str(queue_worker.workerfunc).split()[1], str(arg))
        finally:
            queue_worker.task_done()
            queue_worker.log_progress()


class QueueWorker:
    def __init__(self, workerfunc, queue=None, threads=2, log_progress=True, progress_interval=60):
        self.workerfunc = workerfunc
        self.threads = threads
        if queue is not None:
            self.queue = queue
        else:
            self.queue = Queue.Queue()
        self._init_threads()
        self.log_progress_ = log_progress
        self.progress_interval = progress_interval
        self.progress_lock = threading.Lock()
        self.lastprogress = 0
        self.total_tasks = 0

    def _init_threads(self):
        for i in range(self.threads):
            worker = threading.Thread(target=_worker_wraper, args=(i, self))
            worker.setDaemon(True)
            worker.start()

    def log_progress(self):
        if self.log_progress_:
            self.progress_lock.acquire()
            t1 = int(time.time())
            if t1 - self.lastprogress > self.progress_interval:
                logger.info('Progress: %d / %d done (%d%%)', self.queue.qsize(), self.total_tasks,
                            (100 * self.queue.qsize() / self.total_tasks))  # TODO: Log or print?
                self.lastprogress = t1
            self.progress_lock.release()

    def empty(self):
        return self.queue.empty()

    def full(self):
        return self.queue.full()

    def get(self, block=True, timeout=None):
        return self.queue.get(block=block, timeout=timeout)

    def get_nowait(self):
        return self.queue.get_nowait()

    def join(self):
        return self.queue.join()

    def put(self, item, block=True, timeout=None):
        self.total_tasks += 1
        return self.queue.put(item, block=block, timeout=timeout)

    def put_nowait(self, item):
        self.total_tasks += 1
        return self.queue.put_nowait(item)

    def put_bulk(self, lst):
        for item in lst:
            self.queue.put(item)
        self.total_tasks += len(lst)

    def qsize(self):
        return self.queue.qsize()

    def task_done(self):
        return self.queue.task_done()
