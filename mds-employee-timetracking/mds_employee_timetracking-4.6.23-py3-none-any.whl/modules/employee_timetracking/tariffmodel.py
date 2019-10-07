# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


# tariffmodel
# The tariff model is a combination of accountrule rule, break time rule and presence type.


from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id, And
from trytond.transaction import Transaction
from trytond import backend
import logging

logger = logging.getLogger(__name__)


__all__ = ['TariffModel', 'PresenceRel']
__metaclass__ = PoolMeta


class TariffModel(ModelSQL, ModelView):
    'Tariff model'
    __name__ = 'employee_timetracking.tariffmodel'

    name = fields.Char(string=u'Name', required=True)
    shortname = fields.Char(string=u'shorthand symbol', required=True, size=4,
                    help=u'The shorthand symbol appears in the tables of the reports.')
    company = fields.Many2One(string=u'Company', model_name='company.company',
        states={
            'readonly': 
                ~And(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    Eval('id', -1) == -1
                ),
        }, required=True, select=True)
    accountrule = fields.One2Many(model_name='employee_timetracking.accountrule',
                    field='tariff', string=u'Account rule')
    breaktime = fields.One2Many(model_name='employee_timetracking.breaktime',
                    field='tariff', string=u'Break time rule')
    presence = fields.Many2Many(relation_name='employee_timetracking.presence_rel',
                origin='tariff', target='presence', string=u'Type of presence',
                depends=['company'], domain=[('company', '=', Eval('company'))])
    timeaccounts = fields.Function(fields.One2Many(string=u'Allowed time accounts', 
                model_name='employee_timetracking.timeaccount', 
                field=None, readonly=True, depends=['company']),
                'on_change_with_timeaccounts')
    main_timeaccount = fields.Many2One(string=u'Main time account', 
                model_name='employee_timetracking.timeaccount',
                domain=[('id', 'in', Eval('timeaccounts', []))], 
                depends=['company', 'timeaccounts'], 
                help=u'Time account for monthly worktime')
    type_present = fields.Many2One(string=u'Primary presence type', 
                model_name='employee_timetracking.presence',
                domain=[('id', 'in', Eval('presence', []))], 
                depends=['presence'],
                help=u"Presence type as default for the absent user", 
                ondelete='SET NULL')
    employees = fields.Function(fields.One2Many(model_name='company.employee', field=None,
        readonly=True, string=u'Used by Employees'), 'on_change_with_employees')

    @classmethod
    def __register__(cls, module_name):
        super(TariffModel, cls).__register__(module_name)
        cls.migrate_columns(module_name)

    @classmethod
    def migrate_columns(cls, modul_name):
        """ x.x.9: - dropy column 'type_sitework'
        """
        TableHandler = backend.get('TableHandler')
        table = TableHandler(cls, modul_name)

        # drop column type_sitework
        if table.column_exist('type_sitework'):
            table.drop_column('type_sitework')
            logger.warning('deleted column "type_sitework" from table "tariffmodel"')

    @classmethod
    def __setup__(cls):
        super(TariffModel, cls).__setup__()
        tab_tariff = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_tariff, tab_tariff.name, tab_tariff.company), 
            u'This name is already in use.'),
            ('uniq_short', 
            Unique(tab_tariff, tab_tariff.shortname, tab_tariff.company), 
            u'This shorthand symbol is already in use.'),
            ])

    @classmethod
    def default_company(cls):
        """ set active company to default
        """
        context = Transaction().context
        return context.get('company')

    @classmethod
    def get_reduced_worktime(cls, tariff, worktime, breaktime, domain=[]):
        """ gets reduced worktime with applied breaktimes of actual
            tariff
        """
        BreakTime = Pool().get('employee_timetracking.breaktime')
        domain2 = []
        domain2.extend(domain)
        domain2.extend([
                ('id', 'in', [x.id for x in tariff.breaktime]),
            ])
        (wtime, btime) = BreakTime.get_reduced_worktime(tariff, worktime, breaktime, domain2)
        return wtime

    @fields.depends('company')
    def on_change_with_timeaccounts(self, name=None):
        """ get list of pssible time-accounts
        """
        if isinstance(self.company, type(None)):
            return []
        
        TimeAccount = Pool().get('employee_timetracking.timeaccount')
        ta_lst = TimeAccount.search([('company', '=', self.company)])
        return [x.id for x in ta_lst]

    @fields.depends('id')
    def on_change_with_employees(self, name=None):
        """ get employees which use this presence-type
        """
        Employee = Pool().get('company.employee')
        
        l1 = Employee.search([('tariff', '=', self.id)])
        return [x.id for x in l1]

    @classmethod
    def write(cls, *args):
        """ write item
        """
        actions = iter(args)
        for items, values in zip(actions, actions):
            if 'breaktime' in values.keys():
                for i in values['breaktime']:
                    if ('add' == i[0]) and (len(i[1]) > 1):
                        # check breaktime items to be added
                        BreakTime = Pool().get('employee_timetracking.breaktime')
                        for k in i[1]:
                            br1 = BreakTime(k)
                            l1 = BreakTime.check_overlap(
                                    [BreakTime(x) for x in i[1]],
                                    br1.mintime, br1.maxtime, br1)
                            if len(l1) > 0:
                                brobj = BreakTime(l1[0])
                                t1 = u"'%s (%s)'" % (brobj.name, brobj.shortname)
                                BreakTime.raise_user_error('range_overlap', (t1))
        super(TariffModel, cls).write(*args)

        Evaluation = Pool().get('employee_timetracking.evaluation')
        (items, para) = args
        Evaluation.updt_tariff_model(items)

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('company'):
                values['company'] = cls.default_company()
        return super(TariffModel, cls).create(vlist)

# end TariffModel


class PresenceRel(ModelSQL):
    'presence - tariffmodel'
    __name__ = 'employee_timetracking.presence_rel'
    
    tariff = fields.Many2One(model_name='employee_timetracking.tariffmodel', 
                string=u'Tariff model', ondelete='CASCADE',
                required=True, select=True)
    presence = fields.Many2One(model_name='employee_timetracking.presence', 
                string=u'Presence', ondelete='RESTRICT', 
                required=True, select=True)

    @classmethod
    def __setup__(cls):
        super(PresenceRel, cls).__setup__()
        tab_prerel = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_rel', 
            Unique(tab_prerel, tab_prerel.tariff, tab_prerel.presence), 
            u'This type of presence is already in use in the current tariff model.'),
            ])

# ende PresenceRel
