import os
from unittest import TestCase
from swarmrob.utils import config

DIR = os.path.dirname(__file__)
TEST_CONFIG = DIR + "/swarmrob_test.conf"


class TestInit(TestCase):
    def test_default_init(self):
        try:
            config.Config()
        except Exception:
            self.fail(msg="The config should load an empty config instead of throwing an exception")

    def test_non_existing_config(self):
        try:
            cfg = config.Config()
            cfg._load_config(file="non_existing_file.ini")
        except Exception:
            self.fail(msg="The config should load an empty config instead of throwing an exception")

    def test_existing_config(self):
        try:
            cfg = config.Config()
            cfg._load_config(file=TEST_CONFIG)
            val = cfg.get(config.Section.INTERNET, config.Option.INTERFACE)
            self.assertIsNotNone(val, msg="Config was not loaded correctly. Does the config file exist? " + TEST_CONFIG)
        except Exception:
            self.fail(msg="The config should load an empty config instead of throwing an exception")


class TestGet(TestCase):
    def setUp(self):
        self.cfg = config.Config()
        self.cfg._load_config(file=TEST_CONFIG)

    def test_get(self):
        val = self.cfg.get(config.Section.INTERNET, config.Option.INTERFACE)
        self.assertEqual('eth0', val, msg="Config not loaded correctly")

    def test_with_strings(self):
        val = self.cfg.get("Internet", "interface")
        self.assertEqual('eth0', val, msg="Config not loaded correctly")

    def test_none(self):
        val = self.cfg.get(None, None)
        self.assertEqual(None, val, msg="Config not loaded correctly")

    def test_wrong_object(self):
        val = self.cfg.get(1, 3.0)
        self.assertEqual(None, val, msg="Config not loaded correctly")


class TestGetBoolean(TestCase):
    def setUp(self):
        self.cfg = config.Config(file="tests/swarmrob_test.conf")

    def test_get_boolean(self):
        val = self.cfg.get_boolean(config.Section.LOGGING, config.Option.LOGGING_ENABLED)
        self.assertEqual(True, val, msg="Config not loaded correctly")

    def test_with_strings(self):
        val = self.cfg.get_boolean("Logging", "enabled")
        self.assertEqual(True, val, msg="Config not loaded correctly")

    def test_none(self):
        val = self.cfg.get_boolean(None, None)
        self.assertEqual(None, val, msg="Config not loaded correctly")

    def test_wrong_object(self):
        val = self.cfg.get_boolean(1, 3.0)
        self.assertEqual(None, val, msg="Config not loaded correctly")


