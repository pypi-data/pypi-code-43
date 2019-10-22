from ofx2xlsmbr.reader.IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.model.BankStatement import BankStatement
from ofx2xlsmbr.model.Origin import Origin


class XMLReaderBankStatement(IReaderBankStatement):
    def read(self, factory, ofx, options=None) -> BankStatement:
        bs = BankStatement()

        tranList = None

        signalMultiplier = 1
        if (options):
            if (options['creditcard'] == True):
                #signalMultiplier = -1
                tranList = ofx.find('CREDITCARDMSGSRSV1').find('CCSTMTTRNRS').find('CCSTMTRS')

                # Origin
                institution = None
                branch = None
                account_id = tranList.find('CCACCTFROM').find('ACCTID').text
                account_type = 'CREDITCARD'
            else:
                tranList = ofx.find('BANKMSGSRSV1').find('STMTTRNRS').find('STMTRS')

                # Origin
                account = tranList.find('BANKACCTFROM')
                institution = account.find('BANKID').text
                branch = account.find('BRANCHID').text
                account_id = account.find('ACCTID').text
                account_type = 'BANKACCOUNT'

        origin = Origin(
            account_id=account_id,
            branch=branch,
            institution=institution,
            type=account_type,
        )

        if (tranList):
            tranList = tranList.find('BANKTRANLIST')

        txs = tranList.findall('STMTTRN')

        csReader = factory.createReaderCashFlow()
        for tx in txs:
            cs = csReader.read(factory, tx)
            cs.origin = origin
            cs.value = float(cs.value)
            cs.value *= signalMultiplier
            if (cs.value >= float(0.0)):
                bs.inflows.append(cs)
            else:
                bs.outflows.append(cs)
        
        return bs
