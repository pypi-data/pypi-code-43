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

import unittest

from LedgerTestCase import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import floor_date
from Products.AdvancedQuery import Between, Eq, In
from Products.BastionLedger.BLGlobals import EPOCH
from Products.BastionLedger.interfaces.transaction import IEntry
from Products.BastionLedger.Exceptions import PostingError
from Record import Record


class entryrec(Record):
    __record_schema__ = {'account': 0, 'amount': 1, 'credit': 2, 'title': 3}


def txnQ(ledger, effective):
    return map(lambda x: x.getObject(),
               ledger.bastionLedger().evalAdvancedQuery(Eq('meta_type', 'BLEntry') & Between('effective', effective - 1, effective + 1)))


def accQ(ledger, effective):
    return map(lambda x: x.getObject(),
               ledger.bastionLedger().evalAdvancedQuery(Eq('meta_type', 'BLEntry') & Between('effective', effective - 1, effective + 1)))


class TestTransaction(LedgerTestCase):
    """
    verify transaction workflow
    """

    def _mkTxn(self, effective, acc1, acc2, amount, title='My Txn', tags=[]):
        txn = self.ledger.Ledger.createTransaction(
            title=title, effective=effective, tags=tags)
        txn.createEntry(acc1, amount)
        txn.createEntry(acc2, -amount)
        return txn

    def testTimestamps(self):
        effective = DateTime('2012/01/01')
        now = DateTime()
        self.loginAsPortalOwner()
        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))

        self.assertEqual(txn.effective(), effective)
        self.assertEqual(txn.creationTime()[:10], now.strftime('%Y-%m-%d'))
        self.assertEqual(txn.modificationTime()[:10], now.strftime('%Y-%m-%d'))

    def testTags(self):
        effective = DateTime('2012/01/01')
        now = DateTime()
        self.loginAsPortalOwner()
        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'), tags=['bla'])

        self.assertEqual(txn.tags, ('bla',))
        self.assertEqual(map(lambda x: x.getObject(),
                             self.ledger.evalAdvancedQuery(Eq('meta_type', 'BLTransaction') & Eq('tags', 'bla'))), [txn])

        # verify ~ query (vis a vis EOP)
        num_ents = len(self.ledger.entryValues())
        self.assertEqual(len(self.ledger.evalAdvancedQuery(
            Eq('meta_type', 'BLEntry') & ~In('tags', ['bla']))), num_ents - 2)

    def testEntries(self):
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()
        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))

        self.assertEqual(len(txn.entryIds()), 2)
        self.assertEqual(len(txn.entryValues()), 2)

        entry = txn.entryValues()[0]

        self.assertEqual(entry.meta_type, 'BLEntry')
        self.assertTrue(IEntry.providedBy(entry))
        # eek !!
        # self.assertTrue(IEntry.implementedBy(entry))

        txn.manage_delObjects([entry.getId()])
        self.assertEqual(len(txn.entryIds()), 1)
        self.assertEqual(txn.status(), 'incomplete')

    def testACLUsers(self):
        # TODO - acl_users is/was getting cataloged in testing - wtf ...
        self.loginAsPortalOwner()
        self.maxDiff = None
        #self.assertEqual(len(self.ledger.searchResults()), self.NUMBER_ACCOUNTS)
        self.assertFalse(
            'Control_Panel/plone/acl_users' in self.ledger._catalog.uids.keys())

    def testCataloging(self):
        ledger = self.portal.ledger.Ledger
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        INDEX_COUNT = len(
            self.ledger.evalAdvancedQuery(Eq('status', 'posted')))

        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))
        entry = txn.entryValues()[0]

        self.assertTrue(txn.unrestrictedTraverse('@@uuid'))
        self.assertTrue(entry.unrestrictedTraverse('@@uuid'))

        self.assertEqual(txn.isMultiCurrency(), False)

        self.assertEqual(len(txnQ(ledger, effective)), 2)
        self.assertEqual(len(ledger.A000002.entryValues()), 0)

        self.assertEqual(len(self.ledger.evalAdvancedQuery(
            Eq('status', 'posted'))), INDEX_COUNT)
        self.assertEqual(len(txnQ(ledger, effective)), 2)
        self.assertEqual(len(ledger.A000002.entryValues()), 0)

        txn.manage_post()

        # TODO - figure out how to differentiate between acc & txn entries
        self.assertEqual(len(txnQ(ledger, effective)), 2)

        self.assertEqual(len(self.ledger.evalAdvancedQuery(
            Eq('accountId', 'A000002') & Eq('meta_type', 'BLEntry'))), 1)
        self.assertEqual(len(self.ledger.evalAdvancedQuery(
            Eq('status', 'posted'))), INDEX_COUNT + 3)  # txn + 2 entries
        # self.assertEqual(map(lambda x: x.getPath(),
        # self.ledger.evalAdvancedQuery(Between('effective', effective-1,
        # effective+1))), 3)
        self.assertEqual(len(self.ledger.evalAdvancedQuery(
            Between('effective', effective - 1, effective + 1))), 3)  # TODO

        self.assertEqual(len(ledger.A000002.entryValues()), 1)
        self.assertEqual(len(ledger.A000002.entryValues(effective + 1)), 1)
        self.assertEqual(len(ledger.A000002.entryValues(
            (effective - 1, effective + 1))), 1)

        # verify high-level search ...
        self.assertEqual(self.portal.ledger.transactionValues(
            status='posted'), [txn])
        self.assertEqual(self.portal.ledger.transactionValues(
            accountId=('A000001',)), [txn])
        self.assertEqual(self.portal.ledger.transactionValues(
            accountId=('A000001', 'A000002')), [txn])

        # enforce deletion/reversal
        ledger.manage_delObjects([txn.getId()])

        self.assertEqual(map(lambda x: '%s %s' % (x['meta_type'], x['id']),
                             self.ledger.evalAdvancedQuery(Eq('status', 'posted'))), [])
        self.assertEqual(len(ledger.A000002.entryValues()), 0)

    def testAggregates(self):
        ledger = self.portal.ledger.Ledger
        self.assertTrue(getattr(ledger, 'portal_workflow', False))
        dt = DateTime()
        tid = ledger.manage_addProduct[
            'BastionLedger'].manage_addBLTransaction(effective=dt)
        txn = ledger._getOb(tid)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', 'GBP 10.00')
        self.assertEqual(txn.total(), ZCurrency('GBP10.00'))
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', 'GBP 10.00')
        self.assertEqual(txn.total(), ZCurrency('GBP 20.00'))
        self.assertEqual(txn.effective(), floor_date(dt))

    def testDisaggregates(self):
        ledger = self.portal.ledger.Ledger
        DT = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        acc = ledger.A000001

        txn1 = self._mkTxn(DT, 'A000001', 'A000002', ZCurrency('GBP 10.00'))
        txn2 = self._mkTxn(DT + 1, 'A000001', 'A000002',
                           ZCurrency('GBP 25.00'))

        txn1.manage_post()
        self.assertEqual(acc.totDate(), DT)
        self.assertEqual(acc._balance, ZCurrency('GBP 10.00'))
        self.assertEqual(acc.balance(effective=DT), ZCurrency('GBP 10.00'))

        self.assertEqual(ledger.lastTransactionDate(), DT)

        txn2.manage_post()
        self.assertEqual(acc.totDate(), DT + 1)
        self.assertEqual(acc._balance, ZCurrency('GBP 35.00'))
        self.assertEqual(acc.balance(effective=DT + 1), ZCurrency('GBP 35.00'))

        self.assertEqual(ledger.lastTransactionDate(), DT + 1)

        ledger.manage_delObjects([txn2.getId()])

        self.assertEqual(ledger.lastTransactionDate(), DT)

        self.assertEqual(acc.totDate(), DT)
        self.assertEqual(acc._balance, ZCurrency('GBP 10.00'))
        self.assertEqual(acc.balance(effective=DT), ZCurrency('GBP 10.00'))

    def testWorkflow(self):
        ledger = self.portal.ledger.Ledger
        self.loginAsPortalOwner()

        now = DateTime('2011/01/01')

        self.assertEqual(map(lambda x: x._unrestrictedGetObject(),
                             self.ledger.searchResults(meta_type='BLTransaction')), [])

        # tid = ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(title='My Txn',
        #                                                                        effective=now)
        # txn = ledger._getOb(tid)
        txn = ledger.createTransaction(title='My Txn', effective=now)

        self.assertEqual(txn.getId(), 'T000000000001')
        self.assertEqual(txn.status(), 'incomplete')

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', 'GBP 10.00')
        self.assertEqual(txn.status(), 'incomplete')

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000002', -ZCurrency('GBP 10.00'))

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 10.00'))
        self.assertEqual(txn.creditTotal(), -ZCurrency('GBP 10.00'))
        self.assertEqual(txn.status(), 'complete')
        self.assertEqual(txn.CreationDate()[
                         :10], DateTime().strftime('%Y-%m-%d'))

        txn.manage_statusModify(workflow_action='post')
        self.assertEqual(txn.status(), 'posted')

        # ensure it's not trashing the title (and effective date)
        self.assertEqual(txn.Title(), 'My Txn')

        account = self.ledger.Ledger.A000001
        entry = account.blEntry(txn.getId())

        self.assertEqual(entry.status(), 'posted')
        self.assertEqual(entry.account, account.getId())
        self.assertEqual(entry.accountId(), account.getId())
        self.assertEqual(entry.blAccount(), account)
        self.assertEqual(entry.blTransaction(), txn)
        self.assertEqual(entry.blLedger(), self.ledger.Ledger)
        self.assertEqual(entry.effective(), txn.effective())
        self.assertEqual(entry.amount, ZCurrency('GBP 10.00'))
        self.assertEqual(entry.isControlEntry(), False)
        self.assertEqual(entry.asQIF(), 'D01/01/11\nT10.00\nN\nPMy Txn\n^\n')

        #
        # hmmm - AEDT timezone's inconsistently f**k these tests ...
        #
        #now = DateTime()
        # self.assertEqual(entry.asCSV(),
        #                 'T000000000001,Ledger,T000000000001,"My Txn","%s", GBP 10.00 ,Ledger/A000001,posted' % now.strftime('%Y/%m/%d'))
        # self.assertEqual(entry.asCSV(datefmt='%Y', curfmt="%0.1f"),
        #                 'T000000000001,Ledger,T000000000001,"My Txn","%s",10.0,Ledger/A000001,posted' % now.strftime('%Y'))

        self.assertEqual(account.entryIds(), [txn.getId()])
        self.assertEqual(account.entryValues(), [entry])
        self.assertEqual(account.sum('A000002'), -ZCurrency('GBP10.00'))
        self.assertEqual(account.sum(
            'A000002', debits=False), -ZCurrency('GBP10.00'))
        self.assertEqual(account.sum('A000002', credits=False),
                         ZCurrency('GBP0.00'))
        self.assertEqual(account.entryValues(), [entry])
        self.assertEqual(account.entryValues([now - 1, now + 1]), [entry])
        self.assertEqual(account.openingBalance(), ZCurrency('GBP 0.00'))
        self.assertEqual(account.openingDate(), EPOCH)
        self.assertEqual(account.openingBalance(EPOCH), ZCurrency('GBP 0.00'))
        self.assertEqual(account.entryValues([EPOCH, now + 1]), [entry])
        self.assertEqual(account.total(
            effective=[EPOCH, now + 1]), ZCurrency('GBP 10.00'))
        self.assertEqual(account.balance(), ZCurrency('GBP 10.00'))

        self.assertEqual(entry, txn.blEntry(account.getId()))

        self.assertEqual(len(ledger.transactionValues()), 1)

        txn.manage_statusModify(workflow_action='reverse')
        self.assertEqual(txn.status(), 'reversed')

        self.assertEqual(len(ledger.transactionValues()), 2)

        self.assertEqual(len(account.entryValues()), 2),
        self.assertEqual(
            len(account.entryValues(status=['postedreversal'])), 1)
        self.assertEqual(len(account.entryValues(status=['reversed'])), 1)

        self.assertEqual(account.balance(), 0)

        reversal_txn = txn.referenceObject()
        self.assertEqual(reversal_txn.getId(), 'T000000000002')
        self.assertEqual(reversal_txn.status(), 'postedreversal')
        self.assertEqual(txn.status(), 'reversed')

        # see if reset ain't broke ...
        self.ledger.manage_reset()

        self.assertEqual(list(ledger.transactionIds()), [])
        self.assertEqual(list(ledger.transactionValues()), [])

    def testAccountToggling(self):
        ledger = self.portal.ledger.Ledger
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))
        txn.manage_toggleAccount('A000002', 'A000003')
        self.assertEqual(txn.blEntry('A000002'), None)
        self.assertTrue(txn.blEntry('A000003'))
        self.assertEqual(txn.blEntry('A000003').amount, -
                         ZCurrency('GBP 10.00'))

        txn.manage_post()
        txn.manage_toggleAccount('A000003', 'A000002')
        self.assertTrue(txn.blEntry('A000002'))
        self.assertEqual(txn.status(), 'posted')

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Ledger
        # doCreate should create the real object
        dt = DateTime('2000/01/01')
        temp_object = ledger.restrictedTraverse(
            'portal_factory/BLTransaction/T000000000099')
        self.assertTrue('T000000000099' in ledger.restrictedTraverse(
            'portal_factory/BLTransaction').objectIds())
        A222222 = temp_object.portal_factory.doCreate(
            temp_object, 'T000000000099')
        self.assertTrue('T000000000099' in ledger.objectIds())

        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse(
            'portal_factory/BLTransaction/T000000000100')
        self.assertTrue('T000000000100' in ledger.restrictedTraverse(
            'portal_factory/BLTransaction').objectIds())
        temp_object.bltransaction_edit(title='Foo', effective=dt)
        self.assertEqual(ledger.transactionValues(
            id='T000000000100')[0].title, 'Foo')
        self.assertTrue('T000000000100' in ledger.objectIds())

        self.assertTrue(abs(temp_object.created() - self.now) < self.RUN_TIME)

    # TODO - how to construct __cp cookie ...
    def _x_testCopy(self):
        ledger = self.portal.ledger.Ledger
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))

        copy_id = ledger._next_txn_id
        ledger.manage_pasteObjects({'__cp': {'ids': [txn.getId()]}})

        new_txn = ledger._getOb(copy_id)
        self.assertEqual(new_txn.status(), 'complete')

    def testMerge(self):
        ledger = self.portal.ledger.Ledger
        DT = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        acc = ledger.A000001

        txn1 = self._mkTxn(DT, 'A000001', 'A000002', ZCurrency('GBP 10.00'))
        txn2 = self._mkTxn(DT + 1, 'A000001', 'A000002',
                           ZCurrency('GBP 20.00'))

        txn1.manage_post()
        self.assertEqual(acc.totDate(), DT)
        self.assertEqual(acc._balance, ZCurrency('GBP 10.00'))
        self.assertEqual(acc.balance(effective=DT), ZCurrency('GBP 10.00'))

        txn2.manage_post()
        self.assertEqual(acc.totDate(), DT + 1)
        self.assertEqual(acc._balance, ZCurrency('GBP 30.00'))
        self.assertEqual(acc.balance(effective=DT + 1), ZCurrency('GBP 30.00'))

        self.assertEqual(len(ledger.transactionValues()), 2)
        self.assertEqual(txn1.debitTotal(), ZCurrency('GBP 10.00'))

        txn1.manage_merge([txn2.getId()], force=True)

        # debug
        #self.assertEqual(str(txn1), '')

        self.assertEqual(len(ledger.transactionValues()), 1)
        self.assertEqual(txn1.debitTotal(), ZCurrency('GBP 30.00'))
        self.assertEqual(txn1.status(), 'posted')

        self.assertEqual(acc.totDate(), DT)
        self.assertEqual(acc._balance, ZCurrency('GBP 30.00'))
        self.assertEqual(acc.balance(effective=DT), ZCurrency('GBP 30.00'))

    def testChangeAccount(self):
        ledger = self.portal.ledger.Ledger
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))

        txn.manage_post()

        txn.blEntry('A000002').manage_changeAccount('A000003')

        self.assertEqual(txn.status(), 'posted')
        self.assertEqual(ledger.A000002.balance(
            effective=effective), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.A000003.balance(
            effective=effective), -ZCurrency('GBP 10.00'))

    def testChangeEffective(self):
        # assure date change is reflected in catalog - for entries too...
        ledger = self.portal.ledger.Ledger
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        for effective in (DateTime('2012/01/01'), DateTime('2012/02/01'), DateTime('2012/03/01')):
            txn = self._mkTxn(effective, 'A000001',
                              'A000002', ZCurrency('GBP 10.00'))
            txn.manage_post()

        self.assertEqual(ledger.A000001.entryIds(), [
                         'T000000000003', 'T000000000002', 'T000000000001'])

        # self.ledger.transactionValues()[0].manage_changeProperties(effective_date=DateTime('2011/12/01'))
        txn = ledger.T000000000003

        txn._updateProperty('effective_date', DateTime('2011/12/01'))

        self.assertEqual(ledger.A000001.entryIds(), [
                         'T000000000002', 'T000000000001', 'T000000000003'])

    def testEditEntriesRecords(self):
        ledger = self.portal.ledger.Ledger
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))

        txn.manage_post()

        e1 = entryrec()
        e2 = entryrec()

        e1.account, e1.amount, e1.credit, e1.title = 'A000001', ZCurrency(
            'GBP 20.00'), False, ''
        e2.account, e2.amount, e2.credit, e2.title = 'A000002', ZCurrency(
            'GBP 20.00'), True, ''

        txn.manage_editEntries([e1, e2])

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 20.00'))
        self.assertEqual(txn.status(), 'posted')

        e1.amount = ZCurrency('GBP 30.00')

        # we've changed this behaviour ...
        #self.assertRaises(PostingError, txn.manage_editEntries, [e1])
        txn.manage_editEntries([e1])
        self.assertEqual(txn.status(), 'incomplete')

    def testEditEntriesHashes(self):
        ledger = self.portal.ledger.Ledger
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))

        txn.manage_post()

        txn.manage_editEntries([{'account': 'A000001', 'amount': ZCurrency('GBP 20.00')},
                                {'account': 'A000002', 'amount': -ZCurrency('GBP 20.00')}])

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 20.00'))
        self.assertEqual(txn.status(), 'posted')

    def testEffectiveSearch(self):
        ledger = self.portal.ledger.Ledger
        effective = DateTime('2012/01/01')

        self.loginAsPortalOwner()

        txn = self._mkTxn(effective, 'A000001', 'A000002',
                          ZCurrency('GBP 10.00'))

        self.assertEqual(ledger.transactionValues(effective=effective), [txn])
        self.assertEqual(ledger.transactionValues(
            effective=(effective - 1, effective + 1)), [txn])
        self.assertEqual(ledger.transactionValues(
            effective={'query': effective}), [txn])
        self.assertEqual(ledger.transactionValues(
            effective={'query': effective + 1, 'range': 'max'}), [txn])
        self.assertEqual(ledger.transactionValues(
            effective={'query': (effective - 1, effective + 1), 'range': 'max'}), [txn])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTransaction))
    return suite


if __name__ == '__main__':
    unittest.main()
