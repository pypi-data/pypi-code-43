# -*- coding: utf-8 -*-

from trytond.pool import Pool
from .presence import PresenceType
from .breaktime import BreakTime
from .accountrule import AccountRule
from .tariffmodel import TariffModel, PresenceRel
from .employee import Employee
from .period import Period
from .timeaccount import TimeAccount, TimeAccountItem
from .evaluation import Evaluation, EvaluationItem, RecalcEvaluation, EvaluationWorktime,\
    EvaluationBreakTime
from .dayofevaluation import DaysOfEvaluation
from .user import User
from .evaluation_report import EvaluationMonthOdt
from .evaluation_holidays import EvaluationVacationdays
from .evaluation_sickdays import EvaluationSickdays
from .period_wizard import PeriodAttendanceWizard, PeriodAttendanceWizardStart
from .employee_wizard import EmployeeCreateWizard, EmployeeCreateWizardStart
from .worktimemodel import WorkTimeModel, WorkTimeRule
from .holiday import Holiday
from .breakperiod import BreakPeriod
from .colors import Colors
from .calendar2 import Calendar, Event
from .configwizard import TimetrackingConfigStart, TimetrackingConfig

def register():
    Pool.register(
        Calendar,
        Event,
        User,
        Colors,
        PresenceType,
        BreakTime,
        AccountRule,
        TariffModel,
        PresenceRel,
        Employee,
        Period,
        TimeAccount,
        TimeAccountItem,
        Evaluation,
        EvaluationItem,
        EvaluationWorktime,
        EvaluationBreakTime,
        EvaluationVacationdays,
        EvaluationSickdays,
        DaysOfEvaluation,
        WorkTimeModel,
        WorkTimeRule,
        Holiday,
        BreakPeriod,
        PeriodAttendanceWizardStart,
        EmployeeCreateWizardStart,
        TimetrackingConfigStart,
        module='employee_timetracking', type_='model')
    Pool.register(
        EvaluationMonthOdt,
        module='employee_timetracking', type_='report')
    Pool.register(
        PeriodAttendanceWizard,
        EmployeeCreateWizard,
        RecalcEvaluation,
        TimetrackingConfig,
        module='employee_timetracking', type_='wizard')
