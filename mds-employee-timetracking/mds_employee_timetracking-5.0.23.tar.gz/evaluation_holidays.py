# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


from trytond.model import ModelView, ModelSQL, fields, Check, Unique
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from datetime import date, timedelta
from trytond.pyson import Eval, Id, And, Or
from sqlextension import Overlaps
from .const import WF_EVALUATION_LOCK, WF_EVALUATION_ACTIVE


__all__ = ['EvaluationVacationdays']


# - list of vacation days per evaluation and employee
# - is filled by holiday-calendar of employee
# - can be edited manually
class EvaluationVacationdays(ModelSQL, ModelView):
    'Vacation days of employee while current month'
    __name__ = 'employee_timetracking.evaluation_vacationdays'

    states_ev={
            'readonly':
                ~Or(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    And(
                        Eval('eval_state', '') == WF_EVALUATION_ACTIVE,
                        Id('employee_timetracking', 'group_worktime_edit').\
                            in_(Eval('context', {}).get('groups', [])),
                    ),
                ),
            }

    evaluation = fields.Many2One(string=u'Evaluation', required=True, 
        ondelete='CASCADE', readonly=True, model_name='employee_timetracking.evaluation',
        states=states_ev, depends=['eval_state'], select=True)
    date_start = fields.Date(string='Start Date', required = True,
        states=states_ev, depends=['eval_state'])
    date_end = fields.Date(string='End Date', required = True,
        states=states_ev, depends=['eval_state'])
    halfday = fields.Boolean(string=u'Half Day',
        states=states_ev, depends=['eval_state'])
    autoitem = fields.Boolean(string=u'Automatically', help=u'The entry was created automatically.',
        readonly=True)

    # views
    eval_state = fields.Function(fields.Char(string='State', readonly=True),
        'on_change_with_eval_state')

    @classmethod
    def __setup__(cls):
        super(EvaluationVacationdays, cls).__setup__()
        cls._order.insert(0, ('date_start', 'ASC'))
        tab_vday = cls.__table__()
        cls._sql_constraints.extend([
            ('order_date', 
            Check(tab_vday, tab_vday.date_start <= tab_vday.date_end), 
            u'The end date must be after the start date.'),
            ('uniqu_start',
            Unique(tab_vday, tab_vday.date_start, tab_vday.evaluation),
            u'There is already an entry for this start date.'),
            ('uniqu_end',
            Unique(tab_vday, tab_vday.date_end, tab_vday.evaluation),
            u'There is already an entry for this end date.'),
            ])
        cls._error_messages.update({
            'evholyday_daterange': (u"The beginning and end of the holiday entry must be in the range of '%s' to '%s'."),
            'evholyday_locked': (u"The evaluation '%s' is locked, therefore the entry can not be created or changed."),
            'evholyday_overlap': (u"The item '%s' overlaps with '%s' in the evaluation '%s'."),
            })

    def get_rec_name(self, name):
        t1 = self.date_start.strftime('%Y-%m-%d')
        
        if self.date_start != self.date_end:
            t1 = '%s - %s' % (t1, self.date_end.strftime('%Y-%m-%d'))
        return t1

    @classmethod
    def get_dates_from_optdays(cls, evaluation, daylst):
        """ get list of dates from list of days
            daylst: [True, False, ...] - 
            result: [(date(<start>), date(<end>)), ...]
        """
        res1 = []

        v1 = False
        dt1 = None
        ev_date = evaluation.evaldate
        for i in range(len(daylst)):
            if daylst[i] == True:
                if v1 == False:
                    dt1 = date(ev_date.year, ev_date.month, i + 1)
            else :
                if v1 == True:
                    if isinstance(dt1, type(None)):
                        raise ValueError('invalid date')

                    res1.append((dt1, date(ev_date.year, ev_date.month, i)))
                    dt1 = None

            v1 = daylst[i]

        # close last date
        if v1 == True:
            res1.append((dt1, date(ev_date.year, ev_date.month, i + 1)))
            dt1 = None
        return res1

    @classmethod
    def get_vacation_days_wo_manually(cls, evaluation, daylst):
        """ dont allow autoitems at manually created vacation days
        """
        Vacationdays = Pool().get('employee_timetracking.evaluation_vacationdays')
        man_vd = Vacationdays.search([
                    ('evaluation', '=', evaluation),
                    ('autoitem', '=', False),
                ], order=[('date_start', 'ASC')])
        daylst2 = daylst
        for i in man_vd:
            for k in range(i.date_start.day - 1, i.date_end.day):
                daylst2[k] = False
        return daylst2

    @classmethod
    def get_optimized_vacation_days(cls, evaluation, cal_events):
        """ get list of days in current evaluation
            'cal_events' --> type('pim_calendar.event')
            result: [True, False, ...]
        """
        ev_start = evaluation.datestart
        ev_end = evaluation.dateend
        res1 = []
        
        day_lst = []
        
        # get number of days in month
        dt1 = date(evaluation.evaldate.year, evaluation.evaldate.month, 20) + timedelta(days=15)
        anz_days = (date(dt1.year, dt1.month, 1) - timedelta(days=1)).day
        
        for i in range(anz_days):
            day_lst.append(False)
        
        for i in cal_events:
            # mark days in 'day_lst' with 'True' by event 
            pos1 = 0
            pos2 = 0
            
            # set startpos
            if i.startpos <= ev_start:
                pos1 = 0
            elif (i.startpos > ev_start) and (i.startpos <= ev_end):
                pos1 = i.startpos.day - 1
            else :
                raise ValueError('invalid startpos')

            # set endpos
            if (i.endpos >= ev_start) and (i.endpos <= ev_end):
                pos2 = i.endpos.day - 1
            elif i.endpos > ev_end:
                pos2 = anz_days - 1
            else :
                raise ValueError('invalid endpos')

            if (pos1 >= 0) and (pos1 <= anz_days) and (pos2 >= 0) and (pos2 <= anz_days):
                for k in range(pos1, pos2 + 1):
                    day_lst[k]  = True
            else :
                raise ValueError('start/end-pos not in range')
        return day_lst

    @classmethod
    def updt_days_from_calendar(cls, evaluation):
        """ add/remove vacation days for evaluation from calendar of the employee,
            dont change manually edited items
        """
        pool = Pool()
        VacationDays = pool.get('employee_timetracking.evaluation_vacationdays')
        CalEvent = pool.get('pim_calendar.event')
        
        if evaluation.state == WF_EVALUATION_LOCK:
            cls.raise_user_error('evholyday_locked', (evaluation.rec_name))
        
        if isinstance(evaluation.employee.calendar, type(None)):
            # no calendar connected
            # remove auto-created items
            v_lst = VacationDays.search([('evaluation', '=', evaluation), ('autoitem', '=', True)])
            VacationDays.delete(v_lst)
            return

        # get calendar-items from employee in range of evaluation
        dt_start = evaluation.datestart
        dt_end = evaluation.dateend
        
        c_lst = CalEvent.search([
                ('calendar', '=', evaluation.employee.calendar),
                ['OR',
                    # starts before current month, ends within
                    [('startpos', '<=', dt_start), ('endpos', '>=', dt_start), ('endpos', '<=', dt_end)],
                    # starts + ends in current month
                    [('startpos', '>=', dt_start), ('endpos', '<=', dt_end)],
                    # starts in current month, ends after
                    [('startpos', '>=', dt_start), ('startpos', '<=', dt_end), ('endpos', '>=', dt_end)],
                    # starts before, ends after
                    [('startpos', '<=', dt_start), ('endpos', '>=', dt_end)]
                ],
            ], order=[('startpos', 'ASC')])
        
        # create list of dates to create vacation days
        vd_lst = cls.get_optimized_vacation_days(evaluation, c_lst)
        vd_lst2 = cls.get_vacation_days_wo_manually(evaluation, vd_lst)
        date_lst = cls.get_dates_from_optdays(evaluation, vd_lst2)
        
        # update/create vacation days
        to_keep = []
        for i in date_lst:
            (v_start, v_end) = i
            
            # search for event with same startpos/endpos
            v_lst = VacationDays.search([
                        ('evaluation', '=', evaluation), 
                        ('autoitem', '=', True),
                        ('date_start', '=', v_start),
                        ('date_end', '=', v_end)
                    ])
            if len(v_lst) == 1:
                # found existing item
                to_keep.append(v_lst[0].id)
            elif len(v_lst) == 0:
                # delete items in range of current item
                d_lst = VacationDays.search([
                            ('evaluation', '=', evaluation), 
                            ('autoitem', '=', True),
                            ['OR',
                                # starts before, ends within
                                [('date_start', '<=', v_start), ('date_end', '>=', v_start), ('date_end', '<=', v_end)],
                                # runs within
                                [('date_start', '>=', v_start), ('date_end', '<=', v_end)],
                                # starts within, ends after
                                [('date_start', '>=', v_start), ('date_start', '<=', v_end), ('date_end', '>=', v_end)]
                            ],
                        ])
                if len(d_lst) > 0:
                    VacationDays.delete(d_lst)

                # create new item
                vd1 = VacationDays(evaluation = evaluation,
                            autoitem = True,
                            date_start = v_start,
                            date_end = v_end,
                        )
                vd1.save()
                to_keep.append(vd1.id)
            else :
                raise ValueError('invalid list of vacation days found')

        # delete old vacation days
        del_lst = VacationDays.search([
                        ('evaluation', '=', evaluation), 
                        ('autoitem', '=', True),
                        ('id', 'not in', to_keep)
                    ])
        VacationDays.delete(del_lst)            
        return to_keep

    @fields.depends('evaluation')
    def on_change_with_eval_state(self, name=None):
        """ get state of evaluation
        """
        if isinstance(self.evaluation, type(None)):
            return None
        return self.evaluation.state

    @classmethod
    def default_autoitem(cls):
        """ default: False
        """
        return False

    @classmethod
    def default_halfday(cls):
        """ default: False
        """
        return False

    @classmethod
    def default_date_start(cls):
        """ default: today
        """
        return date.today()

    @classmethod
    def default_date_end(cls):
        """ default: today
        """
        return date.today()
    
    @classmethod
    def get_overlap_days(cls, evaluation, startpos, endpos, ignore_ids=[]):
        """ get overlapping item in selected evaluation
        """
        cursor = Transaction().connection.cursor()
        tab_vdays = cls.__table__()
        
        cond1 = (tab_vdays.evaluation == evaluation.id) & \
                (Overlaps(startpos, endpos, tab_vdays.date_start, tab_vdays.date_end) == True)
        if len(ignore_ids) > 0:
            cond1 = cond1 & (~tab_vdays.id.in_(ignore_ids))

        qu1 = tab_vdays.select(tab_vdays.id,
                where=cond1,
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        return [x[0] for x in l1]
        
    @classmethod
    def create(cls, vlist):
        """ create item
        """
        VacationDays = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        l1 = super(EvaluationVacationdays, cls).create(vlist)
        
        for i in l1:
            if i.evaluation.state == WF_EVALUATION_LOCK:
                cls.raise_user_error('evholyday_locked', (i.evaluation.rec_name))
            
            # overlap
            ls_ovr = cls.get_overlap_days(i.evaluation, i.date_start, i.date_end, ignore_ids=[i.id])
            if len(ls_ovr) > 0:
                cls.raise_user_error('evholyday_overlap', \
                    (i.rec_name, VacationDays(ls_ovr[0]).rec_name, 
                     i.evaluation.rec_name))

            dt_start = i.evaluation.datestart.date()
            dt_end = i.evaluation.dateend.date()

            # check if item in date range of evolution
            if not ((i.date_start >= dt_start) and \
                (i.date_start <= dt_end) and \
                (i.date_end >= dt_start) and \
                (i.date_end <= dt_end)):
                cls.raise_user_error('evholyday_daterange', 
                    (dt_start.strftime('%Y-%m-%d'), 
                     dt_end.strftime('%Y-%m-%d')))
            
            # mark evaluation for recalc
            i.evaluation.needs_recalc = True
            i.evaluation.save()
            
        return l1

    @classmethod
    def write(cls, *args):
        """ write item
        """
        VacationDays = Pool().get('employee_timetracking.evaluation_vacationdays')
        
        updt_evals = []
        actions = iter(args)
        p1 = ['date_start', 'date_end']
        
        for items, values in zip(actions, actions):
            for i in items:
                # deny edit if locked
                if i.evaluation.state == WF_EVALUATION_LOCK:
                    cls.raise_user_error('evholyday_locked', (i.evaluation.rec_name))

                dt_start = values.get('date_start', i.date_start)
                dt_end = values.get('date_end', i.date_end)

                # deny overlap
                ls_ovr = cls.get_overlap_days(i.evaluation, dt_start, dt_end, ignore_ids=[i.id])
                if len(ls_ovr) > 0:
                    t1 = dt_start.strftime('%Y-%m-%d')
                    if dt_start != dt_end:
                        t1 = '%s - %s' % (t1, dt_end)
                    cls.raise_user_error('evholyday_overlap', \
                        (t1, 
                         VacationDays(ls_ovr[0]).rec_name,
                         i.evaluation.rec_name))
                
                # start/end within evaluation
                if (dt_start < i.evaluation.datestart.date()) or \
                    (dt_start > i.evaluation.dateend.date()) or \
                    (dt_end < i.evaluation.datestart.date()) or \
                    (dt_end > i.evaluation.dateend.date()):
                    cls.raise_user_error('evholyday_daterange', 
                        (i.evaluation.datestart.strftime('%Y-%m-%d'), 
                         i.evaluation.dateend.strftime('%Y-%m-%d')))
                
                # mark evaluation for recalc
                i.evaluation.needs_recalc = True
                i.evaluation.save()

        super(EvaluationVacationdays, cls).write(*args)

    @classmethod
    def delete(cls, evalitem):
        """ deny delete if locked
        """
        for i in evalitem:
            if i.evaluation.state == WF_EVALUATION_LOCK:
                cls.raise_user_error('evholyday_locked', i.evaluation.rec_name)

            # mark evaluation for recalc
            i.evaluation.needs_recalc = True
            i.evaluation.save()
            
        return super(EvaluationVacationdays, cls).delete(evalitem)

# end EvaluationVacationdays
