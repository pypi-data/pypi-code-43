# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.company.tests import create_company, set_company
from trytond.exceptions import UserError
from trytond import backend
from datetime import time, datetime, date
from decimal import Decimal
from trytond.modules.employee_timetracking.tests.testlib import create_tariff_full, \
    create_employee, create_accountrule, create_timeaccount, create_period,\
    create_presence, create_tariff
from trytond.modules.employee_timetracking.const import ACRULE_HOLIDAY_AT, \
    ACRULE_HOLIDAY_NOTAT, ACRULE_HOLIDAY_NODEF


class AccountRuleTestCase(ModuleTestCase):
    'Test accountrule module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_accountrule_create_item(self):
        """ test: create valid accountrule item using defaults
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create accountrule
            AccountRule = Pool().get('employee_timetracking.accountrule')
            ta1 = create_timeaccount(name='Work', shortname='W', company=company)
            pr1 = create_presence(name='Work', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')
            
            accrule = create_accountrule(name='8-16', shortname='W1', \
                            mintime=time(8, 0, 23),
                            maxtime=time(16, 0, 42),
                            factor=AccountRule.default_factor(),
                            mon=AccountRule.default_mon(),
                            tue=AccountRule.default_tue(),
                            wed=AccountRule.default_wed(),
                            thu=AccountRule.default_thu(),
                            fri=AccountRule.default_fri(),
                            sat=AccountRule.default_sat(),
                            sun=AccountRule.default_sun(),
                            account=ta1, presence=pr1,
                            tariff=tar1)
            
            # check values
            self.assertTrue(accrule)
            self.assertEqual(accrule.name, '8-16')
            self.assertEqual(accrule.shortname, 'W1')
            self.assertEqual(str(accrule.mintime), '08:00:00')
            self.assertEqual(str(accrule.maxtime), '16:00:00')
            self.assertEqual(str(accrule.factor), '1.0')
            self.assertEqual(str(accrule.mon), 'True')
            self.assertEqual(str(accrule.tue), 'True')
            self.assertEqual(str(accrule.wed), 'True')
            self.assertEqual(str(accrule.thu), 'True')
            self.assertEqual(str(accrule.fri), 'True')
            self.assertEqual(str(accrule.sat), 'False')
            self.assertEqual(str(accrule.sun), 'False')
            
            # edit min/max
            accrule.mintime = time(8, 0, 33)
            accrule.maxtime = time(16, 0, 54)
            accrule.save()
            self.assertEqual(str(accrule.mintime), '08:00:00')
            self.assertEqual(str(accrule.maxtime), '16:00:00')
            
            # field 'company'
            self.assertEqual(accrule.company.id, company.id)
            self.assertEqual(accrule.company.rec_name, 'm-ds 1')
            l1 = AccountRule.search([('company', '=', company.id)])
            self.assertEqual(len(l1), 1)
            self.assertEqual(l1[0].company.rec_name, 'm-ds 1')

    @with_transaction()
    def test_accountrule_create_item_no_weekdays(self):
        """ test: create accountrule item without active weekdays - will except
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            ta1 = create_timeaccount(name='Worktime', shortname='WT1', company=company)
            p1 = create_presence(name='Work 1', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')
                
            # create accountrule
            AccountRule = Pool().get('employee_timetracking.accountrule')
            ar_obj = AccountRule(
                    name='8-16',
                    shortname='W1',
                    tariff=tar1,
                    mon=False, tue=False, wed=False, thu=False,
                    fri=False, sat=False, sun=False,
                    mintime=AccountRule.default_mintime(),
                    maxtime=AccountRule.default_maxtime(), 
                    factor=AccountRule.default_factor(),
                    account=ta1,
                    presence=p1,
                )
            self.assertRaisesRegex(UserError, 
                "at least one weekday must be activated",
                ar_obj.save)

    @with_transaction()
    def test_accountrule_create_item_time_order(self):
        """ test: create accountrule item with maxtime < mintime - will except
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            ta1 = create_timeaccount(name='Worktime', shortname='WT1', company=company)
            p1 = create_presence(name='Work 1', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')
            
            # create accountrule
            AccountRule = Pool().get('employee_timetracking.accountrule')
            ar_obj = AccountRule(
                    name='16-8', shortname='W1', 
                    tariff=tar1,
                    mon=True, tue=False, wed=False, thu=False,
                    fri=False, sat=False, sun=False,
                    mintime=time(16, 0),
                    maxtime=time(8, 0),
                    factor=AccountRule.default_factor(),
                    account=ta1,
                    presence=p1,
                )
            self.assertRaisesRegex(UserError, 
                "'to' must be creater than 'from'",
                ar_obj.save)

    @with_transaction()
    def test_accountrule_create_item_time_equal(self):
        """ test: create accountrule item with maxtime == mintime - will except
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            ta1 = create_timeaccount(name='Worktime', shortname='WT1', company=company)
            p1 = create_presence(name='Work 1', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')

            # create accountrule
            AccountRule = Pool().get('employee_timetracking.accountrule')
            ar_obj = AccountRule(
                    name='10-10', shortname='W1', 
                    tariff=tar1,
                    mon=True, tue=False, wed=False, thu=False,
                    fri=False, sat=False, sun=False,
                    mintime=time(10, 0),
                    maxtime=time(10, 0),
                    factor=AccountRule.default_factor(),
                    account=ta1,
                    presence=p1,
                )
            self.assertRaisesRegex(UserError, 
                "'to' must be creater than 'from'",
                ar_obj.save)

    @with_transaction()
    def test_accountrule_create_item_factor_null(self):
        """ test: create accountrule item with factor == 0 - will except
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create accountrule
            AccountRule = Pool().get('employee_timetracking.accountrule')
            ta1 = create_timeaccount(name='Work', shortname='W', company=company)
            pr1 = create_presence(name='Work', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')
            
            # allowed: +/-
            self.assertTrue(create_accountrule(
                            name='8-16 + 0.5', shortname='W1a', \
                            mintime=time(8, 0),
                            maxtime=time(16, 0),
                            factor=Decimal('0.5'),
                            mon=True, tue=False, wed=False, thu=False,
                            fri=False, sat=False, sun=False,
                            account=ta1, presence=pr1,
                            tariff=tar1))
            self.assertTrue(create_accountrule(
                            name='8-16 - 0.5', shortname='W1b', \
                            mintime=time(8, 0),
                            maxtime=time(16, 0),
                            factor=-Decimal('0.5'),
                            mon=True, tue=False, wed=False, thu=False,
                            fri=False, sat=False, sun=False,
                            account=ta1, presence=pr1,
                            tariff=tar1))
            # not allowed: 0
            ar_obj = AccountRule(
                    name='8-16', shortname='W1', 
                    tariff=tar1,
                    mon=True, tue=False, wed=False, thu=False,
                    fri=False, sat=False, sun=False,
                    mintime=time(8, 0),
                    maxtime=time(16, 0),
                    factor=Decimal('0.0'),
                    account=ta1,
                    presence=pr1,
                )
            self.assertRaisesRegex(UserError, 
                "Factor can not be zero.",
                ar_obj.save)

    @with_transaction()
    def test_accountrule_create_item_twice_name(self):
        """ test: create accountrule item twice - same name - will except
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create accountrule
            AccountRule = Pool().get('employee_timetracking.accountrule')
            ta1 = create_timeaccount(name='Work', shortname='W', company=company)
            pr1 = create_presence(name='Work', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')
            
            self.assertTrue(create_accountrule(name='8-16', shortname='W1', \
                    mintime=time(8, 0), maxtime=time(16, 0),
                    factor=Decimal('1.0'),
                    mon=True, tue=False, wed=False, thu=False,
                    fri=False, sat=False, sun=False,
                    tariff=tar1,
                    account=ta1, presence=pr1
                    ))

            ar_obj = AccountRule(
                    name='8-16', shortname='W1a', 
                    tariff=tar1,
                    mon=True, tue=False, wed=False, thu=False,
                    fri=False, sat=False, sun=False,
                    mintime=time(8, 0), maxtime=time(16, 0),
                    factor=Decimal('1.0'),
                    account=ta1, presence=pr1
                )
            self.assertRaisesRegex(UserError, 
                "This name is already in use.",
                ar_obj.save)

    @with_transaction()
    def test_accountrule_create_item_twice_shortname(self):
        """ test: create accountrule item twice - same shortname - will except
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create accountrule
            AccountRule = Pool().get('employee_timetracking.accountrule')
            ta1 = create_timeaccount(name='Work', shortname='W', company=company)
            pr1 = create_presence(name='Work', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')
            
            self.assertTrue(create_accountrule(name='8-16', shortname='W1', \
                            mintime=time(8, 0), maxtime=time(16, 0),
                            factor=Decimal('1.0'),
                            mon=True, tue=False, wed=False, thu=False,
                            fri=False, sat=False, sun=False,
                            tariff=tar1,
                            account=ta1, presence=pr1
                            ))
            ar_obj = AccountRule(
                    name='8-16 a', shortname='W1', 
                    tariff=tar1,
                    mon=True, tue=False, wed=False, thu=False,
                    fri=False, sat=False, sun=False,
                    mintime=time(8, 0), maxtime=time(16, 0),
                    factor=Decimal('1.0'),
                    account=ta1, presence=pr1
                )
            self.assertRaisesRegex(UserError, 
                "This shorthand symbol is already in use.",
                ar_obj.save)

    @with_transaction()
    def test_accountrule_get_utctime(self):
        """ test: get UTC time from datetime in localtime
        """
        AccountRule = Pool().get('employee_timetracking.accountrule')
        
        # CET --> UTC
        dt1_cet = datetime(2018, 3, 15, 10, 0, 0)
        self.assertEqual(str(dt1_cet), '2018-03-15 10:00:00')
        dt_utc = AccountRule.get_utctime(dt1_cet, 'Europe/Berlin')
        self.assertEqual(str(dt_utc), '2018-03-15 09:00:00')

        # CEST --> UTC
        dt1_cest = datetime(2018, 3, 29, 12, 0, 0)
        self.assertEqual(str(dt1_cest), '2018-03-29 12:00:00')
        dt_utc = AccountRule.get_utctime(dt1_cest, 'Europe/Berlin')
        self.assertEqual(str(dt_utc), '2018-03-29 10:00:00')

        # CEST --> UTC, date change at midnight
        dt1_cest = datetime(2018, 3, 30, 1, 0, 0)
        self.assertEqual(str(dt1_cest), '2018-03-30 01:00:00')
        dt_utc = AccountRule.get_utctime(dt1_cest, 'Europe/Berlin')
        self.assertEqual(str(dt_utc), '2018-03-29 23:00:00')

        # Canada/Atlantic --> UTC
        dt_can = datetime(2018, 3, 25, 7, 0, 0)
        self.assertEqual(str(dt_can), '2018-03-25 07:00:00')
        dt_utc = AccountRule.get_utctime(dt_can, 'Canada/Atlantic')
        self.assertEqual(str(dt_utc), '2018-03-25 10:00:00')

    @with_transaction()
    def test_accountrule_get_localtime(self):
        """ test: get local time from datetime in UTC
        """
        AccountRule = Pool().get('employee_timetracking.accountrule')
        
        # UTC --> CET
        dt1 = datetime(2018, 3, 15, 10, 0, 0)
        self.assertEqual(str(dt1), '2018-03-15 10:00:00')
        dt_cet = AccountRule.get_localtime(dt1, 'Europe/Berlin')
        self.assertEqual(str(dt_cet), '2018-03-15 11:00:00')

        # UTC --> CEST
        dt1 = datetime(2018, 3, 29, 10, 0, 0)
        self.assertEqual(str(dt1), '2018-03-29 10:00:00')
        dt_cest = AccountRule.get_localtime(dt1, 'Europe/Berlin')
        self.assertEqual(str(dt_cest), '2018-03-29 12:00:00')

        # UTC --> CEST, date change at midnight
        dt1 = datetime(2018, 3, 29, 23, 0, 0)
        self.assertEqual(str(dt1), '2018-03-29 23:00:00')
        dt_cest = AccountRule.get_localtime(dt1, 'Europe/Berlin')
        self.assertEqual(str(dt_cest), '2018-03-30 01:00:00')

        # UTC --> Canada/Atlantic
        dt1 = datetime(2018, 3, 25, 10, 0, 0)
        self.assertEqual(str(dt1), '2018-03-25 10:00:00')
        dt_can = AccountRule.get_localtime(dt1, 'Canada/Atlantic')
        self.assertEqual(str(dt_can), '2018-03-25 07:00:00')

    @with_transaction()
    def test_accountrule_match_holiday_rule(self):
        """ test: define holidays, test if date matches
        """
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create accountrule
            pool = Pool()
            AccountRule = pool.get('employee_timetracking.accountrule')
            Holiday = pool.get('employee_timetracking.holiday')
            
            ta1 = create_timeaccount(name='Work', shortname='W', company=company)
            pr1 = create_presence(name='Work', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')
            
            h1 = Holiday(name = 'Mayday', date = date(2018, 5, 1),
                repyear = True, halfday = False, company = company)
            h1.save()

            # sunday
            h2 = Holiday(name = '1. Sept', date = date(2019, 9, 1),
                repyear = False, halfday = False, company = company)
            h2.save()
            
            accrule = create_accountrule(name='8-16', shortname='W1', \
                            mintime=AccountRule.default_mintime(),
                            maxtime=AccountRule.default_maxtime(),
                            factor=AccountRule.default_factor(),
                            mon=True,
                            tue=True,
                            wed=False,
                            thu=False,
                            fri=False,
                            sat=True,
                            sun=True,
                            holiday=ACRULE_HOLIDAY_NODEF,
                            tariff=tar1,
                            account=ta1,
                            presence=pr1,
                            )
                            
            # not def --> True
            dt1 = datetime(2019, 9, 2, 10, 0)  # monday
            self.assertTrue(AccountRule.match_holiday_rule(accrule, dt1))

            accrule.holiday = ACRULE_HOLIDAY_AT
            self.assertEqual(accrule.holiday, 'a')
            accrule.save()

            dt2 = datetime(2019, 9, 2, 10, 0)  # monday
            dt3 = datetime(2019, 9, 1, 10, 0)  # sunday

            self.assertFalse(AccountRule.match_holiday_rule(accrule, dt2))
            self.assertTrue(AccountRule.match_holiday_rule(accrule, dt3))

            accrule.holiday = ACRULE_HOLIDAY_NOTAT
            self.assertEqual(accrule.holiday, 'n')
            accrule.save()

            self.assertTrue(AccountRule.match_holiday_rule(accrule, dt2))
            self.assertFalse(AccountRule.match_holiday_rule(accrule, dt3))

    @with_transaction()
    def test_accountrule_is_in_weekdays(self):
        """ test: check function 'is_in_weekdays'
        """
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create accountrule
            AccountRule = Pool().get('employee_timetracking.accountrule')
            ta1 = create_timeaccount(name='Work', shortname='W', company=company)
            pr1 = create_presence(name='Work', shortname='W1', company=company)
            tar1 = create_tariff(name='Tariff 1', shortname='T1')
            
            accrule = create_accountrule(name='8-16', shortname='W1', \
                            mintime=AccountRule.default_mintime(),
                            maxtime=AccountRule.default_maxtime(),
                            factor=AccountRule.default_factor(),
                            mon=True,
                            tue=True,
                            wed=False,
                            thu=False,
                            fri=False,
                            sat=True,
                            sun=True,
                            tariff=tar1,
                            account=ta1,
                            presence=pr1,
                            )
            dt1 = datetime(2018, 3, 26, 10, 0)  # monday
            self.assertTrue(AccountRule.is_in_weekdays(accrule, dt1))
            dt1 = datetime(2018, 3, 27, 10, 0)  # tuesday
            self.assertTrue(AccountRule.is_in_weekdays(accrule, dt1))
            dt1 = datetime(2018, 3, 28, 10, 0)  # wednesday
            self.assertFalse(AccountRule.is_in_weekdays(accrule, dt1))
            dt1 = datetime(2018, 3, 29, 10, 0)  # thursday
            self.assertFalse(AccountRule.is_in_weekdays(accrule, dt1))
            dt1 = datetime(2018, 3, 30, 10, 0)  # friday
            self.assertFalse(AccountRule.is_in_weekdays(accrule, dt1))
            dt1 = datetime(2018, 3, 31, 10, 0)  # saturday
            self.assertTrue(AccountRule.is_in_weekdays(accrule, dt1))
            dt1 = datetime(2018, 4, 1, 10, 0)  # sunday
            self.assertTrue(AccountRule.is_in_weekdays(accrule, dt1))

    @with_transaction()
    def test_accountrule_optimize_items2create(self):
        """ test: reduce list of start/end-pairs
        """
        AccountRule = Pool().get('employee_timetracking.accountrule')

        # with gaps, no optimize possible
        l1 = [
                (datetime(2018, 3, 25,  8,  0, 0), datetime(2018, 3, 25, 10, 15, 0)),
                (datetime(2018, 3, 25, 10, 20, 0), datetime(2018, 3, 25, 10, 25, 0)),
                (datetime(2018, 3, 25, 10, 30, 0), datetime(2018, 3, 25, 10, 25, 0)),
            ]
        l2 = AccountRule.optimize_items2create(l1, 'Europe/Berlin')
        self.assertEqual(l1, l2)
        
        # 1, 2, 3 --> 1, 2+3
        l1 = [
                (datetime(2018, 3, 25,  8,  0, 0), datetime(2018, 3, 25, 10, 15, 0)),
                (datetime(2018, 3, 25, 10, 20, 0), datetime(2018, 3, 25, 10, 25, 0)),
                (datetime(2018, 3, 25, 10, 25, 0), datetime(2018, 3, 25, 10, 30, 0)),
            ]
        l2 = AccountRule.optimize_items2create(l1, 'Europe/Berlin')
        self.assertEqual(len(l2), 2)
        self.assertEqual(type(l2[0]), type((1,2)))
        self.assertEqual(str(l2[0][0]), '2018-03-25 08:00:00')
        self.assertEqual(str(l2[0][1]), '2018-03-25 10:15:00')
        self.assertEqual(type(l2[1]), type((1,2)))
        self.assertEqual(str(l2[1][0]), '2018-03-25 10:20:00')
        self.assertEqual(str(l2[1][1]), '2018-03-25 10:30:00')

        # 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 --> 1, 2+3, 4+5, 6, 7+8+9, 10+11, 12, 13
        l1 = [
                (datetime(2018, 3, 25,  8,  0, 0), datetime(2018, 3, 25, 10, 14, 59)),  # 1 sec gap
                (datetime(2018, 3, 25, 10, 15, 0), datetime(2018, 3, 25, 10, 25, 0)),
                (datetime(2018, 3, 25, 10, 25, 0), datetime(2018, 3, 25, 10, 30, 0)),
                (datetime(2018, 3, 25, 11, 15, 0), datetime(2018, 3, 25, 11, 25, 0)),
                (datetime(2018, 3, 25, 11, 25, 0), datetime(2018, 3, 25, 11, 30, 0)),
                (datetime(2018, 3, 25, 11, 30, 2), datetime(2018, 3, 25, 11, 32, 45)),
                (datetime(2018, 3, 25, 12, 5, 0), datetime(2018, 3, 25, 12, 10, 0)),
                (datetime(2018, 3, 25, 12, 10, 0), datetime(2018, 3, 25, 12, 15, 0)),
                (datetime(2018, 3, 25, 12, 15, 0), datetime(2018, 3, 25, 12, 19, 45)),
                # don't connect at midnight within same month - time in UTC, local time: 'Europe/Berlin'
                (datetime(2018, 3, 26, 21, 10, 0), datetime(2018, 3, 26, 22, 0, 0)),
                (datetime(2018, 3, 26, 22, 0, 0), datetime(2018, 3, 27, 1, 0, 0)),
                # don't connect at midnight at end of month UTC / CEST
                (datetime(2018, 3, 31, 21, 10, 0), datetime(2018, 3, 31, 22, 0, 0)),
                (datetime(2018, 3, 31, 22, 0, 0), datetime(2018, 4, 1, 1, 0, 0)),
            ]
        l2 = AccountRule.optimize_items2create(l1, 'Europe/Berlin')
        self.assertEqual(len(l2), 9)
        self.assertEqual(type(l2[0]), type((1,2)))
        self.assertEqual(str(l2[0][0]), '2018-03-25 08:00:00')
        self.assertEqual(str(l2[0][1]), '2018-03-25 10:14:59')
        self.assertEqual(type(l2[1]), type((1,2)))
        self.assertEqual(str(l2[1][0]), '2018-03-25 10:15:00')
        self.assertEqual(str(l2[1][1]), '2018-03-25 10:30:00')
        self.assertEqual(type(l2[2]), type((1,2)))
        self.assertEqual(str(l2[2][0]), '2018-03-25 11:15:00')
        self.assertEqual(str(l2[2][1]), '2018-03-25 11:30:00')
        self.assertEqual(type(l2[3]), type((1,2)))
        self.assertEqual(str(l2[3][0]), '2018-03-25 11:30:02')
        self.assertEqual(str(l2[3][1]), '2018-03-25 11:32:45')
        self.assertEqual(type(l2[4]), type((1,2)))
        self.assertEqual(str(l2[4][0]), '2018-03-25 12:05:00')
        self.assertEqual(str(l2[4][1]), '2018-03-25 12:19:45')
        self.assertEqual(type(l2[5]), type((1,2)))
        self.assertEqual(str(l2[5][0]), '2018-03-26 21:10:00')
        self.assertEqual(str(l2[5][1]), '2018-03-26 22:00:00')
        self.assertEqual(type(l2[6]), type((1,2)))
        self.assertEqual(str(l2[6][0]), '2018-03-26 22:00:00')
        self.assertEqual(str(l2[6][1]), '2018-03-27 01:00:00')
        self.assertEqual(type(l2[7]), type((1,2)))
        self.assertEqual(str(l2[7][0]), '2018-03-31 21:10:00')
        self.assertEqual(str(l2[7][1]), '2018-03-31 22:00:00')
        self.assertEqual(type(l2[8]), type((1,2)))
        self.assertEqual(str(l2[8][0]), '2018-03-31 22:00:00')
        self.assertEqual(str(l2[8][1]), '2018-04-01 01:00:00')

    @with_transaction()
    def test_accountrule_get_periods_to_check_by_rule(self):
        """ test: check function 'get_periods_to_check_by_rule'
        """
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name': 'Work', 'shortname':'W'},
                        {'name': 'Work night', 'shortname':'WN'},
                        {'name': 'Work late', 'shortname':'WL'},
                    ],
                accountrules=[
                        {'name':'Work 0-7', 'shortname':'W0', 
                         'mint':time(0, 0), 'maxt':time(7, 0, ), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
                        {'name':'Work 7-12', 'shortname':'W1', 
                         'mint':time(7, 0), 'maxt':time(12, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 12-19', 'shortname':'W2', 
                         'mint':time(12, 0), 'maxt':time(19, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'
        tarobj1.company.save()

        with set_company(tarobj1.company):
            AccountRule = Pool().get('employee_timetracking.accountrule')
            Holiday = Pool().get('employee_timetracking.holiday')

            # add holiday 
            h1 = Holiday(name='27.3.2018', date=date(2018, 3, 27), repyear=False, halfday=False, company=tarobj1.company)
            h1.save()
            
            acc_lst = sorted(tarobj1.accountrule, key=lambda t1: t1.mintime)
            self.assertEqual(acc_lst[1].name, 'Work 7-12')
            # get list of periods to check
            l1 = AccountRule.get_periods_to_check_by_rule(
                        acc_lst[1], 
                        datetime(2018, 3, 26, 8, 0),
                        datetime(2018, 3, 26, 11, 30)
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(str(l1[0][0]), '2018-03-26 07:00:00')
            self.assertEqual(str(l1[0][1]), '2018-03-26 12:00:00')
            
            # rule not active at thursday
            l1 = AccountRule.get_periods_to_check_by_rule(
                        acc_lst[1], 
                        datetime(2018, 3, 29, 8, 0),
                        datetime(2018, 3, 29, 11, 30)
                    )
            self.assertEqual(len(l1), 0)
        
            # worktime runs a few days, sunday --> friday
            # rule active at 4 days
            l1 = AccountRule.get_periods_to_check_by_rule(
                        acc_lst[1], 
                        datetime(2018, 3, 25, 8, 0),
                        datetime(2018, 3, 30, 11, 30)
                    )
            self.assertEqual(len(l1), 3)
            # rule active at: sun, mon, tue, wed, not holiday
            self.assertEqual(str(l1[0][0]), '2018-03-25 07:00:00')  # sun
            self.assertEqual(str(l1[0][1]), '2018-03-25 12:00:00')
            self.assertEqual(str(l1[1][0]), '2018-03-26 07:00:00')  # mon
            self.assertEqual(str(l1[1][1]), '2018-03-26 12:00:00')
            self.assertEqual(str(l1[2][0]), '2018-03-28 07:00:00')  # wed
            self.assertEqual(str(l1[2][1]), '2018-03-28 12:00:00')

            # delete holiday
            hl1 = Holiday.search([])
            if len(hl1) == 1:
                Holiday.delete([hl1[0]])

            # event ends near midnight, localtime is at next day
            l1 = AccountRule.get_periods_to_check_by_rule(
                        acc_lst[1], 
                        datetime(2018, 3, 26, 8, 0),
                        datetime(2018, 3, 26, 23, 30)
                    )
            self.assertEqual(len(l1), 2)
            self.assertEqual(str(l1[0][0]), '2018-03-26 07:00:00')
            self.assertEqual(str(l1[0][1]), '2018-03-26 12:00:00')
            self.assertEqual(str(l1[1][0]), '2018-03-27 07:00:00')
            self.assertEqual(str(l1[1][1]), '2018-03-27 12:00:00')

    @with_transaction()
    def test_accountrule_get_match_periods(self):
        """ test: test function get_match_periods()
        """
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W'},
                    ],
                accountrules=[
                        {'name':'8-16', 'shortname':'W1', 
                         'mint':time(8, 0), 'maxt':time(16, 0),     # localtime
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account':'Work', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                    ],
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'
        tarobj1.company.save()

        with set_company(tarobj1.company):
            AccountRule = Pool().get('employee_timetracking.accountrule')

            # period within rule section
            l1 = AccountRule.get_match_periods(
                        tarobj1.accountrule[0], 
                        datetime(2018, 3, 26, 7, 0),    # utc:   7:00 - 9:00
                        datetime(2018, 3, 26, 9, 0)     # local: 9:00 - 11:00
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(str(l1[0][0]), '2018-03-26 07:00:00')
            self.assertEqual(str(l1[0][1]), '2018-03-26 09:00:00')

            # period starts before rule section
            l1 = AccountRule.get_match_periods(
                        tarobj1.accountrule[0], 
                        datetime(2018, 3, 26, 5, 0),    # utc
                        datetime(2018, 3, 26, 12, 0)    # rule in utc: 6:00 - 14:00
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(str(l1[0][0]), '2018-03-26 06:00:00')
            self.assertEqual(str(l1[0][1]), '2018-03-26 12:00:00')

            # period ends after rule section
            l1 = AccountRule.get_match_periods(
                        tarobj1.accountrule[0], 
                        datetime(2018, 3, 26, 9, 0),
                        datetime(2018, 3, 26, 18, 0)
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(str(l1[0][0]), '2018-03-26 09:00:00')
            self.assertEqual(str(l1[0][1]), '2018-03-26 14:00:00')

            # period start before / end after rule section
            l1 = AccountRule.get_match_periods(
                        tarobj1.accountrule[0], 
                        datetime(2018, 3, 26, 5, 0),
                        datetime(2018, 3, 26, 19, 0)
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(str(l1[0][0]), '2018-03-26 06:00:00')
            self.assertEqual(str(l1[0][1]), '2018-03-26 14:00:00')

            # period start exactly at begin of rule section / end after rule section
            l1 = AccountRule.get_match_periods(
                        tarobj1.accountrule[0], 
                        datetime(2018, 3, 26, 6, 0, 0),
                        datetime(2018, 3, 26, 18, 0)
                    )
            self.assertEqual(len(l1), 1)
            self.assertEqual(str(l1[0][0]), '2018-03-26 06:00:00')
            self.assertEqual(str(l1[0][1]), '2018-03-26 14:00:00')

            # period runs a week, rule active at 4 days
            l1 = AccountRule.get_match_periods(
                        tarobj1.accountrule[0],             # rule utc: 6:00 - 14:00
                        datetime(2018, 3, 25, 9, 0, 0),
                        datetime(2018, 3, 30, 13, 30, 0)
                    )
            self.assertEqual(len(l1), 4)
            self.assertEqual(str(l1[0][0]), '2018-03-25 09:00:00')
            self.assertEqual(str(l1[0][1]), '2018-03-25 14:00:00')
            self.assertEqual(str(l1[1][0]), '2018-03-26 06:00:00')
            self.assertEqual(str(l1[1][1]), '2018-03-26 14:00:00')
            self.assertEqual(str(l1[2][0]), '2018-03-27 06:00:00')
            self.assertEqual(str(l1[2][1]), '2018-03-27 14:00:00')
            self.assertEqual(str(l1[3][0]), '2018-03-28 06:00:00')
            self.assertEqual(str(l1[3][1]), '2018-03-28 14:00:00')
            # period ends in range where rule not applies, therefore last item at 28.3.

    @with_transaction()
    def test_accountrule_create_account_items_by_rule(self):
        """ test: create tariff, employee and period, autocreate necessary time account items
        """
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
                        {'name':'Work 0-7', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(7, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
                        {'name':'Work 7-16', 'shortname':'AR1', 
                         'mint':time(7, 0, 0), 'maxt':time(16, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 16-19', 'shortname':'AR2', 
                         'mint':time(16, 0, 0), 'maxt':time(19, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                        {'name':'Work 19-24', 'shortname':'AR3', 
                         'mint':time(19, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                        {'name':'Ill', 'shortname':'I'},
                        {'name':'Site work', 'shortname':'SW'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            pool = Pool()
            AccountRule = pool.get('employee_timetracking.accountrule')
            Period = pool.get('employee_timetracking.period')

            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            # check account rule
            self.assertEqual(len(tarobj1.accountrule), 4)
            a_lst = AccountRule.search([('name', '=', 'Work 7-16')])
            self.assertEqual(len(a_lst), 1)
            self.assertEqual(a_lst[0].name, 'Work 7-16')
            self.assertEqual(str(a_lst[0].mintime), '07:00:00')
            self.assertEqual(str(a_lst[0].maxtime), '16:00:00')
            self.assertEqual(a_lst[0].mon, True)
            self.assertEqual(a_lst[0].tue, True)
            self.assertEqual(a_lst[0].wed, True)
            self.assertEqual(a_lst[0].thu, False)
            self.assertEqual(a_lst[0].fri, False)
            self.assertEqual(a_lst[0].sat, True)
            self.assertEqual(a_lst[0].sun, True)
            self.assertEqual(a_lst[0].account.name, 'Work')
            
            # monday
            p1 = create_period(
                    datetime(2018, 3, 26, 10, 30, 0), 
                    datetime(2018, 3, 26, 13, 35, 23), 
                    tarobj1.type_present, employee1)    # DB stores in UTC
            self.assertEqual(str(p1.startpos), '2018-03-26 10:30:00')   # UTC
            self.assertEqual(str(p1.endpos),   '2018-03-26 13:35:23')
            self.assertEqual(p1.name, '12:30 - 15:35, 2018-03-26 [W]')  # CEST
            self.assertEqual(p1.employee.party.name, 'Frida')
            self.assertEqual(p1.presence.name, 'Work')
            self.assertEqual(p1.state, 'c')
            l1 = AccountRule.add_item_by_rules(list(tarobj1.accountrule), p1)
            self.assertEqual(len(l1), 1)
            self.assertEqual(str(l1[0].startpos), '2018-03-26 10:30:00')
            self.assertEqual(str(l1[0].endpos), '2018-03-26 13:35:23')
            self.assertEqual(l1[0].account.name, 'Work')
            self.assertEqual(l1[0].period.name, '12:30 - 15:35, 2018-03-26 [W]')
            # evaluation is now created
            self.assertEqual(l1[0].evaluation.rec_name, 'Frida - 2018-03')
        
            # tuesday, 8:00 - 22:30 CEST --> 6:00 - 20:30 UTC
            # 3 rules will be affected: 2 + 3 + 4
            p2 = create_period(                             #         utc                 cest
                    datetime(2018, 3, 27, 6, 0, 0),         # period  6:00:00 - 20:30:23  8:00:00 - 22:30:23
                    datetime(2018, 3, 27, 20, 30, 23),      # rule 1                      0:00:00 -  7:00:00  
                    tarobj1.type_present, employee1)        # rule 2                      7:00:00 - 16:00:00  
            p2.save()                                       # rule 3                     16:00:00 - 19:00:00  
            self.assertEqual(p2.state, 'c')                 # rule 4                     19:00:00 - 00:00:00  
            self.assertEqual(str(p2.startpos), '2018-03-27 06:00:00')
            self.assertEqual(str(p2.endpos),   '2018-03-27 20:30:23')
            self.assertEqual(p2.name, '08:00 - 22:30, 2018-03-27 [W]')
            self.assertEqual(p2.employee.party.name, 'Frida')
            self.assertEqual(p2.presence.name, 'Work')

            l1 = AccountRule.add_item_by_rules(list(tarobj1.accountrule), p2)
            self.assertEqual(len(l1), 3)
            l2 = sorted(l1, key=lambda t1: t1.startpos)

            self.assertEqual(str(l2[0].startpos), '2018-03-27 06:00:00')
            self.assertEqual(str(l2[0].endpos), '2018-03-27 14:00:00')
            self.assertEqual(l2[0].name, '08:00 - 16:00, 2018-03-27 [W1]')
            self.assertEqual(l2[0].account.name, 'Work')
            self.assertEqual(l2[0].accountrule.name, 'Work 7-16')
            self.assertEqual(l2[0].employee.party.name, 'Frida')
            self.assertEqual(l2[0].period.name, '08:00 - 22:30, 2018-03-27 [W]')
            self.assertEqual(l2[0].evaluation.rec_name, 'Frida - 2018-03')
            
            self.assertEqual(str(l2[1].startpos), '2018-03-27 14:00:00')
            self.assertEqual(str(l2[1].endpos), '2018-03-27 17:00:00')
            self.assertEqual(l2[1].name, '16:00 - 19:00, 2018-03-27 [W2]')
            self.assertEqual(l2[1].account.name, 'Work late')
            self.assertEqual(l2[1].accountrule.name, 'Work 16-19')
            self.assertEqual(l2[1].employee.party.name, 'Frida')
            self.assertEqual(l2[1].period.name, '08:00 - 22:30, 2018-03-27 [W]')
            self.assertEqual(l2[1].evaluation.rec_name, 'Frida - 2018-03')

            self.assertEqual(str(l2[2].startpos), '2018-03-27 17:00:00')
            self.assertEqual(str(l2[2].endpos), '2018-03-27 20:30:23')
            self.assertEqual(l2[2].name, '19:00 - 22:30, 2018-03-27 [W3]')
            self.assertEqual(l2[2].account.name, 'Work night')
            self.assertEqual(l2[2].accountrule.name, 'Work 19-24')
            self.assertEqual(l2[2].employee.party.name, 'Frida')
            self.assertEqual(l2[2].period.name, '08:00 - 22:30, 2018-03-27 [W]')
            self.assertEqual(l2[2].evaluation.rec_name, 'Frida - 2018-03')

            # night shift: 25.3. 22:00 - 26.3. 6:30 CEST
            # rules affected: 4 + 1
            p3 = create_period(                             #         utc                  cest
                    datetime(2018, 3, 25, 20, 0, 0),        # period  20:00:00 - 04:30:23  22:00:00 - 06:30:23
                    datetime(2018, 3, 26, 4, 30, 23),       # rule 1                        0:00:00 -  7:00:00  
                    tarobj1.type_present, employee1)        # rule 2                        7:00:00 - 16:00:00  
            p3.save()                                       # rule 3                       16:00:00 - 19:00:00  
            self.assertEqual(p3.state, 'c')                 # rule 4                       19:00:00 - 00:00:00  
            self.assertEqual(str(p3.startpos), '2018-03-25 20:00:00')
            self.assertEqual(str(p3.endpos),   '2018-03-26 04:30:23')
            self.assertEqual(p3.name, '22:00 - 06:30, 2018-03-25 [W]')
            self.assertEqual(p3.employee.party.name, 'Frida')
            self.assertEqual(p3.presence.name, 'Work')
            # results are for same time account, but different rules --> not optimized
            l1 = AccountRule.add_item_by_rules(list(tarobj1.accountrule), p3)
            self.assertEqual(len(l1), 2)

            self.assertEqual(str(l1[0].startpos), '2018-03-25 20:00:00')
            self.assertEqual(str(l1[0].endpos), '2018-03-25 22:00:00')
            self.assertEqual(l1[0].name, '22:00 - 00:00, 2018-03-25 [W3]')
            self.assertEqual(l1[0].account.name, 'Work night')
            self.assertEqual(l1[0].employee.party.name, 'Frida')
            self.assertEqual(l1[0].period.name, '22:00 - 06:30, 2018-03-25 [W]')

            self.assertEqual(str(l1[1].startpos), '2018-03-25 22:00:00')
            self.assertEqual(str(l1[1].endpos), '2018-03-26 04:30:23')
            self.assertEqual(l1[1].name, '00:00 - 06:30, 2018-03-26 [W3]')
            self.assertEqual(l1[1].account.name, 'Work night')
            self.assertEqual(l1[1].employee.party.name, 'Frida')
            self.assertEqual(l1[1].period.name, '22:00 - 06:30, 2018-03-25 [W]')
            
            # check evaluation
            Evaluation = pool.get('employee_timetracking.evaluation')
            evlst = Evaluation.search([('employee', '=', employee1), ('evaldate', '=', date(2018, 3, 1))])
            self.assertEqual(len(evlst), 1)
            self.assertEqual(len(evlst[0].accountitems), 6)

    @with_transaction()
    def test_accountrule_create_account_items_by_rule2(self):
        """ test: create tariff, employee and period, work-rule runs 24h
        """
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
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 16-19', 'shortname':'AR2', 
                         'mint':time(16, 0, 0), 'maxt':time(19, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                        {'name':'Work 19-24', 'shortname':'AR3', 
                         'mint':time(19, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.6'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
                        {'name':'Work 0-7', 'shortname':'AR4', 
                         'mint':time(0, 0, 0), 'maxt':time(7, 0, 0), 
                         'fact':Decimal('1.6'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                        {'name':'Ill', 'shortname':'I'},
                        {'name':'Site work', 'shortname':'SW'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            pool = Pool()
            AccountRule = pool.get('employee_timetracking.accountrule')
            Period = pool.get('employee_timetracking.period')

            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            # check account rule
            self.assertEqual(len(tarobj1.accountrule), 4)
            a_lst = AccountRule.search([('name', '=', 'Work 0-24')])
            self.assertEqual(len(a_lst), 1)
            self.assertEqual(a_lst[0].name, 'Work 0-24')
            self.assertEqual(str(a_lst[0].mintime), '00:00:00')
            self.assertEqual(str(a_lst[0].maxtime), '00:00:00')
            self.assertEqual(a_lst[0].mon, True)
            self.assertEqual(a_lst[0].tue, True)
            self.assertEqual(a_lst[0].wed, True)
            self.assertEqual(a_lst[0].thu, False)
            self.assertEqual(a_lst[0].fri, False)
            self.assertEqual(a_lst[0].sat, True)
            self.assertEqual(a_lst[0].sun, True)
            self.assertEqual(a_lst[0].account.name, 'Work')
            
            # monday
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
            l1 = AccountRule.add_item_by_rules(list(tarobj1.accountrule), p1)
            l2 = sorted(l1, key=lambda t1: t1.startpos)
            self.assertEqual(len(l2), 3)
            
            self.assertEqual(str(l2[0].startpos), '2018-03-26 06:30:00')
            self.assertEqual(str(l2[0].endpos), '2018-03-26 19:35:23')
            self.assertEqual(l2[0].account.name, 'Work')
            self.assertEqual(l2[0].period.name, '08:30 - 21:35, 2018-03-26 [W]')
            
            self.assertEqual(str(l2[1].startpos), '2018-03-26 14:00:00')
            self.assertEqual(str(l2[1].endpos), '2018-03-26 17:00:00')
            self.assertEqual(l2[1].account.name, 'Work late')
            self.assertEqual(l2[1].period.name, '08:30 - 21:35, 2018-03-26 [W]')

            self.assertEqual(str(l2[2].startpos), '2018-03-26 17:00:00')
            self.assertEqual(str(l2[2].endpos), '2018-03-26 19:35:23')
            self.assertEqual(l2[2].account.name, 'Work night')
            self.assertEqual(l2[2].period.name, '08:30 - 21:35, 2018-03-26 [W]')

    @with_transaction()
    def test_accountrule_edit_account_items_by_period_workflow(self):
        """ test: create tariff, employee and period, create/delete account items by period-workflow
        """
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
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 16-19', 'shortname':'AR2', 
                         'mint':time(16, 0, 0), 'maxt':time(19, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                        {'name':'Work 19-24', 'shortname':'AR3', 
                         'mint':time(19, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.6'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
                        {'name':'Work 0-7', 'shortname':'AR4', 
                         'mint':time(0, 0, 0), 'maxt':time(7, 0, 0), 
                         'fact':Decimal('1.6'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work night', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                        {'name':'Ill', 'shortname':'I'},
                        {'name':'Site work', 'shortname':'SW'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()

        with set_company(tarobj1.company):
            pool = Pool()
            AccountRule = pool.get('employee_timetracking.accountrule')
            Period = pool.get('employee_timetracking.period')
            TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')

            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()

            # check account rule
            self.assertEqual(len(tarobj1.accountrule), 4)
            a_lst = AccountRule.search([('name', '=', 'Work 0-24')])
            self.assertEqual(len(a_lst), 1)
            self.assertEqual(a_lst[0].name, 'Work 0-24')
            self.assertEqual(str(a_lst[0].mintime), '00:00:00')
            self.assertEqual(str(a_lst[0].maxtime), '00:00:00')
            self.assertEqual(a_lst[0].mon, True)
            self.assertEqual(a_lst[0].tue, True)
            self.assertEqual(a_lst[0].wed, True)
            self.assertEqual(a_lst[0].thu, False)
            self.assertEqual(a_lst[0].fri, False)
            self.assertEqual(a_lst[0].sat, True)
            self.assertEqual(a_lst[0].sun, True)
            self.assertEqual(a_lst[0].account.name, 'Work')
            
            # monday
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
            
            # workflow action - create items
            Period.wfexamine([p1])

            l1 = TimeAccountItem.search([('employee', '=', employee1)], order=[('startpos', 'ASC')])
            self.assertEqual(len(l1), 3)

            l3 = [x.name for x in l1]
            l2a = sorted(p1.accountitem, key=lambda tl2: tl2.startpos)
            l2 = [x.name for x in l2a]
            self.assertEqual(l2, l3)
            
            self.assertEqual(str(l1[0].startpos), '2018-03-26 06:30:00')
            self.assertEqual(str(l1[0].endpos), '2018-03-26 19:35:23')
            self.assertEqual(str(l1[0].name), '08:30 - 21:35, 2018-03-26 [W1]')
            self.assertEqual(l1[0].account.name, 'Work')
            self.assertEqual(l1[0].period.name, '08:30 - 21:35, 2018-03-26 [W]')
            self.assertEqual(l1[0].state, 'e')
            
            self.assertEqual(str(l1[1].startpos), '2018-03-26 14:00:00')
            self.assertEqual(str(l1[1].endpos), '2018-03-26 17:00:00')
            self.assertEqual(str(l1[1].name), '16:00 - 19:00, 2018-03-26 [W2]')
            self.assertEqual(l1[1].account.name, 'Work late')
            self.assertEqual(l1[1].period.name, '08:30 - 21:35, 2018-03-26 [W]')
            self.assertEqual(l1[1].state, 'e')

            self.assertEqual(str(l1[2].startpos), '2018-03-26 17:00:00')
            self.assertEqual(str(l1[2].endpos), '2018-03-26 19:35:23')
            self.assertEqual(str(l1[2].name), '19:00 - 21:35, 2018-03-26 [W3]')
            self.assertEqual(l1[2].account.name, 'Work night')
            self.assertEqual(l1[2].period.name, '08:30 - 21:35, 2018-03-26 [W]')
            self.assertEqual(l1[2].state, 'e')

            # wf action - lock items (period + account item)
            Period.wflock([p1])
            self.assertEqual(l1[0].state, 'l')
            self.assertEqual(l1[1].state, 'l')
            self.assertEqual(l1[2].state, 'l')
            self.assertEqual(p1.state, 'l')

            # wf action - create - delete account items
            Period.wfcreate([p1])
            self.assertEqual(len(p1.accountitem), 0)
            self.assertEqual(p1.state, 'c')

    @with_transaction()
    def test_accountrule_migrate_columns(self):
        """ create tariff-model, with table "employee_timetracking_accountrule_rel",
            migrate records to new (> ver x.x.8) model
        """
        pool = Pool()
        transaction = Transaction()
        cursor = transaction.connection.cursor()

        TableHandler = backend.get('TableHandler')
        AccountRule = pool.get('employee_timetracking.accountrule')
        PresenceRel = pool.get('employee_timetracking.presence_rel')
        Tariff = pool.get('employee_timetracking.tariffmodel')
        
        table = TableHandler(AccountRule, 'employee_timetracking')
        
        # prepare db
        seq1 = """CREATE SEQUENCE public.employee_timetracking_accountrule_rel_id_seq
                INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1;"""
        cursor.execute(seq1)
        tab1 = """CREATE TABLE public.employee_timetracking_accountrule_rel(
        id integer NOT NULL DEFAULT nextval('employee_timetracking_accountrule_rel_id_seq'::regclass),
        accountrule integer NOT NULL, tariff integer NOT NULL,
        CONSTRAINT employee_timetracking_accountrule_rel_pkey PRIMARY KEY (id))"""
        cursor.execute(tab1)
        self.assertTrue(table.table_exist('employee_timetracking_accountrule_rel'))
        
        # remove 'not null' from table 'accountrule', column 'tariff'
        # if column 'tariff' is new created and there are already item in
        # the table, the option 'not null' is not created
        nn1 = """ALTER TABLE public.employee_timetracking_accountrule
                ALTER COLUMN tariff DROP NOT NULL;"""
        cursor.execute(nn1)

        # add tariff
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[
                        {'name':'Work', 'shortname':'W1'},
                        {'name':'Work late', 'shortname':'W2'},
                    ],
                accountrules=[
                        # time in localtime of company
                        {'name':'Work 0-24', 'shortname':'AR0', 
                         'mint':time(0, 0, 0), 'maxt':time(0, 0, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work', 'presence':'Work'},
                        {'name':'Work 16-19', 'shortname':'AR2', 
                         'mint':time(16, 0, 0), 'maxt':time(19, 0, 0), 
                         'fact':Decimal('1.3'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NOTAT,
                         'tue':True, 'wed':True, 'thu':False, 'fri':False,
                         'sat':True, 'sun':True, 'account': 'Work late', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'W'},
                        {'name':'Ill', 'shortname':'I'},
                        {'name':'Site work', 'shortname':'SW'}
                    ],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        tarobj1.company.timezone = 'Europe/Berlin'  # CET (+1h) / CEST (+2h)
        tarobj1.company.save()
        
        # we have 3 items in presence_rel
        pr1 = PresenceRel.search([])
        self.assertEqual(len(pr1), 3)
        
        # create another tariff
        tar2 = create_tariff(name='Tariff 2', shortname='T2', company=tarobj1.company)
        self.assertTrue(tar2)
        # add existing presences to 2nd tariff
        p_lst = []
        for i in tarobj1.presence:
            if i.name != 'Ill':
                p_lst.append(i)
        tar2.presence = p_lst
        tar2.save()

        # we have now 5 items in presence_rel
        pr1 = PresenceRel.search([])
        self.assertEqual(len(pr1), 5)
        
        # disconnect accountrule-item from tariff1
        dis1 = """update public.employee_timetracking_accountrule set (tariff) = (null);"""
        cursor.execute(dis1)
        self.assertEqual(len(tarobj1.accountrule), 0)
        
        # create relation-items in account_rule_rel
        # for 1st tariff
        acr_lst = AccountRule.search([])
        self.assertEqual(len(acr_lst), 2)
        for i in acr_lst:
            add1 = """insert into public.employee_timetracking_accountrule_rel 
                    (accountrule, tariff) values (%s, %s)""" % \
                (i.id, tarobj1.id)
            cursor.execute(add1)
        # link one rule to 2nd tariff
        add2 = """insert into public.employee_timetracking_accountrule_rel 
                (accountrule, tariff) values (%s, %s)""" % \
            (acr_lst[0].id, tar2.id)
        cursor.execute(add2)
        
        # count item in employee_timetracking_accountrule_rel
        cnt1 = """select count(id) as "numitm" from public.employee_timetracking_accountrule_rel"""
        cursor.execute(cnt1)
        (cnt2,) = cursor.fetchone()
        self.assertEqual(cnt2, 3)
        
        # run migration
        AccountRule.migrate_columns('employee_timetracking')
        
        # check results
        # table 'employee_timetracking_accountrule_rel' removed
        self.assertTrue(table.table_exist('employee_timetracking_accountrule_rel') == False)
        
        # two tariff model
        ta1 = Tariff.search([])
        self.assertEqual(len(ta1), 2)
        
        # table accountrules has 3 records
        ac1 = AccountRule.search([])
        self.assertEqual(len(ac1), 3)
        
        # tariff model 1
        t1 = Tariff.search([('name', '=', 'Tariff1')])
        self.assertEqual(len(t1), 1)
        # tariff model 1 has 2 account rules
        self.assertEqual(len(t1[0].accountrule), 2)
        ac2 = AccountRule.search([('tariff', '=', t1[0])] , order=[('name', 'ASC')])
        self.assertEqual(len(ac2), 2)
        # 1st rule
        self.assertEqual(ac1[0].name, 'Work 0-24')
        self.assertEqual(ac1[0].shortname, 'AR0')
        self.assertEqual(str(ac1[0].mintime), '00:00:00')
        self.assertEqual(str(ac1[0].maxtime), '00:00:00')
        self.assertEqual(str(ac1[0].factor), '1.0')
        self.assertEqual(str(ac1[0].mon), 'True')
        self.assertEqual(str(ac1[0].tue), 'True')
        self.assertEqual(str(ac1[0].wed), 'True')
        self.assertEqual(str(ac1[0].thu), 'False')
        self.assertEqual(str(ac1[0].fri), 'False')
        self.assertEqual(str(ac1[0].sat), 'True')
        self.assertEqual(str(ac1[0].sun), 'True')
        self.assertEqual(ac1[0].account.rec_name, 'Work')
        self.assertEqual(ac1[0].presence.rec_name, 'Work')
        # 2nd rule
        self.assertEqual(ac1[1].name, 'Work 16-19')
        self.assertEqual(ac1[1].shortname, 'AR2')
        self.assertEqual(str(ac1[1].mintime), '16:00:00')
        self.assertEqual(str(ac1[1].maxtime), '19:00:00')
        self.assertEqual(str(ac1[1].factor), '1.3')
        self.assertEqual(str(ac1[1].mon), 'True')
        self.assertEqual(str(ac1[1].tue), 'True')
        self.assertEqual(str(ac1[1].wed), 'True')
        self.assertEqual(str(ac1[1].thu), 'False')
        self.assertEqual(str(ac1[1].fri), 'False')
        self.assertEqual(str(ac1[1].sat), 'True')
        self.assertEqual(str(ac1[1].sun), 'True')
        self.assertEqual(ac1[1].account.rec_name, 'Work late')
        self.assertEqual(ac1[1].presence.rec_name, 'Work')

        # tariff model 2
        t2 = Tariff.search([('name', '=', 'Tariff 2')])
        self.assertEqual(len(t2), 1)
        # tariff model 2 has one account rule
        self.assertEqual(len(t2[0].accountrule), 1)
        ac3 = AccountRule.search([('tariff', '=', t2[0])] , order=[('name', 'ASC')])
        self.assertEqual(len(ac3), 1)
        self.assertEqual(ac3[0].name, 'Work 0-24')
        self.assertEqual(ac3[0].shortname, 'AR0')
        self.assertEqual(str(ac3[0].mintime), '00:00:00')
        self.assertEqual(str(ac3[0].maxtime), '00:00:00')
        self.assertEqual(str(ac3[0].factor), '1.0')
        self.assertEqual(str(ac3[0].mon), 'True')
        self.assertEqual(str(ac3[0].tue), 'True')
        self.assertEqual(str(ac3[0].wed), 'True')
        self.assertEqual(str(ac3[0].thu), 'False')
        self.assertEqual(str(ac3[0].fri), 'False')
        self.assertEqual(str(ac3[0].sat), 'True')
        self.assertEqual(str(ac3[0].sun), 'True')
        self.assertEqual(ac3[0].account.rec_name, 'Work')
        self.assertEqual(ac3[0].presence.rec_name, 'Work')

        # account rule ids are different
        self.assertTrue(ac1[0].id != ac1[1].id)
        self.assertTrue(ac1[0].id != ac3[0].id)
        self.assertTrue(ac1[1].id != ac3[0].id)
        
# end AccountRuleTestCase
