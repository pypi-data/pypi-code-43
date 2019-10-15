from ofx2xlsmbr.reader.IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.model.BankStatement import BankStatement

import xml.etree.ElementTree as ET

class XMLReaderBankStatement(IReaderBankStatement):
    def read(self, factory, ofx, options=None) -> BankStatement:
        bs = BankStatement()

        tranList = None

        signalMultiplier = 1
        if (options):
            if (options['creditcard'] == True):
                #signalMultiplier = -1
                tranList = ofx.find('CREDITCARDMSGSRSV1').find('CCSTMTTRNRS').find('CCSTMTRS')
            else:
                tranList = ofx.find('BANKMSGSRSV1').find('STMTTRNRS').find('STMTRS')

        if (tranList):
            tranList = tranList.find('BANKTRANLIST')

        txs = tranList.findall('STMTTRN')

        csReader = factory.createReaderCashFlow()
        for tx in txs:
            cs = csReader.read(factory, tx)
            cs.value = float(cs.value)
            cs.value *= signalMultiplier
            if (cs.value >= float(0.0)):
                bs.inflows.append(cs)
            else:
                bs.outflows.append(cs)
        
        return bs