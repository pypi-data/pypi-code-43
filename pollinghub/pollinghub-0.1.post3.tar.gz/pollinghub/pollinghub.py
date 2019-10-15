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

    # ret: {'success': True/False, 'msg': '', 'err': ''}
    # TODO: support asynchronous callback(run in other thread/process?)
    def run_cb(self):
        ret = {'success': True, 'msg': '', 'err': ''}

        if self.callback:
            try:
                self.callback(*self.args, **self.kwargs)
            except Exception as e:  # catch all exceptions
                ret['err'] += str(e)
                ret['err'] += str(traceback.format_exc())
                ret['success'] = False

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
            # self.log.debug('polling, now=%s', now)

            # handle expired target
            with self._targets_lock:
                # self.dump()
                for p in self._pollees:
                    if p.trigger_time <= now:
                        self._log.debug('trigger %s', p.name)

                        ret = p.run_cb()
                        if not ret['success']:
                            self._log.error('run callback error %s', ret['err'])

                        p.update_trigger_time()

                        if p.once:
                            self._pollees.remove(p)

                # sorted by trigger_time
                if self._pollees:
                    sorted(self._pollees, key=lambda x: x.trigger_time)

            wait_time = None
            if self._pollees:
                wait_time = self._pollees[0].trigger_time - now
            self._trigger.wait(wait_time)

        self._log.info('STOP')

    def dump(self):
        for p in self._pollees:
            trigger_time = p.trigger_time if p.trigger_time else -1
            self._log.info("%s: period=%s, trigger=%s", p, p.period,
                           trigger_time)

    def __init__(self, name=None):
        self.name = name if name else self.__class__.__name__
        self._log = logging.getLogger(self.name)

        self._targets_lock = threading.Lock()
        self._pollees = []
        self._running = False
        self._trigger = threading.Event()
        self._trigger.clear()
        self._polling_thread = threading.Thread(
            target=self._polling_thread_impl)

    def reg(self, pollee):
        self._log.info("%s", pollee)
        with self._targets_lock:
            exist = False
            for p in self._pollees:
                if pollee is p or pollee.name == p.name:
                    exist = True

            if exist:
                self._log.error('Exist')
                return False

            pollee.update_trigger_time()
            self._pollees.append(pollee)

        return True

    def start(self):
        self._running = True
        self._pollees.sort(key=lambda p: p.trigger_time)
        self._polling_thread.start()

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

    def stop(self):
        self._running = False
        self._trigger.set()
        with self._targets_lock:
            self._pollees = []

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()
