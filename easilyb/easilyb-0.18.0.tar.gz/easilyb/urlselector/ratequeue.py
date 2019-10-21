from time import time as _time
try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading
from . import UrlItem
import logging
logger = logging.getLogger(__name__)

class RateQueue:
    """Create a queue object with a given maximum size.

    If maxsize is <= 0, the queue size is infinite.
    """
    def __init__(self, maxsize=0, maxrate=0.01, domainrate=None, limit=None):
        self.maxsize = maxsize
        self.mutex = _threading.Lock()
        self.not_empty = _threading.Condition(self.mutex)
        self.not_full = _threading.Condition(self.mutex)
        self.all_tasks_done = _threading.Condition(self.mutex)
        self.unfinished_tasks = 0
        self.seen = set()
        self.notseen = set()
        self.limit = limit
        self._count = 0
        self.maxrate = maxrate
        self.domainrate = domainrate
        self._lasttimes = dict()
        self._lasttime = -1


    def task_done(self):
        """Indicate that a formerly enqueued task is complete.

        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        for every item that had been put() into the queue).

        Raises a ValueError if called more times than there were items
        placed in the queue.
        """
        self.all_tasks_done.acquire()
        try:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
        finally:
            self.all_tasks_done.release()

    def join(self):
        """Blocks until all items in the Queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved and all work on it is complete.

        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        self.all_tasks_done.acquire()
        try:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()
        finally:
            self.all_tasks_done.release()

    def qsize(self):
        """Return the approximate size of the queue (not reliable!)."""
        self.mutex.acquire()
        n = self._qsize()
        self.mutex.release()
        return n

    def empty(self):
        """Return True if the queue is empty, False otherwise (not reliable!)."""
        self.mutex.acquire()
        n = not self._qsize()
        self.mutex.release()
        return n

    def full(self):
        """Return True if the queue is full, False otherwise (not reliable!)."""
        self.mutex.acquire()
        n = 0 < self.maxsize == self._qsize()
        self.mutex.release()
        return n

    def put(self, item, block=True, timeout=None):
        """Put an item into the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a positive number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).
        """
        self.not_full.acquire()
        try:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() == self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() == self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a positive number")
                else:
                    endtime = _time() + timeout
                    while self._qsize() == self.maxsize:
                        remaining = endtime - _time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
        finally:
            self.not_full.release()

    def put_nowait(self, item):
        """Put an item into the queue without blocking.

        Only enqueue the item if a free slot is immediately available.
        Otherwise raise the Full exception.
        """
        return self.put(item, False)

    def get(self, block=True, timeout=None):
        return self.pop(block, timeout)

    def pop(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a positive number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """
        self.not_empty.acquire()
        try:
            if not block:
                if not self._qsize():
                    raise Empty
                mindists = self._calc_mindists()
                t1 = _time()
                if self._check_mindists(mindists, t1) is not None:
                    raise NoCandidate

            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
                while True:
                    mindists = self._calc_mindists()
                    t1 = _time()
                    wait = self._check_mindists(mindists, t1)
                    if wait  is None:
                        break
                    self.not_empty.wait(wait)

            elif timeout < 0:
                raise ValueError("'timeout' must be a positive number")
            else:
                endtime = _time() + timeout
                while not self._qsize():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
                while True:
                    mindists = self._calc_mindists()
                    t1 = _time()
                    wait = self._check_mindists(mindists, t1)
                    if wait  is None:
                        break
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise NoCandidate
                    self.not_empty.wait(min(wait,remaining))
            item = self._get(t1, mindists)
            self.not_full.notify()
            return item
        finally:
            self.not_empty.release()

    def get_nowait(self):
        """Remove and return an item from the queue without blocking.

        Only get an item if one is immediately available. Otherwise
        raise the Empty exception.
        """
        return self.get(False)


    def _qsize(self, len=len):
        return len(self.notseen)

    # Put a new item in the queue
    def _put(self, item):
        item = UrlItem(item)
        # check duplicates
        if item in self.seen or item in self.notseen:
            return
        self.notseen.add(item)

    # Get an item from the queue
    def _get(self, t1, mindists):

        curitem = None
        for url, dist in mindists:
            if self._checkrate(url, t1) is None:
                curitem = url
                self._updaterate(url, t1)
                self.notseen.remove(curitem)
                self.seen.add(curitem)
                break
        assert curitem is not None
        print(( self._count))
        if self.limit: #TODO: this code is not tested and have problems while threading
            self._count +=1
            if self._count >= self.limit:
                logger.info("Limit reached: %d", self._count)
                self.unfinished_tasks = 0
                self.seen = set()
                self.notseen = set()
                self.maxsize = 0

        return curitem.url_original

    def _calc_mindists(self):
        mindists = list()
        for n in self.notseen:
            sdist = -1
            for s in self.seen:
                dist = s.dist(n)
                if sdist == -1 or dist < sdist:
                    sdist = dist
            mindists.append((n, sdist))
        mindists.sort(key=lambda x:x[1], reverse=True)
        return mindists

    def _check_mindists(self, mindists, t1):
        minwait = -1
        for url, dist in mindists:
            wait = self._checkrate(url, t1)
            if wait is None:
                return None
            if minwait == -1 or wait < minwait:
                minwait = wait
        assert  minwait > -1
        return minwait

    def _checkrate(self, url, t1):
        if self.domainrate is None or url.host not in self._lasttimes or t1 - self._lasttimes[url.host] > self.domainrate:
            domainwait = -1
        else:
            domainwait = self.domainrate - (t1 - self._lasttimes[url.host])
        interval = t1 - self._lasttime
        if self.maxrate is None or interval > self.maxrate:
            maxwait = -1
        else:
            maxwait = self.maxrate - interval
        wait = max(domainwait, maxwait)
        if wait <=0:
            return None
        return wait


    def _updaterate(self, url, t1):
        self._lasttime = t1
        self._lasttimes[url.host] = t1

    def __len__(self):
        return self.qsize()

class Empty(Exception):
    "Exception raised by Queue.get(block=0)/get_nowait()."
    pass

class NoCandidate(Exception):
    "Exception raised by Queue.get(block=0)/get_nowait()."
    pass

class Full(Exception):
    "Exception raised by Queue.put(block=0)/put_nowait()."
    pass
