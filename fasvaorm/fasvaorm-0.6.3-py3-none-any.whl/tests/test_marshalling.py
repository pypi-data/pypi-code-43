from fasvaorm.schema import DriverSchema, DriveSchema
from tests.test_models import TEST_DRIVER, TEST_DRIVE

from tests.base import EngineTestCase


class TestDriver(EngineTestCase):

    def test_create(self):
        """Test if we can add add a new driver"""

        s = DriverSchema(many=False)
        s.load(TEST_DRIVER)


class TestDrive(EngineTestCase):

    def test_create(self):
        """
        Test if we can marshal a drive entry
        """
        s = DriveSchema(many=False)
        s.load({
            'name' : 'A',
            'idvehicle' : 0,
            'start' : TEST_DRIVE['start'].isoformat(),
            'end' : TEST_DRIVE['end'].isoformat()
        })

