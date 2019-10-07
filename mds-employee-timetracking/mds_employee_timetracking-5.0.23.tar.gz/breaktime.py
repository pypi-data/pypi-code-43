# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# The pause regulation determines the working time for which a  
# break time is deducted from the daily working time.


from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id
from trytond.transaction import Transaction
from trytond import backend
from datetime import timedelta
from sqlextension import Overlaps
from .tools import fmttimedelta

__all__ = ['BreakTime']
__metaclass__ = PoolMeta



class BreakTime(ModelSQL, ModelView):
    'Rule of break time'
    __name__ = 'employee_timetracking.breaktime'
    
    tariff = fields.Many2One(string=u'Tariff model', required=True, select=True,
        model_name='employee_timetracking.tariffmodel', ondelete='CASCADE')
    name = fields.Char(string=u'Name', required=True)
    shortname = fields.Char(string=u'shorthand symbol', required=True, size=4,
                help=u'The shorthand symbol appears in the tables of the reports.')
    mintime = fields.TimeDelta(string=u'from', required=True,
                help=u'Minimum working time per day from which the rule applies. (e.g. 4h30m --> 04:30)')
    maxtime = fields.TimeDelta(string=u'to', required=True,
                help=u'Maximum working time per day until which the rule applies. (e.g. 6h --> 06:00)')
    deduction = fields.TimeDelta(string=u'Deduction time', required=True, 
                help=u'Number of hours/minutes to be deducted (e.g. 30m --> 00:30)')

    @classmethod
    def __setup__(cls):
        super(BreakTime, cls).__setup__()
        tab_breaktime = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_breaktime, tab_breaktime.name, tab_breaktime.tariff), 
            u'This name is already in use.'),
            ('uniq_short', 
            Unique(tab_breaktime, tab_breaktime.shortname, tab_breaktime.tariff), 
            u'This shorthand symbol is already in use.'),
            ('uniq_mintime', 
            Unique(tab_breaktime, tab_breaktime.mintime, tab_breaktime.tariff), 
            u"This 'from' time is already in use."),
            ('uniq_maxtime', 
            Unique(tab_breaktime, tab_breaktime.maxtime, tab_breaktime.tariff), 
            u"This 'to' time is already in use."),
            ('no_negtime2', 
            Check(tab_breaktime, (tab_breaktime.mintime >= '00:00:00') & (tab_breaktime.maxtime > '00:00:00')), 
            u'Time must be positive.'),
            ('order', 
            Check(tab_breaktime, tab_breaktime.mintime < tab_breaktime.maxtime), 
            u"'to' must be creater than 'from'"),
            ('no_negdeduction2', 
            Check(tab_breaktime, tab_breaktime.deduction > '00:00:00'), 
            u'Deduction values must be positive.'),
            ])
        cls._error_messages.update({
                'range_overlap': (u"The from/to time range overlaps with the following rules: %s"),
            })

    @classmethod
    def __register__(cls, module_name):
        super(BreakTime, cls).__register__(module_name)
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
    def default_mintime(cls):
        """ default: 4 h
        """
        return timedelta(seconds=60 * 60 * 4)

    @classmethod
    def default_maxtime(cls):
        """ default: 6 h
        """
        return timedelta(seconds=60 * 60 * 6)

    @classmethod
    def default_deduction(cls):
        """ default: 0 h 30 min
        """
        return timedelta(seconds=60 * 30)

    @classmethod
    def get_reduced_worktime2(cls, dbmodel, domain, sumworktime, sumbreaktime):
        """ calculates the reduced working hours based on the rules
            dbmodel: BreakTime|EvaluationBreakTime,
            domain: to select valid breaktime-items,
            tariff: employee_timetracking.tariffmodel,
            sumworktime: timedelta, sum of all work times per day
            sumbreaktime: timedelta, sum of all break times per day
        """
        if not isinstance(sumworktime, type(timedelta(days=1))):
            raise ValueError(u'sumworktime != type(timedelta)')
        if not isinstance(sumbreaktime, type(timedelta(days=1))):
            raise ValueError(u'sumbreaktime != type(timedelta)')

        # select all breaktime-rules, order by mintime
        rl1 = dbmodel.search(domain, order=[('mintime', 'ASC')])
        fnd1 = False
        worktime_ori = sumworktime
        sumworktime -= sumbreaktime
        if len(rl1) > 0:
            # walk through list, find match
            last_itm = None
            for i in rl1:
                if (i.mintime <= worktime_ori <= i.maxtime):
                    fnd1 = True
                    
                    # the employee has entered his break times
                    # if this sum is below the minimum break time by tariff
                    # add more break time
                    if sumbreaktime < i.deduction:
                        bt_add = i.deduction - sumbreaktime
                    
                        # dont reduce working time below mintime
                        if (sumworktime - bt_add) < i.mintime:
                            if isinstance(last_itm, type(None)):
                                sumworktime = i.mintime
                            else :
                                beg1 = i.mintime - last_itm.deduction
                                sumworktime -= i.deduction
                                if sumworktime < beg1:
                                    sumworktime = beg1
                        else :
                            sumworktime -= bt_add
                    break
                last_itm = i

        if fnd1 == False:
            # no match, select item with maxtime below worktime, use highest
            dom2 = []
            dom2.extend(domain)
            dom2.extend(
                    [
                        ('maxtime', '<=', worktime_ori)
                    ], 
                )
            rl1 = dbmodel.search(dom2, order=[('maxtime', 'DESC')], limit=1)
            if len(rl1) == 1:
                if sumbreaktime < rl1[0].deduction:
                    bt_add = rl1[0].deduction - sumbreaktime

                    if ((sumworktime - bt_add) < rl1[0].mintime) and (sumworktime > rl1[0].mintime):
                        sumworktime = rl1[0].mintime
                    else :
                        sumworktime -= bt_add

        # (<reduced working time>, <used break time>)
        return (sumworktime, worktime_ori - sumworktime)
        
    @classmethod
    def get_reduced_worktime(cls, tariff, sumworktime, sumbreaktime, domain=[]):
        """ calculates the reduced working hours based on the rules
            tariff: employee_timetracking.tariffmodel,
            sumworktime: timedelta,
            sumbreaktime: timedelta,
            domain: for more detailed selection
        """
        if not isinstance(sumworktime, type(timedelta(days=1))):
            raise ValueError(u'sumworktime != type(timedelta)')
        if not isinstance(sumbreaktime, type(timedelta(days=1))):
            raise ValueError(u'sumbreaktime != type(timedelta)')

        dom2 = []
        dom2.extend(domain)
        dom2.extend(
                [
                    ('tariff', '=', tariff),
                ], 
            )

        (wtime, btime) = cls.get_reduced_worktime2(
                cls, dom2, sumworktime, sumbreaktime
            )
        # (<reduced working time>, <used break time>)
        return (wtime, btime)

    @classmethod
    def check_overlap(cls, breaktimes, mintime, maxtime, ignore_breaktime=None):
        """ test for overlapping breaktimes in 'tariff'
            breaktimes = list of breaktime objects to check
            mintime/maxtime = range to check
            ignore_breaktime = ignore item if not None
            returns list of breaktime ids
        """
        if not isinstance(mintime, type(timedelta(days=1))):
            raise ValueError('mintime != type(timedelta)!')
        if not isinstance(maxtime, type(timedelta(days=1))):
            raise ValueError('maxtime != type(timedelta)!')

        qu1 = [
                ('id', 'in', [x.id for x in breaktimes]),
                ['OR',
                    [
                        ('mintime', '>=', mintime),
                        ('mintime', '<=', maxtime),
                    ],
                    [
                        ('maxtime', '>=', mintime),
                        ('maxtime', '<=', maxtime),
                    ],
                ]
            ]
        if not isinstance(ignore_breaktime, type(None)):
            qu1.extend([
                    ('id', '!=', ignore_breaktime.id)
                ])
        br_lst = cls.search(qu1)
        return [x.id for x in br_lst]

    @classmethod
    def check_minmax_range(cls, tariff, mintime, maxtime, breaktime=None):
        """ check valid usage of time ranges
            new mintime - from time (timedelta)
            new maxtime - to time (timedelta)
            dsid - if change existing data - id, if new data - None
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        l1 = cls.check_overlap(tariff.breaktime, mintime, maxtime, breaktime)

        if len(l1) > 0:
            t1 = ''
            for i in l1:
                brobj = BreakTime(i)
                t1 += u"'%s (%s)', " % (brobj.name, brobj.shortname)
            t1 = t1.strip()[:-1]
            cls.raise_user_error('range_overlap', (t1))

    def get_rec_name(self, name):
        t1 = '[%s] %s: %s-%s -> %s' % \
            (self.tariff.rec_name, 
            self.shortname, 
            fmttimedelta(self.mintime, noplussign=True),
            fmttimedelta(self.maxtime, noplussign=True),
            fmttimedelta(self.deduction, noplussign=True, sepbyh=True))
        return t1

    @classmethod
    def write(cls, *args):
        """ write item
        """
        actions = iter(args)
        tar_list = []
        for items, values in zip(actions, actions):
            if 'mintime' in values.keys():
                # move seconds to 0
                values['mintime'] = timedelta(seconds=values['mintime'].seconds - values['mintime'].seconds % 60)

            if 'maxtime' in values.keys():
                # move seconds to 59
                values['maxtime'] = timedelta(seconds=values['maxtime'].seconds - values['maxtime'].seconds % 60 + 59)
            
            # check overlap in tariff
            if ('maxtime' in values.keys()) or ('mintime' in values.keys()):
                for i in items:
                    if not i.tariff in tar_list:
                        tar_list.append(i.tariff)
                        
                    max1 = values.get('maxtime', i.maxtime)
                    min1 = values.get('mintime', i.mintime)
                    if (not isinstance(max1, type(None))) and \
                       (not isinstance(min1, type(None))):
                            cls.check_minmax_range(i.tariff, min1, max1, breaktime=i)
        super(BreakTime, cls).write(*args)

        if len(tar_list) > 0:
            Evaluation = Pool().get('employee_timetracking.evaluation')
            Evaluation.updt_tariff_model(tar_list)

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:

            if 'mintime' in values.keys():
                # move seconds to 0
                values['mintime'] = timedelta(seconds=values['mintime'].seconds - values['mintime'].seconds % 60)

            if 'maxtime' in values.keys():
                # move seconds to 59
                values['maxtime'] = timedelta(seconds=values['maxtime'].seconds - values['maxtime'].seconds % 60 + 59)

            # check overlap in tariff
            TariffModel = Pool().get('employee_timetracking.tariffmodel')
            tar1 = TariffModel(values['tariff'])
            if ('maxtime' in values.keys()) or ('mintime' in values.keys()):
                max1 = values.get('maxtime', cls.default_maxtime())
                min1 = values.get('mintime', cls.default_mintime())
                if (not isinstance(max1, type(None))) and \
                   (not isinstance(min1, type(None))):
                        cls.check_minmax_range(tar1, min1, max1)

        return super(BreakTime, cls).create(vlist)

# BreakTime
