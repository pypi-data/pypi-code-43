from GNOMEAcquirerLibs.Dataset import *


# This class is made to concatenate data from DataBatch
class AcquisitionConfig():
    def __init__(self):
        self.requestedDevice = None
        self.requestedChannels = {}
        self.requestedChannelsTypes = {}
        # self.conversionFactors = {}
        # self.chOffsets = {}
        self.isFakeAcquisition = False

        self.isFileAcquisition = False
        self.fileAcqPath       = None

        self.errorFlag = False
        self.errorMessage = ""

        self.dataPath = ""
        self.stationName = ""
        self.attributes = {}
        self.paranoidMode = False

    #set device to be used
    def registerDevice(self,acquisitionWindow):
        self.requestedDevice = acquisitionWindow.portLine.currentText()

    def registerChannels(self,acquisitionWindow):
        self.requestedChannels = {}
        self.requestedChannelsTypes = {}

        for tabNum in range(0,acquisitionWindow.datasetsTabs.count()):
            #get channel numbers
            tmpChNum = int(acquisitionWindow.datasetsTabs.widget(tabNum).channelLine.currentText())
            tmpChType = acquisitionWindow.datasetsTabs.widget(tabNum).channelDatatypeLine.currentText()
            if tmpChNum in self.requestedChannels.values():
                self.errorFlag = True
                self.errorMessage = "Error: You cannot request the same channel for two datasets"
                return
            self.requestedChannels[acquisitionWindow.datasetsTabs.tabText(tabNum)] = tmpChNum
            self.requestedChannelsTypes[acquisitionWindow.datasetsTabs.tabText(tabNum)] = tmpChType
