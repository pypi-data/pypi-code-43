# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# wizard to create/edit a employee and its connected data
# like: Tryton user, worktime model, tariff model

# 1. selection use existing tryton-user / create new tryton-user
# 2. selection use existing party / create new party
# 3. ask for name etc.
# 4. create party/tryton-user, connect them, add group
# 5. select tariff

from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button, StateAction
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import Eval, If, And, Or, Id, Len
from .tools import get_translation


__all__ = ['EmployeeCreateWizard', 'EmployeeCreateWizardStart']
__metaclass__ = PoolMeta

PARTY_METHOD_NEW = 'n'
PARTY_METHOD_EXIST = 'e'
sel_partymethod = [
        (PARTY_METHOD_NEW, u'create a new party'),
        (PARTY_METHOD_EXIST, u'use an existing party'),
    ]
USER_METHOD_NEW = 'n'
USER_METHOD_EXIST = 'e'
sel_usermethod = [
        (USER_METHOD_NEW, u'create a new user'),
        (USER_METHOD_EXIST, u'use an existing user'),
    ]

CALTITL_HOLIDAY = '0'
CALTITL_HOLIDAYS = '1'
CALTITL_VACAT = '2'
CALTITL_USERS_HOLIDAY = '3'
CALTITL_USERS_HOLIDAYS = '4'
CALTITL_USERS_VACAT = '5'
CALTITL_CUSTOM = '6'
sel_caltitle = [
        (CALTITL_HOLIDAY, u'Holiday'),
        (CALTITL_HOLIDAYS, u'Holidays'),
        (CALTITL_VACAT, u'Vacation'),
        (CALTITL_USERS_HOLIDAY, u"Username's Holiday"),
        (CALTITL_USERS_HOLIDAYS, u"Username's Holidays"),
        (CALTITL_USERS_VACAT, u"Username's Vacation"),
        (CALTITL_CUSTOM, u"Customized Title"),
    ]
dict_caltitle = {}
for i in sel_caltitle:
    (key1, txt1) = i
    dict_caltitle[key1] = txt1


class EmployeeCreateWizardStart(ModelView):
    'Create Employee - start'
    __name__ = 'employee_timetracking.wizemployee_create.start'

    formmode = fields.Char(string=u'Form mode', states={'invisible': True}, readonly=True)
    company = fields.Many2One(string="Company", model_name='company.company', 
                readonly=True)
    partymethod = fields.Selection(string=u'Party', selection=sel_partymethod,
                help=u'create a new party or use an existing party',
                states={
                    'readonly': Eval('formmode', 'n') == 'e',
                    'invisible': Eval('formmode', 'n') == 'e',
                }, depends=['formmode'])
    parties = fields.Function(fields.One2Many(model_name='party.party',
                string='Parties', readonly=True, field=None,
                states={'invisible': True}), 'on_change_with_parties')
    pty_sel = fields.Many2One(string=u'Select Party', 
                depends=['partymethod', 'parties', 'formmode'], model_name='party.party',
                domain=[('id', 'not in', Eval('parties'))],
                states={
                    'required': Eval('partymethod', '') == PARTY_METHOD_EXIST,
                    'invisible': Eval('partymethod', '') == PARTY_METHOD_NEW,
                    'readonly': Eval('formmode', 'n') == 'e',
                })
    pty_name = fields.Char(string=u'Name', depends=['partymethod', 'pty_sel'],
                states={
                    'required': Eval('partymethod', '') == PARTY_METHOD_NEW,
                    'readonly': Eval('partymethod', '') == PARTY_METHOD_EXIST,
                })
    pty_address = fields.Text(string=u'Address', depends=['partymethod', 'pty_sel'])
    pty_zip = fields.Char(string=u'ZIP', depends=['partymethod', 'pty_sel'])
    pty_city = fields.Char(string=u'City', depends=['partymethod', 'pty_sel'])
    pty_country = fields.Many2One(model_name='country.country', string=u'Country', 
                depends=['partymethod', 'pty_sel'])
    pty_subdivision = fields.Many2One(model_name='country.subdivision', string=u'Subdivision', 
                domain=[
                    ('country', '=', Eval('pty_country', -1)),
                    ('parent', '=', None),
                ], depends=['pty_country', 'partymethod', 'pty_sel'])
    pty_phone = fields.Char(string=u'Phone', depends=['partymethod', 'pty_sel'])
    pty_mobile = fields.Char(string=u'Mobile', depends=['partymethod', 'pty_sel'])
    pty_fax = fields.Char(string=u'Fax', depends=['partymethod', 'pty_sel'])
    pty_email = fields.Char(string=u'E-Mail', depends=['partymethod', 'pty_sel'])

    empl_sel = fields.Many2One(string=u'Select Employee', 
                depends=['pty_sel', 'company'], model_name='company.employee',
                domain=[('company', '=', Eval('company'))], readonly=True,
                states={'invisible': True})
    startdate = fields.Date('Start Date', help="When the employee joins the company.",
                domain=[If(
                            (Eval('startdate')) & (Eval('enddate')),
                            ('startdate', '<=', Eval('enddate')),
                            (),
                        )], depends=['enddate'])
    enddate = fields.Date('End Date', help="When the employee leaves the company.",
                domain=[If(
                        (Eval('startdate')) & (Eval('enddate')),
                        ('enddate', '>=', Eval('startdate')),
                        (),
                    )], depends=['startdate'])
    tariff = fields.Many2One(model_name='employee_timetracking.tariffmodel', 
                string=u'Tariff model', depends=['company'], required=True,
                domain=[('company', '=', Eval('company'))])
    worktime = fields.Many2One(model_name='employee_timetracking.worktimemodel', 
                string=u'Working time model', depends=['company'], required=True,
                domain=[('company', '=', Eval('company'))])
    holidays = fields.Integer(string=u'Holidays', required=True, 
                help=u'Number of holidays per year')
    specleave = fields.Integer(string=u'Special leave', required=True, 
                help=u'Number of special leave days per year')
    usr_ena = fields.Boolean(string=u'Tryton user', help=u'Connect employee with a Tryton user')
    usr_method = fields.Selection(string=u'User', selection=sel_usermethod,
                help=u'create a new user or use an existing user',
                states={
                    'invisible': Eval('usr_ena', False) == False,
                }, depends=['usr_ena'])
    users = fields.Function(fields.One2Many(model_name='res.user',
                string='Users', readonly=True, field=None,
                states={'invisible': True}), 'on_change_with_users')
    usr_sel = fields.Many2One(string=u'Selected user', 
                depends=['usr_method', 'usr_ena', 'users'], model_name='res.user',
                domain=[('id', 'not in', Eval('users'))],
                states={
                    'required': And(
                                    Eval('usr_method', '') == USER_METHOD_EXIST,
                                    Eval('usr_ena', False) == True,
                                ),
                    'invisible': Or(
                                    Eval('usr_method', '') == USER_METHOD_NEW,
                                    Eval('usr_ena', False) == False,
                                ),
                    'readonly': And(
                                    Eval('formmode', 'n') == 'e',
                                    Eval('usr_sel', None) != None,
                                ),
                })
    usr_login = fields.Char(string=u'Login', help=u'User name for login to Tryton',
                states={
                    'required': Eval('usr_ena', False) == True,
                    'invisible': Eval('usr_ena', False) == False,
                    'readonly': Eval('usr_method', 'n') == USER_METHOD_EXIST,
                })
    usr_passwd = fields.Char(string=u'Password', help=u'Password for login to Tryton',
                states={
                    'required': Eval('usr_ena', False) == True,
                    'invisible': Eval('usr_ena', False) == False,
                })
    cal_create = fields.Boolean(string=u'Create Holiday Calendar',
                states={
                    'readonly': Len(Eval('calendars', [])) == 0,
                    'invisible': Eval('usr_ena', False) == False,
                }, depends=['calendars', 'usr_ena'])
    cal_titlefmt = fields.Selection(string=u'Title', selection=sel_caltitle,
                states={
                    'required': Eval('cal_create', False) == True,
                    'invisible': Eval('cal_create', False) == False,
                }, depends=['cal_create'], sort=False)
    cal_titletext = fields.Char(string=u'Used Title', size=30,
                states={
                    'invisible': Eval('cal_create', False) == False,
                    'readonly': Eval('cal_titlefmt', '') != CALTITL_CUSTOM,
                    'required': Eval('cal_create', False) == True,
                }, depends=['cal_create', 'cal_titlefmt'])
    calendars = fields.Function(fields.One2Many(string=u'Calendars available', 
                model_name='pim_calendar.calendar', field=None, 
                states={'invisible': True,}), 'on_change_with_calendars')
    cal_sel = fields.Many2One(string=u'Select Calendar', 
                depends=['calendars', 'partymethod', 'cal_create'], model_name='pim_calendar.calendar',
                domain=[('id', 'in', Eval('calendars'))],
                states={
                    'required': And(
                            Eval('partymethod', '') == PARTY_METHOD_EXIST,
                            Eval('cal_create', False) == False,
                        ),
                    'invisible': Eval('cal_create', False) == True,
                })

    @classmethod
    def view_attributes(cls):
        return super(EmployeeCreateWizardStart, cls).view_attributes() + [
                ('//group[@id="grpcal"]', 'states', {'invisible': Eval('usr_ena', False) == False,}),
            ]

    @fields.depends('company')
    def on_change_with_users(self, name=None):
        """ get list of tryton users which are connected to employees
        """
        l1 = []
        pool = Pool()
        Users = pool.get('res.user')
        Company = pool.get('company.company')
        ModelData = pool.get('ir.model.data')
        
        # all employees of all companies
        lstcomp = Company.search([])
        for i in lstcomp:
            l1.extend([x for x in i.employees])

        # connected users
        u_lst = Users.search([
                'OR',
                    ('employee', 'in', l1),
                    ('groups', '=', ModelData.get_id('res', 'user_admin')),
                    ('groups', '=', ModelData.get_id('employee_timetracking', 'group_employee_admin'))
            ])
        return [x.id for x in u_lst]

    @fields.depends('company')
    def on_change_with_parties(self, name=None):
        """ get list of existing partys which are connected to employees/company
        """
        l1 = []
        Company = Pool().get('company.company')
        
        # all companies
        lstcomp = Company.search([])
        for i in lstcomp:
            l1.extend([i.party.id])
            l1.extend([x.party.id for x in i.employees])
        return l1

    @fields.depends('usr_sel')
    def on_change_with_calendars(self, name=None):
        """ get calendars for user
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        if isinstance(self.usr_sel, type(None)):
            return []

        c_lst = Calendar.search([
                    ('allday_events', '=', True), 
                    ('owner', '=', self.usr_sel),
                ], order=[('name', 'ASC')])
        return [x.id for x in c_lst]

    @fields.depends('usr_ena', 'usr_method', 'empl_sel', 'usr_sel', 'usr_login', 'usr_passwd')
    def on_change_usr_ena(self):
        """ tryton user on/off
        """
        if self.usr_ena == True:
            self.usr_method = USER_METHOD_EXIST
            self.on_change_usr_method()
            if isinstance(self.usr_sel, type(None)):
                self.usr_method = USER_METHOD_NEW
        else :
            self.usr_sel = None
            self.usr_method = USER_METHOD_NEW
            self.on_change_usr_method()

    @fields.depends('usr_method', 'empl_sel', 'usr_sel', 'usr_login', 'usr_passwd')
    def on_change_usr_method(self):
        """ switch mode
        """
        User = Pool().get('res.user')
        
        self.usr_sel = None
        if self.usr_method == USER_METHOD_EXIST:
            if not isinstance(self.empl_sel, type(None)):
                u_lst = User.search([('employee', '=', self.empl_sel.id)])
                if len(u_lst) == 1:
                    self.usr_sel = u_lst[0].id
        elif self.usr_method == USER_METHOD_NEW:
            pass
        self.on_change_usr_sel()
        
    @fields.depends('empl_sel', 'startdate', 'enddate', 'hours', 'hoursmode', 'tariff', 'holidays', 'specleave')
    def on_change_empl_sel(self):
        """ load values from selected employee
        """
        if not isinstance(self.empl_sel, type(None)):
            self.startdate = self.empl_sel.start_date
            self.enddate = self.empl_sel.end_date
            self.worktime = self.empl_sel.worktime
            self.tariff = self.empl_sel.tariff
            self.holidays = self.empl_sel.holidays
            self.specleave = self.empl_sel.specleave

    @fields.depends('usr_sel', 'usr_login', 'usr_passwd')
    def on_change_usr_sel(self):
        """ update user fields
        """
        if isinstance(self.usr_sel, type(None)):
            self.usr_login = None
            self.usr_passwd = None
        else :
            self.usr_login = self.usr_sel.login
            self.usr_passwd = self.usr_sel.password
        
    @fields.depends('pty_sel', 'pty_name', 'pty_zip', 'pty_city', 'pty_country', 'pty_subdivision', 'company', 'empl_sel')
    def on_change_pty_sel(self):
        """ update address fields
        """
        self.pty_name = None
        self.pty_address = None
        self.pty_zip = None
        self.pty_city = None
        self.pty_country = None
        self.pty_subdivision = None
        self.pty_phone = None
        self.pty_mobile = None
        self.pty_fax = None
        self.pty_email = None
        self.empl_sel = None
        self.start_date = None
        self.end_date = None
        
        if not isinstance(self.company, type(None)):
            if len(self.company.party.addresses) > 0:
                self.pty_country = self.company.party.addresses[0].country
                self.pty_subdivision = self.company.party.addresses[0].subdivision

        if not isinstance(self.pty_sel, type(None)):
            self.pty_name = self.pty_sel.name
            if len(self.pty_sel.addresses) > 0:
                self.pty_address = self.pty_sel.addresses[0].street
                self.pty_zip = self.pty_sel.addresses[0].zip
                self.pty_city = self.pty_sel.addresses[0].city
                self.pty_country = self.pty_sel.addresses[0].country
                self.pty_subdivision = self.pty_sel.addresses[0].subdivision
            self.pty_phone = self.pty_sel.phone
            self.pty_mobile = self.pty_sel.mobile
            self.pty_fax = self.pty_sel.fax
            self.pty_email = self.pty_sel.email
            
        Employee = Pool().get('company.employee')
        e_lst = Employee.search([
                    ('company', '=', self.company),
                    ('party', '=', self.pty_sel)
                ])
        if len(e_lst) > 0:
            self.empl_sel = e_lst[0].id

    @fields.depends('pty_subdivision', 'pty_country')
    def on_change_pty_country(self):
        if (self.pty_subdivision
                and self.pty_subdivision.country != self.pty_country):
            self.pty_subdivision = None
    
    @fields.depends('cal_titlefmt', 'cal_titletext', 'partymethod', 'pty_sel', 'pty_name')
    def on_change_pty_name(self):
        self.on_change_cal_titlefmt()
    
    @fields.depends('cal_titlefmt', 'cal_titletext', 'partymethod', 'pty_sel', 'pty_name')
    def on_change_cal_titlefmt(self):
        if isinstance(self.partymethod, type(None)):
            return

        if self.partymethod == PARTY_METHOD_NEW:
            if isinstance(self.pty_name, type(None)):
                return
            pname = self.pty_name
        else :
            if isinstance(self.pty_sel, type(None)):
                return
            pname = self.pty_sel.rec_name
        
        if self.cal_titlefmt == CALTITL_CUSTOM:
            pass
        elif (self.cal_titlefmt in dict_caltitle.keys()) and (self.cal_titlefmt != CALTITL_CUSTOM):
            self.cal_titletext = get_translation(
                'employee_timetracking.wizemployee_create.start,cal_titlefmt2', 
                'selection', 
                dict_caltitle[self.cal_titlefmt])
            if 'replacethis' in self.cal_titletext:
                self.cal_titletext = self.cal_titletext.replace('replacethis', pname)

# end EmployeeCreateWizardStart


class EmployeeCreateWizard(Wizard):
    'Create Employee'
    __name__ = 'employee_timetracking.wizemployee_create'
    
    start_state = 'start'
    start = StateView(model_name='employee_timetracking.wizemployee_create.start', \
                view='employee_timetracking.act_createemployee_wizard_form', \
                buttons=[Button(string=u'Cancel', state='end', icon='tryton-cancel'), 
                         Button(string=u'Save Employee', state='saveemployee', icon='tryton-save')])
    saveemployee = StateTransition()

    @classmethod
    def __setup__(cls):
        super(EmployeeCreateWizard, cls).__setup__()
        cls._error_messages.update({
                'wizemploy_onlyone': (u"Please select only one employee."),
                })

    def default_start(self, fields):
        """ fill form
        """
        r1 = {}
        tr1 = Transaction()
        pool = Pool()
        Employee = pool.get('company.employee')
        context = tr1.context
        
        r1['formmode'] = 'n'
        r1['company'] = tr1.context.get('company', None)
        r1['usr_method'] = USER_METHOD_NEW
        r1['usr_ena'] = False
        r1['cal_create'] = True
        r1['cal_titlefmt'] = CALTITL_HOLIDAY
        self.start.company = r1['company']
        
        if context['active_model'] == 'company.employee':
            emplo1 = Employee.browse(context['active_ids'])
            if len(emplo1) != 1:
                self.raise_user_error('wizemploy_onlyone')
            else :
                r1['partymethod'] = PARTY_METHOD_EXIST
                r1['pty_sel'] = emplo1[0].party.id
                r1['formmode'] = 'e'
                
                # get field values
                self.start.pty_sel = emplo1[0].party
                self.start.on_change_pty_sel()
                self.start.on_change_empl_sel()
                
                l1 = ['pty_name', 'pty_address', 'pty_zip', 'pty_city', 'pty_country',
                        'pty_subdivision', 'pty_phone', 'pty_mobile', 'pty_fax', 'pty_email',
                        'startdate', 'enddate', 'tariff', 'worktime', 'holidays', 'specleave', 'empl_sel']
                l2 = ['pty_subdivision', 'pty_country', 'empl_sel', 'tariff', 'worktime']
                for k in l1:
                    r1[k] = getattr(self.start, k, None)
                for k in l2:
                    if not isinstance(r1[k], type(None)):
                        r1[k] = r1[k].id
                
                # tryton user
                self.start.usr_ena = True
                self.start.on_change_usr_ena()
                if isinstance(self.start.usr_sel, type(None)):
                    self.start.usr_ena = False
                l1 = ['usr_passwd', 'usr_login', 'usr_method', 'usr_ena', 'usr_sel']
                for k in l1:
                    r1[k] = getattr(self.start, k, None)
                if not isinstance(r1['usr_sel'], type(None)):
                    r1['usr_sel'] = r1['usr_sel'].id
                    
                # calendar
                if isinstance(emplo1[0].calendar, type(None)):
                    r1['cal_create'] = True
                    r1['cal_titlefmt'] = CALTITL_HOLIDAY
                else :
                    r1['cal_create'] = False
                    r1['cal_sel'] = emplo1[0].calendar.id
        else :
            r1['partymethod'] = PARTY_METHOD_NEW
        return r1

    def edit_group(self, user, onoff):
        """ del/add group to user
        """
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        Group = pool.get('res.group')
        
        id_grp = ModelData.get_id('employee_timetracking', 'group_timetracking_employee')
        grp_obj = Group(id_grp)
        
        l2 = list(user.groups)
        if onoff == True:
            if not grp_obj in l2:
                l2.append(grp_obj)
        else :
            if grp_obj in l2:
                del l2[l2.index(grp_obj)]
        user.groups = l2
        user.save()
        
    def disconnect_user(self, employee):
        """ disconnect tryton user and employee
        """
        User = Pool().get('res.user')

        # disconnect user
        u_lst = User.search([('employee', '=', employee)])
        # some users are still connected with this employee
        for i in u_lst:
            i.employee = None
            l1 = list(i.employees)
            if employee in l1:
                del l1[l1.index(employee)]
            i.employees = l1
            self.edit_group(i, False)
            i.save()

    def edit_user(self, employee):
        """ edit/create tryton user
        """
        pool = Pool()
        User = pool.get('res.user')

        if self.start.usr_ena == False:
            self.disconnect_user(employee)
            return None
        
        if isinstance(self.start.usr_sel, type(None)):
            self.disconnect_user(employee)

            # create new user
            u_obj = User.create([{
                            'name': self.start.pty_name,
                            'login': self.start.usr_login,
                            'password': self.start.usr_passwd,
                        }])
            if len(u_obj) == 1:
                u_obj = u_obj[0]
            else :
                raise ValueError(u'wrong number of users found: %s (--> 1)' % len(u_obj))
        else :
            # edit existing user
            u_obj = self.start.usr_sel

        if self.start.usr_passwd != u_obj.password:
            u_obj.password = self.start.usr_passwd
        u_obj.active = True
        u_obj.name = self.start.pty_name
        u_obj.main_company = self.start.company
        u_obj.company = self.start.company
        u_obj.employees = [employee]
        u_obj.employee = employee
        self.edit_group(u_obj, True)
        u_obj.save()
        return u_obj

    def edit_employee(self, party):
        """ edit/create employee
        """
        pool = Pool()
        Employee = pool.get('company.employee')
        Evaluation = pool.get('employee_timetracking.evaluation')
        
        if isinstance(self.start.empl_sel, type(None)):
            # create new
            e_obj = Employee()
            e_obj.party = party
            e_obj.company = self.start.company
        else :
            # use selected
            e_obj = self.start.empl_sel

        e_obj.start_date = self.start.startdate
        e_obj.end_date = self.start.enddate
        e_obj.worktime = self.start.worktime
        e_obj.tariff = self.start.tariff
        e_obj.holidays = self.start.holidays
        e_obj.specleave = self.start.specleave
        e_obj.save()

        # edit companies of cronjob
        Evaluation.edit_cronjob()

        return e_obj
        
    def edit_contacts(self, party):
        """ edit/create contact
        """
        Contact = Pool().get('party.contact_mechanism')
        
        l2 = [
            ('phone', self.start.pty_phone, 'other_value'), 
            ('mobile', self.start.pty_mobile, 'other_value'),
            ('fax', self.start.pty_fax, 'other_value'), 
            ('email', self.start.pty_email, 'email')]
        for i in l2:
            (typ1, val1, oc1) = i

            # search current type
            c_lst = Contact.search([
                        ('party', '=', party),
                        ('type', '=', typ1)
                    ])

            if (len(val1) == 0) and (len(c_lst) > 0):
                Contact.delete(c_lst)
            elif (len(val1) > 0) and (len(c_lst) == 0):
                c_obj = Contact()
                c_obj.active = Contact.default_active()
                c_obj.type = typ1
                c_obj.party = party
                c_obj.on_change_type()
                setattr(c_obj, oc1, val1)
                getattr(c_obj, 'on_change_' + oc1)()
                c_obj.save()
            elif (len(val1) > 0) and (len(c_lst) > 0):
                # edit 1st item
                setattr(c_lst[0], oc1, val1)
                getattr(c_lst[0], 'on_change_' + oc1)()
                c_lst[0].save()
        
    def edit_party(self):
        """ create/save party data
        """
        Address = Pool().get('party.address')
        Party = Pool().get('party.party')
        
        if self.start.partymethod == PARTY_METHOD_NEW:
            party = Party()
            party.name = self.start.pty_name
            party.active = Party.default_active()
            party.categories = Party.default_categories()
            party.lang = Party.default_lang()
            
            adr = Address()
            adr.name = ''
            adr.street = self.start.pty_address
            adr.zip = self.start.pty_zip
            adr.city = self.start.pty_city
            adr.country = self.start.pty_country
            adr.subdivision = self.start.pty_subdivision
            party.addresses = [adr]
            
            party.save()
            return party
        elif self.start.partymethod == PARTY_METHOD_EXIST:
            p_obj = self.start.pty_sel
            
            # create address
            if len(p_obj.addresses) == 0:
                adr1 = Address()
                adr1.active = True
                p_obj.addresses = [adr1]
                p_obj.save()
            
            # edit address
            p_obj.addresses[0].street = self.start.pty_address
            p_obj.addresses[0].zip = self.start.pty_zip
            p_obj.addresses[0].city = self.start.pty_city
            p_obj.addresses[0].country = self.start.pty_country
            p_obj.addresses[0].subdivision = self.start.pty_subdivision
            p_obj.addresses[0].save()
            return p_obj
        else :
            raise ValueError("wrong field value in 'partymethod'")
            
    def edit_calendar(self, trytonuser, employee):
        """ add/edit calendar
        """
        Calendar = Pool().get('pim_calendar.calendar')
        
        if self.start.usr_ena == False:
            return
        
        if self.start.cal_create == True:
            c1 = Calendar(
                    name = self.start.cal_titletext,
                    owner = trytonuser,
                    allday_events = True,
                )
            c1.save()
            employee.calendar = c1
            employee.save()
        else :
            if isinstance(employee.calendar, type(None)):
                raise ValueError('missing calendar on employee')
            # switch to selected calendar
            if employee.calendar != self.start.cal_sel:
                employee.calendar = self.start.cal_sel
                employee.save()
        
    def transition_saveemployee(self):
        """ create employee
        """
        party = self.edit_party()
        self.edit_contacts(party)
        employee = self.edit_employee(party)
        usr1 = self.edit_user(employee)
        self.edit_calendar(usr1, employee)

        return 'end'

# end EmployeeCreateWizard
