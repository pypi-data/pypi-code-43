# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.tests.testlib import create_worktimemodel,\
    create_worktimerule
from datetime import time


class WorktimemodelTestCase(ModuleTestCase):
    'Test work time model module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_worktimemodel_create_item(self):
        """ test: create work time model, add a rule, check defaults
        """
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')
            self.assertEqual(m1.shortname, 'M1')
            self.assertEqual(m1.rec_name, 'model 1 - 0.0 h')
            self.assertEqual(m1.company.party.name, 'm-ds')

            r1 = create_worktimerule(m1, 'R1')
            r1.mon = True
            r1.tue = False
            r1.save()
            self.assertEqual(r1.name, 'R1')
            self.assertEqual(r1.wtmodel.name, 'model 1')
            self.assertEqual(r1.mon, True)
            self.assertEqual(r1.tue, False)
            self.assertEqual(r1.wed, True)
            self.assertEqual(r1.thu, True)
            self.assertEqual(r1.fri, True)
            self.assertEqual(r1.sat, False)
            self.assertEqual(r1.sun, False)

            r2 = create_worktimerule(m1, 'R2', para={'mintime': time(2,0), 'maxtime':time(3,0)})
            r2.wed = True
            r2.thu = True
            r2.save()
            m1.worktimerule = [r1, r2]
            m1.save()
            self.assertEqual(len(m1.worktimerule), 2)

    @with_transaction()
    def test_worktimemodel_model_twice_same_name(self):
        """ test: create 2x work time model, check constraints
        """
        WorkTimeModel = Pool().get('employee_timetracking.worktimemodel')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')
            self.assertEqual(m1.shortname, 'M1')
            self.assertEqual(m1.company.party.name, 'm-ds')

            # same name
            wt_obj = WorkTimeModel(
                name='model 1', 
                shortname='M1a', 
                company=company1)
            self.assertRaisesRegex(UserError, 
                "This name is already in use.",
                wt_obj.save)

    @with_transaction()
    def test_worktimemodel_model_twice_same_shortname(self):
        """ test: create 2x work time model, check constraints
        """
        WorkTimeModel = Pool().get('employee_timetracking.worktimemodel')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')
            self.assertEqual(m1.shortname, 'M1')
            self.assertEqual(m1.company.party.name, 'm-ds')

            # same shortname
            wt_obj = WorkTimeModel(
                name='model 1 a', 
                shortname='M1', 
                company=company1)
            self.assertRaisesRegex(UserError, 
                "This shorthand symbol is already in use.",
                wt_obj.save)

    @with_transaction()
    def test_worktimemodel_model_twice_different_names(self):
        """ test: create 2x work time model, check constraints
        """
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')
            self.assertEqual(m1.shortname, 'M1')
            self.assertEqual(m1.company.party.name, 'm-ds')

            self.assertTrue(create_worktimemodel('model 2', 'M2', company1))

    @with_transaction()
    def test_worktimemodel_rule_constraint_name(self):
        """ test: create 1x work time model + rules, check name-constraints
        """
        WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')

            r1 = create_worktimerule(m1, 'R1', para={'mintime': time(2,0), 'maxtime':time(3,0), 'mon': True})
            m1.worktimerule = [r1]
            m1.save()
            self.assertEqual(len(m1.worktimerule), 1)

            wt_obj = WorkTimeRule(
                wtmodel=m1,
                name='R1',
                mon=True,
                tue=WorkTimeRule.default_tue(),
                wed=WorkTimeRule.default_wed(),
                thu=WorkTimeRule.default_thu(),
                fri=WorkTimeRule.default_fri(),
                sat=WorkTimeRule.default_sat(),
                sun=WorkTimeRule.default_sun(),
                mintime=time(4,0),
                maxtime=time(5,0))
            self.assertRaisesRegex(UserError, 
                "This name is already in use.",
                wt_obj.save)

    @with_transaction()
    def test_worktimemodel_rule_constraint_order1(self):
        """ test: create 1x work time model + rules, check order-constraints
        """
        WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')

            r1 = create_worktimerule(m1, 'R1', para={'mintime': time(2,0), 'maxtime':time(3,0), 'mon': True})
            self.assertEqual(len(m1.worktimerule), 1)

            wt_obj = WorkTimeRule(
                wtmodel=m1,
                name='R2',
                mon=True,
                tue=WorkTimeRule.default_tue(),
                wed=WorkTimeRule.default_wed(),
                thu=WorkTimeRule.default_thu(),
                fri=WorkTimeRule.default_fri(),
                sat=WorkTimeRule.default_sat(),
                sun=WorkTimeRule.default_sun(),
                mintime=time(6,0),
                maxtime=time(4,0))
            self.assertRaisesRegex(UserError, 
                "'to' must be creater than 'from'",
                wt_obj.save)

    @with_transaction()
    def test_worktimemodel_rule_constraint_order2(self):
        """ test: create 1x work time model + rules, check order-constraints
        """
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')

            r1 = create_worktimerule(m1, 'R1', para={'mintime': time(2,0), 'maxtime':time(3,0), 'mon': True})
            self.assertEqual(len(m1.worktimerule), 1)

            r2 = create_worktimerule(m1, 'R2', para={'mintime': time(6,0), 'maxtime':time(0, 0), 'mon': True})
            self.assertTrue(r2)

    @with_transaction()
    def test_worktimemodel_rule_constraint_weekday(self):
        """ test: create 1x work time model + rules, check weekday-constraints
        """
        WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')

            r1 = create_worktimerule(m1, 'R1', para={'mintime': time(2,0), 'maxtime':time(3,0), 'mon': True,
                'tue': False, 'wed': False, 'thu': False, 'fri': False, 'sat': False, 'sun': False})
            self.assertEqual(len(m1.worktimerule), 1)

            wt_obj = WorkTimeRule(
                wtmodel=m1,
                name='R2',
                mon=False,
                tue=False,
                wed=False,
                thu=False,
                fri=False,
                sat=False,
                sun=False,
                mintime=time(6,0),
                maxtime=time(7,0))
            self.assertRaisesRegex(UserError, 
                "at least one weekday must be activated",
                wt_obj.save)

    @with_transaction()
    def test_worktimemodel_hours_per_week(self):
        """ test: create 1x work time model, add rules, check hours/week
        """
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            self.assertEqual(m1.name, 'model 1')
            self.assertEqual(m1.shortname, 'M1')
            self.assertEqual(m1.company.party.name, 'm-ds')

            # 3x8h = 24h
            r1 = create_worktimerule(m1, 'R1', 
                    {'mon':True, 'tue':True, 'wed':True, 'thu':False, 
                     'fri':False, 'sat':False, 'sun':False, 
                     'mintime': time(8,0), 'maxtime': time(16,0)})

            # 2x 2h = 4h
            r2 = create_worktimerule(m1, 'R2', 
                    {'mon':False, 'tue':False, 'wed':False, 'thu':False, 
                     'fri':True, 'sat':True, 'sun':False, 
                     'mintime': time(10,0), 'maxtime': time(12,0)})

            # 3x 2h = 6h - nightshift
            r3 = create_worktimerule(m1, 'R3', 
                    {'mon':True, 'tue':True, 'wed':True, 'thu':False, 
                     'fri':False, 'sat':False, 'sun':False, 
                     'mintime': time(22,0), 'maxtime': time(0,0)})

            m1.worktimerule = [r1, r2, r3]
            m1.save()
            self.assertEqual(str(m1.hours_per_week), str('34.0'))
            self.assertEqual(m1.rec_name, 'model 1 - 34.0 h')

    @with_transaction()
    def test_worktimemodel_get_overlap_items(self):
        """ test: create 1x work time model, add rules, check hours/week
        """
        WorkTimeModel = Pool().get('employee_timetracking.worktimemodel')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)
            
            # check constraints
            p1 = {'mintime': time(9, 0), 'maxtime': time(11, 0), 'thu': True}
            v1 = WorkTimeModel.get_overlap_items(m1, p1)
            self.assertEqual(len(v1), 0)

            p1 = {'mintime': time(9, 0), 'maxtime': time(11, 0), 'thu': False}
            self.assertRaisesRegex(ValueError, 
                "Weekdays: enable min. 1x \!",
                WorkTimeModel.get_overlap_items,
                m1, p1)
            p1 = {'mintime': time(9, 0), 'maxtime': time(9, 0), 'thu': True}
            self.assertRaisesRegex(ValueError, 
                "Parameter: mintime < maxtime \!",
                WorkTimeModel.get_overlap_items,
                m1, p1)
            p1 = {'mintime': time(9, 0), 'maxtime': time(8, 0), 'thu': True}
            self.assertRaisesRegex(ValueError, 
                "Parameter: mintime < maxtime \!",
                WorkTimeModel.get_overlap_items,
                m1, p1)

            # 3x8h = 24h
            r1 = create_worktimerule(m1, 'R1', 
                    {'mon':True, 'tue':True, 'wed':True, 'thu':True, 
                     'fri':False, 'sat':False, 'sun':False, 
                     'mintime': time(8,0), 'maxtime': time(16,0)})
            r2 = create_worktimerule(m1, 'R2', 
                    {'mon':False, 'tue':False, 'wed':False, 'thu':True, 
                     'fri':True, 'sat':True, 'sun':False, 
                     'mintime': time(7,0), 'maxtime': time(7,55)})
            r3 = create_worktimerule(m1, 'R3', 
                    {'mon':True, 'tue':False, 'wed':False, 'thu':True, 
                     'fri':True, 'sat':True, 'sun':False, 
                     'mintime': time(22,0), 'maxtime': time(0,0)})

            m1.worktimerule = [r1, r2, r3]
            m1.save()
            
            p1 = {'mintime': time(7, 30), 'maxtime': time(8, 30), 'thu': True}
            v1 = WorkTimeModel.get_overlap_items(m1, p1)
            self.assertEqual(len(v1), 2)
            v2 = sorted(v1, key=lambda t1: t1.name)
            self.assertEqual(v2[0].name, 'R1')
            self.assertEqual(v2[1].name, 'R2')
            
            p1 = {'mintime': time(9, 0), 'maxtime': time(11, 0), 'thu': True}
            r2.thu = False
            r2.save()
            v1 = WorkTimeModel.get_overlap_items(m1, p1)
            self.assertEqual(len(v1), 1)
            self.assertEqual(v1[0].name, 'R1')
            
            # check min/max
            for i in [
                    {'mintime': time(6, 0), 'maxtime': time(9, 0), 'mon': True},
                    {'mintime': time(15, 0), 'maxtime': time(19, 0), 'mon': True},
                    {'mintime': time(5, 0), 'maxtime': time(19, 0), 'mon': True}
                ]:
                v1 = WorkTimeModel.get_overlap_items(m1, i)
                self.assertEqual(len(v1), 1)
                self.assertEqual(v1[0].name, 'R1')

            # find midnight-item
            for i in [
                    {'mintime': time(21, 0), 'maxtime': time(23, 0), 'mon': True},
                    {'mintime': time(21, 0), 'maxtime': time(0, 0), 'mon': True},
                    {'mintime': time(22, 0), 'maxtime': time(23, 0), 'mon': True},
                    {'mintime': time(22, 5), 'maxtime': time(23, 0), 'mon': True},
                    {'mintime': time(22, 5), 'maxtime': time(0, 0), 'mon': True},
                    {'mintime': time(22, 0), 'maxtime': time(0, 0), 'mon': True}
                ]:
                v1 = WorkTimeModel.get_overlap_items(m1, i)
                self.assertEqual(len(v1), 1)
                self.assertEqual(v1[0].name, 'R3')

            # no match
            p1 = {'mintime': time(17, 0), 'maxtime': time(18, 0), 'mon': True}
            v1 = WorkTimeModel.get_overlap_items(m1, p1)
            self.assertEqual(len(v1), 0)

    @with_transaction()
    def test_worktimemodel_check_overlap_valid(self):
        """ test: create 1x work time model, add rules, overlap-chcking
        """
        WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)

            r1 = WorkTimeRule(
                    wtmodel=m1, name='R1', mon=True, tue=True, wed=True, thu=True,
                    fri=True, sat=False, sun=False, mintime=time(8, 0), maxtime=time(16,0))
            r2 = WorkTimeRule(
                    wtmodel=m1, name='R2', mon=True, tue=True, wed=True, thu=True,
                    fri=True, sat=False, sun=False, mintime=time(18, 0), maxtime=time(20,0))
        
            m1.worktimerule = [r1, r2]
            m1.save()

    @with_transaction()
    def test_worktimemodel_check_overlap_create(self):
        """ test: create 1x work time model, add rules, overlap-checking
        """
        WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)

            r1 = WorkTimeRule(
                    wtmodel=m1, name='R1', mon=True, tue=True, wed=True, thu=True,
                    fri=True, sat=False, sun=False, mintime=time(8, 0), maxtime=time(16,0))
            r2 = WorkTimeRule(
                    wtmodel=m1, name='R2', mon=True, tue=True, wed=True, thu=True,
                    fri=True, sat=False, sun=False, mintime=time(6, 0), maxtime=time(9,0))
        
            m1.worktimerule = [r1, r2]
            self.assertRaisesRegex(UserError, 
                "The from/to time range overlaps with the following rules: R2 - 06:00-09:00 \[xxxxx__\]",
                m1.save)

    @with_transaction()
    def test_worktimemodel_check_overlap_edit(self):
        """ test: create 1x work time model, add rules, overlap-checking
        """
        WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
        
        company1 = create_company('m-ds')
        with set_company(company1):
            m1 = create_worktimemodel('model 1', 'M1', company1)

            r1 = WorkTimeRule(
                    wtmodel=m1, name='R1', mon=True, tue=True, wed=True, thu=True,
                    fri=True, sat=False, sun=False, mintime=time(8, 0), maxtime=time(16,0))
            r2 = WorkTimeRule(
                    wtmodel=m1, name='R2', mon=True, tue=True, wed=True, thu=True,
                    fri=True, sat=False, sun=False, mintime=time(6, 0), maxtime=time(7,0))

            m1.worktimerule = [r1, r2]
            m1.save()

            for i in m1.worktimerule:
                if i.name == 'R2':
                    i.maxtime = time(9,0)
                    self.assertRaisesRegex(UserError,
                        "The from/to time range overlaps with the following rules: R2 - 06:00-09:00 \[xxxxx__\]",
                        i.save)

# end WorktimemodelTestCase
