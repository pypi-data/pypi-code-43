import time

import numpy as np
from bidict import FrozenOrderedBidict

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method

try:
    from PyDAQmx import *
except ImportError:
    raise DeviceError("PyDAQmx import error!")
from ctypes import *

GROUP_DIAGNOSTICS = u"Diagnostics"
GROUP_AI = "Analog inputs"
GROUP_AO = "Analog outputs"
GROUP_DI = "Digital inputs"
GROUP_DO = "Digital outputs"

CONST_AI_TERM_CONF = FrozenOrderedBidict(
    {DAQmx_Val_Bit_TermCfg_RSE: "RSE", DAQmx_Val_Bit_TermCfg_NRSE: "NRSE", DAQmx_Val_Bit_TermCfg_Diff: "Diff",
     DAQmx_Val_Bit_TermCfg_PseudoDIFF: "PseudoDiff"})
CONST_AI_TERM_CONF_INPUT = {DAQmx_Val_Bit_TermCfg_RSE: DAQmx_Val_RSE,
                            DAQmx_Val_Bit_TermCfg_NRSE: DAQmx_Val_NRSE,
                            DAQmx_Val_Bit_TermCfg_Diff: DAQmx_Val_Diff,
                            DAQmx_Val_Bit_TermCfg_PseudoDIFF: DAQmx_Val_PseudoDiff
                            }


class DeviceNiCard(Device):
    task_handle_diagnose = None

    def __init__(self, card_address, device_id=None, config=None):
        self.card_address = card_address
        self.active_tasks = {}
        super(DeviceNiCard, self).__init__(device_id, config)
        self._expose_methods_to_clients()
        self.connect()

    def _init_attributes(self):
        super(DeviceNiCard, self)._init_attributes()
        self.attributes.update({
            ATTR_SERIAL_NUMBER: Attribute(readonly=True),
            ATTR_PRODUCT_TYPE: Attribute(readonly=True),
            GROUP_DIAGNOSTICS: {

                ATTR_ANALOG_INPUT_READOUT_TASK: Attribute(default_type=bool,
                                                          set_function=self.diagnose_analogue_readout_task,
                                                          set_value_when_set_function=True),
                ATTR_TERMINAL_CONFIGURATION: Attribute(u"RSE", default_type=CONST_AI_TERM_CONF.values()),
                ATTR_SAMPLES_NUMBER: Attribute(2500, default_type=np.uint16, min_value=0, max_value=10000),
                ATTR_READOUT_AT_SAMPLES: Attribute(500, default_type=np.uint16, min_value=0, max_value=10000),
            }
        })

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...
        :param args: connect attributes
        """
        try:
            self.connecting = True
            self.get_system_info()
            self.handle_configuration_event()
            self.connected = True
            self.connecting = False
            self.set_status(STATUS_IDLE)
        except DAQError:
            self.handle_connection_error(u"NiCard was not found")
            return

    def handle_configuration(self):
        try:
            start_at = time.time()
            analog_inputs, (min_voltage, max_voltage) = self.get_analog_inputs_list()
            self.attributes[GROUP_AI] = {}
            for analog_input, terminal_config in analog_inputs:
                if analog_input == '': continue
                self.attributes[GROUP_AI][analog_input] = Attribute(min_value=min_voltage,
                                                                    max_value=max_voltage,
                                                                    default_type=np.float64, unit="V",
                                                                    decimals=12,
                                                                    readonly=True,
                                                                    terminal_config=terminal_config)
            analog_outputs, (min_voltage, max_voltage) = self.get_analog_outputs_list()
            self.attributes[GROUP_AO] = {}
            for analog_output in analog_outputs:
                if analog_output == '': continue
                self.attributes[GROUP_AO][analog_output] = Attribute(min_value=min_voltage,
                                                                     max_value=max_voltage,
                                                                     default_type=np.float64, unit="V",
                                                                     decimals=12,
                                                                     readonly=True)

            digital_outputs = self.get_digital_outputs_list()
            self.attributes[GROUP_DO] = {}
            for digital_output in digital_outputs:
                if digital_output == '': continue
                self.attributes[GROUP_DO][digital_output] = Attribute(default_type=bool, set_function=lambda value,
                                                                                                             do=digital_output: self.set_digital_output(
                    do, value))

            digital_inputs = self.get_digital_inputs_list()
            self.attributes[GROUP_DI] = {}
            for digital_input in digital_inputs:
                if digital_input == '': continue
                self.attributes[GROUP_DI][digital_input] = Attribute(default_type=bool, readonly=True)

            self.get_counters_list()
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))
        except (DAQError, DeviceError):
            self.handle_response_error(u"Could not get device info")
            return

    def task(self, task_name):
        return Task("{}_{}".format(self.device_id, task_name))

    def diagnose_analogue_readout_task(self, start=True):
        try:
            if start:
                task = self.task("analogue_diagnose_task")
                terminal_configuration = CONST_AI_TERM_CONF.inv[
                    self[GROUP_DIAGNOSTICS][ATTR_TERMINAL_CONFIGURATION][VALUE]]
                channels_in_task = []
                for channel, attribute in self[GROUP_AI].items():
                    if attribute["terminal_config"] < terminal_configuration: continue

                    min_voltage, max_voltage = attribute[MIN], attribute[MAX]
                    task.CreateAIVoltageChan("{}/{}".format(self.card_address, channel), "",
                                             CONST_AI_TERM_CONF_INPUT[terminal_configuration],
                                             min_voltage, max_voltage, DAQmx_Val_Volts, "")
                    channels_in_task.append(channel)
                task.CfgSampClkTiming("", self[GROUP_DIAGNOSTICS][ATTR_SAMPLES_NUMBER][VALUE], DAQmx_Val_Rising,
                                      DAQmx_Val_ContSamps, self[GROUP_DIAGNOSTICS][ATTR_READOUT_AT_SAMPLES][VALUE])

                self.analogueInputCallback_C = DAQmxEveryNSamplesEventCallbackPtr(self.analogueInputCallback)
                task.RegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,
                                                self[GROUP_DIAGNOSTICS][ATTR_READOUT_AT_SAMPLES][VALUE], 0,
                                                self.analogueInputCallback_C, None)
                task_buffer = np.zeros(self[GROUP_DIAGNOSTICS][ATTR_READOUT_AT_SAMPLES][VALUE] * len(channels_in_task))
                self.active_tasks[task.taskHandle.value] = (task, task_buffer, channels_in_task)
                self.task_handle_diagnose = task.taskHandle.value
                self.start_task(self.task_handle_diagnose)
            else:
                self.stop_task(self.task_handle_diagnose)
        except DAQError as e:
            raise DeviceError(e)

    def analogueInputCallback(self, taskHandle, status, nSamples, callbackData_ptr):
        try:
            read = int32()
            task, task_buffer, channels_in_task = self.active_tasks[taskHandle]
            DAQmxReadAnalogF64(taskHandle, self[GROUP_DIAGNOSTICS][ATTR_READOUT_AT_SAMPLES][VALUE], 1.0,
                               DAQmx_Val_GroupByChannel, task_buffer, len(task_buffer), byref(read), None)

            for index, channel in enumerate(channels_in_task):
                buffIndex = index * nSamples
                self.set_attribute((GROUP_AI, channel, VALUE), task_buffer[buffIndex:buffIndex + nSamples].mean())
            return 0
        except DAQError as e:
            raise DeviceError(e)

    def get_system_info(self):
        try:
            # Get serial number
            read = uInt32()
            DAQmxGetDevSerialNum(self.card_address, byref(read))
            serial_number = hex(read.value)
            self.set_value(ATTR_SERIAL_NUMBER, serial_number)
            # Get product type
            buffer_size = 100
            read = create_string_buffer(buffer_size)
            DAQmxGetDevProductType(self.card_address, read, buffer_size)
            product_type = read.value.decode()
            self.set_value(ATTR_PRODUCT_TYPE, product_type)

            return product_type, serial_number
        except DAQError as e:
            raise DeviceError(e)

    def get_analog_inputs_list(self):
        try:
            buffer_size = 1000
            read = create_string_buffer(buffer_size)
            DAQmxGetDevAIPhysicalChans(self.card_address, read, buffer_size)
            # There can be many ranges and there is no way to now how many ahead
            voltage_range = (float64 * 256)()
            DAQmxGetDevAIVoltageRngs(self.card_address, voltage_range, 256)

            available_channels = read.value.decode().replace(self.card_address + "/", "").split(", ")

            read = int32()
            channel_pairs = []
            for channel in available_channels:
                DAQmxGetPhysicalChanAITermCfgs("{}/{}".format(self.card_address, channel), byref(read))
                channel_pairs.append((channel, read.value))

            # Return all channels and the biggest range
            return channel_pairs, (min(voltage_range), max(voltage_range))
        except DAQError as e:
            raise DeviceError(u"Error getting analog inputs: {}".format(e))

    def get_analog_outputs_list(self):
        try:
            buffer_size = 1000
            read = create_string_buffer(buffer_size)
            DAQmxGetDevAOPhysicalChans(self.card_address, read, buffer_size)
            # There can be many ranges and there is no way to now how many ahead
            voltage_range = (float64 * 256)()
            DAQmxGetDevAOVoltageRngs(self.card_address, voltage_range, 256)
            # Return all channels and the biggest range
            return read.value.decode().replace(self.card_address + "/", "").split(", "), (
                min(voltage_range), max(voltage_range))
        except DAQError as e:
            raise DeviceError(u"Error getting analog outputs: {}".format(e))

    def get_digital_inputs_list(self):
        try:
            buffer_size = 1000
            read = create_string_buffer(buffer_size)
            DAQmxGetDevDILines(self.card_address, read, buffer_size)
            return read.value.decode().replace(self.card_address + "/", "").split(", ")
        except DAQError:
            raise DeviceError(u"Error getting digital inputs")

    def get_digital_outputs_list(self):
        buffer_size = 1000
        read = create_string_buffer(buffer_size)
        DAQmxGetDevDOLines(self.card_address, read, buffer_size)
        return read.value.decode().replace(self.card_address + "/", "").split(", ")

    def get_counters_list(self):
        buffer_size = 1000
        read = create_string_buffer(buffer_size)
        DAQmxGetDevCOPhysicalChans(self.card_address, read, buffer_size)
        return read.value.decode().replace(self.card_address + "/", "").split(", ")

    def read_digital_input(self):
        try:
            self.read_di_task = self.task("get_digital_output_task")
            self.add_active_task(self.read_di_task, "get_digital_output_task")
            self.read_di_task.CreateDIChan("{}/port0/line0:7".format(self.card_address), "", DAQmx_Val_ChanForAllLines)
            self.read_di_task.CreateDIChan("{}/port1/line0:7".format(self.card_address), "",
                                           DAQmx_Val_ChanForAllLines)
            self.read_di_task.CreateDIChan("{}/port2/line0:7".format(self.card_address), "",
                                           DAQmx_Val_ChanForAllLines)
            self.start_task(self.read_di_task.taskHandle.value)
            task_buffer = np.zeros([100], dtype=uInt8)
            read = int32()
            bytesPerSamp = int32()
            DAQmxReadDigitalLines(self.read_di_task.taskHandle.value, 1, 10.0, DAQmx_Val_GroupByChannel, task_buffer,
                                  100, byref(read), byref(bytesPerSamp), None)
            for i, di_line in enumerate(self[GROUP_DI].keys()):
                self.set_value([GROUP_DI, di_line], task_buffer[i])
            self.stop_task("get_digital_output_task")
        except DAQError:
            raise DeviceError(u"Error getting digital outputs")

    def read_digital_output(self):
        try:
            self.read_do_task = self.task("get_digital_input_task")
            self.add_active_task(self.read_do_task, "get_digital_input_task")
            self.read_do_task.CreateDOChan("{}/port0/line0:7".format(self.card_address), "", DAQmx_Val_ChanForAllLines)
            self.read_do_task.CreateDOChan("{}/port1/line0:7".format(self.card_address), "",
                                           DAQmx_Val_ChanForAllLines)
            self.read_do_task.CreateDOChan("{}/port2/line0:7".format(self.card_address), "",
                                           DAQmx_Val_ChanForAllLines)
            self.start_task(self.read_do_task.taskHandle.value)
            task_buffer = np.zeros([1000], dtype=uInt8)
            read = int32()
            bytesPerSamp = int32()
            DAQmxReadDigitalLines(self.read_do_task.taskHandle.value, 1, 10.0, DAQmx_Val_GroupByChannel, task_buffer,
                                  100, byref(read), byref(bytesPerSamp), None)
            for i, do_line in enumerate(self[GROUP_DO].keys()):
                self.set_value([GROUP_DO, do_line], task_buffer[i])
            self.stop_task("get_digital_input_task")
        except DAQError:
            raise DeviceError(u"Error getting digital inputs")

    def set_digital_output(self, line, value):
        try:
            self.write_do_task = self.task("set_digital_output_task")
            self.add_active_task(self.write_do_task, "set_digital_output_task")
            self.write_do_task.CreateDOChan("{}/{}".format(self.card_address, line), "", DAQmx_Val_ChanForAllLines)
            self.start_task(self.write_do_task.taskHandle.value)
            data = np.ndarray([1], dtype=uInt8)
            data[0] = int(value)
            DAQmxWriteDigitalLines(self.write_do_task.taskHandle.value, 1, 1, 10.0, DAQmx_Val_GroupByChannel, data,
                                   None, None)
            self.stop_task("set_digital_output_task")
        except DAQError as e:
            print(e)
            raise DeviceError(u"Error setting digital output")

    def stop_task(self, task_name):
        self.logger.debug(u"Clearing task {}".format(task_name))
        task_name = "{}_{}".format(self.device_id, task_name)
        try:
            self.active_tasks[task_name][0].ClearTask()
            # task_handle = self.active_tasks[task_name][1]
            # DAQmxStopTask(task_handle)
            # DAQmxClearTask(task_handle)
            del self.active_tasks[task_name]
        except DAQError as e:
            raise DeviceError(e)

    def start_task(self, task_handle):
        self.logger.debug(u"Starting task {}".format(task_handle))
        try:
            DAQmxStartTask(task_handle)
        except DAQError as e:
            raise DeviceError(e)

    @expose_method()
    def stop_all_tasks(self):
        for task_handle in list(self.active_tasks.keys())[:]:
            self.stop_task(task_handle)

    def add_active_task(self, task, task_name, task_resources=None):
        task_name = "{}_{}".format(self.device_id, task_name)
        self.active_tasks[task_name] = (task, task.taskHandle.value, task_resources)

    def command(self, command, callback=None, with_token=False):
        raise DeviceError(u"Not accepting commands")

    def close(self):
        """
        Handle all devices closing stuff here.
        Close socket, close port, etc...        `
        """
        if self.closing:
            return False
        else:
            self.closing = True
            self.connected = False
            self.set_status(STATUS_DISCONNECTING)
            self.stop_all_tasks()
            self.set_status(STATUS_DISCONNECTED)
            self.closing = False
            self.connected = False
