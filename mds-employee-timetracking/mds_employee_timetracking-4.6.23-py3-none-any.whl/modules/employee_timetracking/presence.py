# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


# presence-type
# Defines which presence types exist for the employee.
# Presence types are used to determine what kind of recorded presence is, 
# e.g. 8h work, 3h duty outside the house, 2 days sick, etc.


from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id
from trytond.transaction import Transaction
from sql.aggregate import Count


__all__ = ['PresenceType']
__metaclass__ = PoolMeta


class PresenceType(ModelSQL, ModelView):
    'Type of presence'
    __name__ = 'employee_timetracking.presence'
    
    name = fields.Char(string=u'Name', required=True)
    shortname = fields.Char(string=u'shorthand symbol', required=True, size=4,
        help=u'The shorthand symbol appears in the tables of the reports.')
    company = fields.Many2One(string=u'Company', model_name='company.company',
        states={
            'readonly': ~Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
        }, required=True, select=True)
    color = fields.Many2One(string=u'Text color', ondelete='SET NULL',
        help=u'Text color in the calendar view', 
        model_name="employee_timetracking.colors")

    # views
    employees = fields.Function(fields.One2Many(model_name='company.employee', field=None,
        readonly=True, string=u'Used by Employees'), 'get_employees')
    numemployees = fields.Function(fields.Integer(readonly=True, string=u'Employees',
        help=u'Used by Employees'), 'get_numemployees')

    @classmethod
    def __setup__(cls):
        super(PresenceType, cls).__setup__()
        tab_pres = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_pres, tab_pres.name, tab_pres.company), 
            u'This name is already in use.'),
            ('uniq_short', 
            Unique(tab_pres, tab_pres.shortname, tab_pres.company), 
            u'This shorthand symbol is already in use.'),
            ])

    @classmethod
    def default_color(cls):
        """ get 'Black'
        """
        pool = Pool()
        Colors = pool.get('employee_timetracking.colors')
        ModelData = pool.get('ir.model.data')
        
        try :
            col1 = Colors(ModelData.get_id('employee_timetracking', 'col_black'))
        except :
            return None
        return col1.id

    @classmethod
    def default_company(cls):
        """ set active company to default
        """
        context = Transaction().context
        return context.get('company')
    
    @classmethod
    def get_employees_sql(cls):
        """ get sql code for employees
        """
        Period = Pool().get('employee_timetracking.period')
        tab_per = Period.__table__()
        
        qu1 = tab_per.select(tab_per.employee.as_('id_empl'),
                tab_per.presence.as_('id_pres')
            )
        return qu1
    
    @classmethod
    def get_numemployees(cls, presences, names):
        """ get number of employees
        """
        Period = Pool().get('employee_timetracking.period')
        tab_per = Period.__table__()
        tab_per2 = Period.__table__()

        cursor = Transaction().connection.cursor()
        id_lst = [x.id for x in presences]
        res1 = {'numemployees': {}}
        for i in id_lst:
            res1['numemployees'][i] = 0

        tab_qu1 = tab_per.select(tab_per.employee,
                tab_per.presence,
                group_by=[tab_per.employee, tab_per.presence]
            )
        qu1 = tab_qu1.select(tab_qu1.presence.as_('id_pres'),
                Count(tab_qu1.employee).as_('num_empl'),
                group_by=[tab_qu1.presence],
                where=tab_qu1.presence.in_(id_lst)
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        
        for k in l1:
            (id1, num1) = k
            res1['numemployees'][id1] = num1

        res2 = {}
        for i in names:
            res2[i] = res1[i]
        return res2
        
    @classmethod
    def get_employees(cls, presences, names):
        """ get employees which use this presence-type
        """
        tab_pres = cls.get_employees_sql()
        cursor = Transaction().connection.cursor()
        id_lst = [x.id for x in presences]
        res1 = {'employees': {}}
        
        for i in id_lst:
            qu1 = tab_pres.select(tab_pres.id_empl,
                    where=(tab_pres.id_pres == i)
                )
            cursor.execute(*qu1)
            l1 = cursor.fetchall()
            l2 = []
            for k in l1:
                (id1, ) = k
                l2.append(id1)
            res1['employees'][i] = l2
        
        res2 = {}
        for i in names:
            res2[i] = res1[i]
        return res2

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('company'):
                values['company'] = cls.default_company()
        return super(PresenceType, cls).create(vlist)

# ende PresenceType
