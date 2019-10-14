#
#    Copyright (C) 2002-2018  Corporation of Balclutha. All rights Reserved.
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
import operator
import string
import sys
import traceback
from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens, change_permissions, \
    access_contents_information
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from DocumentTemplate.DT_Util import html_quote
from ExtensionClass import Base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BastionBanking.ZCurrency import ZCurrency
from OFS.ObjectManager import BeforeDeleteException
from zope.interface import implementer
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from BLBase import *
from utils import assert_currency, floor_date, ceiling_date
from BLAttachmentSupport import BLAttachmentSupport
from Permissions import OperateBastionLedgers, OverseeBastionLedgers, ManageBastionLedgers
from Exceptions import PostingError, UnpostedError, IncorrectAmountError, \
    IncorrectAccountError, InvalidTransition, UnbalancedError
from interfaces.transaction import ITransaction, IEntry
import logging

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

LOG = logging.getLogger('BLTransaction')


def _addEntryToTransaction(transaction, ledger, klass, account, amount, title='', id=None):
    """
    helper to validity check and add/aggregate a generic entry
    """
    assert isinstance(transaction, BLTransaction), \
        'Woa - accounts are ONLY manipulated via transactions!'

    # hmmm - an empty status is because workflow tool hasn't yet got to it ...
    assert transaction.status() in ('incomplete', 'complete'), \
        'Woa - invalid txn state (%s)' % (str(transaction))

    if not isinstance(amount, ZCurrency):
        amount = ZCurrency(amount)

    if type(account) == types.StringType:
        account = ledger._getOb(account)

    # aggregate to existing entry??
    entry = transaction.blEntry(account.getId(), ledger.getId())
    if entry is None:
        if not id:
            id = transaction.generateId()

        entry = klass(id, title, account.getId(), amount)
        transaction._setObject(id, entry)
    else:
        id = entry.getId()
        if entry.amount.currency() == amount.currency:
            entry.amount += amount
        else:
            entry.amount += transaction.portal_bastionledger.convertCurrency(amount,
                                                                             transaction.effective_date,
                                                                             entry.amount.currency())
    return transaction._getOb(id)


manage_addBLTransactionForm = PageTemplateFile(
    'zpt/add_transaction', globals())


def manage_addBLTransaction(self, id='', title='', effective=None,
                            ref='', entries=[], tags=[], notes='', REQUEST=None):
    """ add a transaction """
    if ref:
        try:
            ref = '/'.join(ref.getPhysicalPath())
        except:
            pass

    if not id:
        id = self.nextTxnId()

    effective = effective or DateTime()
    if type(effective) == types.StringType:
        effective = DateTime(effective)
    effective.toZone(self.timezone)

    txn = BLTransaction(id, title, effective, ref, tags, notes)
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
        try:
            manage_addBLEntry(txn, entry.account, entry.amount, entry.title)
        except NameError:
            # doh - more cyclic dependencies ...
            from BLEntry import manage_addBLEntry
            manage_addBLEntry(txn, entry.account, entry.amount, entry.title)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % txn.absolute_url())

    return id


def addBLTransaction(self, id, title='', effective=None):
    """
    Plone constructor - we generated this id via our own generateUniqueId function
    in BLLedger ...
    """
    return manage_addBLTransaction(self, id=id, title=title, effective=effective)


@implementer(ITransaction)
class BLTransaction(LargePortalFolder, BLAttachmentSupport):

    meta_type = portal_type = 'BLTransaction'


    __ac_permissions__ = LargePortalFolder.__ac_permissions__ + (
        (view_management_screens, ('manage_verify',)),
        (access_contents_information, ('isMultiCurrency', 'isFX', 'faceCurrencies', 'isAgainst', 'SearchableText',
                                       'currencies', 'effective', 'hasTag', 'isForward')),
        (OperateBastionLedgers, ('manage_post', 'manage_editProperties', 'manage_toggleDRCR',
                                 'manage_toggleAccount', 'createEntry', 'manage_bookFx',
                                 'manage_propertiesForm', 'setStatus', 'addEntries', 'editProperties',
                                 'manage_statusModify', 'manage_editEntries', 'manage_editEffective')),
        (OverseeBastionLedgers, ('manage_reverse', 'manage_cancel', 'manage_merge', 'manage_repost',
                                 'manage_unpost')),
        (view, ('asXML', 'referenceUrl', 'referenceId', 'dateStr', 'blLedger', 'debitTotal',
                'creditTotal', 'total', 'modificationTime', 'created', 'creationTime',
                'blEntry', 'entryIds', 'entryItems', 'entryValues', 'modifiable')),
    ) + BLAttachmentSupport.__ac_permissions__

    _v_already_looking = 0
    tags = ()
    notes = ''

    manage_options = (
        {'label': 'Entries',    'action': 'manage_main',
         'help': ('BastionLedger', 'transaction.stx')},
        {'label': 'View',       'action': '', },
        BLAttachmentSupport.manage_options[0],
        {'label': 'Verify',       'action': 'manage_verify', },
    ) + PortalContent.manage_options

    manage_main = PageTemplateFile('zpt/view_transaction', globals())

    #manage_main = LargePortalFolder.manage_main

    asXML = PageTemplateFile('zpt/xml_txn', globals())

    _properties = (
        {'id': 'title',          'type': 'string',    'mode': 'w'},
        {'id': 'effective_date', 'type': 'date',
            'mode': 'w'},  # this is Dublin Core!!
        {'id': 'entered_by',     'type': 'string',    'mode': 'r'},
        {'id': 'reference',      'type': 'string',    'mode': 'w'},
        {'id': 'tags',           'type': 'lines',     'mode': 'w'},
        {'id': 'notes',          'type': 'text',      'mode': 'w'},
    )

    def __init__(self, id, title, effective, reference, tags, notes):
        LargePortalFolder.__init__(self, id)
        self.title = title
        self.effective_date = floor_date(effective)
        self.entered_by = getSecurityManager().getUser().getUserName()
        self.reference = reference
        self.tags = tuple(tags)
        self.notes = notes

    #
    # a reference may or may not be a reference to an object on the system ...
    #
    def referenceObject(self):
        """
        return the object that's referenced to this transaction
        """
        if self.reference:
            try:
                return self.unrestrictedTraverse(self.reference)
            except:
                pass
        return None

    def referenceUrl(self):
        if self.reference:
            try:
                return self.unrestrictedTraverse(self.reference).absolute_url()
            except:
                pass
        return None

    def referenceId(self):
        return string.split(self.reference, '/').pop()

    def hasTag(self, tag):
        """
        """
        return tag in self.tags

    def dateStr(self): return self.day.strftime('%Y-%m-%d %H:%M:%S')

    def blLedger(self):
        #
        # Transactions are buried within the 'Transactions' folder of a Ledger ...
        #
        return self.aq_parent

    def transactionId(self):
        """
        indexing
        """
        return self.getId()

    def all_meta_types(self):
        """ """
        return [ProductsDictionary('BLEntry')]

    def filtered_meta_types(self, request=None):
        """ """
        if self.status() in ['incomplete', 'complete']:
            return [ProductsDictionary('BLEntry')]
        return []

    def defaultCurrency(self):
        """
        """
        return self.aq_parent.defaultCurrency()

    def isMultiCurrency(self):
        """
        return whether or not this transaction has entries in different currencies
        """
        return len(self.faceCurrencies()) > 1

    def isFX(self):
        """
        return whether or not transaction has entries with fx rate applies (must be posted to be fx)
        """
        entries = self.entryValues()

        return entries and reduce(operator.add, map(lambda x: x.foreignRate(), entries)) != 0.0

    def faceCurrencies(self):
        """
        return a tuple of the currencies represented in the transaction
        """
        currencies = {}
        for amt in map(lambda x: x.amount, self.entryValues()):
            currencies[amt.currency()] = True

        return currencies.keys()

    def currencies(self):
        """
        return all the currencies in which this transaction can be historically valued in
        """
        currencies = self.faceCurrencies()
        for currency in self.foreignCurrencies():
            if currency not in currencies:
                currencies.append(currency)

        return currencies

    def debitTotal(self, currency=''):
        """ sum all the debits """
        base = currency or self.aq_parent.defaultCurrency()
        total = ZCurrency(base, 0.0)
        for entry in filter(lambda x: x.amount > 0, self.entryValues()):
            total += entry.amountAs(base)

        return total

    def creditTotal(self, currency=''):
        """ sum all the credits - effective is for currency rate(s)"""
        base = currency or self.aq_parent.defaultCurrency()
        total = ZCurrency(base, 0.0)
        for entry in filter(lambda x: x.amount < 0, self.entryValues()):
            total += entry.amountAs(base)

        return total

    def total(self, currency=''):
        """ sum all the debits and credits - effective is for currency rate(s) """
        base = currency or self.aq_parent.defaultCurrency()
        return self.debitTotal(base) + self.creditTotal(base)

    def creationTime(self, format='%Y-%m-%d %H:%M'):
        """
        when transaction was entered into system
        """
        return self.creation_date.strftime(format)

    def created(self):
        """
        index function
        """
        return self.creation_date

    def modificationTime(self, format='%Y-%m-%d %H:%M'):
        """ 
        when transaction was last edited
        """
        return self.bobobase_modification_time().strftime(format)

    def setReference(self, ob):
        if not self.reference:
            self._updateProperty('reference', '/'.join(ob.getPhysicalPath()))

    def setStatus(self, cascade=True, REQUEST=None):
        """
        does automatic status promotions - as all these functions are private :(
        """
        wftool = getToolByName(self, 'portal_workflow')
        status = self.status()

        base = self.defaultCurrency()

        if not len(self.objectIds()):
            if status != 'incomplete':
                self._status('incomplete', cascade)
            return

        if status == 'incomplete':
            if self.debitTotal(currency=base) == -self.creditTotal(currency=base):
                #wf = wftool.getWorkflowsFor(self)[0]
                #wf._executeTransition(self, wf.transitions.complete)
                #status = 'complete'
                self._status('complete', cascade)
        elif status == 'complete':
            if self.debitTotal(currency=base) != -self.creditTotal(currency=base):
                #wf = wftool.getWorkflowsFor(self)[0]
                #wf._executeTransition(self, wf.transitions.incomplete)
                #status = 'incomplete'
                self._status('incomplete', cascade)
        elif status != 'reversed':
            self._status('posted', cascade)

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def type(self):
        # ensure no cataloging of this field
        return None

    def manage_editEffective(self, effective, REQUEST=None):
        """
        """
        self._updateProperty('effective_date', effective)
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _updateProperty(self, name, value):
        LargePortalFolder._updateProperty(self, name, value)
        if name in ('tags',):
            self.bastionLedger().catalog_object(
                self, '/'.join(self.getPhysicalPath()), idxs=[name])
        elif name in ('effective_date',):
            self._cascadeIndex(['effective'])
        elif name == 'title':
            # go set untitled entries to this description ...
            for entry in self.entryValues():
                if not entry.title:
                    entry._updateProperty('title', value)
            # we recatalog entries via SearchableText ...
            self.bastionLedger().catalog_object(
                self, '/'.join(self.getPhysicalPath()), idxs=['SearchableText'])

    def addEntries(self, entries):
        """
        Allow scripts to add entries ...
        entries may be BLEntry-derived, or a list of hash's keyed on account, amount, title (optional)
        """
        for e in entries:
            if IEntry.providedBy(e):
                _addEntryToTransaction(
                    self, self.blLedger(), e.__class__, e.blAccount(), e.amount)
            else:
                try:
                    self.createEntry(
                        e['account'], e['amount'], e.get('title', ''))
                except AttributeError:
                    raise ValueError(e)

    def createEntry(self, account, amount, title='', subsidiary=False):
        """
        create an entry without having to worry about entry type
        ignore subsidiary ...
        """
        if amount == 0:
            return None
        if type(account) == types.StringType:
            account = self.aq_parent._getOb(account)
        id = self.manage_addProduct[
            'BastionLedger'].manage_addBLEntry(account, amount, title)
        return self._getOb(id)

    def entryIds(self):
        """
        return ids of entries
        """
        return self.objectIds(('BLEntry', 'BLSubsidiaryEntry'))

    def entryValues(self, ledger_id=''):
        """
        list of entries
        """
        if ledger_id == '':
            return self.objectValues(('BLEntry', 'BLSubsidiaryEntry'))
        return filter(lambda x: x.ledgerId() == ledger_id,
                      self.objectValues(('BLEntry', 'BLSubsidiaryEntry')))

    def entryItems(self, ledger_id=''):
        """
        """
        if ledger_id == '':
            return self.objectItems(('BLEntry', 'BLSubsidiaryEntry'))
        return filter(lambda x: x[1].ledgerId() == ledger_id,
                      self.objectItems(('BLEntry', 'BLSubsidiaryEntry')))

    def blEntry(self, account_id, ledger_id=''):
        """ retrieve an entry that should be posted to indicated account in indicated ledger"""
        for v in self.entryValues():
            if v.accountId() == account_id:
                if ledger_id == '' or v.blLedger().getId() == ledger_id:
                    return v
        return None

    def isAgainst(self, accnos, ledger_id):
        """
        return if this transaction affects any of the accounts from specified ledger
        """
        for v in self.entryValues():
            if v.accountId() in accnos and v.blLedger().getId() == ledger_id:
                return True
        return False

    def _post(self, force=False):
        """
        perform the underlying post operation
        """
        for entry in self.entryValues():
            try:
                entry._post(force)
            except PostingError:
                raise
            except:
                # raise a very meaningful message now!!
                typ, val, tb = sys.exc_info()
                fe = traceback.format_exception(typ, val, tb)
                raise AttributeError('%s\n%s' % ('\n'.join(fe), str(self)))

    def manage_merge(self, txn_ids, force=False, REQUEST=None):
        """
        merge another transaction from the same ledger into this one
        """
        status = self.status()
        base = self.defaultCurrency()

        if status in ('reversed', 'cancelled'):
            raise PostingError(txn_ids)

        ledger = self.aq_parent

        if status == 'posted':
            # need to untotalise ...
            self.manage_unpost()

        for txn_id in txn_ids:
            txn = ledger._getOb(txn_id)
            if txn.status() not in ('posted', 'incomplete', 'complete'):
                raise PostingError(txn)
            self.addEntries(txn.entryValues())
            for attachment in txn.attachmentValues():
                self.manage_addAttachment(attachment)

        # delete first to ensure last transaction date on posting
        ledger.manage_delObjects(txn_ids)

        # (re)post - to recompute totalisations ...
        if status == 'posted':
            self.manage_post()
        elif status in ('incomplete', 'complete'):
            if self.debitTotal(currency=base) == -self.creditTotal(currency=base):
                self._status('complete')
            else:
                self._status('incomplete')

        if REQUEST:
            REQUEST.set('manage_tabs_message',
                        'merged transactions %s' % ', '.join(txn_ids))
            return self.manage_main(self, REQUEST)

    def manage_post(self, REQUEST=None):
        """
        post transaction entries  - note we do not post zero-amount entries!
        """
        status = self.status()

        if status in ('reversed', 'cancelled'):
            if REQUEST:
                return self.manage_main(self, REQUEST)
            return

        # we're flicking the status to posted in the workflow too soon in order to
        # ensure correct status when cataloging the account entries
        if status in ('incomplete', 'posted'):
            message = 'Transaction %s %s != %s' % (
                status, self.debitTotal(), self.creditTotal())
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return self.manage_main(self, REQUEST)
            raise PostingError("%s\n%s" % (message, str(self)))

        if self.effective_date > DateTime():
            if not getToolByName(self, 'portal_bastionledger').allow_forwards:
                message = 'Future-dated transactions not allowed!'
                if REQUEST is not None:
                    REQUEST.set('manage_tabs_message', message)
                    return self.manage_main(self, REQUEST)
                raise PostingError("%s\n%s" % (message, str(self)))
            self._forward = True

        self._post()
        self._status('posted')
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

    def manage_toggleDRCR(self, ids=[], REQUEST=None):
        """
        flip the dr/cr on selected entries (or all if none selected) - useful to correct keying errors
        """
        if ids == []:
            ids = self.entryIds()

        for id, entry in filter(lambda x, ids=ids: x[0] in ids, self.entryItems()):
            entry._updateProperty('amount', -entry.amount)
            # self.setStatus()

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_toggleAccount(self, old, new, REQUEST=None):
        """
        remove the old entry (account id), replacing amount with new entry
        """
        status = self.status()
        entry = self.blEntry(old)

        if entry.blLedger()._getOb(new, None) == None:
            raise IncorrectAccountError(new)

        # only bother with reposting posted stuff - otherwise it's eye candy
        if entry:
            if status == 'posted':
                self.manage_unpost()
            entry.manage_changeProperties(account=new)
            if status == 'posted':
                self.manage_post()

        if self.status() != status:
            self._status(status)

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_verify(self, precision=0.05, REQUEST=None):
        """
        verify the transaction has been applied correctly to the ledger(s)

        precision defaults to five cents

        this function deliberately *does not* use the underlying object's methods
        to check this - it's supposed to independently check the underlying
        library - or consequent tamperings via the ZMI

        it returns a list of (Exception, note) tuples
        """
        bad_entries = []

        entries = self.entryValues()
        status = self.status()

        if status in ('posted', 'reversed'):

            #
            # make sure the transaction balanced (within 5 cents) in the first place ...
            #
            if abs(self.total()) > precision:
                bad_entries.extend(
                    map(lambda x: (UnbalancedError(x), self.total()), entries))
            else:
                #
                # check that the posted entries are consistent with the balanced txn ...
                #
                base_currency = self.defaultCurrency()
                for unposted in entries:
                    account = unposted.blAccount()
                    try:
                        posted = account.blEntry(self.getId())
                    except:
                        # hmmm - dunno why we should have posted zero-amount transactions,
                        # but they're not wrong ...
                        if unposted.amount == 0:
                            continue
                        bad_entries.append((UnpostedError(unposted), ''))
                        continue

                    posted_acc = posted.blAccount()
                    if posted_acc != account:
                        bad_entries.append((IncorrectAccountError(unposted),
                                            '%s/%s' % (posted_acc.ledgerId(), posted_acc.getId())))
                        continue

                    posted_amt = posted.amount
                    unposted_amt = unposted.amount

                    # find/use common currency base
                    if posted_amt.currency() != base_currency:
                        posted_amt = posted.amountAs(base_currency)

                    if unposted_amt.currency() != base_currency:
                        unposted_amt = unposted.amountAs(base_currency)

                    # 5 cent accuracy ...
                    if abs(posted_amt - unposted_amt) > 0.05:
                        # raise AssertionError ((unposted.getId(), unposted.blAccount(), unposted.amount, unposted_amt),
                        #                      (posted.getId(), posted.blAccount(), posted.amount, posted_amt))
                        bad_entries.append((IncorrectAmountError(unposted),
                                            '%s/%s' % (posted_amt, posted_amt - unposted_amt)))

        #
        # we shouldn't be posting these ...
        #
        if status in ('cancelled', 'incomplete'):
            for entry in entries:
                try:
                    posted = entry.blAccount()._getOb(self.getId())
                    bad_entries.append((PostingError(posted), ''))
                except:
                    continue

        if status in ('complete'):
            for entry in entries:
                try:
                    posted = entry.blAccount()._getOb(self.getId())
                    bad_entries.append((PostingError(posted), ''))
                except:
                    continue

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

    def __getattr__(self, name):
        """
        returns the attribute or matches on title of the entries within ...
        """
        if not self._v_already_looking:
            try:
                #LOG.debug( "__getattr__(%s)" % name)
                self._v_already_looking = 1
                if self.__dict__.has_key(name):
                    return self.__dict__[name]

                # we are expecting just BLEntry deriviatives ...
                for entry in self.objectValues():
                    if entry.title == name:
                        return entry
            finally:
                self._v_already_looking = 0
        # not found - pass it on ...
        return Base.__getattr__(self, name)

    def manage_unpost(self, force=False, REQUEST=None):
        """
        remove effects of posting
        """
        if force or self.status() == 'posted':
            for entry in self.entryValues():
                entry._unpost()
            if getattr(aq_base(self), '_forward', None):
                delattr(self, '_forward')
            self._status('complete')

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_editProperties(self, REQUEST):
        """ Overridden to make sure recataloging is done """
        for prop in self._propertyMap():
            name = prop['id']
            if 'w' in prop.get('mode', 'wd'):
                value = REQUEST.get(name, None)
                if value is not None:
                    self._updateProperty(name, value)

        # cascade catalog update to entries (for tags at least...)
        bl = self.bastionLedger()
        bl.catalog_object(self, '/'.join(self.getPhysicalPath()))
        for entry in self.entryValues():
            bl.catalog_object(entry, '/'.join(entry.getPhysicalPath()))

    def editProperties(self, title='', description='', effective=None, tags=[], notes=''):
        """
        Plone form updates
        """
        self.title = title
        self.description = description
        if effective is not None:
            self.effective_date = floor_date(effective)
        self._updateProperty('tags', tags)
        self._updateProperty('notes', notes)
        # cascade catalog update to entries (for tags at least...)
        bl = self.bastionLedger()
        bl.catalog_object(self, '/'.join(self.getPhysicalPath()))
        for entry in self.entryValues():
            bl.catalog_object(entry, '/'.join(entry.getPhysicalPath()))

    def manage_editEntries(self, entries, REQUEST=None):
        """
        entries is a list of Records or hashes
        use/set id field if also want to change account(s)
        """
        repost = False
        if self.status() == 'posted':
            repost = True
            self.manage_unpost()

        eid = ''

        for entry in entries:
            if isinstance(entry, dict):
                title = entry.get('title', '')
                amount = entry['amount']
                account = entry['account']
                if entry.has_key('id'):
                    eid = entry['id']
            else:
                # it's a Record ...
                title = entry.title
                amount = isinstance(
                    entry.amount, ZCurrency) and entry.amount or ZCurrency(entry.amount)
                amount = entry.credit and -amount or amount
                account = entry.account
                if hasattr(entry, 'id'):
                    eid = entry.id

            # acc path may or may not be ledger/accno (ie for subsidiary)
            if account.find('/') != -1:
                ledid, accid = account.split('/')
            else:
                ledid, accid = self.aq_parent.getId(), account

            if eid:
                e = self._getOb(eid)
            else:
                e = self.blEntry(accid, ledid)
                if e is None:
                    raise KeyError('%s/%s' % (ledid, accid))

            if accid != e.accountId() and ledid != e.ledgerId():
                e.manage_changeAccount(account)
            e.manage_changeProperties(title=title, amount=amount)

        if repost:
            try:
                self.manage_post()
            except PostingError:
                # just leave it back to unposted - they'll be doing future
                # editing ...
                pass

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Edited Transaction')
            return self.manage_main(self, REQUEST)

    def modifiable(self):
        """
        returns whether or not this transaction is still editable.  This means
        either in a non-posted state, or you've roles enough to repost it.
        """
        return self.status() in ('complete', 'incomplete') or \
            self.SecurityCheckPermission(ManageBastionLedgers)

    def manage_bookFx(self, entries, REQUEST=None):
        """
        book/change FX (and thus base currency postings) of transaction
        """
        repost = False
        eid = None
        if self.status() == 'posted':
            repost = True
            self.manage_unpost()

        for entry in entries:
            if isinstance(entry, dict):
                if not entry.has_key('fxrate'):
                    continue
                account = entry['account']
                fx = entry['fxrate']
                if entry.has_key('id'):
                    eid = entry['id']
            else:
                # it's a Record ...
                if not hasattr(entry, 'fxrate'):
                    continue
                account = entry.account
                fx = entry.fxrate
                if hasattr(entry, 'id'):
                    eid = entry.id

            # acc path may or may not be ledger/accno (ie for subsidiary)
            if account.find('/') != -1:
                ledid, accid = account.split('/')
            else:
                ledid, accid = self.aq_parent.getId(), account

            if eid:
                e = self._getOb(eid)
            else:
                e = self.blEntry(accid, ledid)
                if e is None:
                    raise KeyError('%s/%s' % (ledid, accid))

            e._setForeignAmount(fx, force=True)

        if repost:
            try:
                self.manage_post()
            except PostingError:
                # just leave it back to unposted - they'll be doing future
                # editing ...
                pass

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_reverse(self, description='', effective=None, REQUEST=None):
        """
        create a reversal transaction
        """
        status = self.status()
        if status != 'posted':
            if REQUEST:
                REQUEST.set('manage_tabs_message',
                            'Transaction not in Posted state!')
                return self.manage_main(self, REQUEST)
            raise PostingError('%s: Transaction not in Posted state (%s)!' % (self.getId(), status))

        txn = self.createTransaction(title=description or 'Reversal: %s' % self.title,
                                     effective=effective or self.effective_date)
        txn.setReference(self)

        for id, entry in self.entryItems():
            e = entry._getCopy(entry)
            e.amount = entry.amount * -1
            e.title = 'Reversal: %s' % entry.title
            # ensure the new entry does proper fx ...
            if getattr(entry, 'posted_amount', None):
                e.posted_amount = entry.posted_amount * -1
            txn._setObject(id, e)

        txn.manage_post()
        txn._status('postedreversal')

        self.setReference(txn)
        self._status('reversed')

        if not REQUEST:
            return txn
        return self.manage_main(self, REQUEST)

    def manage_cancel(self, REQUEST=None):
        """
        cancel a transaction
        """
        status = self.status()
        if status in ('incomplete', 'complete'):
            self._status('cancelled')
        else:
            raise InvalidTransition('cancel')

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_repost(self, force=False, REQUEST=None):
        """
        hmmm, sometimes/somehow stuff gets really f**ked up ...

        we also post complete txns - which could be processed via manage_post

        force causes fx/posted amounts to be recalculated and account totalisation
        to recur
        """
        status = self.status()
        if status in ('posted',):
            for entry in self.entryValues():
                try:
                    # if entry.absAmount() > 0.005:
                    entry._post(force=force)
                except PostingError:
                    raise
            self._status('posted')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_statusModify(self, workflow_action, REQUEST=None):
        """
        perform the workflow (very Plone ...)
        """
        # below tries to update dublin core data in the Plone catalog ...
        # self.content_status_modify(workflow_action)
        self.manage_changeStatus('bltransaction_workflow', workflow_action)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'State Changed')
            return self.manage_main(self, REQUEST)

    def __str__(self):
        """ useful for debugging ... """
        if self.tags:
            return '<%s instance %s (%s)>:\n"%s"\n%s\n\t%s' % (self.meta_type,
                                                               self.absolute_url(
                                                                   1),
                                                               self.status(),
                                                               self.Description() or self.Title(),
                                                               ','.join(
                                                                   self.tags),
                                                               '\n\t'.join(map(lambda x: str(x), self.entryValues())))
        else:
            return '<%s instance %s (%s)>:\n"%s"\n\t%s' % (self.meta_type,
                                                           self.absolute_url(
                                                               1),
                                                           self.status(),
                                                           self.Description() or self.Title(),
                                                           '\n\t'.join(map(lambda x: str(x), self.entryValues())))

    def __cmp__(self, other):
        """
        transactions are only the same if they've the same txn no. 
        this function is mainly for sorting based on effective date
        note that it's a *descending* (latest first) sort
        """
        if not isinstance(other, BLTransaction):
            return 1
        if self.getId() == other.getId():
            return 0
        if self.effective_date < other.effective_date:
            return 1
        else:
            return -1

    def asCSV(self, datefmt='%Y/%m/%d', REQUEST=None):
        """
        """
        return '\n'.join(map(lambda x: x.asCSV(datefmt), self.entryValues()))

    def _repair(self):
        if getattr(aq_base(self), 'entered_date', None):
            delattr(self, 'entered_date')
        map(lambda x: x._repair(), self.objectValues())

    def manage_migrateFX(self, REQUEST=None):
        """
        in the past, we posted the fx rate into the fx_rate attribute of the posted entry
        now, we're actually going to post the txn's entry amount into the posted entry
        """
        if self.isMultiCurrency():
            # recalculate fx_rate
            self.manage_repost(force=True)

            for entry in self.entryValues():
                posted_amount = getattr(aq_base(entry), 'posted_amount', None)
                if posted_amount:
                    delattr(entry, 'posted_amount')

            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Fixed up FX')
        else:
            if REQUEST:
                REQUEST.set('manage_tabs_message',
                            'Non-FX transaction - nothing to do')

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def isForward(self):
        """
        return whether or not this is/was a forward-posted transaction
        """
        return self.status() == 'posted' and getattr(aq_base(self), '_forward', None)

    def _cascadeIndex(self, idxs=[]):
        cat = self.bastionLedger()
        try:
            if idxs:
                cat.catalog_object(
                    self, '/'.join(self.getPhysicalPath()), idxs=idxs)
            else:
                cat.catalog_object(self, '/'.join(self.getPhysicalPath()))
            for entry in self.entryValues():
                if idxs:
                    cat.catalog_object(
                        entry, '/'.join(entry.getPhysicalPath()), idxs=idxs)
                else:
                    cat.catalog_object(entry, '/'.join(entry.getPhysicalPath()))
        except AttributeError:
            # hmmm some old skool/borked catalog thingy (and probably during a ledger delete)...
            pass
        
    def _status(self, status, cascade=True):
        """
        set the status - updating indexes (cascading to entries if true)
        """
        LargePortalFolder._status(self, status, local_index=cascade == False)
        if cascade:
            self._cascadeIndex(['status'])

    def SearchableText(self):
        """
        indexing helper - assure entries drag txn into searches
        """
        title = self.Title()
        texts = [title]
        # TODO notes ?
        for etitle in map(lambda x: x.Title(), self.entryValues()):
            if etitle != title:
                texts.append(etitle)

        return ' '.join(texts) + self.attachmentSearchableText()


AccessControl.class_init.InitializeClass(BLTransaction)


# deprecated API ...
class BLTransactions(LargePortalFolder, ZCatalog):
    pass


def addTransaction(ob, event):
    catalogAdd(ob, event)

    # f**k!! on import we have to recompute state so indexes (and the entire app)
    # aren't f**ked
    ob.setStatus()


def delTransaction(ob, event):

    catalogRemove(ob, event)

    # seems entries get recataloged during the txn setStatus() - dunno why the entry
    # is *still* in the container; so we're cleaning that up here ...

    for entry in ob.entryValues():
        catalogRemove(entry, None)


def cloneTransaction(ob, event):
    ob._status('complete')
