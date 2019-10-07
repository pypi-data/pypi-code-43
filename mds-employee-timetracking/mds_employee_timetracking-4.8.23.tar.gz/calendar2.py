# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# extend the model 'pim_calendar'
# add checkbox 'all-day-events only' to pim_calendar.calendar

from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from datetime import date

__all__ = ['Event', 'Calendar']


class Event(ModelSQL, ModelView):
    'Event'
    __name__ = 'pim_calendar.event'

    @classmethod
    def __setup__(cls):
        super(Event, cls).__setup__()
        cls._error_messages.update({
            'event_holydaycal': (u"In calendar '%s' only all-day events are allowed."),
            })

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        l1 = super(Event, cls).create(vlist)
        id_cal = {}
        for i in l1:
            if (i.calendar.allday_events == True) and \
                (i.wholeday == False):
                cls.raise_user_error('event_holydaycal', (i.calendar.rec_name))

            id_cal = cls.add_to_calendar_mark(id_cal, i.calendar, i)

        Calendar.mark_evaluation_recalc(id_cal)
        return l1

    @classmethod
    def write(cls, *args):
        """ write item
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        actions = iter(args)
        id_cal = {}
        for items, values in zip(actions, actions):
            for i in items:

                id_cal = cls.add_to_calendar_mark(id_cal, i.calendar, i)
                
                wh_day = values.get('wholeday', i.wholeday)
                cal1 = values.get('calendar', i.calendar)
                if isinstance(cal1, type(1)):
                    cal1 = Calendar(cal1)

                id_cal = cls.add_to_calendar_mark(id_cal, cal1, i)

                if (wh_day == False) and (cal1.allday_events == True):
                    cls.raise_user_error('event_holydaycal', (cal1.rec_name))
        
        Calendar.mark_evaluation_recalc(id_cal)
        super(Event, cls).write(*args)

    @classmethod
    def delete(cls, events):
        """ mark calendar for recalc
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        id_cal = {}
        for i in events:
            id_cal = cls.add_to_calendar_mark(id_cal, i.calendar, i)

        Calendar.mark_evaluation_recalc(id_cal)
        return super(Event, cls).delete(events)

    @classmethod
    def add_to_calendar_mark(cls, todo_lst, calendar, event):
        """ update list to mark evaluations for recalc
        """
        if calendar.is_holidaycal == False:
            return todo_lst

        if not calendar.id in todo_lst.keys():
            todo_lst[calendar.id] = []
        
        dt1 = (event.startpos.date(), event.endpos.date())

        if not dt1 in todo_lst[calendar.id]:
            todo_lst[calendar.id].append(dt1)
            
        return todo_lst
# end Event


class Calendar(ModelSQL, ModelView):
    'Calendar'
    __name__ = 'pim_calendar.calendar'

    allday_events = fields.Boolean(string=u'All-Day-Events only', 
        help=u'Allows only full-day appointments in this calendar',
        states={
            'readonly': Eval('is_holidaycal', False) == True,
        }, depends=['is_holidaycal'])
    is_holidaycal = fields.Function(fields.Boolean(string=u'Holiday Calendar', readonly=True,
        help=u'This calendar is used as a holiday calendar.'), 
        'on_change_with_is_holidaycal', searcher='search_is_holidaycal')
    
    @classmethod
    def __setup__(cls):
        super(Calendar, cls).__setup__()
        cls._error_messages.update({
                'calwrt_disena_allday': (u"Disabling the all-day option is not allowed as long as the calendar is connected to an employee."),
            })

    @classmethod
    def search_is_holidaycal(cls, name, clause):
        """ search in 'is_holidaycal'
        """
        Employee = Pool().get('company.employee')

        c_lst = Employee.search([('calendar', '!=', None)])

        clause = list(clause)
        if (['=', True] == clause[1:]) or (['!=', False] == clause[1:]):
            return [('id', 'in', [x.calendar.id for x in c_lst])]
        elif (['=', False] == clause[1:]) or (['!=', True] == clause[1:]):
            return [('id', 'not in', [x.calendar.id for x in c_lst])]
        else :
            raise ValueError('invalid query')

    @fields.depends('id')
    def on_change_with_is_holidaycal(self, name=None):
        """ get True if calendar is holiday-calendar
        """
        Employee = Pool().get('company.employee')
        
        if isinstance(self.id, type(None)):
            return None

        # search for employee using this calendar
        c_lst = Employee.search([('calendar.id', '=', self.id)])
        if len(c_lst) == 1:
            return True
        else :
            return False

    @classmethod
    def mark_evaluation_recalc(cls, todo_lst):
        """ mark evaliation of employees for recalc
            todo_lst: {<calendar-id>: [(<from>, <to>), ..], ...}
        """
        Evaluation = Pool().get('employee_timetracking.evaluation')
        tab_eval = Evaluation.__table__()
        cursor = Transaction().connection.cursor()
        
        for i in todo_lst.keys():
            dt_lst = []
            # create list of dates of corresponding evaluations
            for k in todo_lst[i]:
                (dt1, dt2) = k
                dt1a = date(dt1.year, dt1.month, 1)
                dt2a = date(dt2.year, dt2.month, 1)
                if not dt1a in dt_lst:
                    dt_lst.append(dt1a)
                if not dt2a in dt_lst:
                    dt_lst.append(dt2a)

            # search for matching evaluation
            e_lst = Evaluation.search([
                        ('employee.calendar.id', '=', i),
                        ('evaldate', 'in', dt_lst)
                    ])
            # we need to bypass user-permissions here
            if len(e_lst) > 0:
                qu1 = tab_eval.update(
                        columns=[tab_eval.needs_recalc],
                        values=[True],
                        where=tab_eval.id.in_([x.id for x in e_lst])
                    )
                cursor.execute(*qu1)
        
    @classmethod
    def default_allday_events(cls):
        """ default: False
        """
        return False

    @classmethod
    def write(cls, *args):
        """ write item
        """
        Employee = Pool().get('company.employee')
        
        actions = iter(args)
        for items, values in zip(actions, actions):
            if 'allday_events' in values.keys():
                if values['allday_events'] == False:
                    # deny write if calendar is connected to a employee
                    c_lst = Employee.search([('calendar.id', 'in', [x.id for x in items])])
                    if len(c_lst) > 0:
                        cls.raise_user_error('calwrt_disena_allday')
        super(Calendar, cls).write(*args)

# end Calendar
