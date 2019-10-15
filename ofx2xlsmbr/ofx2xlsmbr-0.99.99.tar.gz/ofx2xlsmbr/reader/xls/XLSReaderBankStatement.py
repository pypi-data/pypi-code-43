from ..IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.model.BankStatement import BankStatement

from decimal import Decimal

import logging

logger = logging.getLogger(__name__)


class XLSReaderBankStatement(IReaderBankStatement):
    def read(self, factory, ofx, options=None) -> BankStatement:
        bs = BankStatement()

        ws = ofx
        
        csReader = factory.createReaderCashFlow()
        headerRow = True
        for row in ws.values:
            # Pulando o cabecalho
            if (headerRow):
                headerRow = False
                continue
            
            cs = csReader.read(factory, row)
            if (cs.value != None):
                if (isinstance(cs.value, str)):
                    cs.value = Decimal(cs.value.replace(',', '.'))
                if (cs.value >= Decimal(0.0)):
                    bs.inflows.append(cs)
                else:
                    bs.outflows.append(cs)

        return bs