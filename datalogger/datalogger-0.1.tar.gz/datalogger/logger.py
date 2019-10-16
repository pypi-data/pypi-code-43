import os
import threading
import time
import traceback
import subprocess
import logging
from datetime import datetime
from time import sleep


def run_cmd(cmd):
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return ps.communicate()[0]


# A background monitor
class BgMonitor(object):
    SCRIPT_PATH = '/tmp/'

    def __init__(self, name, cmd, log_file=None):
        self.name = name if name else self.__class__.__name__
        self._log = logging.getLogger(self.name)

        self._test_time = datetime.now()

        self._cmd = cmd

        self._log_file = log_file

        self._script_file = '{}{}_{}.sh'.format(
            self.SCRIPT_PATH,
            self.name,
            self._test_time.strftime('%Y%m%d_%H%M%S'))

        # basic check
        if type(self._cmd) is not str or len(self._cmd) is 0:
            raise ('parameter error: cmd={}'.format(cmd))

    def start(self):
        self.stop()

        try:
            os.makedirs(self.SCRIPT_PATH)
        except FileExistsError:
            pass

        log_file_str = '> {}'.format(
            self._log_file) if self._log_file else ' /dev/null'
        with open(self._script_file, 'w') as f:
            f.write("{} 2>&1 {} & \n".format(self._cmd, log_file_str))

        cmd = 'sh {}'.format(self._script_file)
        self._log.debug('BgMonitor cmd: %s', cmd)
        os.system(cmd)
        # sleep(1)

    def stop(self):
        os.system("kill -9 `ps aux | grep {} | awk '{{print $2}}' "
                  "| tr '\\n' ' '`".format(self._script_file))

        try:
            os.remove(self._script_file)
        except FileNotFoundError:
            pass


# A column in log
class Column(object):
    ACTION_CMD = 'cmd'
    ACTION_CAT = 'cat'

    # show_diff: calculate avg. difference during interval
    def __init__(self, name, action, cmd=None, node=None, show_diff=False,
                 div=None):
        self.name = name if name else self.__class__.__name__
        self._log = logging.getLogger(self.name)
        self._action = action
        self._cmd = cmd
        self._node = node
        self._show_diff = show_diff
        self._div = div

        self._val = None
        self._latest_val = None

        self._time = None
        self._latest_time = None

        # check error
        if self._action == self.ACTION_CMD and cmd is None:
            raise Exception(
                'parameter error: action={}, cmd={}'.format(action, cmd))
        if self._action == self.ACTION_CAT and node is None:
            raise Exception(
                'parameter error: action={}, node={}'.format(action, node))

    def get(self):
        self._latest_val = self._val
        self._latest_time = self._time

        val = ''
        if self._action == self.ACTION_CMD:
            val = run_cmd(self._cmd)
        elif self._action == self.ACTION_CAT:
            val = run_cmd('cat {}'.format(self._node))
        self._time = time.time()
        self._val = val

        if self._show_diff:
            try:
                new_val = float(val)
            except Exception as e:
                self._log.error(e)
                self._log.error(traceback.format_exc())
                new_val = 0

            try:
                old_val = float(self._latest_val)
            except Exception as e:
                self._log.error(e)
                self._log.error(traceback.format_exc())
                old_val = 0

            if self._latest_time:
                diff = (new_val - old_val) / (
                        self._time - self._latest_time)
            else:
                # simply return 0 if no previous data to compare,
                diff = 0

            ret = diff
        else:
            ret = self._val

        if self._div:
            ret = float(ret) / self._div

        return ret


class Logger(object):
    DEFAULT_LOG_PATH = './logger/'

    DEFAULT_INTERVAL = 1
    TIMEOUT_INFINITY = 0
    DEFAULT_TIMEOUT = TIMEOUT_INFINITY

    def __init__(self, name=None, columns=[], bg_monitors=[], pre_cmds=[],
                 post_cmds=[], log_path=None, interval=DEFAULT_INTERVAL,
                 timeout=DEFAULT_TIMEOUT):
        self.name = name if name else self.__class__.__name__
        self._log = logging.getLogger(self.name)
        self._test_time = datetime.now()
        self._is_running = False
        self._force_stop = False

        self._timeout = timeout
        self._interval = interval
        self._columns = columns
        self._bg_monitors = bg_monitors
        self._pre_cmds = pre_cmds
        self._post_cmds = post_cmds

        if not log_path:
            self._log_path = '{}/{}_{}'.format(
                self.DEFAULT_LOG_PATH,
                self.name,
                self._test_time.strftime('%Y%m%d_%H%M%S'))
        else:
            self._log_path = log_path
        self._log_file = '{}/logger.log'.format(self._log_path)

        self._thread = threading.Thread(target=self._log_columns)

    def start(self, sync=True):

        for monitor in self._bg_monitors:
            monitor.start()

        self._thread.start()

        if sync:
            self._log.info("synchronous mode. use ctrl-c to stop")
            self.join()

    def join(self):
        try:
            self._thread.join()
        except KeyboardInterrupt:
            self._log.error('Ctrl-C')
            self.stop()

    def stop(self):
        self._force_stop = True
        self._thread.join()

        for monitor in self._bg_monitors:
            monitor.stop()

    def _log_columns(self):
        for cmd in self._pre_cmds:
            run_cmd(cmd)

        start_time = time.time()
        with open(self._log_file, 'w') as f:
            # write columns
            line = 'time'
            for col in self._columns:
                line += ',{}'.format(col.name)
            self._log.debug(line)
            f.write('{} \n'.format(line))

            while self._force_stop is False \
                    and (self._timeout is self.TIMEOUT_INFINITY
                         or time.time() < start_time + self._timeout):
                step_time = time.time()
                next_time = step_time + self._interval

                line = '{}'.format(step_time)
                for col in self._columns:
                    line += ',{}'.format(str(col.get(), "utf-8").strip())
                self._log.debug(line)
                f.write('{} \n'.format(line))

                # precise sleep
                now = time.time()
                if now < next_time:
                    sleep(next_time - now)

        for cmd in self._post_cmds:
            run_cmd(cmd)
