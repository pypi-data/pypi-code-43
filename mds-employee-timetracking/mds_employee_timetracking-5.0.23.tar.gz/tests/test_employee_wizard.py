# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.company.tests.test_company import create_company, set_company
from trytond.exceptions import UserError
from trytond.modules.employee_timetracking.tests.testlib import create_tariff_full, \
    create_employee, create_worktime_full
from trytond.modules.employee_timetracking.employee_wizard import USER_METHOD_NEW, CALTITL_HOLIDAYS
from datetime import date, time
from decimal import Decimal


class EmployeeWizardTestCase(ModuleTestCase):
    'Test employee-wizard module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_employee_wizard_on_change_with_users(self):
        """ test: get list of tryton users, connected to employees, but no admins
        """
        pool = Pool()
        User = pool.get('res.user')
        ModelData = pool.get('ir.model.data')

        def create_user(login, password):
            user, = User.create([{'name': login, 'login': login,}])
            User.write([user], {'password': password,})
            return user

        # company + employee
        c1 = create_company('Company 1')
        self.assertTrue(c1)
        e1 = create_employee(c1, 'c1, Emplo 1')
        self.assertTrue(e1)
        e2 = create_employee(c1, 'c1, Emplo 2')
        self.assertTrue(e2)

        l1 = []
        # tryton user 1
        u1 = create_user('emplo1', 'test1234')
        u1.main_company = c1
        u1.company = c1
        u1.employees =[e1]
        u1.employee = e1
        u1.save()
        l1.append(u1.id)

        # tryton user 2
        u2 = create_user('emplo2', 'test1234')
        u2.main_company = c1
        u2.company = c1
        u2.employees =[e2]
        u2.employee = e2
        u2.save()
        l1.append(u2.id)
        
        # single tryton user
        u3 = create_user('emplo3', 'test1234')

        # get admins
        adm_lst = User.search([
                'OR',
                    ('groups', '=', ModelData.get_id('res', 'user_admin')),
                    ('groups', '=', ModelData.get_id('employee_timetracking', 'group_employee_admin'))
            ])
        l1.extend([x.id for x in adm_lst])
        l1.sort()
        
        # get all connected user, ignore single user
        EmployeeCrWizStart = pool.get('employee_timetracking.wizemployee_create.start')
        e_obj = EmployeeCrWizStart()
        l2 = e_obj.on_change_with_users()
        l2.sort()
        self.assertEqual(l1, l2)

    @with_transaction()
    def test_employee_wizard_on_change_with_parties(self):
        """ test: get list of parties connected to employee/company
        """
        l2 = []
        c1 = create_company('Company 1')
        l2.append(c1.party.id)
        self.assertTrue(c1)
        
        c2 = create_company('Company 2')
        l2.append(c2.party.id)
        self.assertTrue(c2)
        
        e1 = create_employee(c1, 'c1, Emplo 1')
        l2.append(e1.party.id)
        self.assertTrue(e1)
        
        e2 = create_employee(c1, 'c1, Emplo 2')
        l2.append(e2.party.id)
        self.assertTrue(e2)
        
        e3 = create_employee(c2, 'c2, Emplo 1')
        l2.append(e3.party.id)
        self.assertTrue(e3)
        l2.sort()
        
        pool = Pool()
        Party = pool.get('party.party')
        p1, = Party.create([{'name': 'Party 1', 'addresses': [('create', [{}])],}])
        self.assertTrue(p1)
        p2, = Party.create([{'name': 'Party 2', 'addresses': [('create', [{}])],}])
        self.assertTrue(p2)
        
        # get all connected parties, ignore single parties
        EmployeeCrWizStart = pool.get('employee_timetracking.wizemployee_create.start')
        e_obj = EmployeeCrWizStart()
        l1 = e_obj.on_change_with_parties()
        l1.sort()
        self.assertEqual(l1, l2)
    
    @with_transaction()
    def test_employee_wizard_edit_user(self):
        """ test: create user, change values, disconnect
        """
        pool = Pool()
        User = pool.get('res.user')

        c1 = create_company('Company 1')
        self.assertTrue(c1)
        e1 = create_employee(c1, 'c1, Emplo 1')
        self.assertTrue(e1)

        EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
        (sess_id, start_state, end_state) = EmployeeWizard.create()
        w_obj = EmployeeWizard(sess_id)
        
        w_obj.start.company = c1
        w_obj.start.usr_ena = True
        w_obj.start.usr_sel = None
        w_obj.start.pty_name = 'Frida'
        w_obj.start.usr_login = 'frida'
        w_obj.start.usr_passwd = 'test1234'
        
        # create user
        w_obj.edit_user(e1)
        
        u_lst = User.search([('employee', '=', e1)])
        self.assertEqual(len(u_lst), 1)
        self.assertEqual(u_lst[0].name, 'Frida')
        self.assertEqual(u_lst[0].login, 'frida')
        self.assertEqual(u_lst[0].employee, e1)
        self.assertEqual(list(u_lst[0].employees), [e1])

        # edit name
        w_obj.start.usr_sel = u_lst[0]
        w_obj.start.pty_name = 'Freya'
        w_obj.edit_user(e1)
        self.assertEqual(u_lst[0].name, 'Freya')        

        # disconnect
        w_obj.start.usr_ena = False
        w_obj.edit_user(e1)
        self.assertEqual(u_lst[0].employee, None)
        self.assertEqual(list(u_lst[0].employees), [])
        
    @with_transaction()
    def test_employee_wizard_disconnect_user(self):
        """ test: remove connection between user and employee
        """
        pool = Pool()
        User = pool.get('res.user')
        u_obj, = User.create([{'name': 'Frida', 'login': 'frida', 'password': 'test1234'}])
        c1 = create_company('Company 1')
        self.assertTrue(c1)
        e1 = create_employee(c1, 'c1, Emplo 1')
        self.assertTrue(e1)
        u_obj.company = c1
        u_obj.main_company = c1
        u_obj.employees = [e1]
        u_obj.employee = e1
        u_obj.save()
        
        # check before
        u_lst = User.search([('employee', '=', e1)])
        self.assertEqual(len(u_lst), 1)
        self.assertEqual(u_lst[0].name, 'Frida')
        self.assertEqual(u_lst[0].login, 'frida')
        self.assertEqual(u_lst[0].employee, e1)
        self.assertEqual(list(u_lst[0].employees), [e1])
        
        EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
        (sess_id, start_state, end_state) = EmployeeWizard.create()
        w_obj = EmployeeWizard(sess_id)

        # disconnect
        w_obj.disconnect_user(e1)
        
        # check after
        self.assertEqual(u_lst[0].name, 'Frida')
        self.assertEqual(u_lst[0].login, 'frida')
        self.assertEqual(u_lst[0].employee, None)
        self.assertEqual(list(u_lst[0].employees), [])

    @with_transaction()
    def test_employee_wizard_edit_group(self):
        """ test: add/del tryton user to/from group 'group_timetracking_employee'
        """
        pool = Pool()
        User = pool.get('res.user')
        Group = pool.get('res.group')
        ModelData = pool.get('ir.model.data')

        grp_obj = Group(ModelData.get_id('employee_timetracking', 'group_timetracking_employee'))
        u_obj, = User.create([{'name': 'Frida', 'login': 'frida', 'password': 'test1234'}])
        self.assertTrue(u_obj)

        self.assertTrue(not grp_obj in u_obj.groups)
        
        EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
        (sess_id, start_state, end_state) = EmployeeWizard.create()
        w_obj = EmployeeWizard(sess_id)

        w_obj.edit_group(u_obj, True)
        self.assertTrue(grp_obj in u_obj.groups)

        w_obj.edit_group(u_obj, False)
        self.assertTrue(not grp_obj in u_obj.groups)
        
    @with_transaction()
    def test_employee_wizard_edit_employee(self):
        """ test: wizard edit existing employee
        """
        pool = Pool()
        Party = pool.get('party.party')
        Employee = pool.get('company.employee')
        Evaluation = pool.get('employee_timetracking.evaluation')

        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            # create party
            party, = Party.create([{
                        'name': 'Frida',
                        'addresses': [('create', [{'zip':'12345', 'city':'Berlin', 'street': 'Color Street 1'}])],
                        'contact_mechanisms': [('create', [
                                    {'type':'phone', 'value': '0123-456789'},
                                    {'type':'email', 'value': 'frida@heaven.org'}
                                ])],
                        }])
            p_lst = Party.search([('name', '=', 'Frida')])
            self.assertEqual(len(p_lst), 1)
            self.assertEqual(p_lst[0].name, 'Frida')
            
            # create employee
            employee, = Employee.create([{
                    'party': p_lst[0].id,
                    'company': tarobj1.company.id,
                    'start_date': date(2000, 10, 1),
                    'end_date': None,
                    'tariff': tarobj1.id,
                    'holidays': 22,
                    'specleave': 2,
                    }])
            e_lst = Employee.search([])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].party.name, 'Frida')
            self.assertEqual(e_lst[0].company.party.name, 'm-ds 1')
            self.assertEqual(e_lst[0].tariff.name, 'Tariff1')
    
            # update context
            transaction.set_context(active_model='company.employee')
            transaction.set_context(active_ids=[e_lst[0].id])
            transaction.set_context(active_id=e_lst[0].id)
    
            # check companies of cron job
            self.assertRaisesRegex(UserError,
                "The company 'm-ds 1' is not in the list of companies of the cron job.",
                Evaluation.check_cronsetup)
            
            # start wizard
            EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
            (sess_id, start_state, end_state) = EmployeeWizard.create()
            w_obj = EmployeeWizard(sess_id)
            self.assertEqual(start_state, 'start')
            
            result = EmployeeWizard.execute(sess_id, {}, start_state)
            self.assertEqual(list(result.keys()), ['view'])
            self.assertEqual(result['view']['defaults']['company'], tarobj1.company.id)
            self.assertEqual(result['view']['defaults']['formmode'], 'e')
            self.assertEqual(result['view']['defaults']['partymethod'], 'e')
            
            for i in result['view']['defaults']:
                setattr(w_obj.start, i, result['view']['defaults'][i])
    
            self.assertEqual(w_obj.start.pty_name, 'Frida')
            self.assertEqual(w_obj.start.pty_address, 'Color Street 1')
            self.assertEqual(w_obj.start.pty_zip, '12345')
            self.assertEqual(w_obj.start.pty_city, 'Berlin')
            self.assertEqual(w_obj.start.pty_phone, '0123-456789')
            self.assertEqual(w_obj.start.pty_email, 'frida@heaven.org')
            self.assertEqual(w_obj.start.pty_fax, '')
            self.assertEqual(w_obj.start.pty_mobile, '')
            self.assertEqual(w_obj.start.pty_sel.id, p_lst[0].id)
            self.assertEqual(w_obj.start.empl_sel.id, e_lst[0].id)
    
            r1 = {}
            l1 = ['pty_name', 'pty_address', 'pty_zip', 'pty_city', 'pty_country', 'pty_subdivision',
                'pty_phone', 'pty_mobile', 'pty_fax', 'pty_email', 'formmode', 'partymethod',
                'holidays', 'specleave']
            for i in l1:
                r1[i] = getattr(w_obj.start, i)
    
            r1.update({
                'company': tarobj1.company.id,
                'pty_sel': w_obj.start.pty_sel.id,
                'startdate': date(2000, 10, 1),
                'enddate': None,
                'tariff': tarobj1.id,
                'worktime': None,
                'empl_sel': w_obj.start.empl_sel.id,
            })
    
            # edit values
            r1['pty_address'] = 'Color Street 2'
            r1['pty_email'] = 'diego@heaven.org'
            r1['pty_fax'] = '0345-4567890'
            r1['holidays'] = 25
            EmployeeWizard.execute(sess_id, {
                    start_state: r1
                }, 'saveemployee')
    
            # check result
            Employee = pool.get('company.employee')
            e_lst = Employee.search([
                        ('company', '=', tarobj1.company),
                    ])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].party.name, 'Frida')
            # address
            self.assertEqual(len(e_lst[0].party.addresses), 1)
            self.assertEqual(e_lst[0].party.addresses[0].street, 'Color Street 2')
            self.assertEqual(e_lst[0].party.addresses[0].zip, '12345')
            self.assertEqual(e_lst[0].party.addresses[0].city, 'Berlin')
            # contact
            self.assertEqual(len(e_lst[0].party.contact_mechanisms), 3)
            self.assertEqual(e_lst[0].party.phone, '0123-456789')
            self.assertEqual(e_lst[0].party.fax, '0345-4567890')
            self.assertEqual(e_lst[0].party.email, 'diego@heaven.org')
            # employee
            self.assertEqual(str(e_lst[0].start_date), '2000-10-01')
            self.assertEqual(e_lst[0].tariff.name, 'Tariff1')

            # check again companies of cron job
            Evaluation.check_cronsetup()

    @with_transaction()
    def test_employee_wizard_create_with_party_exists(self):
        """ test: wizard create new employee and use existing party
        """
        pool = Pool()
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            
            # start wizard
            EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
            (sess_id, start_state, end_state) = EmployeeWizard.create()
            w_obj = EmployeeWizard(sess_id)
            self.assertEqual(start_state, 'start')
    
            # setup form
            transaction.set_context(active_model='ir.ui.menu')
            result = EmployeeWizard.execute(sess_id, {}, start_state)
            self.assertEqual(list(result.keys()), ['view'])
            self.assertEqual(result['view']['defaults']['company'], tarobj1.company.id)
            self.assertEqual(result['view']['defaults']['formmode'], 'n')
            self.assertEqual(result['view']['defaults']['partymethod'], 'n')
            self.assertEqual(result['view']['defaults']['cal_create'], True)
            self.assertEqual(result['view']['defaults']['cal_titlefmt'], '0')
            
            # create party
            Party = pool.get('party.party')
            party, = Party.create([{
                        'name': 'Frida',
                        'addresses': [('create', [{'zip':'12345', 'city':'Berlin', 'street': 'Color Street 1'}])],
                        'contact_mechanisms': [('create', [
                                    {'type':'phone', 'value': '0123-456789'},
                                    {'type':'email', 'value': 'frida@heaven.org'}
                                ])],
                        }])
            p_lst = Party.search([('name', '=', 'Frida')])
            self.assertEqual(len(p_lst), 1)
            self.assertEqual(p_lst[0].name, 'Frida')
    
            # select party
            w_obj.start.pty_sel = p_lst[0]
            w_obj.start.on_change_pty_sel()
            r1 = {}
            l1 = ['pty_name', 'pty_address', 'pty_zip', 'pty_city', 'pty_country', 'pty_subdivision',
                'pty_phone', 'pty_mobile', 'pty_fax', 'pty_email']
            for i in l1:
                r1[i] = getattr(w_obj.start, i)
    
            self.assertEqual(w_obj.start.pty_name, 'Frida')
            self.assertEqual(w_obj.start.pty_address, 'Color Street 1')
            self.assertEqual(w_obj.start.pty_zip, '12345')
            self.assertEqual(w_obj.start.pty_city, 'Berlin')
            self.assertEqual(w_obj.start.pty_phone, '0123-456789')
            self.assertEqual(w_obj.start.pty_email, 'frida@heaven.org')
            self.assertEqual(w_obj.start.pty_fax, '')
            self.assertEqual(w_obj.start.pty_mobile, '')
            self.assertEqual(w_obj.start.empl_sel, None)

            # calendar
            w_obj.start.cal_create = True
            w_obj.start.cal_titlefmt = '0'
            w_obj.start.cal_titletext = 'Holiday'
            l1 = ['cal_create', 'cal_titlefmt', 'cal_titletext']
            for i in l1:
                r1[i] = getattr(w_obj.start, i)

            r1.update({
                'company': tarobj1.company.id,
                'pty_sel': w_obj.start.pty_sel.id,
                # form
                'formmode': 'n',
                'partymethod': 'e',
                # employee
                'startdate': date(2000, 10, 1),
                'enddate': None,
                'tariff': tarobj1.id,
                'worktime': None,
                'holidays': 22,
                'specleave': 2,
                'empl_sel': None,
                # user
                'usr_ena': True,
                'usr_sel': None,
                'usr_login': 'frida',
                'usr_passwd': 'test1234',
            })
    
            EmployeeWizard.execute(sess_id, {
                    start_state: r1
                }, 'saveemployee')
    
            # check result
            Employee = pool.get('company.employee')
            User = pool.get('res.user')
            e_lst = Employee.search([
                        ('company', '=', tarobj1.company),
                        ('party.name', '=', 'Frida'),
                    ])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].party.name, 'Frida')
            # address
            self.assertEqual(len(e_lst[0].party.addresses), 1)
            self.assertEqual(e_lst[0].party.addresses[0].zip, '12345')
            self.assertEqual(e_lst[0].party.addresses[0].city, 'Berlin')
            # contact
            self.assertEqual(len(e_lst[0].party.contact_mechanisms), 2)
            self.assertEqual(e_lst[0].party.phone, '0123-456789')
            self.assertEqual(e_lst[0].party.email, 'frida@heaven.org')
            # employee
            self.assertEqual(str(e_lst[0].start_date), '2000-10-01')
            self.assertEqual(e_lst[0].holidays, 22)
            self.assertEqual(e_lst[0].tariff.name, 'Tariff1')
            # user
            usr_lst = User.search([('employee', '=', e_lst[0])])
            self.assertEqual(len(usr_lst), 1)
            self.assertEqual(usr_lst[0].name, 'Frida')
            self.assertEqual(usr_lst[0].login, 'frida')

    @with_transaction()
    def test_employee_wizard_create_new(self):
        """ test: create new employee + party
        """
        # prepare tariff
        pool = Pool()
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        
        # prepare working time model
        wtmodel = create_worktime_full(tarobj1.company, 'WT1', 'W1', [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':False, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
                {'name':'WTR2', 'mon':False, 'tue':False, 'wed':False, 'thu':True, 
                 'fri':False, 'sat':False, 'sun':False, 'mintime':time(9,0), 'maxtime':time(17, 0)},
            ])
        self.assertTrue(wtmodel)
        self.assertEqual(wtmodel.name, 'WT1')
        self.assertEqual(wtmodel.shortname, 'W1')
        self.assertEqual(len(wtmodel.worktimerule), 2)
        
        with set_company(tarobj1.company):
            transaction = Transaction()
            
            # start wizard
            EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
            (sess_id, start_state, end_state) = EmployeeWizard.create()
            w_obj = EmployeeWizard(sess_id)
            self.assertEqual(start_state, 'start')
    
            # setup form
            transaction.set_context(active_model='ir.ui.menu')
            result = EmployeeWizard.execute(sess_id, {}, start_state)
            self.assertEqual(list(result.keys()), ['view'])
            self.assertEqual(result['view']['defaults']['company'], tarobj1.company.id)
            self.assertEqual(result['view']['defaults']['formmode'], 'n')
            self.assertEqual(result['view']['defaults']['partymethod'], 'n')
            self.assertEqual(result['view']['defaults']['cal_create'], True)
            self.assertEqual(result['view']['defaults']['cal_titlefmt'], '0')

            # fill form and klick create-button
            EmployeeWizard.execute(sess_id, {
                    start_state: {
                        'company': tarobj1.company.id,
                        # form
                        'formmode': 'n',
                        'partymethod': 'n',
                        # party
                        'pty_name':'Frida',
                        'pty_address': 'Color Street 1',
                        'pty_zip': '12345',
                        'pty_city': 'Berlin',
                        'pty_phone': '0123-456789',
                        'pty_email': 'frida@heaven.org',
                        'pty_mobile': '',
                        'pty_fax': '',
                        'pty_country': None,
                        'pty_subdivision': None,
                        # employee
                        'startdate': date(2000, 10, 1),
                        'enddate': None,
                        'tariff': tarobj1.id,
                        'worktime': wtmodel.id,
                        'holidays': 22,
                        'specleave': 2,
                        'empl_sel': None,
                        # user
                        'usr_ena': True,
                        'usr_sel': None,
                        'usr_login': 'frida',
                        'usr_passwd': 'test1234',
                        # calendar
                        'cal_create': True,
                        'cal_titlefmt': '0',
                        'cal_titletext': 'Holiday',
                    }
                }, 'saveemployee')
            
            # check result
            Employee = pool.get('company.employee')
            User = pool.get('res.user')
            e_lst = Employee.search([
                        ('company', '=', tarobj1.company),
                        ('party.name', '=', 'Frida'),
                    ])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].party.name, 'Frida')
            # address
            self.assertEqual(len(e_lst[0].party.addresses), 1)
            self.assertEqual(e_lst[0].party.addresses[0].zip, '12345')
            self.assertEqual(e_lst[0].party.addresses[0].city, 'Berlin')
            # contact
            self.assertEqual(len(e_lst[0].party.contact_mechanisms), 2)
            self.assertEqual(e_lst[0].party.phone, '0123-456789')
            self.assertEqual(e_lst[0].party.email, 'frida@heaven.org')
            # employee
            self.assertEqual(str(e_lst[0].start_date), '2000-10-01')
            self.assertEqual(e_lst[0].holidays, 22)
            self.assertEqual(e_lst[0].tariff.name, 'Tariff1')
            self.assertEqual(e_lst[0].worktime.name, 'WT1')
            # user
            usr_lst = User.search([('employee', '=', e_lst[0])])
            self.assertEqual(len(usr_lst), 1)
            self.assertEqual(usr_lst[0].name, 'Frida')
            self.assertEqual(usr_lst[0].login, 'frida')
        
    @with_transaction()
    def test_employee_wizard_create_new2(self):
        """ test: create new employee + party
        """
        # prepare tariff
        pool = Pool()
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        
        # prepare working time model
        wtmodel = create_worktime_full(tarobj1.company, 'WT1', 'W1', [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':False, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
                {'name':'WTR2', 'mon':False, 'tue':False, 'wed':False, 'thu':True, 
                 'fri':False, 'sat':False, 'sun':False, 'mintime':time(9,0), 'maxtime':time(17, 0)},
            ])
        self.assertTrue(wtmodel)
        self.assertEqual(wtmodel.name, 'WT1')
        self.assertEqual(wtmodel.shortname, 'W1')
        self.assertEqual(len(wtmodel.worktimerule), 2)
        
        with set_company(tarobj1.company):
            transaction = Transaction()
            
            # start wizard
            EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
            (sess_id, start_state, end_state) = EmployeeWizard.create()
            w_obj = EmployeeWizard(sess_id)
            self.assertEqual(start_state, 'start')
    
            # setup form
            transaction.set_context(active_model='ir.ui.menu')
            result = EmployeeWizard.execute(sess_id, {}, start_state)
            self.assertEqual(list(result.keys()), ['view'])
            self.assertEqual(result['view']['defaults']['company'], tarobj1.company.id)
            self.assertEqual(result['view']['defaults']['formmode'], 'n')
            self.assertEqual(result['view']['defaults']['partymethod'], 'n')
            self.assertEqual(result['view']['defaults']['cal_create'], True)
            self.assertEqual(result['view']['defaults']['cal_titlefmt'], '0')
            
            # setup fields from defaults
            for i in result['view']['defaults'].keys():
                setattr(w_obj.start, i, result['view']['defaults'][i])

            # enable create tryton user
            w_obj.start.usr_ena = True
            w_obj.start.on_change_usr_ena()
            # new tryton user
            w_obj.start.usr_method = USER_METHOD_NEW
            w_obj.start.on_change_usr_method()

            w_obj.start.usr_login = 'frida'
            w_obj.start.usr_passwd = 'test1234'

            # setup calendar
            w_obj.start.cal_titlefmt = CALTITL_HOLIDAYS
            w_obj.start.on_change_cal_titlefmt()
            
            # setup party
            w_obj.start.pty_name = 'Frida'
            w_obj.start.on_change_pty_name()
            w_obj.start.pty_address = 'Color Street 1'
            w_obj.start.pty_zip = '12345'
            w_obj.start.pty_city = 'Berlin'
            w_obj.start.pty_phone = '0123-456789'
            w_obj.start.pty_email = 'frida@heaven.org'
            w_obj.start.pty_mobile = ''
            w_obj.start.pty_fax = ''
            w_obj.start.pty_country = None
            w_obj.start.on_change_pty_country()

            # setup employee
            w_obj.start.startdate = date(2000, 10, 1)
            w_obj.start.enddate = None
            w_obj.start.tariff = tarobj1.id
            w_obj.start.worktime = wtmodel.id
            w_obj.start.holidays = 22
            w_obj.start.specleave = 2

            r1 = {}
            for i in w_obj.start._fields.keys():
                r1[i] = getattr(w_obj.start, i, None)

            # check content of form
            self.assertEqual(r1['company'], tarobj1.company)
            self.assertEqual(r1['formmode'], 'n')
            self.assertEqual(r1['usr_ena'], True)
            self.assertEqual(r1['usr_sel'], None)
            self.assertEqual(r1['usr_login'], 'frida')
            self.assertEqual(r1['usr_passwd'], 'test1234')
            self.assertEqual(r1['cal_create'], True)
            self.assertEqual(r1['cal_titlefmt'], '1')
            self.assertEqual(r1['cal_titletext'], 'Holidays')
            self.assertEqual(r1['partymethod'], 'n')
            self.assertEqual(r1['pty_name'], 'Frida')
            self.assertEqual(r1['pty_address'], 'Color Street 1')
            self.assertEqual(r1['pty_zip'], '12345')
            self.assertEqual(r1['pty_city'], 'Berlin')
            self.assertEqual(r1['pty_phone'], '0123-456789')
            self.assertEqual(r1['pty_email'], 'frida@heaven.org')
            self.assertEqual(r1['pty_mobile'], '')
            self.assertEqual(r1['pty_fax'], '')
            self.assertEqual(r1['pty_country'], None)
            self.assertEqual(r1['pty_subdivision'], None)
            self.assertEqual(r1['startdate'], date(2000, 10, 1))
            self.assertEqual(r1['enddate'], None)
            self.assertEqual(r1['tariff'], tarobj1)
            self.assertEqual(r1['worktime'], wtmodel)
            self.assertEqual(r1['holidays'], 22)
            self.assertEqual(r1['specleave'], 2)
            self.assertEqual(r1['empl_sel'], None)

            # fill form and klick create-button
            EmployeeWizard.execute(sess_id, {
                    start_state: r1,
                }, 'saveemployee')

            # check result
            Employee = pool.get('company.employee')
            User = pool.get('res.user')
            e_lst = Employee.search([
                        ('company', '=', tarobj1.company),
                        ('party.name', '=', 'Frida'),
                    ])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].party.name, 'Frida')
            # address
            self.assertEqual(len(e_lst[0].party.addresses), 1)
            self.assertEqual(e_lst[0].party.addresses[0].zip, '12345')
            self.assertEqual(e_lst[0].party.addresses[0].city, 'Berlin')
            # contact
            self.assertEqual(len(e_lst[0].party.contact_mechanisms), 2)
            self.assertEqual(e_lst[0].party.phone, '0123-456789')
            self.assertEqual(e_lst[0].party.email, 'frida@heaven.org')
            # employee
            self.assertEqual(str(e_lst[0].start_date), '2000-10-01')
            self.assertEqual(e_lst[0].holidays, 22)
            self.assertEqual(e_lst[0].tariff.name, 'Tariff1')
            self.assertEqual(e_lst[0].worktime.name, 'WT1')
            # user
            usr_lst = User.search([('employee', '=', e_lst[0])])
            self.assertEqual(len(usr_lst), 1)
            self.assertEqual(usr_lst[0].name, 'Frida')
            self.assertEqual(usr_lst[0].login, 'frida')

    @with_transaction()
    def test_employee_wizard_calendar(self):
        """ test: create/edit calendar
        """
        # prepare tariff
        pool = Pool()
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[],
                type_work = 'Work',
            )
        self.assertTrue(tarobj1)
        
        # prepare working time model
        wtmodel = create_worktime_full(tarobj1.company, 'WT1', 'W1', [
                {'name':'WTR1', 'mon':True, 'tue':True, 'wed':True, 'thu':False, 
                 'fri':True, 'sat':False, 'sun':False, 'mintime':time(8,0), 'maxtime':time(16, 0)},
                {'name':'WTR2', 'mon':False, 'tue':False, 'wed':False, 'thu':True, 
                 'fri':False, 'sat':False, 'sun':False, 'mintime':time(9,0), 'maxtime':time(17, 0)},
            ])
        self.assertTrue(wtmodel)
        self.assertEqual(wtmodel.name, 'WT1')
        self.assertEqual(wtmodel.shortname, 'W1')
        self.assertEqual(len(wtmodel.worktimerule), 2)
        
        with set_company(tarobj1.company):
            transaction = Transaction()
            
            # start wizard
            EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
            (sess_id, start_state, end_state) = EmployeeWizard.create()
            w_obj = EmployeeWizard(sess_id)
            self.assertEqual(start_state, 'start')
    
            # setup form
            transaction.set_context(active_model='ir.ui.menu')
            result = EmployeeWizard.execute(sess_id, {}, start_state)
            self.assertEqual(list(result.keys()), ['view'])
            self.assertEqual(result['view']['defaults']['company'], tarobj1.company.id)
            self.assertEqual(result['view']['defaults']['formmode'], 'n')
            self.assertEqual(result['view']['defaults']['partymethod'], 'n')
            self.assertEqual(result['view']['defaults']['cal_create'], True)
            self.assertEqual(result['view']['defaults']['cal_titlefmt'], '0')

            # fill form and klick create-button
            EmployeeWizard.execute(sess_id, {
                    start_state: {
                        'company': tarobj1.company.id,
                        # form
                        'formmode': 'n',
                        'partymethod': 'n',
                        # party
                        'pty_name':'Frida',
                        'pty_address': 'Color Street 1',
                        'pty_zip': '12345',
                        'pty_city': 'Berlin',
                        'pty_phone': '0123-456789',
                        'pty_email': 'frida@heaven.org',
                        'pty_mobile': '',
                        'pty_fax': '',
                        'pty_country': None,
                        'pty_subdivision': None,
                        # employee
                        'startdate': date(2000, 10, 1),
                        'enddate': None,
                        'tariff': tarobj1.id,
                        'worktime': wtmodel.id,
                        'holidays': 22,
                        'specleave': 2,
                        'empl_sel': None,
                        # user
                        'usr_ena': True,
                        'usr_sel': None,
                        'usr_login': 'frida',
                        'usr_passwd': 'test1234',
                        # calendar
                        'cal_create': True,
                        'cal_titlefmt': '6',
                        'cal_titletext': 'Holiday',
                    }
                }, 'saveemployee')
            
            # check result
            Employee = pool.get('company.employee')
            e_lst = Employee.search([
                        ('company', '=', tarobj1.company),
                        ('party.name', '=', 'Frida'),
                    ])
            self.assertEqual(len(e_lst), 1)
            self.assertEqual(e_lst[0].party.name, 'Frida')
            self.assertEqual(e_lst[0].calendar.name, 'Holiday')

            # delete wizard
            EmployeeWizard.delete(sess_id)

            with transaction.set_context({
                    'active_model': 'company.employee',
                    'active_ids': [e_lst[0].id],
                }):
                EmployeeWizard = pool.get('employee_timetracking.wizemployee_create', type='wizard')
                (sess_id, start_state, end_state) = EmployeeWizard.create()
                w_obj = EmployeeWizard(sess_id)
                self.assertEqual(start_state, 'start')
                
                # employee 'Frida' should be loaded
                result = EmployeeWizard.execute(sess_id, {}, start_state)
                self.assertEqual(list(result.keys()), ['view'])

                self.assertEqual(result['view']['defaults']['formmode'], 'e')
                self.assertEqual(result['view']['defaults']['partymethod'], 'e')
                self.assertEqual(result['view']['defaults']['cal_create'], False)
                
                r1 = {}
                for i in result['view']['defaults'].keys():
                    setattr(w_obj.start, i, result['view']['defaults'][i])
                    r1[i] = result['view']['defaults'][i]

                # try to delete calendar
                r1['cal_sel'] = None
                self.assertRaisesRegex(UserError,
                    'Deleting calendar from employee is not allowed.',
                    EmployeeWizard.execute,
                    sess_id,
                    {start_state: r1},
                    'saveemployee')

                # replace calendar
                r1['cal_create'] = True
                r1['cal_titlefmt'] = '6'
                r1['cal_titletext'] = 'Holiday2'
                self.assertEqual(e_lst[0].calendar.name, 'Holiday')
                EmployeeWizard.execute(sess_id, {start_state: r1}, 'saveemployee')
                self.assertEqual(e_lst[0].calendar.name, 'Holiday2')

                # switch to other calendar
                Calendar = Pool().get('pim_calendar.calendar')
                cal2 = Calendar(
                        name='Holiday3', 
                        owner=result['view']['defaults']['usr_sel'],
                        allday_events= True,
                    )
                cal2.save()
                r1['cal_create'] = False
                r1['cal_sel'] = cal2.id
                self.assertEqual(e_lst[0].calendar.name, 'Holiday2')
                EmployeeWizard.execute(sess_id, {start_state: r1}, 'saveemployee')
                self.assertEqual(e_lst[0].calendar.name, 'Holiday3')

# end EmployeeWizardTestCase
