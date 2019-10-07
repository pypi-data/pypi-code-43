# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import timedelta
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_breaktime, create_tariff



class BreakTimeTestCase(ModuleTestCase):
    'Test breaktime module'
    module = 'employee_timetracking'

    def prep_breaktime(self):
        """ create company and 1st breaktime item
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            tar1 = create_tariff('Tar 1', 'T1', company=company)
            # create break time
            BreakTime = Pool().get('employee_timetracking.breaktime')
            breaktime = create_breaktime(name='4 to 6', shortname='P1', \
                            mintime=timedelta(seconds=4*60*60),
                            maxtime=timedelta(seconds=5*60*60 + 59*60 + 59),
                            deduction=timedelta(seconds=30*60),
                            tariff=tar1
                            )
        return breaktime
        
    @with_transaction()
    def test_breaktime_create_item(self):
        """ test: create valid break time item
        """
        # create a company and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        with set_company(company):
            tar1 = create_tariff('Tar 1', 'T1', company=company)
            
            # create break time
            BreakTime = Pool().get('employee_timetracking.breaktime')
            breaktime = create_breaktime(name='4 to 6', shortname='P1', \
                            # seconds 15: create() will change to 0
                            mintime=timedelta(seconds=4*60*60 + 15),
                            # seconds 23: create() will change to 59
                            maxtime=timedelta(seconds=5*60*60 + 59*60 + 23),
                            deduction=timedelta(seconds=30*60),
                            tariff=tar1
                            )
            
            # check values
            self.assertTrue(breaktime)
            self.assertEqual(breaktime.name, '4 to 6')
            self.assertEqual(breaktime.shortname, 'P1')
            self.assertEqual(breaktime.rec_name, '[Tar 1] P1: 04:00-05:59 -> 00h30')
            self.assertEqual(str(breaktime.mintime), '4:00:00')
            self.assertEqual(str(breaktime.maxtime), '5:59:59')
            self.assertEqual(str(breaktime.deduction), '0:30:00')
            
            # edit item
            breaktime.mintime = timedelta(seconds=4*60*60 + 15)
            breaktime.maxtime = timedelta(seconds=5*60*60 + 59*60 + 15)
            # write() change seconds to 0/59
            breaktime.save()
            self.assertEqual(str(breaktime.mintime), '4:00:00')
            self.assertEqual(str(breaktime.maxtime), '5:59:59')
        
    @with_transaction()
    def test_breaktime_create_item_twice_same_name(self):
        """ test: create break time item twice - same name
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        breaktime = self.prep_breaktime()
        
        with set_company(breaktime.tariff.company):
            # 2nd item
            # same name
            br_obj = BreakTime(
                    name='4 to 6', shortname='P2', 
                    mintime=timedelta(seconds=6*60*60 ),
                    maxtime=timedelta(seconds=7*60*60 + 59*60 + 59),
                    deduction=timedelta(seconds=1*60*60),
                    tariff=breaktime.tariff,
                )
            self.assertRaisesRegex(UserError,
                "This name is already in use.",
                br_obj.save)

    @with_transaction()
    def test_breaktime_create_item_twice_same_shortname(self):
        """ test: create break time item twice - same shortname
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        breaktime = self.prep_breaktime()

        with set_company(breaktime.tariff.company):
            br_obj = BreakTime(
                    name='6 to 8', shortname='P1', 
                    mintime=timedelta(seconds=6*60*60 ),
                    maxtime=timedelta(seconds=7*60*60 + 59*60 + 59),
                    deduction=timedelta(seconds=1*60*60),
                    tariff=breaktime.tariff,
                )
            self.assertRaisesRegex(UserError,
                "This shorthand symbol is already in use.",
                br_obj.save)

    @with_transaction()
    def test_breaktime_create_item_twice_same_mintime(self):
        """ test: create break time item twice - same mintime
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        breaktime = self.prep_breaktime()

        with set_company(breaktime.tariff.company):
            br_obj = BreakTime(
                    name='6 to 8', shortname='P2', 
                    mintime=timedelta(seconds=4*60*60 ),
                    maxtime=timedelta(seconds=7*60*60 + 59*60 + 59),
                    deduction=timedelta(seconds=1*60*60),
                    tariff=breaktime.tariff,
                )
            self.assertRaisesRegex(UserError,
                "The from/to time range overlaps with the following rules: '4 to 6 \(P1\)'",
                br_obj.save)

    @with_transaction()
    def test_breaktime_create_item_twice_same_maxtime(self):
        """ test: create break time item twice - same maxtime
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        breaktime = self.prep_breaktime()

        with set_company(breaktime.tariff.company):
            br_obj = BreakTime(
                    name='6 to 8', shortname='P2', 
                    mintime=timedelta(seconds=3*60*60 ),
                    maxtime=timedelta(seconds=5*60*60 + 59*60 + 59),
                    deduction=timedelta(seconds=1*60*60),
                    tariff=breaktime.tariff,
                )
            self.assertRaisesRegex(UserError,
                "The from/to time range overlaps with the following rules: '4 to 6 \(P1\)'",
                br_obj.save)
            
    def prep_ruleset(self):
        """ create ruleset
        """
        # create a tariff and write new company to context
        company = create_company('m-ds 1')
        self.assertTrue(company)
        tar1 = create_tariff('Tar 1', 'T1', company=company)
        self.assertTrue(tar1)
        with set_company(tar1.company):            
            # create break time
            create_breaktime(name='0 to 3:59 / 20min', shortname='P0', \
                            mintime=timedelta(seconds=0),
                            maxtime=timedelta(seconds=3*60*60 + 59*60 + 59),
                            deduction=timedelta(seconds=20*60),
                            tariff=tar1
                            )
            create_breaktime(name='4 to 5:59 / 30min', shortname='P1', \
                            mintime=timedelta(seconds=4*60*60),
                            maxtime=timedelta(seconds=5*60*60 + 59*60 + 59),
                            deduction=timedelta(seconds=30*60),
                            tariff=tar1
                            )
            create_breaktime(name='6 to 7:59 / 45min', shortname='P2', \
                            mintime=timedelta(seconds=6*60*60),
                            maxtime=timedelta(seconds=7*60*60 + 59*60 + 59),
                            deduction=timedelta(seconds=45*60),
                            tariff=tar1
                            )
            create_breaktime(name='8 to 9:59 / 60min', shortname='P3', \
                            mintime=timedelta(seconds=8*60*60),
                            maxtime=timedelta(seconds=9*60*60 + 59*60 + 59),
                            deduction=timedelta(seconds=60*60),
                            tariff=tar1
                            )
        return tar1

    @with_transaction()
    def test_breaktime_reduced_worktime_7h45_break_15_to_7h(self):
        """ test: calculate reduced worktime: 7h45m - 15m employee-break --> 7h00m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=7*60*60 + 45*60), timedelta(seconds=15*60))
        self.assertEqual(str(wtime), '7:00:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_7h45_break_40_to_7h(self):
        """ test: calculate reduced worktime: 7h45m - 40m employee-break --> 7h00m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=7*60*60 + 45*60), timedelta(seconds=40*60))
        self.assertEqual(str(wtime), '7:00:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_7h45_break_50_to_6h55m(self):
        """ test: calculate reduced worktime: 7h45m - 50m employee-break --> 6h55m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=7*60*60 + 45*60), timedelta(seconds=50*60))
        self.assertEqual(str(wtime), '6:55:00')
        self.assertEqual(str(btime), '0:50:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_6h50_break_40_to_6h05m(self):
        """ test: calculate reduced worktime: 6h50m - 40m employee-break --> 6h05m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=6*60*60 + 50*60), timedelta(seconds=40*60))
        self.assertEqual(str(wtime), '6:05:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_6h50_break_55_to_5h55m(self):
        """ test: calculate reduced worktime: 6h50m - 55m employee-break --> 5h55m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=6*60*60 + 50*60), timedelta(seconds=55*60))
        self.assertEqual(str(wtime), '5:55:00')
        self.assertEqual(str(btime), '0:55:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_10h50_break_45_to_9h50m(self):
        """ test: calculate reduced worktime: 10h50m - 45m employee-break --> 9h50m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=10*60*60 + 50*60), timedelta(seconds=45*60))
        self.assertEqual(str(wtime), '9:50:00')
        self.assertEqual(str(btime), '1:00:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_10h50_break_55_to_9h50m(self):
        """ test: calculate reduced worktime: 10h50m - 55m employee-break --> 9h50m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=10*60*60 + 50*60), timedelta(seconds=55*60))
        self.assertEqual(str(wtime), '9:50:00')
        self.assertEqual(str(btime), '1:00:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_10h50_break_65_to_9h45m(self):
        """ test: calculate reduced worktime: 10h50m - 65m employee-break --> 9h45m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=10*60*60 + 50*60), timedelta(seconds=65*60))
        self.assertEqual(str(wtime), '9:45:00')
        self.assertEqual(str(btime), '1:05:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_4h20m_to_4h(self):
        """ test: calculate reduced worktime: 4h20m --> 4h
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=4*60*60 + 20*60), timedelta(seconds=0))
        self.assertEqual(str(wtime),'3:50:00')
        self.assertEqual(str(btime),'0:30:00')
        
    @with_transaction()
    def test_breaktime_reduced_worktime_4h50m_to_4h20m(self):
        """ test: calculate reduced worktime: 4h50m --> 4h20m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=4*60*60 + 50*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '4:20:00')
        self.assertEqual(str(btime), '0:30:00')
        
    @with_transaction()
    def test_breaktime_reduced_worktime_5h50m_to_5h20m(self):
        """ test: calculate reduced worktime: 5h50m --> 5h20h
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=5*60*60 + 50*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '5:20:00')
        self.assertEqual(str(btime), '0:30:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_6h00m_to_5h30m(self):
        """ test: calculate reduced worktime: 6h00m --> 5h30h
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=6*60*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '5:30:00')
        self.assertEqual(str(btime), '0:30:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_6h10m_to_5h30m(self):
        """ test: calculate reduced worktime: 6h10m --> 5h30h
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=6*60*60 + 10*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '5:30:00')
        self.assertEqual(str(btime), '0:40:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_6h15m_to_5h30m(self):
        """ test: calculate reduced worktime: 6h15m --> 5h30h
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=6*60*60 + 15*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '5:30:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_6h20m_to_5h35m(self):
        """ test: calculate reduced worktime: 6h20m --> 5h35h
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=6*60*60 + 20*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '5:35:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_6h30m_to_5h45m(self):
        """ test: calculate reduced worktime: 6h30m --> 5h45
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=6*60*60 + 30*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '5:45:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_6h58m_to_6h13m(self):
        """ test: calculate reduced worktime: 6h58m --> 6h13m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=6*60*60 + 58*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '6:13:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_7h10m_to_6h25m(self):
        """ test: calculate reduced worktime: 7h10m --> 6h25m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=7*60*60 + 10*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '6:25:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_7h58m_to_7h13m(self):
        """ test: calculate reduced worktime: 7h58m --> 7h13m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=7*60*60 + 58*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '7:13:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_8h00m_to_7h15m(self):
        """ test: calculate reduced worktime: 8h00m --> 7h15m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=8*60*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '7:15:00')
        self.assertEqual(str(btime), '0:45:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_8h14m_to_7h15m(self):
        """ test: calculate reduced worktime: 8h14m --> 7h15m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=8*60*60 + 14*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '7:15:00')
        self.assertEqual(str(btime), '0:59:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_8h16m_to_7h16m(self):
        """ test: calculate reduced worktime: 8h16m --> 7h16m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=8*60*60 + 16*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '7:16:00')
        self.assertEqual(str(btime), '1:00:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_8h45m_to_7h45m(self):
        """ test: calculate reduced worktime: 8h45m --> 7h45m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=8*60*60 + 45*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '7:45:00')
        self.assertEqual(str(btime), '1:00:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_0h45m_to_0h25m(self):
        """ test: calculate reduced worktime: 0h45m --> 0h25m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=45*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '0:25:00')
        self.assertEqual(str(btime), '0:20:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_0h15m_to_0h00m(self):
        """ test: calculate reduced worktime: 0h15m --> 0h00m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=15*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '0:00:00')
        self.assertEqual(str(btime), '0:15:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_3h30m_to_3h10m(self):
        """ test: calculate reduced worktime: 3h30m --> 3h10m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=3*60*60 + 30*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '3:10:00')
        self.assertEqual(str(btime), '0:20:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_10h30m_to_9h30m(self):
        """ test: calculate reduced worktime: 10h30m --> 9h30m
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, timedelta(seconds=10*60*60 + 30*60), timedelta(seconds=0))
        self.assertEqual(str(wtime), '9:30:00')
        self.assertEqual(str(btime), '1:00:00')

    @with_transaction()
    def test_breaktime_reduced_worktime_limit_rule_7h45m_to_7h15m(self):
        """ test: calculate reduced worktime: 7h45m --> 7h15m, limit availabe rules to '4 to 5:59 / 30min'
        """
        tar1 = self.prep_ruleset()
        BreakTime = Pool().get('employee_timetracking.breaktime')
        l1 = BreakTime.search([('tariff', '=', tar1), ('shortname', '=', 'P1')])
        
        (wtime, btime) = BreakTime.get_reduced_worktime(tar1, 
                                timedelta(seconds=3*60*60 + 30*60), 
                                timedelta(seconds=0),
                                domain=[('id', '=', l1[0].id)], 
                            )
        self.assertEqual(str(wtime), '3:30:00')
        self.assertEqual(str(btime), '0:00:00')

    @with_transaction()
    def test_breaktime_create_item_with_overlap(self):
        """ test: add item to db, check overlap function
        """
        company = create_company('m-ds 1')
        self.assertTrue(company)
        tar1 = create_tariff('Tar 1', 'T1', company=company)
        self.assertTrue(tar1)
        with set_company(tar1.company):
            # create break time
            BreakTime = Pool().get('employee_timetracking.breaktime')
            br1 = create_breaktime(name='4 to 5:59 / 30min', shortname='P1', \
                            mintime=timedelta(seconds=4*60*60),
                            maxtime=timedelta(seconds=5*60*60 + 59*60 + 59),
                            deduction=timedelta(seconds=30*60),
                            tariff=tar1
                            )

            self.assertEqual(
                BreakTime.check_overlap([br1], timedelta(seconds=6*60*60), timedelta(seconds=7*60*60 + 59*60 + 59)),
                [])
            # find overlap at begin
            self.assertEqual(
                BreakTime.check_overlap([br1], timedelta(seconds=3*60*60), timedelta(seconds=4*60*60 + 59*60 + 59)),
                [br1.id])
            # find overlap at end
            self.assertEqual(
                BreakTime.check_overlap([br1], timedelta(seconds=5*60*60), timedelta(seconds=6*60*60 + 59*60 + 59)),
                [br1.id])
            # ignore overlap at end
            self.assertEqual(
                BreakTime.check_overlap([br1], timedelta(seconds=5*60*60), timedelta(seconds=6*60*60 + 59*60 + 59), br1),
                [])

# end BreakTimeTestCase
