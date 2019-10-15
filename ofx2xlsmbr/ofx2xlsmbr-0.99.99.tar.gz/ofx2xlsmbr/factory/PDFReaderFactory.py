from .ReaderAbstractFactory import ReaderAbstractFactory

from ofx2xlsmbr.reader.IReaderCashFlow import IReaderCashFlow
from ofx2xlsmbr.reader.IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.reader.IReaderController import IReaderController

from ofx2xlsmbr.reader.pdf.PDFReaderController import PDFReaderController
from ofx2xlsmbr.reader.pdf.PDFReaderCashFlow import PDFReaderCashFlow
from ofx2xlsmbr.reader.pdf.PDFReaderBankStatement import PDFReaderBankStatement

class PDFReaderFactory(ReaderAbstractFactory):
    def createReaderController(self) -> IReaderController:
        return PDFReaderController()

    def createReaderBankStatement(self) -> IReaderBankStatement:
        return PDFReaderBankStatement()
    
    def createReaderCashFlow(self) -> IReaderCashFlow:
        return PDFReaderCashFlow()