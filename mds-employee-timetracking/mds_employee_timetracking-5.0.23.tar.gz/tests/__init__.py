# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import trytond.tests.test_tryton
import unittest

try:
    from trytond.modules.employee_timetracking.tests.test_calendar import CalendarTestCase
    from trytond.modules.employee_timetracking.tests.test_presence import TypeOfPresenceTestCase
    from trytond.modules.employee_timetracking.tests.test_daysofevaluation import DaysOfEvaluationTestCase
    from trytond.modules.employee_timetracking.tests.test_breaktime import BreakTimeTestCase
    from trytond.modules.employee_timetracking.tests.test_accountrule import AccountRuleTestCase
    from trytond.modules.employee_timetracking.tests.test_tariffmodel import TariffModelTestCase
    from trytond.modules.employee_timetracking.tests.test_employee import EmployeeTestCase
    from trytond.modules.employee_timetracking.tests.test_breakperiod import BreakperiodTestCase
    from trytond.modules.employee_timetracking.tests.test_period import PeriodTestCase
    from trytond.modules.employee_timetracking.tests.test_period_wizard import PeriodWizardTestCase
    from trytond.modules.employee_timetracking.tests.test_employee_wizard import EmployeeWizardTestCase
    from trytond.modules.employee_timetracking.tests.test_timeaccount import TimeAccountTestCase
    from trytond.modules.employee_timetracking.tests.test_timeaccountitem import TimeAccountItemTestCase
    from trytond.modules.employee_timetracking.tests.test_evaluation import EvaluationTestCase
    from trytond.modules.employee_timetracking.tests.test_evaluation_holidays import EvaluationHolidaysTestCase
    from trytond.modules.employee_timetracking.tests.test_evaluation_sickdays import EvaluationSickdaysTestCase
    from trytond.modules.employee_timetracking.tests.test_worktimemodel import WorktimemodelTestCase
    from trytond.modules.employee_timetracking.tests.test_holiday import HolidayTestCase
    from trytond.modules.employee_timetracking.tests.test_report_lib import ReportLibTestCase
    from trytond.modules.employee_timetracking.tests.test_tools import ToolsTestCase
except ImportError:
    from .test_calendar import CalendarTestCase
    from .test_presence import TypeOfPresenceTestCase
    from .test_daysofevaluation import DaysOfEvaluationTestCase
    from .test_breaktime import BreakTimeTestCase
    from .test_accountrule import AccountRuleTestCase
    from .test_tariffmodel import TariffModelTestCase
    from .tests.test_employee import EmployeeTestCase
    from .test_breakperiod import BreakperiodTestCase
    from .test_period import PeriodTestCase
    from .test_period_wizard import PeriodWizardTestCase
    from .test_employee_wizard import EmployeeWizardTestCase
    from .test_timeaccount import TimeAccountTestCase
    from .test_timeaccountitem import TimeAccountItemTestCase
    from .test_evaluation import EvaluationTestCase
    from .test_evaluation_holidays import EvaluationHolidaysTestCase
    from .test_evaluation_sickdays import EvaluationSickdaysTestCase
    from .test_worktimemodel import WorktimemodelTestCase
    from .test_holiday import HolidayTestCase
    from .test_report_lib import ReportLibTestCase
    from .test_tools import ToolsTestCase

__all__ = ['suite']


class EmployeeTimetrackingTestCase(\
            EvaluationSickdaysTestCase,\
            CalendarTestCase,\
            TypeOfPresenceTestCase,\
            DaysOfEvaluationTestCase,\
            BreakTimeTestCase, \
            AccountRuleTestCase, \
            TariffModelTestCase,\
            EmployeeTestCase, \
            BreakperiodTestCase,\
            PeriodTestCase, \
            PeriodWizardTestCase, \
            EmployeeWizardTestCase, \
            TimeAccountTestCase, \
            TimeAccountItemTestCase, \
            EvaluationTestCase, \
            EvaluationHolidaysTestCase,\
            WorktimemodelTestCase, \
            HolidayTestCase, \
            ReportLibTestCase, \
            ToolsTestCase):
    'Test employe-timetracking module'
    module = 'employee_timetracking'

#end EmployeeTimetrackingTestCase


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(EmployeeTimetrackingTestCase))
    return suite
