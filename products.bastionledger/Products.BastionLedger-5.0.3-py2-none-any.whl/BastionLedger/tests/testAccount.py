#
#    Copyright (C) 2006-2018  Corporation of Balclutha. All rights Reserved.
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
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionLedger.BLGlobals import EPOCH, MAXDT
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import floor_date, lastXDays
from Products.BastionLedger.Exceptions import TaxCodeError

from Products.AdvancedQuery import In

from zope import component
from Products.BastionLedger.interfaces.transaction import IEntry

ZERO = ZCurrency('GBP 0.00')
TEN = ZCurrency('GBP 10.00')
TWENTYFIVE = ZCurrency('GBP 25.00')
THIRTYFIVE = ZCurrency('GBP 35.00')


class TestAccount(LedgerTestCase):
    """
    verify account processing
    """

    def testUUID(self):
        self.assertTrue(
            self.ledger.Ledger.A000001.unrestrictedTraverse('@@uuid'))

    def testCatalogSetup(self):
        self.assertEqual(
            self.ledger.Ledger.A000001._getCatalogTool(), self.portal.portal_catalog)

    def testEmptyStuff(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        ZERO = ledger.zeroAmount()
        self.assertEqual(account.blLedger(), ledger)
        self.assertEqual(account._balance, ZERO)
        self.assertEqual(account._ctl_balances(), ZERO)
        self.assertEqual(account.openingBalance(), ZERO)
        self.assertEqual(account.balance(), ZERO)
        self.assertEqual(account.totDate(), EPOCH)
        self.assertEqual(account.totBalance(), ZERO)
        self.assertEqual(account.openingDate(), EPOCH)

        self.assertEqual(account.base_currency, 'GBP')
        self.assertEqual(account.isFCA(), False)
        self.assertEqual(account.created(), account.opened)
        self.assertEqual(account.CreationDate()[
                         :10], self.now.strftime('%Y-%m-%d'))

        self.assertEqual(account.lastTransactionDate(), EPOCH)

    def testGlobalTagStuff(self):
        tax_exp = self.ledger.Ledger.accountValues(tags='tax_exp')[0]
        self.assertEqual(tax_exp.hasTag('tax_exp'), True)
        self.assertEqual(tax_exp.hasTag('tax_accr'), False)

    def testLocalTags(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.assertEqual(account.tags, ())
        self.assertFalse(account.hasTag('Whippee'))
        self.assertEqual(self.ledger.uniqueValuesFor('tags'), ())

        ledger.manage_addTag('Whippee', [account.accno])

        self.assertEqual(account.tags, ('Whippee',))
        self.assertEqual(self.ledger.uniqueValuesFor('tags'), (u'Whippee',))
        self.assertTrue(account.hasTag('Whippee'))

    def testAddTag(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        # uniqueValuesFor() implementation ...
        self.assertEqual(self.ledger._catalog.indexes[
                         'tags'].uniqueValues(), ())

        self.assertFalse('tag1' in self.ledger.uniqueValuesFor('tags'))
        account.updateTags('tag1')

        self.assertTrue('tag1' in self.ledger.uniqueValuesFor('tags'))
        self.assertEqual(account.hasTag('tag1'), True)

    def testGlobalTagStuff(self):
        # we silently ignore tags defined at global (portal_bastionledger)
        # level
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.assertEqual(account.tags, ())

        ledger.manage_addTag('bank_account', [account.accno])

        self.assertEqual(account.tags, ())
        self.assertFalse('bank_account' in self.ledger.uniqueValuesFor('tags'))

    def testBalanceFunctions(self):

        now = self.now
        later = now + 5

        ledger = self.ledger.Ledger
        account = ledger.A000001

        ledger.manage_addTag('Whippee', [account.accno])

        txn_now = ledger.createTransaction(effective=now)
        entryid = txn_now.createEntry('A000001', 'GBP 10.00')
        txn_now.createEntry('A000002', '-GBP 10.00')

        #self.assertEqual(component.subscribers(txn_now.entryValues(), IEntry), None)

        txn_now.manage_post()

        txn_now.editProperties('woot', 'woot tag', tags=['woot', ])

        # verify internal counters ...
        self.assertEqual(account._balance, TEN)
        self.assertEqual(account._balance_dt, floor_date(now))

        txn_later = ledger.createTransaction(effective=later)
        txn_later.createEntry('A000001', 'GBP 25.00')
        txn_later.createEntry('A000002', '-GBP 25.00')

        txn_later.manage_post()

        self.assertEqual(account.lastTransactionDate(), txn_now.effective_date)
        self.assertEqual(account.lastTransactionDate(now),
                         txn_now.effective_date)
        self.assertEqual(account.lastTransactionDate(
            later), txn_later.effective_date)
        self.assertEqual(account.lastTransactionDate(
            MAXDT), txn_later.effective_date)

        # verify internal counters (don't aggregate forwards...)
        self.assertEqual(account._balance, TEN)
        self.assertEqual(account._balance_dt, floor_date(now))
        self.assertEqual(account._totValidFor(now), True)
        self.assertEqual(account._totValidFor(later), False)
        self.assertEqual(account._totValidFor(later, now=now), False)
        self.assertEqual(account._totValidFor(later, now=later), False)
        self.assertEqual(account._total(effective=(EPOCH, now)), TEN)
        self.assertEqual(account._ctl_totals(effective=(EPOCH, now)), ZERO)

        # now go hammer balance stuff ...
        self.assertEqual(account.openingDate(), EPOCH)
        self.assertEqual(account.openingDate(now), EPOCH)
        self.assertEqual(account.openingDate(None), EPOCH)
        self.assertEqual(self.ledger.periods.balanceForAccount(
            now, 'Ledger', account.getId()), None)
        self.assertEqual(account.openingBalance(EPOCH), ZERO)
        self.assertEqual(account.openingBalance(now), ZERO)
        self.assertEqual(account.openingBalance(), ZERO)
        self.assertEqual(len(account.entryValues(effective=(EPOCH, now))), 1)
        self.assertEqual(len(account.entryValues(effective=now)), 1)
        self.assertEqual(len(account.entryValues(effective=(EPOCH, later))), 2)
        self.assertEqual(len(account.entryValues(effective=later)), 2)
        self.assertEqual(len(account.entryValues()), 2)
        self.assertEqual(account.total(effective=(EPOCH, now)), TEN)
        self.assertEqual(account.total(effective=now), TEN)
        self.assertEqual(account.balance(effective=now), TEN)
        self.assertEqual(account.balance(), TEN)
        self.assertEqual(account.balance(effective=later), THIRTYFIVE)

        self.assertEqual(account.debitTotal(effective=now), TEN)
        self.assertEqual(account.debitTotal(
            effective=[now + 2, later]), TWENTYFIVE)
        self.assertEqual(account.creditTotal(effective=now), ZERO)
        self.assertEqual(account.creditTotal(effective=now + 2), ZERO)

        self.assertEqual(ledger.sum(tags='Whippee', effective=now), TEN)

        self.assertEqual(len(account.entryValues((EPOCH, later))), 2)
        self.assertEqual(ledger.sum(
            tags='Whippee', effective=later), THIRTYFIVE)

        self.assertEqual(len(account.entryValues((now + 2, later))), 1)
        self.assertEqual(ledger.sum(tags='Whippee', effective=[
                         now + 2, later]), TWENTYFIVE)

        # more sophisticated queries ...
        self.assertEqual(len(account.entryValues(query=In('tags', 'woot'))), 1)
        self.assertEqual(
            len(account.entryValues(query=~In('tags', 'woot'))), 1)

        ledger.manage_delObjects([txn_later.getId()])

        # verify txn manage_unpost has removed entry
        self.assertEqual(len(account.entryValues()), 1)
        entry = account.entryValues()[0]
        self.assertEqual(entry.effective(), floor_date(now))
        self.assertEqual(entry.transactionId(), 'T000000000001')
        self.assertEqual(account.lastTransactionDate(), floor_date(now))

        # verify internal counters ...
        self.assertEqual(account._balance_dt, floor_date(now))
        self.assertEqual(account._balance, TEN)

        self.assertEqual(account.balance(), TEN)

        self.assertEqual(account.transactionValues(), [entry.blTransaction()])

    def testGraphingFunctions(self):
        now = floor_date(DateTime('2016/04/15') - 20)
        days = lastXDays(now, 7)
        ledger = self.ledger.Ledger
        account = ledger.A000001
        self.assertEqual(days, [now - 6, now - 5, now -
                                4, now - 3, now - 2, now - 1, now])
        self.assertEqual(account.balances(days, account.entryValues((now - 7, now))),
                         ['0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00'])

        txn = ledger.createTransaction(effective=now - 4)
        entryid = txn.createEntry('A000001', 'GBP 10.00')
        txn.createEntry('A000002', '-GBP 10.00')
        txn.manage_post()

        self.assertEqual(account.balances(days, account.entryValues((now - 7, now))),
                         ['0.00', '0.00', '10.00', '10.00', '10.00', '10.00', '10.00'])

        self.assertEqual(account.jsonBalances(min(days), max(days)),
                         '[{"amount": 0.0, "effective": "2016/03/21"}, {"amount": 0.0, "effective": "2016/03/22"}, {"amount": 10.0, "effective": "2016/03/23"}, {"amount": 10.0, "effective": "2016/03/24"}, {"amount": 10.0, "effective": "2016/03/25"}, {"amount": 10.0, "effective": "2016/03/26"}]')

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Ledger
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse(
            'portal_factory/BLAccount/A222222')
        self.assertTrue('A222222' in ledger.restrictedTraverse(
            'portal_factory/BLAccount').objectIds())
        A222222 = temp_object.portal_factory.doCreate(temp_object, 'A222222')
        self.assertTrue('A222222' in ledger.objectIds())

        # document_edit should create the real object
        self.assertEqual(len(self.ledger.searchResults(
            meta_type='BLAccount', id='A222223')), 0)
        temp_object = ledger.restrictedTraverse(
            'portal_factory/BLAccount/A222223')
        self.assertTrue('A222223' in ledger.restrictedTraverse(
            'portal_factory/BLAccount').objectIds())
        # assure portal_factory doesn't get catalog'd ....
        self.assertEqual(len(self.ledger.searchResults(
            meta_type='BLAccount', id='A222223')), 0)
        temp_object.blaccount_edit(title='Foo',
                                   description='',
                                   type='Asset',
                                   subtype='Current Asset',
                                   currency='GBP',
                                   accno='2222')

        # assure portal_factory doesn't get catalog'd ....
        self.assertEqual(len(self.ledger.searchResults(
            meta_type='BLAccount', id='A222223')), 1)

        self.assertTrue('2222' in self.ledger.uniqueValuesFor('accno'))
        self.assertEqual(ledger.accountValues(accno='2222')[0].title, 'Foo')
        self.assertTrue('A222223' in ledger.objectIds())

    def testTaxGroups(self):
        # checking persistence/non-taint of tax_codes dictionary
        self.loginAsPortalOwner()
        ledger = self.ledger.Ledger

        # our placebo
        self.assertEqual(ledger.A000001.tax_codes, ())

        acc = ledger.manage_addProduct['BastionLedger'].manage_addBLAccount(
            'crap', 'AUD', type='Revenue', accno='1234',)

        self.assertEqual(acc.taxGroupsCodes(), ())

        self.assertRaises(TaxCodeError, acc.manage_addTaxGroup, 'blabla_tax')

    def testEmailStatementRenders(self):

        self.loginAsPortalOwner()
        account = self.ledger.Ledger.A000001

        # self.assertEqual(account.blaccount_template(account,
        #                                            email='me@crap.com',
        #                                            effective=self.now), '')

        # size fluctuates quite a bit ...
        self.assertTrue(len(account.blaccount_template(account,
                                                       email='me@crap.com',
                                                       effective=self.now)) > 6100)

    def testPDF(self):
        self.loginAsPortalOwner()
        account = self.ledger.Ledger.A000001
        self.assertTrue(len(account.asPDF()) > 4700)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAccount))
    return suite

if __name__ == '__main__':
    unittest.main()
