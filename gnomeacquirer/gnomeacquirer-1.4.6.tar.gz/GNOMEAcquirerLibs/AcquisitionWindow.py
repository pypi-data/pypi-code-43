#!/usr/bin/python3

from GNOMEAcquirerLibs.DataAcquire import *
from GNOMEAcquirerLibs.AcquisitionConfig import *
from GNOMEAcquirerLibs.DataAnalysis import *
from GNOMEAcquirerLibs.Meta import *
from GNOMEAcquirerLibs.ViewLog import *
import numpy as np
import h5py
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
import socket
import urllib
import subprocess
import errno
from math import log
import traceback
import re
import gnomedata as gd
import sympy
import math
import collections
import ssl


# constants

ConfigAttribute_Prefix = "att_"
ConfigAttribute_NameSuffix = "_name"
ConfigAttribute_ValueSuffix = "_value"
ConfigAttribute_TypeSuffix = "_type"
ConfigAttribute_ValueLockedSuffix = "_valueLocked"
ConfigAttribute_LockedSuffix = "_locked"
ConfigOption_Prefix             = "opt_"
ConfigOptionName_SelectedDevice     = "SelectedDevice"
ConfigOptionName_SelectedChannel    = "SelectedChannel"
ConfigOptionName_ChannelDatatype    = "SelectedDataType"
ConfigOptionName_DataPath = "DataPath"
ConfigOptionName_StationName = "StationName"
ConfigOptionName_PortName = "SelectedDevice"

AcquisitionTypeOption_COM  = "Acquisition over COM"
AcquisitionTypeOption_Fake = "Fake acquisition"
AcquisitionTypeOption_File = "Acquisition from files..."

StationType_MagneticField = "Magnetic field sensor"
StationType_AtomicClock   = "Atomic Clock(s) station"

# fix window icon not showing up in the taskbar for ViewLog()
if sys.platform.startswith('win'):
    import ctypes

    myappid = 'budker.gnomeacquirer.subproduct.version'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


# a function that takes an attribute string, and returns it replaced by values when necessary according
# to pre-defined keywords

# a function that doesn't require data information for testing initial values of the attributes
def ApplyAttributeReplacement_tester(attrStr):
    TimeV = datetime.datetime.utcnow()
    attrStrReplaced = copy.deepcopy(attrStr)
    StartTime    = TimeV.strftime(DataBatch.f_timeFormat)
    EndTime      = TimeV.strftime(DataBatch.f_timeFormat)
    Date         = TimeV.strftime(DataBatch.f_dateFormat)
    SR           = "100"
    Weeknum      = "12345"
    Longitude    = "1.23"
    Latitude     = "3.45"
    Altitude     = "6.78"
    IntTemp      = "14.15"
    ExtTemp      = "12.13"
    ChRange      = "+/-1.25[V]"
    MissingPoints = "2"

    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_StartTime,StartTime)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_EndTime,EndTime)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_Date,Date)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_SamplingRate,SR)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_SamplingRate_SanityChannel,SR)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_WeekNumber,Weeknum)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_Altitude,Altitude)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_Latitude,Latitude)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_Longitude,Longitude)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_InternalTemperature,IntTemp)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_ExternalTemperature,ExtTemp)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_MissingPoints,MissingPoints)

    return attrStrReplaced

UpdateFileLink = "https://budker.uni-mainz.de//download/GNOMEAcquirer/updates.xml"


def human_readable_bytes(x):
    # hybrid of http://stackoverflow.com/a/10171475/2595465
    #     with http://stackoverflow.com/a/5414105/2595465
    if x <= 0: return '0 B'
    magnitude = math.floor(log(abs(x),10.24))
    if magnitude > 16:
        format_str = '%iP'
        denominator_mag = 15
    else:
        float_fmt = '%2.1f' if magnitude % 3 == 1 else '%1.2f'
        illion = math.floor(magnitude / 3)
        format_str = float_fmt + ['B', ' KB', ' MB', ' GB', ' TB', ' PB'][illion]
        val = (x * 1.0 / (1024 ** illion))
        val_str = (format_str % val).lstrip('0')
        if len(val_str) > 0 and val_str.startswith("."):
            val_str = "0" + val_str
    return val_str


def CheckForUpdates():
    # if not hasattr(sys, 'frozen'):
    #     return {"success": False, "msg": "Non frozen (non-executable) apps shall not upgraded from here."}

    try:
        with urllib.request.urlopen(UpdateFileLink, context=ssl._create_unverified_context()) as f:
            print("Check for newer versions...")
            tree = ET.parse(f)
            root = tree.getroot()
            versionTree = root.find('version')
            downloadLinkTree = root.find('softwareLink')
            print("Current version: " + SOFTWARE_VERSION)
            print("Latest version: " + versionTree.text)
            if not IsVersionNewer(versionTree.text):
                return {'newerAvailable': False, 'url': '', 'version': versionTree.text, "success": True}
            else:
                return {'newerAvailable': True, 'url': downloadLinkTree.text,
                        'version': versionTree.text, "success": True}
    except Exception as e:
        traceback.print_exc()
        print("Error while trying to get update information. Exception says: " + str(e))
        return {"success": False, "msg": str(e)}


def IsVersionNewer(version):
    isBeta = (len(SOFTWARE_VERSION.split(".")) > 3)
    currentSoftwareVersion = ".".join(SOFTWARE_VERSION.split(".")[0:3]) #fourth part is for beta versions
    currentVersionSplit = list(map(int,currentSoftwareVersion.split(".")))
    newVersionSplit = list(map(int,version.split(".")))

    if isBeta and currentVersionSplit == newVersionSplit: #if the current version is beta and the new version is not beta, then take it
        return True

    # print(currentVersionSplit)
    # print(newVersionSplit)
    if len(newVersionSplit) != 3:
        raise Exception("Error while parsing retrieved version number. The version value " + version + " is not valid.")

    if int(newVersionSplit[0]) > int(currentVersionSplit[0]):
        return True
    elif int(newVersionSplit[0]) < int(currentVersionSplit[0]):
        return False

    if int(newVersionSplit[1]) > int(currentVersionSplit[1]):
        return True
    if int(newVersionSplit[1]) < int(currentVersionSplit[1]):
        return False

    elif int(newVersionSplit[2]) > int(currentVersionSplit[2]):
        return True
    elif int(newVersionSplit[2]) < int(currentVersionSplit[2]):
        return False

    return False


def clean(item):
    """Clean up the memory by closing and deleting the item if possible."""
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(list(item).pop())
    else:
        try:
            item.close()
        except: # deleted or no close method
            try:
                item.deleteLater()
            except: # deleted or no deleteLater method
                pass


Tooltip_StationName      = "Station name (preferably GNOME synchronizer username) to be inserted as a prefix to file names; e.g., berkeley01"
Tooltip_DataPath         = "Path to the folder where acquired data will be stored. This is the same folder that has to be chosen for the synchronizer."
Tooltip_AddDataset       = "Add a dataset to the saved HDF5 file. The dataset contains data that is acquired from a channel in the acquisition device, " \
                           "in addition to some attributes (header information) that is contained in the table shown in the dataset tab."
Tooltip_RemoveDataset    = "Remove an existing dataset"
Tooltip_AcquisitionType  = "Type of acquisiton; either over COM, or from data files, or a fake acquisition for testing."
Tooltip_DumpAcquiredData = "When this checkbox is enabled, in addition to writing HDF5 files, a copy of the strings received from the box will be saved in the directory " + "\"" + stringDumpFolderName + "\" under your data directory."
Tooltip_ParanoidMode     = "Paranoid mode initiates a less performant data acquisition model but safer. It reads lines from the device line by line.\n" \
                           "In contrast, non-paranoid mode empties the buffer of the device and parses it. Use this if you think the software has a problem\n" \
                           "with standard acquisition mode. This mode works only for COM acquisition."
Tooltip_StartAcquisition = "Start data acquisition from the device based on the configuration you chose. "
Tooltip_MissingBatches   = "Due to data communication issues, data may be lost within communication. This is an estimate of the number of batches missing during communication."

if hasattr(sys, 'frozen'):
    ScriptPath = os.path.join(os.path.dirname(sys.executable),"GNOMEAcquirerLibs")
else:
    ScriptPath = os.path.dirname(os.path.realpath(__file__))


class AcqusitionWindow(QWidget):
    #The following signal definition is per object, nevertheless it has to be here.
    #Qt takes a copy of it for each object
    stopAcquisitionSignal = QtCore.Signal()
    # BatchesToStoredInSingleFile = 60
    BatchSecondsLength = 1

    dlProgress_update = pyqtSignal(float)
    dlProgress_done = pyqtSignal()


    def __init__(self, parent = None):
        super(AcqusitionWindow, self).__init__(parent)

        self.splash_pix = QPixmap(os.path.join(ScriptPath, 'icon.png'))
        self.splash = QSplashScreen(self.splash_pix, Qt.WindowStaysOnTopHint)
        self.splash.setMask(self.splash_pix.mask())
        self.splash.show()
        QCoreApplication.processEvents()

        is_windows = sys.platform.startswith('win')

        self.logFilePath = ""
        self.viewLogWidget = ViewLog()

        self.dataCollected = {}

        #set window icon
        self.windowIcon = QIcon(os.path.join(ScriptPath, "icon.png"))
        self.setWindowIcon(self.windowIcon)
        self.setWindowTitle("GNOME Data Acquisition Software")

        #initiate tabs widget
        self.datasetsTabs   = QTabWidget()
        self.listOfDatasets = {}

        #add/remove datasets button objects
        self.addDatasetButton    = QPushButton("Add dataset")
        self.addDatasetButton.setToolTip(Tooltip_AddDataset)
        self.removeDatasetButton = QPushButton("Remove dataset")
        self.removeDatasetButton.setToolTip(Tooltip_RemoveDataset)

        #Splitter of the two halves of the main window
        self.mainWidgetsSplitter = QSplitter()
        self.mainWidgetsSplitter.setOrientation(Qt.Horizontal)
        self.mainLeftWidget = QWidget()
        self.mainLeftGridLayout = QGridLayout()
        self.mainRightWidget = QWidget()
        self.mainRightGridLayout = QGridLayout()
        self.mainWidgetsSplitter.addWidget(self.mainLeftWidget)
        self.mainWidgetsSplitter.addWidget(self.mainRightWidget)
        self.mainLeftWidget.setLayout(self.mainLeftGridLayout)
        self.mainRightWidget.setLayout(self.mainRightGridLayout)

        #data path groupbox
        self.dataGroupbox = QGroupBox()
        self.dataGroupbox.setTitle("Data path")
        self.dataGroupbox.setToolTip(Tooltip_DataPath)
        self.dataLayout = QGridLayout()
        self.dataGroupbox.setLayout(self.dataLayout)

        #Acquisition type (acquire, read files, fake)
        self.acqTypeOptions = \
            {
                0: AcquisitionTypeOption_COM,
                1: AcquisitionTypeOption_Fake,
                2: AcquisitionTypeOption_File
            }
        self.acquisitionFromFilesPath = ""

        self.inputOptionsGroupbox       = QGroupBox("Input options")
        self.inputOptionsGroupboxLayout = QGridLayout()
        self.stationNameLine       = QLineEdit()
        self.stationNameLabel      = QLabel("Station name: ")
        self.inputOptionsGroupbox.setLayout(self.inputOptionsGroupboxLayout)
        self.inputOptionsGroupboxLayout.addWidget(self.stationNameLabel,0,0,1,1)
        self.inputOptionsGroupboxLayout.addWidget(self.stationNameLine,0,1,1,3)

        self.stationNameTooltipText = Tooltip_StationName
        self.stationNameLine.setToolTip(self.stationNameTooltipText)
        self.stationNameLabel.setToolTip(self.stationNameTooltipText)

        self.portLabel = QLabel("Device:")
        self.portLine  = QComboBox()
        self.portLabel.setToolTip(Tooltip_DeviceName)
        self.portLine.setToolTip(Tooltip_DeviceName)
        self.refreshDevicesButton = QPushButton("Refresh devices")

        self.acquisitionTypeLabel = QLabel("Acquisition type: ")
        self.acquisitionTypeLine  = QComboBox()
        [self.acquisitionTypeLine.addItem(self.acqTypeOptions[i]) for i in self.acqTypeOptions]
        self.acquisitionTypeLabel.setToolTip(Tooltip_AcquisitionType)
        self.acquisitionTypeLine.setToolTip(Tooltip_AcquisitionType)
        self.inputOptionsGroupboxLayout.addWidget(self.acquisitionTypeLabel,1,0,1,1)
        self.inputOptionsGroupboxLayout.addWidget(self.acquisitionTypeLine ,1,1,1,3)
        self.inputOptionsGroupboxLayout.addWidget(self.portLabel,2,0,1,1)
        self.inputOptionsGroupboxLayout.addWidget(self.portLine ,2,1,1,2)
        self.inputOptionsGroupboxLayout.addWidget(self.refreshDevicesButton ,2,3,1,1)


        self.dataPathLine         = QLineEdit()
        self.dataPathBrowseButton = QPushButton("Browse")
        self.dataPathLine.setToolTip(Tooltip_DataPath)
        self.dataPathBrowseButton.setToolTip(Tooltip_DataPath)
        self.dataPathBrowseButton.clicked.connect(self.browseDataFolder)
        self.pathCompleter = QCompleter()
        self.pathCompleterModel = QDirModel()
        self.pathCompleterModel.setFilter(QDir.AllDirs | QDir.NoDot | QDir.NoDotDot)
        self.pathCompleter.setModel(self.pathCompleterModel)
        self.dataPathLine.setCompleter(self.pathCompleter)

        self.dataLayout.addWidget(self.dataPathLine,0,0,1,1)
        self.dataLayout.addWidget(self.dataPathBrowseButton,0,1,1,1)

        self.datasetsGroupbox = QGroupBox()
        self.datasetsGroupbox.setTitle("Datasets")
        self.datasetsGroupboxLayout = QGridLayout()
        self.datasetsGroupboxLayout.addWidget(self.addDatasetButton,0,0,1,1)
        self.datasetsGroupboxLayout.addWidget(self.removeDatasetButton,0,1,1,1)
        self.datasetsGroupboxLayout.addWidget(self.datasetsTabs,1,0,1,2)
        self.datasetsGroupbox.setLayout(self.datasetsGroupboxLayout)

        self.startAcqText = "Start data acquisition"
        self.stopAcqText  = "Stop data acquisition"
        self.startStopButtonWaitText = "Please wait..."
        self.acquisitionRunning = False

        self.startAcquisitionButton = QPushButton(self.startAcqText)
        self.startAcquisitionButton.setToolTip(Tooltip_StartAcquisition)


        #dump acquired strings
        self.dumpAcquiredStringsToFileCheckbox = QCheckBox("Dump acquired strings to the folder \"" + stringDumpFolderName + "\" (watch for diskspace)")
        self.dumpAcquiredStringsToFileCheckbox.setToolTip(Tooltip_DumpAcquiredData)

        #paranoid mode checkbox
        self.paranoidModeCheckbox = QCheckBox("Paranoid acquisition mode (less efficient)")
        self.paranoidModeCheckbox.setToolTip(Tooltip_ParanoidMode)

        #data analysis station
        self.dataAnalysisGroupBox = QGroupBox()
        self.dataAnalysisGroupBox.setTitle("Data view")
        self.dataAnalysisLayout   = QGridLayout()
        self.dataAnalysisGroupBox.setLayout(self.dataAnalysisLayout)


        self.dataAnalysisWidget = DataAnalysisWidget()

        # add the plot canvas to a window
        self.dataAnalysisLayout.addWidget(self.dataAnalysisWidget)

        self.aboutButton = QPushButton("About")
        self.checkForUpdatesButton = QPushButton("Check for updates")

        #Logging groupbox
        self.loggingGroupBox = QGroupBox()
        self.loggingGroupBox.setTitle("Acquired data status")
        self.loggingLayout   = QGridLayout()
        self.loggingGroupBox.setLayout(self.loggingLayout)

        self.missingBatchesLabel = QLabel("Missing batches: ")
        self.missingBatchesLine  = QLineEdit()
        self.missingBatchesResetButton = QPushButton("Reset counter")
        self.viewLogFileButton = QPushButton("View log file")
        self.missingBatchesLine.setDisabled(0)
        self.missingBatchesLabel.setToolTip(Tooltip_MissingBatches)
        self.missingBatchesLine.setToolTip(Tooltip_MissingBatches)
        self.missingBatchesLine.setReadOnly(1)
        self.missingBatchesResetButton.setToolTip(Tooltip_MissingBatches)
        self.loggingLayout.addWidget(self.missingBatchesLabel, 0, 0, 1, 1)
        self.loggingLayout.addWidget(self.missingBatchesLine, 0, 1, 1, 1)
        self.loggingLayout.addWidget(self.missingBatchesResetButton, 0, 2, 1, 1)
        self.loggingLayout.addWidget(self.viewLogFileButton, 0, 3, 1, 1)
        self.resetMissingBatches()
        self.missingBatchesResetButton.clicked.connect(self.resetMissingBatches)
        self.viewLogFileButton.clicked.connect(self.viewLogFile)


        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.mainWidgetsSplitter)

        self.mainLeftGridLayout.addWidget(self.dataGroupbox,0,0,1,4)
        self.mainLeftGridLayout.addWidget(self.inputOptionsGroupbox,1,0,1,4)
        self.mainLeftGridLayout.addWidget(self.datasetsGroupbox,3,0,1,4)
        self.mainLeftGridLayout.addWidget(self.dumpAcquiredStringsToFileCheckbox,4,0,1,4)
        self.mainLeftGridLayout.addWidget(self.paranoidModeCheckbox,5,0,1,4)
        self.mainLeftGridLayout.addWidget(self.startAcquisitionButton,6,0,1,4)
        if is_windows:
            # if hasattr(sys, 'frozen'):
            self.mainLeftGridLayout.addWidget(self.checkForUpdatesButton, 7, 0, 1, 2)
            self.mainLeftGridLayout.addWidget(self.aboutButton, 7, 2, 1, 2)
            # else:
            #     self.mainLeftGridLayout.addWidget(self.aboutButton, 7, 0, 1, 4)
        else:
            self.mainLeftGridLayout.addWidget(self.aboutButton, 7, 0, 1, 4)

        self.mainRightGridLayout.addWidget(self.dataAnalysisGroupBox,0,4,6,1)
        self.mainRightGridLayout.addWidget(self.loggingGroupBox,6,4,2,1)


        self.addDatasetButton.clicked.connect(self.addDataset)
        self.removeDatasetButton.clicked.connect(self.removeDataset)
        self.startAcquisitionButton.clicked.connect(self.startAcquisitionButtonAction)
        self.acquisitionTypeLine.currentIndexChanged.connect(self.acquisitionTypeChanged)
        self.aboutButton.clicked.connect(self.showAboutDialog)
        self.checkForUpdatesButton.clicked.connect(self.updateSoftwareSlot)

        #refresh devices list and create button response
        self.refreshDevices()
        self.refreshDevicesButton.clicked.connect(self.refreshDevices)

        self.setLayout(self.mainLayout)

        self.screen = QDesktopWidget().screenGeometry()

        self.resize(int(round(self.screen.width()*0.75)),int(round(self.screen.height()*0.75)))

        self.addDatasetWithName(defaultDatasetName,True,True)
        self.addDatasetWithName(sanityDatasetName,True,True)

        #initialize thread object, in order to check whether it exists on program exit
        #see the member function closeEvent()
        self.acquirer = None

        #plot lock as mutex
        self.plotLocked = False

        #skip plots to avoid having the window freeze due to rapid plotting
        #The mechanism simply calculates an average of how long it takes to plot
        #and waits by some factor of that before plotting again
        self.plot_before_time = None
        self.plot_after_time = None
        self.plot_average_time = 0.5
        self.plot_average_time_window = collections.deque(maxlen=10)
        self.plot_average_time_window.append(0.5)



        # self.dataPathLine.setText("D:\gnome\clientTests")
        # self.stationNameLine.setText("mainz01")

        self.loadSettingsFromFile(ConfigFileName)

        self.lastAttrs = {}

        try:
            cfgtestfile = "tmpcfgtest.bin"
            self.saveSettingsToFile(cfgtestfile)
            os.remove(cfgtestfile)
        except:
            QMessageBox.information(self,"Error","Unable to save configuration file in the program path: " +
            os.path.dirname(os.path.realpath(__file__)) + "\n\n" +
            "This means that you have to redo the configuration of your acquisition every time you start the program.\n\n"
            "To resolve this, make sure you have write access to that path. It is possible that you have the program installed on drive C:, "
            "which is considered a secured system drive in Windows versions newer than Vista. Try running the program as admin "
            "by right clicking on the program and selecting \"Run as administrator\"")

        if is_windows:
            self.updateTimer = QTimer(self)

            self.updateTimer.timeout.connect(self.updateSoftwareSlot_silent)
            self.updateTimer.start(15*60*1000) #check for updates once per hour

            self.updateSoftware(True)


    def doAfterShown(self):
        self.splash.finish(self)
        QCoreApplication.processEvents()
        QMessageBox.information(self, "Information",
                                "Please be aware that the program will not stop the acquisition when errors occur. "
                                "The program will merely continuously skip the data that has the problem. If you notice that all data is being skipped (a counter is provided for that purpose), then review the log and check the cause of the problem. "
                                "This is due to issues related to data communication reliability. Until these issues are resolved, there is no way to tell the difference between corrupt data and user input problems in the acquisition box.")



    def updateSoftwareSlot(self):
        self.updateSoftware(False)

    def updateSoftwareSlot_silent(self):
        self.updateSoftware(True)

    def updateSoftware(self, silent):
        # if not hasattr(sys, 'frozen'):
        #     return

        try:
            updatesReturn = CheckForUpdates()
        except Exception as e:
            if not silent:
                QMessageBox.information(self, "Update error", "Error while checking for updates. Are you connected to the internet?\n\nException says: " + str(e))

            traceback.print_exc()
            print("Error while checking for updates. Are you connected to the internet? Exception says: " + str(e))
            return

        if updatesReturn["success"] is False:
            if not silent:
                QMessageBox.information(self, "Update error", "Checking for updates failed. Exception says: " +
                                        str(updatesReturn["msg"]))
            print("Checking for updates failed. Exception says: " + str(updatesReturn["msg"]))
            return

        if updatesReturn['newerAvailable'] is False:
            if not silent:
                QMessageBox.information(self, "Update info", "You have the latest version. No need for updates.")

        else:
            self.checkForUpdatesButton.setStyleSheet('QPushButton {color: red;}')
            self.checkForUpdatesButton.setText("Update is available!")
            self.updateTimer.stop()
            if not silent:
                is_windows = sys.platform.startswith('win')
                is_frozen = hasattr(sys, 'frozen')

                if is_windows and is_frozen:
                    reply = QMessageBox.question(self, 'Update available',
                                             "An update to version " + updatesReturn['version'] + " is available. Would you like to download it now?",
                                             QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.No:
                        return

                    self.doUpdateSoftware(updatesReturn)
                else:
                    QMessageBox.information(self, "Update info", "There is an update available. "
                                                                 "Please upgrade this software ASAP using your "
                                                                 "Python package manager.\n"
                                                                 "For Anaconda, run:\n"
                                                                 " conda upgrade gnomeacquirer\n"
                                                                 "For pip, run:\n"
                                                                 " pip3 install gnomeacquirer -U")

    def doUpdateSoftware(self,updatesReturn):
        updateFilePath = QFileDialog.getSaveFileName(self, "Save downloaded file...",
                                                     os.path.join(os.path.expanduser("~\\Downloads\\"),
                                                                  updatesReturn['url'].split('/')[-1]),
                                                     "All Files (*)")
        # sometimes QFileDialog.getSaveFileName returns a tuple with the filter as the second element
        if type(updateFilePath) == tuple:
            updateFilePath = updateFilePath[0]

        if updateFilePath != "":
            downloadDialogStaticText = "Please wait while GNOME Acquirer version " + updatesReturn['version'] + " is downloaded...\n"
            downloadDialog = QProgressDialog(self)
            downloadDialog.setWindowTitle("Downloading update...")
            screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
            screenRes = QDesktopWidget().screenGeometry(screen)

            downloadDialog.resize(screenRes.width() / 2, downloadDialog.height())
            downloadDialog.setModal(True)
            downloadDialog.setLabelText(downloadDialogStaticText)
            centerPoint = QDesktopWidget().screenGeometry(screen).center()
            centerPoint.setX(centerPoint.x() - downloadDialog.width() / 2)
            centerPoint.setY(centerPoint.y() - downloadDialog.height() / 2)
            downloadDialog.move(centerPoint)

            downloadDialog.show()

            downloadDialog.isDownloadCanceled = False
            downloadDialog.isFinishActionDone = False

            def setDownloadProgressValue(val):
                downloadDialog.setValue(val)
                downloadDialog.setLabelText(downloadDialogStaticText +
                                            str(human_readable_bytes(downloadDialog.downloadedFileSize)) + " / " +
                                            str(human_readable_bytes(downloadDialog.totalFileSize)))

            def cancelDownload():
                downloadDialog.isDownloadCanceled = True

            def downloadDone():
                print("Update download finished.")

                reply = QMessageBox.question(self, 'Download finished!',
                                             "Update downloaded. Would you like to run it? (the current session will be closed)",
                                             QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    try:
                        os.startfile(updateFilePath) #run the downloaded file
                        sys.exit(0)
                    except Exception as e:
                        QMessageBox.information(self, "Cannot start installer",
                                                "Unable to start installer. Reason: " + str(e))

            self.dlProgress_update.connect(setDownloadProgressValue)
            downloadDialog.canceled.connect(cancelDownload)
            self.dlProgress_done.connect(downloadDone)

            def report(block_count, block_size, total_size):
                QCoreApplication.processEvents()
                downloadDialog.totalFileSize = total_size
                downloadDialog.downloadedFileSize = block_count * block_size
                if downloadDialog.isDownloadCanceled:
                    raise Exception("User canceled the download.")
                else:
                    progVal = float((100 * block_count * block_size) / total_size)
                    if block_count == 0:
                        # print("block_count == 0")
                        self.dlProgress_update.emit(0)
                    # if (block_count * block_size) >= total_size:
                    #     self.dlProgress_done.emit()
                    #     downloadDialog.isFinishActionDone = True
                    # print("BS={0} TS={1} incAmount={2}".format(block_size,total_size,incAmount))
                    else:
                        self.dlProgress_update.emit(progVal)

            try:
                socket.setdefaulttimeout(10)
                urllib.request.urlretrieve(updatesReturn['url'], updateFilePath, reporthook=report)
            except Exception as e:
                print("Download stopped. Reason: " + str(e))
                downloadDialog.isDownloadCanceled = True
                QMessageBox.information(self, "Download stopped", "Download stopped. Reason: " + str(e))

            if not downloadDialog.isDownloadCanceled:
                self.dlProgress_done.emit()

            #cleanup
            urllib.request.urlcleanup()
            #since signals are bound to the main window, they have to be disconnected manually
            self.dlProgress_done.disconnect(downloadDone)
            self.dlProgress_update.disconnect(setDownloadProgressValue)
            downloadDialog.destroy()
            print(updateFilePath)
        else:
            print("No path given")

    def viewLogFile(self):
        if(self.viewLogWidget.setLogFile(self.logFilePath) >= 0):
            self.viewLogWidget.show()

    def showAboutDialog(self):
        QMessageBox.about(self,"About GNOME Data Acquirer","GNOME Data Acquirer, version " + SOFTWARE_VERSION + "\n\n"
            "This program was designed by the Budker Group in Mainz, by Samer Afach. \n"
            "In case you find bugs or you have suggestions, send an e-mail to afach@uni-mainz.de")

    def isFolderWritable(self,path):
        try:
            testfile = tempfile.TemporaryFile(dir = path)
            testfile.close()
        except:
            return False
        return True

    def isDataPathValid(self):
        path = self.dataPathLine.text()
        if path != "":
            if self.isFolderWritable(path):
                return True
            else:
                return False
        else:
            return False

    def browseDataFolder(self):
        self.dataPathLine.setText(QFileDialog.getExistingDirectory(self, "Open Directory", "C:", QFileDialog.ShowDirsOnly))

    def resetMissingBatches(self):
        self.missingBatches = 0
        self.updateMissingBatchesField()

    def updateMissingBatchesField(self):
        self.missingBatchesLine.setText(str(self.missingBatches))

    def addMissingBatches(self,missingBatches):
        self.missingBatches += missingBatches
        self.updateMissingBatchesField()

    def addDataset(self):
        datasetName = QInputDialog.getText(self,"Dataset name?","Enter dataset name (CamelCase, no spaces)")[0].replace(" ","").replace("\t","")
        if not datasetName == "":
            if re.match(dataset_regex, datasetName) is None:
                QMessageBox.information(self, "Error",
                                        "Dataset name \"" + datasetName + "\""
                                        "is invalid. It should start with letters, and can contain numbers"
                                        " and cannot have more than one underscore consecutively.")
                return

            #forbid forbidden words
            for word in ForbiddenDatasetNames:
                if len(datasetName) >= len(word):
                    if datasetName[:len(word)] == word:
                        QMessageBox.information(self,"Error","Dataset name cannot be \"" + word + "\". This word is reserved.")
                        return

            for i in range(self.datasetsTabs.count()):
                self.tmpTabName = self.datasetsTabs.tabText(i)
                if datasetName == self.tmpTabName:
                    QMessageBox.information(self,"Error","A dataset with name " + datasetName + " already exists. "
                                                         "Please choose a different name.")
                    return
            self.addDatasetWithName(datasetName,False,False)

        if self.acqTypeOptions[self.acquisitionTypeLine.currentIndex()] == AcquisitionTypeOption_Fake:
            self.acquisitionTypeChanged(self.acquisitionTypeLine.currentIndex())

    def addDatasetWithName(self,datasetName,isLocked,isvaluelocked):
        for i in range(self.datasetsTabs.count()):
            tabName = self.datasetsTabs.tabText(i)
            if datasetName == tabName:
                #if dataset already exists, just return
                return False
        self.listOfDatasets[datasetName] = DatasetForm(datasetName, parent=self)
        self.listOfDatasets[datasetName].isLocked      = isLocked
        self.listOfDatasets[datasetName].isValueLocked = isvaluelocked
        self.datasetsTabs.addTab(self.listOfDatasets[datasetName],datasetName)
        return True

    def refreshDevices(self):
        self.devicesNames = []
        try:
            #remove all currently listed device
            while self.portLine.count() > 0:
                self.portLine.removeItem(0)

            self.devicesNames = get_serial_ports()
            # if no seerial devices found
            if len(self.devicesNames) == 0:
                self.portLine.addItem(NoDevicesString)
            else:
                self.portLine.addItems(self.devicesNames)

            self.dealWithNoDevicesFound()

        except Exception as e:
            self.portLine.setDisabled(1)
            self.portLine.addItem(NoDevicesString)
            QMessageBox.information(self,"Error","Error while trying to find serial devices. Make sure you have devices connected. Exception message: " + str(e))

    def dealWithNoDevicesFound(self):
        '''
        Decides whether the devices combobox has to be disabled
        :return: None
        '''
        if len(self.devicesNames) == 0:
            self.portLine.setDisabled(1)
        else:
            self.portLine.setDisabled(0)

    def removeDataset(self):
        if self.datasetsTabs.count() > 0:
            items = []
            itemsDic = {}
            for i in range(self.datasetsTabs.count()):
                tabName = self.datasetsTabs.tabText(i)
                items.append(tabName)
                itemsDic[tabName] = i
            self.datasetReturn = QInputDialog.getItem(self,"Dataset name?","Choose dataset to remove",items,self.datasetsTabs.currentIndex(),False)
            self.datasetName   = self.datasetReturn[0]
            self.datasetChosen = self.datasetReturn[1]
            if self.datasetChosen:
                if not self.datasetsTabs.widget(itemsDic[self.datasetName]).isLocked:
                    self.datasetsTabs.removeTab(itemsDic[self.datasetName])
                else:
                    QMessageBox.information(self,"Error","This dataset is locked. You cannot remove it, as data will then not comply to the standard of GNOME.")
        else:
            QMessageBox.information(self,"Error","You can't ask to remove datasets when no datasets are present")


    def closeEvent(self, event):
        while self.datasetsTabs.count():
            self.datasetsTabs.removeTab(0)

        while self.mainLayout.count():
            item = self.mainLayout.takeAt(0)
            widget = item.widget()
            if widget:
                try:
                    widget.close()
                except:
                    pass

    def healthyWait(self,totalWait):
        self._waitTime = 0
        self._waitStep = 0.1
        if totalWait < self._waitStep:
            time.sleep(totalWait)
        else:
            while self._waitTime < totalWait:
                time.sleep(self._waitStep)
                self._waitTime += self._waitStep
                QCoreApplication.processEvents()

    def startAcquisitionButtonAction(self):
        for i in range(self.datasetsTabs.count()):
            tabName = self.datasetsTabs.tabText(i)
            if re.match(dataset_regex, tabName) is None:
                QMessageBox.information(self, "Error",
                                        "Dataset name \"" + tabName +  "\" is invalid. It should start with letters, "
                                        "and can contain numbers"
                                        " and cannot have more than one underscore consecutively.")
                return

        QCoreApplication.processEvents()
        if self.acquisitionRunning:
            #lock acquisition start button
            self.startAcquisitionButton.setDisabled(1)
            QCoreApplication.processEvents()
            self.doStopAcquisition()
            QCoreApplication.processEvents()

            #unlock acquisition start button
            #the unlock will be done by the thread

        else:
            if self.isDataPathValid():
                self.startAcquisitionButton.setDisabled(1)
                QCoreApplication.processEvents()
                self.doStartAcquisition()
                QCoreApplication.processEvents()
                QCoreApplication.processEvents()
            else:
                QMessageBox.information(self,"Error","Error: The data path is either invalid or non-writable. Please select a directory you selected is valid and where you can write.")

    def doStopAcquisition(self):
        self.acquisitionRunning = False
        self.startAcquisitionButton.setText(self.startAcqText)
        self.addDatasetButton.setDisabled(0)
        self.portLine.setDisabled(0)
        self.refreshDevicesButton.setDisabled(0)
        self.removeDatasetButton.setDisabled(0)
        for i in range(self.datasetsTabs.count()):
            # self.datasetsTabs.widget(i).setDisabled(0)
            self.datasetsTabs.widget(i).disableControls(False)
        self.acquisitionTypeLine.setDisabled(0)
        self.dumpAcquiredStringsToFileCheckbox.setDisabled(0)
        self.paranoidModeCheckbox.setDisabled(0)
        self.stationNameLine.setDisabled(0)
        self.dataPathLine.setDisabled(0)
        self.stopAcquisitionSignal.emit()
        self.dataPathBrowseButton.setDisabled(0)
        self.dealWithNoDevicesFound()

    def doStartAcquisition(self):
        self.acquisitionRunning = True
        self.startAcquisitionButton.setText(self.stopAcqText)
        self.addDatasetButton.setDisabled(1)
        self.portLine.setDisabled(1)
        self.refreshDevicesButton.setDisabled(1)
        self.removeDatasetButton.setDisabled(1)
        for i in range(self.datasetsTabs.count()):
            # self.datasetsTabs.widget(i).setDisabled(1)
            self.datasetsTabs.widget(i).disableControls(True)
        self.acquisitionTypeLine.setDisabled(1)
        self.dumpAcquiredStringsToFileCheckbox.setDisabled(1)
        self.paranoidModeCheckbox.setDisabled(1)
        self.stationNameLine.setDisabled(1)
        self.dataPathLine.setDisabled(1)
        self.dataPathBrowseButton.setDisabled(1)

        self.acquisitionCall()

    def getAttributesFromGUI(self):
        attrsContainer = {}
        for i in range(self.datasetsTabs.count()):
            ds_name = self.datasetsTabs.tabText(i)
            num_rows = self.datasetsTabs.widget(i).attribsTable.rowCount()
            for j in range(num_rows):
                if not (self.datasetsTabs.tabText(i) in attrsContainer):
                    attrsContainer[self.datasetsTabs.tabText(i)] = {}

                name  = self.datasetsTabs.widget(i).attribsTable.item(j, self.datasetsTabs.widget(i).AttributesColumns[Attribute_NameKey]).text()
                type  = self.datasetsTabs.widget(i).attribsTable.item(j, self.datasetsTabs.widget(i).AttributesColumns[Attribute_TypeKey]).text()
                value = self.datasetsTabs.widget(i).attribsTable.item(j, self.datasetsTabs.widget(i).AttributesColumns[Attribute_ValueKey]).text()
                attrsContainer[self.datasetsTabs.tabText(i)].update(
                    {
                        name: {Attribute_NameKey:  name,
                               Attribute_ValueKey: value,
                               Attribute_TypeKey:  type}
                    })

            # this older version takes values not from the GUI, but from the table stored, attributesList

            # for attName in sorted(self.datasetsTabs.widget(i).attributesList):
            #     # if dict doesn't exist for this dataset, create it!
            #     if not (self.datasetsTabs.tabText(i) in attrsContainer):
            #         attrsContainer[self.datasetsTabs.tabText(i)] = {}
            #
            #     # append attribute to dict of attributes
            #     attrsContainer[self.datasetsTabs.tabText(i)].update(
            #         {
            #             attName: {Attribute_NameKey:  attName,
            #                       Attribute_ValueKey: self.datasetsTabs.widget(i).attributesList[attName].Value,
            #                       Attribute_TypeKey:  self.datasetsTabs.widget(i).attributesList[attName].Type}
            #         })

        return attrsContainer


    def updateAttributesDuringAcquisition(self):
        """
        This function updates the attributes from the DatasetForms to a container that is passed to the object
        that writes the files
        :return:
        """
        self.dataCollected.acqConfig.attributes = self.getAttributesFromGUI()

    def acquisitionCall(self):
        self.acqConfig = AcquisitionConfig()
        self.acqConfig.registerDevice(self)
        self.acqConfig.dataPath = self.dataPathLine.text()
        self.acqConfig.stationName = self.stationNameLine.text()
        self.acqConfig.logFilePath = os.path.join(self.acqConfig.dataPath, logDirName,
                                        logFileNamePrefix +
                                        datetime.datetime.utcnow().strftime(logDateTimeFormat) +
                                        logFileNameSuffix)
        self.logFilePath = self.acqConfig.logFilePath
        self.acqConfig.attributes = self.getAttributesFromGUI()

        #initialize local data queues, for the data that will be received from the device
        self.dataCollected = DataCollected(self.acqConfig)

        self.acqConfig.registerChannels(self)
        if self.acqConfig.errorFlag:
            QMessageBox.information(self,"Error",self.acqConfig.errorMessage)
            self.doStopAcquisition()
            self.reenableStartButton()
            return

        self.acqConfig.isFakeAcquisition   = (self.acqTypeOptions[self.acquisitionTypeLine.currentIndex()] == AcquisitionTypeOption_Fake)
        self.acqConfig.isFileAcquisition   = (self.acqTypeOptions[self.acquisitionTypeLine.currentIndex()] == AcquisitionTypeOption_File)
        self.acqConfig.doDumpStringsToFile = self.dumpAcquiredStringsToFileCheckbox.isChecked()
        self.acqConfig.paranoidMode        = self.paranoidModeCheckbox.isChecked()
        self.acqConfig.fileAcqPath         = self.acquisitionFromFilesPath
        self.dataAnalysisWidget.initPlots(self.datasetsTabs.count()+1)

        if (not self.acqConfig.isFileAcquisition) and (not self.acqConfig.isFakeAcquisition):
            if self.portLine.currentText() == NoDevicesString:
                QMessageBox.information(self, "Error",
                                        "A valid device is not selected. "
                                        "Please select a valid device before starting acquisition")
                self.doStopAcquisition()
                self.reenableStartButton()
                return

        self.acquirer = DataAcquirer(self.acqConfig)
        self.stopAcquisitionSignal.connect(self.acquirer.stopAcquisition)
        self.acquirer.reenableStartButtonSignal.connect(self.reenableStartButton)
        self.acquirer.finishedSignal.connect(self.reenableStartButton)
        self.acquirer.postErrorMessage.connect(self.acquisitionThreadError)
        self.acquirer.postResultsSignal.connect(self.processDataFromThreadSlot)
        self.acquirer.postNumMissingBatches.connect(self.addMissingBatches)
        castingReturn = self.testAttributesCasting()

        if castingReturn:
            self.saveSettingsToFile(ConfigFileName)
            # self.acquirer.start()
            self.acquirer.run()
        else:
            self.doStopAcquisition()
            self.reenableStartButton()

        return

    def getMagneticFieldEquationString(self):
        attribs = self.getAttributesFromGUI()
        return attribs[defaultDatasetName][defaultMagFieldEqAttrName][Attribute_ValueKey]

    def getDatasetsList(self):
        listOfDS = []
        keysList = self.acqConfig.requestedChannelsTypes.keys()
        for key in keysList:
            listOfDS.append(key)
        return listOfDS

    def testAttribValues(self, attrib_name, attr_val):
        if attrib_name == sensorTypeAttrName:
            if not (attr_val == "VectorMag" or attr_val == "ScalarMag" or attr_val == "Other"):
                raise ValueError("The value of " + sensorDirAltitudeAttrName + " can be one of these (case sensitive): "
                                                                               "\"VectorMag\", \"ScalarMag\" or \"Other\"")
        if attrib_name == sensorDirAzimuthAttrName:
            if attr_val < 0 or attr_val >= 360:
                raise ValueError("The value of " + sensorDirAltitudeAttrName + " should be in the range [0,360)")
        if attrib_name == sensorDirAltitudeAttrName:
            if attr_val < -90 or attr_val > 90:
                raise ValueError("The value of " + sensorDirAltitudeAttrName + " should be in the range [-90,90]")

    def testAttributesCasting(self):
        print("Testing attribute casting...")
        attribs = self.getAttributesFromGUI()
        print("Attributes received: ", attribs)
        tmpPath = copy.deepcopy(self.dataPathLine.text())
        tmpPath = os.path.join(tmpPath, "test.h5")
        self.h5fObj = h5py.File(tmpPath, "w")
        for i in range(self.datasetsTabs.count()):
            ds_name = self.datasetsTabs.tabText(i)
            self.tmpDataset = self.h5fObj.create_dataset(ds_name, data=[np.int32(1)])
            print("Dataset name: " + str(self.tmpDataset.name))
            for attName in sorted(attribs[ds_name]):
                if re.match(attrib_regex, attName) is None:
                    QMessageBox.information(self, "Error",
                                            "Attribute name \"" + attName + "\" in dataset " + ds_name +
                                            " is invalid. It should start with letters, and can contain numbers"
                                            " and cannot have more than one underscore consecutively.")
                    self.h5fObj.close()
                    return False

                try:
                    self.tmpDataset.attrs[attName] = \
                    ApplyAttributeType(ApplyAttributeReplacement_tester(attribs[ds_name][attName]["Value"]),
                                       attribs[ds_name][attName]["Type"])
                except Exception as e:
                    QMessageBox.information(self, "Error", "Error while trying to cast the parameter " + attName +
                                            " in dataset " + ds_name + " to type " +
                                            attribs[ds_name][attName]["Type"] + ". "
                                            "Make sure that the type you chose for this variable is compatible "
                                                                    "with the its contents. The contents "
                    "are: " + ApplyAttributeReplacement_tester(str(attribs[ds_name][attName]["Value"])) + "\n"
                    "Exception says: " + str(e))
                    self.h5fObj.close()
                    try:
                        os.remove(tmpPath)
                    except: pass
                    return False

                try:
                    self.tmpDataset.attrs[attName] = \
                    ApplyAttributeType(ApplyAttributeReplacement_tester(attribs[ds_name][attName]["Value"]),
                                       attribs[ds_name][attName]["Type"])
                    self.testAttribValues(attName, self.tmpDataset.attrs[attName])
                except Exception as e:
                    QMessageBox.information(self, "Error", "Error while testing parameter " + attName +
                                            " in dataset " + ds_name + ". " + str(e))
                    self.h5fObj.close()
                    try:
                        os.remove(tmpPath)
                    except: pass
                    return False

        print("Attributes casting tests successful!")
        self.h5fObj.close()
        try:
            os.remove(tmpPath)
        except: pass

        # parse magnetic field equation and test it

        def attr_getter(attname: str) -> str:
            # in case of failure, this value stores the last known value
            parts = attname.split("/")
            if len(parts) == 1:
                raise SyntaxError("Error: Magnetic field equation given with a global attribute. "
                                  "This is not supported in this software!")

            elif len(parts) == 2:
                for i in range(self.datasetsTabs.count()):
                    print(self.datasetsTabs.tabText(i), parts[0])
                    if self.datasetsTabs.tabText(i) == parts[0]:
                        val = attribs[self.datasetsTabs.tabText(i)][parts[1]]["Value"]
                        val = ApplyAttributeReplacement_tester(val)
                        return val

            else:
                raise SyntaxError("Error: Attributes should be given in the form: ${dataset/attr}")

        try:
            magFieldEquationStr = self.getMagneticFieldEquationString()

            eq_info = gd.parse_equation(magFieldEquationStr)
            print(eq_info)
            if not eq_info["success"]:
                raise SyntaxError(eq_info["msg"])
            magFieldEquationStr = eq_info["equation"]

            datasetsVarReps = {}
            attrsVarReps = {}
            listOfDatasets = self.getDatasetsList()
            if eq_info["datasets_indices"] != eq_info["datasets"]:
                raise SyntaxError("All datasets in this software are one dimensional. "
                                  "You can't use deindexing operators, such as dataset[[i]].")

            for ds in eq_info["datasets"]:
                if ds not in listOfDatasets:
                    raise SyntaxError("Your equation contains the dataset " + ds + ", which doesn't seem to be within "
                                      "the datasets you have in this acquisition.")

            for key in listOfDatasets:
                datasetsVarReps[key] = float(np.random.rand())
            for attr in eq_info["attrs"]:
                val = attr_getter(attr)
                if val is None:
                    raise SyntaxError("Unable to substitute attribute " + attr + ". Are you sure it exists?")
                else:
                    attrsVarReps[attr] = val

            # recursive replacement of attributes
            prev_eq = magFieldEquationStr
            while True:
                for attr in attrsVarReps:
                    magFieldEquationStr = magFieldEquationStr.replace("${"+attr+"}", attrsVarReps[attr])

                if magFieldEquationStr == prev_eq:
                    break
                else:
                    prev_eq = magFieldEquationStr
            expression  = sympy.S(magFieldEquationStr)
            all_symbols = [str(x) for x in expression.atoms(sympy.Symbol)]
            if not set(all_symbols).issubset(listOfDatasets):
                QMessageBox.information(self, "Magetic field equation variables error",
                                              "The magnetic field equation provided: \"" + magFieldEquationStr + "\" must have only dataset names as variables.\n"
                                              "This is because the magnetic field is supposed to be generated from data points from recorded datasets.")
                return False

            np.double(expression.subs(datasetsVarReps))

        except Exception as e:
            QMessageBox.information(self,"Magnetic field equation parsing error",
                                        "Error while parsing the magnetic field equation provided. \n"
                                        "Please make sure the equation provided complies to sympy standards. Exception says: " + str(e))
            print("Magnetic field equation parsing error","Error while parsing the magnetic field equation provided. \n"
                                        "Please make sure the equation provided complies to sympy standards. Exception says: " + str(e))
            return False

        return True

    #saves settings to config file
    def saveSettingsToFile(self, filename):
        self.configFileObj = None
        try:
            print("Saving config file: " + filename)
            self.configFileObj = h5py.File(filename,"w")
            self.configFileObj.attrs[ConfigOptionName_DataPath]    = self.dataPathLine.text()
            self.configFileObj.attrs[ConfigOptionName_StationName] = self.stationNameLine.text()
            self.configFileObj.attrs[ConfigOptionName_PortName] = self.portLine.currentText()

            for i in range(self.datasetsTabs.count()):
                self.tmpDataset = self.configFileObj.create_dataset(self.datasetsTabs.tabText(i),data=[np.int32(1)])
                counter = 0
                for attName in sorted(self.datasetsTabs.widget(i).attributesList):
                    #only attributes that are not locked are saved
                    if not self.datasetsTabs.widget(i).attributesList[attName].isValueLocked:
                        # print(attName)
                        # print(self.datasetsTabs.widget(i).attributesList[attName].Type)
                        # print(self.datasetsTabs.widget(i).attributesList[attName].Value)
                        print(self.datasetsTabs.widget(i).attributesList[attName].asDict())
                        self.tmpDataset.attrs[ConfigAttribute_Prefix+str(counter)+ConfigAttribute_NameSuffix]  = self.datasetsTabs.widget(i).attributesList[attName].Name
                        self.tmpDataset.attrs[ConfigAttribute_Prefix+str(counter)+ConfigAttribute_ValueSuffix] = self.datasetsTabs.widget(i).attributesList[attName].Value
                        self.tmpDataset.attrs[ConfigAttribute_Prefix+str(counter)+ConfigAttribute_TypeSuffix]  = self.datasetsTabs.widget(i).attributesList[attName].Type
                        self.tmpDataset.attrs[ConfigAttribute_Prefix+str(counter)+ConfigAttribute_ValueLockedSuffix]  = self.datasetsTabs.widget(i).attributesList[attName].isValueLocked
                        self.tmpDataset.attrs[ConfigAttribute_Prefix+str(counter)+ConfigAttribute_LockedSuffix] = self.datasetsTabs.widget(i).attributesList[attName].isLocked
                        counter += 1

                self.tmpDataset.attrs[ConfigOption_Prefix+ConfigOptionName_SelectedChannel]    = self.datasetsTabs.widget(i).channelLine.currentText()
                self.tmpDataset.attrs[ConfigOption_Prefix+ConfigOptionName_ChannelDatatype]    = self.datasetsTabs.widget(i).channelDatatypeLine.currentText()
                # self.tmpDataset.attrs[ConfigOption_Prefix+ConfigOptionName_ChConversionFactor] = self.datasetsTabs.widget(i).channelConversionFactorLine.text()
                # self.tmpDataset.attrs[ConfigOption_Prefix+ConfigOptionName_ChOffset]           = self.datasetsTabs.widget(i).channelOffsetLine.text()

            self.configFileObj.close()
            print("Done saving config file.")
        except Exception as e:
            print("Error: An exception was thrown while trying to save your settings. Do you have sufficient write permissions in your program directory? Exception says: " + str(e))
            if not (self.configFileObj is None):
                self.configFileObj.close()

    def loadSettingsFromFile(self,filename):
        print("")
        print("Loading settings file...")
        try:
            self.configFileObj = h5py.File(filename,"r")
        except Exception as e:
            print("Warning: An exception was thrown while trying to load your settings. This probably is OK if you have not saved any settings before. Exception says: " + str(e))
            return
        try:
            self.dataPathLine.setText(self.configFileObj.attrs[ConfigOptionName_DataPath])
        except Exception as e:
            print("Unable to set data path from configuration file. Exception was thrown. Exception says: " + str(e))
        try:
            self.stationNameLine.setText(self.configFileObj.attrs[ConfigOptionName_StationName])
        except Exception as e:
            print("Unable to set station name from configuration file. Exception was thrown. Exception says: " + str(e))
        try:
            index = self.portLine.findText(self.configFileObj.attrs[ConfigOptionName_PortName], QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.portLine.setCurrentIndex(index)
        except Exception as e:
            print("Unable to set selected device from configuration file. Exception was thrown. Exception says: " + str(e))

        datasetsToLoad = list(self.configFileObj.keys())

        print("Datasets to load: " + str(datasetsToLoad))

        #configuration is stored as datasets
        for datasetName in datasetsToLoad:
            print("")
            print("Loading dataset: " + datasetName)
            attributesList = []
            #read all attributes using .items()
            HDF5ConfigAttributes = list(self.configFileObj[datasetName].attrs.items())
            print(HDF5ConfigAttributes)

            #count available attributes
            #the function simply uses the maximum number of attributes available, as every attribute has a number
            #the numbers start from zero and end at n-1, therefore we start from -1 and then add 1 at the end
            self.tmpAttribCount = -1
            for attr in HDF5ConfigAttributes:
                try:
                    if attr[0][-len(ConfigAttribute_NameSuffix):] == ConfigAttribute_NameSuffix:
                        if attr[0][:len(ConfigAttribute_Prefix)] == ConfigAttribute_Prefix:
                            self.tmp = int(attr[0][len(ConfigAttribute_Prefix):-len(ConfigAttribute_NameSuffix)])
                            if(self.tmp > self.tmpAttribCount):
                                self.tmpAttribCount = self.tmp
                except Exception as e:
                    print("Error while parsing the number of attributes in the config file. Exception says: " + str(e))
            self.tmpAttribCount += 1
            # DONE COUNTING ATTRIBUTES

            for i in range(self.tmpAttribCount):
                attributesList.append(Attribute("", "", "", False, False))

            # read attributes and assign them
            try:
                for attr in HDF5ConfigAttributes:
                    if attr[0][:len(ConfigAttribute_Prefix)] == ConfigAttribute_Prefix:
                        if attr[0][-len(ConfigAttribute_NameSuffix):] == ConfigAttribute_NameSuffix:
                            self.attrNum = int(attr[0][len(ConfigAttribute_Prefix):-len(ConfigAttribute_NameSuffix)])
                            attributesList[self.attrNum].Name = attr[1]
                        elif attr[0][-len(ConfigAttribute_ValueSuffix):] == ConfigAttribute_ValueSuffix:
                            self.attrNum = int(attr[0][len(ConfigAttribute_Prefix):-len(ConfigAttribute_ValueSuffix)])
                            attributesList[self.attrNum].Value = attr[1]
                        elif attr[0][-len(ConfigAttribute_TypeSuffix):] == ConfigAttribute_TypeSuffix:
                            self.attrNum = int(attr[0][len(ConfigAttribute_Prefix):-len(ConfigAttribute_TypeSuffix)])
                            attributesList[self.attrNum].Type = attr[1]
                        elif attr[0][-len(ConfigAttribute_LockedSuffix):] == ConfigAttribute_LockedSuffix:
                            self.attrNum = int(attr[0][len(ConfigAttribute_Prefix):-len(ConfigAttribute_LockedSuffix)])
                            attributesList[self.attrNum].isLocked = attr[1]
                        elif attr[0][-len(ConfigAttribute_ValueLockedSuffix):] == ConfigAttribute_ValueLockedSuffix:
                            self.attrNum = int(attr[0][len(ConfigAttribute_Prefix):-len(ConfigAttribute_ValueLockedSuffix)])
                            attributesList[self.attrNum].isValueLocked = attr[1]

            except Exception as e:
                print("Error while trying to parse data from the configuration file. Exception says: " + str(e))

            print("Loaded attributes list:")
            print("Number of attributes in dataset \"" + datasetName + "\" is: " + str(len(attributesList)))
            [attributesList[i].print() for i in range(len(attributesList))]

            # add dataset and attributes

            #find dataset number within the tabs by name
            if not self.addDatasetWithName(datasetName,False,False):
                print("Unable to add dataset " + datasetName + ". It probably already exists.")


            #find the number of the dataset in the tabs
            self.tmpDatasetNumber = -1
            for j in range(self.datasetsTabs.count()):
                if self.datasetsTabs.tabText(j) == datasetName:
                    self.tmpDatasetNumber = j
                    break


            #if dataset was not found
            if self.tmpDatasetNumber == -1:
                print("Error when trying to read config file. Tab cannot be found after being added or after being found existant already.")
                self.configFileObj.close()
                return

            #add attributes to the list
            # (remember that value locked attributes are not saved, and new value locked attributes are ignored)
            for i in range(len(attributesList)):
                #if the attribute already exists and is locked, just ignore it
                #locked attributes are not supposed to be loaded from the config file
                #this helps in case the status of some attribute was changed from normal to value locked
                try:
                    if self.datasetsTabs.widget(self.tmpDatasetNumber).attributeExists(attributesList[i].Name):
                        if self.datasetsTabs.widget(self.tmpDatasetNumber).attributeValueLocked(attributesList[i].Name):
                            print("Ignoring attribute from config file: " + attributesList[i].Name + ", in dataset: " + datasetName + ", since it is locked.")
                            print(attributesList[i].asDict())
                            continue
                except Exception as e:
                    print("Error while trying to check whether the attribute " + attributesList[i].Name + " Exception says: " + str(e))

                self.datasetsTabs.widget(self.tmpDatasetNumber).addAttribFunc_fixed(attributesList[i], True)

            #load options of the dataset dialog
            for attr in HDF5ConfigAttributes:
                #if the prefix of the attribute in the config file indicates that it's an option
                if attr[0][:len(ConfigOption_Prefix)] == ConfigOption_Prefix:
                    try:
                        if attr[0][-len(ConfigOptionName_SelectedChannel):] == ConfigOptionName_SelectedChannel:
                            index = self.datasetsTabs.widget(self.tmpDatasetNumber).channelLine.findText(attr[1], QtCore.Qt.MatchFixedString)
                            if index >= 0:
                                self.datasetsTabs.widget(self.tmpDatasetNumber).channelLine.setCurrentIndex(index)
                        if attr[0][-len(ConfigOptionName_ChannelDatatype):] == ConfigOptionName_ChannelDatatype:
                            index = self.datasetsTabs.widget(self.tmpDatasetNumber).channelDatatypeLine.findText(attr[1], QtCore.Qt.MatchFixedString)
                            if index >= 0:
                                self.datasetsTabs.widget(self.tmpDatasetNumber).channelDatatypeLine.setCurrentIndex(index)


                    except Exception as e:
                        print("Error while parsing dataset options from config file. Exception says: " + str(e))


        try:
            self.configFileObj.close()
        except:
            print("Error: Could not close the config file. Exception says: " + str(e))


        print("Done loading settings file...")

    def acquisitionThreadError(self, message):
        QMessageBox.information(self,"Error",message)
        self.doStopAcquisition()
        # self.acquirer.wait()

    def createMagneticFieldsList(self, dataToSave, dataCollected):
        def dataset_getter(dsname):
            return dataToSave[dsname]

        def attr_getter(attname: str) -> str:
            parts = attname.split("/")
            if len(parts) == 1:
                raise SyntaxError("Error: Magnetic field equation given with a global attribute. "
                                  "This is not supported in this software!")

            elif len(parts) == 2:
                for i in range(self.datasetsTabs.count()):
                    if self.datasetsTabs.tabText(i) == parts[0]:
                        val = self.datasetsTabs.widget(i).attributesList[parts[1]].Value
                        # check if this is an attribute to be read from data,
                        if re.match(r"([%][A-Z]+[%])", val) is not None:
                            try:
                                val = ApplyAttributeReplacement(val, dataCollected, self.acqConfig, parts[0])
                                self.lastAttrs[attname] = val
                            except Exception as e:
                                print("Error while doing attribute replacement; using the last known value. "
                                      "(this error is expected to happen once for every file write). "
                                      "Error says: " + str(e))
                                try:
                                    val = self.lastAttrs[attname]
                                except Exception as e:
                                    print("Failure in using last value. Replacing by value 1.")
                                    val = re.sub(r"([%][A-Z]+[%])", "1", val)
                        return val

            else:
                print("Error: Attributes should be given in the form: ${dataset/attr}")


        equationString = self.getMagneticFieldEquationString()
        # parsed_eq = gd.parse_main_equation(equationString)
        # units = parsed_eq["units"]
        #index of the dictionary
        units = ""
        dictIndex = "Calculated\nMagnetic\nFields " + (units if units != "[]" else "")
        magFieldsArray = gd.eval_equation(equationString,
                                          attr_getter=attr_getter,
                                          dataset_getter=dataset_getter)
        return {dictIndex: magFieldsArray}

    def processDataFromThreadSlot(self,data,dataCollected):

        self.processDataFromThread(data,dataCollected)
        QCoreApplication.processEvents()

    def processDataFromThread(self,data,dataCollected):
        # Append data to data queue
        # self.dataCollected[data.deviceName].appendData(data)

        if not self.plotLocked:
            self.plotLocked = True

            # print("Points saved: " + str(self.dataCollected[data.deviceName].length()))

            # add the calculated magnetic fields to dataToPlot
            dataToPlot = data.dataToSave.copy()
            magFieldsListDict = self.createMagneticFieldsList(data.dataToSave,dataCollected)
            dataToPlot.update(magFieldsListDict)

            # self.dataAnalysisWidget.appendData(dataToPlot, data.startTime, data.samplingRate)
            self.dataAnalysisWidget.setData(dataToPlot, data.startTime, data.samplingRate)

            # Skip plotting if very often
            # The following is for the first plot, where times are None still
            if self.plot_before_time is None or self.plot_after_time is None:
                self.plot_before_time = datetime.datetime.utcnow()
                self.dataAnalysisWidget.doPlotData()
                self.plot_after_time = datetime.datetime.utcnow()

            else:
                # Here plotting should not happen more than once per second,
                # and also not so often that it's N times faster than the time
                # it takes to process data
                time_since_last_plot = (datetime.datetime.utcnow() - self.plot_after_time).total_seconds()
                if time_since_last_plot >= 4*np.average(self.plot_average_time_window) and \
                   time_since_last_plot >= 1:
                    self.plot_before_time = datetime.datetime.utcnow()
                    self.dataAnalysisWidget.doPlotData()
                    self.plot_after_time = datetime.datetime.utcnow()

            self.plot_average_time_window.append((self.plot_after_time - self.plot_before_time).total_seconds())

            self.plotLocked = False



    #enable start button after the thread has started successfully
    def reenableStartButton(self):
        self.startAcquisitionButton.setDisabled(0)

    def acquisitionTypeChanged(self,index):
        if self.acqTypeOptions[index] == AcquisitionTypeOption_Fake:
            # self.addDatasetButton.setDisabled(True)
            self.refreshDevicesButton.setDisabled(True)
            self.portLine.clear()
            self.portLine.addItem("FakeDevice")
            self.portLine.setDisabled(True)

        elif self.acqTypeOptions[index] == AcquisitionTypeOption_COM:
            # self.addDatasetButton.setDisabled(False)
            self.refreshDevicesButton.setDisabled(False)
            self.refreshDevices()

        else:
            self.addDatasetButton.setDisabled(False)
            QMessageBox.information(self,"Information","Acquisition from files entails reading the files "
            "of the SD Card of the acquisition box and parsing them. Please select the directory where these "
            "files are located. It is highly recommended that you copy these files to your computer and not do "
            "the acquisition from the SD Card directly. The directory must be writable too, so that finished "
            "files are moved to a separate folder.")

            self.acquisitionFromFilesPath = QFileDialog.getExistingDirectory(
                self, "Open Directory", self.acquisitionFromFilesPath, QFileDialog.ShowDirsOnly)
            if self.acquisitionFromFilesPath != "":
                self.refreshDevicesButton.setDisabled(True)
                self.portLine.clear()
                self.portLine.addItem("FromFiles")
                self.portLine.setDisabled(True)
            else:
                self.acquisitionTypeLine.setCurrentIndex(0)

    #what to do when forcing window to close
    def closeEvent(self,event):
        #clean up
        #if thread is created, check that it's stopped
        self.viewLogWidget.close()
        if self.acquirer is not None:
            self.stopAcquisitionSignal.emit()
            waitDialog = QProgressDialog()
            waitDialog.setWindowFlags(Qt.FramelessWindowHint)
            progressBar = QProgressBar()
            cancelButton = QPushButton("")
            waitDialog.setBar(progressBar)
            waitDialog.setCancelButton(cancelButton)
            cancelButton.setVisible(0)
            progressBar.setVisible(0)
            waitDialog.setLabelText("Please wait while the acquisition thread closes... This should not take more than 20 seconds.")
            waitDialog.setMinimum(0)
            waitDialog.setMaximum(0)
            # waitDialog.setValue(0)
            windowIcon = QIcon(os.path.join(ScriptPath, "icon.png"))
            waitDialog.setWindowIcon(windowIcon)
            waitDialog.show()
            QCoreApplication.processEvents()
            self.stopAcquisitionSignal.emit()
            QCoreApplication.processEvents()
            #wait for acquisition thread to "die"
            #no need for this as the thread is a daemon
            # self.acquirer.waitForAcquisitionThread()
            QCoreApplication.processEvents()
            # waitDialog.setValue(100)
            QCoreApplication.processEvents()
            waitDialog.close()

    def cleanUp(self):
        # Clean up everything
        for i in self.__dict__:
            item = self.__dict__[i]
            clean(item)


def GetSoftwareInfo():
    versions = {}
    for name, module in sorted(sys.modules.items()):
        if hasattr(module, '__version__'):
            versions[name] = module.__version__
    return versions

def PrintSoftwareInfo():
    print("Starting GNOME Acquirer v" + SOFTWARE_VERSION + "...")
    print("Imported modules: ")
    print(GetSoftwareInfo())
