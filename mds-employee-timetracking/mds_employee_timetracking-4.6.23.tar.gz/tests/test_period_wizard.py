# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Wizard
from trytond.exceptions import UserError
from datetime import timedelta, datetime
from time import sleep
from trytond.modules.company.tests import set_company
from trytond.modules.employee_timetracking.tests.testlib import create_tariff_full, create_period, create_employee
from trytond.modules.employee_timetracking.const import WF_PERIOD_CREATED, WF_PERIOD_EXAMINE
from trytond.modules.employee_timetracking.period_wizard import CURRSTAT_ACTIVE, CURRSTAT_INACTIVE


class PeriodWizardTestCase(ModuleTestCase):
    'Test period-wizard module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_period_attendance_wizard_start_on_change_employee(self):
        """ test: run on-change-employee with different period-items
        """
        pool = Pool()
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
    
            # run wizard view
            wiz_start = pool.get('employee_timetracking.wizperiod_attendance.start')
            obj1 = wiz_start()

            obj1.employee = None
            obj1.on_change_employee()
            
            # no employee selected
            self.assertEqual(obj1.currstate, CURRSTAT_INACTIVE)
            self.assertEqual(obj1.currtype, '')
            self.assertEqual(obj1.currperiod, None)
            self.assertEqual(obj1.currstart, None)
            self.assertEqual(obj1.presence, None)
            self.assertEqual(obj1.breakstate, CURRSTAT_INACTIVE)
            self.assertEqual(obj1.breakperiod, None)
            self.assertEqual(obj1.breakstart, None)

            # select employee
            obj1.employee = employee1
            obj1.on_change_employee()
            
            self.assertEqual(obj1.company, employee1.company)
            
            # no period exist until now
            self.assertEqual(str(obj1.currstate), CURRSTAT_INACTIVE)
            self.assertEqual(str(obj1.currtype), '')
            self.assertEqual(str(obj1.currperiod), '')
            self.assertEqual(obj1.currstart, None)
            self.assertEqual(obj1.presence.rec_name, 'Work')
            # no break time
            self.assertEqual(obj1.breakstate, CURRSTAT_INACTIVE)
            self.assertEqual(obj1.breakperiod, '')
            self.assertEqual(obj1.breakstart, None)
        
            # add break time
            BreakPeriod = pool.get('employee_timetracking.breakperiod')
            br1 = BreakPeriod(employee=employee1, 
                    startpos=datetime(2019, 2, 5, 10, 5, 0),
                )
            br1.save()
            # update infos
            obj1.on_change_employee()
            self.assertEqual(obj1.breakstate, CURRSTAT_ACTIVE)
            self.assertEqual(str(obj1.breakstart), '2019-02-05 10:05:00')
            br1.endpos = datetime(2019, 2, 5, 10, 35, 0)
            br1.save()
            obj1.on_change_employee()
            self.assertEqual(obj1.breakstate, CURRSTAT_INACTIVE)
            self.assertEqual(obj1.breakstart, None)            

            # add work time item, begin, no end
            create_period(datetime(2018, 3, 10, 10, 30, 0), None, tarobj1.type_present, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_ACTIVE)
            self.assertEqual(obj1.currtype, 'Work')
            self.assertEqual(str(obj1.currstart), '2018-03-10 10:30:00')
            self.assertEqual(obj1.presence.rec_name, 'Work')
    
            # add site work item, 1 day later, begin, no end
            for i in tarobj1.presence:
                if i.name == 'Site work':
                    create_period(datetime(2018, 3, 11, 10, 30, 0), None, i, employee1)
                    break
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_ACTIVE)
            self.assertEqual(obj1.currtype, 'Site work')
            self.assertEqual(str(obj1.currstart), '2018-03-11 10:30:00')
            self.assertEqual(obj1.presence.rec_name, 'Site work')
    
            # add ill item, 1 day later, begin, no end
            Presence = pool.get('employee_timetracking.presence')
            l1 = Presence.search([('company', '=', employee1.company), ('name', '=', 'Ill')])
            create_period(datetime(2018, 3, 12, 8, 0, 0), None, l1[0], employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_ACTIVE)
            self.assertEqual(obj1.currtype, 'Ill')
            self.assertEqual(str(obj1.currstart), '2018-03-12 08:00:00')
            self.assertEqual(obj1.presence.rec_name, 'Ill')
    
            # add work time item, begin+end
            create_period(datetime(2018, 3, 13, 8, 30, 0), datetime(2018, 3, 13, 16, 30, 0), tarobj1.type_present, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_INACTIVE)
            self.assertEqual(obj1.currtype, '')
            self.assertEqual(obj1.currstart, None)
            self.assertEqual(obj1.currperiod, '')
            self.assertEqual(obj1.presence.rec_name, 'Work')
    
            # add 2 work time items, begin+no-end, no-begin+end
            create_period(datetime(2018, 3, 15, 8, 30, 0), None, tarobj1.type_present, employee1)
            create_period(None, datetime(2018, 3, 14, 16, 30, 0), tarobj1.type_present, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_ACTIVE)
            self.assertEqual(obj1.currtype, 'Work')
            self.assertEqual(str(obj1.currstart), '2018-03-15 08:30:00')
            self.assertEqual(obj1.presence.rec_name, 'Work')
    
            # add 2 work time items, no-begin+end, begin+no-end
            create_period(None, datetime(2018, 3, 17, 16, 30, 0), tarobj1.type_present, employee1)
            create_period(datetime(2018, 3, 16, 8, 30, 0), None, tarobj1.type_present, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_INACTIVE)
            self.assertEqual(obj1.currtype, '')
            self.assertEqual(obj1.currstart, None)
            self.assertEqual(obj1.currperiod, '')
            self.assertEqual(obj1.presence.rec_name, 'Work')

    @with_transaction()
    def test_period_attendance_wizard_start_get_delta(self):
        """ test: get timedelta 
        """
        wiz_start = Pool().get('employee_timetracking.wizperiod_attendance.start')
        obj1 = wiz_start()
        self.assertEqual(str(obj1.get_delta(datetime.now() - timedelta(seconds=5*60))), '0:05:00')
        self.assertEqual(str(obj1.get_delta(datetime.now() - timedelta(seconds=5*60 + 15))), '0:05:00')
        self.assertEqual(str(obj1.get_delta(datetime.now() - timedelta(days=2, seconds=5*60))), '2 days, 0:05:00')

    @with_transaction()
    def test_period_attendance_wizard_start_format_timedelta(self):
        """ test: convert timedelta to string
        """
        wiz_start = Pool().get('employee_timetracking.wizperiod_attendance.start')
        
        obj1 = wiz_start()
        self.assertEqual(
                obj1.format_timedelta(timedelta(seconds=60*60*5 + 60*24, days=2)), 
                '2 d, 5 h, 24 m'
            )
        self.assertEqual(
                obj1.format_timedelta(timedelta(seconds=60*60*5 + 60*24, days=0)), 
                '5 h, 24 m'
            )
        self.assertEqual(
                obj1.format_timedelta(timedelta(seconds=60*60*18 + 60*25, days=0)), 
                '18 h, 25 m'
            )
        self.assertEqual(
                obj1.format_timedelta(timedelta(seconds=60*60*18 + 60*25 + 15, days=0)), 
                '18 h, 25 m'
            )

    @with_transaction()
    def test_period_attendance_wizard_start_worktime(self):
        """ test: create tariff+employee, start work time
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                self.assertEqual(start_state, 'start')
                self.assertEqual(end_state, 'end')
                w_obj = PerAttndWizard(sess_id)
                self.assertTrue(w_obj)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                self.assertEqual(list(result.keys()), ['view'])

                self.assertEqual(result['view']['defaults']['company'], tarobj1.company.id)
                self.assertEqual(result['view']['defaults']['employee'], employee1.id)
                self.assertEqual(result['view']['defaults']['currstate'], 'c')

                # transitions fire exception w/o tariff
                w_obj.start.employee = None
                self.assertRaisesRegex(UserError, "Please select an employee first.", w_obj.transition_beginning)
                self.assertRaisesRegex(UserError, "Please select an employee first.", w_obj.transition_ending)

                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                setattr(w_obj.start, 'presence', None)

                self.assertEqual(w_obj.start.company, tarobj1.company)
                self.assertEqual(w_obj.start.employee, employee1)
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence, None)

                # transitions fire exception w/o tariff on employee
                self.assertRaisesRegex(UserError, 
                    "Please assign a tariff to employee 'Frida' first.", 
                    w_obj.transition_beginning)
                self.assertRaisesRegex(UserError, 
                    "Please assign a tariff to employee 'Frida' first.", 
                    w_obj.transition_ending)
                self.assertRaisesRegex(UserError, 
                    "Please assign a tariff to employee 'Frida' first.", 
                    w_obj.start.on_change_employee)
        
                employee1.tariff = tarobj1
                employee1.save()
                w_obj.start.on_change_employee()
                
                # start work item
                self.assertEqual(w_obj.start.presence, tarobj1.type_present)
                w_obj.transition_beginning()
                p_lst = Period.search([('employee', '=', employee1)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].presence, tarobj1.type_present)
                self.assertEqual(isinstance(p_lst[0].startpos, type(None)), False)
                self.assertEqual(isinstance(p_lst[0].endpos, type(None)), True)
                
                # wait - otherwise: startpos > endpos --> exception
                sleep(6.0)
                
                # start site work (the still open work time will be closed)
                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))
                
                w_obj.start.presence = type_sitew
                w_obj.transition_beginning()
                s_lst = Period.search([('employee', '=', employee1), ('presence', '=', type_sitew)])
                self.assertEqual(len(s_lst), 1)
                self.assertEqual(s_lst[0].presence, type_sitew)
                self.assertEqual(isinstance(s_lst[0].startpos, type(None)), False)
                self.assertEqual(isinstance(s_lst[0].endpos, type(None)), True)
                # work item is closed by 'startsite'
                self.assertEqual(isinstance(p_lst[0].endpos, type(None)), False)
                
                # end site work
                sleep(1.5)
                w_obj.start.presence = type_sitew
                w_obj.transition_ending()
                self.assertEqual(isinstance(s_lst[0].endpos, type(None)), False)
                
                # stop wizard
                PerAttndWizard.delete(sess_id)
                
    # to check
    # period items
    # no period-items in db:            start (0)  / end (1)  work, start (2)  / end (3) site-work (4x checks)
    # 1x [start|...] (2h ago) in db:    start (4)  / end (5)  work, start (6)  / end (7) site-work (4x checks)
    # 1x [start|...] (13h ago) in db:   start (8)  / end (9)  work, start (10) / end (11) site-work (4x checks)
    # 1x [.....|end] in db:             start (12) / end (13) work, start (14) / end (15) site-work (4x checks)
    # 1x [start|end] in db:             start (16) / end (17) work, start (18) / end (19) site-work (4x checks)
    # break time items
    # no break-time-items in db:        start (20) / end (21) (2x checks)
    # 1x [start|...] (30min ago) in db: start (22) / end (23) (2x checks)
    # 1x [.....|end] in db:             start (24) / end (25) (2x checks)
    # 1x [start|end] in db:             start (26) / end (27) (2x checks)
    @with_transaction()
    def test_period_wizard_start_0(self):
        """ test: create tariff+employee, start work time, no periods in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # coming
                dt1 = datetime.now()
                r1 = w_obj.transition_beginning()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')
                
                # get period
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                t1 = str()
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= p_lst[0].startpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')
                
    @with_transaction()
    def test_period_wizard_start_1(self):
        """ test: create tariff+employee, end work time, no periods in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')                

                # going
                dt1 = datetime.now()
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # get period
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_2(self):
        """ test: create tariff+employee, start site work, no periods in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # start site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))
                
                w_obj.start.presence = type_sitew
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')

                # get period
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_3(self):
        """ test: create tariff+employee, end site work, no periods in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # start site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')

                # get period
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_4(self):
        """ test: create tariff+employee, start work time, [start|...] (2h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=2 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = None
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p1.endpos, None)
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(str(w_obj.start.currstart), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(w_obj.start.currperiod, '2 h, 00 m')
                self.assertEqual(w_obj.start.currtype, 'Work')
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # coming
                dt1 = datetime.now()
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item has now 'endpos'
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p_lst[0].startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                dt3 = dt1 - timedelta(seconds=5)
                dt3a = dt1a - timedelta(seconds=5)
                self.assertTrue(
                    datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt3a.year, dt3a.month, dt3a.day, dt3a.hour, dt3a.minute, dt3a.second))
                self.assertEqual(p_lst[0].state, 'e')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_5(self):
        """ test: create tariff+employee, end work time, [start|...] (2h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=2 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = None
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p1.endpos, None)
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(str(w_obj.start.currstart), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(w_obj.start.currperiod, '2 h, 00 m')
                self.assertEqual(w_obj.start.currtype, 'Work')
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # going
                dt1 = datetime.now()
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we still have 1x item
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 1)

                # get period
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p_lst[0].startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'e')

    @with_transaction()
    def test_period_wizard_start_6(self):
        """ test: create tariff+employee, start site work, [start|...] (2h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')

        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=2 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = None
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p1.endpos, None)
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(str(w_obj.start.currstart), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(w_obj.start.currperiod, '2 h, 00 m')
                self.assertEqual(w_obj.start.currtype, 'Work')
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # start site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                self.assertEqual(w_obj.start.presence.rec_name, 'Site work')
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2x items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)

                # old item has now 'endpos'
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p_lst[0].startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                dt3 = datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) - timedelta(seconds=5)
                dt3a = datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second) - timedelta(seconds=5)
                self.assertTrue(dt3 <= p_lst[0].endpos <= dt3a)
                self.assertEqual(p_lst[0].state, 'e')

                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_7(self):
        """ test: create tariff+employee, end site work, [start|...] (2h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')

        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=2 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = None
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p1.endpos, None)
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(str(w_obj.start.currstart), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(w_obj.start.currperiod, '2 h, 00 m')
                self.assertEqual(w_obj.start.currtype, 'Work')
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # end site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                self.assertEqual(w_obj.start.presence.rec_name, 'Site work')
                r1 = w_obj.transition_ending()
                self.assertEqual(r1, 'end')
                dt1a = datetime.now()
                
                # we have 2x items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)

                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p_lst[0].startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) >= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_8(self):
        """ test: create tariff+employee, start work, [start|...] in db (13h ago)
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=13 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = None
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p1.endpos, None)
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(str(w_obj.start.currstart), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(w_obj.start.currperiod, '13 h, 00 m')
                self.assertEqual(w_obj.start.currtype, 'Work')
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # coming
                dt1 = datetime.now()
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p_lst[0].startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_9(self):
        """ test: create tariff+employee, end work, [start|...] in db (13h ago)
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=13 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = None
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p1.endpos, None)
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(str(w_obj.start.currstart), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(w_obj.start.currperiod, '13 h, 00 m')
                self.assertEqual(w_obj.start.currtype, 'Work')
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # going
                dt1 = datetime.now()
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')

                # we have 1 item
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 1)
                
                # get period
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p_lst[0].startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'e')

    @with_transaction()
    def test_period_wizard_start_10(self):
        """ test: create tariff+employee, start site work, [start|...] in db (13h ago)
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=13 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = None
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p1.endpos, None)
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(str(w_obj.start.currstart), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(w_obj.start.currperiod, '13 h, 00 m')
                self.assertEqual(w_obj.start.currtype, 'Work')
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # start site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                self.assertEqual(w_obj.start.presence.rec_name, 'Site work')
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p_lst[0].startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_11(self):
        """ test: create tariff+employee, end site work, [start|...] in db (13h ago)
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=13 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = None
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p1.endpos, None)
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(str(w_obj.start.currstart), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(w_obj.start.currperiod, '13 h, 00 m')
                self.assertEqual(w_obj.start.currtype, 'Work')
                self.assertEqual(w_obj.start.currstate, 'c')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # end site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                r1 = w_obj.transition_ending()
                self.assertEqual(w_obj.start.presence.rec_name, 'Site work')
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p_lst[0].startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_12(self):
        """ test: create tariff+employee, start work time, [.....|end] (2h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=2 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = None,
                        endpos = dt2,
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(p1.startpos, None)
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # coming
                dt1 = datetime.now()
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertEqual(str(p_lst[0].endpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p_lst[0].state, 'c')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_13(self):
        """ test: create tariff+employee, end work time, [.....|end] (2h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=2 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = None,
                        endpos = dt2,
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(p1.startpos, None)
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # going
                dt1 = datetime.now()
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertEqual(str(p_lst[0].endpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p_lst[0].state, 'c')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_14(self):
        """ test: create tariff+employee, start site work, [.....|end] (2h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=2 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = None,
                        endpos = dt2,
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(p1.startpos, None)
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # start site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                self.assertEqual(w_obj.start.presence.rec_name, 'Site work')
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertEqual(str(p_lst[0].endpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p_lst[0].state, 'c')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_15(self):
        """ test: create tariff+employee, end site work, [.....|end] (2h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=2 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = None,
                        endpos = dt2,
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(p1.startpos, None)
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # end site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                self.assertEqual(w_obj.start.presence.rec_name, 'Site work')
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertEqual(str(p_lst[0].endpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(p_lst[0].state, 'c')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_16(self):
        """ test: create tariff+employee, start work time, [start|end] (12h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=12 * 60 * 60)
                dt3 = dt2 + timedelta(seconds=4 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = dt3,
                    )
                p1.save()
                Period.wfexamine([p1])
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(p1.state, 'e')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second)))
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # coming
                dt1 = datetime.now()
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second)))
                self.assertEqual(p_lst[0].state, 'e')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_17(self):
        """ test: create tariff+employee, end work time, [start|end] (12h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=12 * 60 * 60)
                dt3 = dt2 + timedelta(seconds=4 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = dt3,
                    )
                p1.save()
                Period.wfexamine([p1])
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(p1.state, 'e')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second)))
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # going
                dt1 = datetime.now()
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second)))
                self.assertEqual(p_lst[0].state, 'e')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_18(self):
        """ test: create tariff+employee, start site work, [start|end] (12h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=12 * 60 * 60)
                dt3 = dt2 + timedelta(seconds=4 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = dt3,
                    )
                p1.save()
                Period.wfexamine([p1])
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(p1.state, 'e')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second)))
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # start site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                self.assertEqual(w_obj.start.presence.rec_name, 'Site work')
                r1 = w_obj.transition_beginning()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second)))
                self.assertEqual(p_lst[0].state, 'e')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_19(self):
        """ test: create tariff+employee, end site work, [start|end] (12h ago) in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=12 * 60 * 60)
                dt3 = dt2 + timedelta(seconds=4 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = dt3,
                    )
                p1.save()
                Period.wfexamine([p1])
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                self.assertEqual(p1.state, 'e')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second)))
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # start site work
                dt1 = datetime.now()

                type_sitew = None
                for i in tarobj1.presence:
                    if i.name == 'Site work':
                        type_sitew = i
                self.assertTrue(not isinstance(type_sitew, type(None)))

                w_obj.start.presence = type_sitew
                self.assertEqual(w_obj.start.presence.rec_name, 'Site work')
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')
                
                # we have 2 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 2)
                
                # old item is unchanged
                p_lst = Period.search([('id', '=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Work')
                self.assertEqual(str(p1.startpos), \
                    str(datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second)))
                self.assertEqual(str(p1.endpos), \
                    str(datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt3.minute, dt3.second)))
                self.assertEqual(p_lst[0].state, 'e')
                
                # get new period
                p_lst = Period.search([('id', '!=', p1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(p_lst[0].presence.rec_name, 'Site work')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt1a.year, dt1a.month, dt1a.day, dt1a.hour, dt1a.minute, dt1a.second))
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_20(self):
        """ test: create tariff+employee, start break time, no periods in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.breakstart, None)
                self.assertEqual(w_obj.start.breakperiod, '')
                self.assertEqual(w_obj.start.breakstate, 'i')

                # start break time
                dt1 = datetime.now()
                r1 = w_obj.transition_beginbreak()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')
                
                # get break time period
                p_lst = BreakPeriod.search([])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_21(self):
        """ test: create tariff+employee, end break time, no periods in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.breakstart, None)
                self.assertEqual(w_obj.start.breakperiod, '')
                self.assertEqual(w_obj.start.breakstate, 'i')

                # end break time
                dt1 = datetime.now()
                r1 = w_obj.transition_endbreak()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')
                
                # get break time period
                p_lst = BreakPeriod.search([])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertEqual(p_lst[0].startpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_22(self):
        """ test: create tariff+employee, start break time, 1x [start|...] in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create break time item
                dt1 = datetime.now() - timedelta(seconds=30*60)
                br1 = BreakPeriod(employee = BreakPeriod.default_employee(),
                    startpos = dt1,
                    endpos = None,
                    state = BreakPeriod.default_state(),
                )
                br1.save()
                br_lst = BreakPeriod.search([])
                self.assertEqual(len(br_lst), 1)
                self.assertEqual(br_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(br_lst[0].state, 'c')

                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)

                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertTrue(not isinstance(w_obj.start.breakstart, type(None)))
                self.assertEqual(w_obj.start.breakperiod, '0 h, 30 m')
                self.assertEqual(w_obj.start.breakstate, 'c')

                # end break time
                dt1 = datetime.now()
                r1 = w_obj.transition_beginbreak()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')

                # check result
                br_lst = BreakPeriod.search([])
                self.assertEqual(len(br_lst), 2)
                br_lst = BreakPeriod.search([('id', '=', br1.id)])
                self.assertEqual(len(br_lst), 1)
                self.assertEqual(br_lst[0].state, 'e')
                self.assertTrue(not isinstance(br_lst[0].endpos, type(None)))
                
                # get break time period
                p_lst = BreakPeriod.search([('id', '!=', br1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_23(self):
        """ test: create tariff+employee, end break time, 1x [start|...] in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create break time item
                br1 = BreakPeriod(employee = BreakPeriod.default_employee(),
                    startpos = datetime.now() - timedelta(seconds=30*60),
                    endpos = None,
                    state = BreakPeriod.default_state(),
                )
                br1.save()
                br_lst = BreakPeriod.search([])
                self.assertEqual(len(br_lst), 1)
                self.assertEqual(br_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(br_lst[0].state, 'c')

                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)

                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertTrue(not isinstance(w_obj.start.breakstart, type(None)))
                self.assertEqual(w_obj.start.breakperiod, '0 h, 30 m')
                self.assertEqual(w_obj.start.breakstate, 'c')

                # end break time
                dt1 = datetime.now()
                r1 = w_obj.transition_endbreak()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')

                # check result
                p_lst = BreakPeriod.search([])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].state, 'e')
                self.assertTrue(not isinstance(p_lst[0].endpos, type(None)))

                # get break time period
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertTrue(not isinstance(p_lst[0].startpos, type(None)))
                self.assertEqual(p_lst[0].state, 'e')

    @with_transaction()
    def test_period_wizard_start_24(self):
        """ test: create tariff+employee, start break time, 1x [...|end] in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create break time item
                dt1 = datetime.now() - timedelta(seconds=30*60)
                br1 = BreakPeriod(employee = BreakPeriod.default_employee(),
                    startpos = None,
                    endpos = dt1,
                    state = BreakPeriod.default_state(),
                )
                br1.save()
                br_lst = BreakPeriod.search([])
                self.assertEqual(len(br_lst), 1)
                self.assertEqual(br_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(br_lst[0].state, 'c')

                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)

                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.breakstart, None)
                self.assertEqual(w_obj.start.breakperiod, '')
                self.assertEqual(w_obj.start.breakstate, 'i')

                # end break time
                dt1 = datetime.now()
                r1 = w_obj.transition_beginbreak()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')

                # check result
                br_lst = BreakPeriod.search([])
                self.assertEqual(len(br_lst), 2)
                br_lst = BreakPeriod.search([('id', '=', br1.id)])
                self.assertEqual(len(br_lst), 1)
                self.assertEqual(br_lst[0].state, 'c')
                self.assertEqual(br_lst[0].startpos, None)
                self.assertTrue(not isinstance(br_lst[0].endpos, type(None)))
                
                # get break time period
                p_lst = BreakPeriod.search([('id', '!=', br1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_25(self):
        """ test: create tariff+employee, end break time, 1x [...|end] in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create break time item
                br1 = BreakPeriod(employee = BreakPeriod.default_employee(),
                    startpos = None,
                    endpos = datetime.now() - timedelta(seconds=30*60),
                    state = BreakPeriod.default_state(),
                )
                br1.save()
                br_lst = BreakPeriod.search([])
                self.assertEqual(len(br_lst), 1)
                self.assertEqual(br_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(br_lst[0].state, 'c')

                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)

                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.breakstart, None)
                self.assertEqual(w_obj.start.breakperiod, '')
                self.assertEqual(w_obj.start.breakstate, 'i')

                # end break time
                dt1 = datetime.now()
                r1 = w_obj.transition_endbreak()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')

                # check result
                p_lst = BreakPeriod.search([])
                self.assertEqual(len(p_lst), 2)
                p_lst = BreakPeriod.search([('id', '!=', br1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].state, 'c')
                self.assertEqual(p_lst[0].startpos, None)
                self.assertTrue(not isinstance(p_lst[0].endpos, type(None)))

                # get break time period
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertEqual(p_lst[0].startpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_26(self):
        """ test: create tariff+employee, start break time, [start|end] in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create break time item
                dt1 = datetime.now() - timedelta(seconds=120*60)
                br1 = BreakPeriod(employee = BreakPeriod.default_employee(),
                    startpos = dt1,
                    endpos = dt1 + timedelta(seconds=30*60),
                    state = BreakPeriod.default_state(),
                )
                br1.save()
                BreakPeriod.wfexamine([br1])
                br_lst = BreakPeriod.search([])
                self.assertEqual(len(br_lst), 1)
                self.assertEqual(br_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(br_lst[0].state, 'e')

                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.breakstart, None)
                self.assertEqual(w_obj.start.breakperiod, '')
                self.assertEqual(w_obj.start.breakstate, 'i')

                # start break time
                dt1 = datetime.now()
                r1 = w_obj.transition_beginbreak()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')
                
                # get break time period
                p_lst = BreakPeriod.search([])
                self.assertEqual(len(p_lst), 2)
                p_lst = BreakPeriod.search([('id', '!=', br1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].startpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertEqual(p_lst[0].endpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_27(self):
        """ test: create tariff+employee, end break time, [start|end] in db
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create break time item
                dt1 = datetime.now() - timedelta(seconds=120*60)
                br1 = BreakPeriod(employee = BreakPeriod.default_employee(),
                    startpos = dt1,
                    endpos = dt1 + timedelta(seconds=30*60),
                    state = BreakPeriod.default_state(),
                )
                br1.save()
                BreakPeriod.wfexamine([br1])
                br_lst = BreakPeriod.search([])
                self.assertEqual(len(br_lst), 1)
                self.assertEqual(br_lst[0].employee.rec_name, 'Frida')
                self.assertEqual(br_lst[0].state, 'e')

                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.breakstart, None)
                self.assertEqual(w_obj.start.breakperiod, '')
                self.assertEqual(w_obj.start.breakstate, 'i')

                # end break time
                dt1 = datetime.now()
                r1 = w_obj.transition_endbreak()
                dt2 = datetime.now()
                self.assertEqual(r1, 'end')
                
                # get break time period
                p_lst = BreakPeriod.search([])
                self.assertEqual(len(p_lst), 2)
                p_lst = BreakPeriod.search([('id', '!=', br1.id)])
                self.assertEqual(len(p_lst), 1)
                self.assertEqual(p_lst[0].employee.rec_name, 'Frida')
                self.assertTrue(
                    datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second) <= \
                    p_lst[0].endpos <= \
                    datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt2.minute, dt2.second))
                self.assertEqual(p_lst[0].startpos, None)
                self.assertEqual(p_lst[0].state, 'c')

    @with_transaction()
    def test_period_wizard_start_28(self):
        """ test: create tariff+employee, 2x [start|end] + 1x [...|end] in db (6h ago), end work
        """
        pool = Pool()
        PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
        Period = pool.get('employee_timetracking.period')
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frida')
            employee1.tariff = tarobj1
            employee1.save()
            self.assertTrue(employee1)

            with transaction.set_context({'employee': employee1.id, 'company': tarobj1.company.id}):
                # create period
                dt2 = datetime.now() - timedelta(seconds=5 * 60 * 60)
                p1 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt2,
                        endpos = dt2 + timedelta(seconds=25*60),
                    )
                p1.save()
                self.assertEqual(p1.presence.rec_name, 'Work')
                self.assertEqual(p1.employee.rec_name, 'Frida')
                Period.wfexamine([p1])

                dt3 = datetime.now() - timedelta(seconds=4 * 60 * 60)
                p2 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = dt3,
                        endpos = dt3 + timedelta(seconds=25*60),
                    )
                p2.save()
                self.assertEqual(p2.presence.rec_name, 'Work')
                self.assertEqual(p2.employee.rec_name, 'Frida')

                dt4 = datetime.now() - timedelta(seconds=3 * 60 * 60)
                p3 = Period(employee = employee1,
                        presence = tarobj1.type_present,
                        startpos = None,
                        endpos = dt4 + timedelta(seconds=25*60),
                    )
                p3.save()
                self.assertEqual(p3.presence.rec_name, 'Work')
                self.assertEqual(p3.employee.rec_name, 'Frida')
                
                # start wizard
                (sess_id, start_state, end_state) = PerAttndWizard.create()
                w_obj = PerAttndWizard(sess_id)
                
                # run start-dialog
                result = PerAttndWizard.execute(sess_id, {}, start_state)
                for i in result['view']['defaults']:
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                w_obj.start.on_change_employee()

                # check
                # the wizard should find the newest item 'p3' - a end-item
                # result is 'inactive'
                self.assertEqual(w_obj.start.company.rec_name, 'm-ds 1')
                self.assertEqual(w_obj.start.currstart, None)
                self.assertEqual(w_obj.start.currperiod, '')
                self.assertEqual(w_obj.start.currtype, '')
                self.assertEqual(w_obj.start.currstate, 'i')
                self.assertEqual(w_obj.start.presence.rec_name, 'Work')

                # going
                dt1 = datetime.now()
                r1 = w_obj.transition_ending()
                dt1a = datetime.now()
                self.assertEqual(r1, 'end')

                # we have 4 items
                p_lst = Period.search([])
                self.assertEqual(len(p_lst), 4)

                # we have 2 end-item - created-state, no startpos
                p_lst = Period.search([
                        ('state', '=', WF_PERIOD_CREATED), 
                        ('startpos', '=', None)
                    ])
                self.assertEqual(len(p_lst), 2)

                # we have 1 item - examine-state
                p_lst = Period.search([
                        ('state', '=', WF_PERIOD_EXAMINE)
                    ])
                self.assertEqual(len(p_lst), 1)

                # we have 1 item - created-state, startpos+endpos
                p_lst = Period.search([
                        ('state', '=', WF_PERIOD_CREATED),
                        ('startpos', '!=', None),
                        ('endpos', '!=', None),
                    ])
                self.assertEqual(len(p_lst), 1)

# end PeriodWizardTestCase
