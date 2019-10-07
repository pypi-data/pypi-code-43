# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_presence


class TypeOfPresenceTestCase(ModuleTestCase):
    'Test type-of-presence module'
    module = 'employee_timetracking'

    def prep_presence(self):
        """ create company and 1st presence item
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create type-of-presence
            # defaults are applied: company
            Presence = Pool().get('employee_timetracking.presence')
            presence = create_presence(name='Work', shortname='W', company=Presence.default_company())
        return presence
        
    @with_transaction()
    def test_presence_create_work_day_item(self):
        """ test: create a presence-item, use some defaults
        """
        presence = self.prep_presence()
        
        # check values
        self.assertEqual(presence.name, 'Work')
        self.assertEqual(presence.shortname, 'W')

    @with_transaction()
    def test_presence_create_item_twice_same_name(self):
        """ test: create the presence-item twice in same company, same name
        """
        presence = self.prep_presence()
        Presence = Pool().get('employee_timetracking.presence')
        
        with set_company(presence.company):
            # 2nd items
            # same name
            pr_obj = Presence(
                name='Work', shortname='W1', 
                company=Presence.default_company(),
                )
            self.assertRaisesRegex(UserError, 
                "This name is already in use.",
                pr_obj.save)
        
    @with_transaction()
    def test_presence_create_item_twice_same_shortname(self):
        """ test: create the presence-item twice in same company, same shortname
        """
        presence = self.prep_presence()
        Presence = Pool().get('employee_timetracking.presence')

        with set_company(presence.company):
            # same short hand symbol
            pr_obj = Presence(
                name='Work2', shortname='W', 
                company=Presence.default_company(),
                )
            self.assertRaisesRegex(UserError, 
                "This shorthand symbol is already in use.",
                pr_obj.save)

    @with_transaction()
    def test_presence_create_two_companies_items(self):
        """ test: two companies, same workday/holiday in both companies
        """
        Presence = Pool().get('employee_timetracking.presence')
        
        # 1st company
        company1 = create_company('m-ds 1')
        self.assertTrue(company1)
        with set_company(company1):
            # 2nd company
            company2 = create_company('m-ds 2')
            self.assertTrue(company2)
    
            # 1st company, workday
            self.assertTrue(
                create_presence(name='Workday', shortname='W', \
                    company=Presence.default_company()
                    )
                )
            self.assertTrue(
                create_presence(name='Holiday half', shortname='HH', \
                    company=Presence.default_company()
                    )
                )

            # 2nd company, workday
            self.assertTrue(
                create_presence(name='Workday', shortname='W', \
                    company=company2
                    )
                )
            self.assertTrue(
                create_presence(name='Holiday half', shortname='HH', \
                    company=company2
                    )
                )

# ende TypeOfPresenceTestCase

