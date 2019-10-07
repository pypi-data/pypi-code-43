from unittest import mock

from controlpyweb.errors import ControlPyWebAddressNotFoundError, WebIOConnectionError
from controlpyweb.io_definitions.discrete_io import DiscreteIn, DiscreteOut
from controlpyweb.io_definitions.analog_io import AnalogOut
from controlpyweb.webio_module import WebIOModule
from assertpy import assert_that
import unittest
import json
import time

incoming = '''
    {
    "vin":"23.6",
    "register1":"0",
    "device1DigitalInput1":"1",
    "device1DigitalInput2":"0",
    "device1DigitalInput3":"0",
    "device1DigitalInput4":"0",
    "device1DigitalInput5":"0",
    "device1DigitalInput6":"0",
    "device1DigitalInput7":"0",
    "device1DigitalInput8":"0",
    "redLamp":"1",
    "amberLamp":"1",
    "greenLamp":"0",
    "flashLamp":"0",
    "allowStart":"0",
    "device2Relay6":"0",
    "device2Relay7":"0",
    "device2Relay8":"0",
    "utcTime":"1559533814",
    "timezoneOffset":"-25200",
    "serialNumber":"00:0C:C8:04:24:B2",
    "temperature1":"87",
    "temperature2":"75"
    } 
'''


class Module(WebIOModule):
    member_len = 7
    Button1 = DiscreteIn("Button1", "device1DigitalInput1", units="On/Off")
    Button2 = DiscreteIn("Button2", "device1DigitalInput2", units="Start/Stop")
    Button3 = DiscreteIn("Button3", "device1DigitalInput3")
    Lamp1 = DiscreteOut("Lamp1", "redLamp")
    Lamp2 = DiscreteOut("Lamp2", "amberLamp")
    Temp1 = AnalogOut("Temp1", "temperature1", units="DegF")
    Temp2 = AnalogOut("Temp2", "temperature2")


module = Module("testme")
module.update_reads_on_write = True

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self):
            pass
        def json(self):
            return json.loads(incoming)
    return MockResponse()


class TestReadWrite(unittest.TestCase):

    def setUp(self):
        module.loads(incoming)
        module.update_reads_on_write = True
        self.incoming = json.loads(incoming)    # type: dict

    def test_can_read_common_properties(self):
        assert_that(module.serial_number).is_equal_to("00:0C:C8:04:24:B2")
        assert_that(module.vin).is_equal_to(23.6)
        assert_that(module.time_of_read.day).is_equal_to(2)

    def test_can_read_values(self):
        assert_that(module.Button1).is_true()
        assert_that(module.Button2).is_false()

    def test_can_write_values(self):
        module.Lamp1 = True
        assert_that(module.read("redLamp")).is_true()
        module.Lamp1 = False
        assert_that(module.read("redLamp")).is_false()

    def test_that_changes_are_captured(self):
        module.Lamp1 = not module.Lamp1
        module.Lamp2 = not module.Lamp2
        keys = module.changes
        assert_that(keys).contains('redLamp')
        assert_that(keys).contains('amberLamp')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_that_can_read_values_from_hardware(self, mock_get):
        global incoming
        incoming = incoming.replace(':"0"', ':"1"')
        module.Button1.addr = "device1DigitalInput1"
        module.update_from_hardware()
        assert_that(module.Button1).is_true()
        assert_that(module.Button2).is_true()
        assert_that(module.Button3).is_true()

        incoming = incoming.replace(':"1"', ':"0"')
        module.update_from_hardware()
        assert_that(module.Button1).is_false()
        assert_that(module.Button2).is_false()
        assert_that(module.Button3).is_false()

    def test_that_trying_to_read_non_existing_register_gives_error(self):
        j = json.dumps(dict(dummy=False))
        module.loads(j)
        module.demand_address_exists = True
        try:
            module.Button1 is True
            assert_that(True).is_false()
        except ControlPyWebAddressNotFoundError as ex:
            pass

    def test_that_writing_duplicate_has_no_affect(self):
        module.Lamp1 = not module.Lamp1
        changes = module.dumps(changes_only=True)
        assert_that(changes).is_not_empty()
        module.flush_changes()
        module.Lamp1 = module.Lamp1
        changes = module.dumps(changes_only=True)
        assert_that(changes).is_empty()

    def test_setting_one_equal_to_another(self):
        module.Lamp1 = True
        module.Lamp2 = False
        assert_that(module.Lamp1).is_not_equal_to(module.Lamp2)
        module.Lamp2 = module.Lamp1
        assert_that(module.Lamp1).is_equal_to(module.Lamp2)

    def test_arithmetic_operations(self):
        module.Temp1 = 10.0
        module.Temp2 = 20.0

        assert_that(module.Temp1 + module.Temp2).is_equal_to(30)
        assert_that(module.Temp1 * module.Temp2).is_equal_to(200)
        assert_that(module.Temp2 / module.Temp1).is_equal_to(2)
        assert_that(module.Temp2 - module.Temp1).is_equal_to(10)

    def test_should_be_able_to_read_units(self):
        assert_that(module.Button1.units).is_equal_to("On/Off")
        assert_that(module.Temp1.units).is_equal_to("DegF")

    def test_can_get_members_list(self):
        assert_that(len(module.members)).is_equal_to(module.member_len)

    def test_module_creates_correct_json(self):
        j = module.dumps()
        print(j)

    def test_that_non_matching_address_gives_error(self):
        try:
            module.demand_address_exists = True
            module.Button1.addr = "changed"
            module.loads(incoming)
            print(module.Button1.read())
            assert_that(True).is_false()
        except ControlPyWebAddressNotFoundError:
            pass

    def test_that_can_disable_force_address_match(self):
        module.Button1.addr = "changed"
        module.demand_address_exists = False
        module.loads(incoming)
        print(module.Button1.read())

    def test_turn_off_writes_update_reads(self):
        module.Temp1 = 33
        assert_that(module.Temp1).is_equal_to(33)

        module.update_reads_on_write = False
        module.Temp1 = 34
        assert_that(module.Temp1).is_equal_to(33)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_read_hardware_update_time(self, mock_get):
        t = module.last_hardware_read_time
        assert_that(t).is_none()
        module.update_from_hardware()
        t = module.last_hardware_read_time
        diff = 1000 * (time.time() - t)
        assert_that(diff).is_between(0, 0.1)
        print(diff)

