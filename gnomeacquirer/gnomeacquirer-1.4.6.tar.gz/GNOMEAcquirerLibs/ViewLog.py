from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os

if hasattr(sys, 'frozen'):
    ScriptPath = os.path.join(os.path.dirname(sys.executable), "GNOMEAcquirerLibs")
else:
    ScriptPath = os.path.dirname(os.path.realpath(__file__))


class ViewLog(QWidget):
    def __init__(self, parent = None):
        super(ViewLog, self).__init__(parent)

        #set window icon

        self.windowIcon = QIcon(os.path.join(ScriptPath, "LogFile.png"))
        self.setWindowIcon(self.windowIcon)
        self.setWindowTitle("Log file")

        self.lastLogFilePath = ""
        self.log_oldContent = ""
        self.log_newContent = ""

        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)

        self.mainGroupBox = QGroupBox("Log view")
        self.logTextField = QTextEdit()
        self.logTextField.setReadOnly(1)
        self.logFilePathLineEdit = QLineEdit()
        self.logFilePathLineEdit.setReadOnly(1)
        self.logFilePathLineEdit.setToolTip("Log file path")
        self.reloadButton = QPushButton("Reload log file")
        self.reloadButton.clicked.connect(self.reloadLogFile)

        self.groupBoxLayout = QGridLayout()
        self.groupBoxLayout.addWidget(self.logFilePathLineEdit,0,0,1,1)
        self.groupBoxLayout.addWidget(self.logTextField, 1, 0, 1, 1)
        self.groupBoxLayout.addWidget(self.reloadButton, 2, 0, 1, 1)

        self.mainGroupBox.setLayout(self.groupBoxLayout)
        self.mainLayout.addWidget(self.mainGroupBox)

        self.setWindowState(Qt.WindowMaximized)


    def setLogFile(self,logFilePath):
        if logFilePath == "":
            QMessageBox.information(self,"Error","There is still no log file. You have to start the acquisition first.")
            return -1
        try:
            with open(logFilePath, 'r') as f:
                logFileData = f.readlines()
            self.logFilePathLineEdit.setText(logFilePath)
            self.log_oldContent = self.log_newContent
            self.log_newContent = "".join(logFileData)
            if self.log_newContent != self.log_oldContent:
                self.logTextField.setText(self.log_newContent)
                self.logTextField.verticalScrollBar().setValue(self.logTextField.verticalScrollBar().maximum())
            self.lastLogFilePath = logFilePath

            return 0
        except Exception as e:
            QMessageBox.information(self,"Error","There was a problem while trying to open the log file \"" + logFilePath + "\". Are you sure you haven't deleted the log file? The error says: " + str(e))
            return -2

    def reloadLogFile(self):
        self.setLogFile(self.lastLogFilePath)