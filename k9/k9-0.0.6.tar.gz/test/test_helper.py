from unittest import TestCase
from k9.helper import *
import pprint

from k9.pretty_object import PrettyObject

po = PrettyObject()

pp = pprint.PrettyPrinter(indent=2, width=120)
class TestCron(TestCase):

    def test_create_namespace(self):
        set_default_namespace("unit-test")
        
        create_namespace()
        self.assertTrue(namespace_exists())

        delete_namespace()
        self.assertFalse(namespace_exists())

    def test_yaml(self):
        view_yaml('craft-deploy-dev.yml')
