# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_employee, create_trytonuser,\
    create_evaluation, create_tariff_full
from datetime import datetime, date


class CalendarTestCase(ModuleTestCase):
    'Test calendar module'
    module = 'employee_timetracking'

    def prep_calendar_employee(self):
        """ create company, employee, trytonuser etc.
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

            usr1 = create_trytonuser('frida', 'Test.1234')
            usr1.main_company = tarobj1.company
            usr1.company = tarobj1.company
            usr1.save()
            self.assertTrue(usr1)
            self.assertEqual(usr1.name, 'frida')

            self.assertEqual(employee1.trytonuser, None)
            usr1.employees = [employee1]
            usr1.employee = employee1
            usr1.save()
            self.assertEqual(employee1.trytonuser.name, 'frida')
        return employee1

    def prep_calendar_add_calendar(self, employee):
        """ add tryton user and calendar to DB
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        with set_company(employee.company):
            evobj = create_evaluation(employee, date(2019, 3, 4))
        
            # add calendar
            cal1 = Calendar(
                    name='Cal1',
                    owner=evobj.employee.trytonuser,
                    allday_events = True,
                )
            cal1.save()
            evobj.employee.calendar = cal1
            evobj.employee.save()

        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')
        self.assertEqual(evobj.employee.calendar.rec_name, 'Cal1 (frida)')
        return evobj

    @with_transaction()
    def test_calendar_add_to_user(self):
        """ create calendar, add to tryton user
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.party.name, 'Frida')
        self.assertEqual(employee.trytonuser.name, 'frida')
        self.assertEqual(employee.company.party.name, 'm-ds 1')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')
        
        employee.calendar = cal1
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal1')
        
    @with_transaction()
    def test_calendar_add_from_wrong_owner(self):
        """ create calendar, add to tryton user, connect calendar from wrong owner
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.party.name, 'Frida')
        self.assertEqual(employee.trytonuser.name, 'frida')
        self.assertEqual(employee.company.party.name, 'm-ds 1')

        # 2nd tryton user + employee
        company = employee.company
        with set_company(company):
            # add tryton user
            usr2 = create_trytonuser('diego', 'Test.1234')
            usr2.main_company = company
            usr2.company = company
            usr2.save()
            self.assertTrue(usr2)
            self.assertEqual(usr2.name, 'diego')

            employee2 = create_employee(company, name='Diego')
            self.assertTrue(employee2)
            self.assertEqual(employee2.trytonuser, None)
            usr2.employees = [employee2]
            usr2.employee = employee2
            usr2.save()
            self.assertEqual(employee2.trytonuser.name, 'diego')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')

        cal2 = Calendar(
                name='Cal2',
                owner=employee2.trytonuser,
                allday_events = True,
            )
        cal2.save()
        self.assertEqual(cal2.name, 'Cal2')
        self.assertEqual(cal2.owner.rec_name, 'diego')
        
        employee.calendar = cal2
        self.assertRaisesRegex(UserError, 
            'The value of the field "Holiday Calendar" on "Employee" is not valid according to its domain.',
            employee.save)

    @with_transaction()
    def test_calendar_check_mark_evaluation_recalc(self):
        """ create employee, evaluation, calendar, add events, check 'mark_evaluation_recalc()'
        """
        pool = Pool()
        Event = pool.get('pim_calendar.event')
        Calendar = pool.get('pim_calendar.calendar')
        Evaluation = pool.get('employee_timetracking.evaluation')

        employee = self.prep_calendar_employee()
        evaluation = self.prep_calendar_add_calendar(employee)
        ev_lst = Evaluation.search([])
        self.assertEqual(len(ev_lst), 1)
        self.assertEqual(ev_lst[0].rec_name, 'Frida - 2019-03')

        # add 2nd + 3rd evaluation
        with set_company(employee.company):
            evobj3 = create_evaluation(employee, date(2019, 2, 4))
            self.assertEqual(evobj3.rec_name, 'Frida - 2019-02')
            evobj2 = create_evaluation(employee, date(2019, 4, 4))
            self.assertEqual(evobj2.rec_name, 'Frida - 2019-04')

        # add event to calendar
        ev1 = Event(calendar = employee.calendar,
            name = 'ev1',
            startpos = datetime(2019, 3, 5, 0, 0, 0),
            endpos = datetime(2019, 3, 8, 0, 0, 0),
            wholeday = True)
        ev1.save()
        self.assertEqual(ev1.rec_name, 'ev1 - 05.03.2019 00:00 - 08.03.2019 00:00 (Cal1 (frida))')
        
        todo_lst = Event.add_to_calendar_mark({}, employee.calendar, ev1)
        self.assertEqual(todo_lst, {employee.calendar.id: [(date(2019, 3, 5), date(2019, 3, 8))]})

        # disable recalc
        ev_lst2 = Evaluation.search([], order=[('evaldate', 'ASC')])
        self.assertEqual(len(ev_lst2), 3)
        self.assertEqual(ev_lst2[0].rec_name, 'Frida - 2019-02')
        self.assertEqual(ev_lst2[0].needs_recalc, True)
        ev_lst2[0].needs_recalc = False
        ev_lst2[0].save()
        self.assertEqual(ev_lst2[1].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst2[1].needs_recalc, True)
        ev_lst2[1].needs_recalc = False
        ev_lst2[1].save()
        self.assertEqual(ev_lst2[2].rec_name, 'Frida - 2019-04')
        self.assertEqual(ev_lst2[2].needs_recalc, True)
        ev_lst2[2].needs_recalc = False
        ev_lst2[2].save()

        Calendar.mark_evaluation_recalc(todo_lst)
        
        # check result
        ev_lst3 = Evaluation.search([], order=[('evaldate', 'ASC')])
        self.assertEqual(len(ev_lst3), 3)
        self.assertEqual(ev_lst3[0].needs_recalc, False)
        self.assertEqual(ev_lst3[0].rec_name, 'Frida - 2019-02')
        self.assertEqual(ev_lst3[1].needs_recalc, True)
        self.assertEqual(ev_lst3[1].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst3[2].needs_recalc, False)
        self.assertEqual(ev_lst3[2].rec_name, 'Frida - 2019-04')

    @with_transaction()
    def test_calendar_check_mark_evaluation_recalc_no_holidaycal(self):
        """ create employee, evaluation, calendar (no holiday-calendar), add events, check 'mark_evaluation_recalc()'
        """
        pool = Pool()
        Event = pool.get('pim_calendar.event')
        Calendar = pool.get('pim_calendar.calendar')
        Evaluation = pool.get('employee_timetracking.evaluation')

        employee = self.prep_calendar_employee()
        evaluation = self.prep_calendar_add_calendar(employee)
        ev_lst = Evaluation.search([])
        self.assertEqual(len(ev_lst), 1)
        self.assertEqual(ev_lst[0].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst[0].needs_recalc, True)
        ev_lst[0].needs_recalc = False
        ev_lst[0].save()
        self.assertEqual(ev_lst[0].needs_recalc, False)

        # add 2nd calendar - no a holiday calendar
        cal2 = Calendar(
                name='Cal2',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal2.save()
        self.assertEqual(cal2.rec_name, 'Cal2 (frida)')

        # add event to calendar 'cal2'
        ev1 = Event(calendar = cal2,
            name = 'ev1-cal2',
            startpos = datetime(2019, 3, 5, 0, 0, 0),
            endpos = datetime(2019, 3, 8, 0, 0, 0),
            wholeday = True)
        ev1.save()
        self.assertEqual(ev1.rec_name, 'ev1-cal2 - 05.03.2019 00:00 - 08.03.2019 00:00 (Cal2 (frida))')

        todo_lst = Event.add_to_calendar_mark({}, cal2, ev1)
        self.assertEqual(todo_lst, {})

        Calendar.mark_evaluation_recalc(todo_lst)
        self.assertEqual(ev_lst[0].needs_recalc, False)

    @with_transaction()
    def test_calendar_add_event_check_recalc(self):
        """ create employee, evaluation, calendar, add events, check 'recalc' of evaluation
        """
        pool = Pool()
        Event = pool.get('pim_calendar.event')
        Evaluation = pool.get('employee_timetracking.evaluation')

        employee = self.prep_calendar_employee()
        evaluation = self.prep_calendar_add_calendar(employee)
        ev_lst = Evaluation.search([])
        self.assertEqual(len(ev_lst), 1)
        self.assertEqual(ev_lst[0].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst[0].needs_recalc, True)
        ev_lst[0].needs_recalc = False
        ev_lst[0].save()
        self.assertEqual(ev_lst[0].needs_recalc, False)

        # add event to calendar
        ev1 = Event(calendar = employee.calendar,
            name = 'ev1',
            startpos = datetime(2019, 3, 5, 0, 0, 0),
            endpos = datetime(2019, 3, 8, 0, 0, 0),
            wholeday = True)
        ev1.save()
        self.assertEqual(ev1.rec_name, 'ev1 - 05.03.2019 00:00 - 08.03.2019 00:00 (Cal1 (frida))')

        ev_lst2 = Evaluation.search([])
        self.assertEqual(len(ev_lst2), 1)
        self.assertEqual(ev_lst2[0].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst2[0].needs_recalc, True)

    @with_transaction()
    def test_calendar_add_event_check_recalc_no_holidaycal(self):
        """ create employee, evaluation, calendar (no holiday calendar), add events, check 'recalc' of evaluation
        """
        pool = Pool()
        Event = pool.get('pim_calendar.event')
        Evaluation = pool.get('employee_timetracking.evaluation')
        Calendar = pool.get('pim_calendar.calendar')

        employee = self.prep_calendar_employee()
        evaluation = self.prep_calendar_add_calendar(employee)
        ev_lst = Evaluation.search([])
        self.assertEqual(len(ev_lst), 1)
        self.assertEqual(ev_lst[0].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst[0].needs_recalc, True)
        ev_lst[0].needs_recalc = False
        ev_lst[0].save()
        self.assertEqual(ev_lst[0].needs_recalc, False)

        # add 2nd calendar
        cal2 = Calendar(name="Cal2", 
                owner=employee.trytonuser,
                allday_events = True)
        cal2.save()

        # add event to calendar
        ev1 = Event(calendar = cal2,
            name = 'ev1',
            startpos = datetime(2019, 3, 5, 0, 0, 0),
            endpos = datetime(2019, 3, 8, 0, 0, 0),
            wholeday = True)
        ev1.save()
        self.assertEqual(ev1.rec_name, 'ev1 - 05.03.2019 00:00 - 08.03.2019 00:00 (Cal2 (frida))')

        ev_lst2 = Evaluation.search([])
        self.assertEqual(len(ev_lst2), 1)
        self.assertEqual(ev_lst2[0].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst2[0].needs_recalc, False)

    @with_transaction()
    def test_calendar_edit_event_check_recalc(self):
        """ create employee, evaluation, calendar, add events, edit it, check 'recalc' of evaluation
        """
        pool = Pool()
        Event = pool.get('pim_calendar.event')
        Evaluation = pool.get('employee_timetracking.evaluation')

        employee = self.prep_calendar_employee()
        evaluation = self.prep_calendar_add_calendar(employee)
        ev_lst = Evaluation.search([])
        self.assertEqual(len(ev_lst), 1)
        self.assertEqual(ev_lst[0].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst[0].needs_recalc, True)
        ev_lst[0].needs_recalc = False
        ev_lst[0].save()
        self.assertEqual(ev_lst[0].needs_recalc, False)

        # add event to calendar
        ev1 = Event(calendar = employee.calendar,
            name = 'ev1',
            startpos = datetime(2019, 3, 5, 0, 0, 0),
            endpos = datetime(2019, 3, 8, 0, 0, 0),
            wholeday = True)
        ev1.save()
        self.assertEqual(ev1.rec_name, 'ev1 - 05.03.2019 00:00 - 08.03.2019 00:00 (Cal1 (frida))')
        
        ev_lst2 = Evaluation.search([])
        self.assertEqual(len(ev_lst2), 1)
        self.assertEqual(ev_lst2[0].needs_recalc, True)
        ev_lst2[0].needs_recalc = False
        ev_lst2[0].save()
        self.assertEqual(ev_lst2[0].needs_recalc, False)
        
        # edit event, evaluation should be set to recalc
        ev1.startpos = datetime(2019, 3, 4, 0, 0, 0)
        ev1.save()

        ev_lst3 = Evaluation.search([])
        self.assertEqual(len(ev_lst3), 1)
        self.assertEqual(ev_lst3[0].needs_recalc, True)

    @with_transaction()
    def test_calendar_del_event_check_recalc(self):
        """ create employee, evaluation, calendar, add events, delete it, check 'recalc' of evaluation
        """
        pool = Pool()
        Event = pool.get('pim_calendar.event')
        Evaluation = pool.get('employee_timetracking.evaluation')

        employee = self.prep_calendar_employee()
        evaluation = self.prep_calendar_add_calendar(employee)
        ev_lst = Evaluation.search([])
        self.assertEqual(len(ev_lst), 1)
        self.assertEqual(ev_lst[0].rec_name, 'Frida - 2019-03')
        self.assertEqual(ev_lst[0].needs_recalc, True)
        ev_lst[0].needs_recalc = False
        ev_lst[0].save()
        self.assertEqual(ev_lst[0].needs_recalc, False)

        # add event to calendar
        ev1 = Event(calendar = employee.calendar,
            name = 'ev1',
            startpos = datetime(2019, 3, 5, 0, 0, 0),
            endpos = datetime(2019, 3, 8, 0, 0, 0),
            wholeday = True)
        ev1.save()
        self.assertEqual(ev1.rec_name, 'ev1 - 05.03.2019 00:00 - 08.03.2019 00:00 (Cal1 (frida))')
        
        ev_lst2 = Evaluation.search([])
        self.assertEqual(len(ev_lst2), 1)
        self.assertEqual(ev_lst2[0].needs_recalc, True)
        ev_lst2[0].needs_recalc = False
        ev_lst2[0].save()
        self.assertEqual(ev_lst2[0].needs_recalc, False)
        
        # delete event, evaluation should be set to recalc
        Event.delete([ev1])

        ev_lst3 = Evaluation.search([])
        self.assertEqual(len(ev_lst3), 1)
        self.assertEqual(ev_lst3[0].needs_recalc, True)

    @with_transaction()
    def test_calendar_check_is_holidaycal(self):
        """ create calendar, add to tryton user, check 'is_holidaycal'
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.party.name, 'Frida')
        self.assertEqual(employee.trytonuser.name, 'frida')
        self.assertEqual(employee.company.party.name, 'm-ds 1')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')

        cal2 = Calendar(
                name='Cal2',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal2.save()
        self.assertEqual(cal2.name, 'Cal2')
        self.assertEqual(cal2.owner.rec_name, 'frida')
        
        employee.calendar = cal1
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal1')
        
        self.assertEqual(cal1.is_holidaycal, True)
        self.assertEqual(cal2.is_holidaycal, False)
        
        c1 = Calendar.search([('is_holidaycal', '=', True)])
        self.assertEqual(len(c1), 1)
        self.assertEqual(c1[0].name, 'Cal1')

        c2 = Calendar.search([('is_holidaycal', '!=', False)])
        self.assertEqual(len(c2), 1)
        self.assertEqual(c2[0].name, 'Cal1')

        c3 = Calendar.search([('is_holidaycal', '=', False)])
        self.assertEqual(len(c3), 1)
        self.assertEqual(c3[0].name, 'Cal2')

        c4 = Calendar.search([('is_holidaycal', '!=', True)])
        self.assertEqual(len(c4), 1)
        self.assertEqual(c4[0].name, 'Cal2')
        
        self.assertRaisesRegex(ValueError,
            'invalid query',
            Calendar.search,
            [('is_holidaycal', 'in', [True, False])])


    @with_transaction()
    def test_calendar_delete_from_user(self):
        """ create calendar, add to tryton user, try to delete the calendar from user
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.trytonuser.name, 'frida')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')
        
        employee.calendar = cal1
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal1')

        employee.calendar = None
        self.assertRaisesRegex(UserError,
            'Deleting calendar from employee is not allowed.',
            employee.save)

    @with_transaction()
    def test_calendar_delete_calendar(self):
        """ create calendar, add to tryton user, try to delete the calendar
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.trytonuser.name, 'frida')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')
        
        employee.calendar = cal1
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal1')

        self.assertRaisesRegex(UserError,
            'Deleting calendar from employee is not allowed.',
            Calendar.delete,
            [cal1])

    @with_transaction()
    def test_calendar_switch1_calendar(self):
        """ create calendar, add to tryton user, switch to a 2nd calendar
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.trytonuser.name, 'frida')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')

        # calendars must be all-day-only, test result when switching
        cal2 = Calendar(
                name='Cal2',
                owner=employee.trytonuser,
                allday_events = False,
            )
        cal2.save()
        self.assertEqual(cal2.name, 'Cal2')
        self.assertEqual(cal2.owner.rec_name, 'frida')
        
        employee.calendar = cal1
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal1')

        employee.calendar = cal2
        self.assertRaisesRegex(UserError,
            'The value of the field "Holiday Calendar" on "Employee" is not valid according to its domain.',
            employee.save)

    @with_transaction()
    def test_calendar_switch2_calendar(self):
        """ create calendar, add to tryton user, switch to a 2nd calendar
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.trytonuser.name, 'frida')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')

        # calendars must be all-day-only
        cal2 = Calendar(
                name='Cal2',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal2.save()
        self.assertEqual(cal2.name, 'Cal2')
        self.assertEqual(cal2.owner.rec_name, 'frida')
        
        employee.calendar = cal1
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal1')

        employee.calendar = cal2
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal2')

    @with_transaction()
    def test_calendar_disable_allday(self):
        """ create calendar, disable all-day-option, check result
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.party.name, 'Frida')
        self.assertEqual(employee.trytonuser.name, 'frida')
        self.assertEqual(employee.company.party.name, 'm-ds 1')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')
        
        employee.calendar = cal1
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal1')

        cal1.allday_events = False
        self.assertRaisesRegex(UserError,
            'Disabling the all-day option is not allowed as long as the calendar is connected to an employee.',
            cal1.save)

    @with_transaction()
    def test_event_check_allday(self):
        """ create calendar, check event in holiday-calendar
        """
        pool = Pool()
        Calendar = pool.get('pim_calendar.calendar')
        Event = pool.get('pim_calendar.event')
        
        employee = self.prep_calendar_employee()
        self.assertEqual(employee.party.name, 'Frida')
        self.assertEqual(employee.trytonuser.name, 'frida')
        self.assertEqual(employee.company.party.name, 'm-ds 1')

        cal1 = Calendar(
                name='Cal1',
                owner=employee.trytonuser,
                allday_events = True,
            )
        cal1.save()
        self.assertEqual(cal1.name, 'Cal1')
        self.assertEqual(cal1.owner.rec_name, 'frida')

        employee.calendar = cal1
        employee.save()
        self.assertEqual(employee.calendar.name, 'Cal1')

        ev1 = Event(name='E1',
                calendar = cal1,
                startpos = datetime(2019, 3, 27, 0, 0, 0),
                endpos = datetime(2019, 3, 29, 0, 0, 0),
                wholeday = False,
            )
        self.assertRaisesRegex(UserError,
            "In calendar 'Cal1 \(frida\)' only all-day events are allowed.",
            ev1.save)
        
        ev2 = Event(name='E2',
                calendar = cal1,
                startpos = datetime(2019, 3, 27, 0, 0, 0),
                endpos = datetime(2019, 3, 29, 0, 0, 0),
                wholeday = True,
            )
        ev2.save()
        
        ev2.wholeday = False
        self.assertRaisesRegex(UserError,
            "In calendar 'Cal1 \(frida\)' only all-day events are allowed.",
            ev2.save)

# end CalendarTestCase
