import atexit
import logging
import os
import threading
import time
from abc import abstractmethod

from scopeagent.recorders.utils import fix_timestamps, ProcessLocal

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

from ..tracer import tags, SpanRecorder


LOOP_PERIOD = 1  # seconds between buffer checks
logger = logging.getLogger(__name__)
_proclocal = ProcessLocal()


class AsyncRecorder(SpanRecorder):
    def __init__(self, period=1, test_only=True):
        super(AsyncRecorder, self).__init__()
        self.period = period
        self.test_only = test_only
        self.main_pid = os.getpid()
        self.ensure_recorder_thread()

    def ensure_recorder_thread(self):
        if 'setup' not in _proclocal:
            logger.debug("[%d] starting asyncrecorder thread", os.getpid())
            thread = threading.Thread(target=self.run)
            thread.daemon = True
            thread.start()
            _proclocal['thread'] = thread
            atexit.register(self.stop)
            _proclocal['queue'] = Queue()
            _proclocal['setup'] = True

    def record_span(self, span):
        if not span.context.sampled:
            return

        if self.test_only and span.context.baggage.get(tags.TRACE_KIND) != 'test':
            return

        self.ensure_recorder_thread()
        _proclocal['queue'].put(fix_timestamps(span), block=False)

    def run(self):
        running = True
        buffer = []
        loop_duration = 0
        while running:
            time.sleep(LOOP_PERIOD)
            loop_duration += LOOP_PERIOD
            try:
                while True:
                    item = _proclocal['queue'].get(block=False)
                    _proclocal['queue'].task_done()
                    if item is None:
                        running = False
                        raise Empty()
                    buffer.append(item)
            except Empty:
                pass

            # We flush the buffer if any of the following apply:
            # * Last time we flushed was more than `self.period` seconds ago (even if buffer is empty)
            #   and we are in the parent process
            # * The recorder is being shut down
            # * There is data to be flushed in the buffer
            if (loop_duration >= self.period and os.getpid() == self.main_pid) or not running or len(buffer) > 0:
                loop_duration = 0
                try:
                    self.flush(buffer)
                    buffer = []
                except Exception as e:
                    logger.debug("exception while flushing buffer - trying again in next iteration: %s", str(e))

    def stop(self):
        try:
            if 'setup' in _proclocal:
                logger.debug("stopping asyncrecorder thread")
                _proclocal['queue'].put(None)
                _proclocal['thread'].join()
        except Exception as e:
            logger.debug("failed to stop: %s", e)

    @abstractmethod
    def flush(self, spans):
        raise NotImplementedError()
