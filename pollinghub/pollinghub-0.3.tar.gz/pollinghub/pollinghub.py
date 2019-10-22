import logging
import threading
import time
import traceback


class Pollee(object):
    ASYNC_TIMEOUT = 10

    def update_trigger_time(self):
        self.trigger_time = time.time() + self.period

    def __init__(self, name, period, callback, *args, **kwargs):
        self.name = name if name else self.__class__.__name__
        self._log = logging.getLogger(self.name)

        self.period = period
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.once = (period == 0)

        self.trigger_time = None

    # ret: {'success': True/False, 'err': ''}
    # TODO: support asynchronous callback
    #  (in other thread/process? use thread/process pool?)
    def run_cb(self):
        ret = {'success': True, 'err': ''}

        if self.callback:
            try:
                self.callback(*self.args, **self.kwargs)
            except Exception as e:  # catch all exceptions
                ret['err'] += str(e)
                ret['err'] += str(traceback.format_exc())
                ret['success'] = False
        else:
            ret['success'] = False
            ret['err'] = 'no callback'

        return ret

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class PollingHub(object):
    def _polling_thread_impl(self):
        self._log.info('START')

        while self._running:
            now = time.time()
            self._log.debug('polling, %s', now)
            self.wake_count += 1

            # handle expired target
            with self._targets_lock:
                for p in self._pollees:
                    if p.trigger_time <= now:
                        self._log.debug('trigger %s', p.name)

                        ret = p.run_cb()
                        if not ret['success']:
                            self._log.error('run callback error %s', ret['err'])

                        p.update_trigger_time()

                        if p.once:
                            self._pollees.remove(p)
                self._sort_pollees()
                self._trigger.clear()  # job done

            now = time.time()
            if self._pollees:
                wait_time = self._pollees[0].trigger_time - now
                self._log.debug("wait_time: %s", wait_time)

                if wait_time <= 0:
                    # no need to wait
                    self._log.debug("new pollee available during process")
                    continue

                self._trigger.wait(wait_time)
            else:
                # wait forever
                self._log.debug("no pollee, wait...")
                self._trigger.wait()

        self._log.info('STOP')
        self._log.debug("wake_count=%s", self.wake_count)

    def dump(self):
        self._log.debug(traceback.format_exc())
        for p in self._pollees:
            trigger_time = p.trigger_time if p.trigger_time else -1
            self._log.info("%s: period=%s, trigger=%s", p, p.period,
                           trigger_time)

    def __init__(self, name=None):
        self.name = name if name else self.__class__.__name__
        self._log = logging.getLogger(self.name)

        self._running_lock = threading.Lock()
        self._targets_lock = threading.Lock()
        self._pollees = []
        self._running = False
        self._trigger = threading.Event()
        self._trigger.clear()
        self._polling_thread = None
        self.wake_count = 0

    def reg(self, pollee):
        self._log.info("%s", pollee)

        if not isinstance(pollee, Pollee):
            self._log.error("invalid input type")
            return False

        with self._targets_lock:
            if pollee in self._pollees:
                self._log.error('Exist')
                return False

            pollee.update_trigger_time()
            self._pollees.append(pollee)

        return True

    def _sort_pollees(self):
        self._pollees.sort(key=lambda p: p.trigger_time)

    # return True: success, False: fail
    def start(self):
        self._log.info('')
        with self._running_lock:
            if self._running:
                self._log.error("Already started!")
                return False

            self._running = True
            with self._targets_lock:
                self._sort_pollees()

            # update trigger time
            with self._targets_lock:
                for p in self._pollees:
                    p.update_trigger_time()

            self.wake_count = 0
            self._polling_thread = threading.Thread(
                target=self._polling_thread_impl)
            self._polling_thread.setDaemon(True)
            self._polling_thread.start()

        return True

    def un_reg(self, pollee):
        self._log.info(pollee)
        with self._targets_lock:
            if pollee in self._pollees:
                self._pollees.remove(pollee)
                self._trigger.set()
            else:
                self._log.error("Not exist")
                return False
        return True

    # return True: success, False: fail
    def stop(self):
        self._log.info('')
        with self._running_lock:
            if not self._running:
                self._log.error("Already stopped!")
                return False

            self._running = False

            if self._polling_thread:
                # keep trigger until stop
                while self._polling_thread.is_alive():
                    self._trigger.set()
                    self._polling_thread.join(1)

        return True

    @property
    def running(self):
        return self._running

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()
