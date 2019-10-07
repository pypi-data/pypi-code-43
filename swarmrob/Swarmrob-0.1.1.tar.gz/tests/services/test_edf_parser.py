import os
from unittest import TestCase
from swarmrob.services import edf_parser
from swarmrob.utils.errors import CompositionException

DIR = os.path.dirname(__file__)
EMPTY_FILE = DIR + "/edf_empty.yaml"
VERSION_FILE = DIR + "/edf_version.yaml"
SIMPLE_SERVICE_FILE = DIR + "/edf_simple_service.yaml"
MULTIPLE_SERVICES_FILE = DIR + "/edf_multiple_services.yaml"
COMMENT_FILE = DIR + "/edf_comment.yaml"
MALFORMED_FILE = DIR + "/edf_malformed.yaml"
COMPLEX_FILE = DIR + "/edf_complex.yaml"


class TestEdfParser(TestCase):
    def test_non_existent_file(self):
        composition = edf_parser.create_service_composition_from_edf("non_existent_file.yaml")
        self.assertTrue(composition.is_empty())

    def test_empty_file(self):
        composition = edf_parser.create_service_composition_from_edf(EMPTY_FILE)
        self.assertTrue(composition.is_empty())

    def test_version_file(self):
        composition = edf_parser.create_service_composition_from_edf(VERSION_FILE)
        self.assertEqual("3", composition._version)
        self.assertTrue(composition.is_empty())

    def test_simple_service(self):
        composition = edf_parser.create_service_composition_from_edf(SIMPLE_SERVICE_FILE)
        self.assertFalse(composition.is_empty())
        self.assertEqual(1, composition.get_service_count())
        service = composition.get_service(composition.get_service_key_list()[0])
        self.assertEqual("foo", service._id)
        self.assertEqual("hello-world", service._tag)

    def test_multiple_services(self):
        composition = edf_parser.create_service_composition_from_edf(MULTIPLE_SERVICES_FILE)
        self.assertFalse(composition.is_empty())
        self.assertEqual(4, composition.get_service_count())
        correct_ids = ["foo", "bar", "baz", "foobar"]
        correct_tags = ["hello-world", "hello-python", "hello-minden", "hello-foobar"]
        ids = []
        tags = []
        for service_key in composition.get_service_key_list():
            service = composition.get_service(service_key)
            ids.append(service._id)
            tags.append(service._tag)
        self.assertEqual(sorted(correct_ids), sorted(ids))
        self.assertEqual(sorted(correct_tags), sorted(tags))

    def test_correct_assignment(self):
        composition = edf_parser.create_service_composition_from_edf(MULTIPLE_SERVICES_FILE)
        self.assertEqual("hello-python", composition._services["bar"]._tag)
        self.assertEqual("hello-foobar", composition._services["foobar"]._tag)

    def test_comment(self):
        composition = edf_parser.create_service_composition_from_edf(COMMENT_FILE)
        self.assertFalse(composition.is_empty())
        self.assertEqual(1, composition.get_service_count())

    def test_malformed(self):
        try:
            edf_parser.create_service_composition_from_edf(MALFORMED_FILE)
            self.fail(msg="Malformed edf files should not be loaded")
        except CompositionException:
            pass


class TestEdfComplex(TestCase):
    def setUp(self):
        self.master_id = "rosmaster"
        self.camera_id = "camera"
        self.composition = edf_parser.create_service_composition_from_edf(COMPLEX_FILE)

    def test_version(self):
        self.assertEqual("3", self.composition._version)

    def test_service_count(self):
        self.assertEqual(2, self.composition.get_service_count())

    def test_service_existence(self):
        self.assertIsNotNone(self.composition._services.get(self.master_id))
        self.assertIsNotNone(self.composition._services.get(self.camera_id))

    def test_key_id_equality(self):
        self.assertEqual(self.master_id, self.composition._services.get(self.master_id)._id)
        self.assertEqual(self.camera_id, self.composition._services.get(self.camera_id)._id)

    def test_service_images(self):
        self.assertEqual("repository:5000/ros-master", self.composition._services.get(self.master_id)._tag)
        self.assertEqual("repository:5000/ros-smart-camera", self.composition._services.get(self.camera_id)._tag)

    def test_environment(self):
        master = self.composition._services[self.master_id]
        camera = self.composition._services[self.camera_id]
        self.assertEqual("hm_rosmaster_1", master._environment.get("ROS_IP"))
        self.assertEqual("http://rosmaster_1:11311", camera._environment.get("ROS_URI"))
        self.assertEqual("Cam", camera._environment.get("CAMERA_NAME"))

    def test_depends_on(self):
        camera = self.composition._services[self.camera_id]
        self.assertEqual({"rosmaster"}, camera._dependsOn)

    def test_devices(self):
        camera = self.composition._services[self.camera_id]
        self.assertEqual(list(["/dev/video0:/dev/video0:rwm"]), camera._devices)

    def test_volumes(self):
        camera = self.composition._services[self.camera_id]
        self.assertEqual({
            "/var/run/acpid.socket": {
                "bind": "/var/run/acpid.socket",
                "mode": "rw"
            }}, camera._volumes)
