from .IReaderController import IReaderController

from ofx2xlsmbr.model.BankStatement import BankStatement

from ofx2xlsmbr.factory.XMLReaderFactory import XMLReaderFactory

from typing import List
import datetime
from pytz import timezone

import logging

logger = logging.getLogger(__name__)

from ofxtools import OFXTree

class OFXReaderController(IReaderController):
    def read(self, factory, files=[]) -> List[BankStatement]:
        logger.debug(files)

        bankStmts = []
        bsReader = factory.createReaderBankStatement()
        count_open = 0

        if (files):
            for file in files:
                content = file.read()
                file.seek(0)
                
                upperContent = str(content).upper()
                count_open += upperContent.count('<STMTTRN>')

                try:
                    tree = OFXTree()
                    tree.parse(file)
                    self.treatBradescoException(tree)

                    #check creditcard
                    root = tree.getroot()
                    options = {}
                    if (root.findall("CREDITCARDMSGSRSV1")):
                        options['creditcard'] = True

                        # KN-177 - Check if Bradesco credit card
                        ccstmttrnrs = root.findall('CREDITCARDMSGSRSV1')[0].findall('CCSTMTTRNRS')[0]
                        banktranlist = ccstmttrnrs.findall('CCSTMTRS')[0].findall('BANKTRANLIST')[0]
                        dtstart = banktranlist.findall('DTSTART')[0]
                        dtend = banktranlist.findall('DTEND')[0]
                        if dtstart.text == dtend.text:
                            options['bradesco'] = True
                    else:
                        options['creditcard'] = False

                    options['bancodobrasil'] = False
                    fi = root.findall("SIGNONMSGSRSV1")[0].findall("SONRS")[0].findall("FI")
                    if (fi):
                        org = fi[0].findall("ORG")
                        if (org != None and "Banco do Brasil" in org[0].text):
                            options['bancodobrasil'] = True

                    convertedTree = tree.convert()
                    bs = bsReader.read(factory, convertedTree, options)
                    bankStmts.append(bs)
                except IndexError:
                    # ofx nao consegue ler versao 220. Ler como XML
                    file.seek(0)
                    xmlFactory = XMLReaderFactory()
                    xmlReader = xmlFactory.createReaderController()
                    bs = xmlReader.read(xmlFactory, files=[file])
                    bankStmts.append(bs)

            total_count = 0
            for bankStmtList in bankStmts:
                for bs in bankStmtList:
                    total_count += len(bs.inflows)
                    total_count += len(bs.outflows)

            assert count_open == total_count

            return bankStmts
            
        bsNull = BankStatement()
        return [bsNull]

    # Este tratamento de erro tem que ser melhor descrito
    def treatBradescoException(self, tree):
        root = tree.getroot()
        dtServer = root.findall("SIGNONMSGSRSV1")[0].findall("SONRS")[0].findall("DTSERVER")[0]
        try:
            if (int(dtServer.text) == 0):
                unknownDateInThePast = datetime.datetime(1985, 10, 21, tzinfo=timezone('Brazil/East'))
                dtServer.text = unknownDateInThePast
        except ValueError:
            pass
            # se dtServer for um datetime, ele da erro na conversao para int
            # logger.info('Correcting DTServer')

        # se for cartao de credito, a data do balanco vem errada
        try:
            creditCardTransRs = root.findall("CREDITCARDMSGSRSV1")[0].findall("CCSTMTTRNRS")

            for c in creditCardTransRs:
                dtBalance = c.findall("CCSTMTRS")[0].findall("LEDGERBAL")[0].findall("DTASOF")[0]

                try:
                    if (int(dtBalance.text) == 0):
                        unknownDateInThePast = datetime.datetime(1985, 10, 21, tzinfo=timezone('Brazil/East'))
                        dtBalance.text = unknownDateInThePast
                except ValueError:
                    pass
        except IndexError:
            pass
