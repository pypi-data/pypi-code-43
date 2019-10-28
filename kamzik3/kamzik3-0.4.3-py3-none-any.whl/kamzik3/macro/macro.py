import logging
import os
import re
import time
from threading import Thread

import numpy as np

import kamzik3
from kamzik3 import DeviceError, units, MacroException
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.attributeLogger import AttributeLoggerTriggered
from kamzik3.devices.device import Device
from kamzik3.macro.common import Common
from kamzik3.macro.scan import Scan
from kamzik3.macro.step import Step
from kamzik3.snippets.snippetDataAccess import get_next_file_index
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import seconds_to_datetime, get_scaled_time_duration


class Macro(Common, Device):
    current_point_index = 0
    template_id = None

    def __init__(self, device_id, chain=None, repeat_count=0, wait_after=units.Quantity(0, "s"), retry_count=0,
                 trigger_log=True, comment=None):
        self.logger = logging.getLogger("Macro.{}".format(device_id))
        self.comment = comment
        self.chain = chain
        Common.__init__(self, device_id, repeat_count, wait_after, retry_count, trigger_log)
        Device.__init__(self, device_id)
        self.macro_logger = None
        if self.chain is None:
            self.chain = []
        self.index = -1
        self.macro_body_thread = None
        self._expose_methods_to_clients()
        self.connect()

    def _init_attributes(self):
        super(Macro, self)._init_attributes()

        self.attributes.update({
            ATTR_STATE: Attribute(IDLE, readonly=True, default_type=np.uint8),
            ATTR_POINTS_COUNT: Attribute(1, readonly=True, default_type=np.uint64),
            ATTR_POINT_INDEX: Attribute(0, readonly=True, default_type=np.uint64),
            ATTR_PROGRESS: Attribute(0, readonly=True, default_type=np.float16, unit="%", min_value=0, max_value=100,
                                     decimals=2),
            ATTR_CHAIN_LINK: Attribute(0, readonly=True, default_type=np.uint64),
            ATTR_CHAIN_LINK_OUTPUT: Attribute("", readonly=True),
            ATTR_RUNNING_TIME: Attribute(0, readonly=True),
            ATTR_ESTIMATED_TIME: Attribute(0, readonly=True),
            ATTR_ESTIMATED_END: Attribute(0, readonly=True),
            ATTR_REMAINING_TIME: Attribute(0, readonly=True),
            ATTR_STARTED_AT: Attribute(None, readonly=True),
            ATTR_OUTPUT_FILENAME: Attribute(None, readonly=True),
        })
        self.set_value(ATTR_DESCRIPTION, self.comment)

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.recount_steps()
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        _finish_configuration()

    def add(self, link):
        if isinstance(link, list):
            for link_item in link:
                self.add(link_item)
            return
        assert isinstance(link, Common)
        if isinstance(link, Macro):
            self.chain += link.chain
        else:
            self.chain.append(link)
        self.recount_steps()

    def next(self):
        self.index += 1
        if self.index < len(self.chain):
            return self.chain[self.index]
        else:
            return None

    def prev(self):
        self.index -= 1
        if self.index >= 0:
            return self.chain[self.index]
        else:
            return None

    def reset(self):
        self.index = -1
        self.set_point_index(0)
        super(Macro, self).reset()

    def resolve_scans(self):
        new_chain = []
        for link in self.chain:
            if isinstance(link, Scan) and link.scanner is not None and not link.resolved:
                scanner = kamzik3.session.get_device(link.scanner)
                scan_macro = scanner.get_scanner_macro(scanner_input=link,
                                                       scanner_attributes=link.scanner_attributes)
                new_chain += scan_macro.chain
                link.resolved = True
            else:
                new_chain.append(link)
        self.chain = new_chain
        self.recount_steps()

    @expose_method()
    def start(self, threaded=True):
        if self.get_state() == BUSY:
            raise DeviceError(u"Macro is already running")
        self.resolve_scans()
        super(Macro, self).start()
        if self.macro_logger is not None:
            self.macro_logger.start()

        self.set_point_index(0)
        self.set_value(ATTR_STARTED_AT, seconds_to_datetime(self.started_at))
        self.set_value(ATTR_ESTIMATED_END, seconds_to_datetime(self.started_at))
        self.current_point_index = 0
        self.index = -1

        if threaded:
            self.macro_body_thread = Thread(target=self.body, args=[self.macro_clean])
            self.macro_body_thread.start()
        else:
            self.body(callback=self.macro_clean)

    def body(self, callback=None):
        try:
            for repeat in range(self.repeat_count + 1):
                for link in self.chain:
                    link.reset()
                link = self.next()
                while self.get_state() == BUSY:
                    if link is None:
                        link = self.prev()
                        if self.current_point_index == 0:
                            break
                        else:
                            continue
                    elif link.get_state() == DONE and link.repeated == link.repeat_count:
                        link.reset()
                        link = self.prev()
                        if link is None:
                            if self.repeated == self.repeat_count:
                                self.done()
                            else:
                                self.repeated += 1
                                break
                        continue
                    elif isinstance(link, Step):
                        if link.get_state() == DONE:
                            link.repeat()
                        else:
                            try:
                                link.start()
                            except MacroException as retry_reason:
                                link.retry(retry_reason)
                                continue
                    elif isinstance(link, Scan):
                        if link.as_step:
                            step = link.start()
                            link = step
                            # step.start()
                            continue
                        # Get step from step generator
                        if link.get_state() == DONE:
                            step = link.repeat()
                        else:
                            try:
                                step = link.start()
                            except MacroException as retry_reason:
                                link.retry(retry_reason)
                                continue
                        if step is None:
                            link = self.chain[self.index]
                        else:
                            link = step
                        continue

                    self.set_value(ATTR_CHAIN_LINK, self.index)
                    self.set_attribute((ATTR_CHAIN_LINK_OUTPUT, VALUE),
                                       [self.current_point_index + 1, self.index, link.get_output()])
                    self.set_point_index(self.current_point_index + 1)
                    if link.trigger_log and self.macro_logger is not None:
                        self.macro_logger.trigger()

                    if link.repeated == link.repeat_count:
                        link = self.next()

                if self.in_statuses(IDLE_DEVICE_STATUSES):
                    return

                self.start_timer()
        except MacroException as e:
            self.error(e)
            raise e
        finally:
            if callback is not None:
                callback()

    @expose_method()
    def stop(self):
        if self.in_statuses(IDLE_DEVICE_STATUSES):
            raise DeviceError(u"Macro is not running")

        for link in self.chain:
            link.stop()
        super(Macro, self).stop()

    def macro_clean(self):
        for link in self.chain:
            if isinstance(link, Scan):
                link.return_back_step()

    def recount_steps(self):
        sub_steps_count = 0
        sub_points_count = 0
        for link in reversed(self.chain):
            if isinstance(link, Scan) and sub_steps_count > 0:
                repeat_step = (link.step_attributes.get("repeat_count", 0) + 1)
                repeat_scan = (link.repeat_count + 1)
                total_steps = link.steps_count * sub_steps_count
                sub_steps_count = total_steps * repeat_scan

                total_points = (link.steps_count + 1) * (repeat_step + sub_points_count)
                sub_points_count = total_points * repeat_scan
            else:
                sub_steps_count += link.get_total_steps_count()
                sub_points_count += link.get_total_points_count()

        total_count = sub_points_count * (self.repeat_count + 1)
        self.points_count = total_count
        self.set_value(ATTR_POINTS_COUNT, self.points_count)

    def get_total_steps_count(self):
        return len(self.chain)

    def get_total_points_count(self):
        return self.points_count

    @expose_method()
    def get_chain_link_output(self):
        chain_link_output = []
        for index, chain_item in enumerate(self.chain):
            if isinstance(chain_item, Scan):
                chain_link_output.append((chain_item.step_attributes["device_id"],
                                          chain_item.step_attributes["attribute"], chain_item.points_count))
            else:
                chain_link_output.append(None)
        return chain_link_output

    def set_state(self, new_state):
        self.set_value(ATTR_STATE, new_state)
        if new_state in (IDLE, DONE, STOPPED):
            self.set_status(STATUS_IDLE)
        elif new_state in (BUSY, PAUSED):
            self.set_status(STATUS_BUSY)
        elif new_state == ERROR:
            self.set_status(STATUS_ERROR)

        if self.macro_logger is not None and new_state in (DONE, ERROR, IDLE, DONE, STOPPED):
            self.macro_logger.stop()

        super(Macro, self).set_state(new_state)

    def set_point_index(self, point_index):
        self.current_point_index = point_index
        self.set_value(ATTR_POINT_INDEX, point_index)
        progress = (100. / self[ATTR_POINTS_COUNT][VALUE]) * point_index
        self.set_value(ATTR_PROGRESS, progress)

        running_time = time.time() - self.started_at
        try:
            estimated_time = (100 / progress) * running_time
        except ZeroDivisionError:
            estimated_time = 1
        remaining_time = estimated_time - running_time
        self.set_value(ATTR_RUNNING_TIME, get_scaled_time_duration(running_time))
        self.set_value(ATTR_REMAINING_TIME, get_scaled_time_duration(remaining_time))
        self.set_value(ATTR_ESTIMATED_END, seconds_to_datetime(time.time() + remaining_time))
        self.set_value(ATTR_ESTIMATED_TIME, get_scaled_time_duration(estimated_time))

    def setup_output_file(self, output_directory_path, macro_prefix):
        if not os.path.exists(output_directory_path):
            self.logger.info(u"Output directory {} does not exists, trying to create it.".format(output_directory_path))
            os.makedirs(output_directory_path)
        next_index = get_next_file_index(output_directory_path, re.compile("{}_(\d+)\.log".format(macro_prefix)))
        output_filename = os.path.join(output_directory_path, "{}_{}.log".format(macro_prefix, next_index))
        self.set_value(ATTR_OUTPUT_FILENAME, output_filename)
        self.macro_logger = AttributeLoggerTriggered(output_filename,
                                                     device_id="{}_Log_{}".format(macro_prefix, next_index),
                                                     config={"rotating": False})
        return output_filename, next_index

    def add_output_attribute(self, device_id, attribute):
        if self.macro_logger is None:
            raise DeviceError(u"Macro logger is not set")

        self.macro_logger.add_logged_attribute(device_id, attribute)

    def get_output_header(self):
        lines = []
        for link in self.chain:
            lines += link.get_output_header()
            lines += ["-" * 32]
        return lines

    def disconnect(self):
        if self.chain is not None:
            for chain in self.chain:
                chain.remove()

        if self.macro_logger is not None:
            self.macro_logger.remove()

        return Device.disconnect(self)

    def remove(self):
        Device.remove(self)
        self.macro_logger = None
        self.chain = None
        Common.remove(self)

    def error(self, error_message):
        self.error_at = time.time()
        self.running_time = self.error_at - self.started_at
        self.error_message = error_message
        self.set_value(ATTR_LAST_ERROR, error_message)
        self.logger.error(error_message)
        self.handle_command_error(self.common_id, error_message)
        self.set_state(ERROR)