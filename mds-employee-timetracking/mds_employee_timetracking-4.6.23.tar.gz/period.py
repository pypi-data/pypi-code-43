# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


from trytond.model import Workflow, ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id, And, Or, If
from trytond.transaction import Transaction
from datetime import datetime, timedelta, date
from sql.functions import DatePart, CurrentDate, ToChar, AtTimeZone, Extract
from sql.conditionals import Case, Coalesce
from sql import Cast
from sqlextension import Concat2
from trytond.modules.employee_timetracking.const import WF_ACCOUNT_LOCK, WF_ACCOUNT_EVALUATED,\
    WF_ACCOUNT_CREATED, WF_ACCOUNT_EXAMINE, WF_PERIOD_CREATED, WF_PERIOD_EXAMINE, WF_PERIOD_LOCK,\
    sel_weekday
from trytond.modules.employee_timetracking.evaluation import WF_EVALUATION_LOCK


# Period: employee can enter a period of working time by Wizard or directly into the table,
# if a period has start and end time, it can be 'examine' by workflow - this fires the AccountRules


__all__ = ['Period']
__metaclass__ = PoolMeta


sel_state = [
        (WF_PERIOD_CREATED, u'Editable'),
        (WF_PERIOD_EXAMINE, u'Examine'),
        (WF_PERIOD_LOCK, u'Locked')
    ]


class Period(Workflow, ModelSQL, ModelView):
    'presence times'
    __name__ = 'employee_timetracking.period'
    
    name = fields.Function(fields.Char(string=u'Name', readonly=True), 
        'get_name1', searcher='search_name1')
    employee = fields.Many2One(string=u'Employee', model_name='company.employee',
        states={
            'readonly': 
                ~And(
                    Eval('state', '') == WF_PERIOD_CREATED,
                    Or(
                        Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                        Id('employee_timetracking', 'group_worktime_edit').in_(Eval('context', {}).get('groups', [])),
                    ),
                ),
            }, 
        required=True, ondelete='CASCADE', select=True,
        domain=[
                ('tariff', '!=', None),
                ('company', '=', Eval('context', {}).get('company', None)),
            ], depends=['state'])
    presences = fields.Function(fields.One2Many(model_name='employee_timetracking.presence', 
            field=None, string=u'Allowed Presences', readonly=True, depends=['employee']),
            'on_change_with_presences')
    
    state_datefield = {
            'readonly':
                Or(
                    Eval('state', '') != WF_PERIOD_CREATED,
                    Eval('is_eval_locked', False) == True,
                )
            }
    presence = fields.Many2One(string=u'Type of Presence', model_name='employee_timetracking.presence',
        domain=[('id', 'in', Eval('presences', []))], 
        depends=['presences', 'employee', 'is_eval_locked', 'state'],
        states = state_datefield, required=True, ondelete='RESTRICT', select=True)
    startpos = fields.DateTime(string=u'Start', help=u'Beginning of the presence',
        states = state_datefield, depends=['state', 'is_eval_locked'])
    endpos = fields.DateTime(string=u'End', help=u'End of the presence',
        states = state_datefield, depends=['state', 'is_eval_locked'])
    state = fields.Selection(selection=sel_state, string=u'State', select=True, readonly=True)

    # views
    state_month = fields.Function(fields.Integer(string=u'Month', readonly=True), 
            'get_state_month', searcher='search_state_month')
    duration = fields.Function(fields.TimeDelta(string=u'Duration', readonly=True),
            'on_change_with_duration', searcher='search_duration')
    weekday = fields.Function(fields.Selection(string=u'Weekday', readonly=True, 
            selection=sel_weekday), 'on_change_with_weekday')
    week = fields.Function(fields.Integer(string=u'Week', readonly=True, 
            help=u'Calendar week'), 'get_week', searcher='search_week')
    accountitem = fields.One2Many(model_name='employee_timetracking.timeaccountitem', 
            field='period', string=u'Time Account Item', readonly=True,
            help=u'Entries in the time accounts created by the current presence item.')
    is_eval_locked = fields.Function(fields.Boolean(string=u'Evaluation locked', readonly=True,
            states={'invisible': True}), 'get_is_eval_locked', searcher='search_is_eval_locked')
    textcolor = fields.Function(fields.Char(string=u'Text color', readonly=True), 
            'on_change_with_textcolor')
    bgcolor = fields.Function(fields.Char(string=u'Background color', readonly=True), 
            'on_change_with_bgcolor')

    @classmethod
    def __setup__(cls):
        super(Period, cls).__setup__()
        tab_period = cls.__table__()
        cls._order.insert(0, ('name', 'DESC'))
        cls._transitions |= set((
            (WF_PERIOD_CREATED, WF_PERIOD_EXAMINE),
            (WF_PERIOD_EXAMINE, WF_PERIOD_LOCK),
            (WF_PERIOD_EXAMINE, WF_PERIOD_CREATED),
            (WF_PERIOD_LOCK, WF_PERIOD_CREATED),
            ))
        cls._buttons.update({
            'wfcreate': {
                'invisible': 
                    ~Or(
                        And(
                            Eval('state', '') == WF_PERIOD_LOCK,
                            Or(
                                Id('employee_timetracking', 'group_worktime_edit')\
                                        .in_(Eval('context', {}).get('groups', [])),
                                Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                            ),
                        ),
                        And(
                            Eval('state', '') == WF_PERIOD_EXAMINE,
                            Or(
                                Id('employee_timetracking', 'group_timetracking_employee')\
                                        .in_(Eval('context', {}).get('groups', [])),
                                Id('employee_timetracking', 'group_worktime_edit')\
                                        .in_(Eval('context', {}).get('groups', [])),
                                Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                            ),
                        ),
                    )
                },
            'wfexamine': {
                'invisible': 
                    ~And(
                        Eval('state', '') == WF_PERIOD_CREATED,
                        Or(
                            Id('employee_timetracking', 'group_timetracking_employee')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Id('employee_timetracking', 'group_worktime_edit')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                        ),
                    )
                },
            'wflock': {
                'invisible': 
                    ~And(
                        Eval('state') == WF_PERIOD_EXAMINE,
                        Or(
                            Id('employee_timetracking', 'group_timetracking_employee')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Id('employee_timetracking', 'group_worktime_edit')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                        )
                    )
                },
            })
        cls._error_messages.update({
            'delete_period': (u"The working time entry is in the 'locked' state and can not be deleted."),
            'overlap_period': (u"The working time item overlaps with this item: '%s'"),
            'wfexamine_misstimes': (u"Enter start and end time before moving on."),
            'eval_locked': (u"Edit denied, the evaluation period of the working time item '%s' is locked."),
            'period_locked': (u"Edit denied, the working time item '%s' is locked."),
            })
        cls._sql_constraints.extend([
            ('uniq_startpos', 
            Unique(tab_period, tab_period.employee, tab_period.startpos), 
            u'This start time is already in use.'),
            ('uniq_endpos', 
            Unique(tab_period, tab_period.employee, tab_period.endpos), 
            u'This end time is already in use.'),
            ('order_times', 
            Check(tab_period, tab_period.startpos < tab_period.endpos), 
            u'End time must be after start time.'),
            ('not_empty', 
            Check(tab_period, (tab_period.startpos != None) | (tab_period.endpos != None)), 
            u'Please enter a time.'),
            ('valid_lock', 
            Check(tab_period, (tab_period.startpos != None) & (tab_period.endpos != None) & \
                              (tab_period.state.in_([WF_PERIOD_LOCK, WF_PERIOD_EXAMINE])) | \
                              (tab_period.state == WF_PERIOD_CREATED)), 
            u'Enter start and end time before moving on.'),
            ])

    @classmethod
    def default_employee(cls):
        """ default: current user-employee
        """
        context = Transaction().context
        return context.get('employee')

    @classmethod
    def default_startpos(cls):
        """ default: now
        """
        return datetime.now()

    @classmethod
    def default_state(cls):
        """ default: created
        """
        return WF_PERIOD_CREATED
    
    @classmethod
    def default_presence(cls):
        """ default: last used type
        """
        context = Transaction().context

        l1 = cls.search([('employee', '=', context.get('employee', -1))], 
                order=[('create_date', 'DESC')], limit=1)
        if len(l1) > 0:
            return l1[0].presence.id
        return None
        
    @fields.depends('employee')
    def on_change_with_bgcolor(self, name=None):
        if isinstance(self.employee, type(None)):
            return '#7CB9E8'
        else :
            if isinstance(self.employee.color, type(None)):
                return '#7CB9E8'
            else :
                return self.employee.color.rgbcode

    @fields.depends('presence')
    def on_change_with_textcolor(self, name=None):
        if isinstance(self.presence, type(None)):
            return '#000000'
        else :
            if isinstance(self.presence.color, type(None)):
                return '#000000'
            else :
                return self.presence.color.rgbcode
        
    @fields.depends('startpos', 'endpos')
    def on_change_with_weekday(self, name=None):
        """ get nr of weekday
        """
        if not isinstance(self.startpos, type(None)):
            return str(self.startpos.weekday())
        elif not isinstance(self.endpos, type(None)):
            return str(self.endpos.weekday())
        else :
            return None
        
    @classmethod
    def search_duration(cls, name, clause):
        """ sql-code for search in 'duration'
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        tab_period = cls.__table__()
        
        sql1 = tab_period.select(tab_period.id,
                    where=Operator(tab_period.endpos - tab_period.startpos, clause[2])
                )
        return [('id', 'in', sql1)]

    @fields.depends('startpos', 'endpos')
    def on_change_with_duration(self, name=None):
        """ calculates duration
        """
        if (not isinstance(self.startpos, type(None))) and \
           (not isinstance(self.endpos, type(None))):
            return self.endpos - self.startpos
        else :
            return None

    @classmethod
    def get_week_sql(cls):
        """ get sql-code for week
        """
        tab_period = cls.__table__()
        qu1 = tab_period.select(tab_period.id,
                    Cast(
                        DatePart('week', Coalesce(tab_period.startpos, tab_period.endpos)),
                        'integer').as_('week'),
                )
        return qu1

    @classmethod
    def get_week(cls, period, names):
        """ get week of period items
        """
        r1 = {'week': {}}
        cursor = Transaction().connection.cursor()
        sql1 = cls.get_week_sql()
        id_lst = [x.id for x in period]
        
        # prepare result
        for i in id_lst:
            r1['week'][i] = '-'
            
        qu2 = sql1.select(sql1.id, sql1.week,
                    where=sql1.id.in_(id_lst)
                )
        cursor.execute(*qu2)
        l2 = cursor.fetchall()
        
        for i in l2:
            (id1, name1) = i
            r1['week'][id1] = name1
        return r1

    @classmethod
    def search_week(cls, name, clause):
        """ search in week
        """
        sql1 = cls.get_week_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = sql1.select(sql1.id,
                where=Operator(sql1.week, clause[2])
            )
        return [('id', 'in', qu1)]

    @staticmethod
    def order_week(tables):
        table, _ = tables[None]
        Period = Pool().get('employee_timetracking.period')
        tab_period = Period.get_week_sql()
        
        qu1 = tab_period.select(tab_period.week,
                    where=(table.id==tab_period.id)
                )
        return [qu1]

    @staticmethod
    def order_name(tables):
        table, _ = tables[None]
        Period = Pool().get('employee_timetracking.period')
        tab_period = Period.__table__()
        
        qu1 = tab_period.select(Coalesce(tab_period.startpos, tab_period.endpos, tab_period.create_date),
                    where=(table.id==tab_period.id)
                )
        return [qu1]

    @classmethod
    def get_name1_sql(cls):
        """ get sql-code for name
        """
        pool = Pool()
        Presence = pool.get('employee_timetracking.presence')
        Company = pool.get('company.company')
        context = Transaction().context
        
        tab_per = cls.__table__()
        tab_pres = Presence.__table__()
        
        # get time zone of company
        # the database must convert to company time zone
        time_zone = 'UTC'
        time_info = ' UTC'
        id_company = context.get('company', None)
        if not isinstance(id_company, type(None)):
            tz1 = Company(id_company).timezone
            if not isinstance(tz1, type(None)):
                time_zone = tz1
                time_info = ''

        qu1 = tab_per.join(tab_pres, condition=tab_pres.id==tab_per.presence
            ).select(tab_per.id,
                Concat2(
                    Coalesce(ToChar(AtTimeZone(AtTimeZone(tab_per.startpos, 'UTC'), time_zone), 'HH24:MI'), '-'),
                    ' - ',
                    Coalesce(ToChar(AtTimeZone(AtTimeZone(tab_per.endpos, 'UTC'), time_zone), 'HH24:MI'), '-'),
                    time_info, ', ',
                    Coalesce(
                        ToChar(AtTimeZone(AtTimeZone(tab_per.startpos, 'UTC'), time_zone), 'YYYY-MM-DD'), 
                        ToChar(AtTimeZone(AtTimeZone(tab_per.endpos, 'UTC'), time_zone), 'YYYY-MM-DD'), 
                        '-'),
                    ' [', tab_pres.shortname, ']'
                ).as_('name')
            )
        return qu1
        
    @classmethod
    def get_name1(cls, period, names):
        """ get recname of period items
        """
        r1 = {'name': {}}
        cursor = Transaction().connection.cursor()
        sql1 = cls.get_name1_sql()
        id_lst = [x.id for x in period]
        
        # prepare result
        for i in id_lst:
            r1['name'][i] = '-'
            
        qu2 = sql1.select(sql1.id, sql1.name,
                    where=sql1.id.in_(id_lst)
                )
        cursor.execute(*qu2)
        l2 = cursor.fetchall()
        
        for i in l2:
            (id1, name1) = i
            r1['name'][id1] = name1
        return r1

    @classmethod
    def search_name1(cls, name, clause):
        """ search in recname
        """
        sql1 = cls.get_name1_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = sql1.select(sql1.id,
                where=Operator(sql1.name, clause[2])
            )
        return [('id', 'in', qu1)]

    @classmethod
    def get_is_eval_locked_sql(cls):
        """ get sql-code for 'is_eval_locked'
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        tab_eval = Evaluation.__table__()
        tab_per = cls.__table__()
        
        qu1 = tab_eval.join(tab_per, condition=tab_per.employee==tab_eval.employee
            ).select(tab_per.id.as_('id_per'),
                Case(
                    ((Extract('year', tab_per.startpos) == Extract('year', tab_eval.evaldate)) & \
                     (Extract('month', tab_per.startpos) == Extract('month', tab_eval.evaldate)) & \
                     (tab_eval.state == WF_EVALUATION_LOCK), True),
                    else_ = False
                ).as_('locked'),
            )
        return qu1

    @classmethod
    def get_is_eval_locked(cls, periods, names):
        """ get state of evaluation
        """
        r1 = {'is_eval_locked': {}}
        id_lst = [x.id for x in periods]
        tab_lock = cls.get_is_eval_locked_sql()
        cursor = Transaction().connection.cursor()
        
        # prepare result
        for i in id_lst:
            r1['is_eval_locked'][i] = False
        
        qu1 = tab_lock.select(tab_lock.id_per,
                tab_lock.locked,
                where=tab_lock.id_per.in_(id_lst)
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        
        for i in l1:
            (id1, lock1) = i
            r1['is_eval_locked'][id1] = lock1
        return r1
    
    @classmethod
    def search_is_eval_locked(cls, name, clause):
        """ search in 'is_eval_locked'
        """
        tab_lock = cls.get_is_eval_locked_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        if (clause[1] == '=') and (clause[2] == False):
            tab_per = cls.__table__()

            # list of false
            qu1 = tab_lock.select(tab_lock.id_per,
                    where=Operator(tab_lock.locked, clause[2])
                )
            # get period not in list of true/false
            qu2 = tab_per.select(tab_per.id,
                    where=~tab_per.id.in_(tab_lock.select(tab_lock.id_per))
                )
            return ['OR', ('id', 'in', qu1), ('id', 'in', qu2)]
        elif clause[1] == 'in':
            raise Exception("search with 'in' not allowed")
        else :
            qu1 = tab_lock.select(tab_lock.id_per,
                    where=Operator(tab_lock.locked, clause[2])
                )
            return [('id', 'in', qu1)]
        
    @fields.depends('employee')
    def on_change_with_presences(self, name=None):
        """ get presences
        """
        if isinstance(self.employee, type(None)):
            return []
        if isinstance(self.employee.tariff, type(None)):
            return []
        if isinstance(self.employee.tariff.presence, type(None)):
            return []
        return [x.id for x in self.employee.tariff.presence]

    @fields.depends('employee', 'presence')
    def on_change_employee(self):
        """ clear presence if no employee
        """
        if isinstance(self.employee, type(None)):
            self.presence = None

    @fields.depends('startpos', 'endpos')
    def on_change_startpos(self):
        """ move endpos to 'startpos + 5min'
        """
        if not isinstance(self.endpos, type(None)):
            if not isinstance(self.startpos, type(None)):
                if self.startpos >= self.endpos:
                    self.endpos = self.startpos + timedelta(seconds=5*60)

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_PERIOD_CREATED)
    def wfcreate(cls, period):
        """ create period item
        """
        TimeAccountItem = Pool().get('employee_timetracking.timeaccountitem')
        for i in period:
            # delete existing account items - if not already evaluated
            d1 = True
            for k in i.accountitem:
                if k.state == WF_ACCOUNT_LOCK:
                    TimeAccountItem.wfcreate([k])
                if k.state == WF_ACCOUNT_EVALUATED:
                    d1 = False
            if d1 == True:
                TimeAccountItem.delete(i.accountitem)

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_PERIOD_EXAMINE)
    def wfexamine(cls, period):
        """ check period item
        """
        # create time account items
        pool = Pool()
        AccountRule = pool.get('employee_timetracking.accountrule')
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')

        for i in period:
            if isinstance(i.startpos, type(None)) or isinstance(i.endpos, type(None)):
                cls.raise_user_error('wfexamine_misstimes')

            if len(i.accountitem) == 0:
                AccountRule.add_item_by_rules(i.employee.tariff.accountrule, i)
                # mark evaluation-item for recalc
                TimeAccountItem.wfexamine(i.accountitem)

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_PERIOD_LOCK)
    def wflock(cls, period):
        """ lock period item
        """
        TimeAccountItem = Pool().get('employee_timetracking.timeaccountitem')
        
        # lock connected time account items
        for i in period:
            for k in i.accountitem:
                if k.state == WF_ACCOUNT_CREATED:
                    TimeAccountItem.wfexamine([k])
                    TimeAccountItem.wflock([k])
                elif k.state == WF_ACCOUNT_EXAMINE:
                    TimeAccountItem.wflock([k])

    @classmethod
    def get_state_month_sql(cls):
        """ sql-code
        """
        tab_period = cls.__table__()
        q1 = tab_period.select(tab_period.id,
                    Case (
                        (tab_period.startpos == None, 
                            Case (
                                (tab_period.endpos > CurrentDate(), 0),
                                else_ = Cast(
                                    (DatePart('year', CurrentDate()) - 
                                     DatePart('year', tab_period.endpos)) * 12 + 
                                    (DatePart('month', CurrentDate()) - 
                                     DatePart('month', tab_period.endpos))
                                    , 'integer'),
                            )
                        ),
                        (tab_period.startpos > CurrentDate(), 0),
                        else_ = Cast(
                                    (DatePart('year', CurrentDate()) - 
                                     DatePart('year', tab_period.startpos)) * 12 + 
                                    (DatePart('month', CurrentDate()) - 
                                     DatePart('month', tab_period.startpos))
                                , 'integer')
                    ).as_('month')
                )
        return q1

    @classmethod
    def get_state_month(cls, period, names):
        """ get month of period-item: 0 = current, 1 = last, 2,... = older
        """
        r1 = {'state_month': {}}
        cursor = Transaction().connection.cursor()
        
        sql1 = cls.get_state_month_sql()
        qu2 = sql1.select(sql1.id, sql1.month,
                    where=sql1.id.in_([x.id for x in period])
                )
        cursor.execute(*qu2)
        l2 = cursor.fetchall()
        
        for i in l2:
            (id1, m1) = i
            r1['state_month'][id1] = m1
        return r1

    @classmethod
    def search_state_month(cls, name, clause):
        """ search in state_month
        """
        sql1 = cls.get_state_month_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = sql1.select(sql1.id,
                where=Operator(sql1.month, clause[2])
            )
        return [('id', 'in', qu1)]
        
    @classmethod
    def deny_overlap(cls, values):
        """ raise exception if overlap
        """
        pool = Pool()
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        Period = pool.get('employee_timetracking.period')
        
        l1 = BreakPeriod.get_overlaps(Period, 
            values['employee'], 
            values.get('period', None), 
            values['startpos'], values['endpos'])
        
        if len(l1) > 0:
            # fire exception because overlap in db
            obj1 = Period(l1[0])
            cls.raise_user_error('overlap_period', (obj1.name))
    
    @classmethod
    def write(cls, *args):
        """ write item, deny time range overlap
        """
        actions = iter(args)
        for items, values in zip(actions, actions):
            for i in items:
                if ('state' in values.keys()) and (len(values.keys()) == 1):
                    # edit of 'state' is allowed, even if evaluation is locked
                    pass
                elif i.state in [WF_PERIOD_EXAMINE, WF_PERIOD_LOCK]:
                    cls.raise_user_error('period_locked', i.name)
                elif i.is_eval_locked == True:
                    cls.raise_user_error('eval_locked', i.name)

                # deny overlap of start/end
                if ('startpos' in values.keys()) or ('endpos' in values.keys()):
                    values2 = {}
                    values2.update(values)
                    values2['startpos'] = values.get('startpos', None)
                    values2['endpos'] = values.get('endpos', None)
                    values2['period'] = i
                    values2['employee'] = i.employee.id
                    cls.deny_overlap(values2)

        super(Period, cls).write(*args)

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('employee'):
                values['employee'] = cls.default_employee()

            # check if evaluation is locked
            datetocheck = values.get('startpos', None)
            if isinstance(datetocheck, type(None)):
                datetocheck = values.get('endpos')
            if not isinstance(datetocheck, type(None)):
                datetocheck = date(datetocheck.year, datetocheck.month, 1)
                evlst = Evaluation.search([
                        ('employee', '=', values['employee']),
                        ('state', '=', WF_EVALUATION_LOCK),
                        ('evaldate', '=', datetocheck),
                    ])
                if len(evlst) > 0:
                    # evaluation exists and is locked - deny create
                    cls.raise_user_error('eval_locked', '-/-')
            
            # deny overlap of start/end
            if ('startpos' in values.keys()) and ('endpos' in values.keys()):
                cls.deny_overlap(values)

        return super(Period, cls).create(vlist)

    @classmethod
    def delete(cls, period):
        """ deny delete if locked
        """
        for i in period:
            if (i.state == WF_PERIOD_LOCK) or (i.is_eval_locked == True):
                cls.raise_user_error('delete_period')
        return super(Period, cls).delete(period)
        
# end Period
