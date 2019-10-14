#
#    Copyright (C) 2002-2016  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import AccessControl
import json
import logging
import string
import operator
import re
import transaction
import types
from AccessControl.Permissions import view, view_management_screens,\
    manage_properties, access_contents_information
from Acquisition import aq_base
from DateTime import DateTime
from zExceptions import NotFound
from DocumentTemplate.DT_Util import html_quote
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.AdvancedQuery import And, Between, Eq, In, Le, Ge, Or, MatchRegexp
from utils import floor_date, ceiling_date, assert_currency, isDerived, correspondenceEmail, emailRecipients, download
from BLBase import ProductsDictionary, PortalContent, PortalFolder, LargePortalFolder
from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES
from Products.BastionBanking.Exceptions import UnsupportedCurrency
from Products.BastionBanking.interfaces.IPayee import IPayee
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from BLEntry import manage_addBLEntry, BLEntry
from BLTransaction import manage_addBLTransaction
from BLGlobals import EPOCH, MAXDT, ACC_TYPES
from BLAttachmentSupport import BLAttachmentSupport
from BLTaxCodeSupport import BLTaxCodeSupport
from Exceptions import PostingError, OrphanEntryError, IncorrectAmountError, LedgerError
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2

from Products.CMFCore.utils import getToolByName

from zope.interface import Interface, implementer
from interfaces.account import IAccount

from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

LOG = logging.getLogger('BLAccount')
#
# temporary hack to map new subtype field (works for UK_General/Australia...)
#
SUBTYPES = {1000: 'Current Assets',
            1500: 'Inventory Assets',
            1800: 'Capital Assets',
            2000: 'Current Liabilities',
            2200: 'Current Liabilities',
            2600: 'Long Term Liabilities',
            3300: 'Share Capital',
            3500: 'Retained Earnings',
            4000: 'Sales Revenue',
            4300: 'Consulting Revenue',
            4400: 'Other Revenue',
            5000: 'Cost of Goods Sold',
            5400: 'Payroll Expenses',
            5500: 'Taxation Expenses',
            5600: 'General and Administrative Expenses'}

#
# status's that can/should aggregate to valid txn entries
#
STATUSES = ('posted', 'reversed', 'postedreversal')
#STATUSES = ('posted',)

manage_addBLAccountForm = PageTemplateFile('zpt/add_account', globals())


def manage_addBLAccount(self, title, currency, type, subtype='', accno='',
                        tags=[], id='', description='', opened=None, REQUEST=None):
    """ an account """

    # hmmm - factory construction kills this ...
    # if accno in self.Accounts.uniqueValuesFor('accno'):
    #    raise LedgerError, 'Duplicate accno: %s' % accno

    if not id:
        id = self.nextAccountId()

    assert currency in CURRENCIES, 'Unknown currency type: %s' % currency

    account = BLAccount(id, title, description, type, subtype,
                        currency, accno or id, tags, opened)
    notify(ObjectCreatedEvent(account))

    try:
        self._setObject(id, account)
    except:
        # TODO: a messagedialogue ...
        raise

    acct = self._getOb(id)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % acct.absolute_url())

    return acct


def addBLAccount(self, id='', title='', type='Asset', subtype='Current Assets', accno='', opened=None, REQUEST=None):
    """
    Plone constructor
    """
    # hmmm - this becomes a TempFolder when plugged into portal_factories ...
    #assert self.meta_type=='BLLedger', 'wrong container type: %s != BLLedger' % self.meta_type

    account = manage_addBLAccount(self,
                                  id=id,
                                  title=title,
                                  type=type,
                                  subtype=subtype,
                                  accno=accno or id,
                                  currency=self.defaultCurrency(),
                                  opened=opened)
    return account.getId()


@implementer(IAccount, IPayee)
class BLAccount(LargePortalFolder, BLAttachmentSupport, BLTaxCodeSupport):
    """
    """
    meta_type = portal_type = 'BLAccount'


    __ac_permissions__ = (
        (access_contents_information, ('zeroAmount', 'Currencies', 'hasTag', 'allTags',
                                       'created', 'creationTime', 'controlLedgers', 'effective')),
        (view_management_screens, ('manage_statement', 'manage_btree',
                                   'manage_verify', 'manage_mergeForm', 'totBalance', 'totDate')),
        (ManageBastionLedgers, ('manage_details', 'manage_edit', 'manage_setBalance',
                                'manage_setDescriptionFromEntryAccount',
                                'manage_merge')),
        (OperateBastionLedgers, ('createTransaction', 'createEntry', 'manage_statusModify',
                                 'updateProperty', 'updateTags', 'isDeletable', 'manage_recalculateBalance')),
        (view, ('blLedger', 'blEntry', 'blTransaction', 'balance', 'total', 'debitTotal',
                'creditTotal', 'manage_emailStatement', 'jsonBalances',
                'prettyTitle', 'entryValues', 'entryIds', 'subtypes', 'modificationTime',
                'openingBalance', 'balances', 'transactionValues',
                'getBastionMerchantService', 'isFCA', 'isControl', 'payeeAmount', 'lastTransactionDate',
                'downloadQIF', 'asCSV', 'asEmail', 'asPDF', 'asXML')),
    ) + LargePortalFolder.__ac_permissions__ + BLAttachmentSupport.__ac_permissions__ + BLTaxCodeSupport.__ac_permissions__

    _properties = LargePortalFolder._properties + (
        {'id': 'base_currency', 'type': 'selection',
            'mode': 'w', 'select_variable': 'Currencies'},
        {'id': 'type',          'type': 'selection',
            'mode': 'w', 'select_variable': 'accountTypes'},
        {'id': 'subtype',       'type': 'string',    'mode': 'w', },
        {'id': 'accno',         'type': 'string',    'mode': 'w', },
        {'id': 'tags',          'type': 'lines',     'mode': 'w', },
        {'id': 'opened',        'type': 'date',      'mode': 'w', },
    )

    # Plone requirement - not used
    description = ''

    # just for emergencies ....
    manage_btree = LargePortalFolder.manage_main

    manage_options = (
        {'label': 'Statement', 'action': 'manage_statement',
         'help': ('BastionLedger', 'statement.stx')},
        {'label': 'View', 'action': '', },
        {'label': 'Details', 'action': 'manage_details',
         'help': ('BastionLedger', 'account_props.stx')},
        {'label': 'Verify', 'action': 'manage_verify', },
        {'label': 'Tax Groups', 'action': 'manage_taxcodes'},
        {'label': 'Merge', 'action': 'manage_mergeForm'},
        BLAttachmentSupport.manage_options[0],
    ) + LargePortalFolder.manage_options[1:]

    manage_statement = manage_main = PageTemplateFile(
        'zpt/view_account', globals())
    manage_details = PageTemplateFile('zpt/edit_account', globals())
    manage_mergeForm = PageTemplateFile('zpt/merge_accounts', globals())

    asXML = PageTemplateFile('zpt/xml_acct', globals())

    def __init__(self, id, title, description, type, subtype, currency, accno, tags=[], opened=None):
        LargePortalFolder.__init__(self, id)
        self.opened = floor_date(opened or DateTime())
        self._updateProperty('base_currency', currency)
        self._updateProperty('title', title)
        self.description = description
        self._updateProperty('type', type)
        self._updateProperty('subtype', subtype)
        self._updateProperty('accno', accno)
        self._updateProperty('tags', tags)

    def controlLedgers(self):
        """
        if this is a control account, then return the subsidiary ledger(s)
        """
        return map(lambda x: x.blLedger(), self.objectValues('BLControlEntry'))

    def Currencies(self):
        """
        A list of approved currencies which this account may be based
        """
        return self.aq_parent.currencies

    def accountTypes(self):
        return ACC_TYPES

    def isFCA(self):
        """
        return whether or not this is a foreign currency account - not of the same
        currency as the ledger
        """
        return self.base_currency != self.aq_parent.defaultCurrency()

    # indexing ...
    def accountId(self):
        return self.id

    def isControl(self):
        return len(self.objectIds('BLControlEntry')) > 0

    def controlEntry(self, ledgerid):
        return self._getOb(ledgerid, None)

    def creationTime(self, format='%Y-%m-%d %H:%M'):
        """
        opening date (as string)
        """
        return self.opened.strftime(format)

    def created(self):
        """
        the date the account was created (for indexing)
        """
        # return DateTime(self.CreationDate())
        return self.opened

    def updateTags(self, tags):
        """
        assign/edit tags to account
        """
        if type(tags) == types.StringType:
            tags = (tags,)
        self._updateProperty('tags', tags)
        cat = self.bastionLedger()
        cat.catalog_object(self, idxs=['tags'])

    def manage_edit(self, title, description, type, subtype, accno, tags, opened, base_currency='', REQUEST=None):
        """ """
        # only change currency if there are no entries ...
        # if base_currency and base_currency != self.base_currency and not
        # len(self):
        if base_currency and base_currency != self.base_currency:
            self._updateProperty('base_currency', base_currency)

        self.manage_changeProperties(title=title,
                                     description=description,
                                     type=type,
                                     subtype=subtype,
                                     accno=accno,
                                     tags=tags)
        if opened is not None:
            self._updateProperty('opened', opened)
        self.bastionLedger().catalog_object(self, '/'.join(self.getPhysicalPath()))
        if REQUEST is not None:
            REQUEST.set('management_view', 'Details')
            REQUEST.set('manage_tabs_message', 'Updated')
            return self.manage_details(self, REQUEST)

    def manage_merge(self, ids=[], delete=True, REQUEST=None):
        """
        move entries from nominated account(s) into this one, adjusting their postings
        and removing those account(s) from the ledger if delete
        """
        merged = 0
        ledger = self.aq_parent

        for id in ids:
            try:
                account = ledger._getOb(id)
            except:
                continue

            # we need to take a copy because otherwise we're unindexing stuff we previously
            # had just indexed with the account number changes/substitutions
            # ...
            for entry in account.entryValues():
                entry.blTransaction().manage_toggleAccount(id, self.getId())

            # remove the old account
            if delete:
                ledger._delObject(id)
            merged += 1

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'merged %i accounts' % merged)
            return self.manage_main(self, REQUEST)

    def manage_verify(self, precision=0.05, REQUEST=None):
        """
        verify the account entries have been applied correctly and are still valid

        precision defaults to 5 cents ...

        this function deliberately *does not* use the underlying object's methods
        to check this - it's supposed to independently check the underlying
        library - or consequent tamperings via the ZMI
        """
        bad_entries = []
        ledger_id = self.aq_parent.getId()
        for posted in self.entryValues():
            # if not isinstance(posted, BLEntry):
            #    raise AssertionError, posted
            try:
                txn = posted.blTransaction()
            except:
                bad_entries.append((OrphanEntryError(posted), ''))
                continue
            if txn is None:
                if posted.isControlEntry():
                    continue

                bad_entries.append((OrphanEntryError(posted), ''))
                continue

            if txn.status() not in STATUSES:
                bad_entries.append((PostingError(posted), ''))
                continue

            unposted = txn.blEntry(self.getId(), ledger_id)
            if unposted is None:
                bad_entries.append((OrphanEntryError(posted), ''))
                continue

            # find/use common currency base
            base_currency = self.base_currency

            unposted_amt = unposted.amount
            posted_amt = posted.amount

            if unposted_amt.currency() != base_currency:
                unposted_amt = unposted.amountAs(base_currency)

            if posted_amt.currency() != base_currency:
                posted_amt = posted.amountAs(base_currency)

            if abs(unposted_amt - posted_amt) > precision:
                bad_entries.append((IncorrectAmountError(posted),
                                    '%s - %s' % (unposted_amt, unposted_amt - posted_amt)))

        if REQUEST:
            if bad_entries:
                REQUEST.set('manage_tabs_message',
                            '<br>'.join(map(lambda x: "%s: %s %s" % (x[0].__class__.__name__,
                                                                     html_quote(
                                                                         str(x[0].args[0])),
                                                                     x[1]), bad_entries)))
            else:
                REQUEST.set('manage_tabs_message', 'OK')
            return self.manage_main(self, REQUEST)

        return bad_entries

    def manage_emailStatement(self, emails, message='', effective=None, REQUEST=None):
        """
        email invoice to recipients ...
        """
        good, bad = emailRecipients(self, emails)

        if bad:
            if REQUEST:
                REQUEST.set('manage_tabs_message',
                            'bad emails: %s' % ', '.join(bad))
                return self.manage_main(self, REQUEST)
            raise ValueError(', '.join(bad))

        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise ValueError('no MailHost found')

        # ensure 7-bit ??
        sender = correspondenceEmail(self.aq_parent)
        for recipient in good:
            mail_text = str(self.blaccount_template(self,
                                                    self.REQUEST,
                                                    sender=sender,
                                                    email=recipient,
                                                    effective=effective or DateTime(),
                                                    message=message))
            mailhost._send(sender, recipient, mail_text)

        if REQUEST:
            REQUEST.set('manage_tabs_message',
                        'Statement emailed to %s' % ', '.join(good))
            return self.manage_main(self, REQUEST)
        return good

    def manage_setDescriptionFromEntryAccount(self, REQUEST=None):
        """
        sometimes people stick naf transaction descriptions and this goes and applies
        underlying account title to the description - this is only used against Subsidiary Ledger postings
        """
        for entry in map(lambda x: x[1], self.entries()):
            try:
                # alright - there is most likely only one subsidiary entry in a
                # subsidiary transaction ...
                entry.title = entry.blTransaction().objectValues(
                    'BLSubsidiaryEntry')[0].Account().prettyTitle()
            except:
                pass
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _updateProperty(self, name, value):
        if name == 'base_currency':
            if not value in CURRENCIES:
                raise UnsupportedCurrency(value)
        elif name == 'accno':
            # go change it in periods (if we've got context - ie - not a ctor
            # call)
            periods = getattr(self, 'periods', None)
            if periods:
                for period in periods.periodsForLedger(self.getId()):
                    try:
                        period._getOb(self.getId()).accno = value
                    except KeyError:
                        pass
        elif name == 'opened':
            # assure no transactions prior to opening??
            if value is None:
                raise ValueError('Invalid Opening Date')

        LargePortalFolder._updateProperty(self, name, value)

    def blEntry(self, id):
        """
        return the associated entry for the BLTransaction id
        """
        # hmmm - verify CANNOT SEARCH ON LEDGER (may be subsidiary ledger
        # posting)!!
        brainz = self.bastionLedger().evalAdvancedQuery(Eq('accountId', self.getId(), filter=True) &
                                                        Eq('ledgerId', self.aq_parent.getId(), filter=True) &
                                                        Eq('transactionId', id, filter=True) &
                                                        In('meta_type', ('BLEntry', 'BLSubsidiaryEntry')))
        if brainz:
            # technically, there should *always* be just one entry ...
            return brainz[0]._unrestrictedGetObject()
        return None

    def blLedger(self):
        """
        find the BLLedger (derivative) of this account - in any circumstance
        """
        parent = self.aq_parent

        if not isDerived(parent.__class__, 'LedgerBase'):
            parent = parent.aq_parent

        return parent

    def blTransaction(self, id):
        """
        return the associated entry for the BLTransaction id
        """
        entry = self.blEntry(id)
        return entry and entry.aq_parent or None

    def balance(self, currency=None, effective=None, *args, **kw):
        """
        return the account balance in specified currency (or the base currency of the 
        account), as of date (defaults to all)
        """
        currency = currency or self.base_currency
        effective = effective or DateTime()

        if self._totValidFor(effective):
            return self.totBalance(currency)

        # darn - have to compute it ...
        return self.openingBalance(effective, currency) + \
            self.total(currency=currency, effective=(
                self.openingDate(effective), effective))  # + \
        #self._ctl_balances(effective, currency)

        #
        # TODO - remove *all* the code below !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #

        # figure out if we can use a cached beginning value
        # TODO - we could incorporate period info sums into this as well
        opening_dt = self.openingDate(effective)

        # seems that if it's on a period-boundry, opening date is rolled to
        # next day
        opening_amt = self.openingBalance(effective)

        opening_amt += self._ctl_balances(effective, currency)

        # the cached amount is sufficient ...
        if effective < opening_dt:
            if opening_amt.currency() != currency:
                pt = getToolByName(self, 'portal_bastionledger')
                return pt.convertCurrency(opening_amt, opening_dt, currency)
            return opening_amt

        if not effective:
            dtrange = (opening_dt, DateTime())
        elif isinstance(effective, DateTime):
            dtrange = (opening_dt, effective)
        elif type(effective) in (types.ListType, types.TupleType):
            dtrange = effective
        else:
            raise AttributeError(dtrange)

        if opening_amt.currency() != currency:
            pt = getToolByName(self, 'portal_bastionledger')
            total = pt.convertCurrency(opening_amt, opening_dt, currency)
        else:
            total = opening_amt

        return total + self.total(currency=currency, effective=dtrange)

    def total(self, effective=None, currency=None, status=STATUSES, query=None):
        """
        summates entries over range (or up to a date)
        """
        return self._total(effective, currency, status, query) + \
            self._ctl_totals(effective, currency, status, query)

    def _total(self, effective=None, currency=None, status=STATUSES, query=None):
        """
        summation over date range - without control entries
        """
        currency = currency or self.base_currency
        amt = self.zeroAmount(currency)
        for entry in filter(lambda x: not x.isControlEntry(),
                            self.entryValues(effective, status, query)):
            amt += entry.amountAs(currency)
        return amt

    def _ctl_balances(self, effective=None, currency=''):
        """
        summate balances in control accounts
        """
        effective = effective or DateTime()
        return self._convert(map(lambda x: x.balance(effective=effective),
                                 self.objectValues('BLControlEntry')),
                             effective, currency or self.base_currency)

    def _ctl_totals(self, effective=None, currency='', status=STATUSES, query=None):
        """
        totals for control entries
        """
        # TODO - ignoring status/query ...
        totals = map(lambda x: x.total(currency or self.base_currency, effective),
                     self.objectValues('BLControlEntry'))
        return totals and reduce(operator.add, totals) or self.zeroAmount()

    def debitTotal(self, effective=None, currency=None, status=STATUSES, query=None):
        """
        sum up the debits
        effective_date can be a single value or a list with a single element, in which case, we return
        all debits until that date.  If effective_date is a multi-element list, then we sum the entries
        within that range
        """
        currency = currency or self.base_currency
        return self._convert(map(lambda x: x.amountAs(currency),
                                 filter(lambda x: x.amount > 0,
                                        self.entryValues(effective, status, query))),
                             effective, currency)

    def creditTotal(self, effective=None, currency=None, status=STATUSES, query=None):
        """
        sum up the credits (filtering out any reversals)
        effective_date can be a single value or a list with a single element, in which case, we return
        all credits until that date.  If effective_date is a multi-element list, then we sum the entries
        within that range
        """
        currency = currency or self.base_currency
        return self._convert(map(lambda x: x.amountAs(currency),
                                 filter(lambda x: x.amount < 0,
                                        self.entryValues(effective, status, query))),
                             effective, currency)

    def _convert(self, amounts, effective=None, currency=None):
        """
        summate amounts, doing any necessary currency conversion (as at effective)
        """
        # can't reduce an empty lost ...
        if amounts:
            total = reduce(operator.add, amounts)
        else:
            total = ZCurrency(currency or self.base_currency, 0.0)

        if currency and total.currency() != currency:
            if effective:
                if type(effective) in (types.ListType, types.TupleType):
                    eff = max(effective)
                else:
                    if not isinstance(effective, DateTime):
                        raise ValueError(effective)
                    eff = effective
            else:
                eff = DateTime()

            pt = getToolByName(self, 'portal_bastionledger')
            return pt.convertCurrency(total, eff, currency)

        return total

    def hasForwards(self, dt=None):
        """
        returns whether or not there are forward-dated transactions
        """
        # TODO - rewrite as a catalog query ...
        return len(self.entryValues(effective=(dt or DateTime(), MAXDT))) != 0

    def openingBalance(self, effective=None, currency=''):
        """
        return the amount as per the effective date (as summed past the last period end)
        """
        currency = currency or self.base_currency
        effective = effective or DateTime()

        balance = self.periods.balanceForAccount(
            effective, self.aq_parent.getId(), self.getId())

        if balance is None:
            #balance = self.total(currency=currency, effective=effective)
            balance = self.zeroAmount(currency)
        elif balance.currency() != currency:
            pt = getToolByName(self, 'portal_bastionledger')
            balance = pt.convertCurrency(balance, effective, currency)

        return balance

    def prettyTitle(self):
        """
        seemly title - even in face of portal_factory creation ...
        """
        return "%s - %s" % (self.accno or self.getId(), self.title or self.getId())

    def _entryQuery(self, aquery):
        """ any additional filter to define entry's within an account """
        return aquery & Eq('meta_type', 'BLEntry')

    def entryValues(self, effective=None, status=STATUSES, query=None, REQUEST=None):
        """
        returns all entries in given status's - defaulted to filter cancelled status
        query is an advanced query
        """
        if effective is None:
            end = DateTime('3000/01/01')
            start = self.openingDate(DateTime())
        elif isinstance(effective, DateTime):
            end = effective
            start = self.openingDate(end)
        elif type(effective) == types.StringType:
            end = ceiling_date(effective)
            start = self.openingDate(end)
        else:
            end = max(effective)
            start = min(effective)

        # add control entries to top of list - regardless of balance for the
        # date range!!
        entries = map(lambda x: x.blEntry(effective=(start, end)),
                      self.objectValues('BLControlEntry'))

        # cannot filter on ledgerId - subsidiary ledgers ...
        aquery = self._entryQuery(Eq('accountId', self.getId(), filter=True) &
                                  Eq('ledgerId', self.aq_parent.getId(), filter=True) &
                                  Between('effective', start, end, filter=True) &
                                  In('status', status))

        if query:
            aquery = aquery & query

        # old or new-style catalog?? needed temporarily to allow ledger import
        catalog = self.bastionLedger()
        # if getattr(aq_base(catalog), '_catalog', None) is None:
        #    catalog = self.aq_parent

        # the account-side of any entry (which can include tid's from other journals) is
        # being determined by not starting with btree's generateId tag
        for brain in catalog.evalAdvancedQuery(aquery, (('effective', 'desc'),)):
            try:
                entries.append(brain._unrestrictedGetObject())
            except NotFound:
                # eek - screwed up indexes ...
                raise NotFound(brain.getPath())
                continue
            except KeyError:
                # eek more screwed indexes ....
                # print brain
                # print brain.items()
                # print brain.__record_schema__
                raise KeyError(brain.getPath())

        return entries

    def entryIds(self, effective=None, status=STATUSES, query=None, REQUEST=None):
        """
        returns all entries in given status's - defaulted to filter cancelled
        this is actually the list of transaction ids affecting this account
        query is a ZCatalog query record hash
        """
        return map(lambda x: x.blTransaction().getId(),
                   self.entryValues(effective, status, query))

    def transactionValues(self, effective=None, status=STATUSES, REQUEST=None):
        """
        """
        # TODO - what about control accounts/subsidiary ledgers??

        # return self.aq_parent.transactionValues(effective=effective,
        #                                        status=STATUSES,
        #                                        accountId=self.accountId())
        return map(lambda x: x.blTransaction(),
                   filter(lambda x: x.meta_type in ('BLEntry', 'BLSubsidiaryEntry'),
                          self.entryValues(effective, status)))

    def subtypes(self, type=''):
        if type:
            ret = []
            for stype in map(lambda x: x['subtype'], self.bastionLedger().evalAdvancedQuery(Eq('type', type))):
                if stype == '' or stype in ret:
                    continue
                ret.append(stype)
            return ret
        else:
            return self.bastionLedger().uniqueValuesFor('subtype')

    def modificationTime(self):
        """ """
        return self.bobobase_modification_time().strftime('%Y-%m-%d %H:%M')

    def manage_editProperties(self, REQUEST):
        """ Overridden to make sure recataloging is done """
        for prop in self._propertyMap():
            name = prop['id']
            if 'w' in prop.get('mode', 'wd'):
                value = REQUEST.get(name, '')
                self._updateProperty(name, value)

        self.bastionLedger().catalog_object(self, '/'.join(self.getPhysicalPath()))

    def isDeletable(self, effective=None):
        """
        return whether or not this account may be deleted (ie has no transactions/entries)
        on it
        """
        for entry in self.entryValues():
            if entry.meta_type == 'BLControlEntry':
                if entry.balance(effective=effective) != 0:
                    return False
            else:
                return False
        return True

    def manage_delProperties(self, ids=[], REQUEST=None):
        """ only delete props NOT in extensions ..."""
        if REQUEST:
            # Bugfix for property named "ids" (Casey)
            if ids == self.getProperty('ids', None):
                ids = []
            ids = REQUEST.get('_ids', ids)
        extensions = self.aq_parent.aq_parent.propertyIds()
        ids = filter(lambda x, y=extensions: x not in y, ids)
        LargePortalFolder.manage_delProperties(self, ids)
        if REQUEST:
            return self.manage_propertiesForm(self, REQUEST)

    def createTransaction(self, title='', reference=None, effective=None):
        """
        polymorphically create correct transaction for ledger, returning this transaction
        """
        ledger = self.blLedger()
        tid = manage_addBLTransaction(ledger, '',
                                      title,
                                      effective or DateTime(),
                                      reference)
        return ledger._getOb(tid)

    def createEntry(self, txn, amount, title=''):
        """ transparently create a transaction entry"""
        manage_addBLEntry(txn, self, amount, title)

    def manage_payAccount(self, amount, description='Payment - Thank You', reference='', other_account=None, REQUEST=None):
        """
        make a physical funds payment on the account, implemented using
        BastionBanking

        Note this is intended to work polymorphically across all accounts in
        all types of ledger.
        """
        bms = self.getBastionMerchantService()

        if not bms:
            raise ValueError('No BastionMerchantService')

        # other account should be blank only in Ledger
        if not other_account:
            other_account = self.accountValues(tags='bank_account')[0]

        txn = self.createTransaction('Payment')
        amount = abs(amount)
        if self.balance():
            other_account.createEntry(txn, amount, 'Cash')
            self.createEntry(txn,  -amount, description)
        else:
            other_account.createEntry(txn, -amount, 'Cash')
            self.createEntry(txn, amount, description)

        # if the merchant service redirects, we need to ensure the transaction
        # remains ...
        transaction.get().savepoint(optimistic=True)

        rc = bms.manage_payTransaction(txn, reference, REQUEST=self.REQUEST)

        # BastionMerchantService may hihack us - redirecting our client ...
        if rc and REQUEST:
            REQUEST.set('Payment Processed')
            return self.manage_main(self, REQUEST)

    def manage_statusModify(self, workflow_action, REQUEST=None):
        """
        perform the workflow (very Plone ...)
        """
        self.content_status_modify(workflow_action)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'State Changed')
            return self.manage_main(self, REQUEST)

    # need to allow setting of properties from Python Scripts...- maybe we should just
    # use manage_changeProperties ...
    def updateProperty(self, name, value):
        """
        set or update a property
        """
        if not self.hasProperty(name):
            self._setProperty(name, value)
        else:
            self._updateProperty(name, value)

    def sum(self, id, effective=None, debits=True, credits=True):
        """
        summate entries based upon id (the other account id), date range, and sign
        """
        currency = self.base_currency
        amount = ZCurrency(currency, 0)
        for entry in self.entryValues(effective):
            try:
                a = entry.blTransaction().blEntry(id).amountAs(currency)
            except:
                continue
            if (debits and a > 0) or (credits and a < 0):
                amount += a
        return amount

    def balances(self, dates, entries=[], curfmt='%0.2f'):
        """
        return string balance information for a date range and/or entry range (suitable for graphing)
        an empty format returns ZCurrencies ...
        """
        if len(entries) == 0:
            if curfmt:
                return map(lambda x: self.balance(effective=x).strfcur(curfmt), dates)
            return map(lambda x: self.balance(effective=x), dates)
        days = {}
        for entry in entries:
            effective = entry.effective()
            if days.has_key(effective):
                days[effective] += entry.amount
            else:
                days[effective] = entry.amount
        zero = self.zeroAmount()
        for date in dates:
            if not days.has_key(date):
                days[date] = zero
        drange = days.keys()
        drange.sort()
        for i in xrange(0, len(drange) - 1):
            if i == 0:
                days[drange[0]] += self.balance(effective=drange[0])
            days[drange[i + 1]] += days[drange[i]]

        if curfmt:
            return map(lambda x: days[x].strfcur(curfmt), drange)
        return map(lambda x: days[x], dtrange)

    def zeroAmount(self, currency=''):
        """
        a zero-valued amount in the currency of the account
        """
        return ZCurrency(currency or self.base_currency, 0)

    def allTags(self):
        """
        return a list of all the tags this account is associated with
        """
        tags = list(self.tags)
        pt = getToolByName(self, 'portal_bastionledger')
        ledger_id = self.aq_parent.getId()

        for assocs in pt.objectValues('BLAssociationFolder'):
            for tag in map(lambda x: x.getId(),
                           assocs.searchObjects(ledger=ledger_id, accno=self.accno)):
                if tag not in tags:
                    tags.append(tag)

        tags.sort()
        return tags

    def hasTag(self, tag):
        """
        """
        if tag in self.tags:
            return True

        pt = getToolByName(self, 'portal_bastionledger')
        for assocs in pt.objectValues('BLAssociationFolder'):
            if assocs.searchResults(ledger=self.aq_parent.getId(), accno=self.accno, id=tag):
                return True

        return False

    def __cmp__(self, other):
        """
        hmmm - sorted based on accno
        """
        if not isinstance(other, BLAccount):
            return 1
        if other.accno > self.accno:
            return 1
        elif other.accno < self.accno:
            return -1
        return 0

    def __str__(self):
        return "<%s instance - (%s/%s [%s], %s)>" % (self.meta_type,
                                                     self.aq_parent.getId(),
                                                     self.getId(),
                                                     self.title,
                                                     self.balance())

    def asCSV(self, datefmt='%Y/%m/%d', curfmt='%a', REQUEST=None):
        """
        """
        return '\n'.join(map(lambda x: x.asCSV(datefmt, curfmt), self.entryValues()))

    def asPDF(self, effective=None, REQUEST=None):
        """
        """
        body = self.blaccount_template_html(
            self, REQUEST, effective=effective or DateTime())
        return self.html2pdf(body)

    def asEmail(self, recipient, effective=None, message='', REQUEST=None):
        """
        """
        return self.blaccount_template(self,
                                       REQUEST,
                                       sender=correspondenceEmail(
                                           self.aq_parent),
                                       email=recipient,
                                       effective=effective or DateTime(),
                                       message=message)

    def getBastionMerchantService(self):
        """
        returns a Bastion Internet Merchant tool if present (or None) such that
        any/all account(s) could be paid-down via the internet
        """
        # TODO - use IBankMerchant
        parent = self

        try:
            while parent:
                bms = filter(lambda x: x.status() == 'active',
                             parent.objectValues('BastionMerchantService'))
                if bms:
                    return bms[0]

                parent = parent.aq_parent
        except:
            pass

        return None

    def payeeAmount(self, effective=None):
        """
        """
        return self.balance(effective=effective or DateTime())

    def _repair(self):
        # remove BLObserverSupport
        for attr in ('onAdd', 'onChange', 'onDelete'):
            if getattr(aq_base(self), attr, None):
                delattr(self, attr)
        if not getattr(aq_base(self), 'tags', None):
            self.tags = []
        entryids = list(self.objectIds(['BLEntry', 'BLSubsidiaryEntry']))
        if entryids:
            self.manage_delObjects(entryids)

        opening = getattr(aq_base(self), 'OPENING', None)
        if opening:
            delattr(self, 'OPENING')

        # force reindexing ...
        self.bastionLedger().catalog_object(self, '/'.join(self.getPhysicalPath()))

    def _totalise(self, entry, now=None):
        """ 
        update internal running totals/cache counters

        this is the balance (and date) as at last transaction on this account
        """
        if entry.isControlEntry():
            # no effective date - TODO ???
            # shouldn't be involved in posting!!!
            raise PostingError(entry)

        effective = entry.effective()

        # ignore forward-dated transactions
        if effective > ceiling_date(now or DateTime()):
            return

        if effective >= self.openingDate():
            currency = self.base_currency
            if entry.amount.currency() == currency:
                self._balance += entry.amount
            else:
                amount = entry.foreignAmount()
                if amount and amount.currency() == currency:
                    self._balance += amount
                else:
                    pt = getToolByName(self, 'portal_bastionledger')
                    self._balance += pt.convertCurrency(
                        entry.amount, effective, currency)

        if effective > self._balance_dt:
            self._balance_dt = effective

    def _untotalise(self, entry, now=None):
        """ update internal running totals/cache counters """

        # no effective date ...
        if entry.isControlEntry():
            return

        effective = entry.effective()

        # ignore forward-dated transactions
        if effective > ceiling_date(now or DateTime()):
            return

        # it's previous period, ignore it
        if effective < self.openingDate():
            return

        currency = self.defaultCurrency()
        if entry.amount.currency() == currency:
            self._balance -= entry.amount
        else:
            amount = entry.foreignAmount()
            if amount and amount.currency() == currency:
                self._balance -= amount
            else:
                pt = getToolByName(self, 'portal_bastionledger')
                self._balance -= pt.convertCurrency(
                    entry.amount, effective, currency)

        self._balance_dt = self.lastTransactionDate()

    def _totValidFor(self, effective, now=None, controls=True):
        """
        returns whether or not the cached balance can be used for the date
        """
        # last condition checks that no forward txns exist that thus aren't
        # incorporated in the totalization
        if effective >= self._balance_dt:
            return self.lastTransactionDate(max(effective, now or DateTime()), controls) <= self._balance_dt
        return False

    def _totDate(self):
        """
        TOOO - is this useful???
        """
        controls = map(lambda x: x.lastTransactionDate(),
                       self.objectValues('BLControlEntry'))
        return controls and max(controls + [self._balance_dt]) or self._balance_dt

    def totDate(self):
        """ the running total balance usability date """
        # ignore control entry dates??
        return self._balance_dt  # .strftime('%Y/%m/%d')

    def totBalance(self, currency=''):
        """ the running total balance as per internal caches """
        currency = currency or self.base_currency
        ctls = self._ctl_balances(currency=currency)
        if self._balance.currency() == currency:
            return self._balance + ctls
        return self._convert([self._balance, ctls], self._balance_dt, currency)

    def manage_setBalance(self, amount, effective=None, REQUEST=None):
        """
        manually set/override balance counters
        """
        # if amount.currency != self.bastionLedger().defaultCurrency():
        #    raise UnsupportedCurrency, amount
        self._balance = amount
        self._balance_dt = floor_date(effective or DateTime())

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_recalculateBalance(self, effective=None, REQUEST=None):
        """
        recompute internal cache balance/total
        """
        effective = effective or self.lastTransactionDate()
        # don't incorporate control balances ...
        total = self.openingBalance(effective) + self._total(effective)
        self.manage_setBalance(total, effective)
        if REQUEST:
            REQUEST.set('manage_tabs_message',
                        'Recalculated balance - %s' % total)
            return self.manage_main(self, REQUEST)

    def lastTransactionDate(self, now=None, controls=True):
        """
        the last non-forward-dated transaction date for the ledger
        if effective is set - then the last transaction date prior to this

        looks/does control account entries flag
        """
        opening = self.openingDate()
        now = now or DateTime()

        thisq = Eq('accountId', self.getId(), filter=True) & \
            Eq('ledgerId', self.ledgerId(), filter=True)

        effectiveq = In('meta_type', ('BLEntry', 'BLSubsidiaryEntry')) & \
            Ge('effective', opening, filter=True) & \
            Le('effective', now, filter=True)

        if controls:
            # if it contains control entries, then look for last txn in these
            # too
            subsidiaries = map(lambda x: x.getId(),
                               self.objectValues('BLControlEntry'))
            if subsidiaries:
                query = Or(In('ledgerId', subsidiaries, filter=True) & effectiveq,
                           thisq & effectiveq)

            else:
                query = thisq & effectiveq
        else:
            query = thisq & effectiveq

        # hmmm - still worried about missing/incomplete catalogs
        for brain in self.bastionLedger().evalAdvancedQuery(query, (('effective', 'desc'),)):
            try:
                # return brain._unrestrictedGetObject().effective()
                entry = brain._unrestrictedGetObject()
                # print "%s - lastTransactionDate() entry=%s [effective=%s]" %
                # (self.getId(), repr(entry), entry.effective())
                return entry.effective()
            except:
                pass
        return opening

    #
    # indexing helpers
    #
    def SearchableText(self):
        """
        indexing helper
        """
        return self.Title() + ' ' + self.attachmentSearchableText()

    def effective(self):
        """
        don't index this - it affects retrievals for multiple balance displays et al
        """
        return None

    def ledgerId(self):
        return self.aq_parent.getId()

    def jsonBalances(self, start, end, dtfmt='%Y/%m/%d'):
        """
        balance information for d3 graphing (ie unix-seconds style dates)
        """
        results = []
        dtrange = []
        dt = min(start, end)
        while dt < max(start, end):
            dtrange.append(ceiling_date(dt))
            dt += 1

        balances = self.balances(dtrange, curfmt=None)
        for index in range(0, len(dtrange)):
            # numerical amount (not currency) so it can be graphed ...
            results.append({'effective': dtrange[index].strftime(dtfmt),
                            'amount': balances[index].amount()})

        return json.dumps(results)

    def getIcon(self, relative_to_portal=0):
        """
        use different icon if control account ...
        """
        icon = super(BLAccount, self).getIcon(relative_to_portal)
        return self.isControl() and icon.replace('account.gif', 'controlaccount.gif') or icon

    def downloadQIF(self, query={}, effective=None, statuses=STATUSES):
        """
        """
        qif = '!TYPE:Oth %s\n' % self.type[0]
        for entry in self.applyFilter(query,
                                      self.entryValues(effective,
                                                       statuses,
                                                       self.makeAdvQuery(query))):
            qif += entry.asQIF()
        download(qif, 'application/qif', '%s.qif' %
                 self.getId(), self.REQUEST, self.REQUEST.RESPONSE)

AccessControl.class_init.InitializeClass(BLAccount)


# deprecated implementation
class BLAccounts(BTreeFolder2, PropertyManager):
    pass


def accno_field_cmp(x, y):
    if x.accno == y.accno:
        return 0
    if x.accno > y.accno:
        return 1
    return -1


def date_field_cmp(x, y):
    # we could have dangling accounts :(
    try:
        x_dt = x[1].effective()
    except:
        x_dt = EPOCH
    try:
        y_dt = y[1].effective()
    except:
        y_dt = EPOCH
    if x_dt == y_dt:
        return 0
    if x_dt > y_dt:
        return 1
    return -1


def accountAdd(ob, event):
    # allow copy/pasted to retain balance info
    if getattr(aq_base(ob), '_balance', None):
        return

    # set up cache-amount/totalise stuff
    ob.manage_setBalance(ob.zeroAmount(ob.base_currency), EPOCH)


def cloneAccount(ob, event):
    ob.accno = ob.getId()
