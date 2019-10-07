# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# BreakPeriod: employee can enter pause periods,
# these periods will be collected per day,
# the BreakTime-rules will fill up pause periods to the minimum pause
# period per working day as defined in the tariff model

from trytond.model import Workflow, ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id, And, Or
from trytond.transaction import Transaction
from sql.functions import CurrentDate, DatePart, Extract, ToChar, AtTimeZone
from sql.conditionals import Case, Coalesce
from sql import Cast
from sqlextension import Concat2, Overlaps
from datetime import datetime, timedelta, date
from trytond.modules.employee_timetracking.const import WF_BREAKPERIOD_CREATED, \
    WF_BREAKPERIOD_EXAMINE, WF_BREAKPERIOD_LOCK, WF_EVALUATION_LOCK,\
    sel_weekday


__all__ = ['BreakPeriod']
__metaclass__ = PoolMeta


sel_state = [
        (WF_BREAKPERIOD_CREATED, u'Editable'),
        (WF_BREAKPERIOD_EXAMINE, u'Examine'),
        (WF_BREAKPERIOD_LOCK, u'Locked')
    ]


class BreakPeriod(Workflow, ModelSQL, ModelView):
    'break times'
    __name__ = 'employee_timetracking.breakperiod'
    
    name = fields.Function(fields.Char(string=u'Name', readonly=True), 
        'get_name1', searcher='search_name1')
    employee = fields.Many2One(string=u'Employee', model_name='company.employee',
        states={
            'readonly': 
                ~And(
                    Eval('state', '') == WF_BREAKPERIOD_CREATED,
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
    startpos = fields.DateTime(string=u'Start', help=u'Beginning of the break',
        states = {
            'readonly':
                Or(
                    And(
                        Eval('state', '') != WF_BREAKPERIOD_CREATED, 
                        Id('employee_timetracking', 'group_timetracking_employee')\
                            .in_(Eval('context', {}).get('groups', [])),
                        ),
                    Eval('state', '') == WF_BREAKPERIOD_LOCK,
                    Eval('is_eval_locked', False) == True,
                )
            }, depends=['state', 'is_eval_locked'])
    endpos = fields.DateTime(string=u'End', help=u'End of the break',
        states = {
            'readonly':
                Or(
                    And(
                        Eval('state', '') != WF_BREAKPERIOD_CREATED, 
                        Id('employee_timetracking', 'group_timetracking_employee')\
                            .in_(Eval('context', {}).get('groups', [])),
                        ),
                    Eval('state', '') == WF_BREAKPERIOD_LOCK,
                    Eval('is_eval_locked', False) == True,
                )
            }, depends=['state', 'is_eval_locked'])
    state = fields.Selection(selection=sel_state, string=u'State', select=True, readonly=True)

    # views
    state_month = fields.Function(fields.Integer(string=u'Month', readonly=True), 
            'get_state_month', searcher='search_state_month')
    duration = fields.Function(fields.TimeDelta(string=u'Duration', readonly=True),
            'on_change_with_duration', searcher='search_duration')
    is_eval_locked = fields.Function(fields.Boolean(string=u'Evaluation locked', readonly=True,
            states={'invisible': True}), 'get_is_eval_locked', searcher='search_is_eval_locked')
    weekday = fields.Function(fields.Selection(string=u'Weekday', readonly=True, 
            selection=sel_weekday), 'on_change_with_weekday')
    week = fields.Function(fields.Integer(string=u'Week', readonly=True, 
            help=u'Calendar week'), 'get_week', searcher='search_week')
    bgcolor = fields.Function(fields.Char(string=u'Background color', readonly=True), 
            'on_change_with_bgcolor')
    
    @classmethod
    def __setup__(cls):
        super(BreakPeriod, cls).__setup__()
        tab_break = cls.__table__()
        cls._order.insert(0, ('name', 'DESC'))
        cls._transitions |= set((
            (WF_BREAKPERIOD_CREATED, WF_BREAKPERIOD_EXAMINE),
            (WF_BREAKPERIOD_EXAMINE, WF_BREAKPERIOD_LOCK),
            (WF_BREAKPERIOD_LOCK, WF_BREAKPERIOD_CREATED),
            ))
        cls._error_messages.update({
            'wfexamine_misstimes': (u"Enter start and end time before moving on."),
            'eval_locked': (u"Edit denied, the evaluation period of the break time item '%s' is locked."),
            'delete_breaktime': (u"The break time entry is in the 'locked' state and can not be deleted."),
            'overlap_breakperiod': (u"The break time item overlaps with this item: '%s'"),
            'breakperiod_locked': (u"Edit denied, the break time item '%s' is locked."),
            })
        cls._buttons.update({
            'wfcreate': {
                'invisible': 
                    ~And(
                        Eval('state', '') == WF_BREAKPERIOD_LOCK,
                        Or(
                            Id('employee_timetracking', 'group_worktime_edit')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                        ),
                    )
                },
            'wfexamine': {
                'invisible': 
                    ~And(
                        Eval('state', '') == WF_BREAKPERIOD_CREATED,
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
                        Eval('state') == WF_BREAKPERIOD_EXAMINE,
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
        cls._sql_constraints.extend([
            ('uniq_startpos', 
            Unique(tab_break, tab_break.employee, tab_break.startpos), 
            u'This start time is already in use.'),
            ('uniq_endpos', 
            Unique(tab_break, tab_break.employee, tab_break.endpos), 
            u'This end time is already in use.'),
            ('order_times', 
            Check(tab_break, tab_break.startpos < tab_break.endpos), 
            u'End time must be after start time.'),
            ('not_empty', 
            Check(tab_break, (tab_break.startpos != None) | (tab_break.endpos != None)), 
            u'Please enter a time.'),
            ('valid_lock', 
            Check(tab_break, (tab_break.startpos != None) & (tab_break.endpos != None) & \
                              (tab_break.state.in_([WF_BREAKPERIOD_LOCK, WF_BREAKPERIOD_EXAMINE])) | \
                              (tab_break.state == WF_BREAKPERIOD_CREATED)), 
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
        return WF_BREAKPERIOD_CREATED
    
    @fields.depends('startpos', 'endpos')
    def on_change_startpos(self):
        """ move endpos to 'startpos + 5min'
        """
        if not isinstance(self.endpos, type(None)):
            if self.startpos >= self.endpos:
                self.endpos = self.startpos + timedelta(seconds=5*60)
    
    @classmethod
    def search_duration(cls, name, clause):
        """ sql-code for search in 'duration'
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        tab_break = cls.__table__()
        
        sql1 = tab_break.select(tab_break.id,
                    where=Operator(tab_break.endpos - tab_break.startpos, clause[2])
                )
        return [('id', 'in', sql1)]

    @fields.depends('employee')
    def on_change_with_bgcolor(self, name=None):
        if isinstance(self.employee, type(None)):
            return '#7CB9E8'
        else :
            if isinstance(self.employee.color, type(None)):
                return '#7CB9E8'
            else :
                return self.employee.color.rgbcode
        
    @fields.depends('startpos', 'endpos')
    def on_change_with_duration(self, name=None):
        """ calculates duration
        """
        if (not isinstance(self.startpos, type(None))) and \
           (not isinstance(self.endpos, type(None))):
            return self.endpos - self.startpos
        else :
            return None

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
    def get_name1_sql(cls):
        """ get sql-code for name
        """
        pool = Pool()
        Company = pool.get('company.company')
        context = Transaction().context
        
        tab_per = cls.__table__()
        
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

        qu1 = tab_per.select(tab_per.id,
                Concat2(
                    Coalesce(ToChar(AtTimeZone(AtTimeZone(tab_per.startpos, 'UTC'), time_zone), 'HH24:MI'), '-'),
                    ' - ',
                    Coalesce(ToChar(AtTimeZone(AtTimeZone(tab_per.endpos, 'UTC'), time_zone), 'HH24:MI'), '-'),
                    time_info, ', ',
                    Coalesce(
                        ToChar(AtTimeZone(AtTimeZone(tab_per.startpos, 'UTC'), time_zone), 'YYYY-MM-DD'), 
                        ToChar(AtTimeZone(AtTimeZone(tab_per.endpos, 'UTC'), time_zone), 'YYYY-MM-DD'), 
                        '-')
                ).as_('name')
            )
        return qu1
        
    @classmethod
    def get_name1(cls, breakperiod, names):
        """ get recname of break items
        """
        r1 = {'name': {}}
        cursor = Transaction().connection.cursor()
        sql1 = cls.get_name1_sql()
        id_lst = [x.id for x in breakperiod]
        
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

    @staticmethod
    def order_name(tables):
        table, _ = tables[None]
        BreakPeriod = Pool().get('employee_timetracking.breakperiod')
        tab_break = BreakPeriod.__table__()
        
        qu1 = tab_break.select(Coalesce(tab_break.startpos, tab_break.endpos, tab_break.create_date),
                    where=(table.id==tab_break.id)
                )
        return [qu1]

    @classmethod
    def get_week_sql(cls):
        """ get sql-code for week
        """
        tab_break = cls.__table__()
        qu1 = tab_break.select(tab_break.id,
                    Cast(
                        DatePart('week', Coalesce(tab_break.startpos, tab_break.endpos)),
                        'integer').as_('week'),
                )
        return qu1

    @classmethod
    def get_week(cls, breakperiod, names):
        """ get week of break time items
        """
        r1 = {'week': {}}
        cursor = Transaction().connection.cursor()
        sql1 = cls.get_week_sql()
        id_lst = [x.id for x in breakperiod]
        
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

    @classmethod
    def get_state_month_sql(cls):
        """ sql-code
        """
        tab_break = cls.__table__()
        q1 = tab_break.select(tab_break.id,
                    Case (
                        (tab_break.startpos == None, 0),
                        (tab_break.startpos > CurrentDate(), 0),
                        else_ = Cast(
                                    (DatePart('year', CurrentDate()) - 
                                     DatePart('year', tab_break.startpos)) * 12 + 
                                    (DatePart('month', CurrentDate()) - 
                                     DatePart('month', tab_break.startpos))
                                , 'integer')
                    ).as_('month')
                )
        return q1

    @classmethod
    def get_state_month(cls, period, names):
        """ get month of break-item: 0 = current, 1 = last, 2,... = older
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
    def get_is_eval_locked_sql(cls):
        """ get sql-code for 'is_eval_locked'
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        tab_eval = Evaluation.__table__()
        tab_break = cls.__table__()
        
        qu1 = tab_eval.join(tab_break, condition=tab_break.employee==tab_eval.employee
            ).select(tab_break.id.as_('id_break'),
                Case(
                    ((Extract('year', tab_break.startpos) == Extract('year', tab_eval.evaldate)) & \
                     (Extract('month', tab_break.startpos) == Extract('month', tab_eval.evaldate)) & \
                     (tab_eval.state == WF_EVALUATION_LOCK), True),
                    else_ = False
                ).as_('locked'),
            )
        return qu1

    @classmethod
    def get_is_eval_locked(cls, breakperiods, names):
        """ get state of evaluation
        """
        r1 = {'is_eval_locked': {}}
        id_lst = [x.id for x in breakperiods]
        tab_lock = cls.get_is_eval_locked_sql()
        cursor = Transaction().connection.cursor()
        
        # prepare result
        for i in id_lst:
            r1['is_eval_locked'][i] = False
        
        qu1 = tab_lock.select(tab_lock.id_break,
                tab_lock.locked,
                where=tab_lock.id_break.in_(id_lst)
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
            tab_break = cls.__table__()

            # list of false
            qu1 = tab_lock.select(tab_lock.id_break,
                    where=Operator(tab_lock.locked, clause[2])
                )
            # get period not in list of true/false
            qu2 = tab_break.select(tab_break.id,
                    where=~tab_break.id.in_(tab_lock.select(tab_lock.id_break))
                )
            return ['OR', ('id', 'in', qu1), ('id', 'in', qu2)]
        elif clause[1] == 'in':
            raise Exception("search with 'in' not allowed")
        else :
            qu1 = tab_lock.select(tab_lock.id_break,
                    where=Operator(tab_lock.locked, clause[2])
                )
            return [('id', 'in', qu1)]

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_BREAKPERIOD_CREATED)
    def wfcreate(cls, breakperiod):
        """ create break item
        """
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_BREAKPERIOD_EXAMINE)
    def wfexamine(cls, breakperiod):
        """ check break item
        """
        for i in breakperiod:
            if isinstance(i.startpos, type(None)) or isinstance(i.endpos, type(None)):
                cls.raise_user_error('wfexamine_misstimes')

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_BREAKPERIOD_LOCK)
    def wflock(cls, breakperiod):
        """ lock break item
        """
        pass

    @classmethod
    def get_overlaps(cls, dbmodel, id_employee, itemobj, startpos, endpos):
        """ get ids of overlapping break time items
            dbmodel = Model, Period or BreakPeriod,
            itemobj = current item to edit (if None: startpos+endpos must set)
            startpos/endpos = values to check (id None: take from period)
        """
        cursor = Transaction().connection.cursor()
        tab_period = dbmodel.__table__()
        
        if not isinstance(itemobj, type(None)):
            if isinstance(startpos, type(None)):
                startpos = itemobj.startpos
            if isinstance(endpos, type(None)):
                endpos = itemobj.endpos
        
        if isinstance(itemobj, type(None)):
            id_ignore = -1
        else :
            id_ignore = itemobj.id

        l2 = []
        if isinstance(startpos, type(None)) and (not isinstance(endpos, type(None))):
            # check if endpos is within other period
            l1 = dbmodel.search([
                    ('employee.id', '=', id_employee),
                    ('startpos', '<=', endpos),
                    ('endpos', '>=', endpos),
                ])
            for i in l1:
                l2.append(i.id)
        elif (not isinstance(startpos, type(None))) and isinstance(endpos, type(None)):
            # check if endpos is within other period
            l1 = dbmodel.search([
                    ('employee.id', '=', id_employee),
                    ('startpos', '<=', startpos),
                    ('endpos', '>=', startpos),
                ])
            for i in l1:
                l2.append(i.id)
        else :
            qu1 = tab_period.select(tab_period.id,
                        where=(tab_period.id != id_ignore) & 
                            (Overlaps(startpos, endpos, tab_period.startpos, tab_period.endpos) == True) & 
                            (tab_period.employee == id_employee)
                    )
            cursor.execute(*qu1)
            l1 = cursor.fetchall()
            for i in l1:
                (id1, ) = i
                l2.append(id1)
        return l2

    @classmethod
    def deny_overlap(cls, values):
        """ raise exception if overlap
        """
        pool = Pool()
        BreakPeriod = pool.get('employee_timetracking.breakperiod')
        
        l1 = BreakPeriod.get_overlaps(BreakPeriod, 
            values['employee'], 
            values.get('breakperiod', None), 
            values['startpos'], values['endpos'])
        
        if len(l1) > 0:
            # fire exception because overlap in db
            obj1 = BreakPeriod(l1[0])
            cls.raise_user_error('overlap_breakperiod', (obj1.name))

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

        return super(BreakPeriod, cls).create(vlist)

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
                elif i.state in [WF_BREAKPERIOD_EXAMINE, WF_BREAKPERIOD_LOCK]:
                    cls.raise_user_error('breakperiod_locked', i.name)
                elif i.is_eval_locked == True:
                    cls.raise_user_error('eval_locked', i.name)

                # deny overlap of start/end
                if ('startpos' in values.keys()) or ('endpos' in values.keys()):
                    values2 = {}
                    values2.update(values)
                    values2['startpos'] = values.get('startpos', None)
                    values2['endpos'] = values.get('endpos', None)
                    values2['breakperiod'] = i
                    values2['employee'] = i.employee.id
                    cls.deny_overlap(values2)

        super(BreakPeriod, cls).write(*args)

    @classmethod
    def delete(cls, breaktime):
        """ deny delete if locked
        """
        for i in breaktime:
            if (i.state == WF_BREAKPERIOD_LOCK) or (i.is_eval_locked == True):
                cls.raise_user_error('delete_breaktime')
        return super(BreakPeriod, cls).delete(breaktime)

# end BreakPeriod
