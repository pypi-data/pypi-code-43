# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_timeaccount



class TimeAccountTestCase(ModuleTestCase):
    'Test time account module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_timeaccount_create_valid(self):
        """ test: create valid time account
        """
        Account = Pool().get('employee_timetracking.timeaccount')
        
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            acc1 = create_timeaccount(
                    name='Account 1', 
                    shortname='A1', 
                    company=Account.default_company(),
                    color=Account.default_color())
            self.assertTrue(acc1)
            self.assertEqual(acc1.name, 'Account 1')
            self.assertEqual(acc1.shortname, 'A1')
            self.assertEqual(acc1.company.party.name, 'm-ds 1')
            self.assertEqual(acc1.color.name, 'Azure')
            self.assertEqual(acc1.color.rgbcode, '#007FFF')
    
    @with_transaction()
    def test_timeaccount_create_item_same_name(self):
        """ test: create time account, create 2nd with same name
        """
        Account = Pool().get('employee_timetracking.timeaccount')
        
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            acc1 = create_timeaccount(
                    name='Account 1', 
                    shortname='A1', 
                    company=Account.default_company())
            self.assertTrue(acc1)
            self.assertEqual(acc1.name, 'Account 1')
            self.assertEqual(acc1.shortname, 'A1')
            self.assertEqual(acc1.company.party.name, 'm-ds 1')

            acc_obj = Account(
                name='Account 1', 
                shortname='A1a', 
                company=Account.default_company()
                )
            self.assertRaisesRegex(UserError,
                "This name is already in use.",
                acc_obj.save)

    @with_transaction()
    def test_timeaccount_create_item_same_shortname(self):
        """ test: create time account, create 2nd with same shortname
        """
        Account = Pool().get('employee_timetracking.timeaccount')
        
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            acc1 = create_timeaccount(
                    name='Account 1', 
                    shortname='A1', 
                    company=Account.default_company())
            self.assertTrue(acc1)
            self.assertEqual(acc1.name, 'Account 1')
            self.assertEqual(acc1.shortname, 'A1')
            self.assertEqual(acc1.company.party.name, 'm-ds 1')

            acc_obj = Account(
                name='Account 1a', 
                shortname='A1', 
                company=Account.default_company())
            self.assertRaisesRegex(UserError,
                "This shorthand symbol is already in use.",
                acc_obj.save)

    @with_transaction()
    def test_timeaccount_two_equal_items_two_companies(self):
        """ test: create two time accounts, in two companies
        """
        Account = Pool().get('employee_timetracking.timeaccount')
        
        company1 = create_company('m-ds 1')
        company2 = create_company('m-ds 2')
        self.assertTrue(company1)
        with set_company(company1):
            acc1 = create_timeaccount(
                    name='Account 1', 
                    shortname='A1', 
                    company=company1)
            self.assertTrue(acc1)
            self.assertEqual(acc1.name, 'Account 1')
            self.assertEqual(acc1.shortname, 'A1')
            self.assertEqual(acc1.company.party.name, 'm-ds 1')

            acc2 = create_timeaccount(
                    name='Account 1', 
                    shortname='A1', 
                    company=company2)
            self.assertTrue(acc2)
            self.assertEqual(acc2.name, 'Account 1')
            self.assertEqual(acc2.shortname, 'A1')
            self.assertEqual(acc2.company.party.name, 'm-ds 2')

# end TimeAccountTestCase
