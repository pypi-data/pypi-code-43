from datetime import datetime

import numpy

import fasvaorm
from fasvaorm.models import signal_table_name, Vehicle, Driver, Campaign, Aggregation
from fasvaorm.signal import create_signal_table
from tests.base import EngineTestCase

from tests.test_models import TEST_SIGNAL, TEST_VALUETYPE, TEST_SENSOR, TEST_UNIT, TEST_DRIVE, TEST_VEHICLE, \
    TEST_DRIVER, TEST_CAMPAIGN, TEST_AGGREGATION

from fasvaorm import Signal, Valuetype, Sensor, Unit, Base, Drive


class TestNumpyTypesInsert(EngineTestCase):

    def setUp(self):
        super().setUp()

        self.sensor = Sensor(**TEST_SENSOR)
        self.unit = Unit(**TEST_UNIT)

        drive = Drive(**TEST_DRIVE)
        drive.vehicle = Vehicle(**TEST_VEHICLE)
        drive.driver = Driver(**TEST_DRIVER)
        drive.campaign = Campaign(**TEST_CAMPAIGN)

        # we have to add an entry to the aggregation table
        self.aggregation = Aggregation(**TEST_AGGREGATION)
        self.aggregation.drive = drive

        self.session = fasvaorm.init_session()
        self.session.add(self.aggregation)
        self.session.commit()

    def test_insert_numpy_float(self):

        # populate the database with the required test data
        signal = Signal(name='float_signal',
                        valuetype=Valuetype(name="float"),
                        sensor=self.sensor,
                        # unit=self.unit
                        )

        self.session.add(signal)
        self.session.commit()

        # get the entry of the previously added signal
        signal = self.session.query(Signal).filter_by(name=signal.name).first()

        # get the value type of the signal
        valuetype = self.session.query(Valuetype).get(signal.idvaluetype)

        # create a new signal table based on this type
        model, table = create_signal_table(Base.metadata, Base, signal.name, valuetype.name, True)

        # let the engine metadata update its internal model according to the tables in the database
        Base.metadata.reflect(self.engine)

        test_data = {
            'value': numpy.float64(3.6),
            'timestamp': datetime.now(),
            'idaggregation': self.aggregation.idaggregation
        }

        insert_statement = table.insert().values(**test_data)
        self.session.execute(insert_statement)
        self.session.commit()

        result = self.session.query(table).all()
        self.assertEqual(1, len(result), 'Check if only one result is returned.')

        for key in test_data:
            self.assertEqual(test_data[key], getattr(result[0], key))

        self.assertEqual(3.6, result[0].value)

    def test_insert_numpy_integer(self):

        # populate the database with the required test data
        signal = Signal(name='integer_signal',
                        valuetype=Valuetype(name="int"),
                        sensor=self.sensor,
                        # unit=self.unit
                        )

        self.session.add(signal)
        self.session.commit()

        # get the entry of the previously added signal
        signal = self.session.query(Signal).filter_by(name=signal.name).first()

        # get the value type of the signal
        valuetype = self.session.query(Valuetype).get(signal.idvaluetype)

        # create a new signal table based on this type
        model, table = create_signal_table(Base.metadata, Base, signal.name, valuetype.name, True)

        # let the engine metadata update its internal model according to the tables in the database
        Base.metadata.reflect(self.engine)

        test_data = {
            'value': numpy.int32(112),
            'timestamp': datetime.now(),
            'idaggregation': self.aggregation.idaggregation
        }

        insert_statement = table.insert().values(**test_data)
        self.session.execute(insert_statement)
        self.session.commit()

        result = self.session.query(table).all()
        self.assertEqual(1, len(result), 'Check if only one result is returned.')

        for key in test_data:
            self.assertEqual(test_data[key], getattr(result[0], key))

        self.assertEqual(112, result[0].value)
