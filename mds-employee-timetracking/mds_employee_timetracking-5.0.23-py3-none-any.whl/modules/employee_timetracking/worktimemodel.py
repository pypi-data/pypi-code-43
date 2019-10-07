# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# working time model
# The working time model determines which days are working days 
# and how many hours are worked on these days.


from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id
from trytond.transaction import Transaction
from decimal import Decimal
from datetime import time
from sql import Cast
from sql.aggregate import Sum
from sql.conditionals import Case
from sql.functions import Extract


__all__ = ['WorkTimeModel', 'WorkTimeRule']
__metaclass__ = PoolMeta


class WorkTimeModel(ModelSQL, ModelView):
    'Work time model'
    __name__ = 'employee_timetracking.worktimemodel'

    name = fields.Char(string=u'Name', required=True)
    shortname = fields.Char(string=u'shorthand symbol', required=True, size=4,
                    help=u'The shorthand symbol appears in the tables of the reports.')
    company = fields.Many2One(string=u'Company', model_name='company.company',
        states={
            'readonly': ~Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
        }, required=True, select=True)
    worktimerule = fields.One2Many(model_name='employee_timetracking.worktimerule',
                    field='wtmodel', string=u'Working time rule')
    hours_per_week = fields.Function(fields.Numeric(string=u'Hours/Week', readonly=True, 
        digits=(16, 1)), 'get_hours_per_week', searcher='search_hours_per_week')

    @classmethod
    def __setup__(cls):
        super(WorkTimeModel, cls).__setup__()
        tab_wtm = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_wtm, tab_wtm.name, tab_wtm.company), 
            u'This name is already in use.'),
            ('uniq_short', 
            Unique(tab_wtm, tab_wtm.shortname, tab_wtm.company), 
            u'This shorthand symbol is already in use.'),
            ])
        cls._error_messages.update({
            'range_overlap': (u"The from/to time range overlaps with the following rules: %s"),
            })

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        
        for values in vlist:
            if not values.get('company'):
                values['company'] = cls.default_company()
        return super(WorkTimeModel, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        """ update work time model for existing evaluations
        """
        super(WorkTimeModel, cls).write(*args)
        
        Evaluation = Pool().get('employee_timetracking.evaluation')
        (items, para) = args
        Evaluation.updt_worktime_model(items)

    @classmethod
    def default_company(cls):
        """ set active company to default
        """
        context = Transaction().context
        return context.get('company')

    def get_rec_name(self, name):
        """ create rec_name
        """
        return '%s - %.1f h' % (self.name, self.hours_per_week)

    @classmethod
    def get_hours_per_week_sql(cls):
        """ get sql-code for 'get_hours_per_week'
        """
        WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
        tab_wtr = WorkTimeRule.__table__()
        tab_wtm = cls.__table__()
        
        qu1 = tab_wtr.join(tab_wtm, condition=tab_wtr.wtmodel==tab_wtm.id
            ).select(tab_wtm.id.as_('id_model'),
                Sum(
                    (
                        Case((tab_wtr.mon == True, 1), else_ = 0) +
                        Case((tab_wtr.tue == True, 1), else_ = 0) +
                        Case((tab_wtr.wed == True, 1), else_ = 0) +
                        Case((tab_wtr.thu == True, 1), else_ = 0) +
                        Case((tab_wtr.fri == True, 1), else_ = 0) +
                        Case((tab_wtr.sat == True, 1), else_ = 0) +
                        Case((tab_wtr.sun == True, 1), else_ = 0)
                    ) * 
                    Case(
                        (tab_wtr.maxtime == time(0, 0), 
                            Cast('24:00:00', 'time') - tab_wtr.mintime
                        ),
                        else_ = tab_wtr.maxtime - tab_wtr.mintime
                    )
                ).as_('hours'),
                group_by=[tab_wtm.id],
            )
        qu2 = qu1.select(qu1.id_model,
                (Extract('hours', qu1.hours) + 
                (Extract('minutes', qu1.hours) / 60.0)).as_('hourmin')
            )
        return qu2

    @classmethod
    def get_hours_per_week(cls, wtmodels, names):
        """ get hours per week
        """
        r1 = {'hours_per_week': {}}
        tab_hours = cls.get_hours_per_week_sql()
        cursor = Transaction().connection.cursor()
        id_lst = [x.id for x in wtmodels]
        
        # prepare result
        for i in id_lst:
            r1['hours_per_week'][i] = Decimal('0.0')
        
        qu1 = tab_hours.select(tab_hours.id_model,
                tab_hours.hourmin,
                where=tab_hours.id_model.in_(id_lst)
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        for i in l1:
            (id1, h1) = i
            r1['hours_per_week'][id1] = Decimal(h1).quantize(Decimal('0.1'))

        return r1
        
    @classmethod
    def search_hours_per_week(cls, name, clause):
        """ search in hour/week
        """
        tab_hours = cls.get_hours_per_week_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = tab_hours.select(tab_hours.id_model,
                where=Operator(tab_hours.hourmin, clause[2])
            )
        return [('id', 'in', qu1)]

    @classmethod
    def check_overlap(cls, items):
        """ raises exception if rules overlap
        """
        for i in items:
            for k in i.worktimerule:
                p1 = {'mintime': k.mintime, 'maxtime': k.maxtime, 'mon':k.mon,
                        'tue': k.tue, 'wed': k.wed, 'thu': k.thu, 'fri': k.fri,
                        'sat': k.sat, 'sun': k.sun
                    }
                l2 = cls.get_overlap_items(i, p1, ignore_item=k)
                if len(l2) > 0:
                    t1 = ''
                    for m in l2:
                        t1 += '%s\n' % m.rec_name
                    t1 = t1.strip()
                    cls.raise_user_error('range_overlap', t1)
        
    @classmethod
    def get_overlap_items(cls, wtmodel, to_check={}, ignore_item=None):
        """ get overlapping items
            wtmodel = WorkTimeModel
            to_check = {}
            ignore_item = None or WorkTimeRule()
        """
        WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
        d1 = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        d2 = ['mintime', 'maxtime']

        # import parameter
        daycheck = ['OR']
        par1 = {}
        for i in d1:
            par1[i] = to_check.get(i, False)
            if isinstance(par1[i], type(None)):
                par1[i] = False
            if not isinstance(par1[i], type(True)):
                raise ValueError(u"Parameter '%s' --> Boolean!" % i)
            if par1[i] == True:
                daycheck.append((i, '=', True))
        if len(daycheck) == 1:
            raise ValueError(u"Weekdays: enable min. 1x !")
            
        for i in d2:
            par1[i] = to_check[i]
            if not isinstance(par1[i], type(time(1,2))):
                raise ValueError(u"Parameter '%s' --> Time!" % i)

        if (par1['mintime'] >= par1['maxtime']) and (par1['maxtime'] != time(0, 0)):
            raise ValueError(u"Parameter: mintime < maxtime !")

        qu1 = [
                ('wtmodel', '=', wtmodel),
                ['OR',
                    # starts before, ends within
                    [('mintime', '<=', par1['mintime']), 
                     ('mintime', '<',  par1['maxtime']),
                     ('maxtime', '>',  par1['mintime']), 
                     ('maxtime', '<=', par1['maxtime'])],
                    # starts within, ends after
                    [('mintime', '>=', par1['mintime']), 
                     ('mintime', '<=', par1['maxtime']), 
                     ('maxtime', '>' , par1['mintime']),
                     ('maxtime', '>=', par1['maxtime'])],
                    # starts + ends within
                    [('mintime', '>=', par1['mintime']), 
                     ('mintime', '<=', par1['maxtime']), 
                     ('maxtime', '>=', par1['mintime']),
                     ('maxtime', '<=', par1['maxtime'])],
                    # encloses
                    [('mintime', '<=', par1['mintime']), 
                     ('mintime', '<' , par1['maxtime']),
                     ('maxtime', '>=', par1['maxtime']),
                     ('maxtime', '>',  par1['maxtime'])],
                    # ends at midnight
                    [('maxtime', '=', time(0, 0)), 
                     ('maxtime', '=', par1['maxtime'])],
                    # starts before, ends at midnight
                    [('maxtime', '=', time(0, 0)), 
                     ('mintime', '<=', par1['mintime']),
                     ('mintime', '<' , par1['maxtime'])],
                    # starts after, ends midnight
                    [('maxtime', '=', time(0, 0)),
                     ('mintime', '>=', par1['mintime']),
                     ('mintime', '<', par1['maxtime'])]
                ],
                daycheck
            ]

        # ignore a item
        if not isinstance(ignore_item, type(None)):
            qu1.append(('id', '!=', ignore_item.id))

        return WorkTimeRule.search(qu1)

# end WorkTimeModel


class WorkTimeRule(ModelSQL, ModelView):
    'Work time rule'
    __name__ = 'employee_timetracking.worktimerule'

    wtmodel = fields.Many2One(string=u'Work time model', required=True, select=True,
        model_name='employee_timetracking.worktimemodel', ondelete='CASCADE')
    name = fields.Char(string=u'Name', required=True)
    mon = fields.Boolean(string=u'Mon', help=u'rule applies at Monday')
    tue = fields.Boolean(string=u'Tue', help=u'rule applies at Tuesday')
    wed = fields.Boolean(string=u'Wed', help=u'rule applies at Wednesday')
    thu = fields.Boolean(string=u'Thu', help=u'rule applies at Thursday')
    fri = fields.Boolean(string=u'Fri', help=u'rule applies at Friday')
    sat = fields.Boolean(string=u'Sat', help=u'rule applies at Saturday')
    sun = fields.Boolean(string=u'Sun', help=u'rule applies at Sunday')
    mintime = fields.Time(string=u'from', required=True,
                help=u'Begin time from which the rule applies.')
    maxtime = fields.Time(string=u'to', required=True,
                help=u'End time until which the rule applies.')

    @classmethod
    def __setup__(cls):
        super(WorkTimeRule, cls).__setup__()
        tab_wtitem = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_wtitem, tab_wtitem.name, tab_wtitem.wtmodel), 
            u'This name is already in use.'),
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

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        WorkTimeModel = Pool().get('employee_timetracking.worktimemodel')
        v1 = super(WorkTimeRule, cls).create(vlist)
        
        # check overlap
        wt_id = []
        for i in v1:
            if not i.wtmodel.id in wt_id:
                wt_id.append(i.wtmodel.id)
                WorkTimeModel.check_overlap([i.wtmodel])
        return v1

    @classmethod
    def write(cls, *args):
        """ write item
        """
        WorkTimeModel = Pool().get('employee_timetracking.worktimemodel')
        
        actions = iter(args)
        to_check = []
        for items, values in zip(actions, actions):
            for i in items:
                if not i in to_check:
                    to_check.append(i)
        super(WorkTimeRule, cls).write(*args)

        # check overlap + update local copy of work time model in evaluations
        Evaluation = Pool().get('employee_timetracking.evaluation')
        wt_id = []
        for i in to_check:
            if not i.wtmodel.id in wt_id:
                wt_id.append(i.wtmodel.id)
                WorkTimeModel.check_overlap([i.wtmodel])
                Evaluation.updt_worktime_model([i.wtmodel])

    def get_rec_name(self, name):
        l1 = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        t2 = ''
        for k in l1:
            if getattr(self, k) == True:
                t2 += 'x'
            else :
                t2 += '_'
        t1 = '%s - %s-%s [%s]' % \
            (self.name, self.mintime.strftime('%H:%M'), self.maxtime.strftime('%H:%M'), t2)
        return t1

    @classmethod
    def default_mintime(cls):
        """ default: 8:00
        """
        return time(8, 0, 0)

    @classmethod
    def default_maxtime(cls):
        """ default: 16:00:00
        """
        return time(16, 0, 0)

    @classmethod
    def default_mon(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_tue(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_wed(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_thu(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_fri(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_sat(cls):
        """ default: True
        """
        return False

    @classmethod
    def default_sun(cls):
        """ default: True
        """
        return False

# end WorkTimeRule
