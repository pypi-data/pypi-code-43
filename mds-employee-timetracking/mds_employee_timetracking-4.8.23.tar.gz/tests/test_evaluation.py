# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from datetime import date, time, datetime, timedelta
from decimal import Decimal
from trytond.modules.company.tests import set_company, create_company
from trytond.modules.employee_timetracking.tests.testlib import create_employee, \
    create_evaluation, create_tariff_full, create_period, create_holiday, create_worktime_full,\
    create_tariff, create_breaktime, create_trytonuser, add_tryton_user
from trytond.modules.employee_timetracking.const import ACRULE_HOLIDAY_NODEF


class EvaluationTestCase(ModuleTestCase):
    'Test evaluation module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_evaluation_create_item(self):
        """ test: create a valid evaluation
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
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

        with set_company(tarobj1.company):
            transaction = Transaction()
            
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
            
            tr_usr = add_tryton_user('Cronjob', 'Timetracking - Cronjob', company=tarobj1.company)
            
            with transaction.set_user(tr_usr.id):
                evobj = create_evaluation(employee1, date(2018, 4, 4))
    
                self.assertTrue(evobj)
                self.assertEqual(evobj.rec_name, 'Frida - 2018-04')
                self.assertEqual(str(evobj.evaldate), '2018-04-01')     # date moved to 1st of month
                self.assertEqual(str(evobj.datestart), '2018-04-01 00:00:00')
                self.assertEqual(str(evobj.dateend), '2018-04-30 23:59:59')
                dt1 = date.today()
                self.assertEqual(evobj.state_year, dt1.year - evobj.evaldate.year)
    
                # edit date, must be moved to 1st of month
                evobj.evaldate = date(2018, 4, 12)
                evobj.save()
                self.assertEqual(str(evobj.evaldate), '2018-04-01')
    
                # check days
                self.assertEqual(len(evobj.days), 30)
    
                # try another evaluation for same month
                eval_obj = Evaluation(
                        employee=employee1,
                        evaldate=date(2018, 4, 12),
                    )
                self.assertRaisesRegex(UserError,
                    "This date is already in use.",
                    eval_obj.save)
            
    @with_transaction()
    def test_evaluation_create_item_employee(self):
        """ test: employee tries to create evaluation, should fail
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
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

        with set_company(tarobj1.company):
            transaction = Transaction()
            
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            # employee-role cannot create/delete evaluation
            tr_usr2 = add_tryton_user('Employee1', 'Timetracking - Employee', company=tarobj1.company)
            with transaction.set_user(tr_usr2.id):
                self.assertRaises(UserError,
                    create_evaluation,
                    employee1, 
                    date(2018, 5, 4))
                    #"You try to read records that don't exist anymore\.\n\(Document type: employee_timetracking\.evaluation\)",

    @with_transaction()
    def test_evaluation_add_eval_items_by_tariffmodel(self):
        """ test: create evaluation, activate it
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                        {'name':'Work late', 'shortname':'W2'},
                        {'name':'Work night', 'shortname':'W3'},
                    ],
                accountrules=[
                        # time in localtime of company
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 16-19', 'shortname':'AR2', 
                         'mint':time(16, 0, 0), 'maxt':time(19, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                        {'name':'Work 19-24', 'shortname':'AR3', 
                         'mint':time(19, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.6'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
                        {'name':'Work 0-7', 'shortname':'AR4', 
                         'mint':time(0, 0, 0), 'maxt':time(7, 0, 0), 
                         'fact':Decimal('1.6'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
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

            evobj1 = create_evaluation(employee1, date(2018, 4, 4))
            self.assertEqual(evobj1.state, 'c')
            Evaluation.wfactivate([evobj1])
            self.assertEqual(evobj1.state, 'a')
            self.assertEqual(len(evobj1.evalitem), 3)
            
            ev_lst = sorted(evobj1.evalitem, key=lambda t1: t1.account.shortname)
            self.assertEqual(str(ev_lst[0].evaluation.rec_name), 'Frida - 2018-04')
            self.assertEqual(ev_lst[0].account.name, 'Work')
            self.assertEqual(str(ev_lst[0].balancestart), '0:00:00')
            self.assertEqual(ev_lst[0].start_minute, '00:00')
            self.assertEqual(str(ev_lst[0].balancediff), '0:00:00')
            self.assertEqual(ev_lst[0].diff_minute, '00:00')

            self.assertEqual(str(ev_lst[1].evaluation.rec_name), 'Frida - 2018-04')
            self.assertEqual(ev_lst[1].account.name, 'Work late')
            self.assertEqual(str(ev_lst[1].balancestart), '0:00:00')
            self.assertEqual(str(ev_lst[1].balancediff), '0:00:00')

            self.assertEqual(str(ev_lst[2].evaluation.rec_name), 'Frida - 2018-04')
            self.assertEqual(ev_lst[2].account.name, 'Work night')
            self.assertEqual(str(ev_lst[2].balancestart), '0:00:00')
            self.assertEqual(str(ev_lst[2].balancediff), '0:00:00')

    @with_transaction()
    def test_evaluation_deny_lock_if_predecessor_not_locked(self):
        """ test: create evaluation, dont lock it, create another, try to lock
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
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

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
            
            # 1st evaluation
            evobj1 = create_evaluation(employee1, date(2018, 4, 4))
            self.assertEqual(evobj1.state, 'c')
            
            # 2nd evaluation
            evobj2 = create_evaluation(employee1, date(2018, 5, 5))
            self.assertEqual(evobj2.state, 'c')
            Evaluation.wfactivate([evobj2]) # no account rules defined --> no eval-items
            self.assertEqual(evobj2.state, 'a')
            self.assertRaisesRegex(UserError,
                "The evaluation can not be fixed because the evaluation 'Frida - 2018-04' is not yet fixed.",
                Evaluation.wflock,
                [evobj2])

    @with_transaction()
    def test_evaluation_update_start_balance(self):
        """ test: create evaluation with diff-balance, create another, check transfer
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
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

        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            # 1st item
            evobj1 = create_evaluation(employee1, date(2018, 3, 4))
            self.assertEqual(evobj1.state, 'c')
            Evaluation.wfactivate([evobj1])
            self.assertEqual(evobj1.state, 'a')
            self.assertEqual(len(evobj1.evalitem), 1)
            self.assertEqual(str(evobj1.evalitem[0].balancestart), '0:00:00')
            self.assertEqual(str(evobj1.evalitem[0].balancediff), '0:00:00')
            # add balance-diff
            evobj1.evalitem[0].balancediff = timedelta(seconds=2342)
            evobj1.evalitem[0].save()
            self.assertEqual(evobj1.evalitem[0].balancediff, timedelta(seconds=2342))
            self.assertEqual(evobj1.evalitem[0].diff_minute, '00:39')

            # 2nd item - transfer balance to next month
            evobj2 = create_evaluation(employee1, date(2018, 4, 4))
            self.assertEqual(evobj2.state, 'c')
            Evaluation.wfactivate([evobj2])
            self.assertEqual(evobj2.state, 'a')
            self.assertEqual(len(evobj2.evalitem), 1)
            self.assertEqual(str(evobj2.evalitem[0].balancestart), '0:39:02')
            self.assertEqual(evobj2.evalitem[0].start_minute, '00:39')
            self.assertEqual(str(evobj2.evalitem[0].balancediff), '0:00:00')
            self.assertEqual(evobj2.evalitem[0].diff_minute, '00:00')
            
            self.assertEqual(str(evobj2.bal_prev_month), '0:00:00')
            self.assertEqual(evobj2.bal_prev_month_str, '00:00')

    @with_transaction()
    def test_evaluation_update_diff_balance(self):
        """ test: create evaluation/period/time account items, check diff_balance
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        EvaluationItem = pool.get('employee_timetracking.evaluationitem')
        Period = pool.get('employee_timetracking.period')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                        {'name':'Work late', 'shortname':'W2'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 19-21', 'shortname':'AR1', 
                         'mint':time(19, 0, 0), 'maxt':time(21, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
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
            
            # 03/2018 - target for time-account-items
            evobj1 = create_evaluation(employee1, date(2018, 3, 4))
            self.assertEqual(evobj1.state, 'c')
            self.assertEqual(evobj1.rec_name, 'Frida - 2018-03')
            self.assertEqual(str(evobj1.accountitems), '()')
            self.assertEqual(evobj1.needs_recalc, True)
            Evaluation.wfactivate([evobj1])
            self.assertEqual(evobj1.needs_recalc, False)
            self.assertEqual(len(evobj1.evalitem), 2)
            l2b = sorted(evobj1.evalitem, key=lambda tl2: tl2.rec_name)
            self.assertEqual(l2b[0].rec_name, 'Frida - 2018-03 - Work')
            self.assertEqual(str(l2b[0].balancestart), '0:00:00')
            self.assertEqual(str(l2b[0].balancediff), '0:00:00')
            self.assertEqual(l2b[1].rec_name, 'Frida - 2018-03 - Work late')
            self.assertEqual(str(l2b[1].balancestart), '0:00:00')
            self.assertEqual(str(l2b[1].balancediff), '0:00:00')
            
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
            # workflow action --> create time account items
            Period.wfexamine([p1])
            self.assertEqual(len(p1.accountitem), 2)
            self.assertEqual(evobj1.needs_recalc, True)
            # new time-account-items are connected with its period-item
            l2a = sorted(p1.accountitem, key=lambda tl2: tl2.startpos)
            self.assertEqual(str(l2a[0].name), '08:30 - 21:35, 2018-03-26 [W1]')
            self.assertEqual(str(l2a[0].accountrule.name), 'Work 0-24')
            self.assertEqual(str(l2a[1].name), '19:00 - 21:00, 2018-03-26 [W2]')
            self.assertEqual(str(l2a[1].accountrule.name), 'Work 19-21')
            
            # new time-account-item should be visible by 'accountitems' of evaluation-object
            tal2 = [x.id for x in sorted(evobj1.accountitems, key=lambda tl2: tl2.id)]
            tal3 = [x.id for x in sorted(p1.accountitem, key=lambda tl2: tl2.id)]
            self.assertEqual(tal2, tal3)
            # select evaluation by its account-items
            l2a = sorted(p1.accountitem, key=lambda tl2: tl2.startpos)
            self.assertEqual(str(l2a[0].name), '08:30 - 21:35, 2018-03-26 [W1]')
            # find by single id
            tal4 = Evaluation.search([('accountitems.id', '=', l2a[0].id)])
            self.assertEqual(len(tal4), 1)
            self.assertEqual(tal4[0].rec_name, 'Frida - 2018-03')
            # find by list of ids, no. 1
            tal4 = Evaluation.search([('accountitems.id', 'in', [l2a[0].id])])
            self.assertEqual(len(tal4), 1)
            self.assertEqual(tal4[0].rec_name, 'Frida - 2018-03')
            # find by list of ids, no. 2
            tal4 = Evaluation.search([('accountitems', 'in', [l2a[0].id])])
            self.assertEqual(len(tal4), 1)
            self.assertEqual(tal4[0].rec_name, 'Frida - 2018-03')
            # find by list of ids, no. 3
            # all time-account-items are in 03/2018 - we should find 1x evaluation
            tal4 = Evaluation.search([('accountitems', 'in', [x.id for x in l2a])])
            self.assertEqual(len(tal4), 1)
            self.assertEqual(tal4[0].rec_name, 'Frida - 2018-03')

            # calculate the durations for the difference balance
            # recalc every item (ignore_notchanged=False)
            Evaluation.updt_calc_evaluation(evobj1)
            self.assertEqual(evobj1.needs_recalc, False)
            l2b = sorted(evobj1.evalitem, key=lambda tl2: tl2.rec_name)

            self.assertEqual(str(evobj1.bal_prev_month), '0:00:00')
            self.assertEqual(evobj1.bal_prev_month_str, '00:00')
            
            self.assertEqual(l2b[0].rec_name, 'Frida - 2018-03 - Work')
            self.assertEqual(l2b[0].balancestart, timedelta(seconds=0))
            self.assertEqual(l2b[0].start_minute, '00:00')
            self.assertEqual(str(l2b[0].balancediff), '13:05:23')
            self.assertEqual(l2b[0].diff_minute, '13:05')
            
            self.assertEqual(l2b[1].rec_name, 'Frida - 2018-03 - Work late')
            self.assertEqual(l2b[1].balancestart, timedelta(seconds=0))
            self.assertEqual(l2b[1].start_minute, '00:00')
            self.assertEqual(l2b[1].balancediff, timedelta(seconds=2*3600 + 36*60))    # Factor '1.3' in accountrule
            self.assertEqual(l2b[1].diff_minute, '02:36')

    @with_transaction()
    def test_evaluation_get_companies_to_run(self):
        """ test: find companies having timetracking enabled employees
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
        # 1st company with employee
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
        
        # 2nd company without employee
        tarobj2 = create_tariff_full(tarname='Tariff2', tarshort='T2', 
                companyname='m-ds 2',
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
        self.assertTrue(tarobj2)
        tarobj2.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj2.company.save()

        # 3rd company without tariff
        c3 = create_company('m-ds 3')
        self.assertTrue(c3)
        
        self.assertEqual(Evaluation.get_companies_to_run(), [tarobj1.company])
        
        # disable employee from timetracking
        employee1.tariff = None
        employee1.save()

        self.assertEqual(Evaluation.get_companies_to_run(), [])
        
    @with_transaction()
    def test_evaluation_check_cronsetup(self):
        """ test: check detection of missing company for cron job
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        Cron = pool.get('ir.cron')
        ModelData = pool.get('ir.model.data')
        
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
        
        # now we have tariff and employee, the cron job still has no companies
        # check must fail
        self.assertRaisesRegex(UserError,
            "The company 'm-ds 1' is not in the list of companies of the cron job.",
            Evaluation.check_cronsetup)
            
        # edit cron-job
        cr1 = Cron(ModelData.get_id('employee_timetracking', 'cron_recalc_timeaccounts'))
        cr1.companies = [tarobj1.company]
        cr1.save()

        Evaluation.check_cronsetup()
        
    @with_transaction()
    def test_evaluation_cron_recalc_evaluation(self):
        """ test: create evaluation/employee/periods/time-account-items, run cron-job
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        Period = pool.get('employee_timetracking.period')
        
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                        {'name':'Work late', 'shortname':'W2'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 19-21', 'shortname':'AR1', 
                         'mint':time(19, 0, 0), 'maxt':time(21, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
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

        # add company to cron job
        Evaluation.edit_cronjob()
        
        # run cron-job 1st time
        # creates evaluation-item for current month --> date.today()
        Evaluation.cron_recalc_evaluation()
        ev_auto1 = Evaluation.search([])    # list of evaluations to ignore
        self.assertEqual(len(ev_auto1), 1)
        auto_ids = []
        for i in ev_auto1:
            auto_ids.append(i.id)

        with set_company(tarobj1.company):
            evobj1 = create_evaluation(employee1, date(2018, 3, 4))
            self.assertEqual(evobj1.state, 'c')
            self.assertEqual(evobj1.rec_name, 'Frida - 2018-03')
            self.assertEqual(evobj1.needs_recalc, True)
            Evaluation.wfactivate([evobj1])
            self.assertEqual(evobj1.needs_recalc, False)
            self.assertEqual(evobj1.state, 'a')
            self.assertEqual(len(evobj1.evalitem), 2)
            l2b = sorted(evobj1.evalitem, key=lambda tl2: tl2.rec_name)
            self.assertEqual(l2b[0].rec_name, 'Frida - 2018-03 - Work')
            self.assertEqual(str(l2b[0].balancestart), '0:00:00')
            self.assertEqual(str(l2b[0].balancediff), '0:00:00')
            self.assertEqual(l2b[1].rec_name, 'Frida - 2018-03 - Work late')
            self.assertEqual(str(l2b[1].balancestart), '0:00:00')
            self.assertEqual(str(l2b[1].balancediff), '0:00:00')
            
            # edit balancestart manually
            # recalc will move this back to '0:00:00'
            l2b[0].balancestart = timedelta(minutes=25)
            l2b[0].save()
            self.assertEqual(str(l2b[0].balancestart), '0:25:00')
            self.assertEqual(evobj1.needs_recalc, False)
            evobj1.needs_recalc = True
            evobj1.save()
            self.assertEqual(evobj1.needs_recalc, True)

        # run cron-job
        Evaluation.cron_recalc_evaluation()

        # check result, no time account items until now --> balances = 0
        ev_lst = Evaluation.search([('id', 'not in', auto_ids)])
        self.assertEqual(len(ev_lst), 1)
        l2b = sorted(ev_lst[0].evalitem, key=lambda tl2: tl2.rec_name)
        self.assertEqual(l2b[0].rec_name, 'Frida - 2018-03 - Work')
        self.assertEqual(l2b[0].balancestart, timedelta(seconds=0))
        self.assertEqual(l2b[0].balancediff, timedelta(seconds=0))
        self.assertEqual(l2b[1].rec_name, 'Frida - 2018-03 - Work late')
        self.assertEqual(l2b[1].balancestart, timedelta(seconds=0))
        self.assertEqual(l2b[1].balancediff, timedelta(seconds=0))

        # add balancestart manually, disable recalc of 'balancestart'
        l2b[0].balancestart = timedelta(minutes=25)
        l2b[0].balstartmanu = True
        l2b[0].save()

        # employee adds a period
        with set_company(tarobj1.company):
            p1 = create_period(
                    datetime(2018, 3, 26, 6, 30, 0), 
                    datetime(2018, 3, 26, 16, 35, 23), 
                    tarobj1.type_present, employee1)    # DB stores in UTC
            self.assertEqual(str(p1.startpos), '2018-03-26 06:30:00')   # UTC
            self.assertEqual(str(p1.endpos),   '2018-03-26 16:35:23')
            self.assertEqual(p1.name, '08:30 - 18:35, 2018-03-26 [W]')  # CEST
            self.assertEqual(p1.employee.party.name, 'Frida')
            self.assertEqual(p1.presence.name, 'Work')
            self.assertEqual(p1.state, 'c')
            # workflow action --> create time account items
            Period.wfexamine([p1])
            # wfexamine() creates time-account-items and mark evaluation-item for recalc
            self.assertEqual(len(p1.accountitem), 1)
            self.assertEqual(str(p1.accountitem[0].name), '08:30 - 18:35, 2018-03-26 [W1]')
            self.assertEqual(ev_lst[0].needs_recalc, True)

        # recalc 1x new item
        Evaluation.cron_recalc_evaluation()
        self.assertEqual(ev_lst[0].needs_recalc, False)
        self.assertEqual(type(ev_lst[0].recalc_at), type(datetime.now()))

        # check result, 'work' has now a value
        l2b = sorted(ev_lst[0].evalitem, key=lambda tl2: tl2.rec_name)
        self.assertEqual(l2b[0].rec_name, 'Frida - 2018-03 - Work')
        self.assertEqual(l2b[0].balancestart, timedelta(minutes=25))
        self.assertEqual(l2b[0].balstartmanu, True)
        self.assertEqual(l2b[0].balancediff, timedelta(seconds=10*3600 + 5*60 + 23))
        self.assertEqual(l2b[1].rec_name, 'Frida - 2018-03 - Work late')
        self.assertEqual(l2b[1].balancestart, timedelta(seconds=0))
        self.assertEqual(l2b[1].balstartmanu, False)
        self.assertEqual(l2b[1].balancediff, timedelta(seconds=0))

    @with_transaction()
    def test_evaluation_add_evaluations_by_date(self):
        """ test: create company/employees/evaluations for 1x employee
            test if add_evaluations() auto-creates missing evaluations
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')

        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                        {'name':'Work late', 'shortname':'W2'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 19-21', 'shortname':'AR1', 
                         'mint':time(19, 0, 0), 'maxt':time(21, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
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

            employee2 = create_employee(tarobj1.company, name='Diego')
            self.assertTrue(employee2)
            employee2.tariff = tarobj1
            employee2.save()

            # no tariff for leo
            employee3 = create_employee(tarobj1.company, name='Leo')
            self.assertTrue(employee3)

        lst1 = Evaluation.add_evaluations_by_date(tarobj1.company, evaldate=date(2018, 4, 10))
        self.assertEqual(len(lst1), 2)
        lst2 = sorted(lst1, key=lambda tl2: tl2.employee.party.rec_name)
        self.assertEqual(lst2[0].employee.rec_name, 'Diego')
        self.assertEqual(lst2[0].evaldate, date(2018, 4, 1))
        self.assertEqual(lst2[1].employee.rec_name, 'Frida')
        self.assertEqual(lst2[1].evaldate, date(2018, 4, 1))
        lst1 = Evaluation.add_evaluations_by_date(tarobj1.company, evaldate=date(2018, 4, 10))
        self.assertEqual(len(lst1), 0)

    @with_transaction()
    def test_evaluation_monthly_report(self):
        """ test: create evaluation and times for two months, check report values,
                two sick days
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        Holiday = pool.get('employee_timetracking.holiday')
        Period = pool.get('employee_timetracking.period')

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
                        {'name':'Work', 'shortname':'W1'},
                        {'name':'Work late', 'shortname':'W2'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 19-21', 'shortname':'AR1', 
                         'mint':time(19, 0, 0), 'maxt':time(21, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work', main_account='Work',
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
                {'name':'WTR2', 'mon':False, 'tue':False, 'wed':False, 'thu':False, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(6,0), 'maxtime':time(7, 0)},
            ])
        
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()
        
        # holidays
        create_holiday('half day, every year', date(2018, 4, 4), company=tarobj1.company, repyear=True, halfday=True)
        create_holiday('full day, every year', date(2018, 4, 5), company=tarobj1.company, repyear=True, halfday=False)
        create_holiday('half day, this year',  date(2018, 4, 6), company=tarobj1.company, repyear=False, halfday=True)
        create_holiday('at saturday',          date(2018, 4, 7), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('full day, this year',  date(2018, 4, 10), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('Ascension',  date(2018, 5, 10), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('Whit Sunday',  date(2018, 5, 20), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('Whit Monday',  date(2018, 5, 21), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('Labor Day',  date(2018, 5, 1), company=tarobj1.company, repyear=True, halfday=False)
        self.assertEqual(len(Holiday.search([('company', '=', tarobj1.company)])), 9)

        with set_company(tarobj1.company):            
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.save()
            
            # add company to cron job
            Evaluation.edit_cronjob()

            # check setting of employee
            self.assertEqual(employee1.tariff.name, 'Tariff1')
            self.assertEqual(employee1.worktime.name, 'work day')
            self.assertEqual(employee1.worktime.hours_per_week, Decimal('41.0'))

            # first month
            
            # employee adds a few workdays
            p1 = create_period( datetime(2018, 4, 18, 6, 30, 0),  datetime(2018, 4, 18, 10, 5, 42),tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '08:30 - 12:05, 2018-04-18 [W]')
            self.assertEqual(p1.duration, timedelta(seconds=3*3600 + 30*60 + 5*60 + 42))    # = 12942
            p2 = create_period(datetime(2018, 4, 18, 11, 0, 0), datetime(2018, 4, 18, 14, 42, 23), tarobj1.type_present, employee1)
            self.assertEqual(p2.name, '13:00 - 16:42, 2018-04-18 [W]')
            self.assertEqual(p2.duration, timedelta(seconds=3*3600 + 42*60 + 23))           # = 13343
            p3 = create_period(datetime(2018, 4, 20, 6, 0, 0), datetime(2018, 4, 20, 13, 48, 23), tarobj1.type_present, employee1)
            self.assertEqual(p3.name, '08:00 - 15:48, 2018-04-20 [W]')
            self.assertEqual(p3.duration, timedelta(seconds=7*3600 + 48*60 + 23))           # = 28103
            p4 = create_period(datetime(2018, 4, 12, 9, 0, 0), datetime(2018, 4, 12, 20, 48, 23), tarobj1.type_present, employee1)
            self.assertEqual(p4.name, '11:00 - 22:48, 2018-04-12 [W]')
            self.assertEqual(p4.duration, timedelta(seconds=11*3600 + 48*60 + 23))          # = 42503
            
            # create time-account-items, evaluation is created automatically
            Period.wfexamine([p1, p2, p3, p4])

            # get new created evaluation
            emp_lst = Evaluation.search([('employee', '=', employee1), ('evaldate', '=', date(2018, 4, 1))])
            self.assertEqual(len(emp_lst), 1)
            self.assertEqual(emp_lst[0].rec_name, 'Frida - 2018-04')
            
            # close this month
            Evaluation.wflock([emp_lst[0]])
            self.assertEqual(emp_lst[0].state, 'l')
            self.assertEqual(emp_lst[0].needs_recalc, False)
            # check values
            self.assertEqual(str(emp_lst[0].datestart), '2018-04-01 00:00:00')
            self.assertEqual(str(emp_lst[0].dateend), '2018-04-30 23:59:59')

            self.assertEqual(str(emp_lst[0].bal_prev_month), '0:00:00')
            self.assertEqual(emp_lst[0].bal_prev_month_str, '00:00')

            self.assertEqual(len(emp_lst[0].accountitems), 5)
            l2 = sorted(emp_lst[0].accountitems, key=lambda tl2: tl2.startpos)
            self.assertEqual(l2[0].name, '11:00 - 22:48, 2018-04-12 [W1]')
            self.assertEqual(str(l2[0].duration), '11:48:23')       # W1 : 42503
            self.assertEqual(l2[0].duration, timedelta(seconds=42503))
            
            self.assertEqual(l2[1].name, '19:00 - 21:00, 2018-04-12 [W2]')
            self.assertEqual(str(l2[1].duration), '2:00:00')        # W2 : 7200
            self.assertEqual(l2[1].duration, timedelta(seconds=7200))
            
            self.assertEqual(l2[2].name, '08:30 - 12:05, 2018-04-18 [W1]')
            self.assertEqual(str(l2[2].duration), '3:35:42')        # W1 : 12942
            self.assertEqual(l2[2].duration, timedelta(seconds=12942))
            
            self.assertEqual(l2[3].name, '13:00 - 16:42, 2018-04-18 [W1]')
            self.assertEqual(str(l2[3].duration), '3:42:23')        # W1 : 13343
            self.assertEqual(l2[3].duration, timedelta(seconds=13343))
            
            self.assertEqual(l2[4].name, '08:00 - 15:48, 2018-04-20 [W1]')
            self.assertEqual(str(l2[4].duration), '7:48:23')        # W1 : 28103
            self.assertEqual(l2[4].duration, timedelta(seconds=28103))
            
            # working times
            self.assertEqual(emp_lst[0].worktime_target_str, '147:30')
            self.assertEqual(emp_lst[0].worktime_target, timedelta(seconds=30*60 + 147*60*60))  # 531000
            self.assertEqual(emp_lst[0].worktime_actual_str, '26:55')
            self.assertEqual(emp_lst[0].worktime_actual, timedelta(seconds=55*60 + 26*60*60))   # 96900
            self.assertEqual(emp_lst[0].worktime_wobreaks_str, '25:10')
            self.assertEqual(emp_lst[0].worktime_wobreaks, timedelta(seconds=10*60 + 25*60*60))
            self.assertEqual(emp_lst[0].worktime_diff_str, '-122:20')
            self.assertEqual(emp_lst[0].worktime_diff, -timedelta(seconds=20*60 + 122*60*60))   # 434100
            self.assertEqual(emp_lst[0].holidays, 4)
            self.assertEqual(emp_lst[0].payed_out, timedelta(seconds=30*60 + 147*60*60))        # 531000
            self.assertEqual(emp_lst[0].bal_prev_month, timedelta(seconds=0))
            # current = prev-month + actual - payed
            bal_curr_april = timedelta(seconds=25*3600 + 9*60 + 51) - timedelta(seconds=30*60 + 147*60*60)   # roundup(bal_diff) - bal_payed
            self.assertEqual(emp_lst[0].bal_current_month, bal_curr_april + timedelta(seconds=9))
            
            # balances
            self.assertEqual(len(emp_lst[0].evalitem), 2)
            l2 = sorted(emp_lst[0].evalitem, key=lambda tl2: tl2.rec_name)
            # work
            self.assertEqual(l2[0].rec_name, 'Frida - 2018-04 - Work')
            self.assertEqual(l2[0].account.name, 'Work')
            self.assertEqual(l2[0].balancestart, timedelta(seconds=0))
            self.assertEqual(l2[0].start_minute, '00:00')
            self.assertEqual(l2[0].balancediff, timedelta(seconds=25*3600 + 9*60 + 51))
            self.assertEqual(l2[0].diff_minute, '25:09')    # different from worktime_actual_str (rounded up)
            self.assertEqual(l2[0].payed_out, timedelta(seconds=30*60 + 147*60*60))
            self.assertEqual(l2[0].evalstate, 'l')
            self.assertEqual(bal_curr_april, timedelta(seconds=0) + timedelta(seconds=25*3600 + 9*60 + 51) - timedelta(seconds=30*60 + 147*60*60))

            # work late
            self.assertEqual(l2[1].rec_name, 'Frida - 2018-04 - Work late')
            self.assertEqual(l2[1].account.name, 'Work late')
            self.assertEqual(l2[1].balancestart, timedelta(seconds=0))
            self.assertEqual(l2[1].start_minute, '00:00')
            self.assertEqual(l2[1].balancediff, timedelta(seconds=9360))                        # 9360
            self.assertEqual(l2[1].diff_minute, '02:36')
            self.assertEqual(l2[1].payed_out, timedelta(seconds=0))
            self.assertEqual(l2[1].evalstate, 'l')

            ##############
            # next month #
            ##############
            
            # employee adds a few workdays
            p1 = create_period(datetime(2018, 5, 3, 6, 30, 0), datetime(2018, 5, 3, 14, 5, 0),tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '08:30 - 16:05, 2018-05-03 [W]')
            self.assertEqual(p1.duration, timedelta(seconds=7*3600 + 30*60 + 5*60))         # 27300
            p2 = create_period(datetime(2018, 5, 4, 6, 15, 0), datetime(2018, 5, 4, 14, 42, 0), tarobj1.type_present, employee1)
            self.assertEqual(p2.name, '08:15 - 16:42, 2018-05-04 [W]')
            self.assertEqual(p2.duration, timedelta(seconds=8*3600 + 27*60))                # 30420
            p3 = create_period(datetime(2018, 5, 7, 6, 16, 0), datetime(2018, 5, 7, 14, 35, 0), tarobj1.type_present, employee1)
            self.assertEqual(p3.name, '08:16 - 16:35, 2018-05-07 [W]')
            self.assertEqual(p3.duration, timedelta(seconds=8*3600 + 19*60))                # 29940
            p4 = create_period(datetime(2018, 5, 8, 6, 16, 0), datetime(2018, 5, 8, 14, 35, 0), tarobj1.type_present, employee1)
            self.assertEqual(p4.name, '08:16 - 16:35, 2018-05-08 [W]')
            self.assertEqual(p4.duration, timedelta(seconds=8*3600 + 19*60))                # 29940
            p5 = create_period(datetime(2018, 5, 9, 6, 16, 0), datetime(2018, 5, 9, 14, 35, 0), tarobj1.type_present, employee1)
            self.assertEqual(p5.name, '08:16 - 16:35, 2018-05-09 [W]')
            self.assertEqual(p5.duration, timedelta(seconds=8*3600 + 19*60))                # 29940
            p6 = create_period(datetime(2018, 5, 11, 6, 16, 0), datetime(2018, 5, 11, 14, 35, 0), tarobj1.type_present, employee1)
            self.assertEqual(p6.name, '08:16 - 16:35, 2018-05-11 [W]')
            self.assertEqual(p6.duration, timedelta(seconds=8*3600 + 19*60))                # 29940
            
            # create time-account-items, evaluation is created automatically
            Period.wfexamine([p1, p2, p3, p4, p5, p6])

            # get new created evaluation
            emp_lst = Evaluation.search([('employee', '=', employee1), ('evaldate', '=', date(2018, 5, 1))])
            self.assertEqual(len(emp_lst), 1)
            self.assertEqual(emp_lst[0].rec_name, 'Frida - 2018-05')
            self.assertEqual(emp_lst[0].state, 'a')
            self.assertEqual(emp_lst[0].needs_recalc, True)
            
            # update values
            Evaluation.cron_recalc_evaluation()
            self.assertEqual(emp_lst[0].needs_recalc, False)
            
            # check values
            self.assertEqual(str(emp_lst[0].datestart), '2018-05-01 00:00:00')
            self.assertEqual(str(emp_lst[0].dateend), '2018-05-31 23:59:59')
            self.assertEqual(len(emp_lst[0].accountitems), 6)
            l2 = sorted(emp_lst[0].accountitems, key=lambda tl2: tl2.startpos)
            self.assertEqual(l2[0].name, '08:30 - 16:05, 2018-05-03 [W1]')
            self.assertEqual(str(l2[0].duration), '7:35:00')    # break: 30min
            self.assertEqual(l2[1].name, '08:15 - 16:42, 2018-05-04 [W1]')
            self.assertEqual(str(l2[1].duration), '8:27:00')    # break: 45min
            self.assertEqual(l2[2].name, '08:16 - 16:35, 2018-05-07 [W1]')
            self.assertEqual(str(l2[2].duration), '8:19:00')    # break: 45min
            self.assertEqual(l2[3].name, '08:16 - 16:35, 2018-05-08 [W1]')
            self.assertEqual(str(l2[3].duration), '8:19:00')    # break: 45min
            self.assertEqual(l2[4].name, '08:16 - 16:35, 2018-05-09 [W1]')
            self.assertEqual(str(l2[4].duration), '8:19:00')    # break: 45min
            self.assertEqual(l2[5].name, '08:16 - 16:35, 2018-05-11 [W1]')
            self.assertEqual(str(l2[5].duration), '8:19:00')    # break: 45min
            # balances
            self.assertEqual(len(emp_lst[0].evalitem), 2)
            l2 = sorted(emp_lst[0].evalitem, key=lambda tl2: tl2.rec_name)
            # work
            self.assertEqual(l2[0].rec_name, 'Frida - 2018-05 - Work')
            self.assertEqual(l2[0].account.name, 'Work')
            self.assertEqual(l2[0].balancestart, bal_curr_april)  # balance of previous month: timedelta(seconds=25*3600 + 9*60 + 51) - timedelta(seconds=30*60 + 147*60*60)
            self.assertEqual(l2[0].start_minute, '-122:20')
            self.assertEqual(l2[0].balancediff, timedelta(seconds=49*3600 + 18*60 - 45*60*5 - 30*60))   # reduce by breaks
            self.assertEqual(l2[0].diff_minute, '45:03')
            self.assertEqual(l2[0].payed_out, timedelta(seconds=164*60*60))
            self.assertEqual(l2[0].evalstate, 'a')
            # work late
            self.assertEqual(l2[1].rec_name, 'Frida - 2018-05 - Work late')
            self.assertEqual(l2[1].account.name, 'Work late')
            self.assertEqual(l2[1].balancestart, timedelta(seconds=2*3600 + 36*60))
            self.assertEqual(l2[1].start_minute, '02:36')
            self.assertEqual(l2[1].balancediff, timedelta(seconds=0))
            self.assertEqual(l2[1].diff_minute, '00:00')
            self.assertEqual(l2[1].payed_out, timedelta(seconds=0))
            self.assertEqual(l2[1].evalstate, 'a')

            # working times
            self.assertEqual(emp_lst[0].worktime_target_str, '164:00')
            self.assertEqual(emp_lst[0].worktime_target, timedelta(seconds=164*60*60))
            self.assertEqual(emp_lst[0].worktime_actual_str, '49:18')
            self.assertEqual(emp_lst[0].worktime_actual, timedelta(seconds=18*60 + 49*60*60))
            self.assertEqual(emp_lst[0].worktime_wobreaks_str, '45:03')
            self.assertEqual(emp_lst[0].worktime_wobreaks, timedelta(seconds=3*60 + 45*60*60))
            self.assertEqual(emp_lst[0].worktime_diff_str, '-118:57')
            self.assertEqual(emp_lst[0].worktime_diff, -timedelta(seconds=57*60 + 118*60*60))
            self.assertEqual(emp_lst[0].holidays, 3)
            self.assertEqual(emp_lst[0].payed_out, timedelta(seconds=164*60*60))
            self.assertEqual(emp_lst[0].bal_prev_month, bal_curr_april)
            # prev-month + actual - payed
            # sum(durations) of current month is roundet up, but no change of worktime_actual
            # because its already at full minute
            bal_curr_may = bal_curr_april + timedelta(seconds=45*3600 + 3*60) - timedelta(seconds=164*60*60)
            self.assertEqual(emp_lst[0].bal_current_month, bal_curr_may)

            self.assertEqual(str(emp_lst[0].bal_prev_month), '-6 days, 21:39:51')
            self.assertEqual(emp_lst[0].bal_prev_month_str, '-122:20')

    @with_transaction()
    def test_evaluation_report_export(self):
        """ test: create evaluation and times, run exports
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        Holiday = pool.get('employee_timetracking.holiday')
        Period = pool.get('employee_timetracking.period')

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
                        {'name':'Work', 'shortname':'W1'},
                        {'name':'Work late', 'shortname':'W2'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 19-21', 'shortname':'AR1', 
                         'mint':time(19, 0, 0), 'maxt':time(21, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work', main_account='Work',
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
                {'name':'WTR2', 'mon':False, 'tue':False, 'wed':False, 'thu':False, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(6,0), 'maxtime':time(7, 0)},
            ])
        
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()
        
        # holidays
        create_holiday('half day, every year', date(2018, 4, 4), company=tarobj1.company, repyear=True, halfday=True)
        create_holiday('full day, every year', date(2018, 4, 5), company=tarobj1.company, repyear=True, halfday=False)
        create_holiday('half day, this year',  date(2018, 4, 6), company=tarobj1.company, repyear=False, halfday=True)
        create_holiday('at saturday',          date(2018, 4, 7), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('full day, this year',  date(2018, 4, 10), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('Ascension',  date(2018, 5, 10), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('Whit Sunday',  date(2018, 5, 20), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('Whit Monday',  date(2018, 5, 21), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('Labor Day',  date(2018, 5, 1), company=tarobj1.company, repyear=True, halfday=False)
        self.assertEqual(len(Holiday.search([('company', '=', tarobj1.company)])), 9)

        with set_company(tarobj1.company):            
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.save()
            
            # add company to cron job
            Evaluation.edit_cronjob()

            # check setting of employee
            self.assertEqual(employee1.tariff.name, 'Tariff1')
            self.assertEqual(employee1.worktime.name, 'work day')
            self.assertEqual(employee1.worktime.hours_per_week, Decimal('41.0'))

            # employee adds a few workdays
            p1 = create_period( datetime(2018, 4, 18, 6, 30, 0),  datetime(2018, 4, 18, 10, 5, 42),tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '08:30 - 12:05, 2018-04-18 [W]')
            p2 = create_period(datetime(2018, 4, 18, 11, 0, 0), datetime(2018, 4, 18, 14, 42, 23), tarobj1.type_present, employee1)
            self.assertEqual(p2.name, '13:00 - 16:42, 2018-04-18 [W]')
            p3 = create_period(datetime(2018, 4, 12, 12, 0, 0), datetime(2018, 4, 12, 20, 48, 23), tarobj1.type_present, employee1)
            self.assertEqual(p3.name, '14:00 - 22:48, 2018-04-12 [W]')
            
            # create time-account-items, evaluation is created automatically
            Period.wfexamine([p1, p2, p3])

            # get new created evaluation
            emp_lst = Evaluation.search([('employee', '=', employee1), ('evaldate', '=', date(2018, 4, 1))])
            self.assertEqual(len(emp_lst), 1)
            self.assertEqual(emp_lst[0].rec_name, 'Frida - 2018-04')
            self.assertEqual(len(emp_lst[0].evalitem), 2)
            evitm_l2 = sorted(emp_lst[0].evalitem, key=lambda tl2: tl2.account.name)
            self.assertEqual(evitm_l2[0].account.name, 'Work')
            self.assertEqual(evitm_l2[1].account.name, 'Work late')

            # close this month
            Evaluation.wflock([emp_lst[0]])
            self.assertEqual(emp_lst[0].state, 'l')

            self.assertEqual(len(emp_lst[0].accountitems), 4)
            l2 = sorted(emp_lst[0].accountitems, key=lambda tl2: tl2.startpos)
            self.assertEqual(l2[0].name, '14:00 - 22:48, 2018-04-12 [W1]')
            self.assertEqual(l2[1].name, '19:00 - 21:00, 2018-04-12 [W2]')
            self.assertEqual(l2[2].name, '08:30 - 12:05, 2018-04-18 [W1]')
            self.assertEqual(l2[3].name, '13:00 - 16:42, 2018-04-18 [W1]')

        # prepare print of reports
        EvaluationMonthOdt = pool.get('employee_timetracking.report_evaluation_month', type='report')
        User = pool.get('res.user')

        # run reports - employee
        # use evaluation-employee to print report, other 'Timetracking - Employee'-users cannot see this evaluation
        rep_eval_lst = Evaluation.search([('evaldate', '=', date(2018, 4, 1))])
        self.assertEqual(len(rep_eval_lst), 1)
        rep_eval = rep_eval_lst[0]
        rep_tr1 = add_tryton_user('rep-emplo', 'Timetracking - Employee', 
            company=tarobj1.company, employee=rep_eval.employee, set_to_current=False)
        with Transaction().set_user(rep_tr1.id) as trans1:
            with trans1.set_context(User.get_preferences(context_only=True)):
                rep1 = EvaluationMonthOdt()
                (ext1, bin1, v1, v2) = rep1.execute(ids=[rep_eval.id], 
                    data={
                        'model': 'employee_timetracking.evaluation',
                        'action_id': None,
                        'id': rep_eval.id,
                        })
                self.assertEqual(ext1, 'odt')
                self.assertEqual(v2, '%s-evaluation-month-Frida_-_2018-04' % date.today().strftime('%Y%m%d'))

    @with_transaction()
    def test_evaluation_employee_dayofyear(self):
        """ test: create company/employees/time-account-items/evaluations, check result
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        Period = pool.get('employee_timetracking.period')
        Holiday = pool.get('employee_timetracking.holiday')
        SickDays = pool.get('employee_timetracking.evaluation_sickdays')

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
                        {'name':'Work', 'shortname':'W1'},
                        {'name':'Work late', 'shortname':'W2'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 19-21', 'shortname':'AR1', 
                         'mint':time(19, 0, 0), 'maxt':time(21, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work', main_account='Work',
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
                {'name':'WTR2', 'mon':False, 'tue':False, 'wed':False, 'thu':False, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(6,0), 'maxtime':time(7, 0)},
            ])
        
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()
        
        # holidays
        create_holiday('half day, every year', date(2018, 4, 4), company=tarobj1.company, repyear=True, halfday=True)
        create_holiday('full day, every year', date(2018, 4, 5), company=tarobj1.company, repyear=True, halfday=False)
        create_holiday('half day, this year',  date(2018, 4, 6), company=tarobj1.company, repyear=False, halfday=True)
        create_holiday('at saturday',          date(2018, 4, 7), company=tarobj1.company, repyear=False, halfday=False)
        create_holiday('full day, this year',  date(2018, 4, 10), company=tarobj1.company, repyear=False, halfday=False)
        self.assertEqual(len(Holiday.search([('company', '=', tarobj1.company)])), 5)

        with set_company(tarobj1.company):            
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.save()
            
            self.assertEqual(employee1.tariff.name, 'Tariff1')
            self.assertEqual(employee1.worktime.name, 'work day')
            self.assertEqual(employee1.worktime.hours_per_week, Decimal('41.0'))

            # employee adds a few workdays
            p1 = create_period(
                    datetime(2018, 4, 18, 6, 30, 0), 
                    datetime(2018, 4, 18, 10, 5, 42),                   # UTC
                    tarobj1.type_present, employee1)
            self.assertEqual(p1.name, '08:30 - 12:05, 2018-04-18 [W]')  # CEST  3h35min
            # two items at same day
            p2 = create_period(
                    datetime(2018, 4, 18, 11, 0, 0), 
                    datetime(2018, 4, 18, 14, 42, 23), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p2.name, '13:00 - 16:42, 2018-04-18 [W]')  # 3h42min
            # work at friday
            p3 = create_period(
                    datetime(2018, 4, 20, 6, 0, 0), 
                    datetime(2018, 4, 20, 13, 48, 23), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p3.name, '08:00 - 15:48, 2018-04-20 [W]')  # 7h48min
            # work with 'late'
            p4 = create_period(
                    datetime(2018, 4, 12, 9, 0, 0), 
                    datetime(2018, 4, 12, 20, 48, 23), 
                    tarobj1.type_present, employee1)
            self.assertEqual(p4.name, '11:00 - 22:48, 2018-04-12 [W]')  # 11h48min
            
            # create time-account-items, evaluation is created automatically
            Period.wfexamine([p1, p2, p3, p4])

            # add break time period - 25 min
            # starts 20 min before end of work time 'p1'
            # 20m42sec only counts
            BreakPeriod = pool.get('employee_timetracking.breakperiod')
            br2 = BreakPeriod(employee = employee1,
                startpos = datetime(2018, 4, 18, 9, 45, 0),
                endpos = datetime(2018, 4, 18, 10, 10, 0),
                state = BreakPeriod.default_state()
                )
            br2.save()

            # 15 min within work time - 15 min counts
            # this will rise break time to 35m42s (30 min before)
            br3 = BreakPeriod(employee = employee1,
                startpos = datetime(2018, 4, 18, 13, 0, 0),
                endpos = datetime(2018, 4, 18, 13, 15, 0),
                state = BreakPeriod.default_state()
                )
            br3.save()
            BreakPeriod.wfexamine([br2, br3])
            self.assertEqual(br2.name, '11:45 - 12:10, 2018-04-18')
            self.assertEqual(br2.state, 'e')
            self.assertEqual(br3.name, '15:00 - 15:15, 2018-04-18')
            self.assertEqual(br3.state, 'e')

            # get new created evaluation
            emp_lst = Evaluation.search([()])   # get all evaluations, should be 1x
            self.assertEqual(len(emp_lst), 1)
            self.assertEqual(emp_lst[0].rec_name, 'Frida - 2018-04')
            
            # add sick days
            emp_lst[0].sickdays = [
                    SickDays(date_start=date(2018, 4, 5), date_end=date(2018, 4, 5)),   # sick day at holiday (fullday)     0:00
                    SickDays(date_start=date(2018, 4, 6), date_end=date(2018, 4, 6)),   # sick day at holiday (halfday),    4:30
                    SickDays(date_start=date(2018, 4, 12), date_end=date(2018, 4, 12)), # working time at this day, sick day dont counts
                    SickDays(date_start=date(2018, 4, 14), date_end=date(2018, 4, 14)), # weekend, sick day dont counts
                    SickDays(date_start=date(2018, 4, 16), date_end=date(2018, 4, 16)), # no working time at this day       8:00
                ]
            emp_lst[0].save()

            # evaluation has copy of work time model
            self.assertEqual(len(emp_lst[0].worktimerule), 2)
            l2 = sorted(emp_lst[0].worktimerule, key=lambda tl2: tl2.mintime)
            self.assertEqual(l2[0].rec_name, '06:00-07:00 [____x__]')
            self.assertEqual(l2[1].rec_name, '08:00-16:00 [xxxxx__]')

            # evaluation has copy of break time rules
            self.assertEqual(len(emp_lst[0].breaktimerule), 3)
            l2 = sorted(emp_lst[0].breaktimerule, key=lambda tl2: tl2.mintime)
            self.assertEqual(l2[0].rec_name, 'Frida - 2018-04: 04:00-05:59 -> 00h20')
            self.assertEqual(l2[1].rec_name, 'Frida - 2018-04: 06:00-07:59 -> 00h30')
            self.assertEqual(l2[2].rec_name, 'Frida - 2018-04: 08:00-09:59 -> 00h45')
            
            # evaluation has a list of days
            # it has more than one line per day if the employee adds
            # multiple work-time-items per day
            Evaluation.updt_calc_evaluation(emp_lst[0])
            self.assertEqual(len(emp_lst[0].days), 31)  # 30 days in april + 1x at 12.04. (late)
            self.assertEqual(emp_lst[0].worktime_target_str, '147:30')
            self.assertEqual(emp_lst[0].worktime_actual_str, '26:55')
            self.assertEqual(emp_lst[0].worktime_diff_str, '-109:55')
            self.assertEqual(emp_lst[0].worktime_wobreaks_str, '37:35')
            self.assertEqual(emp_lst[0].worktime_target, timedelta(seconds=30*60 + 147*60*60))
            self.assertEqual(emp_lst[0].worktime_actual, timedelta(seconds=55*60 + 26*60*60))
            self.assertEqual(emp_lst[0].worktime_diff, -timedelta(seconds=55*60 + 109*60*60))
            self.assertEqual(emp_lst[0].worktime_wobreaks, timedelta(seconds=35*60 + 37*60*60))
            self.assertEqual(emp_lst[0].holidays, 4)
            self.assertEqual(emp_lst[0].numsickdays, 2)

            self.assertEqual(len(emp_lst[0].accountitems), 5)
            l2 = sorted(emp_lst[0].accountitems, key=lambda tl2: tl2.startpos)
            self.assertEqual(l2[0].name, '11:00 - 22:48, 2018-04-12 [W1]')
            self.assertEqual(str(l2[0].duration), '11:48:23')
            self.assertEqual(l2[1].name, '19:00 - 21:00, 2018-04-12 [W2]')
            self.assertEqual(str(l2[1].duration), '2:00:00')
            self.assertEqual(l2[2].name, '08:30 - 12:05, 2018-04-18 [W1]')
            self.assertEqual(str(l2[2].duration), '3:35:42')
            self.assertEqual(l2[3].name, '13:00 - 16:42, 2018-04-18 [W1]')
            self.assertEqual(str(l2[3].duration), '3:42:23')
            self.assertEqual(l2[4].name, '08:00 - 15:48, 2018-04-20 [W1]')
            self.assertEqual(str(l2[4].duration), '7:48:23')

            # still to check
            # - work at holiday+weekend, work 2x at holiday+weekend
            
            #for i in emp_lst[0].days:
            #    print ('i:',i.date, i.weekday, i.week, i.startpos, i.endpos, i.sumact, i.targettime, i.duration, i.diff, i.wobreaks, i.breaktime, i.holiday_ena, i.holidayname, i.daytype, i.accountitem, i.accountitems_nonmain, i.info)

            # check values of list-of-days
            # sunday, 2018-04-01
            #    i    i.date        i.weekday, i.week, i.startpos, i.endpos,              i.sumact   i.targettime, i.duration, i.diff,          i.wobreaks, i.breaktime, i.holiday_ena, i.holidayname, i.daytype, i.accountitem, i.accountitems_nonmain, i.info
            for i in [
                (0,  '2018-04-01', '0', 13, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    False, None, 'we', 'None', '()', 'Weekend'),
                (1,  '2018-04-02', '1', 14, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (2,  '2018-04-03', '2', 14, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (3,  '2018-04-04', '3', 14, 'None',                'None',                'None',    '4:00:00', 'None',     '-1 day, 20:00:00', 'None',     'None',    True,  'half day, every year', 'hd', 'None', '()', 'half day, every year'),
                (4,  '2018-04-05', '4', 14, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    True,  'full day, every year', 'hd', 'None', '()', 'full day, every year'),
                (5,  '2018-04-06', '5', 14, 'None',                'None',                '4:30:00', '4:30:00', 'None',     '0:00:00',          '4:30:00',  '0:00:00', True,  'half day, this year', 'hd', 'None', '()', 'half day, this year, Sick Day'),
                (6,  '2018-04-07', '6', 14, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    True,  'at saturday', 'hd', 'None', '()', 'at saturday'),
                (7,  '2018-04-08', '0', 14, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00'         , 'None',     'None',    False, None, 'we', 'None', '()', 'Weekend'),
                (8,  '2018-04-09', '1', 15, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (9,  '2018-04-10', '2', 15, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    True,  'full day, this year', 'hd', 'None', '()', 'full day, this year'),
                (10, '2018-04-11', '3', 15, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (11, '2018-04-12', '4', 15, '2018-04-12 09:00:00', '2018-04-12 20:48:23', '11:48:23','8:00:00', '11:48:23', '3:03:23',          '11:03:23', '0:45:00', False, None, 'wd', str(l2[0]), str((l2[1],)), 'W2:02h00, Break:00h45'),
                (12, '2018-04-13', '5', 15, 'None',                'None',                'None',    '9:00:00', 'None',     '-1 day, 15:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (13, '2018-04-14', '6', 15, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    False, None, 'we', 'None', '()', 'Weekend'),
                (14, '2018-04-15', '0', 15, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    False, None, 'we', 'None', '()', 'Weekend'),
                (15, '2018-04-16', '1', 16, 'None',                'None',                '8:00:00', '8:00:00', 'None',     '0:00:00',          '8:00:00',  '0:00:00', False, None, 'wd', 'None', '()', 'Sick Day'),
                (16, '2018-04-17', '2', 16, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (17, '2018-04-18', '3', 16, '2018-04-18 06:30:00', '2018-04-18 10:05:42', '7:18:05', '8:00:00', '3:35:42',  '-1 day, 22:42:23', '6:42:23',  '0:35:42', False, None, 'wd', str(l2[2]), '()', 'Break:00h35'),
                (18, '2018-04-18', '3', 16, '2018-04-18 11:00:00', '2018-04-18 14:42:23', '7:18:05', '8:00:00', '3:42:23',  '-1 day, 22:42:23', '6:42:23',  '0:35:42', False, None, 'wd', str(l2[3]), '()', 'Break:00h35'),
                (19, '2018-04-19', '4', 16, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (20, '2018-04-20', '5', 16, '2018-04-20 06:00:00', '2018-04-20 13:48:23', '7:48:23', '9:00:00', '7:48:23',  '-1 day, 22:18:23', '7:18:23',  '0:30:00', False, None, 'wd', str(l2[4]), '()', 'Break:00h30'),
                (21, '2018-04-21', '6', 16, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    False, None, 'we', 'None', '()', 'Weekend'),
                (22, '2018-04-22', '0', 16, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    False, None, 'we', 'None', '()', 'Weekend'),
                (23, '2018-04-23', '1', 17, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (24, '2018-04-24', '2', 17, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (25, '2018-04-25', '3', 17, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (26, '2018-04-26', '4', 17, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (27, '2018-04-27', '5', 17, 'None',                'None',                'None',    '9:00:00', 'None',     '-1 day, 15:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                (28, '2018-04-28', '6', 17, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    False, None, 'we', 'None', '()', 'Weekend'),
                (29, '2018-04-29', '0', 17, 'None',                'None',                'None',    '0:00:00', 'None',     '0:00:00',          'None',     'None',    False, None, 'we', 'None', '()', 'Weekend'),
                (30, '2018-04-30', '1', 18, 'None',                'None',                'None',    '8:00:00', 'None',     '-1 day, 16:00:00', 'None',     'None',    False, None, 'wd', 'None', '()', ''),
                ]:
                (i1, date1, wd1, wk1, sp1, ep1, sa1, tt1, dur1, df1, wobr, brtm, he1, hn1, dt1, acc1, acn1, inf1) = i
                
                # ~ print ('date:', str(emp_lst[0].days[i1].date),
                    # ~ ', weekday:', emp_lst[0].days[i1].weekday,
                    # ~ ', week:', emp_lst[0].days[i1].week,
                    # ~ ', startpos:', str(emp_lst[0].days[i1].startpos),
                    # ~ ', endpos:', str(emp_lst[0].days[i1].endpos),
                    # ~ ', sumact:', str(emp_lst[0].days[i1].sumact),
                    # ~ ', targettime:', str(emp_lst[0].days[i1].targettime),
                    # ~ ', duration:',str(emp_lst[0].days[i1].duration),
                    # ~ ', diff:',str(emp_lst[0].days[i1].diff),
                    # ~ ', wobreaks:', str(emp_lst[0].days[i1].wobreaks),
                    # ~ ', breaktime:',str(emp_lst[0].days[i1].breaktime),
                    # ~ ', holiday_ena:',emp_lst[0].days[i1].holiday_ena,
                    # ~ ', holidayname:',emp_lst[0].days[i1].holidayname,
                    # ~ ', daytype:',emp_lst[0].days[i1].daytype,
                    # ~ ', accountitem:',str(emp_lst[0].days[i1].accountitem),
                    # ~ ', accountitems_nonmain:',str(emp_lst[0].days[i1].accountitems_nonmain),
                    # ~ ', info:',emp_lst[0].days[i1].info,
                    # ~ )

                self.assertEqual(str(emp_lst[0].days[i1].date), date1)
                self.assertEqual(emp_lst[0].days[i1].weekday, wd1)
                self.assertEqual(emp_lst[0].days[i1].week, wk1)
                self.assertEqual(str(emp_lst[0].days[i1].startpos), sp1)
                self.assertEqual(str(emp_lst[0].days[i1].endpos), ep1)
                self.assertEqual(str(emp_lst[0].days[i1].sumact), sa1)
                self.assertEqual(str(emp_lst[0].days[i1].targettime), tt1)
                self.assertEqual(str(emp_lst[0].days[i1].duration), dur1)
                self.assertEqual(str(emp_lst[0].days[i1].diff), df1)
                self.assertEqual(str(emp_lst[0].days[i1].wobreaks), wobr)
                self.assertEqual(str(emp_lst[0].days[i1].breaktime), brtm)
                self.assertEqual(emp_lst[0].days[i1].holiday_ena, he1)
                self.assertEqual(emp_lst[0].days[i1].holidayname, hn1)
                self.assertEqual(emp_lst[0].days[i1].daytype, dt1)
                self.assertEqual(str(emp_lst[0].days[i1].accountitem), acc1)
                self.assertEqual(str(emp_lst[0].days[i1].accountitems_nonmain), acn1)
                self.assertEqual(emp_lst[0].days[i1].info, inf1)

    @with_transaction()
    def test_evaluation_worktimerule(self):
        """ test: create company/employees/worktimemodel/evaluation, check local copy of worktimemodel
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')

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

            # evaluation has local copy of work time rules
            self.assertEqual(len(ev1.worktimerule), 1)
            self.assertEqual(ev1.worktimerule[0].rec_name, '08:00-16:00 [xxxxx__]')
            
            # edit worktime model, must update the local copy
            self.assertEqual(wtm_obj.worktimerule[0].rec_name, 'WTR1 - 08:00-16:00 [xxxxx__]')
            wtm_obj.worktimerule[0].mintime = time(7, 0)
            wtm_obj.worktimerule[0].save()
            self.assertEqual(wtm_obj.worktimerule[0].rec_name, 'WTR1 - 07:00-16:00 [xxxxx__]')
            
            # new value should appear in local copy
            self.assertEqual(ev1.worktimerule[0].rec_name, '07:00-16:00 [xxxxx__]')

            # lock evaluation
            Evaluation.wflock([ev1])
            self.assertEqual(ev1.state, 'l')

            # edit again
            self.assertEqual(wtm_obj.worktimerule[0].rec_name, 'WTR1 - 07:00-16:00 [xxxxx__]')
            wtm_obj.worktimerule[0].mintime = time(7, 30)
            wtm_obj.worktimerule[0].save()
            self.assertEqual(wtm_obj.worktimerule[0].rec_name, 'WTR1 - 07:30-16:00 [xxxxx__]')

            # evaluation ist locked: no update in local copy
            self.assertEqual(ev1.worktimerule[0].rec_name, '07:00-16:00 [xxxxx__]')

            # unlock evaluation
            Evaluation.wfcreate([ev1])
            self.assertEqual(ev1.state, 'c')
            Evaluation.wfactivate([ev1])
            self.assertEqual(ev1.state, 'a')

            # add a 2nd work time model
            wtm_obj2 = create_worktime_full(tarobj1.company, 'work day 2', 'WT2', 
                [
                    {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':False, 
                     'fri':True, 'sat':False, 'sun':False, 'mintime':time(6,0), 'maxtime':time(15, 0)},
                ])
            employee1.worktime = wtm_obj2
            employee1.save()    # <-- trigger update

            # check update in local copy
            self.assertEqual(ev1.worktimerule[0].rec_name, '06:00-15:00 [xxx_x__]')

    @with_transaction()
    def test_evaluation_breaktimerule(self):
        """ test: create company/employees/breaktimemodel/evaluation, check local copy of breaktimerule
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')

        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name': '4h - 6h', 'shortname': '6h', 
                        'mint': timedelta(seconds=4*3600),
                        'maxt': timedelta(seconds=5*3600 + 59*60 + 59),
                        'dedu': timedelta(seconds=20*60),
                        },
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
        
            ev1 = Evaluation()
            ev1.employee = employee1
            ev1.evaldate = date(2018, 4, 18)
            ev1.save()
            self.assertEqual(ev1.rec_name, 'Frida - 2018-04')
            self.assertEqual(ev1.state, 'c')
            Evaluation.wfactivate([ev1])
            self.assertEqual(ev1.state, 'a')

            # evaluation has local copy of break time rules
            self.assertEqual(len(ev1.breaktimerule), 1)
            self.assertEqual(ev1.breaktimerule[0].rec_name, 'Frida - 2018-04: 04:00-05:59 -> 00h20')
            
            # edit breaktime, must update the local copy
            self.assertEqual(tarobj1.breaktime[0].rec_name, '[Tariff1] 6h: 04:00-05:59 -> 00h20')
            tarobj1.breaktime[0].mintime = timedelta(seconds=4*3600 + 10*60)
            tarobj1.breaktime[0].save()
            self.assertEqual(tarobj1.breaktime[0].rec_name, '[Tariff1] 6h: 04:10-05:59 -> 00h20')
            
            # new value should appear in local copy
            self.assertEqual(ev1.breaktimerule[0].rec_name, 'Frida - 2018-04: 04:10-05:59 -> 00h20')

            # lock evaluation
            Evaluation.wflock([ev1])
            self.assertEqual(ev1.state, 'l')

            # edit again
            self.assertEqual(tarobj1.breaktime[0].rec_name, '[Tariff1] 6h: 04:10-05:59 -> 00h20')
            tarobj1.breaktime[0].mintime = timedelta(seconds=4*3600 + 15*60)
            tarobj1.breaktime[0].save()
            self.assertEqual(tarobj1.breaktime[0].rec_name, '[Tariff1] 6h: 04:15-05:59 -> 00h20')

            # evaluation ist locked: no update in local copy
            self.assertEqual(ev1.breaktimerule[0].rec_name, 'Frida - 2018-04: 04:10-05:59 -> 00h20')

            # unlock evaluation
            Evaluation.wfcreate([ev1])
            self.assertEqual(ev1.state, 'c')
            Evaluation.wfactivate([ev1])
            self.assertEqual(ev1.state, 'a')

            # add a 2nd tariff model
            tarobj2 = create_tariff(name='Tariff2', shortname='T2', company=tarobj1.company)
            brt1 = create_breaktime(name='5h - 7h', shortname='5h', 
                        mintime=timedelta(seconds=5*3600), 
                        maxtime=timedelta(seconds=7*3600 + 59*60 + 59), \
                        deduction=timedelta(seconds=30*60), 
                        tariff=tarobj2)
            self.assertTrue(tarobj2)

            employee1.tariff = tarobj2
            employee1.save()    # <-- trigger update

            # check update in local copy
            self.assertEqual(ev1.breaktimerule[0].rec_name, 'Frida - 2018-04: 05:00-07:59 -> 00h30')

    @with_transaction()
    def test_evaluation_vacation_days(self):
        """ test: create company/employee/vacantion days, check sum per year
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        Period = pool.get('employee_timetracking.period')
        Holiday = pool.get('employee_timetracking.holiday')
        VacationDays = pool.get('employee_timetracking.evaluation_vacationdays')
        Employee = pool.get('company.employee')
        Event = pool.get('pim_calendar.event')
        Calendar = pool.get('pim_calendar.calendar')

        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                    ],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                    ],
                accountrules=[
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                type_work = 'Work', main_account='Work',
            )
        self.assertTrue(tarobj1)
        
        wtm_obj = create_worktime_full(tarobj1.company, 'work day', 'WT1', 
            [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
            ])
        
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()
        
        # create tryton-user + calendar
        usr1 = create_trytonuser('frida', 'Test.1234')
        usr1.main_company = tarobj1.company
        usr1.company = tarobj1.company
        usr1.save()
        self.assertTrue(usr1)
        self.assertEqual(usr1.name, 'frida')
        
        # holidays
        create_holiday('winter, half day', date(2018, 12, 24), company=tarobj1.company, repyear=False, halfday=True)  # mon - 2018
        create_holiday('winter, full day', date(2018, 12, 25), company=tarobj1.company, repyear=False, halfday=False) # tue - 2018
        create_holiday('half day 2019', date(2019, 4, 2), company=tarobj1.company, repyear=False, halfday=True)  # tue - 2019
        create_holiday('full day 2019', date(2019, 4, 4), company=tarobj1.company, repyear=False, halfday=False) # thu - 2019
        create_holiday('at saturday',          date(2019, 4, 6), company=tarobj1.company, repyear=False, halfday=False)
        self.assertEqual(len(Holiday.search([('company', '=', tarobj1.company)])), 5)

        with set_company(tarobj1.company):            
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.worktime = wtm_obj
            employee1.holidays = 22
            employee1.specleave = 3     # employee has 3 additional vacation days
            employee1.start_date = date(2017, 1, 1)
            employee1.save()
            
            # connect employee and tryton-user
            usr1.employees = [employee1]
            usr1.employee = employee1
            usr1.save()
            self.assertEqual(employee1.trytonuser.name, 'frida')

            # add calendar
            cal1 = Calendar(
                    name='Cal1',
                    owner=employee1.trytonuser,
                    allday_events = True,
                )
            cal1.save()
            cal_lst = Calendar.search([])
            self.assertEqual(len(cal_lst), 1)
            employee1.calendar = cal_lst[0]
            employee1.save()

            self.assertEqual(cal_lst[0].name, 'Cal1')
            self.assertEqual(cal_lst[0].owner.rec_name, 'frida')
            self.assertEqual(employee1.calendar.rec_name, 'Cal1 (frida)')

            e_lst = Employee.search([]) # find all
            self.assertEqual(len(e_lst), 1)
            
            self.assertEqual(e_lst[0].tariff.name, 'Tariff1')
            self.assertEqual(e_lst[0].worktime.name, 'work day')
            self.assertEqual(e_lst[0].holidays, 22)
            self.assertEqual(e_lst[0].specleave, 3)
            self.assertEqual(str(e_lst[0].start_date), '2017-01-01')
            
            # vacation days in 2018
            # uses 10 of 22+3 vacation days
            ev1 = Event(name='Holiday 2018', 
                    startpos = datetime(2018, 3, 26), 
                    endpos = datetime(2018, 4, 6),
                    wholeday = True)
            ev1.save()
            # uses: 5, remain: 7+3
            ev2 = Event(name='Summer 2018', 
                    startpos = datetime(2018, 7, 16), 
                    endpos = datetime(2018, 7, 20),
                    wholeday = True)
            ev2.save()
            # uses: 1 (24.12.) + 3 (26.12. - 28.12.) + 1 (31.12.)
            # remain: 2 + 3
            ev3 = Event(name='Winter 2018', 
                    startpos = datetime(2018, 12, 24), 
                    endpos = datetime(2018, 12, 31),
                    wholeday = True)
            ev3.save()
            # check result
            ev_lst = Event.search([], order=[('startpos', 'ASC')])
            self.assertEqual(len(ev_lst), 3)
            self.assertEqual(ev_lst[0].rec_name, 'Holiday 2018 - 26.03.2018 00:00 - 06.04.2018 00:00 (Cal1 (frida))')
            self.assertEqual(ev_lst[1].rec_name, 'Summer 2018 - 16.07.2018 00:00 - 20.07.2018 00:00 (Cal1 (frida))')
            self.assertEqual(ev_lst[2].rec_name, 'Winter 2018 - 24.12.2018 00:00 - 31.12.2018 00:00 (Cal1 (frida))')

            # create 12x evaluations in 2018
            for i in range(12):
                create_evaluation(employee1, date(2018, i + 1, 2))
            
            eval_lst = Evaluation.search([], order=[('evaldate', 'ASC')])
            self.assertEqual(len(eval_lst), 12)

            l1 = [('2018-01-01', 0, 0, 25), ('2018-02-01', 0, 0, 25), ('2018-03-01', 0, 0, 25), 
                ('2018-04-01', 0, 0, 25),   ('2018-05-01', 0, 0, 25), ('2018-06-01', 0, 0, 25), 
                ('2018-07-01', 0, 0, 25),   ('2018-08-01', 0, 0, 25), ('2018-09-01', 0, 0, 25), 
                ('2018-10-01', 0, 0, 25),   ('2018-11-01', 0, 0, 25), ('2018-12-01', 0, 0, 25), 
                ]

            for i in range(12):
                self.assertEqual(str(eval_lst[i].evaldate), l1[i][0])
                self.assertEqual(len(eval_lst[i].vacationdays), l1[i][1])
                self.assertEqual(eval_lst[i].vacationdays_taken, l1[i][2])
                self.assertEqual(eval_lst[i].vacationdays_remain, l1[i][3])

            # create vacation days from calendar
            for i in range(12):
                VacationDays.updt_days_from_calendar(eval_lst[i])
                
            l1 = [('2018-01-01', 0, 0, 25), ('2018-02-01', 0, 0, 25),  ('2018-03-01', 1, 5, 20), 
                ('2018-04-01', 1, 5, 15), ('2018-05-01', 0, 0, 15), ('2018-06-01', 0, 0, 15), 
                ('2018-07-01', 1, 5, 10),  ('2018-08-01', 0, 0, 10),  ('2018-09-01', 0, 0, 10), 
                ('2018-10-01', 0, 0, 10),  ('2018-11-01', 0, 0, 10),  ('2018-12-01', 1, 5, 5), 
                ]

            for i in range(12):
                self.assertEqual(str(eval_lst[i].evaldate), l1[i][0])
                self.assertEqual(len(eval_lst[i].vacationdays), l1[i][1])
                self.assertEqual(eval_lst[i].vacationdays_taken, l1[i][2])
                self.assertEqual(eval_lst[i].vacationdays_remain, l1[i][3])

            # check vacation days in next year
            create_evaluation(employee1, date(2019, 1, 1))
            eval_lst2 = Evaluation.search([
                    ('evaldate', '>=', date(2019, 1, 1)),
                    ('evaldate', '<=', date(2019, 12, 31)),
                    ])
            self.assertEqual(len(eval_lst2), 1)
            self.assertEqual(eval_lst2[0].vacationdays_taken, 0)
            self.assertEqual(eval_lst2[0].vacationdays_remain, 25)
            
# end EvaluationTestCase
