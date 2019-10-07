# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


# accountrule
# - the accountrule determines the factor with which the actual 
#   hours worked are calculated on the working time account
# - decides on which time account the working hours are written

from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id
from trytond.transaction import Transaction
from datetime import time, datetime, timedelta, date
from decimal import Decimal
from trytond import backend
import pytz, copy, logging
from .period import WF_PERIOD_LOCK, WF_PERIOD_EXAMINE
from .const import WF_ACCOUNT_EXAMINE, WF_ACCOUNT_CREATED, sel_accrule_holiday, \
    ACRULE_HOLIDAY_NODEF, ACRULE_HOLIDAY_AT, ACRULE_HOLIDAY_NOTAT

logger = logging.getLogger(__name__)


__all__ = ['AccountRule']
__metaclass__ = PoolMeta


class AccountRule(ModelSQL, ModelView):
    'Account rule'
    __name__ = 'employee_timetracking.accountrule'

    tariff = fields.Many2One(string=u'Tariff model', required=True, select=True,
        model_name='employee_timetracking.tariffmodel', ondelete='CASCADE')
    company = fields.Function(fields.Many2One(string='Company', readonly=True,
            model_name='company.company', states={'invisible': True}), 
            'on_change_with_company', searcher='search_company')
    name = fields.Char(string=u'Name', required=True)
    shortname = fields.Char(string=u'shorthand symbol', required=True, size=4,
                help=u'The shorthand symbol appears in the tables of the reports.')
    mon = fields.Boolean(string=u'Mon', help=u'rule applies at Monday')
    tue = fields.Boolean(string=u'Tue', help=u'rule applies at Tuesday')
    wed = fields.Boolean(string=u'Wed', help=u'rule applies at Wednesday')
    thu = fields.Boolean(string=u'Thu', help=u'rule applies at Thursday')
    fri = fields.Boolean(string=u'Fri', help=u'rule applies at Friday')
    sat = fields.Boolean(string=u'Sat', help=u'rule applies at Saturday')
    sun = fields.Boolean(string=u'Sun', help=u'rule applies at Sunday')
    holiday = fields.Selection(string=u'Holiday', 
        help=u'Rule is only used on public holidays or not on public holidays',
        selection=sel_accrule_holiday)
    # time is used in localtime of the company
    mintime = fields.Time(string=u'from', required=True,
                help=u'Begin time from which the rule applies.')
    maxtime = fields.Time(string=u'to', required=True,
                help=u'End time until which the rule applies.')
    factor = fields.Numeric(string=u'Factor', required=True,
                help=u'Factor for working hours while the rule applies')
    presence = fields.Many2One(string=u'Type of presence', depends=['company'],
        help=u'Presence type for which the rule applies',
        model_name='employee_timetracking.presence',
        required=True, ondelete='RESTRICT', 
        domain=[('company', '=', Eval('company', None)),])
    account = fields.Many2One(string=u'Time Account', depends=['company'], select=True,
        help=u'Time account on which a suitable presence time is booked.',
        model_name='employee_timetracking.timeaccount', required=True, ondelete='RESTRICT',
        domain=[('company', '=', Eval('company', None)),])

    @classmethod
    def __register__(cls, module_name):
        super(AccountRule, cls).__register__(module_name)
        cls.migrate_contraints(module_name)
        cls.migrate_columns(module_name)

    @classmethod
    def migrate_columns(cls, modul_name):
        """ x.x.9: - dropy column 'company'
                   - link to table tariff
        """
        pool = Pool()
        TimeAccountItem = pool.get('employee_timetracking.timeaccountitem')
        TableHandler = backend.get('TableHandler')
        Employee = pool.get('company.employee')
        AccountRule = pool.get('employee_timetracking.accountrule')

        table = TableHandler(cls, modul_name)
        tab_tai = TimeAccountItem.__table__()
        tab_empl = Employee.__table__()

        # drop company
        if table.column_exist('company'):
            table.drop_column('company')
            logger.warning('deleted column "company" on table "accountrule"')

        # link to tariff
        if table.table_exist('employee_timetracking_accountrule_rel'):
            cursor = Transaction().connection.cursor()
            transaction = Transaction()
            tab_accrule = cls.__table__()
            
            to_delete_accrules = []         # ids of accountrule-records
            to_delete_accrule_rels = []     # ids of relation-records
            
            # prepare columns to copy to the new record
            cols1 = list(cls._fields.keys())
            for i in ['id', 'tariff', 'company', 'rec_name']:
                cols1.remove(i)
            acr_columns = [getattr(tab_accrule, x) for x in cols1]
            acr_columns2 = [getattr(tab_accrule, x) for x in cols1]
            acr_columns2.append(tab_accrule.tariff)

            # get existing relation records between accountrule and tariff
            qu1 = "select id, tariff, accountrule from employee_timetracking_accountrule_rel"
            cursor.execute(qu1)
            l1 = cursor.fetchall()
            for i in l1:
                (id_rel, id_tariff, id_accrule) = i

                # read accountrule
                qu1 = tab_accrule.select(
                        *acr_columns,
                        where=(tab_accrule.id == id_accrule)
                    )
                cursor.execute(*qu1)
                l2 = cursor.fetchall()
                if len(l2) != 1:
                    raise ValueError('failed to read record')

                # prepare data to write, append tariff-id
                acr_vals = list(l2[0])
                acr_vals.append(id_tariff)  # append tariff-id
                acr_vals = tuple(acr_vals)

                # write new accountrule to table
                dbretval = None
                if transaction.database.has_returning():
                    dbretval = [tab_accrule.id]
                else :
                    raise ValueError('missing returning in database')

                qu2 = tab_accrule.insert(
                        columns=acr_columns2,
                        values=[acr_vals],
                        returning=dbretval
                    )
                cursor.execute(*qu2)
                if cursor.rowcount != 1:
                    raise ValueError('failing to convert tariff-accountrule-link')

                # get id of new written record
                id_new = None
                for k in cursor:
                    (id_new, ) = k
                if isinstance(id_new, type(None)):
                    raise ValueError('failing to update time account items')

                # move time-account-items to new rule
                qu3 = tab_tai.join(tab_empl, condition=tab_tai.employee == tab_empl.id
                        ).select(tab_tai.id,
                            where=(
                                (tab_tai.accountrule == id_accrule) &
                                (tab_empl.tariff == id_tariff)
                                )
                        )
                qu4 = tab_tai.update(
                        columns = [tab_tai.accountrule],
                        values = [id_new],
                        where=tab_tai.id.in_(qu3)
                    )
                cursor.execute(*qu4)
                to_delete_accrule_rels.append(id_rel)

                if not id_accrule in to_delete_accrules:
                    to_delete_accrules.append(id_accrule)

            # cleanup db
            qu_del = "delete from employee_timetracking_accountrule_rel where id in %s" % \
                str(tuple(to_delete_accrule_rels)).replace(',)', ')')
            cursor.execute(qu_del)
            logging.warning('deleted %s records from table "employee_timetracking_accountrule_rel"' % \
                len(to_delete_accrule_rels))

            cls.delete([AccountRule(x) for x in to_delete_accrules])
            logging.warning('deleted %s records from table "accountrule"' % len(to_delete_accrules))

            table.drop_table(
                model='employee_timetracking.accountrule_rel',
                table='employee_timetracking_accountrule_rel')

    @classmethod
    def migrate_contraints(cls, module_name):
        """ delete some checks
        """
        TableHandler = backend.get('TableHandler')
        table = TableHandler(cls, module_name)
        table.drop_constraint('uniq_name')
        table.drop_constraint('uniq_short')

    @classmethod
    def __setup__(cls):
        super(AccountRule, cls).__setup__()
        tab_accountrule = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name2', 
            Unique(tab_accountrule, tab_accountrule.name, tab_accountrule.tariff), 
            u'This name is already in use.'),
            ('uniq_short2', 
            Unique(tab_accountrule, tab_accountrule.shortname, tab_accountrule.tariff), 
            u'This shorthand symbol is already in use.'),
            ('no_zerofactor',
            Check(tab_accountrule, tab_accountrule.factor != 0),
            u'Factor can not be zero.'),
            ('order', 
            Check(tab_accountrule, 
                ((tab_accountrule.mintime < tab_accountrule.maxtime) & 
                 (tab_accountrule.maxtime != '00:00:00')) | (tab_accountrule.maxtime == '00:00:00')), 
            u"'to' must be creater than 'from'"),
            ('weekday',
            Check(tab_accountrule, (tab_accountrule.mon == True) | (tab_accountrule.tue == True) | \
                                (tab_accountrule.wed == True) | (tab_accountrule.thu == True) | \
                                (tab_accountrule.fri == True) | (tab_accountrule.sat == True) | \
                                (tab_accountrule.sun == True)),
            u'at least one weekday must be activated'),
            ])

    @classmethod
    def default_holiday(cls):
        """ not-set
        """
        return ACRULE_HOLIDAY_NODEF

    @classmethod
    def default_mintime(cls):
        """ default: 8:00
        """
        return time(8, 0, 0)

    @classmethod
    def default_maxtime(cls):
        """ default: 16:00:00
        """
        return time(16, 0, 0)

    @classmethod
    def default_factor(cls):
        """ default: 1
        """
        return Decimal('1.0')

    @classmethod
    def default_mon(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_tue(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_wed(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_thu(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_fri(cls):
        """ default: True
        """
        return True

    @classmethod
    def default_sat(cls):
        """ default: True
        """
        return False

    @classmethod
    def default_sun(cls):
        """ default: True
        """
        return False

    @classmethod
    def default_company(cls):
        """ set active company to default
        """
        context = Transaction().context
        return context.get('company')

    @fields.depends('tariff')
    def on_change_with_company(self, name=None):
        if not isinstance(self.tariff, type(None)):
            return self.tariff.company.id
        else :
            return None

    @classmethod
    def search_company(cls, name, clause):
        """ search in company
        """
        return [('tariff.company',) + tuple(clause[1:])]

    @classmethod
    def match_holiday_rule(cls, accountrule, tstamp):
        """ check if tstamp matches to holiday-setting
        """
        Holiday = Pool().get('employee_timetracking.holiday')
        
        if accountrule.holiday == ACRULE_HOLIDAY_NODEF:
            # not defined --> True
            return True
        elif accountrule.holiday in [ACRULE_HOLIDAY_AT, ACRULE_HOLIDAY_NOTAT]:
            # check if there is a holiday for this timestamp
            dt1 = date(tstamp.year, tstamp.month, tstamp.day)
            # True --> tstamp is holiday
            rc1 = Holiday.is_holiday(dt1, accountrule.company)
            if accountrule.holiday == ACRULE_HOLIDAY_AT:
                return rc1
            else :
                return not rc1
        else :
            logger.error("wrong value in 'holiday': %s" % accountrule.holiday)
        
    @classmethod
    def is_in_weekdays(cls, accountrule, tstamp):
        """ check if weekday of tstamp match to accountrule
        """
        wkday = []
        if accountrule.mon == True:
            wkday.append(0)
        if accountrule.tue == True:
            wkday.append(1)
        if accountrule.wed == True:
            wkday.append(2)
        if accountrule.thu == True:
            wkday.append(3)
        if accountrule.fri == True:
            wkday.append(4)
        if accountrule.sat == True:
            wkday.append(5)
        if accountrule.sun == True:
            wkday.append(6)
        if tstamp.weekday() in wkday:
            return True
        else :
            return False
    
    @classmethod
    def get_localtime(cls, timestmp,  timezone='UTC'):
        """ timestmp: datetime in UTC from DB,
            timezone: valid time zone string from pytz: UTC, Europe/Berlin, ...
            return: datetime in localtime without time zone info
        """
        if isinstance(timezone, type(None)):
            timezone = 'UTC'

        tzutc = pytz.timezone('UTC')
        tzloc = pytz.timezone(timezone)
        dt1_utc = tzutc.localize(timestmp)
        dt1_loc = dt1_utc.astimezone(tzloc)
        return datetime(
                dt1_loc.year, dt1_loc.month, dt1_loc.day, 
                dt1_loc.hour, dt1_loc.minute, dt1_loc.second
            )

    @classmethod
    def get_utctime(cls, timestmp,  timezone='UTC'):
        """ timestmp: datetime in localtime without time zone info,
            timezone: valid time zone string from pytz: UTC, Europe/Berlin, ...
            return: datetime in UTC without time zone info
        """
        if isinstance(timezone, type(None)):
            timezone = 'UTC'

        tzloc = pytz.timezone(timezone)
        tzutc = pytz.timezone('UTC')
        dt1_loc = tzloc.localize(timestmp)
        dt1_utc = dt1_loc.astimezone(tzutc)
        return datetime(
                dt1_utc.year, dt1_utc.month, dt1_utc.day, 
                dt1_utc.hour, dt1_utc.minute, dt1_utc.second
            )

    @classmethod
    def get_periods_to_check_by_rule(cls, accountrule, startpos, endpos):
        """ create list of (begin, end) pairs,
            startpos, endpos = from period item in UTC,
            if period item run more than a day, we need multiple periods to match-check
            result: list of min/max-datetime-pairs to check for match,
                    datetime values are without time zone and must be used in localtime
        """
        # convert UTC --> localtime of company
        start_loc = cls.get_localtime(startpos, accountrule.tariff.company.timezone)
        end_loc = cls.get_localtime(endpos, accountrule.tariff.company.timezone)
        
        # select whole days, beginning at startpos(localtime), end at endpos(localtime)
        p_start = datetime(start_loc.year, start_loc.month, start_loc.day, 0, 0, 0)
        p_end = datetime(end_loc.year, end_loc.month, end_loc.day, 23, 59, 59)
        check_list = []
        
        # min/maxtime by accountrule
        acc_min = accountrule.mintime
        acc_max = accountrule.maxtime
        
        # 1st item at start day
        # extend the endpos by 1x second, 
        if cls.is_in_weekdays(accountrule, p_start) and cls.match_holiday_rule(accountrule, p_start):
            
            # 0:00 --> 24:00
            if acc_max == time(0, 0):
                acc_max2 = datetime(p_start.year, p_start.month, p_start.day, 23, 59, 59) + timedelta(seconds=1)
            else :
                acc_max2 = datetime(p_start.year, p_start.month, p_start.day, acc_max.hour, acc_max.minute, 0)
                
            check_list.append((
                    datetime(p_start.year, p_start.month, p_start.day, acc_min.hour, acc_min.minute, 0),
                    acc_max2,
                ))

        # more items for more days
        for i in range((p_end - p_start).days):
            p1 = datetime(p_start.year, p_start.month, p_start.day, acc_min.hour, acc_min.minute, 0) + timedelta(days=i + 1)

            if acc_max == time(0, 0):
                acc_max2 = datetime(p_start.year, p_start.month, p_start.day, 23, 59, 59) + timedelta(seconds=1)
            else :
                acc_max2 = datetime(p_start.year, p_start.month, p_start.day, acc_max.hour, acc_max.minute, 0)
            acc_max2 += timedelta(days=i + 1)

            if cls.is_in_weekdays(accountrule, p1) and cls.match_holiday_rule(accountrule, p1):
                check_list.append((p1, acc_max2))
        return check_list

    @classmethod
    def get_match_periods(cls, accountrule, startpos, endpos):
        """ get list of periods matching to account rule sections,
            datetime-pairs in UTC
            result: [(<datetime(-begin-)>, <datetime(-end-)>), ...]
        """
        if not (startpos < endpos):
            raise ValueError(u"startpos < endpos !")

        # get list of possible matching periods, datetime-pairs in localtime
        # weekdays are already checked
        check_list = cls.get_periods_to_check_by_rule(accountrule, startpos, endpos)
        
        l1 = []
        start_loc = cls.get_localtime(startpos, accountrule.tariff.company.timezone)
        end_loc = cls.get_localtime(endpos, accountrule.tariff.company.timezone)
        for i in check_list:
            (beg1, end1) = i
            beg_utc = cls.get_utctime(beg1, accountrule.tariff.company.timezone)
            end_utc = cls.get_utctime(end1, accountrule.tariff.company.timezone)

            if (beg1 <= start_loc < end1) and (beg1 < end_loc <= end1):
                # event starts and ends within a single rule section
                l1.append((startpos, endpos))
            elif (start_loc < beg1) and (beg1 < end_loc <= end1):
                # events starts before begin of rule section, ends in rule section
                l1.append((beg_utc, endpos))
            elif (beg1 <= start_loc < end1) and (end1 < end_loc):
                # event starts within rule section and ends after
                l1.append((startpos, end_utc))
            elif (start_loc < beg1) and (end1 < end_loc):
                # event starts before and ends after rule section
                l1.append((beg_utc, end_utc))
            elif (start_loc < beg1) and (end_loc <= beg1):
                # event before rule section - no match
                pass
            elif (start_loc >= end1) and (end_loc > end1):
                # event after rule section - no match
                pass
            else :
                # bug
                raise Exception(u'bug in get_match_periods(): beg=%s, end=%s, startpos=%s, endpos=%s, start_loc=%s, end_loc=%s' % \
                    (beg1, end1, startpos, endpos, start_loc, end_loc))
        return l1

    @classmethod
    def optimize_items2create(cls, itemlst, timezone='UTC'):
        """ connect entries which follow each other without a gap
            itemlst: [(datetime(<startpos>), datetime(<endpos>)), ...]
            result: reduced input list
        """
        l1 = []
        v1 = None
        for i in itemlst:
            if isinstance(v1, type(None)):
                v1 = list(i)
            else :
                # convert to local time zone
                v1_loc = cls.get_localtime(v1[1], timezone)
                i_loc = cls.get_localtime(i[0], timezone)
                
                # connect both periods if end=begin but not at midnight
                if (v1_loc == i_loc) and \
                    not ((v1_loc.hour == 0) and (v1_loc.minute == 0) and (v1_loc.second == 0)):
                    v1[1] = i[1]
                else :
                    # there is a gap or midnight
                    l1.append(tuple(v1))
                    v1 = list(i)
        if not isinstance(v1, type(None)):
            l1.append(tuple(v1))
        return l1
        
    @classmethod
    def add_item_by_rules(cls, accountrules, perioditem):
        """ check if period item matches to a rule, 
            state of period item must be in [examine, lock]
            create time account item
            return: list of created items in state 'created'
        """
        if not isinstance(accountrules, type([])) and \
            not isinstance(accountrules, type((1,2))):
            raise ValueError(u"'accountrules' --> [] !")
        pool = Pool()
        AccountItem = pool.get('employee_timetracking.timeaccountitem')
        AccountRule = pool.get('employee_timetracking.accountrule')
        Evaluation = pool.get('employee_timetracking.evaluation')

        accounts = {}
        # get periods to create time account items
        for i in accountrules:
            # presence-types must match
            if perioditem.presence.id != i.presence.id:
                continue

            items_to_create = cls.get_match_periods(i, perioditem.startpos, perioditem.endpos)
            key1 = (i.account.id, i.id)
            if key1 in accounts.keys():
                accounts[key1].extend(items_to_create)
            else :
                accounts[key1] = []
                accounts[key1].extend(items_to_create)

        # optimize items
        for i in accounts.keys():
            (id_acc, id_ar) = i
            
            ar_obj = AccountRule(id_ar)
            
            # sort by startpos
            l1 = sorted(accounts[i], key=lambda v1: v1[0])
            accounts[i] = cls.optimize_items2create(l1, ar_obj.tariff.company.timezone)

        # store to db
        l1_res = []
        for i in accounts.keys():
            (id_account, id_rule) = i
            
            for k in accounts[i]:
                (beg1, end1) = k
                a_obj = AccountItem()
                a_obj.employee = perioditem.employee
                a_obj.period = perioditem
                a_obj.account = id_account   # id of TimeAccount()
                a_obj.accountrule = id_rule
                a_obj.startpos = beg1
                a_obj.endpos = end1
                
                # select evaluation
                ar_obj = AccountRule(id_rule)
                beg_loc = cls.get_localtime(beg1, ar_obj.tariff.company.timezone)
                # get matching evaluation, use month from local time
                ev_lst = Evaluation.search([
                            ('employee', '=', perioditem.employee), 
                            ('evaldate', '=', date(beg_loc.year, beg_loc.month, 1))
                        ])
                if len(ev_lst) == 0:
                    evobj = Evaluation()
                    evobj.employee = perioditem.employee
                    evobj.evaldate = beg_loc
                    evobj.save()
                    Evaluation.wfactivate([evobj])
                    a_obj.evaluation = evobj
                else :
                    a_obj.evaluation = ev_lst[0]

                a_obj.save()
                AccountItem.wfcreate([a_obj])
                l1_res.append(a_obj)

                # mark evaluation for recalc
                a_obj.evaluation.needs_recalc = True
                a_obj.evaluation.save()
        return l1_res

    @classmethod
    def write(cls, *args):
        """ write item
        """
        actions = iter(args)
        for items, values in zip(actions, actions):
            # move seconds to 0
            l2 = ['mintime', 'maxtime']
            for i in l2:
                if i in values.keys():
                    values[i] = time(values[i].hour, values[i].minute, 0)
        super(AccountRule, cls).write(*args)

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:

            # move seconds to 0
            l2 = ['mintime', 'maxtime']
            for i in l2:
                if i in values.keys():
                    values[i] = time(values[i].hour, values[i].minute, 0)

        return super(AccountRule, cls).create(vlist)

# end AccountRule
