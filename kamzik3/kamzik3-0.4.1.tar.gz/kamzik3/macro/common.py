import logging
import time
from threading import Event

from kamzik3 import units
from kamzik3.constants import *
from kamzik3.snippets.snippetsYaml import YamlSerializable


class Common(YamlSerializable):
    state = IDLE
    repeated = 0
    error_message = None
    previous_running_time = 0
    running_time = 0
    started_at = 0
    done_at = 0
    stopped_at = 0
    reset_at = 0
    error_at = 0
    steps_count = 0
    points_count = 1
    retry_timeout = 100  # 100 ms
    common_id = None
    logger = None

    def __init__(self, common_id, repeat_count=0, wait_after=units.Quantity(0, "s"), retry_count=0, trigger_log=True):
        assert repeat_count >= 0, u"Repeat parameter should be >= 0"
        assert wait_after >= 0, u"Wait_after parameter should be >= 0"
        self.set_common_id(common_id)
        self.max_retry_count = retry_count
        self.retry_count = retry_count
        self.wait_after = wait_after.to("s")
        self.trigger_log = trigger_log

        self.timer = None
        if self.wait_after > 0:
            self.timer = Event()
        self.repeat_count = int(repeat_count)

    def set_common_id(self, common_id):
        self.common_id = common_id
        if not hasattr(self, "logger") or self.logger is None:
            self.logger = logging.getLogger("Macro.common.{}".format(self.common_id))

    def set_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state

    def reset(self):
        self.logger.debug("Reset")
        self.reset_at = time.time()
        self.error_message = None
        self.repeated = 0
        self.retry_count = self.max_retry_count
        self.set_state(IDLE)

    def start(self):
        self.logger.debug("Started")
        self.started_at = time.time()
        self.running_time = 0
        self.set_state(BUSY)

    def repeat(self):
        self.logger.debug("Repeated")
        self.started_at = time.time()
        self.running_time = 0
        self.repeated += 1
        self.set_state(BUSY)

    def retry(self, retry_reason):
        if self.retry_count == 0:
            raise retry_reason
        else:
            self.retry_count -= 1
            self.logger.error(
                "Retrying step due to error. Remaining tries {}. Error message: {}".format(self.retry_count,
                                                                                           retry_reason))
            self.reset_at = time.time()
            self.error_message = None
            time.sleep(self.retry_timeout / 1e3)

    def stop(self):
        self.stopped_at = time.time()
        self.running_time = self.stopped_at - self.started_at
        if self.timer is not None:
            self.stop_timer()
        self.logger.debug("Stopped")
        self.set_state(STOPPED)

    def done(self):
        self.done_at = time.time()
        self.previous_running_time = self.running_time = self.done_at - self.started_at
        self.logger.debug("Done")
        self.set_state(DONE)

    def error(self, error_message):
        self.error_at = time.time()
        self.running_time = self.error_at - self.started_at
        self.error_message = error_message
        self.logger.error(error_message)
        self.set_state(ERROR)

    def stop_timer(self):
        if self.timer is not None:
            self.logger.debug("Timer for {}s stopped".format(self.wait_after))
            self.timer.set()
            return True
        return False

    def start_timer(self):
        if self.timer is not None:
            self.logger.debug("Waiting for {}s".format(self.wait_after))
            self.timer.clear()
            self.timer.wait(self.wait_after.m)
            return True
        return False

    def get_total_steps_count(self):
        return self.steps_count * (self.repeat_count + 1)

    def remove(self):
        self.logger = None

    def get_reset_step(self):
        return None

    def get_output(self):
        return None
