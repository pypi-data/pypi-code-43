from unittest import TestCase
from swarmrob.services import service


class TestServiceInit(TestCase):
    def setUp(self):
        self.service = service.Service()

    def test_init(self):
        self.assertIsNone(self.service._id)
        self.assertIsNone(self.service._tag)
        self.assertEqual(dict(), self.service._environment)
        self.assertEqual(dict(), self.service._deploy)
        self.assertEqual(set(), self.service._dependsOn)
        self.assertEqual(dict(), self.service._volumes)
        self.assertEqual(list(), self.service._devices)


class TestServiceAddEnv(TestCase):
    def setUp(self):
        self.service = service.Service()

    def test_add_env(self):
        self.service.add_env("KEY", "VALUE")
        self.assertEqual({"KEY": "VALUE"}, self.service._environment)

    def test_add_env_twice(self):
        self.service.add_env("KEY", "VALUE")
        self.service.add_env("KEY2", "VALUE2")
        self.assertEqual({"KEY": "VALUE", "KEY2": "VALUE2"}, self.service._environment)

    def test_add_env_none_value(self):
        self.service.add_env("KEY", None)
        self.assertEqual({}, self.service._environment)

    def test_add_env_none_key(self):
        self.service.add_env(None, "VALUE")
        self.assertEqual({}, self.service._environment)

    def test_add_env_both_none(self):
        self.service.add_env(None, None)
        self.assertEqual({}, self.service._environment)

    def test_add_env_empty_value(self):
        self.service.add_env("KEY", "")
        self.assertEqual({}, self.service._environment)

    def test_add_env_empty_key(self):
        self.service.add_env("", "VALUE")
        self.assertEqual({}, self.service._environment)

    def test_add_env_empty_none(self):
        self.service.add_env("", "")
        self.assertEqual({}, self.service._environment)


class TestServiceAddDeployment(TestCase):
    def setUp(self):
        self.service = service.Service()

    def test_add_deployment(self):
        self.service.add_deployment("KEY", "VALUE")
        self.assertEqual({"KEY": "VALUE"}, self.service._deploy)

    def test_add_deployment_twice(self):
        self.service.add_deployment("KEY", "VALUE")
        self.service.add_deployment("KEY2", "VALUE2")
        self.assertEqual({"KEY": "VALUE", "KEY2": "VALUE2"}, self.service._deploy)

    def test_add_deployment_none_value(self):
        self.service.add_deployment("KEY", None)
        self.assertEqual({}, self.service._deploy)

    def test_add_deployment_none_key(self):
        self.service.add_deployment(None, "VALUE")
        self.assertEqual({}, self.service._deploy)

    def test_add_deployment_both_none(self):
        self.service.add_deployment(None, None)
        self.assertEqual({}, self.service._deploy)

    def test_add_deployment_empty_value(self):
        self.service.add_deployment("KEY", "")
        self.assertEqual({}, self.service._deploy)

    def test_add_deployment_empty_key(self):
        self.service.add_deployment("", "VALUE")
        self.assertEqual({}, self.service._deploy)

    def test_add_deployment_empty_none(self):
        self.service.add_deployment("", "")
        self.assertEqual({}, self.service._deploy)


class TestServiceAddDependency(TestCase):
    def setUp(self):
        self.service = service.Service()

    def test_add_dependency(self):
        self.service.add_dependency("VALUE")
        self.assertEqual({"VALUE"}, self.service._dependsOn)

    def test_add_dependency_twice(self):
        self.service.add_dependency("VALUE")
        self.service.add_dependency("VALUE2")
        self.assertEqual({"VALUE", "VALUE2"}, self.service._dependsOn)

    def test_add_dependency_none_value(self):
        self.service.add_dependency(None)
        self.assertEqual(set(), self.service._dependsOn)

    def test_add_dependency_empty_value(self):
        self.service.add_dependency("")
        self.assertEqual(set(), self.service._dependsOn)


class TestServiceAddVolume(TestCase):
    def setUp(self):
        self.service = service.Service()

    def test_add_volume(self):
        self.service.add_volume("KEY", "VALUE")
        self.assertEqual({"KEY": {"bind": "VALUE", "mode": "rw"}}, self.service._volumes)

    def test_add_volume_two_different(self):
        self.service.add_volume("KEY", "VALUE")
        self.service.add_volume("KEY2", "VALUE2")
        self.assertEqual({"KEY": {"bind": "VALUE", "mode": "rw"},
                         "KEY2": {"bind": "VALUE2", "mode": "rw"}}, self.service._volumes)

    def test_add_volume_same_key_twice(self):
        self.service.add_volume("KEY", "VALUE")
        self.service.add_volume("KEY", "VALUE2")
        self.assertEqual({"KEY": {"bind": "VALUE2", "mode": "rw"}}, self.service._volumes)

    def test_add_volume_none_value(self):
        self.service.add_volume("KEY", None)
        self.assertEqual({}, self.service._volumes)

    def test_add_volume_none_key(self):
        self.service.add_volume(None, "VALUE")
        self.assertEqual({}, self.service._volumes)

    def test_add_volume_both_none(self):
        self.service.add_volume(None, None)
        self.assertEqual({}, self.service._volumes)

    def test_add_volume_empty_value(self):
        self.service.add_volume("KEY", "")
        self.assertEqual({}, self.service._volumes)

    def test_add_volume_empty_key(self):
        self.service.add_volume("", "VALUE")
        self.assertEqual({}, self.service._volumes)

    def test_add_volume_empty_none(self):
        self.service.add_volume("", "")
        self.assertEqual({}, self.service._volumes)

    def test_add_volume_with_mode(self):
        self.service.add_volume("KEY", "VALUE", "r")
        self.assertEqual({"KEY": {"bind": "VALUE", "mode": "r"}}, self.service._volumes)

    def test_add_volume_empty_mode(self):
        self.service.add_volume("KEY", "VALUE", "")
        self.assertEqual({}, self.service._volumes)

    def test_add_volume_none_mode(self):
        self.service.add_volume("KEY", "VALUE", None)
        self.assertEqual({}, self.service._volumes)


class TestServiceAddDevice(TestCase):
    def setUp(self):
        self.service = service.Service()

    def test_add_device(self):
        self.service.add_device("KEY", "VALUE")
        self.assertEqual(['KEY:VALUE:rwm'], self.service._devices)

    def test_add_device_two_different(self):
        self.service.add_device("KEY", "VALUE")
        self.service.add_device("KEY2", "VALUE2")
        self.assertEqual(['KEY:VALUE:rwm', 'KEY2:VALUE2:rwm'], self.service._devices)

    def test_add_device_same_key_twice(self):
        self.service.add_device("KEY", "VALUE")
        self.service.add_device("KEY", "VALUE2")
        self.assertEqual(['KEY:VALUE2:rwm'], self.service._devices)

    def test_add_device_none_value(self):
        self.service.add_device("KEY", None)
        self.assertEqual([], self.service._devices)

    def test_add_device_none_key(self):
        self.service.add_device(None, "VALUE")
        self.assertEqual([], self.service._devices)

    def test_add_device_both_none(self):
        self.service.add_device(None, None)
        self.assertEqual([], self.service._devices)

    def test_add_device_empty_value(self):
        self.service.add_device("KEY", "")
        self.assertEqual([], self.service._devices)

    def test_add_device_empty_key(self):
        self.service.add_device("", "VALUE")
        self.assertEqual([], self.service._devices)

    def test_add_device_empty_none(self):
        self.service.add_device("", "")
        self.assertEqual([], self.service._devices)

    def test_add_device_with_mode(self):
        self.service.add_device("KEY", "VALUE", "r")
        self.assertEqual(['KEY:VALUE:r'], self.service._devices)

    def test_add_device_empty_mode(self):
        self.service.add_device("KEY", "VALUE", "")
        self.assertEqual([], self.service._devices)

    def test_add_device_none_mode(self):
        self.service.add_device("KEY", "VALUE", None)
        self.assertEqual([], self.service._devices)


class TestServiceAreDependenciesStarted(TestCase):
    def setUp(self):
        self.service = service.Service()

    def test_are_dependencies_started_true(self):
        self.service.add_dependency("ONE")
        self.service.add_dependency("TWO")
        self.assertTrue(self.service.are_dependencies_started(["ONE", "TWO"]))

    def test_are_dependencies_started_false(self):
        self.service.add_dependency("ONE")
        self.service.add_dependency("TWO")
        self.assertFalse(self.service.are_dependencies_started(["ONE"]))

    def test_are_dependencies_started_no_dependencies(self):
        self.assertTrue(self.service.are_dependencies_started(["ONE", "TWO"]))

    def test_are_dependencies_started_none_started(self):
        self.service.add_dependency("ONE")
        self.service.add_dependency("TWO")
        self.assertFalse(self.service.are_dependencies_started(None))

    def test_are_dependencies_started_none_started_no_dependencies(self):
        self.assertTrue(self.service.are_dependencies_started(None))

    def test_are_dependencies_started_empty_started(self):
        self.service.add_dependency("ONE")
        self.service.add_dependency("TWO")
        self.assertFalse(self.service.are_dependencies_started([]))

    def test_are_dependencies_started_empty_started_no_dependencies(self):
        self.assertTrue(self.service.are_dependencies_started([]))
