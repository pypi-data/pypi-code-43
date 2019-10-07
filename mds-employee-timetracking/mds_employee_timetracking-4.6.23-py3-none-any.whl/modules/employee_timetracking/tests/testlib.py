# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.employee_timetracking.const import ACRULE_HOLIDAY_NODEF


def create_holiday(name, date1, company, repyear=False, halfday=False):
    Holiday = Pool().get('employee_timetracking.holiday')
    
    hobj = Holiday(
            name=name,
            date=date1, 
            company=company, 
            repyear=repyear,
            halfday=halfday
        )
    hobj.save()
    return hobj
# end create_holiday


def create_worktime_full(company, name, shortname, rules=[]):
    """ create worktime model + rules
    """
    pool = Pool()
    WorkTimeModel = pool.get('employee_timetracking.worktimemodel')
    WorkTimeRule = pool.get('employee_timetracking.worktimerule')
    
    lst_rules = []
    for i in rules:
        lst_rules.append(WorkTimeRule(
            name=i['name'],
            mon=i['mon'], tue=i['tue'], wed=i['wed'], thu=i['thu'],
            fri=i['fri'], sat=i['sat'], sun=i['sun'],
            mintime=i['mintime'], maxtime=i['maxtime']))
        
    wt_obj = WorkTimeModel(
            name=name,
            shortname=shortname,
            company=company,
            worktimerule=lst_rules,
        )
    wt_obj.save()
    return wt_obj

# end create_worktime_full


def create_worktimemodel(name, shortname, company):
    """ create working time model
    """
    WorkTimeModel = Pool().get('employee_timetracking.worktimemodel')
    wt_obj = WorkTimeModel(
            name=name,
            shortname=shortname,
            company=company
        )
    wt_obj.save()
    return wt_obj
# end create_worktimemodel


def create_worktimerule(wtmodel, name, para={}):
    """ create working time rule
    """
    WorkTimeRule = Pool().get('employee_timetracking.worktimerule')
    wt_obj = WorkTimeRule(
            wtmodel=wtmodel,
            name=name,
            mon=para.get('mon', WorkTimeRule.default_mon()),
            tue=para.get('tue', WorkTimeRule.default_tue()),
            wed=para.get('wed', WorkTimeRule.default_wed()),
            thu=para.get('thu', WorkTimeRule.default_thu()),
            fri=para.get('fri', WorkTimeRule.default_fri()),
            sat=para.get('sat', WorkTimeRule.default_sat()),
            sun=para.get('sun', WorkTimeRule.default_sun()),
            mintime=para.get('mintime', WorkTimeRule.default_mintime()),
            maxtime=para.get('maxtime', WorkTimeRule.default_maxtime()),
        )
    wt_obj.save()
    return wt_obj
# end create_worktimerule


def create_evaluation(employee, evaldate):
    Evaluation = Pool().get('employee_timetracking.evaluation')
    eval_obj = Evaluation(
            employee=employee,
            evaldate=evaldate,
        )
    eval_obj.save()
    Evaluation.wfcreate([eval_obj])
    return eval_obj
# end create_evaluation


def create_accountrule(name='-', shortname='-', tariff=None,\
        mon=False, tue=False, wed=False, thu=False, fri=False, sat=False, sun=False,\
        mintime=None, maxtime=None, presence=None, factor=None, account=None, 
        holiday=ACRULE_HOLIDAY_NODEF):
    AccountRule = Pool().get('employee_timetracking.accountrule')
    ar_obj = AccountRule(
            name=name,
            shortname=shortname,
            tariff=tariff,
            mon=mon, tue=tue, wed=wed, thu=thu, fri=fri,
            sat=sat, sun=sun,
            mintime=mintime, maxtime=maxtime, factor=factor,
            account=account,
            presence=presence,
            holiday=holiday,
        )
    ar_obj.save()
    return ar_obj
# end create_accountrule


def create_breaktime(name='-', shortname='-', mintime=None, maxtime=None, \
                    deduction=None, tariff=None):
    BreakTime = Pool().get('employee_timetracking.breaktime')
    br_obj = BreakTime(
            name=name,
            shortname=shortname,
            mintime=mintime,
            maxtime=maxtime,
            deduction=deduction,
            tariff=tariff,
        )
    br_obj.save()
    return br_obj
# end create_breaktime


def create_period(startpos, endpos, presence, employee):
    Period = Pool().get('employee_timetracking.period')
    
    perobj = Period(
            employee=employee,
            presence=presence, 
            startpos=startpos, 
            endpos=endpos,
            state=Period.default_state()
        )
    perobj.save()
    return perobj
# end create_period



def create_presence(name='-', shortname='', company=None):
    """ create a type-of-presence
    """
    Presence = Pool().get('employee_timetracking.presence')
    pr_obj = Presence(
                name=name, 
                shortname=shortname,
                company=company
                )
    pr_obj.save()
    return pr_obj
# end create_presence


def create_timeaccount(name='-', shortname='', company=None, color=None):
    """ create a time account
    """
    Account = Pool().get('employee_timetracking.timeaccount')
    col1 = color
    if isinstance(col1, type(None)):
        col1 = Account.default_color()
    
    acc_obj = Account(
                name=name, 
                shortname=shortname,
                company=company,
                color=col1,
                )
    acc_obj.save()
    return acc_obj
# end create_timeaccount


def create_timeaccountitem(employee, period, evaluation, account, accountrule, startpos, endpos):
    """ create a time account item
    """
    AccountItem = Pool().get('employee_timetracking.timeaccountitem')
    itm_obj = AccountItem(
                employee=employee, 
                period=period,
                account=account,
                accountrule=accountrule,
                startpos=startpos,
                endpos=endpos,
                evaluation=evaluation,
                )
    itm_obj.save()
    AccountItem.wfcreate([itm_obj])
    return itm_obj
# end create_timeaccountitem


def create_trytonuser(login, password):
    User = Pool().get('res.user')
    
    user, = User.create([{'name': login, 'login': login,}])
    User.write([user], {'password': password,})
    return user
# end create_trytonuser


def create_employee(company, name="Frida"):
    pool = Pool()
    Party = pool.get('party.party')
    Employee = pool.get('company.employee')

    party, = Party.create([{
                'name': name,
                'addresses': [('create', [{}])],
                }])

    employee = Employee(party=party, company=company,
                    holidays=Employee.default_holidays(),
                    specleave=Employee.default_specleave(),
                )
    employee.save()
    return employee
# end create_employee


def create_tariff(name='-', shortname='', company=None):
    """ create a tariff model
    """
    Tariff = Pool().get('employee_timetracking.tariffmodel')
    tr_obj = Tariff(
                name=name, 
                shortname=shortname,
                company=company
                )
    tr_obj.save()
    return tr_obj
# end create_tariff


def create_tariff_full(tarname='-', tarshort='-', companyname='',
        breaktimes=[{'name':'-', 'shortname':'-', 'mint':None, 'maxt':None, 'dedu':None},],
        timeaccounts=[{'name': '-', 'shortname':'-'}],
        accountrules=[{'name':'-', 'shortname':'-', 'mint':None, 'maxt':None, 'fact':None,
                'mon':False, 'tue':False, 'wed':False, 'thu':False, 'fri':False,
                'sat':False, 'sun':False, 'holiday': ACRULE_HOLIDAY_NODEF}],
        presences=[{'name':'-', 'shortname':'-', 'wotacc':None, 'hoacc':None, 'fix':None}],
        type_work=None, main_account=None
    ):
    """ create tariff with breaktime, accountrule, presence
    """
    # create a company and write new company to context
    company1 = create_company(companyname)
    with set_company(company1):
        for i in timeaccounts:
            create_timeaccount(name=i['name'], shortname=i['shortname'], company=company1)
        
        # create presence
        lst_pres = []
        for i in presences:
            pr1 = create_presence(name=i['name'], \
                        shortname=i['shortname'], \
                        company=company1)
            lst_pres.append(pr1)

        # create accountrules
        lst_ovr = []
        pool = Pool()
        TimeAccount = pool.get('employee_timetracking.timeaccount')
        Presence = pool.get('employee_timetracking.presence')
        
        tarobj1 = create_tariff(name=tarname, shortname=tarshort, \
                        company=company1)

        for i in accountrules:
            t_lst = TimeAccount.search([('company', '=', company1), ('name', '=', i['account'])])
            if len(t_lst) != 1:
                raise Exception(u't_lst != 1')
            p_lst = Presence.search([('name', '=', i['presence']), ('company', '=', company1)])
            if len(p_lst) != 1:
                raise Exception(u'p_lst != 1')

            ovr1 = create_accountrule(name=i['name'], 
                        shortname=i['shortname'], \
                        mintime=i['mint'], maxtime=i['maxt'],
                        factor=i['fact'], holiday=i['holiday'],
                        mon=i['mon'], tue=i['tue'], wed=i['wed'], thu=i['thu'],
                        fri=i['fri'], sat=i['sat'], sun=i['sun'], tariff=tarobj1,
                        presence=p_lst[0], account=t_lst[0])
            lst_ovr.append(ovr1)

        # add breaktimes, accountrule

        # create breaktimes
        for i in breaktimes:
            br1 = create_breaktime(name=i['name'], 
                        shortname=i['shortname'], 
                        mintime=i['mint'],
                        maxtime=i['maxt'],
                        deduction=i['dedu'],
                        tariff=tarobj1
                    )

        tarobj1.presence = lst_pres
        tarobj1.save()
        
        # main-time-account
        if not isinstance(main_account, type(None)):
            ta1 = TimeAccount.search([('company', '=', company1), ('name', '=', main_account)])
            if len(ta1) == 1:
                tarobj1.main_timeaccount = ta1[0]
                tarobj1.save()

        # type_work
        Presence = Pool().get('employee_timetracking.presence')
        if not isinstance(type_work, type(None)):
            l1 = Presence.search([('name', '=', type_work), ('id', 'in', [x.id for x in tarobj1.presence])])
            if len(l1) == 1:
                tarobj1.type_present = l1[0]
                tarobj1.save()
        
    return tarobj1
# end create_tariff_full


def add_tryton_user(name, groupname, company=None, employee=None, set_to_current=False):
    """ create tryton user, add to group
    """
    pool = Pool()
    User = pool.get('res.user')
    Groups = pool.get('res.group')
    
    # create user
    paras = {'name': name, 'login': name}
    if not isinstance(company, type(None)):
        paras['company'] = company.id
        paras['main_company'] = company.id
    
    if not isinstance(employee, type(None)):
        paras['employees'] = [('add', [employee.id])]
        paras['employee'] = employee.id

    user, = User.create([paras])
    User.write([user], {'password': '123456789',})
    
    # add user to group
    gr1 = Groups.search(['name', '=', groupname])
    if len(gr1) == 1:
        l1 = list(gr1[0].users)
        l1.append(user)
        gr1[0].users = l1
        gr1[0].save()
    else :
        raise ValueError("Group '%s' not found" % groupname)
    
    if set_to_current == True:
        Transaction().set_user(user.id)

    return user
    
# end add_tryton_user
