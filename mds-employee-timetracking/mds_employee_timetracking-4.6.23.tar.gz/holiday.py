# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id
from trytond.transaction import Transaction
from sql.functions import Extract
from sql.conditionals import Case

# Holiday: list of days, national or church holidays,
# can repeat at same date every year, 
# will reduce the planned working time at this day to a half or zero 

__all__ = ['Holiday']
__metaclass__ = PoolMeta


class Holiday(ModelSQL, ModelView):
    'Holiday'
    __name__ = 'employee_timetracking.holiday'

    name = fields.Char(string=u'Name', required=True)
    date = fields.Date(string=u'Date', required=True, select=True)
    repyear = fields.Boolean(string='every year', select=True)
    halfday = fields.Boolean(string='half day', 
        help=u'working hours will be reduced by half this day')
    company = fields.Many2One(string=u'Company', model_name='company.company',
        states={
            'readonly': ~Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
        }, required=True, select=True)

    @classmethod
    def __setup__(cls):
        super(Holiday, cls).__setup__()
        cls._order.insert(0, ('name', 'ASC'))
        tab_hd = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_hd, tab_hd.name, tab_hd.company), 
            u'This name is already in use.'),
            ('uniq_date', 
            Unique(tab_hd, tab_hd.date, tab_hd.company), 
            u'This date is already in use.'),
        ])

    @classmethod
    def default_halfday(cls):
        """ default: halfday --> False
        """
        return False

    @classmethod
    def default_repyear(cls):
        """ repeat every year
        """
        return False

    @classmethod
    def default_company(cls):
        """ set active company to default
        """
        context = Transaction().context
        return context.get('company')

    @classmethod
    def is_weekend(cls, date2check):
        """ returns True is 'date2check' is sat/sun
        """
        if date2check.isoweekday() in [6, 7]:
            return True
        else :
            return False

    @classmethod
    def is_holiday(cls, date2check, company):
        """ returns True if 'date2check' is holiday
        """
        tab_hd = cls.__table__()
        cursor = Transaction().connection.cursor()

        qu1 = tab_hd.select(tab_hd.id,
                tab_hd.halfday,
                tab_hd.repyear,
                where=(tab_hd.repyear == False) & (tab_hd.date == date2check) & (tab_hd.company == company.id) |\
                    (tab_hd.repyear == True) & (Extract('month', tab_hd.date) == date2check.month) & \
                    (Extract('day', tab_hd.date) == date2check.day) & (tab_hd.company == company.id)
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        if len(l1) == 1:
            return True
        else :
            return False

# end Holiday
