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
import logging
import types
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Acquisition import aq_base

from Products.BastionBanking.ZCurrency import ZCurrency

from Permissions import ManageBastionLedgers
from BLEntry import BLEntry, _addEntryToTransaction
from BLTransaction import BLTransaction
from Exceptions import LedgerError
from utils import assert_currency

from zope.interface import implementer
from interfaces.transaction import ISubsidiaryEntry


manage_addBLSubsidiaryEntryForm = PageTemplateFile(
    'zpt/add_subsidiaryentry', globals())


def manage_addBLSubsidiaryEntry(self, account, amount, title='', id=None, REQUEST=None):
    """
    Add an entry - either to an account or a transaction ...
    """
    txn = self.this()
    entry = _addEntryToTransaction(
        txn, txn.aq_parent, BLSubsidiaryEntry, account, amount, title, id)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

    return entry.getId()

@implementer(ISubsidiaryEntry)
class BLSubsidiaryEntry(BLEntry):
    """
    This class is to factor out choosing accounts from the subsidiary ledger for one
    side of the transaction.
    """
    meta_type = 'BLSubsidiaryEntry'
    portal_type = 'BLEntry'


    __ac_permission__ = BLEntry.__ac_permissions__ + (
        (ManageBastionLedgers, ('manage_postedAmount',)),
    )

    def isControlEntry(self):
        return False

    def blLedger(self):
        """
        return the ledger which I am posted (or will be)
        """
        return self.aq_parent.aq_parent

    def manage_postedAmount(self, amount=None, REQUEST=None):
        """
        expert-mode fix up of incorrect fx rate affecting posting
        """
        if isinstance(amount, ZCurrency) and \
                amount.currency() == self.aq_parent.blLedger().controlAccount().base_currency:
            self.posted_amount = amount
        elif amount is None and getattr(aq_base(self), 'posted_amount', None):
            delattr(self, 'posted_amount')

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _post(self, force=False):
        BLEntry._post(self, force)

        control = self.aq_parent._controlEntry()
        control.amount += self.foreignAmount() and self.posted_amount or self.amount

        # adjust effective date on control entry to cache latest txn in
        # subsidiary ledger
        effective = self.effective()
        if effective > control.lastTransactionDate():
            control._setEffectiveDate(effective)

    def _unpost(self):
        BLEntry._unpost(self)
        # TODO - ensure current period ??
        try:
            control = self.controlAccount()
            entry = control._getOb(self.blAccount().getId(), None)
            if entry is not None:
                entry -= self
        except LedgerError:
            # hmmm - control account has been changed/edited since posting
            # hopefully recalculateControls will take care of it ...
            pass

AccessControl.class_init.InitializeClass(BLSubsidiaryEntry)
