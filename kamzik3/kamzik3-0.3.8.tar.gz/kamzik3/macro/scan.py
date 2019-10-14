import copy
import logging
import time

from numpy import linspace

import kamzik3
from kamzik3.constants import *
from kamzik3 import units, MacroException
from kamzik3.devices.attribute import Attribute
from kamzik3.macro.common import Common
from kamzik3.macro.step import StepSetpointNumerical


class Scan(Common):
    first_step_at = 0
    resolved = False

    def __init__(self, common_id, start_point, end_point, steps_count, step_class=StepSetpointNumerical,
                 step_attributes=None, repeat_count=0, wait_after=units.Quantity(0, "s"), retry_count=0,
                 trigger_log=True, as_step=False, bidirectional=False, scanner=None, scanner_attributes=None,
                 return_back=True):
        assert isinstance(start_point, units.Quantity)
        assert isinstance(end_point, units.Quantity)
        assert isinstance(wait_after, units.Quantity)
        assert steps_count > 0
        self.scanner = scanner
        self.scanner_attributes = scanner_attributes
        self.return_back = return_back
        # self.initial_value_of_attribute = None
        self.step_index = 0
        self.start_point = start_point
        self.end_point = end_point
        if as_step:
            self.steps_count = 1
            self.points_count = 1
        else:
            self.steps_count = steps_count
            self.points_count = steps_count + 1
        self.bidirectional = bidirectional
        self.scan_pass = 0
        self.steps = self.step_generator()
        self.scanning_range = linspace(start_point.m, end_point.m, steps_count + 1)
        self.step_class = step_class
        self.step_attributes = step_attributes
        if self.step_attributes is None:
            self.step_attributes = {}
        self.current_step = None
        self.as_step = as_step
        self.logger = logging.getLogger("Macro.Scan.{}".format(common_id))
        attribute = kamzik3.session.get_device(
            self.step_attributes["device_id"]).get_attribute(self.step_attributes["attribute"])
        self.initial_value_of_attribute = attribute.value()
        super(Scan, self).__init__(common_id, repeat_count, wait_after, retry_count, trigger_log)

    def set_steps_count(self, steps_count):
        assert steps_count > 0
        if self.as_step:
            self.steps_count = 1
            self.points_count = 1
        else:
            self.steps_count = steps_count
            self.points_count = steps_count + 1
        self.steps = self.step_generator()
        self.scanning_range = linspace(self.start_point.m, self.end_point.m, steps_count + 1)

    def get_total_steps_count(self):
        repeat_step = (self.step_attributes.get("repeat_count", 0) + 1)
        repeat_scan = (self.repeat_count + 1)
        return self.steps_count * repeat_step * repeat_scan

    def get_total_points_count(self):
        repeat_step = (self.step_attributes.get("repeat_count", 0) + 1)
        repeat_scan = (self.repeat_count + 1)
        return self.points_count * repeat_step * repeat_scan

    def step_generator(self):
        self.first_step_at = time.time()
        scanning_range = self.scanning_range
        if self.bidirectional and self.scan_pass % 2:
            scanning_range = reversed(self.scanning_range)
        for self.step_attributes["common_id"], self.step_attributes["setpoint"] in enumerate(scanning_range):
            if self.get_state() == STOPPED:
                break
            self.step_attributes["setpoint"] = units.Quantity(self.step_attributes["setpoint"], self.start_point.u)
            yield self.step_class(**self.step_attributes)
            self.step_index += 1
        self.scan_pass += 1

    def reset(self):
        self.steps = self.step_generator()
        super(Scan, self).reset()

    def repeat(self):
        super(Scan, self).repeat()
        self.steps = self.step_generator()
        return self.start()

    def start(self):
        super(Scan, self).start()
        try:
            if self.current_step is not None:
                self.current_step.remove()
            self.current_step = next(self.steps)
            return self.current_step
        except StopIteration:
            self.done()
            return None
        except MacroException as e:
            self.error(e)
            raise e

    def stop(self):
        self.started_at = self.first_step_at
        if self.current_step is not None:
            self.current_step.stop()
        super(Scan, self).stop()

    def done(self):
        self.started_at = self.first_step_at
        super(Scan, self).done()

    def error(self, error_message):
        self.started_at = self.first_step_at
        super(Scan, self).error(error_message)

    def return_back_step(self):
        if self.return_back and self.initial_value_of_attribute is not None:
            device = kamzik3.session.get_device(self.step_attributes["device_id"])
            if device.wait_for_status(IDLE_DEVICE_STATUSES):
                step = self.get_reset_step()
                if isinstance(step, list):
                    for sub_step in step:
                        sub_step.start()
                else:
                    step.start()
                # device.set_attribute(self.step_attributes["attribute"] + [VALUE], self.initial_value_of_attribute)
            else:
                self.logger.error(
                    u"Could not return {} to {}, device was not IDLE".format(self.step_attributes["attribute"],
                                                                             self.initial_value_of_attribute))

    def get_output_header(self):
        lines = [
            "Type: {}".format("Scan"),
            "Scanner: {}".format(self.scanner),
            "Device: {}".format(self.step_attributes["device_id"]),
            "Attribute: {}".format(Attribute.list_attribute(self.step_attributes["attribute"])),
            "Start point: {:~}".format(self.start_point),
            "End point: {:~}".format(self.end_point),
            "Steps count: {}".format(self.steps_count),
            "Step size: {:~}".format((self.end_point - self.start_point) / self.steps_count),
            "Points count: {}".format(self.points_count),
            "Bidirectional: {}".format(self.bidirectional),
            "Negative tolerance: {:~}".format(self.step_attributes["negative_tolerance"]),
            "Positive tolerance: {:~}".format(self.step_attributes["positive_tolerance"]),
            "Wait: {:~}".format(self.step_attributes["wait_after"]),
            "Repeat count: {}".format(self.repeat_count),
            "Retry: {}".format(self.retry_count),
            "Return back: {}".format(self.return_back),
            "Trigger log: {}".format(self.step_attributes["trigger_log"]),
        ]
        if self.scanner_attributes is not None:
            for key, value in self.scanner_attributes.items():
                lines.append("{}: {}".format(key, value))
        return lines

    def remove(self):
        if self.current_step is not None:
            self.current_step.remove()
        self.steps = None
        self.scanning_range = None
        self.step_class = None
        self.step_attributes = None
        self.current_step = None
        Common.remove(self)

    def get_reset_step(self):
        setpoint_attributes_copy = copy.copy(self.step_attributes)
        setpoint_attributes_copy["common_id"] = "ReturnBack"
        setpoint_attributes_copy["setpoint"] = self.initial_value_of_attribute
        setpoint_attributes_copy["wait_after"] = units.Quantity(0, "s")
        try:
            del setpoint_attributes_copy["output"]
        except KeyError:
            pass
        return self.step_class(**setpoint_attributes_copy)
