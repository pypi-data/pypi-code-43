# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import timedelta
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from datetime import date, datetime
from trytond.modules.company.tests import set_company
from trytond.modules.employee_timetracking.tests.testlib import create_tariff_full,\
    create_employee, create_evaluation, create_trytonuser


class EvaluationHolidaysTestCase(ModuleTestCase):
    'Test evaluation-holidays module'
    module = 'employee_timetracking'

    def prep_evalholidays_eval(self):
        """ create tariff, company, employee, evaluation
        """
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()
        
        evobj = None
        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
            
            evobj = create_evaluation(employee1, date(2019, 3, 4))

            self.assertTrue(evobj)
            self.assertEqual(evobj.rec_name, 'Frida - 2019-03')
        return evobj

    def prep_evalholidays_add_calendar(self, evaluation):
        """ add tryton user and calendar to DB
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        usr1 = create_trytonuser('frida', 'Test.1234')
        usr1.main_company = evaluation.employee.company
        usr1.company = evaluation.employee.company
        usr1.save()
        self.assertTrue(usr1)
        self.assertEqual(usr1.name, 'frida')

        usr1.employees = [evaluation.employee]
        usr1.employee = evaluation.employee
        usr1.save()
        self.assertEqual(evaluation.employee.trytonuser.name, 'frida')
        
        # add calendar
        cal1 = Calendar(
                name='Cal1',
                owner=evaluation.employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        evaluation.employee.calendar = cal1
        evaluation.employee.save()
        
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')
        self.assertEqual(evaluation.employee.calendar.rec_name, 'Cal1 (frida)')
        return cal1

    @with_transaction()
    def test_evalholidays_create_valid(self):
        """ test: create valid vacancy day
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()
        evobj.needs_recalc = False
        evobj.save()
        self.assertEqual(evobj.needs_recalc, False)
        
        evobj.vacationdays = [
                EvalHoliday(date_start = date(2019, 3, 10),
                        date_end = date(2019, 3, 22)
                    )
            ]
        evobj.save()
        self.assertEqual(evobj.needs_recalc, True)
        
        eh_lst = EvalHoliday.search([])
        self.assertEqual(len(eh_lst), 1)
        self.assertEqual(str(eh_lst[0].date_start), '2019-03-10')
        self.assertEqual(str(eh_lst[0].date_end), '2019-03-22')
        self.assertEqual(eh_lst[0].halfday, False)
        self.assertEqual(eh_lst[0].eval_state, 'c')

    @with_transaction()
    def test_evalholidays_create_valid2(self):
        """ test: create valid vacancy day, 2nd way
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()
        
        ev1 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 22),
                evaluation = evobj)
        ev1.save()
        
        eh_lst = EvalHoliday.search([])
        self.assertEqual(len(eh_lst), 1)
        self.assertEqual(str(eh_lst[0].date_start), '2019-03-10')
        self.assertEqual(str(eh_lst[0].date_end), '2019-03-22')
        self.assertEqual(eh_lst[0].halfday, False)

    @with_transaction()
    def test_evalholidays_edit_vacation_day_checkrecalc(self):
        """ test: create vacation day, edit it, check reclac of evaluation
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()
        
        evobj.vacationdays = [
                EvalHoliday(date_start = date(2019, 3, 10),
                        date_end = date(2019, 3, 22)
                    )
            ]
        evobj.save()
        self.assertEqual(evobj.needs_recalc, True)
        evobj.needs_recalc = False
        evobj.save()
        
        self.assertEqual(evobj.needs_recalc, False)

        eh_lst = EvalHoliday.search([])
        self.assertEqual(len(eh_lst), 1)
        eh_lst[0].halfday = True
        eh_lst[0].save()
        
        self.assertEqual(evobj.needs_recalc, True)

    @with_transaction()
    def test_evalholidays_delete_vacation_day_checkrecalc(self):
        """ test: create vacation day, edit it, check reclac of evaluation
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()
        evobj.vacationdays = [
                EvalHoliday(date_start = date(2019, 3, 10),
                        date_end = date(2019, 3, 22)
                    )
            ]
        evobj.save()
        eh_lst = EvalHoliday.search([])
        self.assertEqual(len(eh_lst), 1)      
        self.assertEqual(evobj.needs_recalc, True)
        
        evobj.needs_recalc = False
        evobj.save()
        self.assertEqual(evobj.needs_recalc, False)

        EvalHoliday.delete(eh_lst)
        self.assertEqual(evobj.needs_recalc, True)

    @with_transaction()
    def test_evalholidays_check_unique_start(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        # same start
        ev1 = EvalHoliday(
                date_start = date(2019, 3, 3),
                date_end = date(2019, 3, 5),
                evaluation = evobj)
        ev1.save()
        
        ev2 = EvalHoliday(
                date_start = date(2019, 3, 3),
                date_end = date(2019, 3, 7),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                'There is already an entry for this start date.',
                ev2.save)

    @with_transaction()
    def test_evalholidays_check_unique_end(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        # same end
        ev1 = EvalHoliday(
                date_start = date(2019, 3, 3),
                date_end = date(2019, 3, 5),
                evaluation = evobj)
        ev1.save()
        
        ev2 = EvalHoliday(
                date_start = date(2019, 3, 4),
                date_end = date(2019, 3, 5),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                'There is already an entry for this end date.',
                ev2.save)

    @with_transaction()
    def test_evalholidays_check_start_after_end(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        # start after end
        ev1 = EvalHoliday(
                date_start = date(2019, 3, 15),
                date_end = date(2019, 3, 12),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                'The end date must be after the start date.',
                ev1.save)

    @with_transaction()
    def test_evalholidays_check_end_outside_month(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        # end outside evaluation-month
        ev2 = EvalHoliday(
                date_start = date(2019, 3, 25),
                date_end = date(2019, 4, 5),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                "The beginning and end of the holiday entry must be in the range of '2019-03-01' to '2019-03-31'.",
                ev2.save)

    @with_transaction()
    def test_evalholidays_check_end_outside_month2(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        ev2 = EvalHoliday(
                date_start = date(2019, 3, 25),
                date_end = date(2019, 3, 27),
                evaluation = evobj)
        ev2.save()
        
        # end outside evaluation-month
        ev2.date_end = date(2019, 4, 27)
        self.assertRaisesRegex(UserError,
                "The beginning and end of the holiday entry must be in the range of '2019-03-01' to '2019-03-31'.",
                ev2.save)

    @with_transaction()
    def test_evalholidays_check_startend_outside_month(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        # start+end outside evaluation-month
        ev3 = EvalHoliday(
                date_start = date(2019, 4, 15),
                date_end = date(2019, 4, 17),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                "The beginning and end of the holiday entry must be in the range of '2019-03-01' to '2019-03-31'.",
                ev3.save)

    @with_transaction()
    def test_evalholidays_check_startend_outside_month2(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        ev3 = EvalHoliday(
                date_start = date(2019, 3, 15),
                date_end = date(2019, 3, 17),
                evaluation = evobj)
        ev3.save()
        
        # start+end outside evaluation-month
        ev3.date_start = date(2019, 4, 15)
        ev3.date_end = date(2019, 4, 17)
        self.assertRaisesRegex(UserError,
                "The beginning and end of the holiday entry must be in the range of '2019-03-01' to '2019-03-31'.",
                ev3.save)

    @with_transaction()
    def test_evalholidays_get_overlap_days(self):
        """ test: create vacation day, check function 'get_overlap_days'
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        # overlap
        ev1 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 15),
                evaluation = evobj)
        ev1.save()
        
        # no overlap
        self.assertEqual(
            EvalHoliday.get_overlap_days(evobj, date(2019, 3, 6), date(2019, 3, 7)), 
            [])

        # overlap at start
        e1 = EvalHoliday.get_overlap_days(evobj, date(2019, 3, 6), date(2019, 3, 12))
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1[0], ev1.id)

        # overlap at end
        e1 = EvalHoliday.get_overlap_days(evobj, date(2019, 3, 13), date(2019, 3, 18))
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1[0], ev1.id)

        # overlap inside
        e1 = EvalHoliday.get_overlap_days(evobj, date(2019, 3, 12), date(2019, 3, 14))
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1[0], ev1.id)

        # overlap around
        e1 = EvalHoliday.get_overlap_days(evobj, date(2019, 3, 8), date(2019, 3, 18))
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1[0], ev1.id)

        # overlap around + ignore ev1
        e1 = EvalHoliday.get_overlap_days(evobj, date(2019, 3, 8), date(2019, 3, 18), ignore_ids=[ev1.id])
        self.assertEqual(len(e1), 0)

    @with_transaction()
    def test_evalholidays_check_create_overlap1(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        ev2 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 17),
                evaluation = evobj)
        ev2.save()
        
        ev3 = EvalHoliday(
                date_start = date(2019, 3, 7),
                date_end = date(2019, 3, 14),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                "The item '2019-03-07 - 2019-03-14' overlaps with '2019-03-10 - 2019-03-17' in the evaluation 'Frida - 2019-03'.",
                ev3.save)

    @with_transaction()
    def test_evalholidays_check_create_overlap2(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        ev2 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 17),
                evaluation = evobj)
        ev2.save()
        
        # a single day item
        ev3 = EvalHoliday(
                date_start = date(2019, 3, 12),
                date_end = date(2019, 3, 12),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                "The item '2019-03-12' overlaps with '2019-03-10 - 2019-03-17' in the evaluation 'Frida - 2019-03'.",
                ev3.save)

    @with_transaction()
    def test_evalholidays_check_edit_overlap1(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        ev2 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 17),
                evaluation = evobj)
        ev2.save()
        
        ev3 = EvalHoliday(
                date_start = date(2019, 3, 7),
                date_end = date(2019, 3, 8),
                evaluation = evobj)
        ev3.save()
        
        ev3.date_end = date(2019, 3, 14)
        self.assertRaisesRegex(UserError,
                "The item '2019-03-07 - 2019-03-14' overlaps with '2019-03-10 - 2019-03-17' in the evaluation 'Frida - 2019-03'.",
                ev3.save)

    @with_transaction()
    def test_evalholidays_check_edit_overlap2(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()

        ev2 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 17),
                evaluation = evobj)
        ev2.save()
        
        # single day
        ev3 = EvalHoliday(
                date_start = date(2019, 3, 7),
                date_end = date(2019, 3, 7),
                evaluation = evobj)
        ev3.save()
        
        ev3.date_start = date(2019, 3, 14)
        ev3.date_end = date(2019, 3, 14)
        self.assertRaisesRegex(UserError,
                "The item '2019-03-14' overlaps with '2019-03-10 - 2019-03-17' in the evaluation 'Frida - 2019-03'.",
                ev3.save)

    @with_transaction()
    def test_evalholidays_create_with_locked_eval(self):
        """ test: create vacancy day, check locking
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        evobj = self.prep_evalholidays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')
        Evaluation.wflock([evobj])
        self.assertEqual(evobj.state, 'l')

        ev1 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 22),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
            "The evaluation 'Frida - 2019-03' is locked, therefore the entry can not be created or changed.",
            ev1.save)

    @with_transaction()
    def test_evalholidays_edit_with_locked_eval(self):
        """ test: create vacancy day, check locking
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        evobj = self.prep_evalholidays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')

        ev1 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 22),
                evaluation = evobj)
        ev1.save()

        Evaluation.wflock([evobj])
        self.assertEqual(evobj.state, 'l')

        ev1.halfday = True
        self.assertRaisesRegex(UserError,
            "The evaluation 'Frida - 2019-03' is locked, therefore the entry can not be created or changed.",
            ev1.save)

    @with_transaction()
    def test_evalholidays_delete_with_locked_eval(self):
        """ test: create vacancy day, check locking
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        evobj = self.prep_evalholidays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')

        ev1 = EvalHoliday(
                date_start = date(2019, 3, 10),
                date_end = date(2019, 3, 22),
                evaluation = evobj)
        ev1.save()

        Evaluation.wflock([evobj])
        self.assertEqual(evobj.state, 'l')

        self.assertRaisesRegex(UserError,
            "The evaluation 'Frida - 2019-03' is locked, therefore the entry can not be created or changed.",
            EvalHoliday.delete,
            [ev1])

    @with_transaction()
    def test_evalholidays_get_optimized_vacation_days(self):
        """ test: create evaluation + calendar + events, check days list
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        CalEvent = pool.get('pim_calendar.event')
        
        evobj = self.prep_evalholidays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')
        cal1 = self.prep_evalholidays_add_calendar(evobj)
        
        # add events to calendar
        ev1 = CalEvent(calendar=cal1, 
                name='ev1', 
                startpos=datetime(2019, 3, 5, 0, 0, 0),
                endpos=datetime(2019, 3, 15, 1, 0, 0),
                wholeday = True)
        ev1.save()
        ev2 = CalEvent(calendar=cal1, 
                name='ev2', 
                startpos=datetime(2019, 3, 16, 0, 0, 0),
                endpos=datetime(2019, 3, 17, 1, 0, 0),
                wholeday = True)
        ev2.save()
        ev3 = CalEvent(calendar=cal1, 
                name='ev3', 
                startpos=datetime(2019, 3, 1, 0, 0, 0),
                endpos=datetime(2019, 3, 3, 1, 0, 0),
                wholeday = True)
        ev3.save()
        ev4 = CalEvent(calendar=cal1, 
                name='ev4', 
                startpos=datetime(2019, 2, 25, 0, 0, 0),
                endpos=datetime(2019, 3, 3, 1, 0, 0),
                wholeday = True)
        ev4.save()
        ev5 = CalEvent(calendar=cal1, 
                name='ev5', 
                startpos=datetime(2019, 3, 25, 0, 0, 0),
                endpos=datetime(2019, 4, 4, 0, 0, 0),
                wholeday = True)
        ev5.save()
        ev6 = CalEvent(calendar=cal1, 
                name='ev6', 
                startpos=datetime(2019, 2, 25, 0, 0, 0),
                endpos=datetime(2019, 4, 4, 0, 0, 0),
                wholeday = True)
        ev6.save()

        l1 = EvalHoliday.get_optimized_vacation_days(evobj, [ev1])
        self.assertEqual(l1, 
            [False, False, False, False, True,  True,  True,  True,  True,  True, 
             True,  True,  True,  True,  True,  False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False])
        l2 = EvalHoliday.get_optimized_vacation_days(evobj, [ev2])
        self.assertEqual(l2, 
            [False, False, False, False, False, False, False, False, False, False, 
             False, False, False, False, False, True,  True,  False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False])
        l3 = EvalHoliday.get_optimized_vacation_days(evobj, [ev3])
        self.assertEqual(l3, 
            [True,  True,  True, False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False])
        l4 = EvalHoliday.get_optimized_vacation_days(evobj, [ev4])
        self.assertEqual(l4, 
            [True,  True,  True, False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False])
        l5 = EvalHoliday.get_optimized_vacation_days(evobj, [ev5])
        self.assertEqual(l5, 
            [False, False, False, False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False, False, False, False, True,  True,  True,  True,  True,  True, 
             True])
        l6 = EvalHoliday.get_optimized_vacation_days(evobj, [ev6])
        self.assertEqual(l6, 
            [True, True, True, True, True, True, True, True, True, True, 
             True, True, True, True, True, True, True, True, True, True, 
             True, True, True, True, True, True, True, True, True, True, 
             True])
        l7 = EvalHoliday.get_optimized_vacation_days(evobj, [])
        self.assertEqual(l7, 
            [False, False, False, False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False])
        l8 = EvalHoliday.get_optimized_vacation_days(evobj, [ev2, ev3, ev5])
        self.assertEqual(l8, 
            [True,  True,  True,  False, False, False, False, False, False, False, 
             False, False, False, False, False, True,  True,  False, False, False, 
             False, False, False, False, True,  True,  True,  True,  True,  True, 
             True])

    @with_transaction()
    def test_evalholidays_get_dates_from_optdays(self):
        """ test: create evaluation, check convert of days list to dates
        """
        EvalHoliday = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        evobj = self.prep_evalholidays_eval()
        
        l1 = [True, True,  True,  False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False, False, False, False, False, False, False, False, False, False, 
             False]
        l2 = EvalHoliday.get_dates_from_optdays(evobj, l1)
        self.assertEqual(l2, [(date(2019, 3, 1), date(2019, 3, 3))])

        l1a = [False, True,  True,  True,  False, False, False, False, False, False, 
               False, False, False, False, False, False, False, False, False, False, 
               False, False, False, False, False, False, False, False, False, False, 
               False]
        l2a = EvalHoliday.get_dates_from_optdays(evobj, l1a)
        self.assertEqual(l2a, [(date(2019, 3, 2), date(2019, 3, 4))])

        l1b = [False, True,  True,  True,  False, False, False, False, False, False, 
               False, False, False, False, False, True,  False, False, False, False, 
               False, False, False, False, False, False, False, False, False, True, 
               True]
        l2b = EvalHoliday.get_dates_from_optdays(evobj, l1b)
        self.assertEqual(l2b, [
            (date(2019, 3, 2), date(2019, 3, 4)),
            (date(2019, 3, 16), date(2019, 3, 16)),
            (date(2019, 3, 30), date(2019, 3, 31)),
            ])

        l1c = [False, False, False, False, False, False, False, False, False, False, 
               False, False, False, False, False, False, False, False, False, False, 
               False, False, False, False, False, False, False, False, False, False, 
               False]
        l2c = EvalHoliday.get_dates_from_optdays(evobj, l1c)
        self.assertEqual(l2c, [])

        l1d = [True, True, True, True, True, True, True, True, True, True, 
               True, True, True, True, True, True, True, True, True, True, 
               True, True, True, True, True, True, True, True, True, True, 
               True]
        l2d = EvalHoliday.get_dates_from_optdays(evobj, l1d)
        self.assertEqual(l2d, [
            (date(2019, 3, 1), date(2019, 3, 31)),
            ])

        l1e = [False, False, False, False, False, False, False, False, False, False, 
               False, False, False, False, False, False, False, False, False, False, 
               False, False, False, False, False, False, False, False, False, False, 
               True]
        l2e = EvalHoliday.get_dates_from_optdays(evobj, l1e)
        self.assertEqual(l2e, [
            (date(2019, 3, 31), date(2019, 3, 31)),
            ])

    @with_transaction()
    def test_evalholidays_updt_days_from_calendar1(self):
        """ test: create calendar, vacancy days, check update of evaluation
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        Calendar = pool.get('pim_calendar.calendar')
        CalEvent = pool.get('pim_calendar.event')
        
        evobj = self.prep_evalholidays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')

        cal1 = self.prep_evalholidays_add_calendar(evobj)

        # add events to calendar
        ev1 = CalEvent(calendar=cal1, 
                name='ev1', 
                startpos=datetime(2019, 3, 12, 0, 0, 0),
                endpos=datetime(2019, 3, 12, 1, 0, 0),
                wholeday = True)
        ev1.save()

        EvalHoliday.updt_days_from_calendar(evobj)
        
        h_lst = EvalHoliday.search([])      # find all
        self.assertEqual(len(h_lst), 1)
        self.assertEqual(str(h_lst[0].date_start), '2019-03-12')
        self.assertEqual(str(h_lst[0].date_end), '2019-03-12')
        self.assertEqual(h_lst[0].autoitem, True)
        self.assertEqual(h_lst[0].evaluation.rec_name, 'Frida - 2019-03')

        # add more events
        ev1.endpos = datetime(2019, 3, 14, 1, 0, 0)
        ev1.save()
        ev2 = CalEvent(calendar=cal1, 
                name='ev2', 
                startpos=datetime(2019, 3, 1, 0, 0, 0),
                endpos=datetime(2019, 3, 4, 1, 0, 0),
                wholeday = True)
        ev2.save()
        ev3 = CalEvent(calendar=cal1, 
                name='ev2', 
                startpos=datetime(2019, 3, 25, 0, 0, 0),
                endpos=datetime(2019, 4, 4, 0, 0, 0),
                wholeday = True)
        ev3.save()

        EvalHoliday.updt_days_from_calendar(evobj)

        h2_lst = EvalHoliday.search([], order=[('date_start', 'ASC')])      # find all
        self.assertEqual(len(h2_lst), 3)
        
        self.assertEqual(str(h2_lst[0].date_start), '2019-03-01')
        self.assertEqual(str(h2_lst[0].date_end), '2019-03-04')
        self.assertEqual(h2_lst[0].autoitem, True)
        self.assertEqual(h2_lst[0].evaluation.rec_name, 'Frida - 2019-03')

        self.assertEqual(str(h2_lst[1].date_start), '2019-03-12')
        self.assertEqual(str(h2_lst[1].date_end), '2019-03-14')
        self.assertEqual(h2_lst[1].autoitem, True)
        self.assertEqual(h2_lst[1].evaluation.rec_name, 'Frida - 2019-03')

        self.assertEqual(str(h2_lst[2].date_start), '2019-03-25')
        self.assertEqual(str(h2_lst[2].date_end), '2019-03-31')
        self.assertEqual(h2_lst[2].autoitem, True)
        self.assertEqual(h2_lst[2].evaluation.rec_name, 'Frida - 2019-03')

        # delete cal event
        CalEvent.delete([ev3])
        EvalHoliday.updt_days_from_calendar(evobj)
        h3_lst = EvalHoliday.search([], order=[('date_start', 'ASC')])      # find all
        self.assertEqual(len(h3_lst), 2)
        
        self.assertEqual(str(h3_lst[0].date_start), '2019-03-01')
        self.assertEqual(str(h3_lst[0].date_end), '2019-03-04')
        self.assertEqual(h3_lst[0].autoitem, True)
        self.assertEqual(h3_lst[0].evaluation.rec_name, 'Frida - 2019-03')

        self.assertEqual(str(h3_lst[1].date_start), '2019-03-12')
        self.assertEqual(str(h3_lst[1].date_end), '2019-03-14')
        self.assertEqual(h3_lst[1].autoitem, True)
        self.assertEqual(h3_lst[1].evaluation.rec_name, 'Frida - 2019-03')

    @with_transaction()
    def test_evalholidays_updt_days_from_calendar2(self):
        """ test: create calendar, vacancy days, add vacation day manually, check update of evaluation
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        Calendar = pool.get('pim_calendar.calendar')
        CalEvent = pool.get('pim_calendar.event')
        
        evobj = self.prep_evalholidays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')

        cal1 = self.prep_evalholidays_add_calendar(evobj)

        # add events to calendar
        ev1 = CalEvent(calendar=cal1, 
                name='ev1', 
                startpos=datetime(2019, 3, 12, 0, 0, 0),
                endpos=datetime(2019, 3, 12, 1, 0, 0),
                wholeday = True)
        ev1.save()

        vd1 = EvalHoliday(evaluation=evobj,
                date_start = date(2019, 3, 7),
                date_end = date(2019, 3, 9))
        vd1.save()
        
        vd_lst1 = EvalHoliday.search([])
        self.assertEqual(len(vd_lst1), 1)
        self.assertEqual(str(vd_lst1[0].date_start), '2019-03-07')
        self.assertEqual(str(vd_lst1[0].date_end), '2019-03-09')
        self.assertEqual(vd_lst1[0].autoitem, False)
        self.assertEqual(vd_lst1[0].halfday, False)
        
        EvalHoliday.updt_days_from_calendar(evobj)
        
        vd_lst2 = EvalHoliday.search([], order=[('date_start', 'ASC')])
        self.assertEqual(len(vd_lst2), 2)

        self.assertEqual(str(vd_lst2[0].date_start), '2019-03-07')
        self.assertEqual(str(vd_lst2[0].date_end), '2019-03-09')
        self.assertEqual(vd_lst2[0].autoitem, False)
        self.assertEqual(vd_lst2[0].halfday, False)

        self.assertEqual(str(vd_lst2[1].date_start), '2019-03-12')
        self.assertEqual(str(vd_lst2[1].date_end), '2019-03-12')
        self.assertEqual(vd_lst2[1].autoitem, True)
        self.assertEqual(vd_lst2[1].halfday, False)

    @with_transaction()
    def test_evalholidays_updt_days_from_calendar3(self):
        """ test: create calendar, vacancy days, add vacation day manually overlapping, check update of evaluation
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        Calendar = pool.get('pim_calendar.calendar')
        CalEvent = pool.get('pim_calendar.event')
        
        evobj = self.prep_evalholidays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')

        cal1 = self.prep_evalholidays_add_calendar(evobj)

        # add events to calendar
        # no autoitem for this cal-event, because user adds a manually item
        ev1 = CalEvent(calendar=cal1, 
                name='ev1', 
                startpos=datetime(2019, 3, 12, 0, 0, 0),
                endpos=datetime(2019, 3, 12, 1, 0, 0),
                wholeday = True)
        ev1.save()
        # 2x autoitems, because user adds a manually item in date range
        ev2 = CalEvent(calendar=cal1, 
                name='ev2', 
                startpos=datetime(2019, 3, 20, 0, 0, 0),
                endpos=datetime(2019, 3, 28, 1, 0, 0),
                wholeday = True)
        ev2.save()

        # add manually vacation days to evaluation
        vd1 = EvalHoliday(evaluation=evobj,
                date_start = date(2019, 3, 7),
                date_end = date(2019, 3, 15))
        vd1.save()
        vd2 = EvalHoliday(evaluation=evobj,
                date_start = date(2019, 3, 22),
                date_end = date(2019, 3, 23))
        vd2.save()
        
        # check before
        vd_lst1 = EvalHoliday.search([], order=[('date_start', 'ASC')])
        self.assertEqual(len(vd_lst1), 2)
        self.assertEqual(str(vd_lst1[0].date_start), '2019-03-07')
        self.assertEqual(str(vd_lst1[0].date_end), '2019-03-15')
        self.assertEqual(vd_lst1[0].autoitem, False)
        self.assertEqual(vd_lst1[0].halfday, False)
        self.assertEqual(str(vd_lst1[1].date_start), '2019-03-22')
        self.assertEqual(str(vd_lst1[1].date_end), '2019-03-23')
        self.assertEqual(vd_lst1[1].autoitem, False)
        self.assertEqual(vd_lst1[1].halfday, False)
        
        EvalHoliday.updt_days_from_calendar(evobj)

        # check result
        vd_lst2 = EvalHoliday.search([], order=[('date_start', 'ASC')])
        self.assertEqual(len(vd_lst2), 4)

        self.assertEqual(str(vd_lst2[0].date_start), '2019-03-07')
        self.assertEqual(str(vd_lst2[0].date_end), '2019-03-15')
        self.assertEqual(vd_lst2[0].autoitem, False)
        self.assertEqual(vd_lst2[0].halfday, False)

        self.assertEqual(str(vd_lst2[1].date_start), '2019-03-20')
        self.assertEqual(str(vd_lst2[1].date_end), '2019-03-21')
        self.assertEqual(vd_lst2[1].autoitem, True)
        self.assertEqual(vd_lst2[1].halfday, False)
        
        self.assertEqual(str(vd_lst2[2].date_start), '2019-03-22')
        self.assertEqual(str(vd_lst2[2].date_end), '2019-03-23')
        self.assertEqual(vd_lst2[2].autoitem, False)
        self.assertEqual(vd_lst2[2].halfday, False)

        self.assertEqual(str(vd_lst2[3].date_start), '2019-03-24')
        self.assertEqual(str(vd_lst2[3].date_end), '2019-03-28')
        self.assertEqual(vd_lst2[3].autoitem, True)
        self.assertEqual(vd_lst2[3].halfday, False)

    @with_transaction()
    def test_evalholidays_updt_days_from_calendar4(self):
        """ test: create calendar + events, add vacation day manually, check update
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        Calendar = pool.get('pim_calendar.calendar')
        CalEvent = pool.get('pim_calendar.event')
        
        evobj = self.prep_evalholidays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')

        cal1 = self.prep_evalholidays_add_calendar(evobj)

        # add events to calendar
        ev1 = CalEvent(calendar=cal1, 
                name='ev1', 
                startpos=datetime(2019, 3, 6, 0, 0, 0),
                endpos=datetime(2019, 3, 16, 1, 0, 0),
                wholeday = True)
        ev1.save()

        # add manually vacation days to evaluation
        vd1 = EvalHoliday(evaluation=evobj,
                date_start = date(2019, 3, 4),
                date_end = date(2019, 3, 8))
        vd1.save()
        
        # check before
        vd_lst1 = EvalHoliday.search([])
        self.assertEqual(len(vd_lst1), 1)
        self.assertEqual(str(vd_lst1[0].date_start), '2019-03-04')
        self.assertEqual(str(vd_lst1[0].date_end), '2019-03-08')
        self.assertEqual(vd_lst1[0].autoitem, False)
        
        EvalHoliday.updt_days_from_calendar(evobj)
        
        # check result 1
        vd_lst2 = EvalHoliday.search([], order=[('date_start', 'ASC')])
        self.assertEqual(len(vd_lst2), 2)
        self.assertEqual(str(vd_lst2[0].date_start), '2019-03-04')
        self.assertEqual(str(vd_lst2[0].date_end), '2019-03-08')
        self.assertEqual(vd_lst2[0].autoitem, False)
        self.assertEqual(str(vd_lst2[1].date_start), '2019-03-09')
        self.assertEqual(str(vd_lst2[1].date_end), '2019-03-16')
        self.assertEqual(vd_lst2[1].autoitem, True)
        
        # user deletes manually item
        EvalHoliday.delete([vd1])
        
        EvalHoliday.updt_days_from_calendar(evobj)

        # vacation day should be from 6. to 16.
        vd_lst3 = EvalHoliday.search([], order=[('date_start', 'ASC')])
        self.assertEqual(len(vd_lst3), 1)
        self.assertEqual(str(vd_lst3[0].date_start), '2019-03-06')
        self.assertEqual(str(vd_lst3[0].date_end), '2019-03-16')
        self.assertEqual(vd_lst3[0].autoitem, True)
        
        id1 = vd_lst3[0].id

        # run update again, no changes, ids should be same
        EvalHoliday.updt_days_from_calendar(evobj)

        vd_lst4 = EvalHoliday.search([], order=[('date_start', 'ASC')])
        self.assertEqual(len(vd_lst4), 1)
        self.assertEqual(vd_lst4[0].id, id1)

    @with_transaction()
    def test_evalholidays_get_vacation_days_wo_manually(self):
        """ create list-of-days, evaluation, add manually vacation days, check function
        """
        pool = Pool()
        EvalHoliday = pool.get('employee_timetracking.evaluation_vacationdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        evobj = self.prep_evalholidays_eval()

        # add some vacation days
        vd1 = EvalHoliday(evaluation=evobj, 
                date_start = date(2019, 3, 12),
                date_end = date(2019, 3, 14),
                autoitem = True
                )
        vd1.save()
        vd2 = EvalHoliday(evaluation=evobj, 
                date_start = date(2019, 3, 16),
                date_end = date(2019, 3, 19),
                autoitem = False
                )
        vd2.save()
        daylst = [
            False, False, False, False, False, False, False, False, False, False, 
            True,  True,  True,  True,  True,  True,  True,  True,  True,  True, 
            False, False, False, False, False, False, False, False, False, False, 
            False
            ]
        
        daylst2 = EvalHoliday.get_vacation_days_wo_manually(evobj, daylst)
        self.assertEqual(daylst2, [
            False, False, False, False, False, False, False, False, False, False, 
            True,  True,  True,  True,  True,  False, False, False, False, True, 
            False, False, False, False, False, False, False, False, False, False, 
            False
            ])

# end EvaluationHolidaysTestCase
