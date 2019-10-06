import unittest
from xml.etree import ElementTree

from midpoint_cli.mpclient import MidpointUser


class ClientModeltest(unittest.TestCase):
    def test_model_user01(self):
        with open('sample-user-01.xml', 'r') as f:
            tree = ElementTree.fromstring(f.read())
            user = MidpointUser(xml_entity=tree)
            self.assertEqual(None, user['FullName'])

    def test_model_user02(self):
        with open('sample-user-02.xml', 'r') as f:
            tree = ElementTree.fromstring(f.read())
            user = MidpointUser(xml_entity=tree)
            self.assertEqual('Lieutenant Templeton Arthur Peck', user['FullName'])


if __name__ == '__main__':
    unittest.main()
