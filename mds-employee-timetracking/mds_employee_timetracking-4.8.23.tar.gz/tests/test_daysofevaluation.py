# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from datetime import date, time, datetime, timedelta
from decimal import Decimal
from trytond.modules.company.tests import set_company
from trytond.modules.employee_timetracking.tests.testlib import create_tariff_full,\
    create_worktime_full, create_employee, create_period, create_holiday
from trytond.modules.employee_timetracking.const import ACRULE_HOLIDAY_NODEF


class DaysOfEvaluationTestCase(ModuleTestCase):
    'Test days-of-evaluation module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_daysofevaluation_breaktimes(self):
        """ create tariff/evaluation/break time item, check reduced work time
        """
        pool = Pool()
        Period = pool.get('employee_timetracking.period')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4-5:59', 'shortname':'BT1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6-7:59', 'shortname':'BT2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=45*60)},
                    ],
                timeaccounts=[
                        {'name': 'Work norm', 'shortname': 'W1'},
                    ],
                accountrules=[
                        {'name':'8-16', 'shortname':'W1', 
                         'mint':time(8, 0), 'maxt':time(16, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':False, 'sun':False, 'account': 'Work norm', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
                main_account='Work norm',
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
            ])
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.save()

            p1 = create_period(
                    datetime(2019, 2, 7, 6, 30, 0), 
                    datetime(2019, 2, 7, 11, 00, 22), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '07:30 - 12:00, 2019-02-07 [1]')  # CET
            p2 = create_period(
                    datetime(2019, 2, 7, 11, 15, 0), 
                    datetime(2019, 2, 7, 13, 0, 0), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p2.name, '12:15 - 14:00, 2019-02-07 [1]')  # CET
            # sum: 5:45:22 --> minimum break time: 30 min

            # create time-account-items, evaluation is created automatically
            Period.wfexamine([p1, p2])

            # get new created evaluation
            eva_lst = Evaluation.search([()])   # get all evaluations, should be 1x
            self.assertEqual(len(eva_lst), 1)
            self.assertEqual(eva_lst[0].rec_name, 'Frida - 2019-02')
            
            self.assertEqual(len(eva_lst[0].days), 29)  # 28 day in febr. + 1x due 2x work times at 7.2.

            # check day 7 - part 1
            self.assertEqual(str(eva_lst[0].days[6].date), '2019-02-07')
            self.assertEqual(eva_lst[0].days[6].period.rec_name, '07:30 - 12:00, 2019-02-07 [1]')
            self.assertEqual(eva_lst[0].days[6].accountitem.rec_name, '08:00 - 12:00, 2019-02-07 [W1]')
            self.assertEqual(eva_lst[0].days[6].weekday_string, 'Thu')
            self.assertEqual(eva_lst[0].days[6].week, 6)
            self.assertEqual(str(eva_lst[0].days[6].startpos), '2019-02-07 07:00:00')
            self.assertEqual(str(eva_lst[0].days[6].duration), '4:00:22')
            # break times - before we enter break times
            self.assertEqual(str(eva_lst[0].days[6].sumbreaks), '0:00:00')
            self.assertEqual(str(eva_lst[0].days[6].breaktime), '0:30:00')
            self.assertEqual(str(eva_lst[0].days[6].wobreaks), '5:15:22')

            # check day 7 - part 2
            self.assertEqual(str(eva_lst[0].days[7].date), '2019-02-07')
            self.assertEqual(eva_lst[0].days[7].period.rec_name, '12:15 - 14:00, 2019-02-07 [1]')
            self.assertEqual(eva_lst[0].days[7].accountitem.rec_name, '12:15 - 14:00, 2019-02-07 [W1]')
            self.assertEqual(eva_lst[0].days[7].weekday_string, 'Thu')
            self.assertEqual(eva_lst[0].days[7].week, 6)
            self.assertEqual(str(eva_lst[0].days[7].startpos), '2019-02-07 11:15:00')
            self.assertEqual(str(eva_lst[0].days[7].duration), '1:45:00')
            # break times - before we enter break times
            self.assertEqual(str(eva_lst[0].days[7].sumbreaks), '0:00:00')
            self.assertEqual(str(eva_lst[0].days[7].breaktime), '0:30:00')
            self.assertEqual(str(eva_lst[0].days[7].wobreaks), '5:15:22')
            
            # add break time period
            br1 = BreakPeriod(employee = employee1,
                startpos = datetime(2019, 2, 7, 8, 0, 0),
                endpos = datetime(2019, 2, 7, 8, 20, 0),
                state = BreakPeriod.default_state()
                )
            br1.save()
            BreakPeriod.wfexamine([br1])
            self.assertEqual(br1.name, '09:00 - 09:20, 2019-02-07')
            self.assertEqual(br1.state, 'e')
            self.assertEqual(str(eva_lst[0].days[6].sumbreaks), '0:20:00')
            self.assertEqual(str(eva_lst[0].days[6].breaktime), '0:30:00')
            self.assertEqual(str(eva_lst[0].days[6].wobreaks), '5:15:22')
            self.assertEqual(str(eva_lst[0].days[7].sumbreaks), '0:20:00')
            self.assertEqual(str(eva_lst[0].days[7].breaktime), '0:30:00')
            self.assertEqual(str(eva_lst[0].days[7].wobreaks), '5:15:22')

            # add another break time period
            br2 = BreakPeriod(employee = employee1,
                startpos = datetime(2019, 2, 7, 10, 50, 0),
                endpos = datetime(2019, 2, 7, 11, 20, 0),
                state = BreakPeriod.default_state()
                )
            br2.save()
            BreakPeriod.wfexamine([br2])
            # break time overlaps two worktime ends/starts
            # break time duration: 30 min, but 15 min are outside of worktime
            # 15 min only counts
            self.assertEqual(br2.name, '11:50 - 12:20, 2019-02-07')
            self.assertEqual(br2.state, 'e')
            self.assertEqual(str(eva_lst[0].days[6].sumbreaks), '0:35:22')
            self.assertEqual(str(eva_lst[0].days[6].breaktime), '0:35:22')
            self.assertEqual(str(eva_lst[0].days[6].wobreaks), '5:10:00')
            self.assertEqual(str(eva_lst[0].days[7].sumbreaks), '0:35:22')
            self.assertEqual(str(eva_lst[0].days[7].breaktime), '0:35:22')
            self.assertEqual(str(eva_lst[0].days[7].wobreaks), '5:10:00')
            
            # searcher
            DayOfYear = pool.get('employee_timetracking.evaluation-dayofyear')
            doy1 = DayOfYear.search([
                ('startpos', '>=', datetime(2019, 2, 7, 6, 20, 0)),
                ('endpos', '<=', datetime(2019, 2, 7, 11, 10, 0)),
                ])
            self.assertEqual(len(doy1), 1)
            self.assertEqual(str(doy1[0].period.startpos), '2019-02-07 06:30:00')

    @with_transaction()
    def test_daysofevaluation_add_delete_timeaccountitems(self):
        """ create evaluation, add/delete time-account-items
        """
        pool = Pool()
        Period = pool.get('employee_timetracking.period')
        Evaluation = pool.get('employee_timetracking.evaluation')
        DaysOfEvaluation = pool.get('employee_timetracking.evaluation-dayofyear')
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name': 'Work norm', 'shortname': 'W1'},
                        {'name': 'Work late', 'shortname': 'W2'},
                    ],
                accountrules=[
                        {'name':'8-16', 'shortname':'W1', 
                         'mint':time(8, 0), 'maxt':time(16, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':False, 'sun':False, 'account': 'Work norm', 'presence':'Work'},
                        {'name':'16-19', 'shortname':'W2', 
                         'mint':time(16, 0), 'maxt':time(19, 0), 
                         'fact':Decimal('1.5'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':False, 'sun':False, 'account': 'Work late', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
                main_account='Work norm',
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
            ])
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.save()

            p1 = create_period(
                    datetime(2018, 5, 16, 6, 30, 0), 
                    datetime(2018, 5, 16, 19, 35, 23), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '08:30 - 21:35, 2018-05-16 [1]')  # CEST

            # create time-account-items, evaluation is created automatically
            Period.wfexamine([p1])

            # get new created evaluation
            eva_lst = Evaluation.search([()])   # get all evaluations, should be 1x
            self.assertEqual(len(eva_lst), 1)
            self.assertEqual(eva_lst[0].rec_name, 'Frida - 2018-05')
            
            # evaluation has copy of work time model
            self.assertEqual(len(eva_lst[0].worktimerule), 1)
            self.assertEqual(eva_lst[0].worktimerule[0].rec_name, '08:00-16:00 [xxxxx__]')

            # period created the time-account-item
            self.assertEqual(len(p1.accountitem), 2)
            l1 = sorted(p1.accountitem, key=lambda ac1: ac1.startpos)
            self.assertEqual(l1[0].name, '08:30 - 16:00, 2018-05-16 [W1]')
            self.assertEqual(l1[1].name, '16:00 - 19:00, 2018-05-16 [W2]')

            # time-account-item is connected with its day in evaluation
            daylst = DaysOfEvaluation.search([('evaluation', '=', eva_lst[0]), ('date', '=', date(2018, 5, 16))])
            self.assertEqual(len(daylst), 1)
            self.assertEqual(str(daylst[0].date), '2018-05-16')
            self.assertEqual(daylst[0].accountitem.name, '08:30 - 16:00, 2018-05-16 [W1]')
            self.assertEqual(daylst[0].accountitem.id, l1[0].id)

            # delete period, this will delete by cascade: time-account-item
            # and disconnect from day-of-evaluation
            Period.delete([p1])
            self.assertEqual(len(TimeAccountItem.search([])), 0)
            self.assertEqual(len(Period.search([])), 0)
            self.assertEqual(str(daylst[0].accountitem), 'None')
            
            p1 = create_period(
                    datetime(2018, 5, 16, 6, 30, 0), 
                    datetime(2018, 5, 16, 12, 35, 23), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '08:30 - 14:35, 2018-05-16 [1]')  # CEST
            p2 = create_period(
                    datetime(2018, 5, 16, 13, 0, 0), 
                    datetime(2018, 5, 16, 15, 15, 0), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p2.name, '15:00 - 17:15, 2018-05-16 [1]')  # CEST

            # create time-account-items - evaluation exists
            Period.wfexamine([p1, p2])

            # period created the time-account-item...
            # 1st period
            self.assertEqual(len(p1.accountitem), 1)
            self.assertEqual(p1.accountitem[0].name, '08:30 - 14:35, 2018-05-16 [W1]')
            # 2ns period
            self.assertEqual(len(p2.accountitem), 2)
            l1 = sorted(p2.accountitem, key=lambda ac1: ac1.startpos)
            self.assertEqual(l1[0].name, '15:00 - 16:00, 2018-05-16 [W1]')
            self.assertEqual(l1[1].name, '16:00 - 17:15, 2018-05-16 [W2]')
            
    @with_transaction()
    def test_daysofevaluation_get_dates_of_month_sql(self):
        """ test sql-code for dates-of-month
        """
        pool = Pool()
        DayOfEval = pool.get('employee_timetracking.evaluation-dayofyear')
        Evaluation = pool.get('employee_timetracking.evaluation')
        tab_date = DayOfEval.get_dates_of_month_sql()
        cursor = Transaction().connection.cursor()
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
            ])
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        # holidays
        create_holiday('half day, every year', date(2018, 4, 4), company=tarobj1.company, repyear=True, halfday=True)
        create_holiday('full day, every year', date(2018, 4, 5), company=tarobj1.company, repyear=True, halfday=False)
        create_holiday('half day, this year',  date(2018, 4, 6), company=tarobj1.company, repyear=False, halfday=True)

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.save()

            evobj = Evaluation()
            evobj.employee = employee1
            evobj.evaldate = date(2018, 4, 10)
            evobj.save()
            self.assertEqual(evobj.rec_name, 'Frida - 2018-04')

        qu1 = tab_date.select(tab_date.evaluation,
                tab_date.date,
                tab_date.weekday,
                tab_date.week, 
                tab_date.holiday_ena,
                tab_date.holidayname,
                tab_date.daytype,
                where=(tab_date.evaluation == evobj.id) & 
                    (tab_date.date >= date(2018, 4, 1)) & (tab_date.date <= date(2018, 4, 10)),
                order_by=[tab_date.date]
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        
        l2 = [
                [evobj.id, '2018-04-01', '0', 13, False, 'None', 'we'],
                [evobj.id, '2018-04-02', '1', 14, False, 'None', 'wd'],
                [evobj.id, '2018-04-03', '2', 14, False, 'None', 'wd'],
                [evobj.id, '2018-04-04', '3', 14, True, 'half day, every year', 'hd'],
                [evobj.id, '2018-04-05', '4', 14, True, 'full day, every year', 'hd'],
                [evobj.id, '2018-04-06', '5', 14, True, 'half day, this year', 'hd'],
                [evobj.id, '2018-04-07', '6', 14, False, 'None', 'we'],
                [evobj.id, '2018-04-08', '0', 14, False, 'None', 'we'],
                [evobj.id, '2018-04-09', '1', 15, False, 'None', 'wd'],
                [evobj.id, '2018-04-10', '2', 15, False, 'None', 'wd'],
            ]
        p1 = 0
        for i in l1:
            (eval1, date1, weekday1, week1, hdena, hdname, daytype) = i
            self.assertEqual(eval1, l2[p1][0])
            self.assertEqual(str(date1), l2[p1][1])
            self.assertEqual(weekday1, l2[p1][2])
            self.assertEqual(week1, l2[p1][3])
            self.assertEqual(hdena, l2[p1][4])
            self.assertEqual(str(hdname), l2[p1][5])
            self.assertEqual(daytype, l2[p1][6])
            p1 += 1

    @with_transaction()
    def test_daysofevaluation_vacation_day(self):
        """ test: create tariff, work time model, employee, add vacation day, check output
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        DaysOfEvaluation = pool.get('employee_timetracking.evaluation-dayofyear')
        VacationDay = pool.get('employee_timetracking.evaluation_vacationdays')
        Period = pool.get('employee_timetracking.period')
        cursor = Transaction().connection.cursor()
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name': '4h - 6h', 'shortname': '6h', 
                        'mint': timedelta(seconds=4*3600),
                        'maxt': timedelta(seconds=5*3600 + 59*60 + 59),
                        'dedu': timedelta(seconds=20*60),
                        },
                        {'name': '6h - 8h', 'shortname': '8h', 
                        'mint': timedelta(seconds=6*3600),
                        'maxt': timedelta(seconds=7*3600 + 59*60 + 59),
                        'dedu': timedelta(seconds=30*60),
                        },
                        {'name': '8h - 10h', 'shortname': '10h', 
                        'mint': timedelta(seconds=8*3600),
                        'maxt': timedelta(seconds=9*3600 + 59*60 + 59),
                        'dedu': timedelta(seconds=45*60),
                        },
                    ],
                timeaccounts=[
                        {'name': 'Work norm', 'shortname': 'W1'},
                    ],
                accountrules=[
                        {'name':'7:30-16', 'shortname':'W1', 
                         'mint':time(7, 30), 'maxt':time(16, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':False, 'sun':False, 'account': 'Work norm', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
                main_account='Work norm',
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
            ])
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.holidays = 15
            employee1.save()
            
            # work time interrupts full vacation days
            p1 = create_period(
                    datetime(2019, 4, 8, 6, 0, 0), 
                    datetime(2019, 4, 8, 13, 15, 0), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '08:00 - 15:15, 2019-04-08 [1]')
            Period.wfexamine([p1])
            # word time adds to half vacation day
            p2 = create_period(
                    datetime(2019, 4, 15, 6, 0, 0), 
                    datetime(2019, 4, 15, 9, 30, 0), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p2.name, '08:00 - 11:30, 2019-04-15 [1]')
            Period.wfexamine([p2])
            
            emp_lst = Evaluation.search([()])   # get all evaluations, should be 1x
            self.assertEqual(len(emp_lst), 1)
            self.assertEqual(emp_lst[0].rec_name, 'Frida - 2019-04')
            # still no vacation days in this month
            self.assertEqual(str(emp_lst[0].vacationdays_taken), '0.0')
            self.assertEqual(str(emp_lst[0].vacationdays_remain), '15.0')
            
            # add vacation days in range of 4/2019
            vd1 = VacationDay(evaluation=emp_lst[0],
                    date_start = date(2019, 4, 7),
                    date_end = date(2019, 4, 11),
                )
            vd1.save()
            vd2 = VacationDay(evaluation=emp_lst[0],
                    date_start = date(2019, 4, 12),
                    date_end = date(2019, 4, 16),
                    halfday = True
                )
            vd2.save()
            vd_lst = VacationDay.search([], order=[('date_start', 'ASC')])
            self.assertEqual(len(vd_lst), 2)
            self.assertEqual(vd_lst[0].rec_name, '2019-04-07 - 2019-04-11')
            self.assertEqual(vd_lst[0].halfday, False)
            self.assertEqual(vd_lst[1].rec_name, '2019-04-12 - 2019-04-16')
            self.assertEqual(vd_lst[1].halfday, True)

            tab_data = DaysOfEvaluation.get_data_sql()
            qu1 = tab_data.select(tab_data.date,
                    tab_data.daytype,
                    tab_data.vacationday,
                    tab_data.sumact,
                    tab_data.sumbreaks,
                    where=tab_data.evaluation == emp_lst[0].id,
                    order_by = tab_data.date)
            cursor.execute(*qu1)
            l1 = cursor.fetchall()
            self.assertEqual(len(l1), 30)

            cnt1 = 0
            #                                            (no breaktimes)
            l2 = [#  date          daytyp  vacation day  worktime   breaktime
                    ('2019-04-06', 'we',   '0',          'None',    '0:00:00'), # weekend
                    ('2019-04-07', 'we',   '0',          'None',    '0:00:00'), # planned full vacation day, but no working time from worktime model
                    ('2019-04-08', 'wd',   '0',          '7:15:00', '0:00:00'), # planned vacation day, but employee added worktime
                    ('2019-04-09', 'wd',   '1',          '8:00:00', '0:00:00'), # full vacation day
                    ('2019-04-10', 'wd',   '1',          '8:00:00', '0:00:00'), # full vacation day
                    ('2019-04-11', 'wd',   '1',          '8:00:00', '0:00:00'), # full vacation day
                    ('2019-04-12', 'wd',   '2',          '4:00:00', '0:00:00'), # half vacation day
                    ('2019-04-13', 'we',   '0',          'None',    '0:00:00'), # planned half vacation day, but weekend
                    ('2019-04-14', 'we',   '0',          'None',    '0:00:00'), # planned half vacation day, but weekend
                    ('2019-04-15', 'wd',   '2',          '7:30:00', '0:00:00'), # half vacation day + 3,5h worktime
                    ('2019-04-16', 'wd',   '2',          '4:00:00', '0:00:00'), # half vacation day
                    ('2019-04-17', 'wd',   '0',          'None',    '0:00:00'),
                ]

            for i in l1[5:17]:
                (date1, daytype, vacationday, sumact, sumbreaks) = i

                self.assertEqual(str(date1), l2[cnt1][0])
                self.assertEqual(daytype, l2[cnt1][1])
                self.assertEqual(vacationday, l2[cnt1][2])
                self.assertEqual(str(sumact), l2[cnt1][3])
                self.assertEqual(str(sumbreaks), l2[cnt1][4])
                cnt1 += 1

            # check output of object
            doe_lst = DaysOfEvaluation.search([
                    ('evaluation.id', '=', emp_lst[0].id),
                    ('date', '>=', date(2019, 4, 6)),
                    ('date', '<=', date(2019, 4, 17)),
                ], order=[('date', 'ASC')])

            cnt1 = 0
            #                                            (no breaktimes)
            l2 = [#  date          daytyp  vacation day  worktime   breaktime  wobreaks   breaktime
                    ('2019-04-06', 'we',   '0',          'None',    '0:00:00', 'None',    'None'),    # weekend
                    ('2019-04-07', 'we',   '0',          'None',    '0:00:00', 'None',    'None'),    # planned full vacation day, but no working time from worktime model
                    ('2019-04-08', 'wd',   '0',          '7:15:00', '0:00:00', '6:45:00', '0:30:00'), # planned vacation day, but employee added worktime
                    ('2019-04-09', 'wd',   '1',          '8:00:00', '0:00:00', '8:00:00', '0:00:00'), # full vacation day
                    ('2019-04-10', 'wd',   '1',          '8:00:00', '0:00:00', '8:00:00', '0:00:00'), # full vacation day
                    ('2019-04-11', 'wd',   '1',          '8:00:00', '0:00:00', '8:00:00', '0:00:00'), # full vacation day
                    ('2019-04-12', 'wd',   '2',          '4:00:00', '0:00:00', '4:00:00', '0:00:00'), # half vacation day
                    ('2019-04-13', 'we',   '0',          'None',    '0:00:00', 'None',    'None'),    # planned half vacation day, but weekend
                    ('2019-04-14', 'we',   '0',          'None',    '0:00:00', 'None',    'None'),    # planned half vacation day, but weekend
                    ('2019-04-15', 'wd',   '2',          '7:30:00', '0:00:00', '7:30:00', '0:00:00'), # half vacation day + 3,5h worktime
                    ('2019-04-16', 'wd',   '2',          '4:00:00', '0:00:00', '4:00:00', '0:00:00'), # half vacation day
                    ('2019-04-17', 'wd',   '0',          'None',    '0:00:00', 'None',    'None'),
                ]

            for i in doe_lst:
                self.assertEqual(str(i.date), l2[cnt1][0])
                self.assertEqual(i.daytype, l2[cnt1][1])
                self.assertEqual(i.vacationday, l2[cnt1][2])
                self.assertEqual(str(i.sumact), l2[cnt1][3])
                self.assertEqual(str(i.sumbreaks), l2[cnt1][4])
                self.assertEqual(str(i.wobreaks), l2[cnt1][5])
                self.assertEqual(str(i.breaktime), l2[cnt1][6])
                cnt1 += 1

            # vacation days in this month by evaluation
            self.assertEqual(str(emp_lst[0].vacationdays_taken), '4.5') # 3x full + 3x half
            self.assertEqual(str(emp_lst[0].vacationdays_remain), '10.5')
            
            # searcher
            doe_lst2 = DaysOfEvaluation.search([('vacationday', '=', '1')], order=[('date', 'ASC')])
            self.assertEqual(len(doe_lst2), 3)
            self.assertEqual(str(doe_lst2[0].date), '2019-04-09')
            self.assertEqual(str(doe_lst2[1].date), '2019-04-10')
            self.assertEqual(str(doe_lst2[2].date), '2019-04-11')

    @with_transaction()
    def test_daysofevaluation_get_eval_sumbreaks_sql(self):
        """ test sql-code for sum of break times
        """
        pool = Pool()
        Period = pool.get('employee_timetracking.period')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        Evaluation = pool.get('employee_timetracking.evaluation')
        DaysOfEvaluation = pool.get('employee_timetracking.evaluation-dayofyear')
        cursor = Transaction().connection.cursor()
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name': 'Work norm', 'shortname': 'W1'},
                    ],
                accountrules=[
                        {'name':'7:30-16', 'shortname':'W1', 
                         'mint':time(7, 30), 'maxt':time(16, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':False, 'sun':False, 'account': 'Work norm', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                    ],
                type_work = 'Work',
                main_account='Work norm',
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
            ])
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.save()

            p1 = create_period(
                    datetime(2019, 2, 7, 6, 30, 0), 
                    datetime(2019, 2, 7, 11, 00, 22), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '07:30 - 12:00, 2019-02-07 [1]')  # CET

            # create time-account-items, evaluation is created automatically
            Period.wfexamine([p1])

            # break time starts before work time
            br1 = BreakPeriod(employee = employee1,
                startpos = datetime(2019, 2, 7, 6, 0, 0),
                endpos = datetime(2019, 2, 7, 7, 0, 0),
                state = BreakPeriod.default_state()
                )
            br1.save()
            BreakPeriod.wfexamine([br1])
            self.assertEqual(br1.name, '07:00 - 08:00, 2019-02-07')
            # 30 min
            
            # break time within work time
            br2 = BreakPeriod(employee = employee1,
                startpos = datetime(2019, 2, 7, 8, 0, 0),
                endpos = datetime(2019, 2, 7, 8, 30, 0),
                state = BreakPeriod.default_state()
                )
            br2.save()
            BreakPeriod.wfexamine([br2])
            self.assertEqual(br2.name, '09:00 - 09:30, 2019-02-07')
            # 30 min

            # break time ends after work time
            br3 = BreakPeriod(employee = employee1,
                startpos = datetime(2019, 2, 7, 10, 45, 0),
                endpos = datetime(2019, 2, 7, 11, 10, 0),
                state = BreakPeriod.default_state()
                )
            br3.save()
            BreakPeriod.wfexamine([br3])
            self.assertEqual(br3.name, '11:45 - 12:10, 2019-02-07')
            # 15 min, 22 sek
            
            ev_lst = Evaluation.search([])
            self.assertEqual(len(ev_lst), 1)
            
            # check sql
            tab_doe = DaysOfEvaluation.get_eval_sumbreaks_sql()
            
            qu1 = tab_doe.select(tab_doe.evaluation,
                    tab_doe.date,
                    tab_doe.sumbreaks,
                    where=(tab_doe.evaluation == ev_lst[0].id)
                )
            cursor.execute(*qu1)
            l1 = cursor.fetchall()
            self.assertEqual(len(l1), 1)
            self.assertEqual(l1[0][0], ev_lst[0].id)
            self.assertEqual(str(l1[0][1]), '2019-02-07')
            self.assertEqual(str(l1[0][2]), '1:15:22')
        
    @with_transaction()
    def test_daysofevaluation_get_working_days_sql(self):
        """ test sql-code for working-days
        """
        pool = Pool()
        DayOfEval = pool.get('employee_timetracking.evaluation-dayofyear')
        Evaluation = pool.get('employee_timetracking.evaluation')
        tab_workday = DayOfEval.get_working_days_sql()
        cursor = Transaction().connection.cursor()
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
                {'name':'WTR2', 'mon':False, 'tue':False, 'wed':False, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(6,0), 'maxtime':time(7, 30)},
            ])
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()
        
        # holidays
        create_holiday('half day, every year', date(2018, 4, 4), company=tarobj1.company, repyear=True, halfday=True)
        create_holiday('full day, every year', date(2018, 4, 5), company=tarobj1.company, repyear=True, halfday=False)
        create_holiday('half day, this year',  date(2018, 4, 6), company=tarobj1.company, repyear=False, halfday=True)

        with set_company(tarobj1.company):            
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.save()
        
            ev1 = Evaluation()
            ev1.employee = employee1
            ev1.evaldate = date(2018, 4, 18)
            ev1.save()
            self.assertEqual(ev1.rec_name, 'Frida - 2018-04')
            self.assertEqual(ev1.state, 'c')
            Evaluation.wfactivate([ev1])
            self.assertEqual(ev1.state, 'a')
            self.assertEqual(len(ev1.worktimerule), 2)

        qu1 = tab_workday.select(tab_workday.evaluation,
                tab_workday.date,
                tab_workday.weekday,
                tab_workday.week,
                tab_workday.holiday_ena, 
                tab_workday.holidayname,
                tab_workday.daytype,
                tab_workday.targettime,
                where=(tab_workday.evaluation == ev1.id),
                order_by=[tab_workday.date]
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        
        l2 = [
                [ev1.id, '2018-04-01', '0', 13, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-02', '1', 14, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-03', '2', 14, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-04', '3', 14, True, 'half day, every year', 'hd', '4:00:00'],
                [ev1.id, '2018-04-05', '4', 14, True, 'full day, every year', 'hd', '0:00:00'],
                [ev1.id, '2018-04-06', '5', 14, True, 'half day, this year', 'hd', '4:45:00'],
                [ev1.id, '2018-04-07', '6', 14, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-08', '0', 14, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-09', '1', 15, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-10', '2', 15, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-11', '3', 15, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-12', '4', 15, False, 'None', 'wd', '9:30:00'],
                [ev1.id, '2018-04-13', '5', 15, False, 'None', 'wd', '9:30:00'],
                [ev1.id, '2018-04-14', '6', 15, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-15', '0', 15, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-16', '1', 16, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-17', '2', 16, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-18', '3', 16, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-19', '4', 16, False, 'None', 'wd', '9:30:00'],
                [ev1.id, '2018-04-20', '5', 16, False, 'None', 'wd', '9:30:00'],
                [ev1.id, '2018-04-21', '6', 16, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-22', '0', 16, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-23', '1', 17, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-24', '2', 17, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-25', '3', 17, False, 'None', 'wd', '8:00:00'],
                [ev1.id, '2018-04-26', '4', 17, False, 'None', 'wd', '9:30:00'],
                [ev1.id, '2018-04-27', '5', 17, False, 'None', 'wd', '9:30:00'],
                [ev1.id, '2018-04-28', '6', 17, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-29', '0', 17, False, 'None', 'we', '0:00:00'],
                [ev1.id, '2018-04-30', '1', 18, False, 'None', 'wd', '8:00:00'],
            ]
        p1 = 0
        for i in l1:
            (ev1, date1, weekday1, week1, hdena, hdname, daytype, targ1) = i
            self.assertEqual(ev1, l2[p1][0])
            self.assertEqual(str(date1), l2[p1][1])
            self.assertEqual(weekday1, l2[p1][2])
            self.assertEqual(week1, l2[p1][3])
            self.assertEqual(hdena, l2[p1][4])
            self.assertEqual(str(hdname), l2[p1][5])
            self.assertEqual(daytype, l2[p1][6])
            self.assertEqual(str(targ1), l2[p1][7])
            p1 += 1

    @with_transaction()
    def test_daysofevaluation_reduced_workingtime(self):
        """ test reduce of working time due breaks
        """
        pool = Pool()
        EvalBtRule = pool.get('employee_timetracking.evaluation_btrule')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4-5:59', 'shortname':'BT1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6-7:59', 'shortname':'BT2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=45*60)},
                        {'name':'8-9:59', 'shortname':'BT3', 
                         'mint':timedelta(seconds=8*60*60), 
                         'maxt':timedelta(seconds=9*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=60*60)},                        
                    ],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            evobj = Evaluation()
            evobj.employee = employee1
            evobj.evaldate = date(2018, 4, 10)
            evobj.save()
            self.assertEqual(evobj.rec_name, 'Frida - 2018-04')
            
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, None, None)
            self.assertEqual(str(wtime), 'None')
            self.assertEqual(str(btime), 'None')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(None, timedelta(seconds=0), timedelta(seconds=0))
            self.assertEqual(str(wtime), 'None')
            self.assertEqual(str(btime), 'None')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=3*60*60 + 30*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '3:30:00')
            self.assertEqual(str(btime), '0:00:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=4*60*60 + 20*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '4:00:00')
            self.assertEqual(str(btime), '0:20:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=4*60*60 + 50*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '4:20:00')
            self.assertEqual(str(btime), '0:30:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=5*60*60 + 50*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '5:20:00')
            self.assertEqual(str(btime), '0:30:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=6*60*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '5:30:00')
            self.assertEqual(str(btime), '0:30:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=6*60*60 + 10*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '5:30:00')
            self.assertEqual(str(btime), '0:40:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=6*60*60 + 15*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '5:30:00')
            self.assertEqual(str(btime), '0:45:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=6*60*60 + 20*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '5:35:00')
            self.assertEqual(str(btime), '0:45:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=6*60*60 + 30*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '5:45:00')
            self.assertEqual(str(btime), '0:45:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=6*60*60 + 58*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '6:13:00')
            self.assertEqual(str(btime), '0:45:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=7*60*60 + 10*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '6:25:00')
            self.assertEqual(str(btime), '0:45:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=7*60*60 + 58*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '7:13:00')
            self.assertEqual(str(btime), '0:45:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=8*60*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '7:15:00')
            self.assertEqual(str(btime), '0:45:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=8*60*60 + 14*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '7:15:00')
            self.assertEqual(str(btime), '0:59:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=8*60*60 + 16*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '7:16:00')
            self.assertEqual(str(btime), '1:00:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=8*60*60 + 45*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '7:45:00')
            self.assertEqual(str(btime), '1:00:00')
            (wtime, btime) = EvalBtRule.get_reduced_worktime(evobj, timedelta(seconds=10*60*60 + 30*60), timedelta(seconds=0))
            self.assertEqual(str(wtime), '9:30:00')
            self.assertEqual(str(btime), '1:00:00')

# end DaysOfEvaluationTestCase
