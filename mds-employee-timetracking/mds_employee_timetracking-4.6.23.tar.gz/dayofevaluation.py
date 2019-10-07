# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# DayOfEvaluation: one item is stored per employee and day
# collects all infos of this day for this employee

from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from sql.functions import Extract, ToChar
from sql.conditionals import Coalesce, Case
from sql.aggregate import Sum
from sql import Cast
from datetime import date, timedelta
from .const import sel_weekday2, WF_BREAKPERIOD_EXAMINE, WF_BREAKPERIOD_LOCK,\
    VACDAY_NONE, VACDAY_FULL, VACDAY_HALF, sel_vacationday
from .tools import fmttimedelta, get_translation, round_timedelta


__all__ = ['DaysOfEvaluation']
__metaclass__ = PoolMeta


EVAL_WEEKEND = 'we'
EVAL_WEEKDAY = 'wd'
EVAL_HOLIDAY = 'hd'
sel_daytype = [
        (EVAL_WEEKEND, u'Weekend'),
        (EVAL_WEEKDAY, u'Weekday'),
        (EVAL_HOLIDAY, u'Holiday'),
    ]


class DaysOfEvaluation(ModelSQL, ModelView):
    "days of evaluation"
    __name__ = 'employee_timetracking.evaluation-dayofyear'

    evaluation = fields.Many2One(string=u"Evaluation", readonly=True, required=True,
        model_name='employee_timetracking.evaluation', select=True, ondelete='CASCADE')
    date = fields.Date(string=u'Date', readonly=True, required=True, select=True)
    dow = fields.Integer(string=u'Day of week', required=True, select=True)
    accountitem = fields.Many2One(string=u"Account item", readonly=True, 
        model_name='employee_timetracking.timeaccountitem', ondelete='SET NULL',
        help=u'Time account entry in the main time account')

    # views
    period = fields.Function(fields.Many2One(string=u"Presence time", readonly=True,
        model_name='employee_timetracking.period'), 'get_day_data')
    weekday = fields.Function(fields.Selection(string=u'Weekday', 
        selection=sel_weekday2, readonly=True), 'get_day_data')
    weekday_string  = weekday.translated('weekday')
    daytype = fields.Function(fields.Selection(string=u'Day type', 
        selection=sel_daytype, readonly=True), 'get_day_data')
    daytype_string  = daytype.translated('daytype')
    week = fields.Function(fields.Integer(string=u'Week', help=u'Calendar week', 
        readonly=True), 'get_day_data')
    startpos = fields.Function(fields.DateTime(string=u'Start', readonly=True), 
        'get_day_data', searcher='search_startpos')
    endpos = fields.Function(fields.DateTime(string=u'End', readonly=True), 
        'get_day_data', searcher='search_endpos')
    duration = fields.Function(fields.TimeDelta(string=u'Duration', readonly=True,
        help=u'Duration of the current time account item'), 'get_day_data')
    sumact = fields.Function(fields.TimeDelta(string=u'Actual', readonly=True,
        help=u'Actual time of all attendances for this day.'), 'get_day_data')
    holiday_ena = fields.Function(fields.Boolean(string=u'Holiday', readonly=True), 'get_day_data')
    holidayname = fields.Function(fields.Char(string=u'Holiday', readonly=True), 'get_day_data')
    targettime = fields.Function(fields.TimeDelta(string=u'Target', 
        readonly=True, help=u'Target working time'), 'get_day_data')
    sumbreaks = fields.Function(fields.TimeDelta(string=u'entered break times', 
        help=u'Sum of break times entered by the employee', readonly=True), 'get_day_data')
    vacationday = fields.Function(fields.Selection(string=u'Vacation Day', readonly=True, 
        selection=sel_vacationday), 'get_day_data', searcher='search_vacationday')
    sickday = fields.Function(fields.Boolean(string=u'Sick Day', readonly=True), 
        'get_day_data', searcher='search_sickday')

    # views
    diff = fields.Function(fields.TimeDelta(string=u'Difference', readonly=True,
        help=u'Difference between target time and actual time without breaks.'), 'get_break_info')
    wobreaks = fields.Function(fields.TimeDelta(string=u'Actual', 
        help=u'reduced working time due to break time', readonly=True), 'get_break_info')
    breaktime = fields.Function(fields.TimeDelta(string=u'break time', 
        help=u'used break time at this day', readonly=True), 'get_break_info')
    info = fields.Function(fields.Char(string=u'Info', readonly=True), 'on_change_with_info')
    accountitems_nonmain = fields.Function(fields.One2Many(string=u'other account items', readonly=True,
        model_name='employee_timetracking.timeaccountitem', field=None, 
        help=u'Time account entries in the other time accounts'), 'on_change_with_accountitems_nonmain')

    @classmethod
    def __register__(cls, module_name):
        super(DaysOfEvaluation, cls).__register__(module_name)
        cls.migrate_days()

    @classmethod
    def __setup__(cls):
        super(DaysOfEvaluation, cls).__setup__()
        cls._order.insert(0, ('startpos', 'ASC'))
        cls._order.insert(0, ('date', 'ASC'))

        tab_day = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_date',
            Unique(tab_day, tab_day.date, tab_day.evaluation, tab_day.accountitem),
            u'The date is already in use'),
            ('uniq_accitm',
            Unique(tab_day, tab_day.evaluation, tab_day.accountitem),
            u'The time-account-item is already in use'),
            ('weekday', 
            Check(tab_day, Cast(Extract('dow', tab_day.date), 'integer') == tab_day.dow), 
            u'Day-of-week mismatch.'),
            ])

    @classmethod
    def migrate_days(cls):
        """ add days for all evaluations
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')
        
        ev_lst = Evaluation.search([])
        cls.add_days_of_month(ev_lst)
        
        for i in ev_lst:
            acc_itm = TimeAccountItem.search([
                    ('evaluation', '=', i), 
                    ('id', 'not in', [getattr(x.accountitem, 'id', None) for x in i.days]),
                    ('account', '=', i.employee.tariff.main_timeaccount)
                ])
            for k in acc_itm:
                cls.updt_day_by_timeaccountitem(k)
    
    @classmethod
    def del_day_by_timeaccountitem(cls, tacc_item):
        """ disconnect/delete day if delete
        """
        # get day by time-account-item
        tacc_lst = DaysOfEvaluation.search([
                ('evaluation', '=', tacc_item.evaluation), 
                ('accountitem', '=', tacc_item)
            ])
        if len(tacc_lst) == 0:
            return
        elif len(tacc_lst) == 1:
            # get days with same date
            day_lst = DaysOfEvaluation.search([
                    ('evaluation', '=', tacc_item.evaluation), 
                    ('date', '=', tacc_lst[0].date)
                ])
            if len(day_lst) > 1:
                # connected day can be savely deleted
                DaysOfEvaluation.delete(tacc_lst)
            elif len(day_lst) == 1:
                # its the last day-item for this date, disconnect
                tacc_lst[0].accountitem = None
                tacc_lst[0].save()
            else :
                raise ValueError(u'bug in del_day_by_timeaccountitem (1)')
        else :
            raise ValueError(u'bug in del_day_by_timeaccountitem (2)')
    
    @classmethod
    def updt_day_by_timeaccountitem(cls, tacc_item):
        """ add/connect day with time-account-item
        """
        AccountRule = Pool().get('employee_timetracking.accountrule')
        
        # only connect item which are in main-time-account
        if tacc_item.account != tacc_item.employee.tariff.main_timeaccount:
            return

        date1 = AccountRule.get_localtime(tacc_item.startpos, tacc_item.employee.company.timezone)
        date2 = date(date1.year, date1.month, date1.day)
        
        # get not-connected-day for requested date
        day_lst = DaysOfEvaluation.search([
                    ('evaluation', '=', tacc_item.evaluation), 
                    ('date', '=', date2),
                    ('accountitem', '=', None)
                ])
        if len(day_lst) == 1:
            day_lst[0].accountitem = tacc_item
            day_lst[0].save()
        elif len(day_lst) == 0:
            # no free day-item, create one
            d_obj = DaysOfEvaluation()
            d_obj.evaluation = tacc_item.evaluation
            d_obj.date = date2
            d_obj.accountitem = tacc_item
            d_obj.save()
        else :
            raise ValueError(u'bug in updt_day_by_timeaccountitem')
        
    @classmethod
    def add_days_of_month(cls, evaluation_lst):
        """ add items
        """
        for ev1 in evaluation_lst:
            # get existing items
            d_lst = DaysOfEvaluation.search([('evaluation', '=', ev1)])
            date_lst = []
            for i in d_lst:
                date_lst.append(i.date)

            # add missing dates
            for i in range(ev1.datestart.day, ev1.dateend.day + 1):
                d1 = date(ev1.datestart.year, ev1.datestart.month, i)
                if not d1 in date_lst:
                    n_obj = DaysOfEvaluation()
                    n_obj.evaluation = ev1
                    n_obj.date = d1
                    n_obj.save()

    @staticmethod
    def order_startpos(tables):
        table, _ = tables[None]
        TimeAccountItem = Pool().get('employee_timetracking.timeaccountitem')
        tab_accitem = TimeAccountItem.__table__()

        qu1 = tab_accitem.select(tab_accitem.startpos,
                    where=(table.accountitem==tab_accitem.id)
                )
        return [qu1]
    
    @classmethod
    def get_target_worktime_sql(cls):
        """ sql-code for target worktime per day
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        DaysOfEvaluation = pool.get('employee_timetracking.evaluation-dayofyear')
        WorkTimeRule = pool.get('employee_timetracking.evaluation_wtrule')
        
        tab_eval = Evaluation.__table__()
        tab_wtrl = WorkTimeRule.__table__()
        tab_day = DaysOfEvaluation.__table__()

        tab_dates = tab_eval.join(tab_day, condition=tab_day.evaluation==tab_eval.id
            ).select(tab_eval.id.as_('evaluation'),
                tab_day.date,
                tab_day.dow,
                distinct_on=[tab_day.date, tab_eval.id]
            )
        tab_wt = tab_dates.join(tab_wtrl, condition=tab_wtrl.evaluation==tab_dates.evaluation
            ).select(tab_dates.evaluation,
                tab_dates.date,
                Sum(tab_wtrl.maxtime - tab_wtrl.mintime).as_('targtime'),
                where=((tab_dates.dow==1) & (tab_wtrl.mon == True)) |
                    ((tab_dates.dow==2) & (tab_wtrl.tue == True)) |
                    ((tab_dates.dow==3) & (tab_wtrl.wed == True)) |
                    ((tab_dates.dow==4) & (tab_wtrl.thu == True)) |
                    ((tab_dates.dow==5) & (tab_wtrl.fri == True)) |
                    ((tab_dates.dow==6) & (tab_wtrl.sat == True)) |
                    ((tab_dates.dow==0) & (tab_wtrl.sun == True)),
                group_by=[tab_dates.evaluation, tab_dates.date]
            )
        return tab_wt

    @classmethod
    def get_dates_of_month_sql(cls):
        """ sql-code: days of month, holidays, 
            selected to company
        """
        pool = Pool()
        Employee = pool.get('company.employee')
        Evaluation = pool.get('employee_timetracking.evaluation')
        DaysOfEvaluation = pool.get('employee_timetracking.evaluation-dayofyear')
        Holiday = pool.get('employee_timetracking.holiday')

        tab_emp = Employee.__table__()
        tab_eval = Evaluation.__table__()
        tab_doe = DaysOfEvaluation.__table__()
        tab_holi = Holiday.__table__()
        
        tab_days = tab_emp.join(tab_eval, condition=tab_eval.employee==tab_emp.id
            ).join(tab_doe, condition=tab_doe.evaluation==tab_eval.id
            ).join(tab_holi, 
                condition=(tab_holi.company==tab_emp.company) &
                    (
                        (
                            (tab_holi.repyear == True) &
                            (Extract('month', tab_holi.date) == Extract('month', tab_doe.date)) & 
                            (Extract('day', tab_holi.date) == Extract('day', tab_doe.date))
                        ) | (
                            (tab_holi.repyear == False) & (tab_holi.date == tab_doe.date)
                        )
                    ),
                type_ = 'LEFT OUTER'
            ).select(tab_eval.id.as_('evaluation'),
                tab_doe.id.as_('id_date'),
                tab_doe.date,
                tab_doe.accountitem,
                ToChar(tab_doe.dow, 'FM99').as_('weekday'),
                Cast(Extract('week', tab_doe.date), 'integer').as_('week'),
                Case(
                    (tab_holi.date != None, True),
                    else_ = False
                ).as_('holiday_ena'),
                tab_holi.halfday,
                tab_holi.name.as_('holidayname'),
                Case(
                    (tab_holi.date != None, EVAL_HOLIDAY),
                    ((tab_holi.date == None) & (tab_doe.dow.in_([0, 6])), EVAL_WEEKEND),
                    else_ = EVAL_WEEKDAY
                ).as_('daytype'),
            )
        return tab_days

    @classmethod
    def get_working_days_sql(cls):
        """ sql-code for days, weekday, week, holiday, daytype, targettime
        """
        tab_days = cls.get_dates_of_month_sql()
        tab_worktime = cls.get_target_worktime_sql()
        
        qu1 = tab_days.join(tab_worktime, 
                condition=(tab_worktime.evaluation==tab_days.evaluation) &
                    (tab_worktime.date==tab_days.date),
                type_='LEFT OUTER'
            ).select(tab_days.evaluation,
                tab_days.date,
                tab_days.id_date,
                tab_days.accountitem,
                tab_days.weekday,       
                tab_days.week,          # number of week in year (int)
                tab_days.holiday_ena,   # True = day is holiday (national, church, ...)
                tab_days.holidayname,   # title of holiday
                tab_days.daytype,       # weekday, weekend, holiday
                Case(
                    ((tab_days.holiday_ena == True) & (tab_days.halfday == True),   # half working time if half-day-holiday
                     Coalesce(tab_worktime.targtime, timedelta(seconds=0)) / 2),    
                    ((tab_days.holiday_ena == True) & (tab_days.halfday == False),  # no working time if full-day-holiday
                     timedelta(seconds=0)),
                    else_ = Coalesce(tab_worktime.targtime, timedelta(seconds=0))
                ).as_('targettime'),
            )
        return qu1

    @classmethod
    def get_eval_sumact_sql(cls):
        """ sql-code for sum of actual work time
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        DayOfEval = pool.get('employee_timetracking.evaluation-dayofyear')
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')

        tab_eval = Evaluation.__table__()
        tab_doe = DayOfEval.__table__()
        tab_tacc = TimeAccountItem.__table__()

        # list of items in main-time-account of employee
        tab_sumact = tab_eval.join(tab_doe, condition=tab_doe.evaluation==tab_eval.id
            ).join(tab_tacc, condition=tab_tacc.id==tab_doe.accountitem
            ).select(tab_eval.id.as_('evaluation'),
                tab_doe.date,
                Sum(tab_tacc.endpos - tab_tacc.startpos).as_('sumact'),
                group_by=[tab_doe.date, tab_eval.id]
            )
        return tab_sumact
        
    @classmethod
    def get_eval_sumbreaks_sql(cls):
        """ sql-code for sum of break time items
        """
        pool = Pool()
        Evaluation = pool.get('employee_timetracking.evaluation')
        DayOfEval = pool.get('employee_timetracking.evaluation-dayofyear')
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')
        BreakPeriod = pool.get('employee_timetracking.breakperiod')

        tab_eval = Evaluation.__table__()
        tab_doe = DayOfEval.__table__()
        tab_tacc = TimeAccountItem.__table__()
        tab_break = BreakPeriod.__table__()

        # list of items with break times in main-time-account of employee
        tab_sumbreaks = tab_eval.join(tab_doe, condition=tab_doe.evaluation==tab_eval.id
            ).join(tab_tacc, condition=tab_tacc.id==tab_doe.accountitem
            ).join(tab_break, 
                condition=(tab_break.employee==tab_eval.employee) & 
                    (tab_break.state.in_([WF_BREAKPERIOD_EXAMINE, WF_BREAKPERIOD_LOCK])) & (\
                    # break time within work time
                    ((tab_tacc.startpos <= tab_break.startpos) & (tab_break.startpos < tab_tacc.endpos) &
                     (tab_tacc.startpos < tab_break.endpos) & (tab_break.endpos <= tab_tacc.endpos)) |
                    # break time starts before work time
                    ((tab_break.startpos < tab_tacc.startpos) & 
                     (tab_tacc.startpos < tab_break.endpos) & (tab_break.endpos <= tab_tacc.endpos)) |
                    # break time ends after work time
                    ((tab_tacc.startpos <= tab_break.startpos) & (tab_break.startpos < tab_tacc.endpos) & 
                     (tab_tacc.endpos < tab_break.endpos))
                    )
            ).select(tab_eval.id.as_('evaluation'),
                tab_doe.date,
                Sum(
                    Case(
                        ((tab_tacc.startpos <= tab_break.startpos) & 
                         (tab_break.startpos < tab_tacc.endpos) &
                         (tab_tacc.startpos < tab_break.endpos) & 
                         (tab_break.endpos <= tab_tacc.endpos), tab_break.endpos - tab_break.startpos),
                        ((tab_break.startpos < tab_tacc.startpos) & 
                         (tab_tacc.startpos < tab_break.endpos) & 
                         (tab_break.endpos <= tab_tacc.endpos), tab_break.endpos - tab_tacc.startpos),
                        ((tab_tacc.startpos <= tab_break.startpos) & 
                         (tab_break.startpos < tab_tacc.endpos) & 
                         (tab_tacc.endpos < tab_break.endpos), tab_tacc.endpos - tab_break.startpos),
                        else_ = timedelta(seconds=0)
                    )
                ).as_('sumbreaks'),
                group_by=[tab_eval.id, tab_doe.date]
            )
        return tab_sumbreaks

    @classmethod
    def get_data_sql(cls):
        """ combine sql-queries for table result
        """
        pool = Pool()
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')
        VacationDays = pool.get('employee_timetracking.evaluation_vacationdays')
        SickDays = pool.get('employee_timetracking.evaluation_sickdays')

        # list of days per month (days, weekday, week, holiday, daytype, targettime)
        tab_workdays = cls.get_working_days_sql()
        # sum of working time per day, taken from time account items - checked in by employee
        tab_sumact = cls.get_eval_sumact_sql()
        tab_tacc = TimeAccountItem.__table__()
        # sum of break times per day, taken from break time items - checked in by employee
        tab_breaks = cls.get_eval_sumbreaks_sql()
        tab_vacday = VacationDays.__table__()
        tab_sickday = SickDays.__table__()

        tab_qu1 = tab_workdays.join(tab_sumact,
                condition=(tab_sumact.evaluation==tab_workdays.evaluation) &
                    (tab_sumact.date==tab_workdays.date),
                type_='LEFT OUTER'
            ).join(tab_breaks, 
                condition=(tab_breaks.evaluation==tab_workdays.evaluation) & 
                    (tab_breaks.date==tab_workdays.date),
                type_='LEFT OUTER'
            ).join(tab_tacc,
                condition=tab_workdays.accountitem==tab_tacc.id,
                type_='LEFT OUTER'
            ).join(tab_vacday, 
                condition=(tab_vacday.evaluation==tab_workdays.evaluation) &    # vacation day:
                    (tab_vacday.date_start <= tab_workdays.date) &              # - a planned vacation day exists at this day
                    (tab_workdays.date <= tab_vacday.date_end) &                #
                    (tab_workdays.targettime != timedelta(seconds=0)),          # - worktime model has a planned worktime at this day                    
                type_='LEFT OUTER'
            ).join(tab_sickday,
                condition=(tab_sickday.evaluation==tab_workdays.evaluation) &
                    (tab_sickday.date_start <= tab_workdays.date) &
                    (tab_workdays.date <= tab_sickday.date_end) &
                    (tab_workdays.targettime != timedelta(seconds=0)),
                type_='LEFT OUTER'
            ).select(tab_workdays.id_date.as_('id'),    # id of date item
                tab_workdays.evaluation,        # id of evaluation
                tab_workdays.date,              # date - date of working day
                tab_workdays.weekday,           # string - 0 = sun, 1 = mon, 2 = tue, 3 = wed, 4 = thu, 5 = fri, 6 = sat
                tab_workdays.week,              # integer - number of week in year
                tab_workdays.holiday_ena,       # boolean - True = day is holiday (national, church, ...)
                tab_workdays.holidayname,       # string - title of holiday
                tab_workdays.daytype,           # string - weekday (wd), weekend (we), holiday (hd)
                tab_workdays.targettime,        # timedelta - target working time at this day
                Case (                          # timedelta - sum of working time per day,
                    # sick day: at full/half-holiday -> use targtime
                    ((tab_sickday.date_start != None) & (tab_workdays.accountitem == None), tab_workdays.targettime),
                    ((tab_vacday.date_start != None) &  (tab_workdays.accountitem == None) &    # full vacation day
                     (tab_vacday.halfday != True) & (tab_sickday.date_start == None), tab_workdays.targettime),
                    ((tab_vacday.date_start != None) & (tab_vacday.halfday == True) &
                     (tab_sickday.date_start == None),                                          # half vacation day
                     Coalesce(tab_sumact.sumact, timedelta(seconds=0)) + tab_workdays.targettime / 2),
                    else_ = tab_sumact.sumact                                                   # no vacation day
                ).as_('sumact'),
                tab_tacc.id.as_('accountitem'), # id of time account item
                tab_tacc.period,                # id of period item, connected with time account item
                tab_tacc.startpos,              # datetime - start of working time
                tab_tacc.endpos,                # datetime - end of working time
                (tab_tacc.endpos - tab_tacc.startpos).as_('duration'),  # timedelta - duration of working time
                Coalesce(tab_breaks.sumbreaks, timedelta(seconds=0)).as_('sumbreaks'), # timedelta - sum of break times per day
                Case (
                    ((tab_vacday.date_start != None) & (tab_workdays.accountitem == None) & 
                     (tab_vacday.halfday != True), VACDAY_FULL),
                    ((tab_vacday.date_start != None) & (tab_vacday.halfday == True), VACDAY_HALF),
                    else_ = VACDAY_NONE
                ).as_('vacationday'),
                Case (
                    ((tab_sickday.date_start != None) & (tab_workdays.accountitem == None), True),
                    else_ = False
                ).as_('sickday'),
            )
        return tab_qu1

    @classmethod
    def search_sickday(cls, name, clause):
        """ search in sickday
        """
        tab_data = cls.get_data_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = tab_data.select(tab_data.id,
                where=Operator(tab_data.sickday, clause[2])
            )
        return [('id', 'in', qu1)]
        
    @classmethod
    def search_vacationday(cls, name, clause):
        """ search in vacationday
        """
        tab_data = cls.get_data_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = tab_data.select(tab_data.id,
                where=Operator(tab_data.vacationday, clause[2])
            )
        return [('id', 'in', qu1)]

    @classmethod
    def search_startpos(cls, name, clause):
        """ search in startpos
        """
        tab_data = cls.get_data_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = tab_data.select(tab_data.id,
                where=Operator(tab_data.startpos, clause[2])
            )
        return [('id', 'in', qu1)]
    
    @classmethod
    def search_endpos(cls, name, clause):
        """ search in endpos
        """
        tab_data = cls.get_data_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = tab_data.select(tab_data.id,
                where=Operator(tab_data.endpos, clause[2])
            )
        return [('id', 'in', qu1)]
    
    @classmethod
    def get_day_data(cls, days, names):
        """ get data for views
        """
        cursor = Transaction().connection.cursor()
        tab_data = cls.get_data_sql()
        
        r1 = {
                'period': {}, 'weekday': {}, 'daytype': {},
                'week': {}, 'startpos': {}, 'endpos': {}, 'duration': {},
                'sumact': {}, 'holiday_ena': {}, 'holidayname': {},
                'targettime': {}, 'sumbreaks': {}, 'vacationday': {},
                'sickday': {},
            }
        id_lst = [x.id for x in days]
        
        # prepare result
        for i in id_lst:
            for k in r1.keys():
                r1[k][i] = None
    
        qu1 = tab_data.select(tab_data.id,
                tab_data.period,
                tab_data.weekday,
                tab_data.daytype,
                tab_data.week,
                tab_data.startpos,
                tab_data.endpos,
                tab_data.duration,
                tab_data.sumact,
                tab_data.holiday_ena,
                tab_data.holidayname,
                tab_data.targettime,
                tab_data.sumbreaks,
                tab_data.vacationday,
                tab_data.sickday,
                where=tab_data.id.in_(id_lst),
                order_by=[tab_data.date, tab_data.startpos.desc]
            )
        
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        for i in l1:
            (id1, p1, wd1, dt1, w1, sp1, ep1, du1, su1, he1, hn1, tt1, sb1, vd1, skd1) = i
            r1['period'][id1] = p1
            r1['weekday'][id1] = wd1
            r1['daytype'][id1] = dt1
            r1['week'][id1] = w1
            r1['startpos'][id1] = sp1
            r1['endpos'][id1] = ep1
            r1['duration'][id1] = du1
            r1['sumact'][id1] = su1
            r1['holiday_ena'][id1] = he1
            r1['holidayname'][id1] = hn1
            r1['targettime'][id1] = tt1
            r1['sumbreaks'][id1] = sb1
            r1['vacationday'][id1] = vd1
            r1['sickday'][id1] = skd1

        # remove not requested fields
        r2 = {}
        for i in names:
            r2[i] = r1[i]
        return r2
        
    @classmethod
    def get_break_info(cls, days, names):
        """ gets info about breaks at this day
        """
        EvaluationBreakTime = Pool().get('employee_timetracking.evaluation_btrule')

        res = {'wobreaks': {}, 'breaktime': {}, 'diff': {}}
        
        for i in days:
            sumact2 = timedelta(seconds=0)
            targettime = timedelta(seconds=0)

            if isinstance(i.sumact, type(None)):
                (wtime, btime) = (None, None)
            else :
                if i.sickday == True:
                    wtime = i.sumact
                    btime =  i.sumbreaks
                elif i.vacationday == VACDAY_FULL:
                    wtime = i.sumact
                    btime =  i.sumbreaks
                elif i.vacationday == VACDAY_HALF:
                    # reduce sum of worktime by period of half vacantion day (half targettime)
                    # allow calculation of break times for remaining working time
                    (wtime, btime) = EvaluationBreakTime.get_reduced_worktime(i.evaluation,
                        i.sumact - i.targettime / 2, i.sumbreaks)
                    wtime += i.targettime / 2   # add vacation day period to fill up working time
                else:
                    (wtime, btime) = EvaluationBreakTime.get_reduced_worktime(i.evaluation,
                        i.sumact, i.sumbreaks)

            res['wobreaks'][i.id] = wtime
            res['breaktime'][i.id] = btime

            if not isinstance(i.targettime, type(None)):
                targettime = i.targettime
            if not isinstance(wtime, type(None)):
                sumact2 = wtime
            res['diff'][i.id] = sumact2 - targettime

        # remove not requested fields
        res2 = {}
        for i in names:
            res2[i] = res[i]
        return res2

    @fields.depends('daytype', 'holidayname', 'accountitems_nonmain', 'breaktime', 'vacationday', 'sickday')
    def on_change_with_info(self, name=None):
        """ generate info for day
        """
        t1 = ''

        # holiday
        if self.daytype == EVAL_HOLIDAY:
            t1 += self.holidayname
        elif self.daytype == EVAL_WEEKEND:
            if len(t1) > 0:
                t1 += ', '
            t1 += self.daytype_string

        if self.sickday == True:
            if len(t1) > 0:
                t1 += ', '
            t1 += get_translation('employee_timetracking.evaluation-dayofyear,sickday', 'field', 'Sick Day')
        elif self.vacationday == VACDAY_FULL:
            # vacation day - full
            if len(t1) > 0:
                t1 += ', '
            t1 += get_translation('employee_timetracking.evaluation-dayofyear,vacationday', 'selection', 'full vacation day')
        elif self.vacationday == VACDAY_HALF:
            # vacation day - half
            if len(t1) > 0:
                t1 += ', '
            t1 += get_translation('employee_timetracking.evaluation-dayofyear,vacationday', 'selection', 'half vacation day')
        
        # time which are not booked to the main-time-account
        for i in self.accountitems_nonmain:
            if len(t1) > 0:
                t1 += ', '
            t1 += '%s:%s' % (i.account.shortname, 
                             fmttimedelta(i.duration, noplussign=True, sepbyh=True))

        if isinstance(self.breaktime, type(timedelta(seconds=0))):
            if self.breaktime > timedelta(seconds=0):
                txt_break = get_translation('employee_timetracking.evaluation-dayofyear,info_pause', 'help', 'Break')
                if len(t1) > 0:
                    t1 += ', '
                t1 += '%s:%s' % (txt_break, fmttimedelta(self.breaktime, noplussign=True, sepbyh=True))
        return t1

    @fields.depends('accountitem', 'period')
    def on_change_with_accountitems_nonmain(self, name=None):
        """ get list of time-account-item, which are not booket to main-time-account
        """
        TimeAccountItem = Pool().get('employee_timetracking.timeaccountitem')
        
        if isinstance(self.period, type(None)) or isinstance(self.accountitem, type(None)):
            return []

        l1 = []
        ta1 = TimeAccountItem.search([
                    ('period', '=', self.period), 
                    ('id', '!=', self.accountitem.id),
                    ('startpos', '>=', self.accountitem.startpos),
                    ('endpos', '<=', self.accountitem.endpos)
                ], order=[('startpos', 'ASC')])
        return [x.id for x in ta1]

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if 'date' in values.keys():
                # python: tuesday = 1, sql tuesday = 2
                values['dow'] = values['date'].weekday() + 1
                if values['dow'] == 7:
                    values['dow'] = 0
        return super(DaysOfEvaluation, cls).create(vlist)

# end DaysOfEvaluation
