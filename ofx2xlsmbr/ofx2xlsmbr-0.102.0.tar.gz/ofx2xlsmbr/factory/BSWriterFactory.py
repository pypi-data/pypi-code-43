from .WriterAbstractFactory import WriterAbstractFactory

from ofx2xlsmbr.writer.IWriterCashFlow import IWriterCashFlow
from ofx2xlsmbr.writer.IWriterBankStatement import IWriterBankStatement
from ofx2xlsmbr.writer.IWriterController import IWriterController

from ofx2xlsmbr.writer.bankstatement.BSWriterController import BSWriterController

class BSWriterFactory(WriterAbstractFactory):
    def createWriterController(self) -> IWriterController:
        return BSWriterController()

    def createWriterBankStatement(self) -> IWriterBankStatement:
        return None
    
    def createWriterCashFlow(self) -> IWriterCashFlow:
        return None