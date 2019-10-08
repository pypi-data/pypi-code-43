from .IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.model.BankStatement import BankStatement
from ofx2xlsmbr.model.Origin import Origin

from decimal import Decimal

import logging

logger = logging.getLogger(__name__)


class OFXReaderBankStatement(IReaderBankStatement):
    def read(self, factory, ofx, options=None):
        signalMultiplier = 1
        if (options):
            if (options['creditcard'] == True and options['bancodobrasil'] == False):
                signalMultiplier = -1

        stmts = ofx.statements

        csReader = factory.createReaderCashFlow()

        bankStmts = []

        # btmts -> bs
        for stmt in stmts:
            bs = BankStatement()
            account = stmt.account
            origin = Origin(account)

            txs = stmt.transactions

            for tx in txs:
                cs = csReader.read(factory, tx)
                cs.value = Decimal(cs.value)
                cs.value *= signalMultiplier
                if (cs.value >= Decimal(0.0)):
                    bs.inflows.append(cs)
                else:
                    bs.outflows.append(cs)

                cs.origin = origin

                if origin.is_bank_account():
                    cs.cash_date = cs.date
                if options['creditcard'] and options.get('bradesco'):
                    cs.cash_date = stmt.dtstart
                    # TODO: BB
                    # TODO: other banks

            bankStmts.append(bs)

        return bankStmts
