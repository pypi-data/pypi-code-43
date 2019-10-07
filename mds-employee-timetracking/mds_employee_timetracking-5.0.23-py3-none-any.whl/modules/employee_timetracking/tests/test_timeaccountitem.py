# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from datetime import time, datetime, date, timedelta
from decimal import Decimal
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_timeaccountitem, \
    create_period, create_tariff_full, create_employee, create_evaluation
from trytond.modules.employee_timetracking.const import ACRULE_HOLIDAY_NODEF


class TimeAccountItemTestCase(ModuleTestCase):
    'Test time account item module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_timeaccountitem_create_valid(self):
        """ test: create valid time account item
        """
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                    ],
                accountrules=[
                        # time in localtime of company
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.5'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        self.assertEqual(len(tarobj1.accountrule), 1)
        self.assertEqual(tarobj1.accountrule[0].name, 'Work 0-24')
        self.assertEqual(str(tarobj1.accountrule[0].mintime), '00:00:00')
        self.assertEqual(str(tarobj1.accountrule[0].maxtime), '00:00:00')
        self.assertEqual(tarobj1.accountrule[0].name, 'Work 0-24')
        self.assertEqual(tarobj1.accountrule[0].account.name, 'Work')
        self.assertEqual(tarobj1.timeaccounts[0].color.name, 'Azure')
        self.assertEqual(tarobj1.presence[0].color.name, 'Black')

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
            self.assertEqual(employee1.color.name, 'Aero')

            p1 = create_period(
                    datetime(2018, 3, 26, 6, 30, 0), 
                    datetime(2018, 3, 26, 19, 35, 23), 
                    tarobj1.type_present, employee1)    # DB stores in UTC
            self.assertEqual(str(p1.startpos), '2018-03-26 06:30:00')   # UTC
            self.assertEqual(str(p1.endpos),   '2018-03-26 19:35:23')
            self.assertEqual(p1.name, '08:30 - 21:35, 2018-03-26 [W]')  # CEST
            self.assertEqual(p1.employee.party.name, 'Frida')
            self.assertEqual(p1.presence.name, 'Work')
            self.assertEqual(p1.state, 'c')
            self.assertEqual(p1.textcolor, '#000000')
            self.assertEqual(p1.bgcolor, '#7CB9E8')

            evobj = create_evaluation(employee1, date(2018, 3, 10))

            itm_obj = create_timeaccountitem(
                    employee=employee1,
                    period=p1,
                    account=tarobj1.accountrule[0].account,
                    accountrule=tarobj1.accountrule[0],
                    startpos=datetime(2018, 3, 26, 10, 0, 0),
                    endpos=datetime(2018, 3, 26, 16, 0, 0),
                    evaluation=evobj,
                )
            self.assertEqual(itm_obj.name, '12:00 - 18:00, 2018-03-26 [W1]')
            self.assertEqual(itm_obj.textcolor, '#007FFF')
            self.assertEqual(itm_obj.bgcolor, '#7CB9E8')
            self.assertEqual(itm_obj.week, 13)
            self.assertEqual(str(itm_obj.duration), '6:00:00')
            self.assertEqual(str(itm_obj.duration_wfactor), '9:00:00')

    @with_transaction()
    def test_timeaccountitem_check_get_overlaps(self):
        """ test: create time account item and check overlap
        """
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                    ],
                accountrules=[
                        # time in localtime of company
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        self.assertEqual(len(tarobj1.accountrule), 1)
        self.assertEqual(tarobj1.accountrule[0].name, 'Work 0-24')
        self.assertEqual(str(tarobj1.accountrule[0].mintime), '00:00:00')
        self.assertEqual(str(tarobj1.accountrule[0].maxtime), '00:00:00')
        self.assertEqual(tarobj1.accountrule[0].name, 'Work 0-24')
        self.assertEqual(tarobj1.accountrule[0].account.name, 'Work')

        with set_company(tarobj1.company):
            AccountItem = Pool().get('employee_timetracking.timeaccountitem')

            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            evobj = create_evaluation(employee1, date(2018, 3, 10))
            
            p1 = create_period(
                    datetime(2018, 3, 26, 6, 30, 0), 
                    datetime(2018, 3, 26, 19, 35, 23), 
                    tarobj1.type_present, employee1)    # DB stores in UTC
            self.assertEqual(str(p1.startpos), '2018-03-26 06:30:00')   # UTC
            self.assertEqual(str(p1.endpos),   '2018-03-26 19:35:23')
            self.assertEqual(p1.name, '08:30 - 21:35, 2018-03-26 [W]')  # CEST
            self.assertEqual(p1.employee.party.name, 'Frida')
            self.assertEqual(p1.presence.name, 'Work')
            self.assertEqual(p1.state, 'c')

            itm_obj = create_timeaccountitem(
                    employee=employee1,
                    period=p1,
                    account=tarobj1.accountrule[0].account,
                    accountrule=tarobj1.accountrule[0],
                    startpos=datetime(2018, 3, 26, 10, 0, 0),
                    endpos=datetime(2018, 3, 26, 16, 0, 0),
                    evaluation=evobj,
                )
            self.assertEqual(itm_obj.name, '12:00 - 18:00, 2018-03-26 [W1]')

            # deny wrong parameter
            self.assertRaisesRegex(ValueError,
                "id of employee or account invalid \(employee=None, account=%s\)" % tarobj1.accountrule[0].account.id,
                AccountItem.get_overlaps,
                id_employee=None,
                id_account=tarobj1.accountrule[0].account.id,
                startpos=datetime(2018, 3, 24, 10, 0, 0),
                endpos=datetime(2018, 3, 24, 11, 0, 0))
            self.assertRaisesRegex(ValueError,
                "id of employee or account invalid \(employee=%s, account=None\)" % employee1.id,
                AccountItem.get_overlaps,
                id_employee=employee1.id,
                id_account=None,
                startpos=datetime(2018, 3, 24, 10, 0, 0),
                endpos=datetime(2018, 3, 24, 11, 0, 0))
            self.assertRaisesRegex(ValueError,
                "startpos/endpos invalid \(startpos=1, endpos=2018-03-24 11:00:00\)",
                AccountItem.get_overlaps,
                id_employee=employee1.id,
                id_account=tarobj1.accountrule[0].account.id,
                startpos=1,
                endpos=datetime(2018, 3, 24, 11, 0, 0))
            self.assertRaisesRegex(ValueError,
                "startpos/endpos invalid \(startpos=2018-03-24 11:00:00, endpos=1\)",
                AccountItem.get_overlaps,
                id_employee=employee1.id,
                id_account=tarobj1.accountrule[0].account.id,
                startpos=datetime(2018, 3, 24, 11, 0, 0),
                endpos=1)
            
            # no overlap
            l1 = AccountItem.get_overlaps(
                    id_employee=employee1.id,
                    id_account=tarobj1.accountrule[0].account.id,
                    startpos=datetime(2018, 3, 24, 10, 0, 0),
                    endpos=datetime(2018, 3, 24, 11, 0, 0),
                    )
            self.assertEqual(len(l1), 0)

            # overlap at startpos
            l1 = AccountItem.get_overlaps(
                    id_employee=employee1.id,
                    id_account=tarobj1.accountrule[0].account.id,
                    startpos=datetime(2018, 3, 26, 9, 0, 0),
                    endpos=datetime(2018, 3, 26, 11, 0, 0),
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(l1[0], itm_obj.id)

            # overlap at endpos
            l1 = AccountItem.get_overlaps(
                    id_employee=employee1.id,
                    id_account=tarobj1.accountrule[0].account.id,
                    startpos=datetime(2018, 3, 26, 14, 0, 0),
                    endpos=datetime(2018, 3, 26, 17, 0, 0),
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(l1[0], itm_obj.id)

            # period to check is within item
            l1 = AccountItem.get_overlaps(
                    id_employee=employee1.id,
                    id_account=tarobj1.accountrule[0].account.id,
                    startpos=datetime(2018, 3, 26, 13, 0, 0),
                    endpos=datetime(2018, 3, 26, 14, 0, 0),
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(l1[0], itm_obj.id)
            
            # period to check is around item
            l1 = AccountItem.get_overlaps(
                    id_employee=employee1.id,
                    id_account=tarobj1.accountrule[0].account.id,
                    startpos=datetime(2018, 3, 26, 9, 0, 0),
                    endpos=datetime(2018, 3, 26, 17, 0, 0),
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(l1[0], itm_obj.id)

            # period to check is around item, but ignore 'itm_obj'
            l1 = AccountItem.get_overlaps(
                    id_employee=employee1.id,
                    id_account=tarobj1.accountrule[0].account.id,
                    startpos=datetime(2018, 3, 26, 9, 0, 0),
                    endpos=datetime(2018, 3, 26, 17, 0, 0),
                    ign_item=itm_obj
                    )
            self.assertEqual(len(l1), 0)

    @with_transaction()
    def test_timeaccountitem_create_item_with_overlaps(self):
        """ test: create two time account item with overlap
        """
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                    ],
                accountrules=[
                        # time in localtime of company
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        self.assertEqual(len(tarobj1.accountrule), 1)
        self.assertEqual(tarobj1.accountrule[0].name, 'Work 0-24')
        self.assertEqual(str(tarobj1.accountrule[0].mintime), '00:00:00')
        self.assertEqual(str(tarobj1.accountrule[0].maxtime), '00:00:00')
        self.assertEqual(tarobj1.accountrule[0].name, 'Work 0-24')
        self.assertEqual(tarobj1.accountrule[0].account.name, 'Work')

        with set_company(tarobj1.company):
            AccountItem = Pool().get('employee_timetracking.timeaccountitem')

            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            evobj = create_evaluation(employee1, date(2018, 3, 10))
            
            p1 = create_period(
                    datetime(2018, 3, 26, 6, 30, 0), 
                    datetime(2018, 3, 26, 19, 35, 23), 
                    tarobj1.type_present, employee1)    # DB stores in UTC
            self.assertEqual(str(p1.startpos), '2018-03-26 06:30:00')   # UTC
            self.assertEqual(str(p1.endpos),   '2018-03-26 19:35:23')
            self.assertEqual(p1.name, '08:30 - 21:35, 2018-03-26 [W]')  # CEST
            self.assertEqual(p1.employee.party.name, 'Frida')
            self.assertEqual(p1.presence.name, 'Work')
            self.assertEqual(p1.state, 'c')

            # 1st item
            itm_obj = create_timeaccountitem(
                    employee=employee1,
                    period=p1,
                    account=tarobj1.accountrule[0].account,
                    accountrule=tarobj1.accountrule[0],
                    startpos=datetime(2018, 3, 26, 10, 0, 0),
                    endpos=datetime(2018, 3, 26, 16, 0, 0),
                    evaluation=evobj,
                )
            self.assertEqual(itm_obj.name, '12:00 - 18:00, 2018-03-26 [W1]')

            # 2nd item
            # overlap at startpos
            itm_obj2 = AccountItem(
                employee=employee1,
                period=p1,
                account=tarobj1.accountrule[0].account,
                accountrule=tarobj1.accountrule[0],
                startpos=datetime(2018, 3, 26, 9, 0, 0),
                endpos=datetime(2018, 3, 26, 11, 0, 0),
                evaluation=evobj)
            self.assertRaisesRegex(UserError,
                "The time account item overlaps with this item: '2018-03-26: 10:00 - 16:00'",
                itm_obj2.save)
        
            # overlap at endpos
            itm_obj3 = AccountItem(
                employee=employee1,
                period=p1,
                account=tarobj1.accountrule[0].account,
                accountrule=tarobj1.accountrule[0],
                startpos=datetime(2018, 3, 26, 12, 0, 0),
                endpos=datetime(2018, 3, 26, 17, 0, 0),
                evaluation=evobj)
            self.assertRaisesRegex(UserError,
                "The time account item overlaps with this item: '2018-03-26: 10:00 - 16:00'",
                itm_obj3.save)

            # overlap within
            itm_obj4 = AccountItem(
                employee=employee1,
                period=p1,
                account=tarobj1.accountrule[0].account,
                accountrule=tarobj1.accountrule[0],
                startpos=datetime(2018, 3, 26, 12, 0, 0),
                endpos=datetime(2018, 3, 26, 13, 0, 0),
                evaluation=evobj)
            self.assertRaisesRegex(UserError,
                "The time account item overlaps with this item: '2018-03-26: 10:00 - 16:00'",
                itm_obj4.save)

            # overlap around
            itm_obj5 = AccountItem(
                employee=employee1,
                period=p1,
                account=tarobj1.accountrule[0].account,
                accountrule=tarobj1.accountrule[0],
                startpos=datetime(2018, 3, 26, 9, 0, 0),
                endpos=datetime(2018, 3, 26, 17, 0, 0),
                evaluation=evobj)
            self.assertRaisesRegex(UserError,
                "The time account item overlaps with this item: '2018-03-26: 10:00 - 16:00'",
                itm_obj5.save)

            # no overlap
            itm_obj6 = AccountItem(
                employee=employee1,
                period=p1,
                account=tarobj1.accountrule[0].account,
                accountrule=tarobj1.accountrule[0],
                startpos=datetime(2018, 3, 26, 9, 0, 0),
                endpos=datetime(2018, 3, 26, 9, 30, 0),
                evaluation=evobj)
            itm_obj6.save()
            self.assertTrue(itm_obj6)

    @with_transaction()
    def test_timeaccountitem_edit_item_with_overlaps(self):
        """ test: create two time account item with overlap
        """
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                    ],
                accountrules=[
                        # time in localtime of company
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        self.assertEqual(len(tarobj1.accountrule), 1)
        self.assertEqual(tarobj1.accountrule[0].name, 'Work 0-24')
        self.assertEqual(str(tarobj1.accountrule[0].mintime), '00:00:00')
        self.assertEqual(str(tarobj1.accountrule[0].maxtime), '00:00:00')
        self.assertEqual(tarobj1.accountrule[0].name, 'Work 0-24')
        self.assertEqual(tarobj1.accountrule[0].account.name, 'Work')

        with set_company(tarobj1.company):
            AccountItem = Pool().get('employee_timetracking.timeaccountitem')

            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            evobj = create_evaluation(employee1, date(2018, 3, 10))

            p1 = create_period(
                    datetime(2018, 3, 26, 6, 30, 0), 
                    datetime(2018, 3, 26, 19, 35, 23), 
                    tarobj1.type_present, employee1)    # DB stores in UTC
            self.assertEqual(str(p1.startpos), '2018-03-26 06:30:00')   # UTC
            self.assertEqual(str(p1.endpos),   '2018-03-26 19:35:23')
            self.assertEqual(p1.name, '08:30 - 21:35, 2018-03-26 [W]')  # CEST
            self.assertEqual(p1.employee.party.name, 'Frida')
            self.assertEqual(p1.presence.name, 'Work')
            self.assertEqual(p1.state, 'c')

            # create 1st item
            itm_obj = create_timeaccountitem(
                    employee=employee1,
                    period=p1,
                    account=tarobj1.accountrule[0].account,
                    accountrule=tarobj1.accountrule[0],
                    startpos=datetime(2018, 3, 26, 10, 0, 0),
                    endpos=datetime(2018, 3, 26, 16, 0, 0),
                    evaluation=evobj,
                )
            self.assertEqual(itm_obj.name, '12:00 - 18:00, 2018-03-26 [W1]')

            # 2nd item, no overlap
            itm_2 = create_timeaccountitem(
                    employee=employee1,
                    period=p1,
                    account=tarobj1.accountrule[0].account,
                    accountrule=tarobj1.accountrule[0],
                    startpos=datetime(2018, 3, 26, 8, 0, 0),
                    endpos=datetime(2018, 3, 26, 9, 0, 0),
                    evaluation=evobj,
                )
            self.assertEqual(itm_2.name, '10:00 - 11:00, 2018-03-26 [W1]')

            # edit with overlap
            itm_2.endpos = datetime(2018, 3, 26, 11, 0, 0)
            self.assertRaises(Exception, itm_2.save)

            itm_2.startpos = datetime(2018, 3, 26, 12, 0, 0)
            itm_2.endpos = datetime(2018, 3, 26, 17, 0, 0)
            self.assertRaises(Exception, itm_2.save)

            itm_2.startpos = datetime(2018, 3, 26, 17, 0, 0)
            itm_2.endpos = datetime(2018, 3, 26, 18, 0, 0)
            itm_2.save()

            itm_2.endpos = datetime(2018, 3, 26, 15, 0, 0)
            self.assertRaises(Exception, itm_2.save)

    @with_transaction()
    def test_timeaccountitem_is_eval_locked(self):
        """ test: create period/evaluation, check locking-info
        """
        pool = Pool()
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')
        Evaluation = pool.get('employee_timetracking.evaluation')
        Period = pool.get('employee_timetracking.period')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(23, 59, 59), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
        
            evobj0 = create_evaluation(employee1, date(2018, 3, 4))
            Evaluation.wfactivate([evobj0])
            self.assertEqual(evobj0.state, 'a')
            self.assertEqual(evobj0.rec_name, 'Frida - 2018-03')

            p1 = create_period(
                    datetime(2018, 3, 10, 6, 30, 0), 
                    datetime(2018, 3, 10, 16, 35, 23), 
                    employee1.tariff.type_present, employee1)
            self.assertEqual(str(p1.startpos), '2018-03-10 06:30:00')
            self.assertEqual(str(p1.endpos),   '2018-03-10 16:35:23')
            self.assertEqual(p1.name, '07:30 - 17:35, 2018-03-10 [W]')
            self.assertEqual(p1.is_eval_locked, False)

            Period.wfexamine([p1])
            self.assertEqual(len(p1.accountitem), 1)
            self.assertEqual(p1.accountitem[0].rec_name, '07:30 - 17:35, 2018-03-10 [W1]')
            self.assertEqual(p1.accountitem[0].is_eval_locked, False)
            self.assertEqual(p1.accountitem[0].state, 'e')

            # find time-account-items by its evaluation-state
            pl1 = TimeAccountItem.search([('is_eval_locked', '=', True)])
            self.assertEqual(len(pl1), 0)
            pl1 = TimeAccountItem.search([('is_eval_locked', '=', False)])
            self.assertEqual(len(pl1), 1)
            self.assertEqual(pl1[0].name, '07:30 - 17:35, 2018-03-10 [W1]')
            # 'in' - search throws exception
            self.assertRaises(Exception,
                    TimeAccountItem.search,
                    [('is_eval_locked', 'in', [False, None])]
                )

            Evaluation.wflock([evobj0])
            self.assertEqual(p1.accountitem[0].is_eval_locked, True)
            pl1 = TimeAccountItem.search([('is_eval_locked', '=', True)])
            self.assertEqual(len(pl1), 1)
            self.assertEqual(pl1[0].name, '07:30 - 17:35, 2018-03-10 [W1]')

            # evaluation is now locked --> edit to time-account-items must be denied
            pl1[0].endpos = pl1[0].endpos + timedelta(seconds=60)
            self.assertRaises(Exception, pl1[0].save)
            self.assertRaises(Exception,
                    Period.delete,
                    pl1
                )
            # state-change keeps allowed
            self.assertEqual(p1.accountitem[0].state, 'e')
            TimeAccountItem.wflock(p1.accountitem)
            # no new items in locked evaluation-period
            ta1 = TimeAccountItem()
            ta1.employee = employee1
            ta1.period = pl1[0].period
            ta1.account = pl1[0].account
            ta1.accountrule = pl1[0].accountrule
            ta1.startpos = datetime(2018, 3, 11, 6, 30, 0)
            ta1.endpos = datetime(2018, 3, 11, 12, 30, 0)
            self.assertRaises(Exception, ta1.save)

    @with_transaction()
    def test_timeaccountitem_over_midnight(self):
        """ test: create period/evaluation, check values at midnight + timezone
        """
        pool = Pool()
        AccountRule = pool.get('employee_timetracking.accountrule')
        Period = pool.get('employee_timetracking.period')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
        
            # timezone CEST (GMT+2h)
            # employee starts at midnight local time
            t1 = AccountRule.get_utctime(datetime(2018, 4, 25, 0, 25, 0), tarobj1.company.timezone)
            self.assertEqual(str(t1), '2018-04-24 22:25:00')
            # and leaves at half past ten, local time
            t2 = AccountRule.get_utctime(datetime(2018, 4, 25, 10, 25, 0), tarobj1.company.timezone)
            self.assertEqual(str(t2), '2018-04-25 08:25:00')
            
            p1 = create_period(t1, t2, employee1.tariff.type_present, employee1)
            self.assertEqual(str(p1.startpos), '2018-04-24 22:25:00')
            self.assertEqual(str(p1.endpos),   '2018-04-25 08:25:00')
            self.assertEqual(p1.name, '00:25 - 10:25, 2018-04-25 [W]')
            self.assertEqual(p1.is_eval_locked, False)

            Period.wfexamine([p1])
            
            # Accountrule uses local time to split period-item to account-items,
            # user sends time in localtime, db stores in utc, therefore we have only one item
            # from 22:25 --> 8:25 UTC
            self.assertEqual(len(p1.accountitem), 1)
            self.assertEqual(str(p1.accountitem[0].startpos), '2018-04-24 22:25:00')
            self.assertEqual(str(p1.accountitem[0].endpos), '2018-04-25 08:25:00')
            self.assertEqual(p1.accountitem[0].rec_name, '00:25 - 10:25, 2018-04-25 [W1]')
            self.assertEqual(p1.accountitem[0].is_eval_locked, False)
            self.assertEqual(p1.accountitem[0].state, 'e')

    @with_transaction()
    def test_timeaccountitem_more_days(self):
        """ test: create period/evaluation, check values while 4 days + timezone
        """
        pool = Pool()
        AccountRule = pool.get('employee_timetracking.accountrule')
        Period = pool.get('employee_timetracking.period')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
        
            # timezone CEST (GMT+2h)
            # employee starts at monday, 9:00
            t1 = AccountRule.get_utctime(datetime(2018, 4, 23, 9, 0, 0), tarobj1.company.timezone)
            self.assertEqual(str(t1), '2018-04-23 07:00:00')
            # and leaves at thursday, 19:00
            t2 = AccountRule.get_utctime(datetime(2018, 4, 26, 19, 0, 0), tarobj1.company.timezone)
            self.assertEqual(str(t2), '2018-04-26 17:00:00')
            
            p1 = create_period(t1, t2, employee1.tariff.type_present, employee1)
            self.assertEqual(str(p1.startpos), '2018-04-23 07:00:00')
            self.assertEqual(str(p1.endpos),   '2018-04-26 17:00:00')
            self.assertEqual(p1.name, '09:00 - 19:00, 2018-04-23 [W]')
            self.assertEqual(p1.is_eval_locked, False)

            Period.wfexamine([p1])

            # Accountrule uses local time to split period-item to account-items
            self.assertEqual(len(p1.accountitem), 4)
            l1 = sorted(p1.accountitem, key=lambda ac1: ac1.startpos)
            
            self.assertEqual(str(l1[0].startpos), '2018-04-23 07:00:00')
            self.assertEqual(str(l1[0].endpos), '2018-04-23 22:00:00')
            self.assertEqual(l1[0].rec_name, '09:00 - 00:00, 2018-04-23 [W1]')
            self.assertEqual(str(l1[0].duration), '15:00:00')

            self.assertEqual(str(l1[1].startpos), '2018-04-23 22:00:00')
            self.assertEqual(str(l1[1].endpos), '2018-04-24 22:00:00')
            self.assertEqual(l1[1].rec_name, '00:00 - 00:00, 2018-04-24 [W1]')
            self.assertEqual(str(l1[1].duration), '1 day, 0:00:00')

            self.assertEqual(str(l1[2].startpos), '2018-04-24 22:00:00')
            self.assertEqual(str(l1[2].endpos), '2018-04-25 22:00:00')
            self.assertEqual(l1[2].rec_name, '00:00 - 00:00, 2018-04-25 [W1]')
            self.assertEqual(str(l1[2].duration), '1 day, 0:00:00')

            self.assertEqual(str(l1[3].startpos), '2018-04-25 22:00:00')
            self.assertEqual(str(l1[3].endpos), '2018-04-26 17:00:00')
            self.assertEqual(l1[3].rec_name, '00:00 - 19:00, 2018-04-26 [W1]')
            self.assertEqual(str(l1[3].duration), '19:00:00')

# end TimeAccountItemTestCase
