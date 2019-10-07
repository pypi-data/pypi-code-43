from assertpy import assert_that
from controlpyweb.io_definitions.analog_io import AnalogOut
from controlpyweb.io_definitions.discrete_io import DiscreteIn, DiscreteOut
from controlpyweb.webio_module import WebIOModule
import unittest
import json

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


class TestOverloads(unittest.TestCase):

    def setUp(self):
        module.loads(incoming)
        self.incoming = json.loads(incoming)    # type: dict

    def test_and_operator(self):
        module.Lamp1 = True
        module.Lamp2 = True
        assert_that(module.Lamp1 and module.Lamp2).is_true()

        module.Lamp2 = False
        assert_that(module.Lamp1 and module.Lamp2).is_false()

        assert_that(module.Lamp1 and True).is_true()
        assert_that(module.Lamp1 and False).is_false()

        assert_that(True and module.Lamp1).is_true()
        assert_that(False and module.Lamp1).is_false()

    def test_bool(self):
        module.Lamp1 = True
        result = False
        if module.Lamp1:
            result = True
        assert_that(result).is_true()

    def test_gt_lt_eq(self):
        module.Temp1 = 50
        module.Temp2 = 100
        assert_that(module.Temp1 < module.Temp2).is_true()
        assert_that(module.Temp2 > module.Temp1).is_true()

        module.Temp1 = 100
        assert_that(module.Temp1 == module.Temp2)
        assert_that(module.Temp1).is_equal_to(module.Temp2)
        assert_that(module.Temp2 >= module.Temp1).is_true()
        assert_that(module.Temp2 <= module.Temp1).is_true()

    def test_modulo(self):
        module.Temp1 = 10
        module.Temp2 = 3
        assert_that(module.Temp1 % 3).is_equal_to(1)
        assert_that(module.Temp1 % module.Temp2).is_equal_to(1)

    def test_coersion(self):
        module.Temp1 = 50
        assert_that(float(module.Temp1)).is_equal_to(50)
        assert_that(int(module.Temp1)).is_equal_to(50)
        assert_that(bool(module.Temp1)).is_true()
