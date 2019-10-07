# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.modules.company.tests import set_company
from trytond.modules.employee_timetracking.tests.testlib import create_tariff_full, \
    create_employee, create_evaluation
from datetime import datetime, timedelta, date


class BreakperiodTestCase(ModuleTestCase):
    'Test break module'
    module = 'employee_timetracking'

    def prep_breakperiod_employee(self):
        """ create tariff,  company, employee...
        """
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                        {'name':'Ill', 'shortname':'I'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        
        tarobj1.company.timezone = 'Europe/Berlin'
        tarobj1.company.save()
            
        with set_company(tarobj1.company):        
            # employee + tariff
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
        return employee1

    @with_transaction()
    def test_breakperiod_create_item(self):
        """ test: create break for employee, check name + usage of time zone
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 1, 30, 10, 5, 23),
                        endpos=None,
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertTrue(bt1)
                self.assertEqual(bt1.employee.rec_name, 'Frida')
                self.assertEqual(bt1.state, 'c')
                self.assertEqual(str(bt1.startpos), '2019-01-30 10:05:23')
                # timezone: europe/berlin, CET, GMT+1
                self.assertEqual(bt1.name, '11:05 - -, 2019-01-30')
                
                # search on name
                v1 = Breakperiod.search([('name', '=', 'nope')])
                self.assertEqual(len(v1), 0)
                v1 = Breakperiod.search([('name', '=', '11:05 - -, 2019-01-30')])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('name', 'like', '%2019%')])
                self.assertEqual(len(v1), 1)

    @with_transaction()
    def test_breakperiod_duration(self):
        """ test: create break, check duration
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                # 60 min
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 1, 30, 10, 0, 0),
                        endpos=datetime(2019, 1, 30, 11, 0, 0),
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertEqual(str(bt1.duration), '1:00:00')

                # no start
                bt1.startpos = None
                bt1.save()
                self.assertEqual(bt1.duration, None)

                # no end
                bt1.startpos = datetime(2019, 1, 30, 10, 0, 0)
                bt1.endpos = None
                bt1.save()
                self.assertEqual(bt1.duration, None)

    @with_transaction()
    def test_breakperiod_week(self):
        """ test: create break, check week
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 2, 1, 10, 0, 0),
                        endpos=None,
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertEqual(bt1.name, '11:00 - -, 2019-02-01')
                self.assertEqual(str(bt1.week), '5')
                
                # change source for week
                bt1.startpos = None
                bt1.endpos = datetime(2019, 2, 1, 10, 35, 0)
                bt1.save()
                self.assertEqual(bt1.name, '- - 11:35, 2019-02-01')
                self.assertEqual(str(bt1.week), '5')
                
                v1 = Breakperiod.search([('week', '=', 6)])
                self.assertEqual(len(v1), 0)
                v1 = Breakperiod.search([('week', '=', 5)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('week', '>', 4)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('week', '>=', 5)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('week', '>', 5)])
                self.assertEqual(len(v1), 0)
                v1 = Breakperiod.search([('week', '<', 5)])
                self.assertEqual(len(v1), 0)
                v1 = Breakperiod.search([('week', '<', 6)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('week', '>', 4), ('week', '<', 6)])
                self.assertEqual(len(v1), 1)

    @with_transaction()
    def test_breakperiod_state_month(self):
        """ test: create break, check state_month
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                dt1 = datetime.today()
                
                # startpos: 2 days ago
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=dt1 - timedelta(days=2),
                        endpos=None,
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                if dt1.month == bt1.startpos.month:
                    self.assertEqual(bt1.state_month, 0)
                else :
                    self.assertEqual(bt1.state_month, 1)
                
                # startpos: today
                bt1.startpos = dt1
                bt1.save()
                self.assertEqual(bt1.state_month, 0)
                v1 = Breakperiod.search([('state_month', '=', 0)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('state_month', '=', 1)])
                self.assertEqual(len(v1), 0)
                v1 = Breakperiod.search([('state_month', '<', 1)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('state_month', '>', 1)])
                self.assertEqual(len(v1), 0)
                v1 = Breakperiod.search([('state_month', '>=', 0)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('state_month', '>', -1), ('state_month', '<', 1)])
                self.assertEqual(len(v1), 1)
                
                # startpos: 15. of current month
                bt1.startpos = datetime(dt1.year, dt1.month, 15, 10, 0, 0)
                bt1.save()
                self.assertEqual(bt1.state_month, 0)
                
                # startpos: 1. of last month
                dt2 = datetime(dt1.year, dt1.month, 15, 10, 0, 0)
                dt2 = dt2 - timedelta(days=30)
                bt1.startpos = dt2
                bt1.save()
                self.assertEqual(bt1.state_month, 1)

                # startpos: 15. of two month before
                dt2 = datetime(dt1.year, dt1.month, 15, 10, 0, 0)
                dt2 = dt2 - timedelta(days=60)
                bt1.startpos = dt2
                bt1.save()
                self.assertEqual(bt1.state_month, 2)
                v1 = Breakperiod.search([('state_month', '=', 2)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('state_month', '=', 1)])
                self.assertEqual(len(v1), 0)
                v1 = Breakperiod.search([('state_month', '<', 1)])
                self.assertEqual(len(v1), 0)
                v1 = Breakperiod.search([('state_month', '>', 1)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('state_month', '>=', 1)])
                self.assertEqual(len(v1), 1)
                v1 = Breakperiod.search([('state_month', '>', 1), ('state_month', '<', 4)])
                self.assertEqual(len(v1), 1)
    
    @with_transaction()
    def test_breakperiod_get_overlaps(self):
        """ create break time items, check for overlaps
        """
        BreakPeriod = Pool().get('employee_timetracking.breakperiod')
        employee1 = self.prep_breakperiod_employee()

        with set_company(employee1.company):
            br1 = BreakPeriod(
                startpos = datetime(2018, 7, 3, 6, 30, 0),
                endpos = datetime(2018, 7, 3, 16, 35, 23),
                employee = employee1)
            br1.save()
            self.assertTrue(br1)
            
            br2 = BreakPeriod(
                startpos = datetime(2018, 7, 4, 6, 30, 0),
                endpos = datetime(2018, 7, 4, 16, 35, 23),
                employee = employee1)
            br2.save()
            self.assertTrue(br2)
            
            br3 = BreakPeriod(
                startpos = datetime(2018, 7, 5, 6, 30, 0),
                endpos = None,
                employee = employee1)
            br3.save()
            self.assertTrue(br3)

            self.assertEqual(BreakPeriod.get_overlaps(BreakPeriod, employee1.id, br1, None, None), [])
            self.assertEqual(BreakPeriod.get_overlaps(BreakPeriod, employee1.id, br3, None, None), [])

            # find overlap of 'br3'
            self.assertEqual(BreakPeriod.get_overlaps(BreakPeriod, employee1.id, None, 
                datetime(2018, 7, 5, 6, 25, 0), datetime(2018, 7, 5, 14, 30)), [br3.id])

    @with_transaction()
    def test_breakperiod_overlaps_on_write(self):
        """ create break times, check for overlaps at writing break time  item
        """
        BreakPeriod = Pool().get('employee_timetracking.breakperiod')
        
        employee1 = self.prep_breakperiod_employee()

        with set_company(employee1.company):
            br1 = BreakPeriod(
                startpos = datetime(2018, 7, 3, 6, 30, 0),
                endpos = datetime(2018, 7, 3, 16, 35, 23),
                employee = employee1)
            br1.save()
            self.assertTrue(br1)
            
            br2 = BreakPeriod(
                startpos = datetime(2018, 7, 4, 6, 30, 0),
                endpos = datetime(2018, 7, 4, 16, 35, 23),
                employee = employee1)
            br2.save()
            self.assertTrue(br2)
            
            br3 = BreakPeriod(
                startpos = datetime(2018, 7, 5, 6, 30, 0),
                endpos = None,
                employee = employee1)
            br3.save()
            self.assertTrue(br3)
            
            br4 = BreakPeriod(
                startpos = datetime(2018, 7, 5, 6, 25, 0),
                endpos = datetime(2018, 7, 5, 14, 35, 23),
                employee = employee1)
            self.assertRaisesRegex(UserError,
                "The break time item overlaps with this item: '08:30 - -, 2018-07-05'",
                br4.save)

            br5 = BreakPeriod(
                startpos = datetime(2018, 7, 5, 6, 35, 0),
                endpos = datetime(2018, 7, 5, 14, 35, 23),
                employee = employee1)
            br5.save()
            self.assertTrue(br5)
            
            br3.endpos = datetime(2018, 7, 5, 6, 40, 0)
            self.assertRaisesRegex(UserError,
                "The break time item overlaps with this item: '08:35 - 16:35, 2018-07-05'",
                br3.save)

    @with_transaction()
    def test_breakperiod_same_start_and_employee(self):
        """ test: create two break times, with same startpos, test constraints
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 1, 30, 10, 5, 0),
                        endpos=datetime(2019, 1, 30, 10, 35, 0),
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertEqual(bt1.name, '11:05 - 11:35, 2019-01-30')

                bt2 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 1, 30, 10, 5, 0),
                        endpos=None,
                        state=Breakperiod.default_state(),
                    )
                self.assertRaisesRegex(UserError,
                    "The break time item overlaps with this item: '11:05 - 11:35, 2019-01-30'",
                    bt2.save)

    @with_transaction()
    def test_breakperiod_same_start_end_diff_employee(self):
        """ test: create two break times on two employees, with same start-/endpos, test constraints
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        employee2 = create_employee(employee1.company, name='Diego')
        self.assertTrue(employee2)
        employee2.tariff = employee1.tariff
        employee2.save()

        with set_company(employee1.company):
            bt1 = Breakperiod(
                    employee=employee1,
                    startpos=datetime(2019, 1, 30, 10, 5, 0),
                    endpos=datetime(2019, 1, 30, 10, 35, 0),
                    state=Breakperiod.default_state(),
                )
            bt1.save()
            self.assertEqual(bt1.name, '11:05 - 11:35, 2019-01-30')
            self.assertEqual(bt1.employee.rec_name, 'Frida')

            bt2 = Breakperiod(
                    employee=employee2,
                    startpos=datetime(2019, 1, 30, 10, 5, 0),
                    endpos=datetime(2019, 1, 30, 10, 35, 0),
                    state=Breakperiod.default_state(),
                )
            bt2.save()
            self.assertEqual(bt2.name, '11:05 - 11:35, 2019-01-30')
            self.assertEqual(bt2.employee.rec_name, 'Diego')

    @with_transaction()
    def test_breakperiod_same_end_and_employee(self):
        """ test: create two break times, with same endpos, test constraints
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 1, 30, 10, 5, 0),
                        endpos=datetime(2019, 1, 30, 10, 35, 0),
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertEqual(bt1.name, '11:05 - 11:35, 2019-01-30')
                
                bt2 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=None,
                        endpos=datetime(2019, 1, 30, 10, 35, 0),
                        state=Breakperiod.default_state(),
                    )
                self.assertRaisesRegex(UserError,
                    "The break time item overlaps with this item: '11:05 - 11:35, 2019-01-30'",
                    bt2.save)

    @with_transaction()
    def test_breakperiod_no_start_end(self):
        """ test: create break, no value for start/end, test constraints
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=None,
                        endpos=None,
                        state=Breakperiod.default_state(),
                    )
                self.assertRaisesRegex(UserError,
                    "Please enter a time.",
                    bt1.save)

    @with_transaction()
    def test_breakperiod_end_before_start(self):
        """ test: create break, wrong order of start/end, test constraints
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 1, 30, 11, 5, 0),
                        endpos=datetime(2019, 1, 30, 10, 5, 0),
                        state=Breakperiod.default_state(),
                    )
                self.assertRaisesRegex(UserError,
                    "End time must be after start time.",
                    bt1.save)

    @with_transaction()
    def test_breakperiod_no_start_wf_examine(self):
        """ test: create break, no start time, wf step, test constraints
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=None,
                        endpos=datetime(2019, 1, 30, 10, 35, 0),
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertEqual(bt1.name, '- - 11:35, 2019-01-30')
                
                self.assertRaisesRegex(UserError,
                    "Enter start and end time before moving on.",
                    Breakperiod.wfexamine,
                    [bt1])

    @with_transaction()
    def test_breakperiod_no_end_wf_examine(self):
        """ test: create break, no end time, wf step, test constraints
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 1, 30, 10, 5, 0),
                        endpos=None,
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertEqual(bt1.name, '11:05 - -, 2019-01-30')
                
                self.assertRaisesRegex(UserError,
                    "Enter start and end time before moving on.",
                    Breakperiod.wfexamine,
                    [bt1])

    @with_transaction()
    def test_breakperiod_run_wf(self):
        """ test: create break, run wf
        """
        Breakperiod = Pool().get('employee_timetracking.breakperiod')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2019, 1, 30, 10, 5, 0),
                        endpos=datetime(2019, 1, 30, 10, 35, 0),
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertEqual(bt1.name, '11:05 - 11:35, 2019-01-30')
                Breakperiod.wfexamine([bt1])
                self.assertEqual(bt1.state, 'e')
                Breakperiod.wflock([bt1])
                self.assertEqual(bt1.state, 'l')

    @with_transaction()
    def test_breakperiod_create_with_evaluation(self):
        """ test: create break, test with existing evaluation
        """
        pool = Pool()
        Breakperiod = pool.get('employee_timetracking.breakperiod')
        Evaluation = pool.get('employee_timetracking.evaluation')
        transaction = Transaction()
        employee1 = self.prep_breakperiod_employee()
        
        with set_company(employee1.company):
            with transaction.set_context(employee=employee1):
                # create evaluation
                evobj = create_evaluation(employee1, date(2018, 10, 15))
                self.assertTrue(evobj)
                Evaluation.wfactivate([evobj])
                self.assertEqual(evobj.rec_name, 'Frida - 2018-10')
                self.assertEqual(evobj.state, 'a')

                # break time in time range of evaluation
                bt1 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2018, 10, 30, 10, 5, 0),
                        endpos=datetime(2018, 10, 30, 10, 35, 0),
                        state=Breakperiod.default_state(),
                    )
                bt1.save()
                self.assertEqual(bt1.name, '11:05 - 11:35, 2018-10-30')
                self.assertEqual(bt1.is_eval_locked, False)

                pl1 = Breakperiod.search([('is_eval_locked', '=', True)])
                self.assertEqual(len(pl1), 0)
                pl1 = Breakperiod.search([('is_eval_locked', '=', False)])
                self.assertEqual(len(pl1), 1)

                # 'in' - search throws exception
                self.assertRaisesRegex(Exception,
                    "search with 'in' not allowed",
                    Breakperiod.search,
                    [('is_eval_locked', 'in', [False, None])])

                # lock evaluation
                Evaluation.wflock([evobj])
                self.assertEqual(bt1.is_eval_locked, True)
                pl1 = Breakperiod.search([('is_eval_locked', '=', True)])
                self.assertEqual(len(pl1), 1)

                # create another break time in time range of locked evaluation
                bt2 = Breakperiod(
                        employee=Breakperiod.default_employee(),
                        startpos=datetime(2018, 10, 28, 10, 5, 0),
                        endpos=datetime(2018, 10, 28, 10, 35, 0),
                        state=Breakperiod.default_state(),
                    )
                self.assertRaisesRegex(UserError,
                    "Edit denied, the evaluation period of the break time item '-/-' is locked.",
                    bt2.save)

                # edit existing break item
                bt1.endpos = datetime(2018, 10, 30, 10, 40, 0)
                self.assertRaisesRegex(UserError,
                    "Edit denied, the evaluation period of the break time item '11:05 - 11:35, 2018-10-30' is locked.",
                    bt1.save)

                # edit existing break item
                self.assertRaisesRegex(UserError,
                    "The break time entry is in the 'locked' state and can not be deleted.",
                    Breakperiod.delete,
                    [bt1])

# end BreakperiodTestCase
