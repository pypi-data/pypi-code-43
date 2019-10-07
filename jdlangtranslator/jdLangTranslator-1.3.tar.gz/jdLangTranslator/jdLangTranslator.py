#!/usr/bin/env python3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDir, QLocale, Qt
from PyQt5.QtGui import QIcon
import sys
import os

def showMessageBox(title,text):
    messageBox = QMessageBox()
    messageBox.setWindowTitle(title)
    messageBox.setText(text)
    messageBox.setStandardButtons(QMessageBox.Ok)
    messageBox.exec_()

def readLanguageFile(path):
    strings = {}
    linesContent = []
    with open(path, encoding="utf-8") as f:
        content = f.readlines()
        for line in content:
            if line.find("#") == 0:
                linesContent.append([False,line])
            else:
                try:
                    a,b = line.rstrip().split("=")
                    strings[a] = b
                    linesContent.append([True,a])
                except:
                    linesContent.append([False,line])
    return strings, linesContent
       
class TranslationHelper():
    def __init__(self, language):
        currentDir = os.path.dirname(os.path.realpath(__file__))
        langPath = os.path.join(currentDir,"translation","en_GB.lang")
        self.strings, nothing = readLanguageFile(langPath)
        langPath = os.path.join(currentDir,"translation",language + ".lang")
        if os.path.isfile(langPath):
            newStrings, nothing = readLanguageFile(langPath)
            for k, v in newStrings.items():
                self.strings[k] = v

    def translate(self, key):
        if key in self.strings:
            return self.strings[key]
        else:
            return key

class TranslateWindow(QWidget):
    def setupWindow(self):
        self.texts = TranslationHelper(QLocale.system().name())
        self.textTable = QTableWidget(0, 3)
        self.originalTextButton = QPushButton(self.texts.translate("button.loadOriginal"))
        self.translateTextLoadButton = QPushButton(self.texts.translate("button.loadTranslated"))
        self.translateTextSaveButton = QPushButton(self.texts.translate("button.saveTranslated"))
        self.originalTextLabel = QLabel(self.texts.translate("label.originalString"))
        self.originalTextEdit = QLineEdit()
        self.translateTextLabel = QLabel(self.texts.translate("label.translatedString"))
        self.translateTextEdit = QLineEdit()
        
        self.originalTextEdit.setReadOnly(True)

        self.textTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.textTable.setHorizontalHeaderLabels((self.texts.translate("table.key"),self.texts.translate("table.originalString"),self.texts.translate("table.translatedString")))
        self.textTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.textTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.textTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.textTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.textTable.verticalHeader().hide()
        self.textTable.setShowGrid(False)
        
        self.originalTextButton.clicked.connect(self.openOrinalFile)
        self.translateTextLoadButton.clicked.connect(self.openTranslatedFile)
        self.translateTextSaveButton.clicked.connect(self.saveTranslatedFile)
        self.translateTextEdit.textChanged.connect(self.translateTextInsert)
        self.textTable.cellClicked.connect(self.tableClicked)

        self.textButtonLayout = QHBoxLayout()
        self.textButtonLayout.addWidget(self.originalTextButton)
        self.textButtonLayout.addWidget(self.translateTextLoadButton)
        self.textButtonLayout.addWidget(self.translateTextSaveButton)
        
        #self.originalTextEditLayout = QHBoxLayout()
        #self.originalTextEditLayout.addWidget(self.originalTextLabel)
        #self.originalTextEditLayout.addWidget(self.originalTextEdit)

        #self.translateTextEditLayout = QHBoxLayout()
        #self.translateTextEditLayout.addWidget(self.translateTextLabel)
        #self.translateTextEditLayout.addWidget(self.translateTextEdit)

        self.editLayout = QGridLayout()
        self.editLayout.addWidget(self.originalTextLabel,0,0)
        self.editLayout.addWidget(self.originalTextEdit,0,1)
        self.editLayout.addWidget(self.translateTextLabel,1,0)
        self.editLayout.addWidget(self.translateTextEdit,1,1)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.textTable)
        self.mainLayout.addLayout(self.textButtonLayout)
        #self.mainLayout.addLayout(self.originalTextEditLayout)
        #self.mainLayout.addLayout(self.translateTextEditLayout)
        self.mainLayout.addLayout(self.editLayout)
        
        self.selectedRow = -1
        self.originalOpen = False
        self.openPath = QDir.currentPath()
        self.setLayout(self.mainLayout)
        self.resize(650, 550)
        self.setWindowTitle("jdLangTranslator")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Icon.png')))
        self.show()
          
    def tableClicked(self, row, column):
        self.selectedRow = row
        self.updateSelection()

    def updateSelection(self):
        row = self.selectedRow
        item = self.textTable.item(row, 1)
        self.originalTextEdit.setText(item.text())
        item = self.textTable.item(row, 2)
        if item != None:
            self.translateTextEdit.setText(item.text())
        else:
            self.translateTextEdit.setText("")
        self.translateTextEdit.setFocus()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.selectedRow > 0:
                self.selectedRow -= 1
                self.updateSelection()
                self.textTable.setCurrentCell(self.selectedRow,0)
        elif event.key() == Qt.Key_Down:
            if (self.selectedRow != self.textTable.rowCount()-1) and (self.selectedRow != -1):
                self.selectedRow += 1
                self.updateSelection()
                self.textTable.setCurrentCell(self.selectedRow,0)

    def translateTextInsert(self, text):
        if self.selectedRow != -1:
            newItem = QTableWidgetItem(text)
            newItem.setFlags(newItem.flags() ^ Qt.ItemIsEditable)
            self.textTable.setItem(self.selectedRow, 2, newItem)

    def openOrinalFile(self):
        path = QFileDialog.getOpenFileName(self,self.texts.translate("opendialog.title"),self.openPath,self.texts.translate("filedialog.filetype"))
        
        if path:
            if not os.path.isfile(path[0]):
                return
            self.openPath = os.path.dirname(path[0])
            originalStrings, self.lines = readLanguageFile(path[0])
            while (self.textTable.rowCount() > 0):
                self.textTable.removeRow(0)
            count = 0
            for key, value in originalStrings.items():
                keyItem = QTableWidgetItem(key)
                keyItem.setFlags(keyItem.flags() ^ Qt.ItemIsEditable)
                originalItem = QTableWidgetItem(value)
                originalItem.setFlags(originalItem.flags() ^ Qt.ItemIsEditable)
                self.textTable.insertRow(count)
                self.textTable.setItem(count, 0, keyItem) 
                self.textTable.setItem(count, 1, originalItem) 
                count += 1
            self.translateTextEdit.setText("")
            self.originalTextEdit.setText("")
            self.originalOpen = True
    
    def openTranslatedFile(self):
        if not self.originalOpen:
            showMessageBox(self.texts.translate("nooriginal.title"),self.texts.translate("nooriginal.text"))
            return

        path = QFileDialog.getOpenFileName(self,self.texts.translate("opendialog.title"),self.openPath,self.texts.translate("filedialog.filetype"))
        
        if path:
            if not os.path.isfile(path[0]):
                return
            self.openPath = os.path.dirname(path[0])
            originalStrings, nothing = readLanguageFile(path[0])
            for i in range(self.textTable.rowCount()):
                item = self.textTable.item(i, 0)
                key = item.text()
                if key in originalStrings:
                    translateItem = QTableWidgetItem(originalStrings[key])
                    translateItem.setFlags(translateItem.flags() ^ Qt.ItemIsEditable)
                    self.textTable.setItem(i, 2, translateItem)                
            self.translateTextEdit.setText("")
            self.originalTextEdit.setText("")

    def saveTranslatedFile(self):
        if not self.originalOpen:
            showMessageBox(self.texts.translate("nooriginal.title"),self.texts.translate("nooriginal.text"))
            return

        path = QFileDialog.getSaveFileName(self,self.texts.translate("savedialog.title"),os.path.join(self.openPath,self.texts.translate("savedialog.filename")),self.texts.translate("filedialog.filetype"))

        if path[0]:
            self.openPath = os.path.dirname(path[0])
            translations = {}
            for i in range(self.textTable.rowCount()):
                keyName = self.textTable.item(i, 0)
                translateText = self.textTable.item(i, 2)
                if translateText != None:
                    translations[keyName.text()] = translateText.text()
            fileHandle = open(path[0],"w",encoding="utf-8")
            for line in self.lines:
                if line[0] == False:
                    fileHandle.write(line[1])
                else:
                    if line[1] in translations:
                        fileHandle.write(line[1] + "=" + translations[line[1]] + "\n")
            fileHandle.close()

        

app = QApplication(sys.argv)
w = TranslateWindow()
w.setupWindow()
sys.exit(app.exec_())