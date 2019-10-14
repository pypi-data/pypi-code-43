#
#    Copyright (C) 2002-2017  Corporation of Balclutha. All rights Reserved.
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
import logging
import types
import sys
import traceback
import string
import uuid
from Acquisition import aq_base
from DateTime import DateTime
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionBanking.Exceptions import UnsupportedCurrency
from utils import floor_date, assert_currency
from BLBase import PortalContent, UUID_ATTR, catalogAdd, catalogRemove
from BLGlobals import EPOCH
from BLTransaction import BLTransaction, _addEntryToTransaction
from AccessControl.Permissions import view, view_management_screens, manage_properties, \
    access_contents_information
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from Exceptions import LedgerError, PostingError, AlreadyPostedError, InvalidAccount

from zope.interface import Interface, implementer
from interfaces.transaction import IEntry

LOG = logging.getLogger('BLEntry')


manage_addBLEntryForm = PageTemplateFile('zpt/add_entry', globals())


def manage_addBLEntry(self, account, amount, title='', id=None, REQUEST=None):
    """
    Add an entry - to a transaction ...

    account is either a BLAccount or an account id
    """
    entry = _addEntryToTransaction(
        self.this(), self.Ledger, BLEntry, account, amount, title, id)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

    return entry.getId()


@implementer(IEntry)
class BLEntry(PropertyManager, PortalContent):
    """
    An account/transaction entry

    Once the transaction has been posted, the entry has a date attribute
    Also, if there was any fx required, it will have an fx_rate attribute - from which the
    original currency trade may be derived ??
    """
    meta_type = portal_type = 'BLEntry'


    #  SECURITY MACHINERY DOES NOT LIKE PropertyManager.__ac_permissions__ ''
    __ac_permissions__ = (
        (manage_properties, ('manage_addProperty', 'manage_editProperties',
                             'manage_delProperties', 'manage_changeProperties',
                             'manage_propertiesForm', 'manage_propertyTypeForm',
                             'manage_changePropertyTypes', )),
        (access_contents_information, ('hasProperty', 'propertyIds', 'propertyValues',
                                       'propertyItems', 'getProperty', 'getPropertyType',
                                       'propertyMap', 'blAccount', 'blTransaction', 'isMultiCurrency',
                                       'blLedger', 'accountId', 'transactionId', 'tags'), ('Anonymous', 'Manager')),
        (view, ('amountStr', 'absAmount', 'absAmountStr', 'isDebit', 'isCredit', 'status',
                'effective',  'reference', 'isControlEntry', 'asCSV', 'foreignAmount', 'foreignRate', 'foreignCurrency')),
        (OperateBastionLedgers, ('edit', 'setReference', 'manage_changeAccount')),
        (ManageBastionLedgers, ('manage_edit', 'manage_removeForeignAmount')),
    ) + PortalContent.__ac_permissions__

    #
    # we have some f**ked up stuff because id's may be used further up the aquisition path ...
    #
    __replaceable__ = 1

    manage_options = (
        {'label': 'Details',    'action': 'manage_main'},
        {'label': 'View',       'action': ''},
    ) + PortalContent.manage_options

    manage_main = PageTemplateFile('zpt/edit_entry', globals())

    property_extensible_schema__ = 0
    _properties = (
        {'id': 'title',    'type': 'string',    'mode': 'w'},
        # this seems to screw up!
        {'id': 'ref',      'type': 'string',    'mode': 'w'},
        {'id': 'account',  'type': 'string',    'mode': 'w'},
        {'id': 'amount',   'type': 'currency',  'mode': 'w'},
    )

    def __init__(self, id, title, account, amount, ref=''):
        assert type(
            account) == types.StringType, "Invalid Account: %s" % account
        assert_currency(amount)
        self.id = id
        self.title = title
        # account is actually the account path from the Ledger
        self.account = account
        self.amount = amount
        self.ref = ref

    def Title(self):
        """
        return the description of the entry, guaranteed non-null
        """
        return self.title or self.blTransaction().Title()

    def amountStr(self): return self.amount.strfcur()

    def amountAs(self, currency=''):
        """
        each entry may support two currencies, it's face currency and the posting currency
        """
        if currency == '' or self.amount.currency() == currency:
            return self.amount

        amount = self.foreignAmount()

        if amount and amount.currency() == currency:
            return amount

        try:
            return self.portal_bastionledger.convertCurrency(self.amount, self.effective(), currency)
        except:
            raise UnsupportedCurrency('%s - %s' % (currency, str(self)))

    def foreignAmount(self):
        """ optional FX/amount for multi-currency txns """
        return getattr(aq_base(self), 'posted_amount', None)

    def foreignRate(self):
        """
        """
        return getattr(aq_base(self), 'fx_rate', 0.0)

    def foreignCurrency(self):
        """
        """
        fa = self.foreignAmount()
        return fa and fa.currency or self.amount.currency

    def absAmount(self, currency=''):
        return abs(self.amountAs(currency))

    def absAmountStr(self): return self.absAmount().strfcur()

    def isDebit(self): return self.amount > 0

    def isCredit(self): return not self.isDebit()

    def effective(self):
        """
        return the effective date of the entry - usually deferring to the effective
        date of the underlying transaction the entry relates to

        a None value represents a control entry
        """
        dt = getattr(aq_base(self), '_effective_date', None)
        if dt:
            return dt.toZone(self.timezone)

        return self.blTransaction().effective()

    # stop shite getting into the catalog ...
    def _noindex(self): pass
    tags = type = subtype = accno = _noindex

    def blLedger(self):
        """
        return the ledger which I relate to (or None if I'm not yet posted)
        """
        return self.bastionLedger().Ledger

    def ledgerId(self):
        """
        returns the id of the account which the entry is posted/postable to
        """
        if self.account.find('/') != -1:
            return self.account.split('/')[0]

        return self.blLedger().getId()

    def accountId(self):
        """
        returns the id of the account which the entry is posted/postable to
        """
        if self.account.find('/') != -1:
            return self.account.split('/')[1]
        return self.account

    def transactionId(self):
        """
        returns the id of the transaction (used for indexing/collation)
        """
        return self.blTransaction().getId()

    def blAccount(self):
        """
        return the underlying account to which this affects
        """
        aid = self.accountId()
        account = self.blLedger()._getOb(aid, None)
        if account is None:
            raise InvalidAccount(aid)
        return account

    def blTransaction(self):
        """
        A context independent way of retrieving the txn.  If it's posted then there
        are issues with the object id not being identical in container and object ...
        """
        parent = self.aq_parent
        if isinstance(parent, BLTransaction):
            return parent

        ledger = self.blLedger()

        # I must be in an account, acquire my Ledger's Transactions ...
        try:
            return ledger._getOb(self.getId())
        except (KeyError, AttributeError):
            if self.isControlEntry():
                return None

        raise AttributeError('%s - %s' % (ledger, self))

    def _setEffectiveDate(self, dt):
        """
        some entry's don't belong to transaction's specifically, but we still want to give them a date
        """
        self._effective_date = floor_date(dt)
        cat = self.bastionLedger()
        cat.catalog_object(self, idxs=['effective'])

    def edit(self, title, amount, fx_rate=None, account=None):
        """
        Plone edit
        """
        self._updateProperty('title', title)
        try:
            status = self.status()
            if not status in ('posted', 'reversed', 'cancelled', 'postedreversal'):
                self._updateProperty('amount', amount)
                if account:
                    self._updateProperty('account', account)
            # hmmm - allow posted-amount tweaks ...
            if fx_rate:
                self._setForeignAmount(fx_rate)
        except:
            pass

    def manage_edit(self, amount, title='', ref='', fx_rate=None, REQUEST=None):
        """
        priviledged edit mode for experts only ...
        """
        self.manage_changeProperties(amount=amount,
                                     title=title,
                                     ref=ref)
        if type(fx_rate) == types.FloatType and isinstance(self.aq_parent, BLTransaction):
            self._setForeignAmount(fx_rate, force=True)

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def isControlEntry(self):
        """
        returns if this is an entry for a control account
        """
        return False

    def isMultiCurrency(self):
        """
        is this a multi-currency entry (represented in two currency values?)
        """
        return self.foreignAmount() is not None

    def __str__(self):
        """
        Debug representation
        """
        try:
            acct_str = self.blAccount().title
        except:
            acct_str = ''

        # only have txn (and thus effective) if we've been added (and not
        # control entry) ...
        try:
            dt = self.effective()
        except:
            dt = EPOCH
        return "<%s instance - %s %s %s %s/%s at %s>" % (self.meta_type,
                                                         dt and dt.strftime(
                                                             '%Y/%m/%d'),
                                                         self.account,
                                                         acct_str,
                                                         self.amount,
                                                         self.foreignAmount() or '???',
                                                         self.absolute_url())

    __repr__ = __str__

    def manage_removeForeignAmount(self, REQUEST=None):
        """
        delete a posting amount, use with care ...
        """
        if getattr(aq_base(self), 'posted_amount', None):
            delattr(self, 'posted_amount')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _setForeignAmount(self, fx_rate=None, force=False):
        """
        set FX amount (and rate)
        use force to reset/recalculate
        """
        if not force and self.foreignAmount():
            return

        target = self.aq_parent.defaultCurrency()
        base = self.amount.currency()

        if target == base:
            return

        if fx_rate is None:
            if force or not getattr(aq_base(self), 'fx_rate', None):
                self.fx_rate = fx_rate = getToolByName(self, 'portal_bastionledger').crossMidRate(base,
                                                                                                  target,
                                                                                                  self.effective())
            else:
                fx_rate = self.fx_rate

        self.posted_amount = ZCurrency(target, self.amount) * fx_rate

        return self.posted_amount

    def manage_changeAccount(self, accno):
        """
        change the account this entry affects, auto-reposting etc
        """
        if self.blLedger()._getOb(accno, None) is None:
            raise PostingError(accno)

        status = self.status()

        if status in ('posted',):
            self._unpost()
        self.account = accno
        if status in ('posted',):
            self._post()
        # recatalog it ...
        self.bastionLedger().catalog_object(self, '/'.join(self.getPhysicalPath()))

    def _post(self, force=False):
        txn = self.blTransaction()
        account = self.blAccount()

        # do any FX conversion ...
        if self.amount.currency() != txn.defaultCurrency():
            self._setForeignAmount(force=force)

        account._totalise(self)
        return self

    def _unpost(self):
        account = self.blAccount()
        account._untotalise(self)

    def setReference(self, value):
        self._updateProperty('ref', value)

    def reference(self):
        # return a string, or the underlying object if available ...
        if self.ref:
            try:
                return self.unrestrictedTraverse(self.ref)
            except:
                return self.ref
        return ''

    def status(self):
        """
        my status is the status of my transaction ...
        """
        txn = self.blTransaction()
        return txn.status()

    def _repair(self):
        #
        # date is irrelevant on the entry - it's an attribute of the txn ...
        #
        if getattr(aq_base(self), 'date', None):
            delattr(self, 'date')

    def _updateProperty(self, name, value):
        """
        do a status check on the transaction after updating amount
        """
        # we don't update any entries except those in Transactions - ie not posted ...
        # if not isinstance(self.aq_parent, BLTransaction) and name not in ('ref', 'title', 'ledger'):
        #    return

        PropertyManager._updateProperty(self, name, value)
        if name == 'amount' and isinstance(self.aq_parent, BLTransaction):
            self.aq_parent.setStatus()

    def __add__(self, other):
        """
        do any necessary currency conversion ...
        """
        if not isinstance(other, BLEntry):
            raise TypeError(other)

        if not other.account == self.account:
            raise ArithmeticError(other)

        other_currency = other.amount.currency()
        self_currency = self.amount.currency()
        if other_currency != self_currency:
            other_amount = other.foreignAmount()
            if other_amount is None:
                rate = self.portal_bastionledger.crossMidRate(
                    self_currency, other_currency, self.effective())
                amount = ZCurrency(
                    self_currency, (other.amount.amount() * rate + self.amount.amount()))
            else:
                rate = other.fx_rate
                amount = other_amount + self.amount
            entry = BLEntry(self.getId(),
                            self.title,
                            self.account,
                            amount,
                            self.ref)
            entry.fx_rate = rate
            return entry

        else:
            return BLEntry(self.getId(),
                           self.title,
                           self.account,
                           other.amount + self.amount,
                           self.ref)

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        return BLEntry(self.getId(),
                       self.title,
                       self.account,
                       self.amount * other,
                       self.ref)

    def __div__(self, other):
        return BLEntry(self.getId(),
                       self.title,
                       self.account,
                       self.amount / other,
                       self.ref)

    def asCSV(self, datefmt='%Y/%m/%d', curfmt='%a'):
        """
        """
        txn = self.blTransaction()
        account = self.blAccount()
        amount = self.amount
        return ','.join((self.getId(),
                         txn and txn.aq_parent.getId() or '',
                         txn and txn.getId() or '',
                         '"%s"' % self.Title(),
                         txn and '"%s"' % txn.effective().toZone(self.timezone).strftime(datefmt) or '',
                         amount.strfcur(curfmt),
                         account.accno or '',
                         account.Title() or '',
                         self.status()))

    def asQIF(self, datefmt='%d/%m/%y'):
        """
        Quicken Interchange Format of this entry
        """
        return '\n'.join(('D%s' % self.effective().strftime(datefmt),
                          'T%s' % self.amount.amount_str(),
                          'N',
                          'P%s' % self.Title(),
                          '^\n'))

    def __cmp__(self, other):
        """
        sort entries on effective date
        """
        if not isinstance(other, BLEntry):
            return 1

        thisaccid = self.accountId()
        otheraccid = other.accountId()

        if thisaccid < otheraccid:
            return 1
        if thisaccid > otheraccid:
            return -1

        thisamt = self.amount
        otheramt = other.amount

        if thisamt != otheramt:
            return 1

        return 0

    def postingEntry(self):
        """
        the entry in the transaction from which the posted entry was/will be generated
        """
        if self.isPosting():
            return self
        return self.blTransaction().entry(self.accountId())

    def postedEntry(self):
        """
        if the transaction is posted, then the corresponding entry in the affected account,
        otherwise None
        """
        if not self.isPosting():
            return self

        acc = self.blAccount()
        tid = self.aq_parent.getId()
        try:
            return acc._getOb(tid)
        except (KeyError, AttributeError):
            pass

        return None

    def tags(self):
        """
        indexing (transactions only - for now....)
        """
        if isinstance(self.aq_parent, BLTransaction):
            return self.aq_parent.tags
        return []

AccessControl.class_init.InitializeClass(BLEntry)


def addEntry(ob, event):

    if ob.meta_type == 'BLControlEntry':
        return

    parent = ob.aq_parent

    # OLD-CATALOG - ignore copy/paste/import for accounts
    if not isinstance(parent, BLTransaction):
        return

    catalogAdd(ob, event)

    parent.setStatus()


def delEntry(ob, event):
    if ob.meta_type == 'BLControlEntry':
        return

    # wtf - this is getting called multiple times!!!
    if getattr(aq_base(ob), '_v_deleted', False):
        return

    ob._v_deleted = True

    # uncatalog it first - affects lastTransactionDate calculation !!
    catalogRemove(ob, event)

    parent = ob.aq_parent

    # global ledger deletes cascade to this, but *only* process as if
    # transaction ...
    if isinstance(parent, BLTransaction):
        if parent.status() == 'posted':
            try:
                ob.blAccount()._untotalise(ob)
            except AttributeError:
                # old style/unmigrated ledger
                pass
            except SyntaxError:
                # old style/unmigrated periodinfos
                pass

        parent.setStatus()
