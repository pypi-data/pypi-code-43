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

from unittest import TestSuite, makeSuite
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase, MULTICURRENCY

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import floor_date
from Products.BastionLedger.BLGlobals import EPOCH

TEN = ZCurrency('GBP 10.00')
ZERO = ZCurrency('GBP 0.00')


class TestSubsidiaryTransaction(LedgerTestCase):
    """
    verify transaction workflow
    """

    def testStaticControlAccount(self):
        gl = self.portal.ledger.Ledger
        receivables = self.portal.ledger.Receivables
        control = receivables.controlAccount()

        self.assertEqual(receivables._control_accounts, ('A000005',))
        self.assertEqual(control, gl.A000005)
        self.assertEqual(control.openingDate(), EPOCH)
        self.assertEqual(control.openingBalance(), gl.zeroAmount())

        # the account isn't *special* - and needs/has this for normal posting
        # ...
        self.assertEqual(control.blLedger(), gl)
        self.assertEqual(control.ledgerId(), 'Ledger')

    def testStaticControlEntry(self):
        gl = self.portal.ledger.Ledger
        receivables = self.portal.ledger.Receivables
        control = receivables.controlEntry()

        self.assertEqual(control, gl.A000005._getOb('Receivables'))
        self.assertEqual(control.openingDate(), EPOCH)
        self.assertEqual(control.openingBalance(), gl.zeroAmount())
        self.assertEqual(control.blLedger(), receivables)
        self.assertEqual(control.ledgerId(), 'Receivables')

    def testEntry(self):
        ledger = self.portal.ledger.Receivables

        INDEX_COUNT = len(self.ledger.searchResults())

        ledger.manage_addProduct[
            'BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        dt = DateTime(self.ledger.timezone)

        self.assertEqual(len(self.ledger.searchResults()), INDEX_COUNT + 1)

        tid = ledger.manage_addProduct[
            'BastionLedger'].manage_addBLSubsidiaryTransaction(effective=dt)
        txn = ledger._getOb(tid)

        self.assertEqual(len(self.ledger.searchResults()), INDEX_COUNT + 2)

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', 'GBP 10.00')
        self.assertEqual(len(self.ledger.searchResults()), INDEX_COUNT + 3)
        self.assertEqual(txn.total(), ZCurrency('GBP10.00'))

        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(
            'A1000000', 'GBP -10.00')
        # self.assertEqual(len(self.ledger.searchResults()), INDEX_COUNT + 4) #
        # TODO
        self.assertEqual(txn.total(), 0)

        glent = txn.blEntry('A000001')
        subent = txn.blEntry('A1000000')

        self.assertEqual(glent.amount, TEN)
        self.assertEqual(glent.ledgerId(), 'Ledger')
        self.assertEqual(glent.accountId(), 'A000001')

        self.assertEqual(subent.amount, -TEN)
        self.assertEqual(subent.ledgerId(), 'Receivables')
        self.assertEqual(subent.accountId(), 'A1000000')

        self.assertEqual(txn.blEntry('A000001', 'Ledger').amount, TEN)
        self.assertEqual(txn.blEntry('A1000000', 'Receivables').amount, -TEN)


class TestMultiCurrencySubsidiaryTransaction(LedgerTestCase):

    def testMultiCurrencyEntry(self):
        ledger = self.portal.ledger.Receivables
        ledger.manage_addProduct[
            'BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')

        self.assertEqual(ledger.lastTransactionDate(), EPOCH)

        DT = DateTime(self.ledger.timezone)

        ctl_entry = ledger.controlEntry()
        ctl_acc = ledger._defaultControl()

        # simulate a charge
        txn = ledger.createTransaction(effective=DT)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', 'GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(
            'A1000000', 'AUD -25.00')

        self.assertEqual(txn.controlAccount(), ctl_acc)

        self.assertEqual(txn.status(), 'complete')
        self.assertEqual(ctl_entry.amount, ZERO)
        self.assertEqual(ctl_entry.balance(effective=DT), ZERO)
        self.assertEqual(ctl_acc.balance(effective=DT), ZERO)

        self.assertFalse(txn.isFX())

        txn.manage_post()

        # hmmm - this *should* be true ...
        self.assertTrue(txn.isFX())

        # verify _totalize internals ...
        entry = txn.blEntry('A1000000')
        self.assertEqual(entry.posted_amount, -TEN)
        self.assertEqual(entry.fx_rate, 0.4)

        self.assertEqual(ledger.lastTransactionDate(), floor_date(DT))

        self.assertEqual(ctl_entry.entryValues(), [entry])
        self.assertEqual(ctl_entry.transactionValues(), [txn])
        self.assertEqual(ctl_entry.lastTransactionDate(), floor_date(DT))
        self.assertEqual(ctl_entry.amount, -TEN)
        self.assertEqual(ctl_entry.balance(effective=DT), -TEN)
        self.assertEqual(ctl_entry.total(effective=DT), -TEN)
        self.assertEqual(ctl_entry.total(effective=(EPOCH, DT)), -TEN)

        self.assertEqual(ctl_acc._balance, ZERO)
        self.assertEqual(ctl_acc._balance_dt, EPOCH)  # floor_date(DT) ??
        self.assertEqual(ctl_acc._ctl_balances(DT), -TEN)
        self.assertEqual(ctl_acc.openingBalance(DT), ZERO)
        self.assertEqual(ctl_acc.lastTransactionDate(), floor_date(DT))
        # hmmm - while _balance_dt == EPOCH
        self.assertEqual(ctl_acc._totValidFor(DT), False)
        self.assertEqual(ctl_acc.totBalance(), -TEN)
        self.assertEqual(ctl_acc.balance(effective=DT), -TEN)

        self.assertEqual(ledger.A1000000.balance(effective=DT), -TEN)
        self.assertEqual(ledger.A1000000.balance(
            effective=DT, currency='AUD'), -ZCurrency('AUD 25.00'))

        # simulate a payment
        txn = ledger.createTransaction(effective=DT)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', '-GBP 9.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000042', '-GBP 1.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(
            'A1000000', 'AUD 25.00')

        txn.manage_post()

        entry = txn.blEntry('A1000000')
        self.assertEqual(entry.foreignAmount(), TEN)

        self.assertEqual(txn.debitTotal(), TEN)
        self.assertEqual(txn.creditTotal(), -TEN)

        self.assertEqual(ledger.A1000000.balance(effective=DT), ZERO)
        self.assertEqual(ledger.A1000000.balance(
            effective=DT, currency='AUD'), ZCurrency('AUD 0.00'))
        self.assertEqual(ctl_acc.balance(effective=DT), ZERO)

        # now mark to market at different fx rate ...
        txn.manage_bookFx([{'account': 'A1000000', 'fxrate': 0.5}])
        self.assertEqual(txn.status(), 'posted')

        # hmmm - this may not be correct ...
        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 12.50'))
        self.assertEqual(txn.creditTotal(), -TEN)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubsidiaryTransaction))
    if MULTICURRENCY:
        suite.addTest(makeSuite(TestMultiCurrencySubsidiaryTransaction))
    return suite
