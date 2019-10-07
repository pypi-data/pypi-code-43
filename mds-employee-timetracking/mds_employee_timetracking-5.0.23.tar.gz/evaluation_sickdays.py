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


__all__ = ['EvaluationSickdays']


# - list of sick days per evaluation and employee
# - can be edited manually
class EvaluationSickdays(ModelSQL, ModelView):
    'Sick days of employee while current month'
    __name__ = 'employee_timetracking.evaluation_sickdays'

    states_ev={
            'readonly':
                ~Or(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    Eval('eval_state', '') == WF_EVALUATION_ACTIVE,
                ),
            }

    evaluation = fields.Many2One(string=u'Evaluation', required=True, select=True,
        ondelete='CASCADE', readonly=True, model_name='employee_timetracking.evaluation',
        states=states_ev, depends=['eval_state'])
    date_start = fields.Date(string='Start Date', required = True,
        states=states_ev, depends=['eval_state'])
    date_end = fields.Date(string='End Date', required = True,
        states=states_ev, depends=['eval_state'])

    # views
    eval_state = fields.Function(fields.Char(string='State', readonly=True),
        'on_change_with_eval_state')

    @classmethod
    def __setup__(cls):
        super(EvaluationSickdays, cls).__setup__()
        cls._order.insert(0, ('date_start', 'ASC'))
        tab_sday = cls.__table__()
        cls._sql_constraints.extend([
            ('order_date', 
            Check(tab_sday, tab_sday.date_start <= tab_sday.date_end), 
            u'The end date must be after the start date.'),
            ('uniqu_start',
            Unique(tab_sday, tab_sday.date_start, tab_sday.evaluation),
            u'There is already an entry for this start date.'),
            ('uniqu_end',
            Unique(tab_sday, tab_sday.date_end, tab_sday.evaluation),
            u'There is already an entry for this end date.'),
            ])
        cls._error_messages.update({
            'evsickday_daterange': (u"The beginning and end of the sickday entry must be in the range of '%s' to '%s'."),
            'evsickday_locked': (u"The evaluation '%s' is locked, therefore the entry can not be created or changed."),
            'evsickday_overlap': (u"The item '%s' overlaps with '%s' in the evaluation '%s'."),
            })

    def get_rec_name(self, name):
        t1 = self.date_start.strftime('%Y-%m-%d')
        
        if self.date_start != self.date_end:
            t1 = '%s - %s' % (t1, self.date_end.strftime('%Y-%m-%d'))
        return t1

    @fields.depends('evaluation')
    def on_change_with_eval_state(self, name=None):
        """ get state of evaluation
        """
        if isinstance(self.evaluation, type(None)):
            return None
        return self.evaluation.state

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
        tab_sdays = cls.__table__()
        
        cond1 = (tab_sdays.evaluation == evaluation.id) & \
                (Overlaps(startpos, endpos, tab_sdays.date_start, tab_sdays.date_end) == True)
        if len(ignore_ids) > 0:
            cond1 = cond1 & (~tab_sdays.id.in_(ignore_ids))

        qu1 = tab_sdays.select(tab_sdays.id,
                where=cond1,
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        return [x[0] for x in l1]

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        SickDays = Pool().get('employee_timetracking.evaluation_sickdays')
        
        l1 = super(EvaluationSickdays, cls).create(vlist)
        
        for i in l1:
            if i.evaluation.state == WF_EVALUATION_LOCK:
                cls.raise_user_error('evsickday_locked', (i.evaluation.rec_name))
            
            # overlap
            ls_ovr = cls.get_overlap_days(i.evaluation, i.date_start, i.date_end, ignore_ids=[i.id])
            if len(ls_ovr) > 0:
                cls.raise_user_error('evsickday_overlap', \
                    (i.rec_name, SickDays(ls_ovr[0]).rec_name, 
                     i.evaluation.rec_name))

            dt_start = i.evaluation.datestart.date()
            dt_end = i.evaluation.dateend.date()

            # check if item in date range of evolution
            if not ((i.date_start >= dt_start) and \
                (i.date_start <= dt_end) and \
                (i.date_end >= dt_start) and \
                (i.date_end <= dt_end)):
                cls.raise_user_error('evsickday_daterange', 
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
        SickDays = Pool().get('employee_timetracking.evaluation_sickdays')
        
        updt_evals = []
        actions = iter(args)
        p1 = ['date_start', 'date_end']
        
        for items, values in zip(actions, actions):
            for i in items:
                # deny edit if locked
                if i.evaluation.state == WF_EVALUATION_LOCK:
                    cls.raise_user_error('evsickday_locked', (i.evaluation.rec_name))

                dt_start = values.get('date_start', i.date_start)
                dt_end = values.get('date_end', i.date_end)

                # deny overlap
                ls_ovr = cls.get_overlap_days(i.evaluation, dt_start, dt_end, ignore_ids=[i.id])
                if len(ls_ovr) > 0:
                    t1 = dt_start.strftime('%Y-%m-%d')
                    if dt_start != dt_end:
                        t1 = '%s - %s' % (t1, dt_end)
                    cls.raise_user_error('evsickday_overlap', \
                        (t1, 
                         SickDays(ls_ovr[0]).rec_name,
                         i.evaluation.rec_name))
                
                # start/end within evaluation
                if (dt_start < i.evaluation.datestart.date()) or \
                    (dt_start > i.evaluation.dateend.date()) or \
                    (dt_end < i.evaluation.datestart.date()) or \
                    (dt_end > i.evaluation.dateend.date()):
                    cls.raise_user_error('evsickday_daterange', 
                        (i.evaluation.datestart.strftime('%Y-%m-%d'), 
                         i.evaluation.dateend.strftime('%Y-%m-%d')))
                
                # mark evaluation for recalc
                i.evaluation.needs_recalc = True
                i.evaluation.save()

        super(EvaluationSickdays, cls).write(*args)

    @classmethod
    def delete(cls, evalitem):
        """ deny delete if locked
        """
        for i in evalitem:
            if i.evaluation.state == WF_EVALUATION_LOCK:
                cls.raise_user_error('evsickday_locked', i.evaluation.rec_name)

            # mark evaluation for recalc
            i.evaluation.needs_recalc = True
            i.evaluation.save()

        return super(EvaluationSickdays, cls).delete(evalitem)

# end EvaluationSickdays
