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
import types
from DateTime import DateTime
from Acquisition import aq_base
from AccessControl.Permissions import access_contents_information, view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BastionBanking.ZCurrency import ZCurrency
from BLBase import ProductsDictionary
from utils import assert_currency
from BLTransaction import BLTransaction
from Permissions import OperateBastionLedgers
from Exceptions import LedgerError, UnexpectedTransaction, InvalidAccount

from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

manage_addBLSubsidiaryTransactionForm = PageTemplateFile(
    'zpt/add_subsidiarytransaction', globals())


def manage_addBLSubsidiaryTransaction(self, id='', title='', effective=None,
                                      ref=None, entries=[], tags=[], notes='', control=None, REQUEST=None):
    """ add a subsidiary ledger transaction """

    if ref:
        try:
            ref = '/'.join(ref.getPhysicalPath())
        except:
            pass

    # portal_factory needs this to be settable...
    if not id:
        id = str(self.nextTxnId())

    effective = effective or DateTime()
    if type(effective) == types.StringType:
        effective = DateTime(effective)
    effective.toZone(self.timezone)

    if control is not None:
        if not self.isValidControl(control):
            raise UnexpectedTransaction(control)
    else:
        # TODO - wtf - factory dispatcher is borked here ...
        realself = self.__class__.__name__ == '__FactoryDispatcher__' and self.this() or self
        if realself.__class__.__name__ == 'TempFolder':
            realself = realself.aq_parent.aq_parent
        try:
            control = realself._defaultControl().getId()
        except:
            # wtf!! why aren't I a SubsidiaryLedger ...
            raise AssertionError(self,
                                 self.__class__.__name__,
                                 realself)

    txn = BLSubsidiaryTransaction(
        id, title, effective, ref, tags, notes, control)
    notify(ObjectCreatedEvent(txn))

    self._setObject(id, txn)

    txn = self._getOb(id)

    # don't do entries with blank amounts ...
    for entry in filter(lambda x: getattr(x, 'amount', None), entries):
        try:
            assert_currency(entry.amount)
        except:
            entry.amount = ZCurrency(entry.amount)
        if entry.get('credit', False):
            entry.amount = -abs(entry.amount)
        if entry.subsidiary:
            try:
                manage_addBLSubsidiaryEntry(
                    txn, entry.account, entry.amount, entry.title)
            except NameError:
                # doh - more cyclic dependencies ...
                from BLSubsidiaryEntry import manage_addBLSubsidiaryEntry
                manage_addBLSubsidiaryEntry(
                    txn, entry.account, entry.amount, entry.title)
        else:
            try:
                manage_addBLEntry(txn, entry.account,
                                  entry.amount, entry.title)
            except NameError:
                # doh - more cyclic dependencies ...
                from BLEntry import manage_addBLEntry
                manage_addBLEntry(txn, entry.account,
                                  entry.amount, entry.title)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % txn.absolute_url())

    return id


def addBLSubsidiaryTransaction(self, id, title=''):
    """
    Plone constructor
    """
    return manage_addBLSubsidiaryTransaction(self, id=id, title=title)


class BLSubsidiaryTransaction(BLTransaction):
    """
    A transaction in a subsidiary ledger, which will apply to a control account
    in the general ledger
    """
    meta_type = portal_type = 'BLSubsidiaryTransaction'

    __ac_permissions__ = BLTransaction.__ac_permissions__ + (
        (access_contents_information, ('controlAccount',)),
        (OperateBastionLedgers, ('setControlAccount',)),
    )

    def __init__(self, id, title, effective, reference, tags, notes, control):
        BLTransaction.__init__(
            self, id, title, effective, reference, tags, notes)
        self._control_account = control

    def filtered_meta_types(self, user=None):
        """ """
        if self.status() in ['incomplete', 'complete']:
            return [ProductsDictionary('BLEntry'),
                    ProductsDictionary('BLSubsidiaryEntry')]
        return[]

    def _setObject(self, id, object, Roles=None, User=None, set_owner=1):
        #
        # auto-control the acceptable debit/credit sides to this ledger ...
        #
        assert object.meta_type in ('BLEntry', 'BLSubsidiaryEntry'), \
            "Must be derivative of BLEntry!"

        for control in self.blLedger().controlAccounts():
            assert object.account != 'Ledger/%s' % control.getId(), \
                "Cannot transact against Control Account: %s (%s)" % (
                    control.prettyTitle(), str(self))

        BLTransaction._setObject(self, id, object, Roles, User, set_owner)
        # self.setStatus()

    def createEntry(self, account, amount, title='', subsidiary=True):
        """
        create an entry without having to worry about entry type
        """
        if amount == 0:
            return None

        if subsidiary:
            if type(account) == types.StringType:
                try:
                    account = self.aq_parent._getOb(account)
                except:
                    raise InvalidAccount(account)
            id = self.manage_addProduct[
                'BastionLedger'].manage_addBLSubsidiaryEntry(account, amount, title)
            return self._getOb(id)

        # it's actually on the GL ...
        if type(account) == types.StringType:
            try:
                account = self.Ledger._getOb(account)
            except:
                raise InvalidAccount(account)

        return BLTransaction.createEntry(self, account, amount, title)

    def controlAccount(self):
        """
        return the control account for this transaction
        """
        return self.aq_parent.controlAccount(self._control_account)

    def _controlEntry(self):
        """
        return the control entry for this transaction
        """
        return self.aq_parent.controlEntry(self._control_account)

    def accountId(self):
        """
        the control account id (overloaded to share existing index)
        """
        return self._control_account

    def setControlAccount(self, controlid, REQUEST=None):
        """
        """
        if controlid != self._control_account:
            ledger = self.aq_parent
            if controlid not in ledger._control_accounts:
                raise LedgerError(controlid)
            self._control_account = controlid
            self.bastionLedger().catalog_object(self, idxs=['accountId'])
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _repair(self):
        if self._control_account is None:
            self.setControlAccount(self.aq_parent._defaultControl().getId())

AccessControl.class_init.InitializeClass(BLSubsidiaryTransaction)
