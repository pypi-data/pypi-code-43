#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import os
import shutil
import tempfile
import unittest

from myorm.dbobject import DbObject
from myorm.exceptions import TooManyResultsError
from myorm.fields import BooleanField, CharField, DateTimeField, ForeignKey, IntegerField, TextField
from myorm.adaptors.sqlite import TestAdaptor
from myorm.migrations import Migration

# from myorm.adaptors.mysql import MySQLAdaptor
# DbObject.adaptor = MySQLAdaptor(
#     {'host': 'localhost', 'user': 'myorm', 'db': 'myorm', 'use_unicode': True, 'charset': 'utf8'}
# )

DbObject.adaptor = TestAdaptor()

print("# Running tests with %s" % DbObject.adaptor.__class__.__name__)


class Driver(DbObject):
    name = CharField(max_length=10)


class Car(DbObject):
    wheels = IntegerField(default=4)
    seats = IntegerField(default=5)
    manufacturer = CharField(max_length=120)
    description = TextField()
    motorcycle = BooleanField(default=False)
    built = DateTimeField()
    driver = ForeignKey(Driver)


class Bus(DbObject):
    driver = ForeignKey(Driver, reverse_name='busses')


class TestMethods(unittest.TestCase):

    def setUp(self):
        Driver.create_table()
        self.driver = Driver.objects.create(name='Harry')
        Car.create_table()
        self.car1 = Car.objects.create(wheels=4, manufacturer='Mercedes', seats=5, driver=self.driver)
        self.car2 = Car.objects.create(wheels=4, manufacturer='BMW', seats=3)
        self.car3 = Car.objects.create(wheels=4, manufacturer='Porsche', seats=2, built=datetime.now())
        self.car4 = Car.objects.create(wheels=2, manufacturer='Harley Davidson', seats=2, motorcycle=True)
        Bus.create_table()
        Bus.objects.create(driver=self.driver)

    def test_create_instance(self):
        """ Creates a car and should return an object with an id """

        suzuki = Car.objects.create(wheels=2, manufacturer='Suzuki')
        self.assertEqual(type(suzuki.id), int)
        self.assertEqual(suzuki.wheels, 2)
        self.assertTrue(isinstance(suzuki, Car))
        self.assertTrue(isinstance(suzuki, DbObject))

    def test_save_instance(self):
        """ Tests the save() method in instances"""
        suzuki = Car(wheels=4, seats=5)
        suzuki.save()
        self.assertEqual(suzuki.wheels, 4)
        self.assertEqual(suzuki.seats, 5)

        suzuki.wheels = 6
        suzuki.seats = 10
        suzuki.save()

        new_inst = Car.objects.get(id=suzuki.id)
        self.assertEqual(new_inst.wheels, 6)
        self.assertEqual(new_inst.seats, 10)
        self.assertEqual(new_inst.seats, 10)

        vw = Car(wheels=4, manufacturer='VW')
        vw.save()
        self.assertEqual(type(vw.id), int)
        self.assertEqual(vw.manufacturer, 'VW')

        vw.manufacturer = 'Opel'
        opel = Car.objects.get(id=vw.id)
        self.assertEqual(opel.manufacturer, 'VW')

        vw.save()
        opel = Car.objects.get(id=vw.id)
        self.assertEqual(opel.manufacturer, 'Opel')

    def test_filter(self):
        """ Some filter tests """

        self.assertEqual(Car.objects.filter(id=10000).count(), 0)
        self.assertEqual(Car.objects.filter(manufacturer='Mercedes')[0].wheels, 4)

    def test_all(self):
        """ Tests the objecs.all() method """

        self.assertEqual(len(Car.objects.all()), len(Car.objects.filter()))

    def test_get(self):
        """ Tests the get method. """

        self.assertEqual(Car.objects.get(manufacturer='Mercedes').id, Car.objects.get(seats=5).id)
        with self.assertRaises(TooManyResultsError):
            Car.objects.get(wheels=4)

    def test_in_filters(self):
        """ Tests the __in filter """

        self.assertEqual(len(Car.objects.filter(manufacturer__in=['BMW', 'Porsche'])), 2)

    def test_lte_gte_filters(self):
        """ Tests the __lte, __lt, __gte and __gt filter """

        # Single filters:
        self.assertEqual(len(Car.objects.filter(seats__lte=3)), 3)
        self.assertEqual(len(Car.objects.filter(seats__lt=3)), 2)
        self.assertEqual(len(Car.objects.filter(seats__gte=3)), 2)
        self.assertEqual(len(Car.objects.filter(seats__gt=3)), 1)

        # Combined filters:
        self.assertEqual(len(Car.objects.filter(seats__lte=3, wheels=2)), 1)
        self.assertEqual(len(Car.objects.filter(seats__lt=3, wheels=2)), 1)
        self.assertEqual(len(Car.objects.filter(seats__gte=3, manufacturer='BMW')), 1)
        self.assertEqual(len(Car.objects.filter(seats__gt=2, manufacturer='Mercedes')), 1)

        # Combined limit filters
        self.assertEqual(len(Car.objects.filter(seats__lte=3, wheels__gt=3)), 2)

    def test_order_by_filters(self):
        """ Tests the order_by filter """

        self.assertEqual(Car.objects.filter().order_by('seats')[0].manufacturer, 'Porsche')
        self.assertEqual(Car.objects.filter().order_by('-seats')[0].manufacturer, 'Mercedes')
        self.assertEqual(Car.objects.filter(seats=2).order_by('-wheels')[0].manufacturer, 'Porsche')
        self.assertEqual(Car.objects.filter(seats=2).order_by('wheels')[0].manufacturer, 'Harley Davidson')

    def test_bulk_create_high(self):
        """ Tests the mass creation of objects """

        amount = 5324
        cars = [Car(wheels=i, seats=4, manufacturer='Lada', driver=self.driver.id, description='cheap')
                for i in range(0, amount)]
        Car.objects.bulk_create(cars)
        self.assertEqual(Car.objects.count(), amount + 4)

    def test_bulk_create_middle(self):
        """ Tests the limit amount creation of objects """

        amount = 999
        drivers = [Driver(name='Kevin') for i in range(0, amount)]
        Driver.objects.bulk_create(drivers)
        self.assertEqual(Driver.objects.count(), amount + 1)

    def test_bulk_create_low(self):
        """ Tests the lower limit amount creation of objects """

        amount = 4
        drivers = [Driver(name='Kevin') for i in range(0, amount)]
        Driver.objects.bulk_create(drivers)
        self.assertEqual(Driver.objects.count(), amount + 1)

    def test_bulk_create_one(self):
        """ Tests the lowest limit amount creation of objects """

        amount = 1
        drivers = [Driver(name='Kevin') for i in range(0, amount)]
        Driver.objects.bulk_create(drivers)
        self.assertEqual(Driver.objects.count(), amount + 1)

    def test_delete(self):
        """ Tests the deletion of objects """

        old_len = len(Car.objects.all())
        self.car1.delete()
        self.assertEqual(len(Car.objects.all()), old_len - 1)

    def test_raw_queries(self):
        """ Tests some raw queries """
        # if isinstance(DbObject.adaptor, MySQLAdaptor):
        #     PH = '%s'
        # elif isinstance(DbObject.adaptor, TestAdaptor):
        #    PH = '?'
        PH = '?'

        old_len = len(Car.objects.all())

        mercedes = DbObject.raw("SELECT id FROM car WHERE manufacturer={0}".format(PH), "Mercedes")
        self.assertEqual(len(mercedes), len(Car.objects.filter(manufacturer="Mercedes")))
        self.assertEqual(mercedes[0][0], Car.objects.get(manufacturer="Mercedes").id)

        all = DbObject.raw("SELECT id FROM car")
        self.assertEqual(len(all), old_len)

        with self.assertRaises(IndexError):
            Car.objects.get(manufacturer="General Motors")
        DbObject.raw("INSERT INTO car (wheels, seats, manufacturer) VALUES (4, 8, 'General Motors')")
        self.assertEqual(Car.objects.get(manufacturer="General Motors").seats, 8)

        with self.assertRaises(IndexError):
            Car.objects.get(manufacturer="MAN")
        DbObject.raw("INSERT INTO car (wheels, seats, manufacturer) VALUES ({0}, {0}, {0})".format(PH), 8, 39, 'MAN')
        self.assertEqual(Car.objects.get(manufacturer="MAN").seats, 39)

    def test_field_defaults(self):
        """ Tests the defaults of the fields """
        toyota = Car.objects.create(manufacturer='Toyota')
        self.assertEqual(toyota.manufacturer, 'Toyota')
        self.assertEqual(toyota.wheels, 4)
        self.assertEqual(toyota.seats, 5)

        nissan = Car.objects.create(manufacturer='Nissan', wheels=8, seats=2)
        self.assertEqual(nissan.manufacturer, 'Nissan')
        self.assertEqual(nissan.wheels, 8)
        self.assertEqual(nissan.seats, 2)

    def test_exclude(self):
        self.assertEqual(Car.objects.filter(wheels=2).count(), 1)

        cars = Car.objects.exclude(wheels=2)
        for car in cars:
            self.assertEqual(car.wheels, 4)

    def test_filter_none(self):
        cars = Car.objects.filter(driver=None)
        self.assertEqual(cars.count(), 3)

    def test_filter_none_chaining(self):
        cars = Car.objects.filter(driver=None).filter(seats=3)
        self.assertEqual(cars[0].manufacturer, 'BMW')

    def test_exclude_none(self):
        cars = Car.objects.exclude(driver=None)
        self.assertEqual(cars[0].manufacturer, 'Mercedes')

    def test_exclude_none_chaining(self):
        Car.objects.create(wheels=4, manufacturer='Trabbi', seats=3.5, built=datetime.now())
        cars = Car.objects.exclude(built=None)
        for car in cars:
            self.assertIn(car.manufacturer, ['Trabbi', 'Porsche'])

        cars = cars.exclude(manufacturer='Porsche')
        self.assertEqual(cars[0].manufacturer, 'Trabbi')

    def test_first_on_manager(self):
        car = Car.objects.first()
        self.assertEqual(car.id, 1)

    def test_first_on_queryset(self):
        Bus.objects.all().delete()
        bus = Bus.objects.all().order_by('id').first()
        self.assertIsNone(bus)

    def test_first_on_manager_without_result(self):
        Bus.objects.all().delete()
        bus = Bus.objects.first()
        self.assertIsNone(bus)

    def test_first_on_queryset_without_result(self):
        car = Car.objects.all().order_by('-id').first()
        self.assertEqual(car.id, 4)

    def test_chaining_querysets(self):
        cars = Car.objects.filter(seats=2).exclude(motorcycle=True)
        self.assertEqual(cars.count(), 1)
        self.assertEqual(cars[0].manufacturer, 'Porsche')

    def test_chaining_append_get_valid_result(self):
        cars = Car.objects.filter(wheels=4).exclude(motorcycle=True)
        self.assertEqual(cars.get(manufacturer="BMW").seats, 3)

    def test_chaining_append_get_too_many_results(self):
        cars = Car.objects.exclude(motorcycle=True)
        with self.assertRaises(TooManyResultsError):
            cars.get(wheels=4)

    def test_chaining_append_get_no_result(self):
        cars = Car.objects.filter(wheels=4).exclude(motorcycle=True)
        with self.assertRaises(IndexError):
            cars.get(manufacturer="Tesla")

    def test_update(self):
        self.assertEqual(Car.objects.filter(seats=6).count(), 0)

        Car.objects.all().update(seats=6)
        self.assertEqual(Car.objects.filter(seats=6).count(), 4)

    def test_reverse_relation_exists(self):
        self.assertEqual(self.driver.car_set.exists(), True)

    def test_reverse_relation_get(self):
        self.assertEqual(self.driver.car_set.get(manufacturer="Mercedes").manufacturer, "Mercedes")

    def test_reverse_relation_get_not_found(self):
        with self.assertRaises(IndexError):
            self.driver.car_set.get(manufacturer="Tesla")

    def test_reverse_relation_get_too_many_results(self):
        self.car2.driver = self.driver
        self.car2.save()
        with self.assertRaises(TooManyResultsError):
            self.driver.car_set.get(wheels="4")

    def test_reverse_relation_filter(self):
        self.car2.driver = self.driver
        self.car2.save()
        self.assertEqual(self.driver.car_set.filter(seats=3).count(), 1)
        self.assertEqual(self.driver.car_set.filter(seats=3)[0].manufacturer, "BMW")

    def test_reverse_relation_exclude(self):
        self.car2.driver = self.driver
        self.car2.save()
        self.assertEqual(self.driver.car_set.exclude(seats=3).count(), 1)
        self.assertEqual(self.driver.car_set.exclude(seats=3)[0].manufacturer, "Mercedes")

        self.assertEqual(self.driver.car_set.exclude(seats=5).count(), 1)
        self.assertEqual(self.driver.car_set.exclude(seats=5)[0].manufacturer, "BMW")

    def test_reverse_relation_exists_no_relation(self):
        driver = Driver.objects.create(name="Otto")
        self.assertEqual(driver.car_set.exists(), False)

    def test_reverse_relation_amount(self):
        self.assertEqual(self.driver.car_set.count(), 1)

    def test_reverse_relation_identity(self):
        self.assertEqual(self.driver.car_set.all()[0].manufacturer, "Mercedes")

    def test_reverse_relation_reverse_name(self):
        with self.assertRaises(AttributeError):
            self.driver.bus_set
        self.assertEqual(self.driver.busses.count(), 1)

        with self.assertRaises(AttributeError):
            self.driver.cars
        self.assertEqual(self.driver.car_set.count(), 1)

    def test_create_migrations(self):
        with tempfile.TemporaryDirectory() as migration_dir:
            Migration.migration_dir = migration_dir
            migration = Migration()
            self.assertEqual(os.listdir(migration_dir), [])
            migration.create_migrations()
            self.assertEqual(len(os.listdir(migration_dir)), 1)

    def test_validate_migration_file_content(self):
        with MigrationContext() as migration:
            migration_file = os.listdir(migration.migration_dir)[0]
            old_state, actions, new_state = migration.get_content_from_migration_file(migration_file)
            self.assertIsInstance(old_state, dict)
            self.assertIsInstance(actions, dict)
            self.assertIsInstance(new_state, dict)

    def test_validate_migration_file_content_actions(self):
        with MigrationContext() as migration:
            migration_file = os.listdir(migration.migration_dir)[0]
            old_state, actions, new_state = migration.get_content_from_migration_file(migration_file)
            self.assertEqual(old_state, {})
            self.assertEqual(set(actions['creations'].keys()), set(['Bus', 'Car', 'Driver']))
            self.assertEqual(new_state.keys(), set(['Bus', 'Car', 'Driver']))

    def tearDown(self):
        DbObject.adaptor.execute_query("DROP TABLE bus", None)
        DbObject.adaptor.execute_query("DROP TABLE car", None)
        DbObject.adaptor.execute_query("DROP TABLE driver", None)


class MigrationContext:
    def __enter__(self, *args):
        self.migration_dir = tempfile.mkdtemp()
        Migration.migration_dir = self.migration_dir
        migration = Migration()
        migration.create_migrations()
        return migration

    def __exit__(self, exc_type, exc_value, exc_traceback):
        shutil.rmtree(self.migration_dir)


if __name__ == '__main__':
    unittest.main()
