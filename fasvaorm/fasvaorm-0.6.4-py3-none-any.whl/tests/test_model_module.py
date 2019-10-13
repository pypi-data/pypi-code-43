# -*- coding: utf-8 -*-
# ex: set tabstop=4 expandtab:
# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@hs-emden-leer.de.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import uuid
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from time import sleep

from sqlalchemy.exc import IntegrityError

import fasvaorm
from fasvaorm import Module, AvailableDrive, ProcessedDrive, FailedDrive
from tests.base import EngineTestCase

from itertools import repeat

class TestModuleAdd(EngineTestCase):

    def test_add_single_module(self):
        """
        Try to add a new module
        """
        m = Module(name='Test')

        with fasvaorm.session() as session:
            session.add(m)
            session.commit()

            modules = session.query(Module).filter_by(name='Test').all()

            self.assertEqual(1, len(modules))
            self.assertEqual('Test', modules[0].name)

    def test_add_multiple_modules(self):
        """
        Try to add multiple modules
        """
        test_names = ['Test1', 'Test2', 'Test3']
        modules = [Module(name=n) for n in test_names]

        with fasvaorm.session() as session:
            session.add_all(modules)

            session.commit()

            modules = session.query(Module).all()

            names = [m.name for m in modules]

            for n in names:
                self.assertIn(n, test_names)

    def test_add_modules_with_same_name(self):
        """
        Try to add two modules with the same name - this should raise an Exception.
        """

        with fasvaorm.session() as session:
            # create the first module
            module = Module(name=str(uuid.uuid4()))
            session.add(module)
            session.commit()

            # create the second one with the same name
            module = Module(name=module.name)
            session.add(module)

            # the mysql server should raise an integrity error
            with self.assertRaises(IntegrityError):
                session.commit()
                session.close()


class TestAvailableDrive(EngineTestCase):

    def test_add_available_drive(self):
        drive = AvailableDrive(name='TestDrive')

        with fasvaorm.session() as session:
            session.add(drive)

            session.commit()

            drives = session.query(AvailableDrive).all()

            self.assertEqual(1, len(drives))
            self.assertEqual('TestDrive', drives[0].name)

    def test_add_available_drive_non_unique_name(self):
        """
        Test if an IntegrityError is raised if a user tries to add two drives with the same name
        """
        with fasvaorm.session() as session:
            drive = AvailableDrive(name='TestDrive')
            session.add(drive)

            drive2 = AvailableDrive(name='TestDrive')
            session.add(drive2)

            with self.assertRaises(IntegrityError):
                session.commit()


@fasvaorm.isolate
def _insert_drive(iddrive, idmodule, timestamp):
    with fasvaorm.session() as session:
        drive = FailedDrive(idavailable_drive=iddrive, idmodule=idmodule, timestamp=timestamp)

        session.add(drive)
        session.commit()


class TestAddDrives(EngineTestCase):

    def setUp(self):
        super().setUp()

        self.session = fasvaorm.init_session()

        # add a test module
        self.module = Module(name='TestModule')
        self.session.add(self.module)

        # add a test drive
        self.drive = AvailableDrive(name='TestDrive')
        self.session.add(self.drive)

        self.session.commit()

    def tearDown(self):
        fasvaorm.close_session(self.session)

        super().tearDown()

    def test_add_processed_drive(self):
        processed_drive = ProcessedDrive(drive=self.drive, module=self.module)

        self.session.add(processed_drive)
        self.session.commit()

        processed_drives = self.session.query(ProcessedDrive).all()

        self.assertEqual(1, len(processed_drives))
        self.assertEqual('TestDrive', processed_drives[0].drive.name)
        self.assertEqual('TestModule', processed_drives[0].module.name)

    def test_add_processed_drive_multiple_times_at_same_time(self):
        """
        Test if an exception is raised when we try indicate that a drive was processed by a module multiple times at
        the same point in time.
        """

        timestamp = datetime.now()
        processed_drive = ProcessedDrive(drive=self.drive, module=self.module, timestamp=timestamp)

        self.session.add(processed_drive)
        self.session.commit()

        processed_drive = ProcessedDrive(drive=self.drive, module=self.module, timestamp=timestamp)

        self.session.add(processed_drive)

        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_add_processed_drive_multiple_times_different_times(self):
        """
        Test if it is fine to indicate that a drive was processed by a module multiple times if they differ on their
        occurrence.
        """

        processed_drive = ProcessedDrive(drive=self.drive, module=self.module, timestamp=datetime.now())

        self.session.add(processed_drive)
        self.session.commit()

        # wait two second to take care that the drives were not processed at the same time
        sleep(2)

        processed_drive = ProcessedDrive(drive=self.drive, module=self.module, timestamp=datetime.now())

        self.session.add(processed_drive)
        self.session.commit()

        drives = self.session.query(ProcessedDrive).all()

        self.assertEqual(2, len(drives))

        # the name of the drive should equal
        self.assertEqual(drives[0].drive.name, drives[1].drive.name)

        # but the timestamp should differ
        self.assertNotEqual(drives[0].timestamp, drives[1].timestamp)

    def test_add_failed_drive(self):
        failed_drive = FailedDrive(drive=self.drive, module=self.module)

        self.session.add(failed_drive)
        self.session.commit()

        failed_drive = self.session.query(FailedDrive).all()

        self.assertEqual(1, len(failed_drive))
        self.assertEqual('TestDrive', failed_drive[0].drive.name)
        self.assertEqual('TestModule', failed_drive[0].module.name)

    def test_add_failed_drive_multiple_times_same_time(self):
        """
        Test if an exception is raised when we try indicate that drive was processed by a module multiple times at
        the same point in time.
        """
        timestamp = datetime.now()
        processed_drive = ProcessedDrive(drive=self.drive, module=self.module, timestamp=timestamp)

        self.session.add(processed_drive)
        self.session.commit()

        processed_drive = ProcessedDrive(drive=self.drive, module=self.module, timestamp=timestamp)

        self.session.add(processed_drive)

        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_add_failed_drive_multiple_times_different_times(self):
        """
        Test if it is fine to indicate that a module failed to process a drive multiple times if they differ on their
        occurrence.
        """

        drive = FailedDrive(drive=self.drive, module=self.module, timestamp=datetime.now())

        self.session.add(drive)
        self.session.commit()

        # wait two second to take care that the drives were not processed at the same time
        sleep(2)

        drive = FailedDrive(drive=self.drive, module=self.module, timestamp=datetime.now())

        self.session.add(drive)
        self.session.commit()

        drives = self.session.query(FailedDrive).all()

        self.assertEqual(2, len(drives))

        # the name of the drive should equal
        self.assertEqual(drives[0].drive.name, drives[1].drive.name)

        # but the timestamp should differ
        self.assertNotEqual(drives[0].timestamp, drives[1].timestamp)

    def test_add_multiple_drives_in_parallel(self):
        with ProcessPoolExecutor() as pool:
            list(pool.map(_insert_drive, repeat(self.drive.idavailable_drive), repeat(self.module.idmodule),
                          [datetime.now() + timedelta(seconds=s) for s in range(5)], timeout=None,
                          chunksize=1))

        with fasvaorm.session() as session:
            failed_drives = session.query(FailedDrive).all()

        self.assertEqual(len(failed_drives), 5)


class TestRemoveDrives(EngineTestCase):

    def setUp(self):
        super().setUp()

        self.session = fasvaorm.init_session()
        # add a test module
        self.module = Module(name='TestModule')
        self.session.add(self.module)

        # add a test drive
        self.drive = AvailableDrive(name='TestDrive')
        self.session.add(self.drive)

        self.session.commit()

    def tearDown(self):
        fasvaorm.close_session(self.session)

        super().tearDown()

    def test_add_processed_drive(self):
        processed_drive = ProcessedDrive(drive=self.drive, module=self.module)

        self.session.add(processed_drive)
        self.session.commit()

        processed_drives = self.session.query(ProcessedDrive).all()

        self.assertEqual(1, len(processed_drives))
        self.assertEqual('TestDrive', processed_drives[0].drive.name)
        self.assertEqual('TestModule', processed_drives[0].module.name)

        self.session.delete(processed_drives[0])
        self.session.commit()

        self.assertEqual(0, len(self.session.query(ProcessedDrive).all()))

    def test_add_failed_drive(self):
        failed_drive = FailedDrive(drive=self.drive, module=self.module)

        self.session.add(failed_drive)
        self.session.commit()

        failed_drive = self.session.query(FailedDrive).all()

        self.assertEqual(1, len(failed_drive))
        self.assertEqual('TestDrive', failed_drive[0].drive.name)
        self.assertEqual('TestModule', failed_drive[0].module.name)

        self.session.delete(failed_drive[0])
        self.session.commit()

        self.assertEqual(0, len(self.session.query(ProcessedDrive).all()))
