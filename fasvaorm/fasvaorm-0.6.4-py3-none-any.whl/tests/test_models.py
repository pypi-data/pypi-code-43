import random
from datetime import datetime, timedelta

import fasvaorm
from fasvaorm.models import Base, Vehicle, Drive, Sensor, Unit, Valuetype, Signal, Aggregation, Record, Driver, \
    signal_table_name, Campaign, Maneuver, DrivingPrimitive, DrivingPrimitiveInDrive
from fasvaorm.signal import create_signal_table, _TYPE_MIXIN_MAP
from tests.base import EngineTestCase

TEST_VEHICLE = {'serial_number': "ABC", 'dimension_width': 2000, 'dimension_height': 1500, 'dimension_length': 5000,
                'description': None}
TEST_DRIVE = {'start': datetime.now(), 'end': datetime.now() + timedelta(seconds=5), 'name': 'Testdrive'}
TEST_SENSOR = {'name': 'TestSensor', 'description': 'The testsensor is only for testing purposes.'}
TEST_UNIT = {'name': "km/h"}
TEST_SCENE_VALUE = 10.55
TEST_VALUETYPE = {'name': type(TEST_SCENE_VALUE).__name__}
TEST_SIGNAL = {'name': "TestSignal"}
TEST_AGGREGATION = {'timestamp': datetime.now()}
TEST_RECORD = {'start_mileage': 0, 'end_mileage': 100, 'drive_length': 100, 'start_time': datetime.now(),
               'end_time': datetime.now() + timedelta(minutes=60), 'filepath': "/opt/test/test_record.json"
               }
TEST_CAMPAIGN = dict(name="TestCampaign", start=datetime.now(), end=datetime.now() + timedelta(hours=5),
                     description='I am a test campaign')
TEST_DRIVER = {'name': "Testdriver", 'sex': "male", 'weight': 110, 'height': 180}

TEST_MANEUVER = {'name': 'TestManeuver', 'start': datetime.now(), 'end': datetime.now()}


class TestDriver(EngineTestCase):

    def test_create(self):
        """Test if we can add add a new driver"""

        entity = Driver(**TEST_DRIVER)

        session = fasvaorm.init_session()

        session.add(entity)
        session.commit()

        retval = session.query(Driver).filter_by(name=entity.name).first()

        self.assertIsNotNone(retval)


class TestSensor(EngineTestCase):

    def test_create_sensor(self):
        """Test if we can add the test sensor."""

        session = fasvaorm.init_session()

        entity = Sensor(**TEST_SENSOR)
        session.add(entity)

        session.commit()

        retval = session.query(Sensor).filter_by(name=entity.name).first()

        self.assertIsNotNone(retval)


class TestUnit(EngineTestCase):

    def test_create_unit(self):
        """Test if we can add a unit to our database"""

        session = fasvaorm.init_session()

        unit = Unit(**TEST_UNIT)
        session.add(unit)
        session.commit()

        retval = session.query(Unit).filter_by(name=unit.name).first()

        self.assertIsNotNone(retval)


class TestValuetype(EngineTestCase):

    def test_create_unit(self):
        """Test if we can add the a signal type to our database"""

        session = fasvaorm.init_session()

        valuetype = Valuetype(**TEST_VALUETYPE)
        session.add(valuetype)
        session.commit()

        retval = session.query(Valuetype).filter_by(name=valuetype.name).first()

        self.assertIsNotNone(retval)


class TestVehicle(EngineTestCase):

    def test_create_vehicle(self):
        """Test if we can add a vehicle to our database"""

        session = fasvaorm.init_session()

        entity = Vehicle(**TEST_VEHICLE)
        session.add(entity)
        session.commit()

        retval = session.query(Vehicle).filter_by(serial_number=entity.serial_number).first()

        self.assertIsNotNone(retval)
        self.assertIsNotNone(retval.idvehicle)


class TestCampaign(EngineTestCase):

    def test_create_drive(self):
        """Test if we can add a campaignto our database
        """
        session = fasvaorm.init_session()

        # add the test vehicle
        campaign = Campaign(**TEST_CAMPAIGN)

        session.add(campaign)
        session.commit()

        retval = session.query(Campaign).filter_by(description=campaign.description).first()

        self.assertEqual(TEST_CAMPAIGN['description'], retval.description), 'The descriptions do not equal'

        self.assertIsNotNone(retval)


class TestDrive(EngineTestCase):

    def test_create_drive(self):
        """Test if we can add the a drive which depends on a vehicle to our database
        """

        session = fasvaorm.init_session()

        drive = Drive(**TEST_DRIVE)
        drive.vehicle = Vehicle(**TEST_VEHICLE)
        drive.driver = Driver(**TEST_DRIVER)
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        session.add(drive)
        session.commit()

        retval = session.query(Drive).filter_by(name=drive.name).first()

        self.assertEqual(TEST_DRIVE['start'], retval.start), 'The datetimes do not equal'
        self.assertIsNotNone(retval)


class TestRecord(EngineTestCase):

    def test_add_entity(self):
        """Test if we can add a new record including dependencies to the database."""

        session = fasvaorm.init_session()

        drive = Drive(**TEST_DRIVE)
        drive.vehicle = Vehicle(**TEST_VEHICLE)
        drive.driver = Driver(**TEST_DRIVER)
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        record = Record(**TEST_RECORD)
        record.drive = drive

        session.add(record)
        session.commit()

        retval = session.query(Record).filter_by(filepath=record.filepath).first()

        self.assertIsNotNone(retval)


class TestManeuver(EngineTestCase):

    def test_add_entity(self):
        """Test if we can add a new maneuver including dependencies to the database."""

        session = fasvaorm.init_session()

        drive = Drive(**TEST_DRIVE)
        drive.vehicle = Vehicle(**TEST_VEHICLE)
        drive.driver = Driver(**TEST_DRIVER)
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        session.add(drive)

        agg1 = Aggregation(timestamp=datetime.now())
        agg1.drive = drive

        agg2 = Aggregation(timestamp=datetime.now())
        agg2.drive = drive

        mano = Maneuver(name='testmaneuver')
        mano.start_scene = agg1
        mano.end_scene = agg2

        session.add(mano)
        session.commit()

        retval = session.query(Maneuver).filter_by(name='testmaneuver').first()

        self.assertIsNotNone(retval)

        self.assertEqual(agg1.timestamp, retval.start_scene.timestamp)
        self.assertEqual(agg2.timestamp, retval.end_scene.timestamp)


class TestDrivingPrimitive(EngineTestCase):

    def test_add_entity(self):
        """Test if we can add a new maneuver including dependencies to the database."""

        session = fasvaorm.init_session()

        drive = Drive(**TEST_DRIVE)
        drive.vehicle = Vehicle(**TEST_VEHICLE)
        drive.driver = Driver(**TEST_DRIVER)
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        session.add(drive)

        agg1 = Aggregation(timestamp=datetime.now())
        agg1.drive = drive

        agg2 = Aggregation(timestamp=datetime.now())
        agg2.drive = drive

        mano = Maneuver(name='testmaneuver')
        mano.start_scene = agg1
        mano.end_scene = agg2

        session.add(mano)
        session.commit()

        retval = session.query(Maneuver).filter_by(name='testmaneuver').first()

        self.assertIsNotNone(retval)

        self.assertEqual(agg1.timestamp, retval.start_scene.timestamp)
        self.assertEqual(agg2.timestamp, retval.end_scene.timestamp)

    def test_create_primitive(self):
        session = fasvaorm.init_session()

        dp = DrivingPrimitive(name='approach_lane_marking')

        session.add(dp)
        session.commit()

        retval = session.query(DrivingPrimitive).filter_by(name='approach_lane_marking').first()

        self.assertIsNotNone(retval)

        self.assertEqual('approach_lane_marking', retval.name)

    def test_add_driving_primitive(self):
        session = fasvaorm.init_session()

        drive = Drive(**TEST_DRIVE)
        drive.vehicle = Vehicle(**TEST_VEHICLE)
        drive.driver = Driver(**TEST_DRIVER)
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        session.add(drive)

        agg1 = Aggregation(timestamp=datetime.now())
        agg1.drive = drive

        agg2 = Aggregation(timestamp=datetime.now())
        agg2.drive = drive

        dp = DrivingPrimitive(name='approach_lane_marking')

        dpid = DrivingPrimitiveInDrive()

        dpid.driving_primitive = dp
        dpid.start_scene = agg1
        dpid.end_scene = agg2

        session.add(dpid)
        session.commit()

        retval = session.query(DrivingPrimitiveInDrive).first()

        self.assertIsNotNone(retval)

        self.assertEqual(agg1.timestamp, retval.start_scene.timestamp)
        self.assertEqual(agg2.timestamp, retval.end_scene.timestamp)


class TestSignalEntryAdd(EngineTestCase):

    def test_add_new_signal_entry(self):
        """
        Test if we can add a new signal to the signal table
        """

        session = fasvaorm.init_session()

        # each signal has a unit, valuetype and a sensor it belongs to
        signal = Signal(**TEST_SIGNAL)
        signal.valuetype = Valuetype(**TEST_VALUETYPE)
        signal.sensor = Sensor(**TEST_SENSOR)
        signal.unit = Unit(**TEST_UNIT)

        session.add(signal)
        session.commit()

        result = session.query(Signal).filter_by(name=signal.name).first()

        self.assertIsNotNone(result)


class TestAggregatedSignalTableCreation(EngineTestCase):

    def setUp(self):
        super().setUp()

        self.session = fasvaorm.init_session()
        # populate the database with the required test data
        signal = Signal(**TEST_SIGNAL)
        signal.valuetype = Valuetype(**TEST_VALUETYPE)
        signal.sensor = Sensor(**TEST_SENSOR)
        signal.unit = Unit(**TEST_UNIT)

        self.session.add(signal)
        self.session.commit()

        self.signal = self.session.query(Signal).filter_by(name=signal.name).first()

    def test_signal_table_creation_based_on_signal_entry(self):
        """Test if we can create a new aggregated signal table"""

        # get the value type of the signal
        valuetype = self.session.query(Valuetype).get(self.signal.idvaluetype)

        # create a new signal table based on this type
        create_signal_table(Base.metadata, Base, self.signal.name, valuetype.name, True)

        # let the engine metadata update its internal model according to the tables in the database
        Base.metadata.reflect(self.engine)

        # now check if our previously created table exists
        self.assertTrue(signal_table_name(self.signal.name, True) in Base.metadata.tables.keys())

    def test_insert_into_created_table(self):
        """Test if we can insert a new entry to a dynamically created aggregated signal table."""

        drive = Drive(**TEST_DRIVE)
        drive.vehicle = Vehicle(**TEST_VEHICLE)
        drive.driver = Driver(**TEST_DRIVER)
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        # we have to add an entry to the aggregation table
        aggregation = Aggregation(**TEST_AGGREGATION)
        aggregation.drive = drive
        self.session.add(aggregation)
        self.session.commit()

        # get the value type of the signal
        valuetype = self.session.query(Valuetype).get(self.signal.idvaluetype)

        # create a new signal table based on this type
        model, table = create_signal_table(Base.metadata, Base, self.signal.name, valuetype.name, True)

        # let the engine metadata update its internal model according to the tables in the database
        Base.metadata.reflect(self.engine)

        test_data = {
            'value': 500,
            'timestamp': datetime.now(),
            'idaggregation': aggregation.idaggregation
        }

        insert_statement = table.insert().values(**test_data)
        self.session.execute(insert_statement)
        self.session.commit()

        result = self.session.query(table).all()
        self.assertEqual(1, len(result), 'Check if only one result is returned.')

        for key in test_data:
            self.assertEqual(test_data[key], getattr(result[0], key))


class TestSignalTableCreation(EngineTestCase):

    def setUp(self):
        super().setUp()

        self.session = fasvaorm.init_session()
        # populate the database with the required test data
        signal = Signal(**TEST_SIGNAL)
        signal.valuetype = Valuetype(**TEST_VALUETYPE)
        signal.sensor = Sensor(**TEST_SENSOR)
        signal.unit = Unit(**TEST_UNIT)

        self.session.add(signal)
        self.session.commit()

        self.signal = self.session.query(Signal).filter_by(name=signal.name).first()

    def test_signal_table_creation_based_on_signal_entry(self):
        """Test if we can create a new signal table"""

        # get the value type of the signal
        valuetype = self.session.query(Valuetype).get(self.signal.idvaluetype)

        # create a new signal table based on this type
        create_signal_table(Base.metadata, Base, self.signal.name, valuetype.name, aggregated=False)

        self.session.commit()

        # let the engine metadata update its internal model according to the tables in the database
        Base.metadata.reflect(self.engine)

        # now check if our previously created table exists
        self.assertTrue(signal_table_name(self.signal.name) in Base.metadata.tables.keys())

    def test_insert_into_created_table(self):
        """Test if we can insert a new entry to a dynamically created signal table."""

        # add the test vehicle
        vehicle = Vehicle(**TEST_VEHICLE)
        driver = Driver(**TEST_DRIVER)
        drive = Drive(**TEST_DRIVE)
        drive.vehicle = vehicle
        drive.driver = driver
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        scene = Aggregation(**TEST_AGGREGATION)
        scene.drive = drive

        self.session.add(scene)
        self.session.commit()

        test_data = {
            'timestamp': datetime.now(),
            'idaggregation': scene.idaggregation,
            'value': TEST_SCENE_VALUE
        }

        # get the value type of the signal
        valuetype = self.session.query(Valuetype).get(self.signal.idvaluetype)

        # create a new signal table based on this type
        model, table = create_signal_table(Base.metadata, Base, self.signal.name, valuetype.name)

        self.session.commit()

        # let the engine metadata update its internal model according to the tables in the database
        Base.metadata.reflect(self.engine)

        entity = model(**test_data)

        self.session.add(entity)
        self.session.commit()

        result = self.session.query(table).all()

        self.assertEqual(1, len(result))

        for key in test_data:
            self.assertEqual(test_data[key], getattr(result[0], key))

        # access the signal id
        self.assertGreaterEqual(getattr(result[0], 'id{}'.format(table.name)), 0)


class TestSignalTableCreationMultiple(EngineTestCase):

    def setUp(self):
        super().setUp()

        self.session = fasvaorm.init_session()
        # populate the database with the required test data
        signal = Signal(**TEST_SIGNAL)
        signal.valuetype = Valuetype(**TEST_VALUETYPE)
        signal.sensor = Sensor(**TEST_SENSOR)
        signal.unit = Unit(**TEST_UNIT)

        self.session.add(signal)
        self.session.commit()

        self.signal = self.session.query(Signal).filter_by(name=signal.name).first()

    def test_create_multiple_signal_tables(self):
        # add the test vehicle
        vehicle = Vehicle(**TEST_VEHICLE)
        driver = Driver(**TEST_DRIVER)
        drive = Drive(**TEST_DRIVE)
        drive.vehicle = vehicle
        drive.driver = driver
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        scene = Aggregation(**TEST_AGGREGATION)
        scene.drive = drive

        self.session.add(scene)
        self.session.commit()

        [create_signal_table(Base.metadata, Base, "{}".format(i), random.choice(list(_TYPE_MIXIN_MAP.keys()))) for i in
         range(100)]

        self.session.commit()
        for i in range(100):
            model, table = create_signal_table(Base.metadata, Base, "{}".format(i),
                                               random.choice(list(_TYPE_MIXIN_MAP.keys())))

            test_data = {
                'timestamp': datetime.now(),
                'idaggregation': scene.idaggregation,
                'value': None
            }

            ins = table.insert()

            self.session.execute(ins, test_data)

            r = self.session.query(model).filter(model.idaggregation == test_data['idaggregation']).first()

            self.assertEqual(test_data['timestamp'], r.timestamp)
