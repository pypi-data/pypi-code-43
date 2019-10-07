# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import timedelta
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from decimal import Decimal
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_employee, create_trytonuser


class EmployeeTestCase(ModuleTestCase):
    'Test employee module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_employee_holidays(self):
        """ test: holidays of employee
        """
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            employee = create_employee(company, name='Frida')
            self.assertTrue(employee)
            
            employee.holidays = 25
            employee.specleave = 5
            employee.save()
            self.assertEqual(str(employee.holidays), '25')
            self.assertEqual(str(employee.specleave), '5')

    @with_transaction()
    def test_employee_holidays_not_neg(self):
        """ test: holidays of employee not neg
        """
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            employee = create_employee(company, name='Frieda')
            self.assertTrue(employee)
            
            employee.holidays = -25
            self.assertRaisesRegex(UserError,
                "'Holidays' must be positive",
                employee.save)

    @with_transaction()
    def test_employee_specleave_not_neg(self):
        """ test: specleave of employee not neg
        """
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            employee = create_employee(company, name='Frida')
            self.assertTrue(employee)
            
            employee.specleave = -5
            self.assertRaisesRegex(UserError,
                "'Special leave' must be positive",
                employee.save)

    @with_transaction()
    def test_employee_trytonuser(self):
        """ test: get tryton user of employee
        """
        pool = Pool()
        Employee = pool.get('company.employee')
        
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # add tryton user
            usr1 = create_trytonuser('frida', 'Test.1234')
            usr1.main_company = company
            usr1.company = company
            usr1.save()
            self.assertTrue(usr1)
            self.assertEqual(usr1.name, 'frida')
            self.assertEqual(usr1.login, 'frida')
            self.assertEqual(usr1.employees, ())
            self.assertEqual(usr1.employee, None)
            self.assertEqual(usr1.company.rec_name, 'm-ds 1')
            self.assertEqual(usr1.main_company.rec_name, 'm-ds 1')

            employee = create_employee(company, name='Frida')
            self.assertTrue(employee)

            # add employee to tryton user
            self.assertEqual(employee.trytonuser, None)
            usr1.employees = [employee]
            usr1.employee = employee
            usr1.save()
            self.assertEqual(employee.trytonuser.name, 'frida')
            
            e_lst = Employee.search([('trytonuser.name', '=', 'frida')])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].party.name, 'Frida')
            self.assertEqual(e_lst[0].trytonuser.name, 'frida')
            
            e_lst = Employee.search([('trytonuser.login', 'in', ['frida', 'diego'])])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].trytonuser.name, 'frida')
            
            e_lst = Employee.search([('trytonuser.id', 'in', [usr1.id])])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].trytonuser.name, 'frida')

            e_lst = Employee.search([('trytonuser.id', '=', usr1.id)])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].trytonuser.name, 'frida')

# end EmployeeTestCase
