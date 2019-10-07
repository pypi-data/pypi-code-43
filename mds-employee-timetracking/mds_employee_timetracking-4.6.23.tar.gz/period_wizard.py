# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button, StateAction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id, Or, Len
from trytond.transaction import Transaction
from datetime import datetime, timedelta
from trytond.modules.employee_timetracking.const import WF_BREAKPERIOD_CREATED, WF_PERIOD_CREATED

# wizard to simplify the enter Period of working time
# workflow actions are started if possible

__all__ = ['PeriodAttendanceWizard', 'PeriodAttendanceWizardStart']
__metaclass__ = PoolMeta


CURRSTAT_ACTIVE = 'c'
CURRSTAT_INACTIVE = 'i'
sel_currstate = [
        (CURRSTAT_ACTIVE, u'Active'),
        (CURRSTAT_INACTIVE, u'Inactive'),
    ]

class PeriodAttendanceWizardStart(ModelView):
    'Enter attendance - start'
    __name__ = 'employee_timetracking.wizperiod_attendance.start'

    company = fields.Many2One(string="Company", model_name='company.company', 
            readonly=True, depends=['employee'])
    employee = fields.Many2One(string="Employee", model_name='company.employee',
            states={
                'readonly': ~Or(
                        Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                        Id('employee_timetracking', 'group_worktime_edit').in_(Eval('context', {}).get('groups', [])),
                    )
            }, 
            domain=[
                ('company', '=', Eval('context', {}).get('company', None)),
                ('tariff', '!=', None)
            ])
    currstate = fields.Selection(string=u'Current State', readonly=True, 
            selection=sel_currstate)
    currtype = fields.Char(string=u'Type of Presence', readonly=True)
    currstart = fields.DateTime(string=u'Start', readonly=True)
    currperiod = fields.Char(string=u'Time period', readonly=True)
    presences = fields.Function(fields.One2Many(string='Presences', readonly=True,
            help='allowed presences', field=None, 
            model_name='employee_timetracking.presence',
            states={'invisible': True}, depends=['employee']), 
            'on_change_with_presences')
    presence = fields.Many2One(string=u'Presence', model_name='employee_timetracking.presence',
            help='select the presence type to enter', depends=['presences'],
            domain=[('id', 'in', Eval('presences', []))],
            states={
                'readonly': Len(Eval('presences', []))==0,
                'required': Len(Eval('presences', []))>0,
            })
    breakstate = fields.Selection(string=u"Status of the break", readonly=True,
            selection=sel_currstate)
    breakstart = fields.DateTime(string=u"Break start", readonly=True, 
            help=u"Start time of the current break")
    breakperiod = fields.Char(string=u'Break time period', readonly=True,
            help=u"Duration of the current break")

    @classmethod
    def __setup__(cls):
        super(PeriodAttendanceWizardStart, cls).__setup__()
        cls._error_messages.update({
                'enterper_notariff': (u"Please assign a tariff to employee '%s' first."),
                })

    @fields.depends('employee')
    def on_change_with_presences(self, name=None):
        """ get presences from employee
        """
        if isinstance(self.employee, type(None)):
            return []
        else :
            return [x.id for x in self.employee.tariff.presence]
    
    def get_newest_period(self):
        """ return newest period-item, state-info
        """
        Period = Pool().get('employee_timetracking.period')
        
        # newest item by startpos
        s_lst = Period.search([('employee', '=', self.employee), ('startpos', '!=', None)], 
                    order=[('startpos', 'DESC')], limit=1)
        # newest item by endpos
        e_lst = Period.search([('employee', '=', self.employee), ('endpos', '!=', None)], 
                    order=[('endpos', 'DESC')], limit=1)

        currstart = None
        presence = self.employee.tariff.type_present
        period = None
        currstate = CURRSTAT_INACTIVE
        
        if (len(s_lst) > 0) and (len(e_lst) > 0):
            if s_lst[0].id == e_lst[0].id:
                pass
            elif s_lst[0].startpos > e_lst[0].endpos:
                # last item is 'begin'
                currstate = CURRSTAT_ACTIVE
                period = s_lst[0]
                presence = s_lst[0].presence
        elif (len(s_lst) > 0) and (len(e_lst) == 0):
            currstate = CURRSTAT_ACTIVE
            period = s_lst[0]
            presence = s_lst[0].presence
        return (currstate, period, presence)
        
    def updt_period_info(self):
        """ select period item, update infos
        """
        self.currperiod = ''
        self.currtype = ''
        self.currstart = None
        self.presence = None

        (c_state, c_period, c_presence) = self.get_newest_period()

        self.currstate = c_state
        self.presence = c_presence
        if c_state == CURRSTAT_ACTIVE:
            self.currstart = c_period.startpos
            self.currperiod = self.format_timedelta(self.get_delta(c_period.startpos))
            self.currtype = c_presence.name

    def updt_break_info(self):
        """ select break time item, update info
        """
        def set_breaktime_info(self, startbreak):
            self.breakstate = CURRSTAT_ACTIVE
            self.breakstart = startbreak.startpos
            self.breakperiod = self.format_timedelta(self.get_delta(startbreak.startpos))

        BreakPeriod = Pool().get('employee_timetracking.breakperiod')
        # newest item by startpos
        s_lst = BreakPeriod.search([('employee', '=', self.employee), ('startpos', '!=', None)], 
                    order=[('startpos', 'DESC')], limit=1)
        # newest item by endpos
        e_lst = BreakPeriod.search([('employee', '=', self.employee), ('endpos', '!=', None)], 
                    order=[('endpos', 'DESC')], limit=1)

        self.breakstart = None
        self.breakperiod = ''
        self.breakstate = CURRSTAT_INACTIVE
        if (len(s_lst) > 0) and (len(e_lst) > 0):
            if s_lst[0].id == e_lst[0].id:
                pass
            elif s_lst[0].startpos > e_lst[0].endpos:
                # last item is 'begin'
                set_breaktime_info(self, s_lst[0])
        elif (len(s_lst) > 0) and (len(e_lst) == 0):
            set_breaktime_info(self, s_lst[0])

    @fields.depends('company', 'employee','currstate', 'currstart', 'currperiod', 'presence', \
        'breakstate', 'breakstart', 'breakperiod')
    def on_change_employee(self):
        """ update company
        """
        if not isinstance(self.employee, type(None)):
            if isinstance(self.employee.tariff, type(None)):
                self.raise_user_error('enterper_notariff', (self.employee.party.rec_name))
                
            self.company = self.employee.company
            self.updt_period_info()
            self.updt_break_info()
        else :
            self.currstart = None
            self.currperiod = None
            self.currtype = ''
            self.currstate = CURRSTAT_INACTIVE
            self.presence = None
            self.breakstate = CURRSTAT_INACTIVE
            self.breakstart = None
            self.breakperiod = None

    def format_timedelta(self, tdelta):
        """ format
        """
        hours = tdelta.seconds // (60 * 60)
        minutes = (tdelta.seconds - hours * 60 *60) // 60
        t1 = '%d h, %02d m' % (hours, minutes)
        if tdelta.days > 0:
            return '%d d, %s' % (tdelta.days, t1)
        else :
            return t1

    def get_delta(self, startpos):
        """ get timedelta since start, round down to minute
        """
        sec1 = (datetime.now() - startpos).seconds
        sec1 = sec1 - sec1 % 60
        return timedelta(seconds=sec1, days=(datetime.now() - startpos).days)
        
# end PeriodAttendanceWizardStart


class PeriodAttendanceWizard(Wizard):
    'Enter attendance'
    __name__ = 'employee_timetracking.wizperiod_attendance'
    
    start_state = 'start'
    start = StateView(model_name='employee_timetracking.wizperiod_attendance.start', \
                view='employee_timetracking.attendance_wizard_start_form', \
                buttons=[Button(string=u'Cancel', state='end', icon='tryton-cancel'), 
                         Button(string=u'End break', state='endbreak', icon='tryton-save'),
                         Button(string=u'Start break', state='beginbreak', icon='tryton-save'),
                         Button(string=u'Ending', state='ending', icon='tryton-save'),
                         Button(string=u'Beginning', state='beginning', icon='tryton-save'),
                        ])
    beginning = StateTransition()
    ending = StateTransition()
    beginbreak = StateTransition()
    endbreak = StateTransition()

    @classmethod
    def __setup__(cls):
        super(PeriodAttendanceWizard, cls).__setup__()
        cls._error_messages.update({
                'enterper_noemployee': (u"Please select an employee first."),
                'enterper_notariff': (u"Please assign a tariff to employee '%s' first."),
                'enterper_notinit': (u"Dialog not init."),
                'enterper_nopresence': (u"No presence entered."),
                })
    
    def default_start(self, fields):
        """ fill form
        """
        r1 = {}
        tr1 = Transaction()
        r1['employee'] = tr1.context.get('employee', None)
        r1['company'] = tr1.context.get('company', None)
        r1['currstate'] = CURRSTAT_ACTIVE
        return r1

    def open_item(self, pres_type):
        """ open a item of type 'pres_type'
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        
        Period = Pool().get('employee_timetracking.period')
        
        (currstate, period, presence) = self.start.get_newest_period()
        if currstate == CURRSTAT_ACTIVE:
            if period.state != WF_PERIOD_CREATED:
                raise ValueError('wrong state in period: id=%s (%s)' % \
                    (period.id, period.rec_name))
            # startpos not older than 12h
            if ((period.startpos + timedelta(seconds=12*60*60)) > datetime.now()):
                period.endpos = datetime.now() - timedelta(seconds=5)
                period.save()
                Period.wfexamine([period])    # wf-step

        pobj = Period(
                    employee=self.start.employee,
                    presence=pres_type,
                    startpos=datetime.now(),
                    endpos=None,
                    state=Period.default_state()
                )
        pobj.save()
    
    def close_item(self, pres_type):
        """ close a item of 'pres_type'
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')

        Period = Pool().get('employee_timetracking.period')

        (currstate, period, presence) = self.start.get_newest_period()
        if currstate == CURRSTAT_ACTIVE:
            if (period.presence == pres_type) and (period.state == WF_PERIOD_CREATED):
                period.endpos = datetime.now()
                period.save()
                Period.wfexamine([period])    # wf-step
                return

        # no matching open item found- create one
        pobj = Period(
                employee=self.start.employee,
                presence=pres_type,
                startpos=None,
                endpos=datetime.now(),
                state=Period.default_state()
                )
        pobj.save()

    def transition_beginbreak(self):
        """ store begin of break
        """
        if isinstance(self.start, type(None)):
            self.raise_user_error('enterper_notinit')
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        if isinstance(self.start.employee.tariff, type(None)):
            self.raise_user_error('enterper_notariff', (self.start.employee.rec_name))

        BreakPeriod = Pool().get('employee_timetracking.breakperiod')
        
        # search possibly open item
        o_lst = BreakPeriod.search([
                    ('employee', '=', self.start.employee),
                ], order=[('startpos', 'DESC')], limit=1)

        if len(o_lst) > 0:
            # close open break time item
            # if startpos not older than 2h
            if o_lst[0].state == WF_BREAKPERIOD_CREATED:
                if isinstance(o_lst[0].endpos, type(None)) and \
                    ((o_lst[0].startpos + timedelta(seconds=2*60*60)) > datetime.now()):
                    o_lst[0].endpos = datetime.now() - timedelta(seconds=5)
                    o_lst[0].save()
                    BreakPeriod.wfexamine([o_lst[0]])    # wf-step

        pobj = BreakPeriod(
                    employee=self.start.employee,
                    startpos=datetime.now(),
                    endpos=None,
                    state=BreakPeriod.default_state()
                )
        pobj.save()
        return 'end'

    def transition_endbreak(self):
        """ store end of break
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        if isinstance(self.start, type(None)):
            self.raise_user_error('enterper_notinit')
        if isinstance(self.start.employee.tariff, type(None)):
            self.raise_user_error('enterper_notariff', (self.start.employee.rec_name))

        # find open item
        BreakPeriod = Pool().get('employee_timetracking.breakperiod')
        p_lst = BreakPeriod.search([
                    ('employee', '=', self.start.employee),
                ], order=[('startpos', 'DESC')], limit=1)
        
        if len(p_lst) > 0:
            # if newest item is still open
            if (p_lst[0].state == WF_BREAKPERIOD_CREATED) and \
                (not isinstance(p_lst[0].startpos, type(None))) and \
                isinstance(p_lst[0].endpos, type(None)):
                p_lst[0].endpos = datetime.now()
                p_lst[0].save()
                BreakPeriod.wfexamine([p_lst[0]])    # wf-step
                return 'end'

        # no matching open item found- create one
        pobj = BreakPeriod(
                    employee=self.start.employee,
                    startpos=None,
                    endpos=datetime.now(),
                    state=BreakPeriod.default_state()
                )
        pobj.save()
        return 'end'

    def transition_ending(self):
        """ store end of local work
        """
        if isinstance(self.start, type(None)):
            self.raise_user_error('enterper_notinit')
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        if isinstance(self.start.employee.tariff, type(None)):
            self.raise_user_error('enterper_notariff', (self.start.employee.rec_name))
        if isinstance(self.start.presence, type(None)):
            self.raise_user_error('enterper_nopresence')
        self.close_item(self.start.presence)
        return 'end'

    def transition_beginning(self):
        """ store start of local work
        """
        if isinstance(self.start, type(None)):
            self.raise_user_error('enterper_notinit')
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        if isinstance(self.start.employee.tariff, type(None)):
            self.raise_user_error('enterper_notariff', (self.start.employee.rec_name))
        if isinstance(self.start.presence, type(None)):
            self.raise_user_error('enterper_nopresence')
        self.open_item(self.start.presence)
        return 'end'
    
# end PeriodAttendanceWizard
