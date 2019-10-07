# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# The evaluation calculates the value of the time accounts according 
# to the time account rules. The evaluation is made monthly for each employee.


from trytond.model import Workflow, ModelView, ModelSQL, fields, Unique, Check
from trytond.wizard import Wizard, StateTransition
from trytond import backend
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id, And, Or
from trytond.transaction import Transaction
from sql.functions import DatePart, CurrentDate
from sql.conditionals import Case
from sql.aggregate import Sum
from sql import Cast
from datetime import date, timedelta, datetime
from decimal import Decimal
from .const import WF_EVALUATION_CREATED, WF_EVALUATION_LOCK, WF_EVALUATION_ACTIVE, VACDAY_FULL, VACDAY_HALF
from .tools import fmttimedelta, round_timedelta


__all__ = ['Evaluation', 'EvaluationItem', 'RecalcEvaluation', 'EvaluationWorktime',\
    'EvaluationBreakTime']
__metaclass__ = PoolMeta


sel_state = [
        (WF_EVALUATION_CREATED, u'Created'),
        (WF_EVALUATION_ACTIVE, u'Active'),
        (WF_EVALUATION_LOCK, u'Locked'),
    ]


class Evaluation(Workflow, ModelSQL, ModelView):
    'Evaluation'
    __name__ = 'employee_timetracking.evaluation'

    employee = fields.Many2One(string=u'Employee', model_name='company.employee',
        states={
            'readonly': 
                ~And(
                    Eval('state', '') == WF_EVALUATION_CREATED,
                    Or(
                        Id('res', 'group_admin').\
                            in_(Eval('context', {}).get('groups', [])),
                        Id('employee_timetracking', 'group_worktime_edit').\
                            in_(Eval('context', {}).get('groups', [])),
                    ),
                ),
            }, 
        required=True, ondelete='CASCADE', depends=['state'], select=True,
        domain=[
                ('tariff', '!=', None),
                ('company', '=', Eval('context', {}).get('company', None)),
            ])
    evaldate = fields.Date(string=u'Date', required=True, select=True,
        help=u'First day of the month for the evaluation.',
        states={
            'readonly':
                ~Or(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    And(
                        Eval('state', '') == WF_EVALUATION_CREATED,
                        Or(
                            Id('employee_timetracking', 'group_worktime_edit').\
                                in_(Eval('context', {}).get('groups', [])),
                            Id('employee_timetracking', 'group_timetracking_employee').\
                                in_(Eval('context', {}).get('groups', [])),
                        ),
                    ),
                ),
        }, depends=['state'])
    state = fields.Selection(selection=sel_state, string=u'State', select=True, readonly=True)
    state_string = state.translated('state')
    worktimerule = fields.One2Many(model_name='employee_timetracking.evaluation_wtrule',
        field='evaluation', string=u'Working time rule 2')
    breaktimerule = fields.One2Many(model_name='employee_timetracking.evaluation_btrule',
        field='evaluation', string=u'Break time rule')
    accountitems = fields.One2Many(string=u'Time Account Items', readonly=True,
        model_name='employee_timetracking.timeaccountitem', field='evaluation')
    vacationdays = fields.One2Many(string=u'Vacation days', field='evaluation',
        model_name='employee_timetracking.evaluation_vacationdays',
        states={
            'readonly':
                ~Or(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    And(
                        Eval('state', '') == WF_EVALUATION_ACTIVE,
                        Id('employee_timetracking', 'group_worktime_edit').\
                            in_(Eval('context', {}).get('groups', [])),
                    ),
                ),
        }, depends=['state'])
    payed_out = fields.TimeDelta(string=u'Paid out', converter='tdconv_hhhmm',
        help=u'paid working time, usually corresponds to the planned working time, may also include overtime',
        states={
            'readonly':
                ~Or(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    And(
                        Eval('state', '') == WF_EVALUATION_ACTIVE,
                        Id('employee_timetracking', 'group_worktime_edit').\
                            in_(Eval('context', {}).get('groups', [])),
                    ),
                ),
        }, depends=['state'])
    bal_current_month = fields.TimeDelta(string=u'Current month',
        readonly=True, converter='tdconv_hhhmm',
        help=u'Balance of the primary working time account of the current month')
    days = fields.One2Many(model_name='employee_timetracking.evaluation-dayofyear',
        field='evaluation', string=u'Daily view', readonly=True)
    evalitem = fields.One2Many(model_name='employee_timetracking.evaluationitem', 
        field='evaluation', string=u'Time accounts', 
        states={
            'readonly':
                ~Or(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    And(
                        Eval('state', '') == WF_EVALUATION_ACTIVE,
                        Or(
                            Id('employee_timetracking', 'group_worktime_edit').\
                                in_(Eval('context', {}).get('groups', [])),
                            Id('employee_timetracking', 'group_timetracking_employee_editeval').\
                                in_(Eval('context', {}).get('groups', [])),
                        ),
                    ),
                ),
        }, depends=['state'])
    needs_recalc = fields.Boolean(string=u'Recalculation', readonly=True,
        help=u'The evaluation is scheduled for recalculation.')
    recalc_at = fields.DateTime(string=u'Recalculated', readonly=True,
        help=u'The evaluation was recalculated at the time shown.')
    sickdays = fields.One2Many(string=u'Sick Days', field='evaluation',
        model_name='employee_timetracking.evaluation_sickdays',
        states={
            'readonly':
                ~Or(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    Eval('state', '') == WF_EVALUATION_ACTIVE,
                ),
        }, depends=['state'])

    # views
    datestart = fields.Function(fields.DateTime(string=u'Begin', readonly=True), 'on_change_with_datestart')
    dateend = fields.Function(fields.DateTime(string=u'End', readonly=True), 'on_change_with_dateend')
    state_year = fields.Function(fields.Integer(string=u'Year', readonly=True), 
            'get_state_year', searcher='search_state_year')
    state_month = fields.Function(fields.Integer(string=u'Month', readonly=True), 
            'get_state_year', searcher='search_state_month')
    worktime_target_str = fields.Function(fields.Char(string=u'Target', 
            help=u'Target working time per month', readonly=True), 'get_worktime_info')
    worktime_wobreaks_str = fields.Function(fields.Char(string=u'Actual', 
            help=u'Actual working time per month without breaks', readonly=True), 'get_worktime_info')
    worktime_diff_str = fields.Function(fields.Char(string=u'Difference', 
            help=u'Difference between actual and target working time per month', 
            readonly=True), 'get_worktime_info')
    worktime_target = fields.Function(fields.TimeDelta(string=u'Target', 
            converter='tdconv_hhhmm',
            help=u'Target working time per month', readonly=True), 'get_worktime_info')
    worktime_actual = fields.Function(fields.TimeDelta(string=u'Actual', 
            converter='tdconv_hhhmm', help=u'Actual working time per month', readonly=True),
            'on_change_with_worktime_actual')
    worktime_actual_str = fields.Function(fields.Char(string=u'Actual', 
            help=u'Actual working time per month', readonly=True), 
            'on_change_with_worktime_actual_str')
    worktime_wobreaks = fields.Function(fields.TimeDelta(string=u'Actual', 
            converter='tdconv_hhhmm',
            help=u'Actual working time per month without breaks', readonly=True), 'get_worktime_info')
    worktime_diff = fields.Function(fields.TimeDelta(string=u'Difference', 
            converter='tdconv_hhhmm',
            help=u'Difference between actual and target working time per month', 
            readonly=True), 'get_worktime_info')
    holidays = fields.Function(fields.Integer(string=u'Holidays', 
            help=u'public holidays', readonly=True), 'get_worktime_info')
    numsickdays = fields.Function(fields.Integer(string=u'Sick Days', 
            help=u'number of sick days', readonly=True), 'on_change_with_numsickdays')
    bal_prev_month = fields.Function(fields.TimeDelta(string=u'Previous month',
            readonly=True, converter='tdconv_hhhmm',
            help=u'Balance of the primary working time account of the previous month'),
            'on_change_with_bal_prev_month')
    bal_prev_month_str = fields.Function(fields.Char(string=u'Previous month',
            readonly=True, help=u'Balance of the primary working time account of the previous month'),
            'on_change_with_bal_prev_month_str')
    vacationdays_taken = fields.Function(fields.Numeric(string=u'Vacation Days', readonly=True,
            digits=(16, 1), help=u'vacantion days taken this month'), 'on_change_with_vacationdays_taken')
    vacationdays_remain = fields.Function(fields.Numeric(string=u'Remain Vacation Days', readonly=True,
            digits=(16, 1), help=u'vacantion days remainig after current month'), 
            'on_change_with_vacationdays_remain')

    @classmethod
    def __setup__(cls):
        super(Evaluation, cls).__setup__()
        tab_eval = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_date', 
            Unique(tab_eval, tab_eval.evaldate, tab_eval.employee), 
            u'This date is already in use.'),
            ])
        cls._order.insert(0, ('evaldate', 'DESC'))
        cls._order.insert(0, ('employee.party.name', 'ASC'))
        cls._transitions |= set((
            (WF_EVALUATION_CREATED, WF_EVALUATION_ACTIVE),
            (WF_EVALUATION_ACTIVE, WF_EVALUATION_LOCK),
            (WF_EVALUATION_LOCK, WF_EVALUATION_CREATED),
            ))
        cls._error_messages.update({
            'delete_evalitem': (u"The evaluation item is in the '%s' state and can not be deleted."),
            'eval_nolock_incurrent_month': (u"The evaluation '%s' is currently in the active month and can not be fixed until next month."),
            'eval_nolock_prev_are_unlocked': (u"The evaluation can not be fixed because the evaluation '%s' is not yet fixed."),
            'evalitm_denyedit': (u"The evaluation '%s' is %s and cannot changed."),
            'croncheck_misscompany': (u"The company '%s' is not in the list of companies of the cron job."),
            })
        cls._buttons.update({
            'wfcreate': {
                'invisible': 
                    ~And(
                        Eval('state', '') == WF_EVALUATION_LOCK,
                        Or(
                            Id('employee_timetracking', 'group_worktime_edit')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                        ),
                    )
                },
            'wfactivate': {
                'invisible': 
                    ~And(
                        Eval('state', '') == WF_EVALUATION_CREATED,
                        Or(
                            Id('employee_timetracking', 'group_worktime_edit')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Id('employee_timetracking', 'group_timetracking_employee').\
                                in_(Eval('context', {}).get('groups', [])),
                            Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                        ),
                    )
                },
            'wflock': {
                'invisible': 
                    ~And(
                        Eval('state') == WF_EVALUATION_ACTIVE,
                        Or(
                            Id('employee_timetracking', 'group_worktime_edit')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                        )
                    )
                },
            })
    
    @classmethod
    def default_employee(cls):
        """ default: current user-employee
        """
        context = Transaction().context
        return context.get('employee')

    @classmethod
    def default_state(cls):
        """ default: created
        """
        return WF_EVALUATION_CREATED

    @classmethod
    def default_needs_recalc(cls):
        """ default: True
        """
        return True

    def get_rec_name(self, name):
        t1 = '%s - %s' % \
            (self.employee.party.rec_name, self.evaldate.strftime('%Y-%m'))
        return t1

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('employee.party.rec_name',) + tuple(clause[1:])]

    @fields.depends('evaldate')
    def on_change_with_datestart(self, name=None):
        """ calculate time + date of begin of evaluation period
        """
        if isinstance(self.evaldate, type(None)):
            return None
        return datetime(self.evaldate.year, self.evaldate.month, 1, 0, 0, 0)

    @fields.depends('evaldate')
    def on_change_with_dateend(self, name=None):
        """ calculate time + date of end of evaluation period
        """
        if isinstance(self.evaldate, type(None)):
            return None
        if self.evaldate.month == 12:
            return datetime(self.evaldate.year, self.evaldate.month, 31, 23, 59, 59)
        else :
            return datetime(self.evaldate.year, self.evaldate.month + 1, 1, 23, 59, 59) - timedelta(days=1)

    @classmethod
    def get_bal_prev_month(cls, evaluation):
        """ get balance of main-time-account of previous month
        """
        EvalItem = Pool().get('employee_timetracking.evaluationitem')
        
        if isinstance(evaluation, type(None)):
            return None

        ev_lst = EvalItem.search([
                ('evaluation', '=', evaluation.id),
                ('account', '=', evaluation.employee.tariff.main_timeaccount)
            ])
        if len(ev_lst) == 0:
            return timedelta(seconds=0)
        elif len(ev_lst) == 1:
            return ev_lst[0].balancestart
        else :
            raise ValueError(u'wrong number of items')
        
    @fields.depends('employee', 'id')
    def on_change_with_bal_prev_month(self, name=None):
        """ get balance of main-time-account of previous month
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
        if isinstance(self.employee, type(None)) or isinstance(self.id, type(None)):
            return None
        return Evaluation.get_bal_prev_month(self)

    @fields.depends('employee', 'id')
    def on_change_with_bal_prev_month_str(self, name=None):
        """ get balance-text of main-time-account of previous month
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
        if isinstance(self.employee, type(None)) or isinstance(self.id, type(None)):
            return None
        return fmttimedelta(Evaluation.get_bal_prev_month(self), noplussign=True)

    @fields.depends('id')
    def on_change_with_numsickdays(self, name=None):
        """ get number of sick days
        """
        DayOfEval = Pool().get('employee_timetracking.evaluation-dayofyear')
        
        num_sday = 0
        
        if isinstance(self.id, type(None)):
            return num_sday

        num_sday = DayOfEval.search_count([
                ('sickday', '=', True),
                ('evaluation', '=', self.id),
            ])
        return num_sday

    @fields.depends('employee', 'evaldate')
    def on_change_with_vacationdays_remain(self, name=None):
        """ get remainig vacation days
        """
        DayOfEval = Pool().get('employee_timetracking.evaluation-dayofyear')

        ret1 = Decimal('0.0')
        if isinstance(self.employee, type(None)):
            return ret1
        if isinstance(self.evaldate, type(None)):
            return ret1

        # get start date
        dt_beg = date(self.evaldate.year, 1, 1)
        if not isinstance(self.employee.start_date, type(None)):
            if dt_beg < self.employee.start_date:
                dt_beg = self.employee.start_date
        
        # end date is last day of current evaluation
        dt_end = self.evaldate + timedelta(days=32)
        dt_end = date(dt_end.year, dt_end.month, 1)
        dt_end -= timedelta(days=1)
        
        # count full vacation days
        vd_cnt = DayOfEval.search_count([
                ('date', '>=', dt_beg),
                ('date', '<=', dt_end),
                ('evaluation.employee.id', '=', self.employee.id),
                ('vacationday', '=', VACDAY_FULL)
            ])
        ret1 += Decimal(vd_cnt)

        # count half vacation days
        vd_cnt = DayOfEval.search_count([
                ('date', '>=', dt_beg),
                ('date', '<=', dt_end),
                ('evaluation.employee.id', '=', self.employee.id),
                ('vacationday', '=', VACDAY_HALF)
            ])
        ret1 += Decimal(vd_cnt) * Decimal('0.5')
        return self.employee.holidays + self.employee.specleave - ret1

    @fields.depends('id')
    def on_change_with_vacationdays_taken(self, name=None):
        """ get taken vacation days in current month
        """
        DayOfEval = Pool().get('employee_timetracking.evaluation-dayofyear')
        
        if isinstance(self.id, type(None)):
            return Decimal('0.0')

        ret1 = Decimal('0.0')
        
        # count full vacation days
        fvd_cnt = DayOfEval.search_count([
                ('evaluation.id', '=', self.id),
                ('vacationday', '=', VACDAY_FULL)
            ])
        ret1 += Decimal(fvd_cnt)

        # count full vacation days
        hvd_cnt = DayOfEval.search_count([
                ('evaluation.id', '=', self.id),
                ('vacationday', '=', VACDAY_HALF)
            ])
        ret1 += Decimal(hvd_cnt) * Decimal('0.5')
        
        return ret1

    @fields.depends('id', 'employee')
    def on_change_with_worktime_actual(self, name=None):
        """ get current worktime of the month in main-time-account
        """
        pool = Pool()
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        if isinstance(self.id, type(None)) or isinstance(self.employee, type(None)):
            return None

        res1 = timedelta(seconds=0)
        
        ta_lst = TimeAccountItem.search([
                    ('evaluation.id', '=', self.id),
                    ('account.id', '=', self.employee.tariff.main_timeaccount.id)
                ])
        for i in ta_lst:
            res1 += i.duration_wfactor

        # add worktime of vacation days
        (wktime, brtime) = Evaluation.get_breaktimes_vacationtimes(self)
        res1 += wktime

        res1 = round_timedelta(res1, rndmode='up')            
        return res1
        
    @fields.depends('worktime_actual')
    def on_change_with_worktime_actual_str(self, name=None):
        """ get formatted text of 'worktime_actual'
        """
        if isinstance(self.worktime_actual, type(None)):
            return None
            
        return fmttimedelta(self.worktime_actual, noplussign=True)
        
    @classmethod
    def get_worktime_info(cls, evaluations, names):
        """ get target/actual/diff working time
        """
        pool = Pool()
        DayOfEval = pool.get('employee_timetracking.evaluation-dayofyear')
        tab_targwt = DayOfEval.get_working_days_sql()
        tab_data = DayOfEval.get_data_sql()
        cursor = Transaction().connection.cursor()

        res = {'worktime_target': {}, 'worktime_target_str': {}, 
                'worktime_diff':{}, 'worktime_diff_str':{}, 
                'worktime_wobreaks': {}, 'worktime_wobreaks_str': {},
                'holidays': {}}
        id_lst = [x.id for x in evaluations]

        # prepare result
        for i in id_lst:
            for k in res.keys():
                res[k][i] = None

        # target working time
        qu1 = tab_targwt.select(tab_targwt.evaluation,
                tab_targwt.targettime,
                Case (
                    (~tab_targwt.weekday.in_(['0', '6']) & 
                     (tab_targwt.holiday_ena == True), 1),
                    else_ = 0
                ).as_('holiday'),
                distinct_on=[tab_targwt.date, tab_targwt.evaluation]
            )
        qu2 = qu1.select(qu1.evaluation,
                Sum(qu1.targettime).as_('targwt'),      # sum of target work times
                Sum(qu1.holiday).as_('holidays'),       # count holidays per month
                where=qu1.evaluation.in_(id_lst),
                group_by=[qu1.evaluation],
            )
        cursor.execute(*qu2)
        l1 = cursor.fetchall()

        for i in l1:
            (id1, targ, holidays) = i
            res['worktime_target'][id1] = targ  # field 'Target' in evaluation (depends on 
                                                # number of days in month and nat./church. holidays)
            res['holidays'][id1] = holidays     # field 'Holidays' in evaluation (number of holidays which are not at weekend)

        # actual working time without breaks
        if ('worktime_wobreaks' in names) or ('worktime_wobreaks_str' in names) or \
            ('worktime_diff' in names) or ('worktime_diff_str' in names):
            for i in evaluations:
                date_cache = []
                work_time = timedelta(seconds=0)
                for k in i.days:
                    # days with more than one working time appear more than one time
                    # in 'days' - count the first
                    if k.date in date_cache:
                        continue
                    date_cache.append(k.date)

                    if not isinstance(k.wobreaks, type(None)):
                        work_time += k.wobreaks
                res['worktime_wobreaks'][i.id] = work_time

        for i in id_lst:
            targ1 = res['worktime_target'].get(i, timedelta(seconds=0))
            wobreak1 = res['worktime_wobreaks'].get(i, timedelta(seconds=0))
            if isinstance(targ1, type(None)):
                targ1 = timedelta(seconds=0)
            if isinstance(wobreak1, type(None)):
                wobreak1 = timedelta(seconds=0)
            targ1 = round_timedelta(targ1, rndmode='up')
            wobreak1 = round_timedelta(wobreak1, rndmode='up')
            diff1 = wobreak1 - targ1

            res['worktime_wobreaks'][i] = wobreak1
            res['worktime_target'][i] = targ1
            res['worktime_diff'][i] = diff1
            res['worktime_wobreaks_str'][i] = fmttimedelta(wobreak1, noplussign=True)
            res['worktime_target_str'][i] = fmttimedelta(targ1, noplussign=True)
            res['worktime_diff_str'][i] = fmttimedelta(diff1, noplussign=True)

        res2 = {}
        for i in res.keys():
            res2[i] = res[i]
        return res2

    @classmethod
    def get_state_year_sql(cls):
        """ sql-code
        """
        tab_eval = cls.__table__()
        q1 = tab_eval.select(tab_eval.id,
                    Cast(DatePart('year',  CurrentDate()) - 
                         DatePart('year',  tab_eval.evaldate), 
                        'integer').as_('year'),
                    Cast((DatePart('year', CurrentDate()) - 
                          DatePart('year', tab_eval.evaldate)) * 12 + 
                         (DatePart('month', CurrentDate()) - 
                          DatePart('month', tab_eval.evaldate)),
                        'integer').as_('month')
                )
        return q1

    @classmethod
    def get_state_year(cls, evalitem, names):
        """ get year of evaluation-item: 0 = current, 1 = last, 2,... = older
        """
        r1 = {'state_year': {}, 'state_month':{}}
        cursor = Transaction().connection.cursor()
        
        sql1 = cls.get_state_year_sql()
        qu2 = sql1.select(sql1.id, 
                    sql1.year,
                    sql1.month,
                    where=sql1.id.in_([x.id for x in evalitem])
                )
        cursor.execute(*qu2)
        l2 = cursor.fetchall()
        
        for i in l2:
            (id1, y1, m1) = i
            r1['state_year'][id1] = y1
            r1['state_month'][id1] = m1
        
        r2 = {}
        for i in names:
            r2[i] = r1[i]
        return r2

    @classmethod
    def search_state_year(cls, name, clause):
        """ search in state_year
        """
        sql1 = cls.get_state_year_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = sql1.select(sql1.id,
                where=Operator(sql1.year, clause[2])
            )
        return [('id', 'in', qu1)]

    @classmethod
    def search_state_month(cls, name, clause):
        """ search in state_month
        """
        sql1 = cls.get_state_year_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = sql1.select(sql1.id,
                where=Operator(sql1.month, clause[2])
            )
        return [('id', 'in', qu1)]

    @classmethod
    def add_evaluations_by_date(cls, company, evaldate=None):
        """ automatic add of evaluation by current-month/employee
            'evaldate' = set 'current-date'
        """
        pool = Pool()
        Employee = pool.get('company.employee')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        use_date = date.today()
        if not isinstance(evaldate, type(None)):
            use_date = evaldate
        use_date = date(use_date.year, use_date.month, 1)

        # employees with tariff,  without current evaluation
        empl_lst = Employee.search([
                ('company', '=', company),
                ('tariff', '!=', None),
                ('id', 'not in', 
                    # evaluations of current company/month
                    [y.employee.id for y in cls.search([
                        ('evaldate', '=', use_date),
                        ('employee.company', '=', company)
                        ])
                    ]),
            ])

        # create missing evaluations
        tr1 = Transaction()
        ev_lst = []
        for i in empl_lst:
            evobj = Evaluation()
            evobj.employee = i
            evobj.evaldate = use_date
            evobj.save()
            ev_lst.append(evobj)
        Evaluation.wfactivate(ev_lst)
        return ev_lst

    @classmethod
    def add_breaktime_rules(cls, evaluations):
        """ adds break time rules to evaluation
        """
        EvalBreakTime = Pool().get('employee_timetracking.evaluation_btrule')
        
        for i in evaluations:
            if i.state == WF_EVALUATION_LOCK:
                cls.raise_user_error('evalitm_denyedit', i.rec_name)

            if isinstance(i.employee.tariff, type(None)):
                continue
            if len(i.employee.tariff.breaktime) == 0:
                continue
                
            l1 = []
            for k in list(i.employee.tariff.breaktime):
                bt1 = EvalBreakTime(mintime = k.mintime, maxtime = k.maxtime, deduction=k.deduction)
                l1.append(bt1)
            i.breaktimerule = l1
            i.save()

    @classmethod
    def updt_tariff_model(cls, tariff_list):
        """ update tariff model in all evaluations which use it and are not locked
        """
        EvalBreakTime = Pool().get('employee_timetracking.evaluation_btrule')
        
        ev_lst = cls.search([
                    ('employee.tariff', 'in', tariff_list), 
                    ('state', '!=', WF_EVALUATION_LOCK)
                ])
        for i in ev_lst:
            EvalBreakTime.delete(i.breaktimerule)
        cls.add_breaktime_rules(ev_lst)

    @classmethod
    def add_worktime_rules(cls, evaluations):
        """ adds work time rules to evaluation
        """
        EvalWorkTime = Pool().get('employee_timetracking.evaluation_wtrule')
        
        for i in evaluations:
            if i.state == WF_EVALUATION_LOCK:
                cls.raise_user_error('evalitm_denyedit', i.rec_name)

            if isinstance(i.employee.worktime, type(None)):
                continue
                
            l1 = []
            for k in list(i.employee.worktime.worktimerule):
                wt1 = EvalWorkTime(mon = k.mon, tue = k.tue, wed = k.wed, thu = k.thu, fri = k.fri,
                        sat = k.sat, sun = k.sun, mintime = k.mintime, maxtime = k.maxtime)
                l1.append(wt1)
            i.worktimerule = l1
            i.save()

    @classmethod
    def updt_worktime_model(cls, wtmodel_list):
        """ update worktime model in all evaluations which use it and are not locked
        """
        EvalWorkTime = Pool().get('employee_timetracking.evaluation_wtrule')
        
        ev_lst = cls.search([
                    ('employee.worktime', 'in', wtmodel_list), 
                    ('state', '!=', WF_EVALUATION_LOCK)
                ])
        for i in ev_lst:
            EvalWorkTime.delete(i.worktimerule)
        cls.add_worktime_rules(ev_lst)

    @classmethod
    def updt_eval_items(cls, evaluation_list):
        """ add/delete evaluation-item to match with tariff model of employee
        """
        EvalItem = Pool().get('employee_timetracking.evaluationitem')

        for i in evaluation_list:
            if i.state == WF_EVALUATION_LOCK:
                cls.raise_user_error('evalitm_denyedit', i.rec_name)

            acc_id = []
            edit1 = False
            # add eval items
            for k in i.employee.tariff.accountrule:
                acc_id.append(k.account.id)
                
                evitm = EvalItem.search([
                        ('evaluation', '=', i.id),
                        ('account', '=', k.account.id)
                    ])
                if len(evitm) == 0:
                    ob1 = EvalItem()
                    ob1.evaluation = i
                    ob1.account = k.account
                    ob1.balancestart = timedelta(seconds=0)
                    ob1.balancediff = timedelta(seconds=0)
                    ob1.payed_out = timedelta(seconds=0)
                    ob1.save()
                    edit1 = True

            # delete eval item for missing time accounts
            dellst = EvalItem.search([
                    ('evaluation', '=', i.id),
                    ('account', 'not in', acc_id)
                ])
            if len(dellst) > 0:
                EvalItem.delete(dellst)
                edit1 = True
            
            if edit1 == True:
                i.needs_recalc = True
                i.save()

    @classmethod
    def updt_calc_evaluation(cls, evaluation):
        """ recalc evaluation and its items
        """
        pool = Pool()
        EvalItem = pool.get('employee_timetracking.evaluationitem')
        EvalObj = pool.get('employee_timetracking.evaluation')
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')
        DaysOfEvaluation = pool.get('employee_timetracking.evaluation-dayofyear')
        VacationDays = pool.get('employee_timetracking.evaluation_vacationdays')

        if evaluation.state == WF_EVALUATION_LOCK:
            cls.raise_user_error('evalitm_denyedit', evaluation.rec_name)

        # update vacations days
        VacationDays.updt_days_from_calendar(evaluation)
        
        edit1 = False
        bal_prev_month = timedelta(seconds=0)

        # date of evaluation of the month before current evaluation
        if evaluation.evaldate.month == 1:
            prev_eval = date(evaluation.evaldate.year - 1, 12, 1)
        else :
            prev_eval = date(evaluation.evaldate.year, evaluation.evaldate.month - 1, 1)

         # update time-accounts
        for i in evaluation.evalitem:
            evitems = EvalItem.search([
                        ('evaluation.employee', '=', evaluation.employee),
                        ('evaluation.evaldate', '=', prev_eval),
                        ('account', '=', i.account)
                    ], limit=1, order=[('evaluation.evaldate', 'DESC')])
            
            # start balance
            if i.balstartmanu == True:
                # manually entered value, ignore previous month
                balstart = i.balancestart
            else :
                # startbalance at zero or take value from previous month
                balstart = timedelta(seconds=0)
                if len(evitems) > 0:
                    balstart = evitems[0].balancestart + evitems[0].balancediff - evitems[0].payed_out

            if i.account == evaluation.employee.tariff.main_timeaccount:
                bal_prev_month = balstart

                # 'payed_out' of eval-item for main-time-account is taken
                # from evaluation.payed_out
                if (i.payed_out != evaluation.payed_out):
                    i.payed_out = evaluation.payed_out
                    i.save()
                    edit1 = True

            # difference
            baldiff = timedelta(seconds=0)
            ta_lst = TimeAccountItem.search([
                    ('id', 'in', [x.id for x in evaluation.accountitems]),
                    ('account', '=', i.account),
                ])
            for k in ta_lst:
                baldiff += k.duration_wfactor

            # main-time-account: reduce by breaktime, add vacation days
            if i.account == evaluation.employee.tariff.main_timeaccount:
                (wktime, brtime) = cls.get_breaktimes_vacationtimes(evaluation)
                baldiff += wktime
                baldiff -= brtime

            if (baldiff != i.balancediff) or (balstart != i.balancestart):
                i.balancestart = balstart
                i.balancediff = baldiff
                i.save()
                edit1 = True

        # calculated field 'worktime_wobreaks' in evaluation
        # sum of durations in main-time-account
        worktime_actual = evaluation.worktime_wobreaks
        if isinstance(worktime_actual, type(None)):
            worktime_actual = timedelta(seconds=0)

        # stored field 'payed_out' in evaluation
        payed_out = evaluation.payed_out
        if isinstance(payed_out, type(None)):
            payed_out = timedelta(seconds=0)

        # balance of previous month
        if isinstance(bal_prev_month, type(None)):
            bal_prev_month = timedelta(seconds=0)
        bal_current_month = bal_prev_month + worktime_actual - payed_out
        
        if bal_current_month != evaluation.bal_current_month:
            evaluation.bal_current_month = bal_current_month
            edit1 = True

        if edit1 == True:
            evaluation.recalc_at = datetime.now()
            
            # mark following evaluations for recalc
            ftr_eval = EvalObj.search([
                    ('employee', '=', evaluation.employee),
                    ('evaldate', '>', evaluation.evaldate),
                    ('needs_recalc', '=', False)
                ])
            for i in ftr_eval:
                i.needs_recalc = True
                i.save()

        evaluation.needs_recalc = False
        evaluation.save()

    @classmethod
    def get_breaktimes_vacationtimes(cls, evaluation):
        """ get sum of breaktimes and 
            working time of vacation days
        """
        if isinstance(evaluation, type(None)):
            return (None, None)
            
        date_cache = []
        worktime = timedelta(seconds=0)
        breaktime = timedelta(seconds=0)
        
        for k in evaluation.days:
            if k.date in date_cache:
                continue
            date_cache.append(k.date)

            # add working time, if its a vacation day
            if k.vacationday == VACDAY_FULL:
                worktime += k.targettime
            elif k.vacationday == VACDAY_HALF:
                worktime += k.targettime / 2
            
            # reduce by break time
            if not isinstance(k.breaktime, type(None)):
                breaktime += k.breaktime
        
        return (worktime, breaktime)

    @classmethod
    def edit_cronjob(cls):
        """ update companies at cronjob
        """
        # edit cron-job
        pool = Pool()
        Cron = pool.get('ir.cron')
        ModelData = pool.get('ir.model.data')
        Employee = pool.get('company.employee')

        cr1 = Cron(ModelData.get_id('employee_timetracking', 'cron_recalc_timeaccounts'))
        cl1 = list(cr1.companies)

        # find employees having tariff, create list of companies
        el1 = Employee.search([('tariff', '!=', None)])
        for i in el1:
            if not i.company in cl1:
                cl1.append(i.company)
        
        cr1.companies = cl1
        cr1.save()

    @classmethod
    def get_companies_to_run(cls):
        """ get list of companies with employees activated for timetracking
        """
        Employee = Pool().get('company.employee')
        c1 = Employee.search([
                ('tariff', '!=', None)
            ])
        return [x.company for x in c1]
        
    @classmethod
    def check_cronsetup(cls):
        """ check if cronjob has valid company settings
        """
        pool = Pool()
        Cron = pool.get('ir.cron')
        ModelData = pool.get('ir.model.data')
        
        cr1 = Cron(ModelData.get_id('employee_timetracking', 'cron_recalc_timeaccounts'))
        comp1 = cls.get_companies_to_run()
        for i in comp1:
            if not i in cr1.companies:
                cls.raise_user_error('croncheck_misscompany', (i.party.rec_name))

    @classmethod
    def cron_recalc_evaluation(cls):
        """ recalc evaluations for all employees which have new items
        """
        pool = Pool()
        EvalItem = pool.get('employee_timetracking.evaluationitem')
        Company = pool.get('company.company')
        
        cls.check_cronsetup()

        # add evaluations
        c_lst = Company.search([])
        for i in c_lst:
            # for current month
            cls.add_evaluations_by_date(i)

        # evaluations
        todo_lst = cls.search([
                ('needs_recalc', '=', True),
                ('state', '!=', WF_EVALUATION_LOCK)
            ], order=[('evaldate', 'ASC')])
        if len(todo_lst) > 0:
            for i in todo_lst:
                cls.updt_calc_evaluation(i)

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_EVALUATION_CREATED)
    def wfcreate(cls, evalitem):
        """ create evaluation item
        """
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_EVALUATION_ACTIVE)
    def wfactivate(cls, evalitem):
        """ activate evaluation item
        """
        cls.updt_eval_items(evalitem)
        for i in evalitem:
            i.payed_out = i.worktime_target
            i.save()
            cls.updt_calc_evaluation(i)

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_EVALUATION_LOCK)
    def wflock(cls, evalitem):
        """ lock evaluation item
        """
        # first and last day of current month
        dt1 = date.today()
        mon_1st = date(dt1.year, dt1.month, 1)
        if dt1.month == 12:
            mon_last = date(dt1.year, dt1.month, 31)
        else :
            mon_last = date(dt1.year, dt1.month + 1, 1) - timedelta(days=1)
        
        for i in evalitem:
            # deny locking in current month
            if mon_1st <= i.evaldate <= mon_last:
                cls.raise_user_error('eval_nolock_incurrent_month', i.rec_name)

            # deny locking if there are still not locked previous evaluations
            l1 = cls.search([
                    ('employee', '=', i.employee), 
                    ('state', '!=', WF_EVALUATION_LOCK),
                    ('evaldate', '<', i.evaldate)
                    ])
            if len(l1) > 0:
                cls.raise_user_error('eval_nolock_prev_are_unlocked', l1[0].rec_name)
            cls.updt_eval_items([i])
            cls.updt_calc_evaluation(i)

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('employee'):
                values['employee'] = cls.default_employee()

            # move date to 1. of month
            if 'evaldate' in values.keys():
                values['evaldate'] = date(values['evaldate'].year, values['evaldate'].month, 1)
        l1 = super(Evaluation, cls).create(vlist)
        
        Evaluation.add_worktime_rules(l1)
        Evaluation.add_breaktime_rules(l1)
        
        DaysOfEvaluation = Pool().get('employee_timetracking.evaluation-dayofyear')
        DaysOfEvaluation.add_days_of_month(l1)
        
        return l1

    @classmethod
    def write(cls, *args):
        """ write item, fix evaldate to 1. of month
        """
        updt_evals = []
        actions = iter(args)
        for items, values in zip(actions, actions):
            for i in items:
                # move date to 1. of month
                if 'evaldate' in values.keys():
                    values['evaldate'] = date(values['evaldate'].year, values['evaldate'].month, 1)
                    
                if 'payed_out' in values.keys():
                    values['needs_recalc'] = True
        super(Evaluation, cls).write(*args)

    @classmethod
    def delete(cls, evalitem):
        """ deny delete if locked
        """
        for i in evalitem:
            if i.state in [WF_EVALUATION_LOCK, WF_EVALUATION_ACTIVE]:
                cls.raise_user_error('delete_evalitem', i.state_string)
        return super(Evaluation, cls).delete(evalitem)

# end Evaluation


# item for timeaccount in evaluation per employee
# contains: which time-account, start-balance
class EvaluationItem(ModelSQL, ModelView):
    'Evaluation Item'
    __name__ = 'employee_timetracking.evaluationitem'

    evaluation = fields.Many2One(string=u'Evaluation', required=True, select=True,
        ondelete='CASCADE', readonly=True, model_name='employee_timetracking.evaluation')
    account = fields.Many2One(string=u'Time Account', model_name='employee_timetracking.timeaccount', 
        ondelete='RESTRICT', readonly=True, required=True)
    balancestart = fields.TimeDelta(string=u'Initial balance', required=True,
        states={
            'readonly': Eval('balstartmanu', False) == False,
            'invisible': Eval('balstartmanu', False) == False,
        }, depends=['balstartmanu'])
    balstartmanu = fields.Boolean(string=u'Initial balance manually', 
        help=u'Enter a defined initial balance for this month')
    balancediff = fields.TimeDelta(string=u'Balance', required=True)
    payed_out = fields.TimeDelta(string=u'Paid out', converter='tdconv_hhhmm',
        help=u'paid working time, ',
        states={
            'readonly':
                ~Or(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    And(
                        Eval('evalstate', '') == WF_EVALUATION_ACTIVE,
                        Id('employee_timetracking', 'group_worktime_edit').\
                            in_(Eval('context', {}).get('groups', [])),
                    ),
                ),
        }, depends=['evalstate'], required=True)

    # views
    evalstate = fields.Function(fields.Selection(string=u'State', readonly=True, 
        selection=sel_state), 'on_change_with_evalstate')
    start_minute = fields.Function(fields.Char(string=u'Initial Balance', readonly=True,
        help=u'Initial balance, taken from the previous month, in hh:mm'), 
        'on_change_with_start_minute')
    diff_minute = fields.Function(fields.Char(string=u'Balance', readonly=True,
        help=u'calculated balance from time account items in hh:mm'), 
        'on_change_with_diff_minute')

    @classmethod
    def __setup__(cls):
        super(EvaluationItem, cls).__setup__()
        tab_evalitm = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_account', 
            Unique(tab_evalitm, tab_evalitm.evaluation, tab_evalitm.account), 
            u'This time account is already in use.'),
            ])
        cls._error_messages.update({
            'evalitm_denyedit': (u"The evaluation '%s' is locked and cannot changed."),
            })

    def get_rec_name(self, name):
        t1 = '%s - %s' % \
            (self.evaluation.rec_name, self.account.rec_name)
        return t1

    @classmethod
    def default_balstartmanu(cls):
        """ default: False
        """
        return False

    @classmethod
    def default_payed_out(cls):
        """ default: 0
        """
        return timedelta(seconds=0)
        
    @fields.depends('evaluation')
    def on_change_with_evalstate(self, name=None):
        """ get state from evaluation
        """
        if isinstance(self.evaluation, type(None)):
            return None
        else :
            return self.evaluation.state
        
    @fields.depends('balancestart')
    def on_change_with_start_minute(self, name=None):
        """ convert balancestart (in seconds) to human readable [hh:mm]
        """
        return fmttimedelta(self.balancestart, noplussign=True)

    @fields.depends('balancediff')
    def on_change_with_diff_minute(self, name=None):
        """ convert balancestart (in seconds) to human readable [hh:mm]
        """
        return fmttimedelta(self.balancediff, noplussign=True)

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('evaluation.rec_name',) + tuple(clause[1:])]

    @classmethod
    def write(cls, *args):
        """ write item, fix evaldate to 1. of month
        """
        EvalObj = Pool().get('employee_timetracking.evaluation')
        
        updt_evals = []
        actions = iter(args)
        for items, values in zip(actions, actions):
            for i in items:
                recalc = False
                
                if 'balstartmanu' in values.keys():
                    recalc = True
                if 'payed_out' in values.keys():
                    recalc = True
                if ('balancestart' in values.keys()) and \
                    ((i.balstartmanu == True) or ('balstartmanu' in values.keys())):
                    recalc = True
                    
                if recalc == True:
                    i.evaluation.needs_recalc = True
                    i.evaluation.save()
                    
                    # mark next evaluations for recalc
                    ftr_eval = EvalObj.search([
                            ('employee', '=', i.evaluation.employee),
                            ('evaldate', '>', i.evaluation.evaldate),
                            ('needs_recalc', '=', False)
                        ])
                    for k in ftr_eval:
                        k.needs_recalc = True
                        k.save()

        super(EvaluationItem, cls).write(*args)

    @classmethod
    def delete(cls, evalitem):
        """ deny delete if locked
        """
        for i in evalitem:
            if i.evaluation.state in [WF_EVALUATION_LOCK]:
                cls.raise_user_error('delete_evalitem', i.evaluation.state_string)
        return super(EvaluationItem, cls).delete(evalitem)

# EvaluationItem


class RecalcEvaluation(Wizard):
    'recalc evalution'
    __name__ = 'employee_timetracking.recalc_evaluation'
    start_state = 'recalc'
    recalc = StateTransition()

    def transition_recalc(self):
        Evaluation = Pool().get('employee_timetracking.evaluation')

        context = Transaction().context

        if context['active_model'] == 'employee_timetracking.evaluation':
            evallst = Evaluation.browse(context['active_ids'])
            Evaluation.updt_eval_items(evallst)
            for i in evallst:
                Evaluation.updt_calc_evaluation(i)
        return 'end'

# RecalcEvaluation


class EvaluationBreakTime(ModelSQL):
    'Rule of break time for evaluation'
    __name__ = 'employee_timetracking.evaluation_btrule'
    
    evaluation = fields.Many2One(string=u'Evaluation', required=True, select=True,
        ondelete='CASCADE', readonly=True, model_name='employee_timetracking.evaluation')
    mintime = fields.TimeDelta(string=u'from', required=True)
    maxtime = fields.TimeDelta(string=u'to', required=True)
    deduction = fields.TimeDelta(string=u'Deduction time', required=True)

    @classmethod
    def __register__(cls, module_name):
        super(EvaluationBreakTime, cls).__register__(module_name)
        cls.migrate_contraints(module_name)

    @classmethod
    def migrate_contraints(cls, module_name):
        """ delete some checks
        """
        TableHandler = backend.get('TableHandler')
        table = TableHandler(cls, module_name)
        table.drop_constraint('no_zerodeduction')
        table.drop_constraint('no_negdeduction')
        table.drop_constraint('no_negtime')

    @classmethod
    def __setup__(cls):
        super(EvaluationBreakTime, cls).__setup__()
        tab_btitem = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_mintime', 
            Unique(tab_btitem, tab_btitem.mintime, tab_btitem.evaluation), 
            u"This 'from' time is already in use."),
            ('uniq_maxtime', 
            Unique(tab_btitem, tab_btitem.maxtime, tab_btitem.evaluation), 
            u"This 'to' time is already in use."),
            ('no_negtime2', 
            Check(tab_btitem, (tab_btitem.mintime >= '00:00:00') & (tab_btitem.maxtime > '00:00:00')), 
            u'Time must be positive.'),
            ('order', 
            Check(tab_btitem, tab_btitem.mintime < tab_btitem.maxtime), 
            u"'to' must be creater than 'from'"),
            ('no_negdeduction2', 
            Check(tab_btitem, tab_btitem.deduction > '00:00:00'), 
            u'Deduction values must be positive.'),
            ])

    def get_rec_name(self, name):
        t1 = '%s: %s-%s -> %s' % \
            (self.evaluation.rec_name, 
            fmttimedelta(self.mintime, noplussign=True),
            fmttimedelta(self.maxtime, noplussign=True),
            fmttimedelta(self.deduction, noplussign=True, sepbyh=True))
        return t1

    @classmethod
    def get_reduced_worktime(cls, evaluation, sumworktime, sumbreaktime):
        """ calculates the reduced working hours based on the rules
            evaluation: employee_timetracking.evaluation,
            worktime: timedelta
        """
        pool = Pool()
        BreakTime = pool.get('employee_timetracking.breaktime')
        EvaluationBreakTime = pool.get('employee_timetracking.evaluation_btrule')
        
        if isinstance(evaluation, type(None)) or isinstance(sumworktime, type(None)):
            return (None, None)

        (wtime, btime) = BreakTime.get_reduced_worktime2(
                EvaluationBreakTime, 
                [('evaluation', '=', evaluation)], 
                sumworktime, 
                sumbreaktime
            )
        # (<reduced working time>, <used break time>)
        return (wtime, btime)

# end EvaluationBreakTime


class EvaluationWorktime(ModelSQL):
    'Evaluation worktime item'
    __name__ = 'employee_timetracking.evaluation_wtrule'
    
    # work time model ist stored in each evaluation for each employee, 
    # because the work time model cannot changed if evaluation is locked

    evaluation = fields.Many2One(string=u'Evaluation', required=True, select=True,
        ondelete='CASCADE', readonly=True, model_name='employee_timetracking.evaluation')
    mon = fields.Boolean(string=u'Mon')
    tue = fields.Boolean(string=u'Tue')
    wed = fields.Boolean(string=u'Wed')
    thu = fields.Boolean(string=u'Thu')
    fri = fields.Boolean(string=u'Fri')
    sat = fields.Boolean(string=u'Sat')
    sun = fields.Boolean(string=u'Sun')
    mintime = fields.Time(string=u'from', required=True)
    maxtime = fields.Time(string=u'to', required=True)

    @classmethod
    def __setup__(cls):
        super(EvaluationWorktime, cls).__setup__()
        tab_wtitem = cls.__table__()
        cls._sql_constraints.extend([
            ('order', 
            Check(tab_wtitem, 
                ((tab_wtitem.mintime < tab_wtitem.maxtime) & (tab_wtitem.maxtime != '00:00')) | \
                (tab_wtitem.maxtime == '00:00')), 
            u"'to' must be creater than 'from'"),
            ('weekday',
            Check(tab_wtitem, (tab_wtitem.mon == True) | (tab_wtitem.tue == True) | \
                              (tab_wtitem.wed == True) | (tab_wtitem.thu == True) | \
                              (tab_wtitem.fri == True) | (tab_wtitem.sat == True) | \
                              (tab_wtitem.sun == True)),
            u'at least one weekday must be activated'),
            ])

    def get_rec_name(self, name):
        l1 = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        t2 = ''
        for k in l1:
            if getattr(self, k) == True:
                t2 += 'x'
            else :
                t2 += '_'
        t1 = '%s-%s [%s]' % \
            (self.mintime.strftime('%H:%M'), self.maxtime.strftime('%H:%M'), t2)
        return t1

# end EvaluationWorktime

