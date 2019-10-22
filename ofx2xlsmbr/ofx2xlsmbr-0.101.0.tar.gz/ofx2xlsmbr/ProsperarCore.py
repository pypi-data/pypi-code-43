from .factory.OFXReaderFactory import OFXReaderFactory
from .factory.XLSReaderFactory import XLSReaderFactory
from .factory.PDFReaderFactory import PDFReaderFactory
from .factory.XLSMWriterFactory import XLSMWriterFactory
from .factory.BSWriterFactory import BSWriterFactory

from .utils.BankStatementAdder import BankStatementAdder

from .model.BankStatement import BankStatement

import logging

logger = logging.getLogger(__name__)

class ProsperarCore(object):
    def run(self, files, returnBankStatement=False):
        #ler o caminho do arquivo e verificar se ele existe
        if (not files):
            logger.info('No files specified.')
            return

        xlsFiles = []
        ofxFiles = []
        pdfFiles = []

        for file in files:
            try:
                if ('.xls' in file.filename):
                    xlsFiles.append(file)
                elif ('.pdf' in file.filename):
                    pdfFiles.append(file)
                else:
                    ofxFiles.append(file)
            except AttributeError:
                if ('.xls' in file.name):
                    xlsFiles.append(file)
                elif ('.pdf' in file.name):
                    pdfFiles.append(file)
                else:
                    ofxFiles.append(file)

        logger.info(ofxFiles)
        logger.info(xlsFiles)
        logger.info(pdfFiles)

        #chamar o leitor ofx
        factoryOFX = OFXReaderFactory()
        readerController = factoryOFX.createReaderController()
        ofxBankStmts = readerController.read(factoryOFX, files=ofxFiles)

        #chamar o leitor xls
        factoryXLS = XLSReaderFactory()
        readerController = factoryXLS.createReaderController()
        xlsBankStmts = readerController.read(factoryXLS, files=xlsFiles)

        #chamar o leitor pdf
        factoryPDF = PDFReaderFactory()
        readerController = factoryPDF.createReaderController()
        pdfBankStmts = readerController.read(factoryPDF, files=pdfFiles)

        bankStmt = BankStatement()
        logger.info(bankStmt)

        adder = BankStatementAdder()

        for bs in ofxBankStmts:
            bankStmt = adder.add(bankStmt, bs, True)
        for bs in xlsBankStmts:
            bankStmt = adder.add(bankStmt, bs, True)
        for bs in pdfBankStmts:
            bankStmt = adder.add(bankStmt, bs, True)
        bankStmts = [bankStmt]

        #bankStmts = xlsBankStmts + ofxBankStmts + pdfBankStmts

        factory = None

        if (returnBankStatement):
            factory = BSWriterFactory()
        else:
            #chamar o escritor xlsm
            factory = XLSMWriterFactory()

        writerController = factory.createWriterController()
        return writerController.write(bankStmts, factory)

    def createXLSX(self, bankStatement):
        print(bankStatement)