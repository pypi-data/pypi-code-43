from ..IReaderController import IReaderController

from ofx2xlsmbr.model.BankStatement import BankStatement
from ofx2xlsmbr.model.CashFlow import CashFlow, CashFlowType

from typing import List

from .pdfParser import PDFParser
from .PDFParserSantander import PDFParserSantander

import logging

logger = logging.getLogger(__name__)

class PDFReaderController(IReaderController):
    def read(self, factory, files=[]) -> List[BankStatement]:
        logger.debug(files)

        bankStmts = []
        bsReader = factory.createReaderBankStatement()

        if (files):
            for file in files:
                try:
                    parser = PDFParserSantander(file)
                    result = parser.run()
                except ValueError as err:
                    logger.debug(err)
                    parser = PDFParser()
                    result = parser.run(file)

                bs = bsReader.read(factory, result)
                bankStmts.append(bs)

            return bankStmts

        bsNull = BankStatement()
        return [bsNull]