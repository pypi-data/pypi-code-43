#
#    Copyright (C) 2007-2018  Corporation of Balclutha. All rights Reserved.
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
import operator
import types
from Acquisition import aq_base
from AccessControl.Permissions import access_contents_information
from Products.CMFCore.utils import getToolByName
from BLEntry import BLEntry
from DateTime import DateTime
from Permissions import ManageBastionLedgers
from Exceptions import PostingError
from BLGlobals import EPOCH
from Products.AdvancedQuery import Between, Eq, In
from Products.BastionBanking.ZCurrency import ZCurrency
from utils import floor_date, ceiling_date

LOG = logging.getLogger('BLControlEntry')


class BLControlEntry(BLEntry):
    """
    An entry representing a summary amount from a subsidiary ledger

    This guy is *only* found in accounts, and there is *no* associated
    transaction
    """
    meta_type = 'BLControlEntry'
    portal_type = 'BLEntry'

    __ac_permissions__ = BLEntry.__ac_permissions__ + (
        (access_contents_information, ('lastTransactionDate',
                                       'blEntry',
                                       'entryValues',
                                       'transactionValues')),
        (ManageBastionLedgers, ('manage_recalculate',)),
    )

    _properties = BLEntry._properties + (
        {'id': 'ledger',   'type': 'selection',
            'mode': 'r', 'select_variable': 'ledgerIds'},
    )

    def isControlEntry(self):
        """
        returns if this is an entry for a control account
        """
        return True

    def effective(self):
        """
        hmmm - this guy is *always* effective, it's just his amount varies ...
        """
        return None

    def lastTransactionDate(self):
        """
        date from which this entry is valid - anything prior to this will
        require a recomputation from the underlying subsidiary ledger
        """
        # _balance_dt only missing before/during OLD-CATALOG repair
        dt = getattr(aq_base(self), '_effective_date', None)
        if dt is not None:
            return dt
        txn = self.blLedger().lastTransaction()
        if txn:
            return txn.effective_date
        return self.aq_parent.totDate()

    def lastControlDate(self):
        """
        the anticipated/expected date for this entry to be valid/relevant
        """
        return max(self.lastTransactionDate(), self.periods.lastPeriod())

    def blTransaction(self):
        """
        there is no transaction associated with a control entry - it's the summation
        of all the transactions in the subsidiary ledger
        """
        return None

    def blLedger(self):
        """
        return the ledger which I relate to (or None if I'm not yet posted)
        """
        # find by acquisition
        theledger = self.bastionLedger()

        try:
            # id should be the same as ledger now as well ...
            return theledger._getOb(self.getId())
        except (KeyError, AttributeError):
            raise AttributeError('No BLLedger - BastionLedger=%s\n%s' % (theledger, self))

    def blAccount(self):
        """
        """
        return self.aq_parent

    def accountId(self):
        """
        """
        return self.aq_parent.getId()

    def blLedgerUrl(self):
        """
        the URL of the journal that aggregates to this entry
        """
        return '%s/%s' % (self.bastionLedger().absolute_url(), self.getId())

    def status(self):
        """ always posted """
        return 'posted'

    def balance(self, currency='', effective=None):
        """
        return the sum of all the entries from opening balance date til date specified
        """
        # _effective_date is the effective date of the latest subsidiary txn - the
        # latest date for which this 'cache' is good!!
        if effective is None:
            return self.amount

        opening_dt = self.lastTransactionDate()

        if type(effective) in (types.ListType, types.TupleType):
            effective = max(effective)

        if not isinstance(effective, DateTime):
            raise ValueError(effective)

        if effective >= opening_dt:
            return self.amount

        # if we've deleted the ledger this control account is associated with we
        # don't want the thing to be borked ...
        try:
            ledger = self.blLedger()
            return ledger.total(currency=currency, effective=(EPOCH, effective))
        except:
            pass
        return self.zeroAmount()

    def total(self, currency='', effective=None):
        """
        summates entries over range (or up to a date)
        """
        cache_dt = self.lastTransactionDate()
        if type(effective) in (types.ListType, types.TupleType):
            min_dt = min(effective)
            max_dt = max(effective)
        elif effective is None:
            if effective >= cache_dt:
                return self.amount
            min_dt = self.openingDate()
            max_dt = cache_dt
        else:
            min_dt = min([effective, self.openingDate()])
            max_dt = max([effective, cache_dt])

        # make sure we get any marked/converted fx posted amounts ....
        entries = self.entryValues((min_dt, max_dt))
        if entries:
            return reduce(operator.add, map(lambda x: x.amountAs(currency or self.aq_parent.base_currency), entries))
        return ZCurrency(currency or self.aq_parent.base_currency, 0)

    def manage_recalculate(self, effective=None, force=False, REQUEST=None):
        """
        recompute our cached 'amount', for effective (or Now)
        note that 'force' should probably *always* be false ...
        """
        old = self.amount
        self.blLedger().manage_recalculateControl(
            self.aq_parent.getId(), effective or DateTime(), force)
        if REQUEST:
            REQUEST.set('manage_tabs_message',
                        'Recalculated control as at %s (%s->%s)' % (effective or DateTime(), old, self.amount))
            return self.manage_main(self, REQUEST)

    def blEntry(self, currency='', effective=None):
        """
        return a BLControlEntry with the appropriate amount in our acquisition context

        we cannot return a genuine BLEntry because we are still not associated with
        any transaction ...
        """
        parent = self.aq_parent

        entry = BLControlEntry(self.getId(),
                               self.title,
                               self.account,
                               self.total(currency, effective))

        entry._effective_date = effective and type(effective) in (
            types.ListType, types.TupleType) and max(effective) or DateTime()

        return entry.__of__(parent)

    def transactionValues(self, effective=None):
        """
        """
        results = {}
        for entry in self.entryValues(effective):
            txn = entry.blTransaction()
            if not results.has_key(txn.getId()):
                results[txn.getId()] = txn
        return results.values()

    def entryValues(self, effective=None):
        """
        the entries in the subsidiary ledger on this control account
        """
        results = []
        if type(effective) in (types.ListType, types.TupleType):
            max_dt = max(effective)
            min_dt = min(effective)
        else:
            min_dt = self.openingDate()
            max_dt = effective or DateTime()
        ledger = self.blLedger()
        # we need to ensure we filter out ledger entries on *other* control
        # accounts so we grab via txn
        for txn in map(lambda x: x._unrestrictedGetObject(),
                       ledger.bastionLedger().evalAdvancedQuery(Eq('meta_type', 'BLSubsidiaryTransaction', filter=True) &
                                                                Eq('ledgerId', ledger.getId(), filter=True) &
                                                                Eq('accountId', self.accountId(), filter=True) &
                                                                Between('effective',
                                                                        floor_date(
                                                                            min_dt),
                                                                        ceiling_date(max_dt), filter=True) &
                                                                In('status', ('posted', 'reversed', 'postedreversal')))):
            results.extend(txn.entryValues(ledger.getId()))
        return results

    def _post(self, force=False):
        raise PostingError('wtf!')

AccessControl.class_init.InitializeClass(BLControlEntry)
