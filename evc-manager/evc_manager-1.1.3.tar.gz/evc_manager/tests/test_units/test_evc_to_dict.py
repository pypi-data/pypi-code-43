"""
    Test the convert_class function that converts a class to a dict.
"""


import unittest
from.backends.oess import Oess
from libs.models.evc import EthernetVirtualCircuit
from libs.models.nni import NNI
from libs.core.evc_to_dict import convert_class
from tests.test_integration.content_files.oess_outputs import OESS_REPL2
from tests.test_integration.content_files.oess_outputs import OESS_REPL3
from tests.test_integration.content_files.oess_outputs import OESS_REPL4
from tests.test_integration.content_files.oess_outputs import OESS_REPLY


class TestConvertionOfNNI(unittest.TestCase):
    """ Test all combinations for evc.name """

    def setUp(self):
        self.evc = EthernetVirtualCircuit()

        my_list = list()
        for links in ['links', 'backup_links']:
            for span in OESS_REPLY[links]:
                link = NNI()
                link.device_a = span['node_a']
                link.interface_a = span['interface_a']
                link.device_z = span['node_z']
                link.interface_z = span['interface_z']
                link.name = span['name']
                my_list.append(link)
                del link
            self.evc.paths.append(my_list[:])
            my_list.clear()

    def test_correct_convertion_to_dict(self):
        """ Test converting List of NNIs to dict"""
        converted = convert_class(self.evc.paths)
        self.assertIsInstance(converted, list)
        self.assertGreater(len(converted), 0)
        self.assertEqual(converted[0][0]['name'], 'FTLZ-MIA-100G')
        self.assertEqual(converted[0][1]['name'], 'FTLZ-SP-100G')

    def test_incorrect_empty_requested_path(self):
        """ Test converting List of NNIs to dict"""
        self.evc.paths.clear()
        converted = convert_class(self.evc.paths)
        self.assertIsInstance(converted, list)
        self.assertEqual(len(converted), 0)
        self.assertEqual(converted, self.evc.paths)


class TestOESSinput(unittest.TestCase):
    """ Use Oess Class and oess_reply as input params """

    def setUp(self):
        self.oess = Oess()

    def test_correct_evc_class_instantiation_from_oess_reply(self):
        """ Test correct EVC class using OESS reply """
        evc = self.oess.process_oess_circuit(OESS_REPLY)
        self.assertIsInstance(evc, EthernetVirtualCircuit)
        converted = convert_class(evc)
        self.assertIsInstance(converted, dict)

    def test_correct_evc_class_instantiation_from_oess_full_reply(self):
        """ Test correct EVC class using OESS reply """
        evc = self.oess.process_oess_circuit(OESS_REPL2)
        self.assertIsInstance(evc, EthernetVirtualCircuit)
        converted = convert_class(evc)
        self.assertIsInstance(converted, dict)

    def test_correct_multiple_oess_circuits(self):
        """ Test correct EVC class using OESS reply """
        oess_circuits = list()
        oess_circuits.append(OESS_REPLY)
        oess_circuits.append(OESS_REPL2)
        oess_circuits.append(OESS_REPL3)
        oess_circuits.append(OESS_REPL4)
        evcs = self.oess.process_oess_circuits(oess_circuits)
        for evc in evcs:
            self.assertIsInstance(evc, EthernetVirtualCircuit)


if __name__ == '__main__':
    unittest.main()
