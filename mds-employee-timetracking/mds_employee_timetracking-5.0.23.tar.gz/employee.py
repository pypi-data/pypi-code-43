# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, Check, Unique
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

# extends the company.employee by fields for tariff, worktime etc.

__all__ = ['Employee']
__metaclass__ = PoolMeta


class Employee(ModelSQL, ModelView):
    'Employee'
    __name__ = 'company.employee'

    tariff = fields.Many2One(model_name='employee_timetracking.tariffmodel', 
                string=u'Tariff model', ondelete='RESTRICT', depends=['company'],
                select=True, domain=[('company', '=', Eval('company'))])
    worktime = fields.Many2One(model_name='employee_timetracking.worktimemodel', 
                string=u'Working time model', ondelete='RESTRICT', depends=['company'],
                select=True, domain=[('company', '=', Eval('company'))])
    holidays = fields.Integer(string=u'Holidays', required=True, 
                help=u'Number of holidays per year')
    specleave = fields.Integer(string=u'Special leave', required=True, 
                help=u'Number of special leave days per year')
    color = fields.Many2One(string=u'Background color', ondelete='SET NULL',
                help=u'Background color in the calendar view', 
                model_name="employee_timetracking.colors")
    calendar = fields.Many2One(string=u'Holiday Calendar', ondelete='SET NULL',
                model_name='pim_calendar.calendar', depends=['trytonuser'],
                domain=[
                    ('allday_events', '=', True), 
                    ('owner', '=', Eval('trytonuser')),
                    ])

    # views
    trytonuser = fields.Function(fields.Many2One(string=u'User', model_name='res.user',
                readonly=True), 'on_change_with_trytonuser', searcher='search_trytonuser')

    @classmethod
    def __setup__(cls):
        super(Employee, cls).__setup__()
        tab_empl = cls.__table__()
        cls._sql_constraints.extend([
            ('holidays_not_neg', 
            Check(tab_empl, tab_empl.holidays >= 0), 
            u"'Holidays' must be positive"),
            ('specleave_not_neg', 
            Check(tab_empl, tab_empl.specleave >= 0), 
            u"'Special leave' must be positive"),
            ('calendar_uniq',
            Unique(tab_empl, tab_empl.calendar),
            u"This calendar is already used by another user."),
            ])
        cls._error_messages.update({
                'emplwrt_delcal': (u"Deleting calendar from employee is not allowed."),
            })

    @fields.depends('id')
    def on_change_with_trytonuser(self, name=None):
        """ get connected tryton user
        """
        User = Pool().get('res.user')

        if isinstance(self, type(None)):
            return None

        tr_usr = User.search([('employee.id', '=', self.id)])
        if len(tr_usr) == 1:
            return tr_usr[0].id
        else :
            return None
    
    @classmethod
    def search_trytonuser(cls, name, clause):
        """ search in trytonuser
        """
        User = Pool().get('res.user')
        
        cl1 = clause[0]
        if cl1.startswith('trytonuser.'):
            cl1 = cl1[len('trytonuser.'):]
        usr_lst = User.search([(cl1,) + tuple(clause[1:]), ('employee', '!=', None)])
        return [('id', 'in', [x.employee.id for x in usr_lst])]
        
    @classmethod
    def default_color(cls):
        """ get 'Aero'
        """
        pool = Pool()
        Colors = pool.get('employee_timetracking.colors')
        ModelData = pool.get('ir.model.data')
        
        try :
            col1 = Colors(ModelData.get_id('employee_timetracking', 'col_aero'))
        except :
            return None
        return col1.id

    @classmethod
    def default_holidays(cls):
        """ default: 0
        """
        return 0
        
    @classmethod
    def default_specleave(cls):
        """ default: 0
        """
        return 0

    @classmethod
    def write(cls, *args):
        """ write item
        """
        actions = iter(args)
        to_check1 = []
        to_check2 = []
        for items, values in zip(actions, actions):
            if 'worktime' in values.keys():
                to_check1.append(values['worktime'])
            if 'tariff' in values.keys():
                to_check2.append(values['tariff'])
            if 'calendar' in values.keys():
                if isinstance(values['calendar'], type(None)):
                    cls.raise_user_error('emplwrt_delcal')
        super(Employee, cls).write(*args)

        # update local work time models
        Evaluation = Pool().get('employee_timetracking.evaluation')
        Evaluation.updt_worktime_model(to_check1)
        Evaluation.updt_tariff_model(to_check2)
        
# end Employee
