# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool, PoolMeta
from datetime import date
from .report_lib import ReportLib

__all__ = ['EvaluationMonthOdt']
__metaclass__ = PoolMeta


class EvaluationMonthOdt(ReportLib):
    __name__ = 'employee_timetracking.report_evaluation_month'

    reportfname = 'evaluation-month'
# end EvaluationMonthOdt
