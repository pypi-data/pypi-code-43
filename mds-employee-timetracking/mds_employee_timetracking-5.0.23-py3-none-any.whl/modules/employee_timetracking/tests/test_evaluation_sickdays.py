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


class EvaluationSickdaysTestCase(ModuleTestCase):
    'Test evaluation-sickdays module'
    module = 'employee_timetracking'

    def prep_evalsickdays_eval(self):
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
            
            evobj = create_evaluation(employee1, date(2019, 8, 4))

            self.assertTrue(evobj)
            self.assertEqual(evobj.rec_name, 'Frida - 2019-08')
        return evobj

    @with_transaction()
    def test_evalsickdays_create_valid(self):
        """ test: create valid sick day
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')

        evobj = self.prep_evalsickdays_eval()
        evobj.needs_recalc = False
        evobj.save()
        self.assertEqual(evobj.needs_recalc, False)
        
        evobj.sickdays = [
                EvalSick(date_start = date(2019, 8, 4),
                        date_end = date(2019, 8, 6)
                    )
            ]
        evobj.save()
        self.assertEqual(evobj.needs_recalc, True)

        eh_lst = EvalSick.search([])
        self.assertEqual(len(eh_lst), 1)
        self.assertEqual(str(eh_lst[0].date_start), '2019-08-04')
        self.assertEqual(str(eh_lst[0].date_end), '2019-08-06')
        self.assertEqual(eh_lst[0].eval_state, 'c')

    @with_transaction()
    def test_evalsickdays_create_valid2(self):
        """ test: create valid sick day, 2nd way
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()
        
        ev1 = EvalSick(
                date_start = date(2019, 8, 5),
                date_end = date(2019, 8, 8),
                evaluation = evobj)
        ev1.save()
        
        eh_lst = EvalSick.search([])
        self.assertEqual(len(eh_lst), 1)
        self.assertEqual(str(eh_lst[0].date_start), '2019-08-05')
        self.assertEqual(str(eh_lst[0].date_end), '2019-08-08')

    @with_transaction()
    def test_evalsickdays_edit_sick_day_checkrecalc(self):
        """ test: create sick day, edit it, check reclac of evaluation
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()
        
        evobj.sickdays = [
                EvalSick(date_start = date(2019, 8, 10),
                        date_end = date(2019, 8, 15)
                    )
            ]
        evobj.save()
        self.assertEqual(evobj.needs_recalc, True)
        evobj.needs_recalc = False
        evobj.save()
        
        self.assertEqual(evobj.needs_recalc, False)

        eh_lst = EvalSick.search([])
        self.assertEqual(len(eh_lst), 1)
        eh_lst[0].date_end = date(2019, 8, 14)
        eh_lst[0].save()
        
        self.assertEqual(evobj.needs_recalc, True)

    @with_transaction()
    def test_evalsickdays_delete_sick_day_checkrecalc(self):
        """ test: create sick day, edit it, check reclac of evaluation
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()
        evobj.sickdays = [
                EvalSick(date_start = date(2019, 8, 10),
                        date_end = date(2019, 8, 22)
                    )
            ]
        evobj.save()
        eh_lst = EvalSick.search([])
        self.assertEqual(len(eh_lst), 1)      
        self.assertEqual(evobj.needs_recalc, True)
        
        evobj.needs_recalc = False
        evobj.save()
        self.assertEqual(evobj.needs_recalc, False)

        EvalSick.delete(eh_lst)
        self.assertEqual(evobj.needs_recalc, True)

    @with_transaction()
    def test_evalsickdays_check_unique_start(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        # same start
        ev1 = EvalSick(
                date_start = date(2019, 8, 3),
                date_end = date(2019, 8, 5),
                evaluation = evobj)
        ev1.save()
        
        ev2 = EvalSick(
                date_start = date(2019, 8, 3),
                date_end = date(2019, 8, 7),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                'There is already an entry for this start date.',
                ev2.save)

    @with_transaction()
    def test_evalsickdays_check_unique_end(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        # same end
        ev1 = EvalSick(
                date_start = date(2019, 8, 3),
                date_end = date(2019, 8, 5),
                evaluation = evobj)
        ev1.save()
        
        ev2 = EvalSick(
                date_start = date(2019, 8, 4),
                date_end = date(2019, 8, 5),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                'There is already an entry for this end date.',
                ev2.save)

    @with_transaction()
    def test_evalsickdays_check_start_after_end(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        # start after end
        ev1 = EvalSick(
                date_start = date(2019, 8, 15),
                date_end = date(2019, 8, 12),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                'The end date must be after the start date.',
                ev1.save)

    @with_transaction()
    def test_evalsickdays_check_end_outside_month(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')

        evobj = self.prep_evalsickdays_eval()

        # end outside evaluation-month
        ev2 = EvalSick(
                date_start = date(2019, 8, 25),
                date_end = date(2019, 9, 5),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                "The beginning and end of the sickday entry must be in the range of '2019-08-01' to '2019-08-31'.",
                ev2.save)

    @with_transaction()
    def test_evalsickdays_check_end_outside_month2(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        ev2 = EvalSick(
                date_start = date(2019, 8, 25),
                date_end = date(2019, 8, 27),
                evaluation = evobj)
        ev2.save()
        
        # end outside evaluation-month
        ev2.date_end = date(2019, 9, 27)
        self.assertRaisesRegex(UserError,
                "The beginning and end of the sickday entry must be in the range of '2019-08-01' to '2019-08-31'.",
                ev2.save)

    @with_transaction()
    def test_evalsickdays_check_startend_outside_month(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        # start+end outside evaluation-month
        ev3 = EvalSick(
                date_start = date(2019, 9, 15),
                date_end = date(2019, 9, 17),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                "The beginning and end of the sickday entry must be in the range of '2019-08-01' to '2019-08-31'.",
                ev3.save)

    @with_transaction()
    def test_evalsickdays_check_startend_outside_month2(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        ev3 = EvalSick(
                date_start = date(2019, 8, 15),
                date_end = date(2019, 8, 17),
                evaluation = evobj)
        ev3.save()
        
        # start+end outside evaluation-month
        ev3.date_start = date(2019, 9, 15)
        ev3.date_end = date(2019, 9, 17)
        self.assertRaisesRegex(UserError,
                "The beginning and end of the sickday entry must be in the range of '2019-08-01' to '2019-08-31'.",
                ev3.save)

    @with_transaction()
    def test_evalsickdays_get_overlap_days(self):
        """ test: create sick day, check function 'get_overlap_days'
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        # overlap
        ev1 = EvalSick(
                date_start = date(2019, 8, 10),
                date_end = date(2019, 8, 15),
                evaluation = evobj)
        ev1.save()
        
        # no overlap
        self.assertEqual(
            EvalSick.get_overlap_days(evobj, date(2019, 8, 6), date(2019, 8, 7)), 
            [])

        # overlap at start
        e1 = EvalSick.get_overlap_days(evobj, date(2019, 8, 6), date(2019, 8, 12))
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1[0], ev1.id)

        # overlap at end
        e1 = EvalSick.get_overlap_days(evobj, date(2019, 8, 13), date(2019, 8, 18))
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1[0], ev1.id)

        # overlap inside
        e1 = EvalSick.get_overlap_days(evobj, date(2019, 8, 12), date(2019, 8, 14))
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1[0], ev1.id)

        # overlap around
        e1 = EvalSick.get_overlap_days(evobj, date(2019, 8, 8), date(2019, 8, 18))
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1[0], ev1.id)

        # overlap around + ignore ev1
        e1 = EvalSick.get_overlap_days(evobj, date(2019, 8, 8), date(2019, 8, 18), ignore_ids=[ev1.id])
        self.assertEqual(len(e1), 0)

    @with_transaction()
    def test_evalsickdays_check_create_overlap1(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        ev2 = EvalSick(
                date_start = date(2019, 8, 10),
                date_end = date(2019, 8, 17),
                evaluation = evobj)
        ev2.save()
        
        ev3 = EvalSick(
                date_start = date(2019, 8, 7),
                date_end = date(2019, 8, 14),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                "The item '2019-08-07 - 2019-08-14' overlaps with '2019-08-10 - 2019-08-17' in the evaluation 'Frida - 2019-08'.",
                ev3.save)

    @with_transaction()
    def test_evalsickdays_check_create_overlap2(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        ev2 = EvalSick(
                date_start = date(2019, 8, 10),
                date_end = date(2019, 8, 17),
                evaluation = evobj)
        ev2.save()
        
        # a single day item
        ev3 = EvalSick(
                date_start = date(2019, 8, 12),
                date_end = date(2019, 8, 12),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
                "The item '2019-08-12' overlaps with '2019-08-10 - 2019-08-17' in the evaluation 'Frida - 2019-08'.",
                ev3.save)

    @with_transaction()
    def test_evalsickdays_check_edit_overlap1(self):
        """ test: create sick day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        ev2 = EvalSick(
                date_start = date(2019, 8, 10),
                date_end = date(2019, 8, 17),
                evaluation = evobj)
        ev2.save()
        
        ev3 = EvalSick(
                date_start = date(2019, 8, 7),
                date_end = date(2019, 8, 8),
                evaluation = evobj)
        ev3.save()
        
        ev3.date_end = date(2019, 8, 14)
        self.assertRaisesRegex(UserError,
                "The item '2019-08-07 - 2019-08-14' overlaps with '2019-08-10 - 2019-08-17' in the evaluation 'Frida - 2019-08'.",
                ev3.save)

    @with_transaction()
    def test_evalholidays_check_edit_overlap2(self):
        """ test: create vacancy day, check daterange-contraints
        """
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        
        evobj = self.prep_evalsickdays_eval()

        ev2 = EvalSick(
                date_start = date(2019, 8, 10),
                date_end = date(2019, 8, 17),
                evaluation = evobj)
        ev2.save()
        
        # single day
        ev3 = EvalSick(
                date_start = date(2019, 8, 7),
                date_end = date(2019, 8, 7),
                evaluation = evobj)
        ev3.save()
        
        ev3.date_start = date(2019, 8, 14)
        ev3.date_end = date(2019, 8, 14)
        self.assertRaisesRegex(UserError,
                "The item '2019-08-14' overlaps with '2019-08-10 - 2019-08-17' in the evaluation 'Frida - 2019-08'.",
                ev3.save)

    @with_transaction()
    def test_evalsickdays_create_with_locked_eval(self):
        """ test: create sick day, check locking
        """
        pool = Pool()
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        evobj = self.prep_evalsickdays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')
        Evaluation.wflock([evobj])
        self.assertEqual(evobj.state, 'l')

        ev1 = EvalSick(
                date_start = date(2019, 8, 10),
                date_end = date(2019, 8, 22),
                evaluation = evobj)
        self.assertRaisesRegex(UserError,
            "The evaluation 'Frida - 2019-08' is locked, therefore the entry can not be created or changed.",
            ev1.save)

    @with_transaction()
    def test_evalsickdays_edit_with_locked_eval(self):
        """ test: create sick day, check locking
        """
        pool = Pool()
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        evobj = self.prep_evalsickdays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')

        ev1 = EvalSick(
                date_start = date(2019, 8, 10),
                date_end = date(2019, 8, 22),
                evaluation = evobj)
        ev1.save()

        Evaluation.wflock([evobj])
        self.assertEqual(evobj.state, 'l')

        ev1.date_end = date(2019, 8, 23)
        self.assertRaisesRegex(UserError,
            "The evaluation 'Frida - 2019-08' is locked, therefore the entry can not be created or changed.",
            ev1.save)

    @with_transaction()
    def test_evalsickdays_delete_with_locked_eval(self):
        """ test: create sick day, check locking
        """
        pool = Pool()
        EvalSick = Pool().get('employee_timetracking.evaluation_sickdays')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        evobj = self.prep_evalsickdays_eval()
        self.assertEqual(evobj.state, 'c')
        Evaluation.wfactivate([evobj])
        self.assertEqual(evobj.state, 'a')

        ev1 = EvalSick(
                date_start = date(2019, 8, 10),
                date_end = date(2019, 8, 22),
                evaluation = evobj)
        ev1.save()

        Evaluation.wflock([evobj])
        self.assertEqual(evobj.state, 'l')

        self.assertRaisesRegex(UserError,
            "The evaluation 'Frida - 2019-08' is locked, therefore the entry can not be created or changed.",
            EvalSick.delete,
            [ev1])

# end EvaluationSickdaysTestCase
