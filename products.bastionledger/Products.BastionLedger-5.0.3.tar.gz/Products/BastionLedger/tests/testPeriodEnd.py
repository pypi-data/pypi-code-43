#
#    Copyright (C) 2008-2018  Corporation of Balclutha. All rights Reserved.
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
from Testing import ZopeTestCase  # this fixes up PYTHONPATH :)
from Products.BastionLedger.tests import LedgerTestCase

from Products.BastionLedger.Exceptions import InvalidPeriodError
from Products.BastionLedger.utils import ceiling_date, floor_date, add_seconds
from Products.BastionLedger.BLGlobals import EPOCH, EOP_TAGS

from Products.BastionLedger.interfaces.periodend import IPeriodEndInfo, IPeriodEndInfos

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency

P1_DT = DateTime('2007/06/30')  # .toZone('UTC')
P2_DT = DateTime('2008/06/30')  # .toZone('UTC')
P3_DT = DateTime('2009/06/30')  # .toZone('UTC')

ZERO = ZCurrency('GBP 0.00')
TEN = ZCurrency('GBP 10.00')
TWENTY = ZCurrency('GBP 20.00')
TWENTYTWO = ZCurrency('GBP 22.00')

TZ = 'GMT+10'


class TestPeriodEnd(LedgerTestCase.LedgerTestCase):

    def testCreated(self):
        self.assertTrue(self.controller_tool.periodend_tool)

    def testEOD(self):
        self.assertEqual(self.ledger.accrued_to, ceiling_date(self.now))
        self.assertEqual(self.ledger.requiresEOD(), False)
        self.assertEqual(self.ledger.requiresEOD(self.now + 2), True)
        self.assertEqual(self.ledger.requiresEOD(
            DateTime('1900/01/01')), False)

    def testStartDates(self):
        periods = self.ledger.periods

        self.assertEqual(P1_DT.timezone(), TZ)
        self.assertEqual(periods.nextPeriodStart(P1_DT), EPOCH)
        self.assertEqual(periods.nextPeriodEnd(P1_DT), ceiling_date(P1_DT))

        periods.addPeriodLedger(self.ledger.Ledger, EPOCH, P1_DT)

        self.assertEqual(periods.periodEnds(), [P1_DT])
        self.assertEqual(periods.nextPeriodStart(P1_DT), P1_DT + 1)
        self.assertEqual(periods.nextPeriodEnd(
            P1_DT), ceiling_date(P1_DT + 366))

    def testStartDatesForLedger(self):
        effective = DateTime('2009/01/01 UTC')
        periods = self.ledger.periods

        self.assertEqual(periods.lastClosingForLedger('Ledger'), EPOCH)
        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', effective), EPOCH)

        periods.addPeriodLedger(self.ledger.Ledger, EPOCH, effective)

        self.assertEqual(periods.lastClosingForLedger('Ledger'), effective)
        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', effective), effective)
        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', effective + 5), effective)

    def testTags(self):
        # assure underlying profit/loss etc methods work
        self.assertEqual(len(self.ledger.accountValues(
            type='Proprietorship', tags='loss_fwd')), 1)
        self.assertEqual(len(self.ledger.accountValues(
            type='Asset', tags='tax_defr')), 1)
        self.assertEqual(len(self.ledger.accountValues(
            type='Expense', tags='tax_exp')), 1)

    def testRunReRun(self):
        self.loginAsPortalOwner()

        now = DateTime(self.ledger.timezone) - 366
        yend = self.controller_tool.yearEnd(now)

        ledger = self.portal.ledger
        gl = ledger.Ledger
        a44 = gl.A000044

        txn = gl.createTransaction(
            title='Advertising Payment', effective=now - 1)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', '-GBP 10.00')
        txn.manage_addProduct[
            'BastionLedger'].manage_addBLEntry('A000044', TEN)
        txn.manage_post()

        self.assertEqual(a44.type, 'Expense')
        self.assertEqual(a44.balance(effective=now), TEN)

        pe_tool = self.controller_tool.periodend_tool

        self.assertEqual(ledger.periods.nextPeriodStart(now + 1), EPOCH)
        self.assertEqual(ledger.periods.nextPeriodEnd(now + 1), yend)

        # rolls to yend ...
        pe_tool.manage_periodEnd(ledger, now + 1)

        # hmmm - whats's in there ...
        #self.assertEqual(map(lambda x: str(x), ledger.transactionValues(tags=EOP_TAGS, case_sensitive=True)), [])
        self.assertEqual(len(ledger.transactionValues(
            tags=EOP_TAGS, case_sensitive=True)), 2)

        self.assertEqual(ledger.periods.periodsForLedger(
            'Ledger')[0].period_ended, yend)
        self.assertEqual(ledger.periods.lastClosingForLedger(
            'Ledger', now + 2), EPOCH)

        self.assertEqual(a44.openingBalance(effective=now + 2), ZERO)
        self.assertEqual(a44.balance(effective=now + 2), TEN)
        self.assertEqual(a44.openingDate(effective=now + 2), EPOCH)

        self.assertEqual(a44.openingBalance(effective=yend + 2), ZERO)
        self.assertEqual(a44.openingDate(
            effective=yend + 2), add_seconds(yend, 1))

        #self.assertEqual(a44.entryValues(effective=now+2), [])
        self.assertEqual(a44.total(effective=yend + 2), ZERO)
        self.assertEqual(a44.balance(effective=yend + 2), ZERO)

        # we're overwriting now ...
        #self.assertRaises(InvalidPeriodError, pe_tool.manage_periodEnd, ledger, now+1)

        pe_tool.manage_periodEnd(ledger, now + 1, force=True)

        self.assertEqual(len(ledger.transactionValues(
            tags=EOP_TAGS, case_sensitive=True)), 2)

        pe_tool.manage_reset(ledger)

        self.assertEqual(len(ledger.transactionValues(
            tags=EOP_TAGS, case_sensitive=True)), 0)
        self.assertEqual(len(ledger.transactionValues()), 1)

        # yeah ...
        #self.assertEqual(a44.entryValues(effective=now+2), [])
        self.assertEqual(a44._balance_dt, txn.effective_date)
        self.assertEqual(a44._balance, TEN)
        self.assertEqual(a44.balance(effective=yend + 2), TEN)

    def testLossClosingEntries(self):
        #
        # set up a GBP 10.00 expense txn and roll some year ends ...
        #
        self.loginAsPortalOwner()

        ledger = self.portal.ledger
        gl = ledger.Ledger

        txn = gl.createTransaction(
            title='Advertising Payment', effective=P1_DT - 20)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', '-GBP 10.00')
        txn.manage_addProduct[
            'BastionLedger'].manage_addBLEntry('A000044', TEN)
        txn.manage_post()

        self.assertEqual(gl.A000001.openingDate(effective=P1_DT - 20), EPOCH)
        self.assertEqual(gl.A000001.openingBalance(effective=P1_DT - 20), ZERO)

        self.assertEqual(gl.A000001.balance(effective=P1_DT), -TEN)
        self.assertEqual(gl.A000001.type, 'Asset')  # balance carries over
        self.assertEqual(gl.A000044.balance(effective=P1_DT), TEN)
        # need something to close out (insurance exp)
        self.assertEqual(gl.A000044.type, 'Expense')

        self.assertEqual(ledger.periods.lastClosingForLedger(
            'Ledger', P1_DT), EPOCH)

        self.assertEqual(ledger.grossProfit(P1_DT), -TEN)
        self.assertEqual(ledger.lossesAttributable(P1_DT), ZERO)
        self.assertEqual(ledger.corporationTax(P1_DT), ZERO)
        self.assertEqual(ledger.netProfit(P1_DT), -TEN)

        self.assertEqual(ledger.lossesAttributable(P1_DT, -TEN), ZERO)
        self.assertEqual(ledger.corporationTax(P1_DT, -TEN, ZERO), ZERO)
        self.assertEqual(ledger.netProfit(P1_DT, -TEN, ZERO, ZERO), -TEN)

        self.assertEqual(ledger.grossProfit((EPOCH, P1_DT)), -TEN)
        self.assertEqual(ledger.lossesAttributable((EPOCH, P1_DT)), ZERO)
        self.assertEqual(ledger.corporationTax((EPOCH, P1_DT)), ZERO)
        self.assertEqual(ledger.netProfit((EPOCH, P1_DT)), -TEN)

        #######################################################################
        #
        # RUN YEAR END 1
        #
        #######################################################################
        self.controller_tool.periodend_tool.manage_periodEnd(
            self.ledger, P1_DT, force=False)

        # DEBUG print "\n".join(map(lambda x: str(x), gl.transactionValues()))

        periods = ledger.periods
        pinfo1 = periods.objectValues()[0]
        pinfo1L = pinfo1.Ledger

        self.assertEqual(pinfo1.period_began, EPOCH)
        self.assertEqual(pinfo1.period_ended, ceiling_date(P1_DT))
        self.assertEqual(pinfo1.gross_profit, -TEN)
        self.assertEqual(pinfo1.net_profit, -TEN)
        self.assertEqual(pinfo1.company_tax, ZERO)
        self.assertEqual(pinfo1.companyTax(), ZERO)
        self.assertEqual(pinfo1.losses_forward, TEN)
        # self.assertEqual(pinfo1.lossesForward(), TEN) hmmm - ZERO

        self.assertEqual(pinfo1L.numberTransactions(), 2)  # closing + tax loss
        # self.assertEqual(pinfo1L.numberAccounts(), 55) # hmmm 'created' ndx
        # borked ...

        self.assertEqual(pinfo1L.balance('A000001'), -TEN)
        self.assertEqual(pinfo1L.balance('A000044'), ZERO)  # it's closed out
        self.assertEqual(pinfo1L.reportedBalance('A000044'), TEN)

        # this is transactions on account, *excluding* any period-end ...
        self.assertEqual(pinfo1L.A000044.total(), TEN)

        # TODO self.assertRaises(InvalidPeriodError, periods.periodForLedger,
        # 'Ledger', P1_DT - 367)
        self.assertEqual(periods.periodForLedger('Ledger', P1_DT - 30), None)
        self.assertEqual(periods.periodForLedger(
            'Ledger', P1_DT - 20), None)  # official period_began!
        self.assertEqual(periods.periodForLedger('Ledger', P1_DT - 19.5), None)
        self.assertEqual(periods.periodForLedger('Ledger', P1_DT), pinfo1L)
        self.assertEqual(periods.periodForLedger('Ledger', P1_DT + 1), pinfo1L)
        # TODO self.assertRaises(InvalidPeriodError, periods.periodForLedger,
        # 'Ledger', P1_DT - 10)

        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', P1_DT - 1), EPOCH)
        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', P1_DT), ceiling_date(P1_DT))
        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', P1_DT + 1), ceiling_date(P1_DT))

        self.assertEqual(periods.balanceForAccount(
            P1_DT + 1, 'Ledger', 'A000001'), -TEN)
        self.assertEqual(periods.balanceForAccount(
            P1_DT, 'Ledger', 'A000001'), -TEN)
        self.assertEqual(periods.balanceForAccount(
            P1_DT - 1, 'Ledger', 'A000001'), None)  # prev period
        self.assertEqual(periods.balanceForAccount(
            P1_DT + 1, 'Ledger', 'A000044'), ZERO)
        self.assertEqual(periods.balanceForAccount(
            P1_DT, 'Ledger', 'A000044'), ZERO)
        self.assertEqual(periods.balanceForAccount(
            P1_DT - 1, 'Ledger', 'A000044'), None)
        self.assertEqual(periods.balanceForAccount(
            P1_DT - 10, 'Ledger', 'A000044'), None)

        # checked newly cached amounts still compute correct balances for A, L,
        # P's ...
        asset = gl.A000001
        # opening bal is always ZERO (but theres a txn summation from dt - 10)
        self.assertEqual(asset.openingDate(effective=P1_DT - 1), EPOCH)
        self.assertEqual(asset.openingDate(effective=P1_DT - 10), EPOCH)
        self.assertEqual(asset.openingDate(effective=P1_DT - 22), EPOCH)
        self.assertEqual(asset.openingDate(effective=P1_DT + 1), P1_DT + 1)
        self.assertEqual(asset.openingDate(effective=P1_DT), P1_DT + 1)

        self.assertEqual(asset.openingBalance(effective=P1_DT + 1), -TEN)
        self.assertEqual(asset.openingBalance(effective=P1_DT), -TEN)
        self.assertEqual(asset.openingBalance(effective=P1_DT - 1), ZERO)
        self.assertEqual(asset.openingBalance(effective=P1_DT - 22), ZERO)

        self.assertEqual(asset.total(effective=(P1_DT - 10, P1_DT)), ZERO)
        self.assertEqual(asset.total(effective=(P1_DT - 30, P1_DT)), -TEN)
        self.assertEqual(asset.total(effective=(P1_DT - 1, P1_DT)), ZERO)

        self.assertEqual(asset.balance(effective=P1_DT + 1), -TEN)
        self.assertEqual(asset.balance(effective=P1_DT), -TEN)
        self.assertEqual(asset.balance(effective=P1_DT - 1), -TEN)
        self.assertEqual(asset.balance(effective=P1_DT - 10), -TEN)
        self.assertEqual(asset.balance(effective=P1_DT - 30), ZERO)

        loss = gl._getOb(self.LOSSFWD_ID)
        lossL = pinfo1L._getOb(self.LOSSFWD_ID)
        self.assertEqual(loss.type, 'Proprietorship')
        self.assertTrue(loss.hasTag('loss_fwd'))
        self.assertEqual(loss.openingDate(), P1_DT + 1)
        self.assertEqual(loss.lastTransactionDate(), P1_DT + 1)
        self.assertEqual(loss.openingBalance(P1_DT + 1), ZERO)  # TEN ??
        self.assertEqual(lossL.balance, ZERO)  # ??
        self.assertEqual(lossL.reporting_balance, ZERO)  # ??
        self.assertEqual(loss._balance, TEN)
        self.assertEqual(loss._balance_dt, P1_DT + 1)
        self.assertEqual(loss.balance(effective=P1_DT - 1), ZERO)
        self.assertEqual(loss.balance(effective=P1_DT), TEN)
        self.assertEqual(loss.balance(effective=P1_DT + 1), TEN)

        retained = gl._getOb(self.RETAINED_ID)
        self.assertTrue(retained.hasTag('retained_earnings'))
        self.assertEqual(retained.balance(effective=P1_DT), ZERO)
        self.assertEqual(retained.balance(effective=P1_DT + 1), ZERO)

        profit = gl._getOb(self.PROFIT_ID)
        profitL = pinfo1L._getOb(self.PROFIT_ID)
        self.assertTrue(profit.hasTag('profit_loss'))
        self.assertEqual(profit.openingDate(), P1_DT + 1)
        self.assertEqual(profit.lastTransactionDate(), P1_DT + 1)
        self.assertEqual(profit.openingBalance(P1_DT + 1), TEN)  # ?? ZERO
        self.assertEqual(profitL.balance, TEN)  # ??
        self.assertEqual(profitL.reporting_balance, TEN)  # ??
        self.assertEqual(profit._balance, -TEN)  # ??
        self.assertEqual(profit._balance_dt, P1_DT + 1)
        self.assertEqual(profit.balance(effective=P1_DT - 1), ZERO)
        self.assertEqual(profit.balance(effective=P1_DT), TEN)
        # wtf?? - ZERO ????
        self.assertEqual(profit.balance(effective=P1_DT + 1), -TEN)

        tax_defr = gl._getOb(self.DEFERRED_ID)
        self.assertTrue(tax_defr.hasTag('tax_defr'))
        self.assertEqual(tax_defr.balance(effective=P1_DT - 1), ZERO)
        self.assertEqual(tax_defr.periods.periodForLedger(
            'Ledger', P1_DT), pinfo1L)

        # tax loss is rolled forward into *next* period
        self.assertEqual(pinfo1L.balance(self.LOSSFWD_ID), ZERO)  # ???
        self.assertEqual(pinfo1L.balance(self.DEFERRED_ID), ZERO)
        self.assertEqual(pinfo1L.reportedBalance(self.PROFIT_ID), TEN)  # ???
        self.assertEqual(pinfo1L.reportedBalance(self.RETAINED_ID), ZERO)

        self.assertEqual(tax_defr.periods.balanceForAccount(
            P1_DT, 'Ledger', self.DEFERRED_ID), ZERO)
        self.assertEqual(tax_defr.openingDate(effective=P1_DT), P1_DT + 1)
        self.assertEqual(tax_defr.openingBalance(effective=P1_DT), ZERO)
        self.assertEqual(tax_defr.balance(effective=P1_DT), ZERO)
        self.assertEqual(tax_defr.balance(effective=P1_DT + 1), ZERO)

        # TODO self.assertEqual(Ledger.sum(tags='retained_earnings',
        # effective=P1_DT+1), TEN)

        self.assertEqual(len(pinfo1L.blTransactions()),
                         2)  # closing + deferred

        # blTransactions is sorted by date (and the deferred is forward-dated)
        closing = pinfo1L.blTransactions()[0]

        self.assertEqual(closing.effective(), floor_date(P1_DT))
        self.assertEqual(closing.debitTotal(), TEN)

        self.assertEqual(ledger.lossesAttributable(
            P1_DT + 1, ZCurrency('GBP 50.00')), TEN)
        self.assertEqual(ledger.lossesAttributable(
            P1_DT + 1, ZCurrency('GBP 5.00')), ZCurrency('GBP 5.00'))

    def testProfitClosingEntries(self):
        # tests profit + subsidiary ledger balances which have proved
        # problematic
        self.loginAsPortalOwner()

        order_dt = P1_DT - 20
        ledger = self.ledger

        ledger.Inventory.manage_addProduct['BastionLedger'].manage_addBLPart(
            'widget', taxcodes=('sales_tax/A',))
        self.widget = ledger.Inventory.widget

        gl = ledger.Ledger
        periodend_tool = self.controller_tool.periodend_tool

        income = gl.accountValues(tags='part_inc')[0]
        self.widget.edit_prices('kilo', 1.5, 5,
                                TWENTY,
                                TEN,
                                TEN,
                                ZERO,
                                gl.accountValues(tags='part_inv')[0].getId(),
                                income.getId(),
                                gl.accountValues(tags='part_cogs')[0].getId())

        receivables = ledger.Receivables
        control_account = receivables.controlAccounts()[0]
        control_entry = receivables.controlEntries()[0]

        # need to make sure it's opened in this period ....
        id = receivables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading',
                                                                                     opened=P1_DT - 30)
        account = receivables._getOb(id)

        # assets carry over period-end balances
        self.assertEqual(control_account.type, 'Asset')
        self.assertEqual(control_account.getId(), 'A000005')
        self.assertEqual(account.type, 'Asset')
        self.assertEqual(account.opened, P1_DT - 30)
        self.assertEqual(account.created(), P1_DT - 30)

        account.manage_addOrder(orderdate=order_dt)
        order = account.objectValues('BLOrder')[0]
        order.manage_addProduct[
            'BastionLedger'].manage_addBLOrderItem('widget')
        order.manage_invoice()

        # wtf is the txn??
        self.assertEqual(order.status(), 'invoiced')
        otxn = order.blTransaction()
        self.assertEqual(otxn.status(), 'posted')
        self.assertEqual(otxn.effective(), order_dt)

        self.assertEqual(account.balance(effective=order_dt + 1), TWENTYTWO)
        self.assertEqual(account.balance(effective=order_dt), TWENTYTWO)
        self.assertEqual(account.balance(effective=P1_DT), TWENTYTWO)
        self.assertEqual(control_account.balance(
            effective=order_dt + 1), TWENTYTWO)
        self.assertEqual(control_account.balance(
            effective=order_dt), TWENTYTWO)

        # this *is* crucially important - and *must* carry into period
        # info/opening balance!!!
        self.assertEqual(control_entry.total(
            effective=(EPOCH, P1_DT)), TWENTYTWO)  # ??
        self.assertEqual(control_account.lastTransactionDate(), order_dt)
        self.assertEqual(control_account.balance(effective=P1_DT), TWENTYTWO)
        self.assertEqual(control_account.totBalance(), TWENTYTWO)
        self.assertEqual(control_account.totDate(), EPOCH)
        self.assertEqual(control_account._totValidFor(P1_DT), False)
        self.assertEqual(control_account._ctl_balances(P1_DT), TWENTYTWO)
        self.assertEqual(control_account.total(
            effective=(EPOCH, P1_DT)), TWENTYTWO)  # ??

        self.assertEqual(income.balance(effective=order_dt), -TWENTY)
        self.assertEqual(income.balance(effective=P1_DT), -TWENTY)

        self.assertEqual(ledger.grossProfit(effective=P1_DT), TEN)
        self.assertEqual(ledger.grossProfit(
            effective=(P1_DT - 30, P1_DT)), TEN)
        self.assertEqual(ledger.grossProfit(effective=(P1_DT, P2_DT)), ZERO)

        self.assertEqual(ledger.lossesAttributable((EPOCH, P1_DT)), ZERO)
        self.assertEqual(ledger.corporationTax(
            (EPOCH, P1_DT)), ZCurrency('GBP 3.00'))
        self.assertEqual(ledger.netProfit(
            (EPOCH, P1_DT)), ZCurrency('GBP 7.00'))

        self.assertEqual(periodend_tool.reportingInfos(ledger, P1_DT), [])

        self.assertEqual(control_entry.balance(effective=P1_DT), TWENTYTWO)
        self.assertEqual(control_entry.total(
            effective=(EPOCH, P1_DT)), TWENTYTWO)

        periods = ledger.periods
        self.assertEqual(list(periods.objectValues()), [])

        #######################################################################
        #
        # RUN YEAR END 1
        #
        #######################################################################
        periodend_tool.manage_periodEnd(ledger, P1_DT, force=True)

        # DEBUG print "\n".join(map(lambda x: str(x), gl.transactionValues()))

        pinfo1 = periods.objectValues()[0]
        pinfo1R = pinfo1.Receivables
        pinfo1L = pinfo1.Ledger

        self.assertEqual(pinfo1.effective(), P1_DT)
        self.assertEqual(pinfo1.period_began, EPOCH)
        self.assertEqual(pinfo1.period_ended, ceiling_date(P1_DT))
        self.assertEqual(ceiling_date(P1_DT), DateTime(
            '2007-06-30 23:59:59 %s' % TZ))
        self.assertEqual(ceiling_date(
            P1_DT).strftime('%Y-%m-%d'), '2007-06-30')
        self.assertEqual(floor_date(ceiling_date(
            P1_DT)).strftime('%Y-%m-%d'), '2007-06-30')

        self.assertEqual(pinfo1.getId(), '2007-06-30')
        self.assertEqual(periodend_tool.reportingInfos(
            ledger, P1_DT), ['2007-06-30'])

        self.assertEqual(periods.periodForLedger(
            'Receivables', P1_DT + 2), pinfo1R)
        # TODO self.assertRaises(InvalidPeriodError, periods.periodForLedger,
        # 'Ledger', P1_DT - 2)

        self.assertEqual(len(pinfo1R.objectIds()), 1)

        recR = pinfo1R.objectValues()[0]
        self.assertEqual(recR.blAccount(), account)
        self.assertEqual(recR.blLedger(), receivables)

        # this is from manage_updateChart: opening_bal + total(dtrange)
        self.assertEqual(recR.balance, TWENTYTWO)

        recL = pinfo1L._getOb(control_account.getId())
        self.assertEqual(recL.blAccount(), control_account)
        self.assertEqual(recL.balance, TWENTYTWO)  # TWENTYTWO??

        self.assertEqual(pinfo1R.numberAccounts(), 1)

        self.assertEqual(pinfo1R.numberTransactions(), 1)
        self.assertEqual(pinfo1R.period_began, EPOCH)
        self.assertEqual(pinfo1R.period_ended, ceiling_date(P1_DT))

        self.assertEqual(list(pinfo1R.objectIds()), [account.getId()])

        self.assertEqual(pinfo1.gross_profit, TEN)
        self.assertEqual(pinfo1.net_profit, ZCurrency('GBP 7.00'))
        self.assertEqual(pinfo1.company_tax, ZCurrency('GBP 3.00'))
        self.assertEqual(pinfo1.losses_forward, ZERO)
        self.assertEqual(pinfo1.losses_recognised, ZERO)

        self.assertEqual(pinfo1.netProfit(), -ZCurrency('GBP 7.00'))
        self.assertEqual(pinfo1.companyTax(), ZCurrency('GBP 3.00'))
        self.assertEqual(pinfo1.lossesForward(), ZERO)
        self.assertEqual(pinfo1.lossesRecognised(), ZERO)

        self.assertEqual(pinfo1L.balance(income.getId()),
                         ZERO)  # it's had closing applied
        self.assertEqual(pinfo1R.balance(account.getId()), TWENTYTWO)
        self.assertEqual(pinfo1L.balance(control_account.getId()), TWENTYTWO)
        self.assertEqual(periods.balanceForAccount(
            P2_DT, 'Ledger', income.getId()), ZERO)
        self.assertEqual(periods.balanceForAccount(
            P2_DT, 'Ledger', control_account.getId()), TWENTYTWO)
        self.assertEqual(periods.balanceForAccount(
            P2_DT, 'Receivables', account.getId()), TWENTYTWO)

        # closing + tax + p&l forward
        self.assertEqual(len(pinfo1L.blTransactions()), 3)
        self.assertEqual(len(pinfo1R.blTransactions()), 0)  # no I or E a/c's

        self.assertEqual(pinfo1L.balance(self.LOSSFWD_ID), ZERO)
        self.assertEqual(pinfo1L.balance(self.DEFERRED_ID), ZERO)
        self.assertEqual(pinfo1L.reportedBalance(
            self.PROFIT_ID), -ZCurrency('GBP 7.00'))
        self.assertEqual(pinfo1L.reportedBalance(self.RETAINED_ID), ZERO)

        closing = pinfo1L.closingTransaction()

        self.assertEqual(closing.effective(), P1_DT)

        self.assertEqual(ledger.lossesAttributable(
            P2_DT, ZCurrency('GBP 50.00')), ZERO)
        self.assertEqual(ledger.lossesAttributable(
            P2_DT, ZCurrency('GBP 5.00')), ZERO)

        # TODO - this needs fleshing out ...
        tax = pinfo1L.taxTransaction()
        self.assertEqual(tax.effective(), P1_DT)

        self.assertEqual(control_entry.balance(effective=P1_DT + 1), TWENTYTWO)
        self.assertEqual(control_entry.total(
            effective=(P1_DT - 1, P1_DT + 1)), ZERO)
        self.assertEqual(control_account.openingBalance(
            effective=P1_DT + 1), TWENTYTWO)
        self.assertEqual(control_account.total(
            effective=(P1_DT - 1, P1_DT + 1)), ZERO)

        #######################################################################
        #
        # RUN YEAR END 2
        #
        #######################################################################
        periodend_tool.manage_periodEnd(ledger, P2_DT)

        pinfo2 = periods.objectValues()[1]
        pinfo2R = pinfo2.Receivables
        pinfo2L = pinfo2.Ledger

        self.assertTrue(pinfo2.period_began > pinfo1.period_ended)
        self.assertTrue(pinfo2.period_began - pinfo1.period_ended < 0.00005)

        self.assertEqual(periodend_tool.reportingInfos(
            ledger, P2_DT), ['2007-06-30', '2008-06-30'])

        self.assertEqual(pinfo2R.numberTransactions(),
                         0)  # no txns this period

        self.assertEqual(pinfo2.gross_profit, ZERO)
        self.assertEqual(pinfo2.net_profit, ZERO)
        self.assertEqual(pinfo2.company_tax, ZERO)

        # this is supposed summation of tax_exp accounts - seems maybe a balance is getting carried across...
        # self.assertEqual(pinfo2.companyTax(), ZERO) # -THREE wtf ??
        self.assertEqual(pinfo2.losses_forward, ZERO)
        self.assertEqual(pinfo2.lossesForward(), ZERO)

        self.assertEqual(pinfo2R.balance(account.getId()), TWENTYTWO)
        self.assertEqual(pinfo2L.balance(income.getId()), ZERO)
        self.assertEqual(pinfo2L.balance(control_account.getId()), TWENTYTWO)
        self.assertEqual(periods.balanceForAccount(
            P2_DT, 'Ledger', control_account.getId()), TWENTYTWO)
        self.assertEqual(periods.balanceForAccount(
            P2_DT, 'Receivables', account.getId()), TWENTYTWO)
        self.assertEqual(periods.balanceForAccount(
            P2_DT, 'Ledger', income.getId()), ZERO)

        # now pay the bill ...
        pmt = ledger.Receivables.createTransaction(effective=P3_DT - 10)
        pmt.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', TWENTYTWO)
        pmt.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(
            account.getId(), -TWENTYTWO)
        pmt.manage_post()

        self.assertEqual(income.balance(effective=P3_DT), ZERO)
        self.assertEqual(account.balance(effective=P3_DT), ZERO)

        # first check that *any* delegation actually works ...
        self.assertEqual(ledger.Receivables.total(
            effective=(P2_DT, P3_DT)), -TWENTYTWO)

        # self.assertEqual(control_entry.balance(effective=P3_DT), -TWENTYTWO)
        # # hmmm ZERO ...
        self.assertEqual(control_entry.total(
            effective=(P2_DT, P3_DT)), -TWENTYTWO)
        self.assertEqual(control_entry.lastTransactionDate(), P3_DT - 10)

        # then verify the call itself ...
        self.assertEqual(control_account.openingDate(
            P3_DT), floor_date(P2_DT + 1))
        self.assertEqual(control_account.openingBalance(P3_DT), TWENTYTWO)
        self.assertEqual(control_account.balance(effective=P3_DT), ZERO)

        #######################################################################
        #
        # RUN YEAR END 3
        #
        #######################################################################
        periodend_tool.manage_periodEnd(ledger, P3_DT)

        pinfo3 = periods.objectValues()[2]
        pinfo3R = pinfo3.Receivables
        pinfo3L = pinfo3.Ledger

        self.assertTrue(pinfo3L.period_began > pinfo2L.period_ended)
        self.assertTrue(pinfo3L.period_began - pinfo2L.period_ended < 0.00005)

        self.assertEqual(periodend_tool.reportingInfos(ledger, P3_DT),
                         ['2007-06-30', '2008-06-30', '2009-06-30'])

        self.assertEqual(pinfo3R.numberTransactions(), 1)  # pmt

        self.assertEqual(pinfo3.gross_profit, ZERO)
        self.assertEqual(pinfo3.net_profit, ZERO)
        self.assertEqual(pinfo3.company_tax, ZERO)
        # TODO self.assertEqual(pinfo3.companyTax(), ZERO) # (GPB 3.00) wtf -
        # negative!!
        self.assertEqual(pinfo3.losses_forward, ZERO)
        self.assertEqual(pinfo3.lossesForward(), ZERO)

        self.assertEqual(pinfo3R.balance(account.getId()), ZERO)
        self.assertEqual(pinfo3L.balance(control_account.getId()), ZERO)
        self.assertEqual(periods.balanceForAccount(
            P3_DT, 'Receivables', account.getId()), ZERO)

        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', P1_DT - 1), EPOCH)
        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', P2_DT - 1), ceiling_date(P1_DT))
        self.assertEqual(periods.lastClosingForLedger(
            'Ledger', P3_DT - 1), ceiling_date(P2_DT))

        # ensure delete removes txns
        tids = map(lambda x: x.getId(), pinfo1.blTransactions())
        self.assertEqual(len(tids), 3)

        self.controller_tool.periodend_tool.manage_reset(ledger)
        self.assertEqual(ledger.transactionValues(id=tids), [
                         otxn, pmt])  # just the original order

    def testClosingTxnOnEOP(self):
        self.loginAsPortalOwner()

        txn = self.ledger.Ledger.createTransaction(
            title='My Txn', effective=P1_DT + 1)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry(
            'A000001', '-GBP 10.00')
        txn.manage_addProduct[
            'BastionLedger'].manage_addBLEntry('A000044', TEN)
        txn.manage_post()

        #######################################################################
        #
        # RUN YEAR END 1
        #
        #######################################################################
        self.controller_tool.periodend_tool.manage_periodEnd(
            self.ledger, P1_DT, force=False)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestPeriodEnd))
    return suite
