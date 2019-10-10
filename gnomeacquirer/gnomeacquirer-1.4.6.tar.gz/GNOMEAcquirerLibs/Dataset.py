#!/usr/bin/python3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import serial
from GNOMEAcquirerLibs.AttributeData import *
import re
import os
import sys

if hasattr(sys, 'frozen'):
    ScriptPath = os.path.join(os.path.dirname(sys.executable), "GNOMEAcquirerLibs")
else:
    ScriptPath = os.path.dirname(os.path.realpath(__file__))

ConfigFileName = "Config.bin"

dataset_regex = r"^(?!.*?__)[a-zA-Z\_]+[a-zA-Z0-9\_]*$"
attrib_regex = r"^(?!.*?__)[a-zA-Z\_]+[a-zA-Z0-9\_\(\)]*$"

defaultDatasetName = "MagneticFields"
sanityDatasetName = "SanityChannel"

defaultMagFieldEqAttrName = "MagFieldEq"
sensorTypeAttrName = "SensorType"
sensorDirAltitudeAttrName = "SensorDirAltitude(Deg)"
sensorDirAzimuthAttrName="SensorDirAzimuth(Deg)"

AttributeKeyword_StartTime           = "%STARTTIME%"
AttributeKeyword_EndTime             = "%ENDTIME%"
AttributeKeyword_Date                = "%DATE%"
AttributeKeyword_SamplingRate        = "%SAMPLINGRATE%"
AttributeKeyword_SamplingRate_SanityChannel = "%SAMPLINGRATESANITYCHANNEL%"
AttributeKeyword_WeekNumber          = "%WEEKNUMBER%"
# AttributeKeyword_ConversionFactor    = "%CONVERSIONFACTOR%"
# AttributeKeyword_ChannelOffset       = "%OFFSET%"
AttributeKeyword_Altitude            = "%ALTITUDE%"
AttributeKeyword_Latitude            = "%LATITUDE%"
AttributeKeyword_Longitude           = "%LONGITUDE%"
AttributeKeyword_SensorDirAzimuth    = "Unset"
AttributeKeyword_SensorDirAltitude   = "Unset"
AttributeKeyword_InternalTemperature = "%INTTEMPERATURE%"
AttributeKeyword_ExternalTemperature = "%EXTTEMPERATURE%"
AttributeKeyword_ChannelRange        = "%CHANNELRANGE%"
AttributeKeyword_MissingPoints       = "%MISSINGPOINTS%"

OutputPrefix_Error = "Error_"
OutputMagFieldSensorDataset = "AuxiliaryMagneticFields"
InternalTemperaturesDataset = "InternalTemperatures"
ExternalTemperaturesDataset = "ExternalTemperatures"

ForbiddenDatasetNames = [OutputMagFieldSensorDataset,
                         InternalTemperaturesDataset,
                         ExternalTemperaturesDataset]

Tooltip_DeviceName       = "Devices are selected using their names (COM port names for Windows). Select the device, from which the data acquiring has to be done."
Tooltip_Channel          = "As this dataset will create a data array in the HDF5 file. Which channel should it use from the device?"
Tooltip_ChannelDataType  = "The data is acquired from the device as ASCII text (strings). For the data to become meaningful, it should be cast to some numerical format, such as floating-point numbers. Which format should be used? " \
                           "\nBe aware that you should cast data to something compatible; i.e., you cannot cast 1.3 to an integer."
# Tooltip_ConversionFactor = "Data received from the selected channel will be multiplied by this number."
# Tooltip_ChannelOffset    = "Data received from the selected channel will be added to this number before scaling it with the specified conversion factor."
Tooltip_MagFieldEquation = "The equation, or method, with which all channels have to be combined to produce a magnetic field. \n" \
                           "This can be changed from the attribute MagFieldEq. " \
                           "For example, if you have two datasets, say MagneticFields and Amplitude, you can combine them with any " \
                           "set of mathematical operations to produce a magnetic field. \nFor example: 2*MagneticFields+1/Amplitude[pT]. \n" \
                           "Please be careful about mathematical operations priorities and use brackets. \n" \
                           "This field is necessary for the post processing of the data."
Tooltip_SanityThreshold  = "The " + sanityDatasetName + "'s values are converted to binary numbers while processing the data. This is the threshold value, \n" \
                           "where if the voltage value is greater than this (or equal), the channel value is assigned True, and otherwise is assigned False. You can invert these with the invert option. \n" \
                                                        "Change this from within the attributes."
Tooltip_SanityInvert     = "The " + sanityDatasetName + "'s output is by default True if higher than the threshold and False if lower. If this option is True, it flips that value with a NOT gate. \n" \
                                                        "Change this from within the attributes."

Tooltip_AddAttribute     = "Each dataset contains header information (attributes). You could add custom information to your program."
Tooltip_RemoveAttribute  = "Remove an attribute that you added. You cannot remove default attributes."

Attribute_NameKey  = "Name"
Attribute_TypeKey  = "Type"
Attribute_ValueKey = "Value"

SanityChannel_Attr_Thresh_name = "Threshold(V)"
SanityChannel_Attr_InvCutoff_name = "InvertAfterThreshold"

class DatasetForm(QWidget):
    def __init__(self, datasetName, parent=None):
        super(DatasetForm, self).__init__(parent)

        #locked datasets cannot be deleted
        isLocked = False

        self.name = datasetName

        windowIcon = QIcon(os.path.join(ScriptPath, "icon.png"))
        self.setWindowIcon(windowIcon)

        self.channelLabel = QLabel("Channel:")
        self.channelLine  = QComboBox()
        self.channelLabel.setToolTip(Tooltip_Channel)
        self.channelLine.setToolTip(Tooltip_Channel)

        self.channelDatatypeLabel = QLabel("Channel elements data type: ")
        self.channelDatatypeLine  = QComboBox()
        self.channelDatatypeLine.addItem(GetTypeNameString(AttributeType.Double))
        self.channelDatatypeLine.addItem(GetTypeNameString(AttributeType.Float))
        self.channelDatatypeLine.addItem(GetTypeNameString(AttributeType.Integer64))
        self.channelDatatypeLine.addItem(GetTypeNameString(AttributeType.Integer32))
        self.channelDatatypeLabel.setToolTip(Tooltip_ChannelDataType)
        self.channelDatatypeLine.setToolTip(Tooltip_ChannelDataType)

        # self.channelConversionFactorLabel     = QLabel("Conversion factor: ")
        # self.channelConversionFactorLine      = QLineEdit("1.0")
        # self.channelConversionFactorLine.setValidator(QDoubleValidator(-1e100,1e100,20,self))
        # self.channelConversionFactorUnitLabel = QLabel()
        # self.channelConversionFactorUnitLabel.setAlignment(Qt.AlignCenter)
        # self.channelConversionFactorLabel.setToolTip(Tooltip_ConversionFactor)
        # self.channelConversionFactorLine.setToolTip(Tooltip_ConversionFactor)
        #
        # self.channelOffsetLabel               = QLabel("Channel offset (before conversion): ")
        # self.channelOffsetLine                = QLineEdit("0.0")
        # self.channelOffsetLine.setValidator(QDoubleValidator(-1e100,1e100,20,self))
        # self.channelOffsetUnitLabel               = QLabel("V")
        # self.channelOffsetUnitLabel.setAlignment(Qt.AlignCenter)
        # self.channelOffsetLabel.setToolTip(Tooltip_ChannelOffset)
        # self.channelOffsetLine.setToolTip(Tooltip_ChannelOffset)

        if self.name == defaultDatasetName:
            self.magFieldEquationLabel     = QLabel("Magnetic field equation: ")
            self.magFieldEquationLine      = QLineEdit("")
            self.magFieldEquationLine.setReadOnly(True)
            self.magFieldEquationLabel.setToolTip(Tooltip_MagFieldEquation)
            self.magFieldEquationLine.setToolTip(Tooltip_MagFieldEquation)

        if self.name == sanityDatasetName:
            self.thresholdToBinaryLabel     = QLabel("Threshold to binary: ")
            self.thresholdToBinaryLine      = QLineEdit("")
            self.thresholdToBinaryUnitsLabel = QLabel("Volts")
            self.thresholdToBinaryLine.setReadOnly(True)
            self.thresholdToBinaryLabel.setToolTip(Tooltip_SanityThreshold)
            self.thresholdToBinaryLine.setToolTip(Tooltip_SanityThreshold)
            self.thresholdToBinaryUnitsLabel.setToolTip(Tooltip_SanityThreshold)

            self.thresholdInvertCheckBox = QCheckBox("Invert thresholded value")
            self.thresholdInvertCheckBox.setToolTip(Tooltip_SanityInvert)
            # self.thresholdInvertCheckBox.setDisabled(True)
            self.thresholdInvertCheckBox.clicked.connect(self.preventToggle_InvCutoff)

        self.items = list(map(str,range(1,5)))
        self.channelLine.addItems(self.items)

        #Buttons
        self.addAttribButton    = QPushButton("Add attribute")
        self.removeAttribButton = QPushButton("Remove selected attribute")
        self.addAttribButton.setToolTip(Tooltip_AddAttribute)
        self.removeAttribButton.setToolTip(Tooltip_RemoveAttribute)

        #Buttons connections
        self.addAttribButton.clicked.connect(self.addAttribFunc)
        self.removeAttribButton.clicked.connect(self.deleteAttrib)

        #Groupbox of connection parts
        self.channelSettingsGroupbox  = QGroupBox("Channel settings")
        self.connectionGroupboxLayout = QGridLayout()

        #set the layout of groupbox
        self.channelSettingsGroupbox.setLayout(self.connectionGroupboxLayout)

        #add items to
        self.connectionGroupboxLayout.addWidget(self.channelLabel,1,0,1,1)
        self.connectionGroupboxLayout.addWidget(self.channelLine ,1,1,1,2)
        self.connectionGroupboxLayout.addWidget(self.channelDatatypeLabel,2,0,1,1)
        self.connectionGroupboxLayout.addWidget(self.channelDatatypeLine ,2,1,1,2)
        if self.name == defaultDatasetName:
            self.connectionGroupboxLayout.addWidget(self.magFieldEquationLabel,3,0,1,1)
            self.connectionGroupboxLayout.addWidget(self.magFieldEquationLine ,3,1,1,2)

        if self.name == sanityDatasetName:
            self.connectionGroupboxLayout.addWidget(self.thresholdToBinaryLabel,3,0,1,1)
            self.connectionGroupboxLayout.addWidget(self.thresholdToBinaryLine ,3,1,1,1)
            self.connectionGroupboxLayout.addWidget(self.thresholdToBinaryUnitsLabel ,3,2,1,1)
            self.connectionGroupboxLayout.addWidget(self.thresholdInvertCheckBox,4,0,1,3)

        #columns addresses
        self.AttributesColumns = {}
        self.AttributesColumns[Attribute_TypeKey]  = 0
        self.AttributesColumns[Attribute_NameKey]  = 1
        self.AttributesColumns[Attribute_ValueKey] = 2

        #create the table
        self.attribsTable = QTableWidget()
        self.attribsTable.setColumnCount(len(self.AttributesColumns))
        self.attribNameHeader  = QTableWidgetItem()
        self.attribValueHeader = QTableWidgetItem()
        self.attribTypeHeader  = QTableWidgetItem()
        self.attribNameHeader.setText("Name")
        self.attribValueHeader.setText("Value")
        self.attribTypeHeader.setText("Type")
        self.attribsTable.setHorizontalHeaderItem(self.AttributesColumns[Attribute_NameKey],self.attribNameHeader)
        self.attribsTable.setHorizontalHeaderItem(self.AttributesColumns[Attribute_ValueKey],self.attribValueHeader)
        self.attribsTable.setHorizontalHeaderItem(self.AttributesColumns[Attribute_TypeKey],self.attribTypeHeader)


        #main layout grid
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.channelSettingsGroupbox, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.removeAttribButton ,1,1,1,1)
        self.mainLayout.addWidget(self.addAttribButton    ,1,0,1,1)
        self.mainLayout.addWidget(self.attribsTable       ,2,0,1,2)

        tableSize = self.attribsTable.size()

        #bind layout to main window
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Data Acquisition")
        self.resize(tableSize.width(),self.height())

        #this next line is for Qt 5
        self.attribsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #this next line is for Qt 4
        # self.attribsTable.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        # direct connection is important here in order to avoid separating between the effect of changing
        # attributes and responding to them. We want to avoid any delays due to the eventloop
        self.attribsTable.itemChanged.connect(self.itemWasChanged, Qt.DirectConnection)

        # follow up list with all attributes in a table; this helps in restoring value when it's wrong
        self.attributesList = {}

        # when true, items will refuse to changed their values if their values are locked
        self.ImplementLock = True

        # add default attributes
        self.addDefaultAttributes()

        # self.writeConversionFactorUnit()

        self.writeMagFieldEq()

    # def writeConversionFactorUnit(self):
    #     self.channelConversionFactorUnitLabel.setText(self.attributesList["Units"].Value + "/V")

    def preventToggle_InvCutoff(self):
        if SanityChannel_Attr_InvCutoff_name in self.attributesList:

            checkstatus = Qt.Checked if ApplyAttributeType(self.attributesList[SanityChannel_Attr_InvCutoff_name].Value,
                                                                       self.attributesList[SanityChannel_Attr_InvCutoff_name].Type)\
            else Qt.Unchecked
            self.thresholdInvertCheckBox.setChecked(checkstatus)

        QMessageBox.information(self, "This control is only for viewing",
                            "Please change the control from within the attributes.")

    def writeMagFieldEq(self):
        if self.name == defaultDatasetName:
            if defaultMagFieldEqAttrName in self.attributesList:
                self.magFieldEquationLine.setText(self.attributesList[defaultMagFieldEqAttrName].Value)

    def writeSanityChannelThresholdingValues(self):
        if self.name == sanityDatasetName:
            if SanityChannel_Attr_Thresh_name in self.attributesList:

                # print(ApplyAttributeType(self.attributesList[SanityChannel_Attr_Thresh_name].Value,
                #                          self.attributesList[SanityChannel_Attr_Thresh_name].Type))
                self.thresholdToBinaryLine.setText(self.attributesList[SanityChannel_Attr_Thresh_name].Value)
            if SanityChannel_Attr_InvCutoff_name in self.attributesList:
                self.thresholdInvertCheckBox.setChecked(ApplyAttributeType(self.attributesList[SanityChannel_Attr_InvCutoff_name].Value,
                                                                       self.attributesList[SanityChannel_Attr_InvCutoff_name].Type))
    def addDefaultAttributes(self):
        self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.String),"t0"              ,AttributeKeyword_StartTime,True,True))
        self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.String),"t1"              ,AttributeKeyword_EndTime,True,True))
        self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.Double),"Longitude"       ,AttributeKeyword_Longitude,True,True))
        self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.Double),"Latitude"        ,AttributeKeyword_Latitude,True,True))
        self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.Double),"Altitude"        ,AttributeKeyword_Altitude,True,True))
        self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.String),"Date"            ,AttributeKeyword_Date,True,True))
        self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.String),"ChannelRange"    ,AttributeKeyword_ChannelRange,True,True))
        self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.Integer32),"MissingPoints",AttributeKeyword_MissingPoints,True,True))
        if self.name == defaultDatasetName:
            self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.String), "Units", "V", True, False))
            self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.String),defaultMagFieldEqAttrName,str(defaultDatasetName+"[pT]"),True,False))
            self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.Float),sensorDirAzimuthAttrName ,AttributeKeyword_SensorDirAzimuth,True,False))
            self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.Float),sensorDirAltitudeAttrName,AttributeKeyword_SensorDirAltitude,True,False))
            self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.String),sensorTypeAttrName,AttributeKeyword_SensorDirAltitude, True, False))
        if self.name == sanityDatasetName:
            self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.String), "Units", "", True, True))
            self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.Double), SanityChannel_Attr_Thresh_name,"2.5", True, False))
            self.addAttribFunc_fixed(Attribute(GetTypeNameString(AttributeType.Boolean),SanityChannel_Attr_InvCutoff_name,"False", True, False))
            self.addAttribFunc_fixed(
                Attribute(GetTypeNameString(AttributeType.Double), "SamplingRate(Hz)", AttributeKeyword_SamplingRate_SanityChannel,
                          True, True))
        else:
            self.addAttribFunc_fixed(
                Attribute(GetTypeNameString(AttributeType.Double), "SamplingRate(Hz)", AttributeKeyword_SamplingRate,
                          True, True))

    def resetTableItemFromStored(self, item):
        if item.column() == self.AttributesColumns[Attribute_NameKey]:
            self.ImplementLock = False
            self.attribsTable.item(item.row(), item.column()).setText(self.itemname)
            self.ImplementLock = True
        elif item.column() == self.AttributesColumns[Attribute_ValueKey]:
            self.ImplementLock = False
            self.attribsTable.item(item.row(), item.column()).setText(self.attributesList[self.itemname].Value)
            self.ImplementLock = True
        elif item.column() == self.AttributesColumns[Attribute_TypeKey]:
            self.ImplementLock = False
            self.attribsTable.item(item.row(), item.column()).setText(self.attributesList[self.itemname].Type)
            self.ImplementLock = True
        else:
            QMessageBox.information(self, "Severe Error",
                                    "Error: Unknown column type caught when trying to modify item. "
                                    "This shows a serious error.")
            raise AssertionError(
                "Error: Unknown column type caught when trying to modify item. This shows a serious error.")

    def disableControls(self, value=True):
        self.channelSettingsGroupbox.setDisabled(value)
        self.addAttribButton.setDisabled(value)

    def enableControls(self, value=True):
        self.disableControls(not value)

    def itemWasChanged(self, item):
        if self.ImplementLock:
            self.itemname = self.attribsTable.item(item.row(), self.AttributesColumns[Attribute_NameKey]).text()
            #if the value is locked, then restore the value from the attributesList
            if self.attributesList[self.itemname].isValueLocked:
                self.resetTableItemFromStored(item)
                QMessageBox.information(self,"Error","You cannot modify this item. It's locked!")

            #if the value is not locked, change the value
            else:
                if item.column() == self.AttributesColumns[Attribute_NameKey]:
                    self.attributesList[self.attribsTable.item(item.row(), item.column()).text()] = \
                        self.attributesList[self.itemname]
                    del self.attributesList[self.itemname]
                elif item.column() == self.AttributesColumns[Attribute_ValueKey]:
                    """
                    This part updates the values of the attributes that will be saved in the file
                    Since the DatasetForm objects are used as childs of the AcquisitionWindow object,
                    they are accessed through parents. The parents are set when DatasetForm is instantiated.
                    Keep in mind that this must be done only when acquiring data, because changing attributes this way
                    is not compatible with the default mode, including when the program is started.
                    """
                    AcqWindowWidgetReference = self.parent().parent().parent().parent().parent().parent()
                    if AcqWindowWidgetReference.acquisitionRunning:
                        success = AcqWindowWidgetReference.testAttributesCasting()
                        if success:
                            # apply the change to the list of attributes
                            self.attributesList[self.itemname].Value = self.attribsTable.item(item.row(),
                                                                                              item.column()).text()
                            AcqWindowWidgetReference.updateAttributesDuringAcquisition()
                            AcqWindowWidgetReference.saveSettingsToFile(ConfigFileName)

                        else:
                            # if bad value is given, fall back to the stored value
                            self.resetTableItemFromStored(item)
                    else:
                        # if the acquisition is not running, just change the value, as it will be tested when
                        # acquisition starts
                        self.attributesList[self.itemname].Value = self.attribsTable.item(item.row(),
                                                                                          item.column()).text()

                elif item.column() == self.AttributesColumns[Attribute_TypeKey]:
                    self.attributesList[self.itemname].Type = self.attribsTable.item(item.row(),item.column()).text()
                else:
                    QMessageBox.information(self,"Assertion Error","Error: Unknown column type caught when trying to modify item. This shows a serious error.")
                    raise AssertionError("Error: Unknown column type caught when trying to modify item. This shows a serious error.")
        # try:
        #     self.writeConversionFactorUnit()
        # except:
        #     pass

        try:
        # if True:
            self.writeMagFieldEq()
            self.writeSanityChannelThresholdingValues()
        except Exception as e:
            print("Exception was thrown while trying to write values "
                  "from attributes list to text fields. Exception says: " + str(e))

    def addAttribFunc(self):
        attrNameReturn = QInputDialog.getText(self,"Attribute name?","Enter attribute name. Please use CamelCase, and no spaces!")
        attrName = attrNameReturn[0]

        #forbid OutputPrefix_Error as a prefix
        if len(attrName) >= len(OutputPrefix_Error):
            if attrName[:len(OutputPrefix_Error)] == OutputPrefix_Error:
                QMessageBox.information(self,"Error","Attribute name cannot start with \"" + OutputPrefix_Error + "\". This word is reserved.")
                return

        if attrNameReturn[1]:
            if(not attrName == ""):
                attrReturn = QInputDialog.getItem(self,"Attribute name?",
                                                  "Enter attribute name", GetTypesList(), 0, False)
                attrType  = attrReturn[0]
                attrGiven = attrReturn[1]
                if attrGiven:
                    self.addAttribFunc_fixed(Attribute(attrType, attrName.replace(" ", "").replace("\t", ""), None, False, False))
            else:
                QMessageBox.information(self,"Error","Attribute name cannot be empty.")

    #name,value,type,islocked,isvaluelocked
    def addAttribFunc_fixed(self, attribute, modifyIfExists=False):
        if re.match(attrib_regex, attribute.Name) is None:
            QMessageBox.information(self, "Error",
                                    "Attribute name \"" + attribute.Name + "\""
                                    "is invalid. It should start with letters, and can contain numbers"
                                    " and cannot have more than one underscore consecutively.")
            return

        if attribute.Name in self.attributesList:
            if modifyIfExists:
                self.modifyAttribute(attribute.Name, attribute, False)
            return
        self.ImplementLock = False
        nameitem = QTableWidgetItem()
        nameitem.setText(attribute.Name)
        nameitem.setFlags(Qt.ItemIsEditable)
        valitem = QTableWidgetItem()

        if attribute.Value is None:
            attribute.Value = GetTypeDefaultValue_strType(attribute.Type)

        valitem.setText(attribute.Value)
        typeitem = QTableWidgetItem()
        typeitem.setText(attribute.Type)
        typeitem.setFlags(Qt.ItemIsEditable)
        self.attribsTable.setRowCount(self.attribsTable.rowCount()+1)
        self.attribsTable.setItem(self.attribsTable.rowCount()-1, self.AttributesColumns[Attribute_NameKey], nameitem)
        self.attribsTable.setItem(self.attribsTable.rowCount()-1, self.AttributesColumns[Attribute_ValueKey], valitem)
        self.attribsTable.setItem(self.attribsTable.rowCount()-1, self.AttributesColumns[Attribute_TypeKey], typeitem)
        self.scrollTableDown()

        self.attributesList[attribute.Name] = attribute
        self.ImplementLock = True

    def attributeExists(self,attributeName):
        return attributeName in self.attributesList

    def attributeLocked(self, attributeName):
        return self.attributesList[attributeName].isLocked

    def attributeValueLocked(self, attributeName):
        return self.attributesList[attributeName].isValueLocked

    def modifyAttribute(self,name,attribute,changeTypeToo=False,forceModify=False):
        doChange = True
        if self.attributesList[attribute.Name].Type == attribute.Type:
            doChange = True
        else:
            if changeTypeToo:
                doChange = True
            else:
                doChange = False

        if doChange:
            #release lock if forced to be changed
            lockWasOpened = False
            if forceModify:
                #if locked, then state that the lock was opened to relock it later
                if self.ImplementLock:
                    lockWasOpened = True
                self.ImplementLock = False
            self.attributesList[attribute.Name].Value = attribute.Value
            self.attributesList[attribute.Name].Type = attribute.Type
            for i in range(self.attribsTable.rowCount()):
                if self.attribsTable.item(i,self.AttributesColumns[Attribute_NameKey]).text() == attribute.Name:
                    tmpValueItem = QTableWidgetItem()
                    tmpTypeItem = QTableWidgetItem()
                    tmpValueItem.setText(attribute.Value)
                    tmpTypeItem.setText(attribute.Type)
                    tmpTypeItem.setFlags(Qt.ItemIsEditable)
                    self.attribsTable.setItem(i,self.AttributesColumns[Attribute_ValueKey],tmpValueItem)
                    self.attribsTable.setItem(i,self.AttributesColumns[Attribute_TypeKey],tmpTypeItem)

            #restore lock
            if lockWasOpened:
                self.ImplementLock = True


    def deleteAttrib(self):
        selectedRows = self.attribsTable.selectionModel().selectedRows()
        AcqWindowWidgetReference = self.parent().parent().parent().parent().parent().parent()
        if len(selectedRows) > 0:
            for rowObject in selectedRows:
                self.itemname = self.attribsTable.item(rowObject.row(),self.AttributesColumns[Attribute_NameKey]).text()
                if not self.attributesList[self.itemname].isLocked:
                    self.attribsTable.removeRow(rowObject.row())
                    del self.attributesList[self.itemname]
                    AcqWindowWidgetReference.updateAttributesDuringAcquisition()
                    AcqWindowWidgetReference.saveSettingsToFile(ConfigFileName)
                else:
                    QMessageBox.information(self,"Error","This attribute is locked. You can't delete it!")
        else:
            QMessageBox.information(self,"Error","No rows selected. Please select the rows you would like to remove (by clicking on their numbers on the left)")

    def scrollTableDown(self):
        self.attribsTable.verticalScrollBar().setValue(self.attribsTable.verticalScrollBar().maximum())

    def getTypesCombobox(self):
        typitem = QComboBox()
        for i in list(AttributeType):
            typitem.addItem((i.name))
        return typitem

    def closeEvent(self, event):
        while self.connectionGroupboxLayout.count():
            item = self.connectionGroupboxLayout.takeAt(0)
            item.widget().deleteLater()

        while self.mainLayout.count():
            item = self.mainLayout.takeAt(0)
            item.widget().deleteLater()

# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#
#     screen = DatasetForm()
#     screen.show()
#
#     sys.exit(app.exec_())
