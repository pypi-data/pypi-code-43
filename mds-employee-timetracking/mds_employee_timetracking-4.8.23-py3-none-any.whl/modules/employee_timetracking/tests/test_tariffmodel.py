# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_presence, \
    create_accountrule, create_breaktime, create_tariff, create_tariff_full,\
    create_timeaccount
from datetime import timedelta, time
from decimal import Decimal
from trytond.modules.employee_timetracking.const import ACRULE_HOLIDAY_NODEF


class TariffModelTestCase(ModuleTestCase):
    'Test tariff model module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_tariffmodel_create_minimal(self):
        """ create a tariff model without 'breaktime', 'accountrule', 'presence'
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create tariff model
            # some defaults are applied
            TariffM = Pool().get('employee_timetracking.tariffmodel')
            tarobj = create_tariff(name='Tariff1', shortname='T1', \
                            company=TariffM.default_company()
                            )
            self.assertTrue(tarobj)

    @with_transaction()
    def test_tariffmodel_create_twice_same_name(self):
        """ create a tariff model twice with same name in same company
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create tariff model
            TariffM = Pool().get('employee_timetracking.tariffmodel')
            tarobj = create_tariff(name='Tariff1', shortname='T1', \
                            company=TariffM.default_company()
                            )
            self.assertTrue(tarobj)
            
            # 2nd with same name
            tr_obj = TariffM(
                name='Tariff1', shortname='T1a', 
                company=TariffM.default_company())
            self.assertRaisesRegex(UserError, 
                "This name is already in use.",
                tr_obj.save)
    
    @with_transaction()
    def test_tariffmodel_create_twice_same_shortname(self):
        """ create a tariff model twice with same shortname in same company
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            # create tariff model
            TariffM = Pool().get('employee_timetracking.tariffmodel')
            tarobj = create_tariff(name='Tariff1', shortname='T1', \
                            company=TariffM.default_company()
                            )
            self.assertTrue(tarobj)
            
            # 2nd with same shortname
            tr_obj = TariffM(
                name='Tariff1a', shortname='T1', 
                company=TariffM.default_company())
            self.assertRaisesRegex(UserError, 
                "This shorthand symbol is already in use.",
                tr_obj.save)

    @with_transaction()
    def test_tariffmodel_create_twice_in_two_companies(self):
        """ create a tariff model twice with same shortname in same company
        """
        # create a company and write new company to context
        company1 = create_company('m-ds 1')
        self.assertTrue(company1)
        company2 = create_company('m-ds 2')
        self.assertTrue(company2)
        
        with set_company(company1):
            TariffM = Pool().get('employee_timetracking.tariffmodel')
    
            # create tariff model
            tarobj1 = create_tariff(name='Tariff1', shortname='T1', \
                            company=company1
                            )
            self.assertTrue(tarobj1)
    
            # 2nd tariffmodel in 2nd company
            tarobj2 = create_tariff(name='Tariff1', shortname='T1', \
                            company=company2
                            )
            self.assertTrue(tarobj2)

    @with_transaction()
    def test_tariffmodel_create_full1(self):
        """ create a tariff model with breaktime, accountrule, presence
        """
        Presence = Pool().get('employee_timetracking.presence')
        BreakTime = Pool().get('employee_timetracking.breaktime')
        AccountRule = Pool().get('employee_timetracking.accountrule')

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
                        {'name': 'Work late', 'shortname': 'W2'},
                    ],
                accountrules=[
                        {'name':'8-16', 'shortname':'W1', 
                         'mint':time(8, 0), 'maxt':time(16, 0), 
                         'fact':Decimal('1.0'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':False, 'sun':False, 'account': 'Work norm', 'presence':'Work'},
                        {'name':'16-19', 'shortname':'W2', 
                         'mint':time(16, 1), 'maxt':time(19, 0), 
                         'fact':Decimal('1.5'), 'mon':True, 'holiday': ACRULE_HOLIDAY_NODEF,
                         'tue':True, 'wed':True, 'thu':True, 'fri':True,
                         'sat':False, 'sun':False, 'account': 'Work late', 'presence':'Work'},
                    ],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
                main_account='Work norm',
            )
        self.assertTrue(tarobj1)

        # read breaktimes
        l2 = BreakTime.search([
                ('tariff', '=', tarobj1),
                ('id', 'in', [x.id for x in tarobj1.breaktime])
            ], order=[('mintime', 'ASC')])
        self.assertEqual(len(l2), 2)
        self.assertEqual(l2[0].name, '4-5:59')
        self.assertEqual(l2[1].name, '6-7:59')
        # breaktime must show 'used from tariff'
        self.assertEqual(l2[0].tariff.name, 'Tariff1')
        
        # read presences
        l2 = Presence.search([
                ('company', '=', tarobj1.company),
                ('id', 'in', [x.id for x in tarobj1.presence]),
            ], order=[('shortname', 'ASC')])
        self.assertEqual(len(l2), 3)
        self.assertEqual(l2[0].name, 'Work')
        self.assertEqual(l2[1].name, 'Ill')
        self.assertEqual(l2[2].name, 'Site work')
        self.assertEqual(tarobj1.type_present.name, 'Work')
        
        # read accountrule
        l3 = AccountRule.search([
                ('company', '=', tarobj1.company.id),
                ('id', 'in', [x.id for x in tarobj1.accountrule])
            ], order=[('mintime', 'ASC')])
        self.assertEqual(len(l3), 2)
        self.assertEqual(l3[0].name, '8-16')
        self.assertEqual(l3[1].name, '16-19')
        
        self.assertEqual(tarobj1.main_timeaccount.name, 'Work norm')

    @with_transaction()
    def test_tariffmodel_reduce_worktime(self):
        """ test: reduce worktime by current tariff
        """
        # prepare ruleset
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4 to 5:59 / 30min', 'shortname':'P1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6 to 7:59 / 60min', 'shortname':'P2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=60*60)},
                    ],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)

        TariffM = Pool().get('employee_timetracking.tariffmodel')
        # 4:50 --> 4:20
        self.assertEqual(
            str(TariffM.get_reduced_worktime(tarobj1, timedelta(seconds=4*60*60 + 50*60), timedelta(seconds=0))),
            '4:20:00'
            )
        # 6:30 --> 5:30
        self.assertEqual(
            str(TariffM.get_reduced_worktime(tarobj1, timedelta(seconds=6*60*60 + 30*60), timedelta(seconds=0))),
            '5:30:00'
            )
        # 6:58 --> 5:58
        self.assertEqual(
            str(TariffM.get_reduced_worktime(tarobj1, timedelta(seconds=6*60*60 + 58*60), timedelta(seconds=0))),
            '5:58:00'
            )
        # 7:10 --> 6:10
        self.assertEqual(
            str(TariffM.get_reduced_worktime(tarobj1, timedelta(seconds=7*60*60 + 10*60), timedelta(seconds=0))),
            '6:10:00'
            )

    @with_transaction()
    def test_breaktime_overlap_valid(self):
        """ test: create tarif with breaktimes, check non-overlapping items
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        
        # prepare ruleset
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4 to 5:59 / 30min', 'shortname':'P1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6 to 7:59 / 60min', 'shortname':'P2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=60*60)},
                    ],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)
        
        self.assertEqual(BreakTime.check_overlap(tarobj1.breaktime, 
                    timedelta(seconds=2*60*60 + 30*60),     # 2:30
                    timedelta(seconds=3*60*60 + 59*60 + 59) # 3:59:59
                ), [])
        self.assertEqual(BreakTime.check_overlap(tarobj1.breaktime, 
                    timedelta(seconds=8*60*60),             # 8:00
                    timedelta(seconds=8*60*60 + 59*60 + 59) # 8:59:59
                ), [])

    @with_transaction()
    def test_breaktime_overlap_invalid(self):
        """ test: create tarif with breaktimes, check overlapping items
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        
        # prepare ruleset
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4 to 5:59 / 30min', 'shortname':'P1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6 to 7:59 / 60min', 'shortname':'P2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=60*60)},
                    ],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)
        
        l1 = BreakTime.search([('tariff', '=', tarobj1), ('name', '=', '4 to 5:59 / 30min')], limit=1)
        self.assertEqual(BreakTime.check_overlap(tarobj1.breaktime, 
                    timedelta(seconds=3*60*60 + 30*60),     # 3:30
                    timedelta(seconds=5*60*60)              # 5:00
                ), [l1[0].id])
        
        l1 = BreakTime.search([('tariff', '=', tarobj1), ('name', '=', '6 to 7:59 / 60min')], limit=1)
        self.assertEqual(BreakTime.check_overlap(tarobj1.breaktime, 
                    timedelta(seconds=7*60*60),             # 7:00
                    timedelta(seconds=8*60*60 + 59*60 + 59) # 8:59:59
                ), [l1[0].id])

        # fire exception if overlap
        self.assertRaisesRegex(UserError,
            "The from/to time range overlaps with the following rules: '6 to 7:59 / 60min \(P2\)",
            BreakTime.check_minmax_range,
            tarobj1, 
            timedelta(seconds=7*60*60),             # 7:00
            timedelta(seconds=8*60*60 + 59*60 + 59) # 8:59:59
            )
        # ignore item '6 to 7:59 / 60min' - no exception
        self.assertEqual(
            BreakTime.check_minmax_range(
                tarobj1, 
                timedelta(seconds=7*60*60),            
                timedelta(seconds=8*60*60 + 59*60 + 59), 
                BreakTime(l1[0])
            ),
            None)

    @with_transaction()
    def test_breaktime_edit_no_overlap(self):
        """ test: create tarif with breaktimes, edit breaktime item, no overlap = no exception
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        
        # prepare ruleset
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4 to 5:59 / 30min', 'shortname':'P1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6 to 7:59 / 60min', 'shortname':'P2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=60*60)},
                    ],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)

        l1 = BreakTime.search([('tariff', '=', tarobj1), ('name', '=', '4 to 5:59 / 30min')], limit=1)
        self.assertEqual(len(l1), 1)
        l1[0].maxtime = timedelta(seconds=5*60*60 + 57*60 + 59)
        l1[0].save()
        self.assertEqual(str(l1[0].maxtime), '5:57:59')

    @with_transaction()
    def test_breaktime_edit_with_overlap(self):
        """ test: create tarif with breaktimes, edit breaktime item, with overlap --> exception
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        
        # prepare ruleset
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4 to 5:59 / 30min', 'shortname':'P1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6 to 7:59 / 60min', 'shortname':'P2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=60*60)},
                    ],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)

        l1 = BreakTime.search([('tariff', '=', tarobj1), ('name', '=', '4 to 5:59 / 30min')], limit=1)
        self.assertEqual(len(l1), 1)
        l1[0].maxtime = timedelta(seconds=6*60*60 + 2*60 + 59)
        self.assertRaisesRegex(UserError,
            "The from/to time range overlaps with the following rules: '6 to 7:59 / 60min \(P2\)'",
            l1[0].save)

    @with_transaction()
    def test_breaktime_add_two_items_with_overlap(self):
        """ test: create tarif without breaktimes, add two overlapping breaktime items --> exception
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')

        # prepare ruleset
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)

        br1 = create_breaktime(name='4 to 5:59 / 30min', shortname='P1', 
                    mintime=timedelta(seconds=4*60*60),
                    maxtime=timedelta(seconds=5*60*60 + 59*60 + 59),
                    deduction=timedelta(seconds=30*60),
                    tariff=tarobj1)
        self.assertTrue(br1)
        

        br_obj = BreakTime(
            name='4:30 to 6:30 / 30min', shortname='P2', 
            mintime=timedelta(seconds=4*60*60 + 30*60),
            maxtime=timedelta(seconds=6*60*60 + 30*60),
            deduction=timedelta(seconds=30*60),
            tariff=tarobj1)
        self.assertRaisesRegex(UserError,
            "The from/to time range overlaps with the following rules: '4 to 5:59 / 30min \(P1\)'",
            br_obj.save)

    @with_transaction()
    def test_tariffmodel_add_breaktime_no_overlap(self):
        """ test: create tarif with breaktimes, add non-overlap-breaktime = no exception
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        
        # prepare ruleset
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4 to 5:59 / 30min', 'shortname':'P1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6 to 7:59 / 60min', 'shortname':'P2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=60*60)},
                    ],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)
        self.assertEqual(len(tarobj1.breaktime), 2)

        l1 = list(tarobj1.breaktime)
        l1.append(BreakTime(name='2 to 4', shortname='P3', \
                        mintime=timedelta(seconds=2*60*60),
                        maxtime=timedelta(seconds=3*60*60 + 59*60 + 59),
                        deduction=timedelta(seconds=30*60)))
        tarobj1.breaktime = l1
        tarobj1.save()
        self.assertEqual(len(tarobj1.breaktime), 3)

    @with_transaction()
    def test_tariffmodel_add_breaktime_with_overlap(self):
        """ test: create tarif with breaktimes, add overlap-breaktime --> exception
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        
        # prepare ruleset
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[
                        {'name':'4 to 5:59 / 30min', 'shortname':'P1', 
                         'mint':timedelta(seconds=4*60*60), 
                         'maxt':timedelta(seconds=5*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=30*60)},
                        {'name':'6 to 7:59 / 60min', 'shortname':'P2', 
                         'mint':timedelta(seconds=6*60*60), 
                         'maxt':timedelta(seconds=7*60*60 + 59*60 + 59),
                         'dedu':timedelta(seconds=60*60)},
                    ],
                timeaccounts=[],
                accountrules=[],
                presences=[],
            )
        self.assertTrue(tarobj1)
        self.assertEqual(len(tarobj1.breaktime), 2)

        l1 = list(tarobj1.breaktime)
        l1.append(BreakTime(name='3 to 5', shortname='P3', \
                        mintime=timedelta(seconds=3*60*60),
                        maxtime=timedelta(seconds=4*60*60 + 59*60 + 59),
                        deduction=timedelta(seconds=30*60)))
        tarobj1.breaktime = l1
        self.assertRaisesRegex(UserError, 
            "The from/to time range overlaps with the following rules: '4 to 5:59 / 30min \(P1\)'",
            tarobj1.save)

    @with_transaction()
    def test_tariffmodel_allowed_timeaccounts(self):
        """ test: two companies + time accounts, get valid time accounts
        """
        company1 = create_company('m-ds 2')
        self.assertTrue(company1)
        company2 = create_company('m-ds 2')
        self.assertTrue(company2)
        
        ta1 = create_timeaccount('ta comp 1', 't1', company1)
        ta2 = create_timeaccount('ta comp 2', 't2', company2)
        
        tarobj1 = create_tariff(name='Tariff1', shortname='T1', \
                        company=company1)
        self.assertTrue(tarobj1)

        tarobj2 = create_tariff(name='Tariff2', shortname='T2', \
                        company=company2)
        self.assertTrue(tarobj2)
        
        # check time accounts
        self.assertEqual(len(tarobj1.timeaccounts), 1)
        self.assertEqual(tarobj1.timeaccounts[0].name, 'ta comp 1')
        self.assertEqual(len(tarobj2.timeaccounts), 1)
        self.assertEqual(tarobj2.timeaccounts[0].name, 'ta comp 2')

# end TariffModelTestCase

