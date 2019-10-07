# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# config wizard: starts the configuration of tariff model and
# work time model after module install

from trytond.model import ModelView
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateView, Button, StateTransition


__all__ = ['TimetrackingConfigStart', 'TimetrackingConfig']


class TimetrackingConfigStart(ModelView):
    'Tariff model Config'
    __name__ = 'employee_timetracking.tariffmodel.config.start'

# end TimetrackingConfigStart


class TimetrackingConfig(Wizard):
    'Configure Tariff Model'
    __name__ = 'employee_timetracking.tariffmodel.config'
    
    start = StateView('employee_timetracking.tariffmodel.config.start',
        'employee_timetracking.tariffmodel_config_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'timeaccount', 'tryton-ok', True),
            ])
    timeaccount = StateView('employee_timetracking.timeaccount',
        'employee_timetracking.timeaccount_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add', 'addtimeaccount', 'tryton-ok', True),
            ])
    presences = StateView('employee_timetracking.presence',
        'employee_timetracking.presence_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add', 'addpresences', 'tryton-ok', True),
            ])
    tariffmodel = StateView('employee_timetracking.tariffmodel',
        'employee_timetracking.tariffmodel_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add', 'addtariff', 'tryton-ok', True),
            ])
    worktimemodel = StateView('employee_timetracking.worktimemodel',
        'employee_timetracking.worktimemodel_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add', 'addworktimemodel', 'tryton-ok', True),
            ])

    addtimeaccount = StateTransition()
    addpresences = StateTransition()
    addtariff = StateTransition()
    addworktimemodel = StateTransition()

    def transition_addtimeaccount(self):
        self.timeaccount.save()
        return 'presences'

    def transition_addpresences(self):
        self.presences.save()
        return 'tariffmodel'

    def transition_addtariff(self):
        self.tariffmodel.save()
        return 'worktimemodel'

    def transition_addworktimemodel(self):
        self.worktimemodel.save()
        return 'end'

# end TimetrackingConfig
