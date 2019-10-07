# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.modules.employee_timetracking.tests.testlib import create_company, \
    set_company, create_holiday
from datetime import date


class HolidayTestCase(ModuleTestCase):
    'Test holiday module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_holiday_create_item(self):
        """ test: create holiday
        """
        Holiday = Pool().get('employee_timetracking.holiday')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            hd1 = create_holiday('Mayday', date(2018, 5, 1), 
                    company=Holiday.default_company(),
                    repyear=True,
                    halfday=Holiday.default_halfday(),
                )
            self.assertTrue(hd1)
            self.assertEqual(hd1.name, 'Mayday')
            self.assertEqual(str(hd1.date), '2018-05-01')
            self.assertEqual(hd1.company.party.name, 'm-ds')
            self.assertEqual(str(hd1.repyear), 'True')
            self.assertEqual(str(hd1.halfday), 'False')

    @with_transaction()
    def test_holiday_create_item_two_compnies(self):
        """ test: create holiday in two companies
        """
        Holiday = Pool().get('employee_timetracking.holiday')
        
        company1 = create_company('m-ds')
        company2 = create_company('m-ds 2')
        with set_company(company1):
            hd1 = create_holiday('Mayday', date(2018, 5, 1), 
                    company=Holiday.default_company(),
                    repyear=True,
                    halfday=Holiday.default_halfday(),
                )
            self.assertTrue(hd1)
            self.assertEqual(hd1.name, 'Mayday')
            self.assertEqual(str(hd1.date), '2018-05-01')
            self.assertEqual(hd1.company.party.name, 'm-ds')
            self.assertEqual(str(hd1.repyear), 'True')
            self.assertEqual(str(hd1.halfday), 'False')

        with set_company(company2):
            hd2 = create_holiday('Mayday', date(2018, 5, 1), 
                    company=Holiday.default_company(),
                    repyear=True,
                    halfday=Holiday.default_halfday(),
                )
            self.assertTrue(hd2)
            self.assertEqual(hd2.name, 'Mayday')
            self.assertEqual(str(hd2.date), '2018-05-01')
            self.assertEqual(hd2.company.party.name, 'm-ds 2')
            self.assertEqual(str(hd2.repyear), 'True')
            self.assertEqual(str(hd2.halfday), 'False')

    @with_transaction()
    def test_holiday_create_item_same_name(self):
        """ test: create two holiday-item with same name
        """
        Holiday = Pool().get('employee_timetracking.holiday')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            hd1 = create_holiday('Mayday', date(2018, 5, 1), 
                    company=Holiday.default_company(),
                    repyear=True,
                    halfday=Holiday.default_halfday(),
                )
            self.assertTrue(hd1)
            self.assertEqual(hd1.name, 'Mayday')
            self.assertEqual(str(hd1.date), '2018-05-01')

            hobj = Holiday(
                    name='Mayday',
                    date=date(2018, 5, 2), 
                    company=company1, 
                    repyear=True,
                    halfday=False
                )
            self.assertRaisesRegex(UserError, 
                "This name is already in use.",
                hobj.save)

    @with_transaction()
    def test_holiday_create_item_same_date(self):
        """ test: create two holiday-item with same date
        """
        Holiday = Pool().get('employee_timetracking.holiday')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            hd1 = create_holiday('Mayday', date(2018, 5, 1), 
                    company=Holiday.default_company(),
                    repyear=True,
                    halfday=Holiday.default_halfday(),
                )
            self.assertTrue(hd1)
            self.assertEqual(hd1.name, 'Mayday')
            self.assertEqual(str(hd1.date), '2018-05-01')

            hobj = Holiday(
                    name='Mayday2',
                    date=date(2018, 5, 1), 
                    company=company1, 
                    repyear=True,
                    halfday=False
                )
            self.assertRaisesRegex(UserError, 
                "This date is already in use.",
                hobj.save)

    @with_transaction()
    def test_holiday_is_holiday(self):
        """ test: create holiday-items, test function 'is_holiday'
        """
        Holiday = Pool().get('employee_timetracking.holiday')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            hd1 = create_holiday('Mayday', date(2018, 5, 1),  company=company1, repyear=True, halfday=False)
            self.assertTrue(hd1)
            self.assertEqual(hd1.name, 'Mayday')
            self.assertEqual(str(hd1.date), '2018-05-01')

            hd2 = create_holiday('Easter monday', date(2018, 4, 2),  company=company1, repyear=False, halfday=False)
            self.assertTrue(hd2)
            self.assertEqual(hd2.name, 'Easter monday')
            self.assertEqual(str(hd2.date), '2018-04-02')

            self.assertEqual(Holiday.is_holiday(date(2018, 5, 1), company1), True)
            self.assertEqual(Holiday.is_holiday(date(2018, 5, 2), company1), False)
            self.assertEqual(Holiday.is_holiday(date(2019, 5, 1), company1), True)
            self.assertEqual(Holiday.is_holiday(date(2018, 4, 2), company1), True)
            self.assertEqual(Holiday.is_holiday(date(2019, 4, 2), company1), False)

    @with_transaction()
    def test_holiday_is_weekend(self):
        """ test: test function 'is_weekend'
        """
        Holiday = Pool().get('employee_timetracking.holiday')
        self.assertEqual(Holiday.is_weekend(date(2018, 4, 27)), False)
        self.assertEqual(Holiday.is_weekend(date(2018, 4, 28)), True)
        self.assertEqual(Holiday.is_weekend(date(2018, 4, 29)), True)
        self.assertEqual(Holiday.is_weekend(date(2018, 4, 30)), False)

# end HolidayTestCase
