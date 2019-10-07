# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import timedelta
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from datetime import datetime, date, timedelta
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_tariff_full, \
    create_period, create_employee, create_evaluation
from trytond.exceptions import UserError


class PeriodTestCase(ModuleTestCase):
    'Test period module'
    module = 'employee_timetracking'

    def prep_period_employee(self):
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
        with set_company(tarobj1.company):        
            # employee + tariff
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
        return employee1
        
    @with_transaction()
    def test_period_create_item(self):
        """ test: create period for employee, check name + usage of time zone
        """
        Presence = Pool().get('employee_timetracking.presence')
        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)
            
            # create Worktime item
            per_obj = create_period(startpos=datetime(2018, 3, 10, 8, 0), 
                    endpos=datetime(2018, 3, 10, 15, 55), 
                    employee=employee1, presence=pr_lst[0])
            self.assertTrue(per_obj)
            self.assertEqual(per_obj.name, '08:00 - 15:55 UTC, 2018-03-10 [W]')
            self.assertEqual(str(per_obj.duration), '7:55:00')
            
            # add time zone to company
            employee1.company.timezone = 'Europe/Berlin'
            employee1.company.save()
            # period item is now shown in local time
            # german winter time
            self.assertEqual(per_obj.name, '09:00 - 16:55, 2018-03-10 [W]')
            # german summer time
            per_obj.startpos = datetime(2018, 4, 10, 8, 0)
            per_obj.endpos = datetime(2018, 4, 10, 15, 55)
            per_obj.save()
            self.assertEqual(per_obj.name, '10:00 - 17:55, 2018-04-10 [W]')
            self.assertEqual(per_obj.week, 15)
    
            # check presence
            pr_lst2 = Presence.search([], order=[('name', 'ASC')])
            self.assertEqual(len(pr_lst2), 2)
            self.assertEqual(pr_lst2[0].name, 'Ill')
            self.assertEqual(len(pr_lst2[0].employees), 0)
            self.assertEqual(pr_lst2[0].numemployees, 0)
            self.assertEqual(pr_lst2[1].name, 'Work')
            self.assertEqual(pr_lst2[1].employees, (employee1, ))
            self.assertEqual(pr_lst2[1].numemployees, 1)

    @with_transaction()
    def test_period_edit_item(self):
        """ test: create incomplete period for employee, edit item to complete it
        """
        Presence = Pool().get('employee_timetracking.presence')
        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)
            
            # create Worktime item
            per_obj = create_period(startpos=datetime(2018, 3, 10, 8, 0), 
                    endpos=None, 
                    employee=employee1, presence=pr_lst[0])
            self.assertTrue(per_obj)
            self.assertEqual(per_obj.name, '08:00 - - UTC, 2018-03-10 [W]')
    
            # edit work time item
            per_obj.endpos = datetime(2018, 3, 10, 15, 56)
            per_obj.save()
            self.assertEqual(per_obj.name, '08:00 - 15:56 UTC, 2018-03-10 [W]')

    @with_transaction()
    def test_period_same_startpos_endpos(self):
        """ test: create period for employee, add another item with same start
        """
        pool = Pool()
        Presence = pool.get('employee_timetracking.presence')
        Period = pool.get('employee_timetracking.period')
        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)
            
            # create Worktime item
            per_obj = create_period(startpos=datetime(2018, 3, 10, 8, 0), 
                    endpos=datetime(2018, 3, 10, 15, 0), 
                    employee=employee1, presence=pr_lst[0])
            self.assertTrue(per_obj)
            self.assertEqual(per_obj.name, '08:00 - 15:00 UTC, 2018-03-10 [W]')
    
            # same startpos
            perobj = Period(
                    employee=employee1,
                    presence=pr_lst[0],
                    startpos=datetime(2018, 3, 10, 8, 0), 
                    endpos=None, 
                    state=Period.default_state()
                )
            self.assertRaisesRegex(UserError,
                "The working time item overlaps with this item: '08:00 - 15:00 UTC, 2018-03-10 \[W\]'",
                perobj.save)

    @with_transaction()
    def test_period_same_endpos(self):
        """ test: create period for employee, add another item with same endpos
        """
        pool = Pool()
        Presence = pool.get('employee_timetracking.presence')
        Period = pool.get('employee_timetracking.period')
        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)
            
            # create Worktime item
            per_obj = create_period(startpos=datetime(2018, 3, 10, 8, 0), 
                    endpos=datetime(2018, 3, 10, 15, 0), 
                    employee=employee1, presence=pr_lst[0])
            self.assertTrue(per_obj)
            self.assertEqual(per_obj.name, '08:00 - 15:00 UTC, 2018-03-10 [W]')
    
            # same endpos (startpos = None --> no overlap check)
            perobj = Period(
                    employee=employee1,
                    presence=pr_lst[0],
                    startpos=None, 
                    endpos=datetime(2018, 3, 10, 15, 0), 
                    state=Period.default_state()
                )
            self.assertRaisesRegex(UserError,
                "The working time item overlaps with this item: '08:00 - 15:00 UTC, 2018-03-10 \[W\]'",
                perobj.save)

    @with_transaction()
    def test_period_wrong_order_startpos_endpos(self):
        """ test: create period for employee with start > end
        """
        pool = Pool()
        Presence = pool.get('employee_timetracking.presence')
        Period = pool.get('employee_timetracking.period')

        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)

            # create work time item --> exception
            perobj = Period(
                    employee=employee1,
                    presence=pr_lst[0],
                    startpos=datetime(2018, 3, 10, 12, 0), 
                    endpos=datetime(2018, 3, 10, 8, 0), 
                    state=Period.default_state()
                )
            self.assertRaisesRegex(UserError,
                "End time must be after start time.",
                perobj.save)

    @with_transaction()
    def test_period_empty_start_endpos(self):
        """ test: create period for employee with start = end = None
        """
        pool = Pool()
        Presence = pool.get('employee_timetracking.presence')
        Period = pool.get('employee_timetracking.period')
        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)
            
            # create work time item --> exception
            perobj = Period(
                    employee=employee1,
                    presence=pr_lst[0],
                    startpos=None, 
                    endpos=None, 
                    state=Period.default_state()
                )
            self.assertRaisesRegex(UserError,
                "Please enter a time.",
                perobj.save)

    @with_transaction()
    def test_period_state_month(self):
        """ test: create period, check result of 'state_month'
        """
        pool = Pool()
        Presence = pool.get('employee_timetracking.presence')
        Period = pool.get('employee_timetracking.period')
        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)
            
            dt1 = datetime.today()
            dt3 = datetime(2018, 5, 1, 0, 5, 0)
            dt2 = (dt1.year - dt3.year) * 12 + (dt1.month - dt3.month)

            perobj = Period(
                    employee=employee1,
                    presence=pr_lst[0],
                    startpos=datetime(2018, 5, 1, 0, 5, 0), 
                    endpos=None, 
                    state=Period.default_state()
                )
            perobj.save()
            self.assertEqual(perobj.rec_name, '00:05 - - UTC, 2018-05-01 [W]')
            self.assertEqual(perobj.state_month, dt2)
            
            perobj.startpos = None
            perobj.endpos = datetime(2018, 5, 1, 0, 5, 0)
            perobj.save()
            self.assertEqual(perobj.rec_name, '- - 00:05 UTC, 2018-05-01 [W]')
            self.assertEqual(perobj.state_month, dt2)

            perobj.startpos = datetime(2018, 5, 1, 0, 5, 0)
            perobj.endpos = datetime(2018, 5, 1, 10, 5, 0)
            perobj.save()
            self.assertEqual(perobj.rec_name, '00:05 - 10:05 UTC, 2018-05-01 [W]')
            self.assertEqual(perobj.state_month, dt2)

    @with_transaction()
    def test_period_workflow_wfexamine(self):
        """ test: create incomplete period, wfexamine --> exception
        """
        pool = Pool()
        Presence = pool.get('employee_timetracking.presence')
        Period = pool.get('employee_timetracking.period')

        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)
            
            per_obj = create_period(startpos=datetime(2018, 3, 10, 8, 0), 
                    endpos=None, 
                    employee=employee1, presence=pr_lst[0]
                )
            self.assertEqual(per_obj.name, '08:00 - - UTC, 2018-03-10 [W]')
            # next wf-step --> exception
            self.assertRaisesRegex(UserError,
                "Enter start and end time before moving on.",
                Period.wfexamine,
                [per_obj])

    @with_transaction()
    def test_period_workflow_end_text_del(self):
        """ test: create period, go through workflow, try to delete item
        """
        Presence = Pool().get('employee_timetracking.presence')
        Period = Pool().get('employee_timetracking.period')
        employee1 = self.prep_period_employee()

        with set_company(employee1.company):
            # select 'Work'
            pr_lst = Presence.search([
                    ('id', 'in', [x.id for x in employee1.tariff.presence]), 
                    ('name', '=', 'Work')
                ])
            self.assertEqual(len(pr_lst), 1)
            
            # create work time item --> exception
            per_obj = create_period(startpos=datetime(2018, 3, 10, 8, 0), 
                    endpos=datetime(2018, 3, 10, 15, 0), 
                    employee=employee1, presence=pr_lst[0]
                )
            self.assertEqual(per_obj.name, '08:00 - 15:00 UTC, 2018-03-10 [W]')
            Period.wfexamine([per_obj])
            Period.wflock([per_obj])
            
            # delete --> exception
            self.assertRaisesRegex(UserError,
                "The working time entry is in the 'locked' state and can not be deleted.",
                Period.delete,
                [per_obj])

    @with_transaction()
    def test_period_get_overlaps(self):
        """ create periods, check for overlaps
        """
        pool = Pool()
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        Period = pool.get('employee_timetracking.period')
        
        employee1 = self.prep_period_employee()
        employee1.tariff.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        employee1.tariff.company.save()

        with set_company(employee1.company):
            p1 = create_period(
                    datetime(2018, 7, 3, 6, 30, 0), 
                    datetime(2018, 7, 3, 16, 35, 23), 
                    employee1.tariff.type_present, employee1)
            p2 = create_period(
                    datetime(2018, 7, 4, 6, 30, 0), 
                    datetime(2018, 7, 4, 16, 35, 23), 
                    employee1.tariff.type_present, employee1)
            p3 = create_period(
                    datetime(2018, 7, 5, 6, 30, 0), 
                    None, 
                    employee1.tariff.type_present, employee1)
            self.assertTrue(p1)
            self.assertTrue(p2)
            self.assertTrue(p3)
            
            self.assertEqual(BreakPeriod.get_overlaps(Period, employee1.id, p1, None, None), [])
            self.assertEqual(BreakPeriod.get_overlaps(Period, employee1.id, p3, None, None), [])
            
            # find overlap of 'p3'
            self.assertEqual(BreakPeriod.get_overlaps(Period, employee1.id, None, 
                datetime(2018, 7, 5, 6, 25, 0), datetime(2018, 7, 5, 14, 30)), [p3.id])

    @with_transaction()
    def test_period_overlaps_on_write(self):
        """ create periods, check for overlaps at writing period item
        """
        Period = Pool().get('employee_timetracking.period')
        
        employee1 = self.prep_period_employee()
        employee1.tariff.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        employee1.tariff.company.save()

        with set_company(employee1.company):
            p1 = create_period(
                    datetime(2018, 7, 3, 6, 30, 0), 
                    datetime(2018, 7, 3, 16, 35, 23), 
                    employee1.tariff.type_present, employee1)
            p2 = create_period(
                    datetime(2018, 7, 4, 6, 30, 0), 
                    datetime(2018, 7, 4, 16, 35, 23), 
                    employee1.tariff.type_present, employee1)
            p3 = create_period(
                    datetime(2018, 7, 5, 6, 30, 0), 
                    None, 
                    employee1.tariff.type_present, employee1)
            self.assertTrue(p1)
            self.assertTrue(p2)
            self.assertTrue(p3)
            
            perobj = Period(
                    employee=employee1,
                    presence=employee1.tariff.type_present, 
                    startpos=datetime(2018, 7, 5, 6, 25, 0), 
                    endpos=datetime(2018, 7, 5, 14, 35, 23),
                    state=Period.default_state()
                )
            self.assertRaisesRegex(UserError,
                "The working time item overlaps with this item: '08:30 - -, 2018-07-05 \[W\]'",
                perobj.save)

    @with_transaction()
    def test_period_is_eval_locked(self):
        """ test: create period/evaluation, check locking-info
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        Period = pool.get('employee_timetracking.period')
        
        employee1 = self.prep_period_employee()
        employee1.tariff.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        employee1.tariff.company.save()

        with set_company(employee1.company):
            evobj = create_evaluation(employee1, date(2018, 3, 4))
            self.assertTrue(evobj)
            Evaluation.wfactivate([evobj])
            self.assertEqual(evobj.rec_name, 'Frida - 2018-03')
            self.assertEqual(evobj.state, 'a')

            # period in evaluation-date-range
            p1 = create_period(
                    datetime(2018, 3, 10, 6, 30, 0), 
                    datetime(2018, 3, 10, 16, 35, 23), 
                    employee1.tariff.type_present, employee1)    # DB stores in UTC
            self.assertEqual(str(p1.startpos), '2018-03-10 06:30:00')   # UTC
            self.assertEqual(str(p1.endpos),   '2018-03-10 16:35:23')
            self.assertEqual(p1.name, '07:30 - 17:35, 2018-03-10 [W]')  # CET
            
            self.assertEqual(p1.is_eval_locked, False)
            
            # find period by its evaluation-state
            pl1 = Period.search([('is_eval_locked', '=', True)])
            self.assertEqual(len(pl1), 0)
            pl1 = Period.search([('is_eval_locked', '=', False)])
            self.assertEqual(len(pl1), 1)
            self.assertEqual(pl1[0].name, '07:30 - 17:35, 2018-03-10 [W]')
            # 'in' - search throws exception
            self.assertRaisesRegex(Exception,
                "search with 'in' not allowed",
                Period.search,
                [('is_eval_locked', 'in', [False, None])]
                )

            Evaluation.wflock([evobj])
            self.assertEqual(p1.is_eval_locked, True)
            pl1 = Period.search([('is_eval_locked', '=', True)])
            self.assertEqual(len(pl1), 1)
            self.assertEqual(pl1[0].name, '07:30 - 17:35, 2018-03-10 [W]')
            
            # evaluation is now locked --> edit to period-item must be denied
            p1.endpos = p1.endpos + timedelta(seconds=60)
            self.assertRaisesRegex(UserError, 
                "Edit denied, the evaluation period of the working time item '07:30 - 17:35, 2018-03-10 \[W\]' is locked.",
                p1.save)
            self.assertRaisesRegex(UserError,
                "The working time entry is in the 'locked' state and can not be deleted.",
                Period.delete,
                [p1])
            # state-change keeps allowed
            Period.wfexamine([p1])
            # no new items in locked evaluation-period
            perobj1 = Period(
                    employee=employee1,
                    presence=employee1.tariff.type_present, 
                    startpos=datetime(2018, 3, 11, 6, 30, 0),  
                    endpos=datetime(2018, 3, 11, 16, 35, 23), 
                    state=Period.default_state()
                )
            self.assertRaisesRegex(UserError,
                "Edit denied, the evaluation period of the working time item '-/-' is locked.",
                perobj1.save)

            # period outside of locked evaluation
            p2 = create_period(
                    datetime(2018, 5, 10, 6, 30, 0), 
                    datetime(2018, 5, 10, 16, 35, 23), 
                    employee1.tariff.type_present, employee1)    # DB stores in UTC
            self.assertEqual(p2.name, '08:30 - 18:35, 2018-05-10 [W]')  # CEST
            self.assertEqual(p2.is_eval_locked, False)

            pl1 = Period.search([('is_eval_locked', '=', False)])
            self.assertEqual(len(pl1), 1)
            self.assertEqual(pl1[0].name, '08:30 - 18:35, 2018-05-10 [W]')

# end PeriodTestCase
