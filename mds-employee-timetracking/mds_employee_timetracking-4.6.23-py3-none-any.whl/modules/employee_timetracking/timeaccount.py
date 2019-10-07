# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


from trytond.model import Workflow, ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id, Or, And
from trytond.transaction import Transaction
from datetime import datetime, date
from sql.functions import DatePart, CurrentDate, ToChar, AtTimeZone
from sql.conditionals import Case, Coalesce
from sql import Cast
from sqlextension import Overlaps, Concat2
from trytond.modules.employee_timetracking.const import WF_ACCOUNT_CREATED, \
    WF_ACCOUNT_EXAMINE, WF_ACCOUNT_LOCK, WF_ACCOUNT_EVALUATED, sel_weekday
from trytond.modules.employee_timetracking.evaluation import WF_EVALUATION_LOCK


__all__ = ['TimeAccount', 'TimeAccountItem']
__metaclass__ = PoolMeta


sel_state = [
        (WF_ACCOUNT_CREATED, u'Created'),
        (WF_ACCOUNT_EXAMINE, u'Examine'),
        (WF_ACCOUNT_LOCK, u'Locked'),
        (WF_ACCOUNT_EVALUATED, u'Evaluated')
    ]


class TimeAccount(ModelSQL, ModelView):
    'time account'
    __name__ = 'employee_timetracking.timeaccount'
    
    name = fields.Char(string=u'Name', required=True)
    shortname = fields.Char(string=u'shorthand symbol', required=True, size=4,
        help=u'The shorthand symbol appears in the tables of the reports.')
    company = fields.Many2One(string=u'Company', model_name='company.company',
        states={
            'readonly': ~Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
        }, required=True, select=True)
    color = fields.Many2One(string=u'Text Color', ondelete='SET NULL',
            help=u'Text color in the calendar view', 
            model_name="employee_timetracking.colors")

    @classmethod
    def __setup__(cls):
        super(TimeAccount, cls).__setup__()
        tab_tacc = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_tacc, tab_tacc.name, tab_tacc.company), 
            u'This name is already in use.'),
            ('uniq_shortname', 
            Unique(tab_tacc, tab_tacc.shortname, tab_tacc.company), 
            u'This shorthand symbol is already in use.'),
            ])

    @classmethod
    def default_color(cls):
        """ get 'col_azure'
        """
        pool = Pool()
        Colors = pool.get('employee_timetracking.colors')
        ModelData = pool.get('ir.model.data')
        
        try :
            col1 = Colors(ModelData.get_id('employee_timetracking', 'col_azure'))
        except :
            return None
        return col1.id

    @classmethod
    def default_company(cls):
        """ set active company to default
        """
        context = Transaction().context
        return context.get('company')

# end TimeAccount



class TimeAccountItem(Workflow, ModelSQL, ModelView):
    'time account item'
    __name__ = 'employee_timetracking.timeaccountitem'
    
    name = fields.Function(fields.Char(string=u'Name', readonly=True), 
        'get_name1', searcher='search_name1')
    employee = fields.Many2One(string=u'Employee', model_name='company.employee',
        states={
            'readonly': 
                ~And(
                    Eval('state', '') == WF_ACCOUNT_CREATED,
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
    period = fields.Many2One(string=u'Presence time', model_name='employee_timetracking.period', 
        states={
            'readonly': 
                Or(
                    And(
                        Eval('state', '') != WF_ACCOUNT_CREATED, 
                        Id('employee_timetracking', 'group_timetracking_employee')\
                            .in_(Eval('context', {}).get('groups', [])),
                        ),
                    Eval('state', '') == WF_ACCOUNT_LOCK,
                    Eval('is_eval_locked', False) == True,
                )
            }, 
        required=True, ondelete='CASCADE', depends=['employee', 'state', 'is_eval_locked'],
        domain=[('employee', '=', Eval('employee'))])
    account = fields.Many2One(string=u'Time Account', model_name='employee_timetracking.timeaccount', 
        states={
            'readonly': 
                Or(
                    And(
                        Eval('state', '') != WF_ACCOUNT_CREATED, 
                        Id('employee_timetracking', 'group_timetracking_employee')\
                            .in_(Eval('context', {}).get('groups', [])),
                        ),
                    Eval('state', '') == WF_ACCOUNT_LOCK,
                    Eval('is_eval_locked', False) == True,
                )
            }, 
        required=True, ondelete='RESTRICT', select=True, depends=['state', 'is_eval_locked'])
    accountrule = fields.Many2One(string=u'Account rule', model_name='employee_timetracking.accountrule', 
        help=u'applied time account rule',
        states={
            'readonly': 
                Or(
                    And(
                        Eval('state', '') != WF_ACCOUNT_CREATED, 
                        Id('employee_timetracking', 'group_timetracking_employee')\
                            .in_(Eval('context', {}).get('groups', [])),
                        ),
                    Eval('state', '') == WF_ACCOUNT_LOCK,
                    Eval('is_eval_locked', False) == True,
                )
            }, 
        required=True, ondelete='RESTRICT', depends=['state', 'is_eval_locked'])
    evaluation = fields.Many2One(string=u'Evaluation', model_name='employee_timetracking.evaluation', 
        states={
            'readonly': 
                Or(
                    And(
                        Eval('state', '') != WF_ACCOUNT_CREATED, 
                        Id('employee_timetracking', 'group_timetracking_employee')\
                            .in_(Eval('context', {}).get('groups', [])),
                        ),
                    Eval('state', '') == WF_ACCOUNT_LOCK,
                    Eval('is_eval_locked', False) == True,
                )
            }, 
        required=True, ondelete='RESTRICT', depends=['employee', 'state', 'is_eval_locked'],
        domain=[('employee', '=', Eval('employee'))], select=True)
    startpos = fields.DateTime(string=u'Start', required=True, select=True,
        states = {
            'readonly': 
                Or(
                    And(
                        Eval('state', '') != WF_ACCOUNT_CREATED, 
                        Id('employee_timetracking', 'group_timetracking_employee')\
                            .in_(Eval('context', {}).get('groups', [])),
                        ),
                    Eval('state', '') == WF_ACCOUNT_LOCK,
                    Eval('is_eval_locked', False) == True,
                )
            }, depends=['state', 'is_eval_locked'])
    endpos = fields.DateTime(string=u'End', required=True, select=True,
        states = {
            'readonly': 
                Or(
                    And(
                        Eval('state', '') != WF_ACCOUNT_CREATED, 
                        Id('employee_timetracking', 'group_timetracking_employee')\
                            .in_(Eval('context', {}).get('groups', [])),
                        ),
                    Eval('state', '') == WF_ACCOUNT_LOCK,
                    Eval('is_eval_locked', False) == True,
                )
            }, depends=['is_eval_locked', 'state'])
    state = fields.Selection(selection=sel_state, string=u'State', select=True, readonly=True)

    # views
    state_month = fields.Function(fields.Integer(string=u'Month', readonly=True), 
            'get_state_month', searcher='search_state_month')
    duration = fields.Function(fields.TimeDelta(string=u'Duration', readonly=True),
            'on_change_with_duration', searcher='search_duration')
    duration_wfactor = fields.Function(fields.TimeDelta(string=u'Duration', readonly=True),
            'on_change_with_duration_wfactor')
    weekday = fields.Function(fields.Selection(string=u'Weekday', readonly=True, 
            selection=sel_weekday), 'on_change_with_weekday')
    week = fields.Function(fields.Integer(string=u'Week', readonly=True, 
            help=u'Calendar week'), 'get_week', searcher='search_week')
    is_eval_locked = fields.Function(fields.Boolean(string=u'Evaluation locked', readonly=True,
            states={'invisible': True}), 'get_is_eval_locked', searcher='search_is_eval_locked')
    textcolor = fields.Function(fields.Char(string=u'Text color', readonly=True), 
            'on_change_with_textcolor')
    bgcolor = fields.Function(fields.Char(string=u'Background color', readonly=True), 
            'on_change_with_bgcolor')

    @classmethod
    def __setup__(cls):
        super(TimeAccountItem, cls).__setup__()
        cls._order.insert(0, ('startpos', 'DESC'))
        tab_account = cls.__table__()
        cls._transitions |= set((
            (WF_ACCOUNT_CREATED, WF_ACCOUNT_EXAMINE),
            (WF_ACCOUNT_EXAMINE, WF_ACCOUNT_LOCK),
            (WF_ACCOUNT_LOCK, WF_ACCOUNT_CREATED),
            ))
        cls._error_messages.update({
            'delete_accitem': (u"The time account item is in the 'locked' state and can not be deleted or edited."),
            'overlap_accitem': (u"The time account item overlaps with this item: '%s'"),
            'eval_locked': (u"Edit denied, the evaluation period of the time account item '%s' is locked."),
            })
        cls._sql_constraints.extend([
            ('uniq_startpos', 
            Unique(tab_account, tab_account.employee, tab_account.startpos, tab_account.account), 
            u'This start time is already in use.'),
            ('uniq_endpos', 
            Unique(tab_account, tab_account.employee, tab_account.endpos, tab_account.account), 
            u'This end time is already in use.'),
            ('order_times', 
            Check(tab_account, tab_account.startpos < tab_account.endpos), 
            u'End time must be after start time.'),
            ])
        cls._buttons.update({
            'wfcreate': {
                'invisible': 
                    Or(
                        Id('employee_timetracking', 'group_timetracking_employee')\
                                .in_(Eval('context', {}).get('groups', [])),
                        Id('employee_timetracking', 'group_worktime_edit')\
                                .in_(Eval('context', {}).get('groups', [])),
                        Eval('state', '') != WF_ACCOUNT_LOCK,
                    )
                },
            'wfexamine': {
                'invisible': 
                    ~Or(
                        And(
                            Id('employee_timetracking', 'group_timetracking_employee')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Eval('state', '') == WF_ACCOUNT_CREATED,
                        ),
                        And(
                            Id('employee_timetracking', 'group_worktime_edit')\
                                    .in_(Eval('context', {}).get('groups', [])),
                            Eval('state', '').in_([WF_ACCOUNT_CREATED, WF_ACCOUNT_LOCK]),
                        ),
                        And(
                            Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                            Eval('state', '').in_([WF_ACCOUNT_CREATED, WF_ACCOUNT_LOCK]),
                        )
                    )
                },
            'wflock': {
                'invisible': 
                    ~And(
                        Eval('state') == WF_ACCOUNT_EXAMINE,
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

    @classmethod
    def default_state(cls):
        """ default: created
        """
        return WF_ACCOUNT_CREATED

    @classmethod
    def default_employee(cls):
        """ default: current user-employee
        """
        context = Transaction().context
        return context.get('employee')

    @classmethod
    def get_state_month_sql(cls):
        """ sql-code
        """
        tab_tacc = cls.__table__()
        q1 = tab_tacc.select(tab_tacc.id,
                Case (
                    (tab_tacc.startpos == None, 0),
                    (tab_tacc.startpos > CurrentDate(), 0),
                    else_ = Cast(
                                (DatePart('year', CurrentDate()) - 
                                 DatePart('year', tab_tacc.startpos)) * 12 + 
                                (DatePart('month', CurrentDate()) - 
                                 DatePart('month', tab_tacc.startpos))
                            , 'integer')
                ).as_('month')
            )
        return q1

    @classmethod
    def get_state_month(cls, timeaccount, names):
        """ get month of timeaccount-item: 0 = current, 1 = last, 2,... = older
        """
        r1 = {'state_month': {}}
        cursor = Transaction().connection.cursor()
        
        sql1 = cls.get_state_month_sql()
        qu2 = sql1.select(sql1.id, sql1.month,
                    where=sql1.id.in_([x.id for x in timeaccount])
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
    def search_duration(cls, name, clause):
        """ sql-code for search in 'duration'
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        tab_tacc = cls.__table__()
        
        sql1 = tab_tacc.select(tab_tacc.id,
                    where=Operator(tab_tacc.endpos - tab_tacc.startpos, clause[2])
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

    @fields.depends('account')
    def on_change_with_textcolor(self, name=None):
        if isinstance(self.account, type(None)):
            return '#000000'
        else :
            if isinstance(self.account.color, type(None)):
                return '#000000'
            else :
                return self.account.color.rgbcode

    @fields.depends('startpos', 'endpos', 'accountrule')
    def on_change_with_duration_wfactor(self, name=None):
        """ calculates duration
        """
        if isinstance(self.startpos, type(None)) or isinstance(self.endpos, type(None)) or \
            isinstance(self.accountrule, type(None)):
            return None
        
        return (self.endpos - self.startpos) * float(self.accountrule.factor)

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
    def get_is_eval_locked_sql(cls):
        """ get sql-code for 'is_eval_locked'
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        tab_eval = Evaluation.__table__()
        tab_accitm = cls.__table__()
        
        qu1 = tab_eval.join(tab_accitm, condition=tab_accitm.evaluation==tab_eval.id
            ).select(tab_accitm.id.as_('id_accitm'),
                Case(
                    (tab_eval.state == WF_EVALUATION_LOCK, True),
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
        
        qu1 = tab_lock.select(tab_lock.id_accitm,
                tab_lock.locked,
                where=tab_lock.id_accitm.in_(id_lst)
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
            tab_accitm = cls.__table__()

            # list of false
            qu1 = tab_lock.select(tab_lock.id_accitm,
                    where=Operator(tab_lock.locked, clause[2])
                )
            # get period not in list of true/false
            qu2 = tab_accitm.select(tab_accitm.id,
                    where=~tab_accitm.id.in_(tab_lock.select(tab_lock.id_accitm))
                )
            return ['OR', ('id', 'in', qu1), ('id', 'in', qu2)]
        elif clause[1] == 'in':
            raise Exception("search with 'in' not allowed")
        else :
            qu1 = tab_lock.select(tab_lock.id_accitm,
                    where=Operator(tab_lock.locked, clause[2])
                )
            return [('id', 'in', qu1)]

    @classmethod
    def get_week_sql(cls):
        """ get sql-code for week
        """
        tab_accitem = cls.__table__()
        qu1 = tab_accitem.select(tab_accitem.id,
                    Cast(
                            DatePart('week', tab_accitem.startpos),
                            'integer'
                        ).as_('week'),
                )
        return qu1

    @classmethod
    def get_week(cls, accitem, names):
        """ get week of time account items
        """
        r1 = {'week': {}}
        cursor = Transaction().connection.cursor()
        sql1 = cls.get_week_sql()
        id_lst = [x.id for x in accitem]
        
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
        TimeAccountItem = Pool().get('employee_timetracking.timeaccountitem')
        tab_accitem = TimeAccountItem.get_week_sql()
        
        qu1 = tab_accitem.select(tab_accitem.week,
                    where=(table.id==tab_accitem.id)
                )
        return [qu1]

    @classmethod
    def get_name1_sql(cls):
        """ get sql-code for name
        """
        pool = Pool()
        Account = pool.get('employee_timetracking.timeaccount')
        Company = pool.get('company.company')
        context = Transaction().context

        tab_accitem = cls.__table__()
        tab_acc = Account.__table__()
        
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

        qu1 = tab_acc.join(tab_accitem, condition=tab_acc.id==tab_accitem.account
            ).select(tab_accitem.id,
                Concat2(
                    Coalesce(ToChar(AtTimeZone(AtTimeZone(tab_accitem.startpos, 'UTC'), time_zone), 'HH24:MI'), '-'),
                    ' - ',
                    Coalesce(ToChar(AtTimeZone(AtTimeZone(tab_accitem.endpos, 'UTC'), time_zone), 'HH24:MI'), '-'),
                    time_info, ', ',
                    Coalesce(
                        ToChar(AtTimeZone(AtTimeZone(tab_accitem.startpos, 'UTC'), time_zone), 'YYYY-MM-DD'), 
                        ToChar(AtTimeZone(AtTimeZone(tab_accitem.endpos, 'UTC'), time_zone), 'YYYY-MM-DD'), 
                        '-'),
                    ' [', tab_acc.shortname, ']'
                ).as_('name')
            )
        return qu1
        
    @classmethod
    def get_name1(cls, accountitem, names):
        """ get recname of time account items
        """
        r1 = {'name': {}}
        cursor = Transaction().connection.cursor()
        sql1 = cls.get_name1_sql()
        id_lst = [x.id for x in accountitem]
        
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
    @ModelView.button
    @Workflow.transition(WF_ACCOUNT_CREATED)
    def wfcreate(cls, accountitem):
        """ create account item
        """
        DaysOfEvaluation = Pool().get('employee_timetracking.evaluation-dayofyear')
        for i in accountitem:
            DaysOfEvaluation.del_day_by_timeaccountitem(i)

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_ACCOUNT_EXAMINE)
    def wfexamine(cls, accountitem):
        """ check account item
        """
        pool = Pool()
        EvaluationItem = pool.get('employee_timetracking.evaluationitem')
        DaysOfEvaluation = pool.get('employee_timetracking.evaluation-dayofyear')
        
        for i in accountitem:
            # mark eval-item for recalc
            ev_obj = EvaluationItem.search([
                    ('evaluation.accountitems', '=', i.id),
                    ('account', '=', i.account)
                ])
            if len(ev_obj) == 1:
                ev_obj[0].evaluation.needs_recalc = True
                ev_obj[0].evaluation.save()
        
            # connect to days in evaluation
            DaysOfEvaluation.updt_day_by_timeaccountitem(i)

    @classmethod
    @ModelView.button
    @Workflow.transition(WF_ACCOUNT_LOCK)
    def wflock(cls, accountitem):
        """ lock account item
        """
        pass

    @classmethod
    def get_overlaps(cls, id_employee, id_account, startpos, endpos, ign_item=None):
        """ get ids of overlapping time account items
            id_employee / id_account = employee+account to check,
            startpos/endpos = values to check,
            ign_item = ignore item at check
        """
        cursor = Transaction().connection.cursor()
        tab_accitm = cls.__table__()

        if (not isinstance(id_employee, type(1))) or (not isinstance(id_account, type(1))):
            raise ValueError(u'id of employee or account invalid (employee=%s, account=%s)' % \
                (id_employee, id_account))
        
        if (not isinstance(startpos, type(datetime(2017, 1, 1, 10, 0, 0)))) or \
            (not isinstance(endpos, type(datetime(2017, 1, 1, 10, 0, 0)))):
            raise ValueError(u'startpos/endpos invalid (startpos=%s, endpos=%s)' % \
                (str(startpos), str(endpos)))

        if isinstance(ign_item, type(None)):
            id_ignore = -1
        else :
            id_ignore = ign_item.id

        qu1 = tab_accitm.select(tab_accitm.id,
                    where=(tab_accitm.id != id_ignore) & 
                        (tab_accitm.account == id_account) &
                        (tab_accitm.employee == id_employee) &
                        (Overlaps(startpos, endpos, tab_accitm.startpos, tab_accitm.endpos) == True)
                )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        l2 = []
        for i in l1:
            (id1, ) = i
            l2.append(id1)
        return l2

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
                elif i.state in [WF_ACCOUNT_LOCK, WF_ACCOUNT_EVALUATED]:
                    cls.raise_user_error('delete_accitem', i.name)
                elif i.is_eval_locked == True:
                    cls.raise_user_error('eval_locked', i.name)

                # deny overlap of start/end
                if ('startpos' in values.keys()) or ('endpos' in values.keys()):
                    id_emplo = values.get('employee', i.employee.id)
                    id_acc = values.get('account', i.account.id)

                    l1 = cls.get_overlaps(id_emplo, id_acc, 
                            values.get('startpos', i.startpos), 
                            values.get('endpos', i.endpos),
                            ign_item=i)
                    
                    if len(l1) > 0:
                        obj1 = TimeAccountItem(l1[0])
                        t1 = '%s: %s - %s' % \
                            (obj1.startpos.strftime('%d.%m.%Y'), 
                             obj1.startpos.strftime('%H:%M'), 
                             obj1.endpos.strftime('%H:%M'), 
                            )
                        cls.raise_user_error('overlap_accitem', (t1))
        super(TimeAccountItem, cls).write(*args)

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
            l1 = cls.get_overlaps(values['employee'], values['account'], \
                            values['startpos'], values['endpos'])
            if len(l1) > 0:
                obj1 = TimeAccountItem(l1[0])
                t1 = '%s: %s - %s' % \
                    (obj1.startpos.strftime('%Y-%m-%d'), 
                     obj1.startpos.strftime('%H:%M'), 
                     obj1.endpos.strftime('%H:%M'), 
                    )
                cls.raise_user_error('overlap_accitem', (t1))

        return super(TimeAccountItem, cls).create(vlist)

    @classmethod
    def delete(cls, accitem):
        """ deny delete if locked
        """
        DaysOfEvaluation = Pool().get('employee_timetracking.evaluation-dayofyear')
        
        for i in accitem:
            if (i.state in [WF_ACCOUNT_LOCK, WF_ACCOUNT_EVALUATED]) or (i.is_eval_locked == True):
                cls.raise_user_error('delete_accitem')
            
            # disconnect from evaluation-day
            DaysOfEvaluation.del_day_by_timeaccountitem(i)
            
        return super(TimeAccountItem, cls).delete(accitem)

# end TimeAccountItem
