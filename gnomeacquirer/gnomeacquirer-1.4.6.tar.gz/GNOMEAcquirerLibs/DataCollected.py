import copy
import os
import datetime
import numpy as np
import h5py
import sys
from GNOMEAcquirerLibs.Dataset import *
from GNOMEAcquirerLibs.AttributeData import *
from GNOMEAcquirerLibs.DataBatch import *
from GNOMEAcquirerLibs.Meta import *

def CreateDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

BatchesToStoredInSingleFile = 60

CorruptDataSubfolder = "CorruptData"

logDateTimeFormat = "%Y-%m-%d_%H-%M-%S_UTC"
logDirName        = "Logs"
logFileNamePrefix = "AcquisitionLog_"
logFileNameSuffix = ".txt"

def ApplyAttributeReplacement(attrStr,data,acqConfig,datasetName):
    attrStrReplaced = copy.deepcopy(attrStr)
    StartTime    = data.getStartTimeString()
    EndTime      = data.getEndTimeString()
    Date         = data.getDateString()
    SR           = data.getSamplingRateString()
    Weeknum      = data.getWeekNumberString()
    Longitude    = data.getLongitudeString()
    Latitude     = data.getLatitudeString()
    Altitude     = data.getAltitudeString()
    IntTemp      = data.getIntTemperatureString()
    ExtTemp      = data.getExtTemperatureString()
    ChRange      = data.getChannelRangeString(datasetName)
    MissingPoints = data.getMissingPointsString()

    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_StartTime,StartTime)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_EndTime,EndTime)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_Date,Date)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_SamplingRate,SR)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_SamplingRate_SanityChannel,"1")
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_WeekNumber,Weeknum)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_Altitude,Altitude)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_Latitude,Latitude)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_Longitude,Longitude)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_InternalTemperature,IntTemp)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_ExternalTemperature,ExtTemp)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_ChannelRange,ChRange)
    attrStrReplaced = attrStrReplaced.replace(AttributeKeyword_MissingPoints,MissingPoints)

    return attrStrReplaced

# This class is made to concatenate data from DataBatch. It contains the mechanism to concatenate data batches together
# to create a dataset. The most important function here is DataCollected.appendData()
class DataCollected():
    BatchSecondsLength = 1
    #whether there were problems when adding data
    AppendData_ReturnSuccessKey   = "Success"
    #error message when problems exist
    AppendData_ReturnErrorMsgKey  = "ErrorMsg"
    #whether it's the last batch of a single file
    AppendData_ReturnIsLastBatchKey = "LastBatch"

    def __init__(self, acqConfig):
        self.acqConfig = acqConfig
        self.initialize()

    def setAttributes(self, attrs):
        self.acqConfig.attributes = attrs

    def initialize(self):
        self.dataArray = {}
        self.auxMagFieldSensorArray = np.array([])
        self.intTemperatureArray = np.array([])
        self.extTemperatureArray = np.array([])
        self.numOfPoints = 0
        self.missingPoints = 0
        self.samplingRate = 0
        self.startTime = None
        self.numOfBatches = 0
        self.lastAddedBatchTime = None

    def appendData(self,dataBatch):
        if len(self.dataArray) == 0:
            self.dataArray    = copy.deepcopy(dataBatch.dataToSave)
            self.auxMagFieldSensorArray = np.array(dataBatch.auxMagFieldSensorArray)
            self.magFieldSenorRange = dataBatch.magFieldSenorRange
            self.magFieldSenorUnit  = dataBatch.magFieldSenorUnit
            self.channelRangesPerName    = dataBatch.channelRangesPerName

            self.startTime    = dataBatch.startTime
            self.samplingRate = dataBatch.samplingRate
            self.numOfBatches = 1
            self.numOfPoints  = len(dataBatch.dataArray)
            self.weekNumber   = dataBatch.weekNumber
            self.latitude     = dataBatch.latitude
            self.longitude    = dataBatch.longitude
            self.altitude     = dataBatch.altitude

            self.intTemperatureArray = np.array([])
            self.extTemperatureArray = np.array([])
            self.intTemperature = dataBatch.intTemperature
            self.intTemperatureArray = np.concatenate([self.intTemperatureArray, [np.float32(dataBatch.intTemperature)] ])
            self.extTemperature = dataBatch.extTemperature
            self.extTemperatureArray = np.concatenate([self.extTemperatureArray, [np.float32(dataBatch.extTemperature)] ])

            self.errorFlag = dataBatch.errorFlag
            self.errorMsgs = dataBatch.errorMsgs

            self.lastAddedBatchTime = dataBatch.startTime

            self.checkNumberOfBatches()

            return {DataCollected.AppendData_ReturnSuccessKey  : True,
                    DataCollected.AppendData_ReturnErrorMsgKey : "",
                    DataCollected.AppendData_ReturnIsLastBatchKey: (self.numOfBatches == 0)}

        else:
            self.missingPoints += dataBatch.missingPoints
            self.numOfBatches += 1
            appendedLength = 0
            self.intTemperatureArray = np.concatenate([self.intTemperatureArray, [np.float32(dataBatch.intTemperature)] ])
            self.extTemperatureArray = np.concatenate([self.extTemperatureArray, [np.float32(dataBatch.extTemperature)] ])

            for dataset in dataBatch.dataToSave:
                self.dataArray[dataset] = np.concatenate([self.dataArray[dataset], dataBatch.dataToSave[dataset]])
                appendedLength = len(dataBatch.dataToSave[dataset])

            if len(dataBatch.auxMagFieldSensorArray) > 0:
                if len(self.auxMagFieldSensorArray) > 0:
                    self.auxMagFieldSensorArray = np.concatenate([self.auxMagFieldSensorArray,np.array(dataBatch.auxMagFieldSensorArray)])
                else:
                    self.auxMagFieldSensorArray = np.array(dataBatch.auxMagFieldSensorArray)
            self.numOfPoints += appendedLength
            self.errorFlag = self.errorFlag or dataBatch.errorFlag
            self.errorMsgs = self.errorMsgs + dataBatch.errorMsgs
            #remove duplicates
            self.errorMsgs = [dict(t) for t in set([tuple(d.items()) for d in self.errorMsgs])]

            #check for that batches are consecutive
            if not (self.lastAddedBatchTime is None):
                timeDiff = dataBatch.startTime - self.lastAddedBatchTime
                if abs(timeDiff.total_seconds()-1.0) >= 1e-6:
                    return {DataCollected.AppendData_ReturnSuccessKey: False,
                            DataCollected.AppendData_ReturnErrorMsgKey: "Error while adding batches from the received data (time of batch: " + str(self.startTime) + ". The data received is not consecutive in time.\n"
                                "The difference in time between the last two batches is: " + str(timeDiff.total_seconds()) + " seconds",
                            DataCollected.AppendData_ReturnIsLastBatchKey: (self.numOfBatches == 0)}

                else:
                    self.lastAddedBatchTime = dataBatch.startTime
                    self.checkNumberOfBatches()
                    return {DataCollected.AppendData_ReturnSuccessKey: True,
                            DataCollected.AppendData_ReturnErrorMsgKey: "",
                            DataCollected.AppendData_ReturnIsLastBatchKey: (self.numOfBatches == 0)}

    def checkNumberOfBatches(self):
        if self.numOfBatches >= BatchesToStoredInSingleFile:
            self.dumpDataToFile()
            self.clearData()

    def length(self):
        return self.numOfPoints

    def size(self):
        return self.length()

    def getLongitudeString(self):
        return str(self.longitude)

    def getLatitudeString(self):
        return str(self.latitude)

    def getAltitudeString(self):
        return str(self.altitude)

    def getStartTimeString(self):
        tmpTime = self.startTime
        return str(str(tmpTime.hour).zfill(2) + ":" + str(tmpTime.minute).zfill(2) + ":" + str(tmpTime.second).zfill(2) + "." + str(tmpTime.microsecond).zfill(6))

    def getEndTimeString(self):
        tmpTime = self.startTime
        tmpTime = tmpTime + datetime.timedelta(seconds = self.numOfBatches*DataCollected.BatchSecondsLength)
        return str(str(tmpTime.hour).zfill(2) + ":" + str(tmpTime.minute).zfill(2) + ":" + str(tmpTime.second).zfill(2) + "." + str(tmpTime.microsecond).zfill(6))

    def getDateString(self):
        return str(str(self.startTime.year).zfill(4) + "/" + str(self.startTime.month).zfill(2) + "/" + str(self.startTime.day).zfill(2))

    def getSamplingRateString(self):
        return str(self.samplingRate)

    def getWeekNumberString(self):
        return str(self.weekNumber)

    def getMissingPointsString(self):
        return str(self.missingPoints)

    def getIntTemperatureString(self):
        return str(self.intTemperature)

    def getExtTemperatureString(self):
        return str(self.extTemperature)

    def getChannelRangeString(self,datasetName):
        return str(self.channelRangesPerName[datasetName])

    def clearData(self):
        self.initialize()

    def createDayFolder(self, dataPath, startTime):
        tmpPath = copy.deepcopy(dataPath)
        tmpPath = os.path.join(tmpPath, str(startTime.year).zfill(4))
        CreateDir(tmpPath)
        tmpPath = os.path.join(tmpPath, str(startTime.month).zfill(2))
        CreateDir(tmpPath)
        tmpPath = os.path.join(tmpPath, str(startTime.day).zfill(2))
        CreateDir(tmpPath)
        print(tmpPath)

        return tmpPath

    def createCorruptDataFolder(self, dataPath):
        tmpPath = copy.deepcopy(dataPath)
        tmpPath = os.path.join(tmpPath,CorruptDataSubfolder)
        CreateDir(tmpPath)
        return tmpPath

    def dumpDataToFile(self):
        print("Dumping data to file...")
        # print(data.dataArray[1:10])
        tmpPath = self.createDayFolder(self.acqConfig.dataPath, self.startTime)
        tmpFileName = self.acqConfig.stationName + "_" + \
            str(self.startTime.year).zfill(4) + str(self.startTime.month).zfill(2) + str(self.startTime.day).zfill(2) + "_" \
          + str(self.startTime.hour).zfill(2) + str(self.startTime.minute).zfill(2) + str(self.startTime.second).zfill(2) + ".h5"

        tmpFullFilePath = os.path.join(tmpPath, tmpFileName)

        print("Opening file for write: " + tmpFileName)
        try:
            self.h5fObj = h5py.File(tmpFullFilePath, "w")
            print("File is open successfully.")
        except:
            print("File open error: " + tmpFullFilePath)
            return

        #write software version to the root of the HDF5 data file
        self.h5fObj.attrs["GNOMEAcquirer_version"] = SOFTWARE_VERSION
        self.h5fObj.attrs["LocalFileCreationTime"] = str(datetime.datetime.utcnow().strftime(logDateTimeFormat))
        self.h5fObj.attrs["DataModel"] = "MagneticField_Default"
        self.h5fObj.attrs["DefaultDataset"] = defaultDatasetName
        self.h5fObj.attrs["DefaultMainEquation"] = defaultMagFieldEqAttrName
        self.h5fObj.attrs["DefaultMainEquationVersion"] = "1.0"
        self.h5fObj.attrs["DefaultMainEquationVarName"] = "Magnetic field"


        for dsName in self.acqConfig.attributes:
            #special data analysis has to be done to the dataset of sanity to downsample it and apply thresholding
            if dsName == sanityDatasetName:
                if len(self.dataArray[dsName]) <= BatchesToStoredInSingleFile:
                    self.tmpDataset = self.h5fObj.create_dataset(dsName, data=self.dataArray[dsName],
                                                                 compression="gzip", compression_opts=9)
                else:
                    #The following downsamples the data to be minimum number of points 60, and then limits the size of the array to 60
                    downsampledDS = list((self.dataArray[dsName][::int(np.floor(len(self.dataArray[dsName]) / BatchesToStoredInSingleFile))])[:BatchesToStoredInSingleFile])
                    #threshold by the given threshold in the attributes
                    threshValue = ApplyAttributeType(self.acqConfig.attributes[dsName][SanityChannel_Attr_Thresh_name][Attribute_ValueKey],
                                                     self.acqConfig.attributes[dsName][SanityChannel_Attr_Thresh_name][Attribute_TypeKey])
                    downsampledDS = list(map(lambda x: True if x >= threshValue else False, downsampledDS))
                    #invert if required by user
                    InvCutoff = ApplyAttributeType(
                        self.acqConfig.attributes[dsName][SanityChannel_Attr_InvCutoff_name][Attribute_ValueKey],
                        self.acqConfig.attributes[dsName][SanityChannel_Attr_InvCutoff_name][Attribute_TypeKey])

                    if InvCutoff:
                        downsampledDS = list(not x for x in downsampledDS)

                    #cast to numpy array
                    downsampledDS = np.asarray(downsampledDS,dtype=bool)
                    #save to file
                    self.tmpDataset = self.h5fObj.create_dataset(dsName, data=downsampledDS,
                                                                 compression="gzip", compression_opts=9)

                # SanityChannel_Attr_Thresh_name
                # SanityChannel_Attr_Cutoff_name

            else:
                self.tmpDataset = self.h5fObj.create_dataset(dsName, data=self.dataArray[dsName],
                                                             compression="gzip", compression_opts=9)
            # print("Dataset name: " + str(self.tmpDataset.name))
            for attName in self.acqConfig.attributes[dsName]:
                # print(attName)
                # print(self.datasetsTabs.widget(i).attributesList[attName].Type)
                # print(self.datasetsTabs.widget(i).attributesList[attName].Value)
                try:
                    self.tmpDataset.attrs[attName] = \
                        ApplyAttributeType(
                                           ApplyAttributeReplacement(self.acqConfig.attributes[dsName][attName][Attribute_ValueKey],
                                                      self, self.acqConfig, dsName),
                                           self.acqConfig.attributes[dsName][attName][Attribute_TypeKey])
                except:
                    sys.stderr.write(
                        "Error while trying to cast the parameter \"" + attName + "\" from the attribute list to type " +
                        self.acqConfig.attributes[dsName][attName][Attribute_TypeKey] + ". "
                                                                                   "Make sure that the type you chose for this variable is compatible with the its contents. The contents "
                                                                                   "are: " + ApplyAttributeReplacement(
                            str(self.acqConfig.attributes[dsName][attName][Attribute_ValueKey]), self, self.acqConfig,
                            dsName) + "\n")
                    sys.stderr.flush()

        # write built-in sensor magnetic fields
        self.tmpDataset = self.h5fObj.create_dataset(OutputMagFieldSensorDataset, data=self.auxMagFieldSensorArray,
                                                     compression="gzip", compression_opts=9)
        self.tmpDataset.attrs["Units"] = self.magFieldSenorUnit
        self.tmpDataset.attrs["Range"] = self.magFieldSenorRange

        # write built-in temperature sensor values
        self.h5fObj.create_dataset(InternalTemperaturesDataset, data=self.intTemperatureArray,
                                   compression="gzip", compression_opts=9)
        self.h5fObj.create_dataset(ExternalTemperaturesDataset, data=self.extTemperatureArray,
                                   compression="gzip", compression_opts=9)

        # write errors list to the file
        errorArray = []
        for errorElement in self.errorMsgs:
            QCoreApplication.processEvents()
            errorArray.append(
                [np.str(errorElement[ERROR_IDENTIFIER_SEVERITY]), np.str(errorElement[ERROR_IDENTIFIER_MESSAGE])])
        self.tmpErrorDataset = self.h5fObj.create_dataset("Errors", data=[0],
                                                          compression="gzip", compression_opts=9)
        for i in range(len(errorArray)):
            QCoreApplication.processEvents()
            self.tmpErrorDataset.attrs[OutputPrefix_Error + str(i)] = errorArray[i][0] + ": " + errorArray[i][1]
        self.h5fObj.close()
        print("File written with no errors.")

    #dumps data to file in emergencies (in case data is corrupted)
    def dumpRemainingDataToFile(self,strQueue):
        print("Dumping remaining data to file after discovering a corruption in the data...")
        # print(data.dataArray[1:10])
        hdf5Suffix = ".h5"
        textSuffix = ".txt"
        tmpPath = self.createCorruptDataFolder(self.acqConfig.dataPath)

        #in case there's no data collected yet, don't use the date for the file name as it's unknown
        if self.numOfBatches == 0:
            tmpCurrTime = datetime.datetime.utcnow()
            tmpFileName = self.acqConfig.stationName + "_" + "UnknownDate_WrittenInUTC_" \
                + str(tmpCurrTime.year).zfill(4) + str(tmpCurrTime.month).zfill(2) + str(tmpCurrTime.day).zfill(2) + "_" \
                + str(tmpCurrTime.hour).zfill(2) + str(tmpCurrTime.minute).zfill(2) + str(tmpCurrTime.second).zfill(2)

        else:
            tmpFileName = self.acqConfig.stationName + "_" + \
                str(self.startTime.year).zfill(4) + str(self.startTime.month).zfill(2) + str(self.startTime.day).zfill(2) + "_" \
              + str(self.startTime.hour).zfill(2) + str(self.startTime.minute).zfill(2) + str(self.startTime.second).zfill(2)

        #write the queued strings that are not parsed to hdf5
        with open(os.path.join(tmpPath,tmpFileName)+textSuffix, 'w') as txtFileHandler:
            txtFileHandler.write('\n'.join(strQueue))

        #if there are no batches stored, exit and don't write the hdf5 file
        if self.numOfBatches <= 0:
            print("Batch found to be empty. Skipping...")
            return

        tmpFullFilePath = os.path.join(tmpPath, tmpFileName) + hdf5Suffix

        #fix the end time of the current set of batches


        print("Opening file for write: " + tmpFileName)
        try:
            self.h5fObj = h5py.File(tmpFullFilePath, "w")
            print("File opened for writing...")
        except Exception as e:
            print("File open error: " + tmpFullFilePath + ". Exception says: " + str(e))
        for dsName in self.acqConfig.attributes:
            #special data analysis has to be done to the dataset of sanity to downsample it and apply thresholding
            if dsName == sanityDatasetName:
                if len(self.dataArray[dsName]) <= BatchesToStoredInSingleFile:
                    self.tmpDataset = self.h5fObj.create_dataset(dsName, data=self.dataArray[dsName],
                                                                 compression="gzip", compression_opts=9)
                else:

                    #The following downsamples the data to be minimum number of points 60, and then limits the size of the array to 60
                    downsampledDS = list((self.dataArray[dsName][::int(np.floor(len(self.dataArray[dsName]) / BatchesToStoredInSingleFile))])[:BatchesToStoredInSingleFile])
                    #threshold by the given threshold in the attributes
                    threshValue = ApplyAttributeType(self.acqConfig.attributes[dsName][SanityChannel_Attr_Thresh_name][Attribute_ValueKey],
                                                     self.acqConfig.attributes[dsName][SanityChannel_Attr_Thresh_name][Attribute_TypeKey])
                    downsampledDS = list(map(lambda x: True if x >= threshValue else False, downsampledDS))
                    #invert if required by user
                    InvCutoff = ApplyAttributeType(
                        self.acqConfig.attributes[dsName][SanityChannel_Attr_InvCutoff_name][Attribute_ValueKey],
                        self.acqConfig.attributes[dsName][SanityChannel_Attr_InvCutoff_name][Attribute_TypeKey])

                    if InvCutoff:
                        downsampledDS = list(not x for x in downsampledDS)

                    #cast to numpy array
                    downsampledDS = np.asarray(downsampledDS,dtype=bool)
                    #save to file
                    self.tmpDataset = self.h5fObj.create_dataset(dsName, data=downsampledDS,
                                                                 compression="gzip", compression_opts=9)

                # SanityChannel_Attr_Thresh_name
                # SanityChannel_Attr_Cutoff_name

            else:
                self.tmpDataset = self.h5fObj.create_dataset(dsName, data=self.dataArray[dsName],
                                                             compression="gzip", compression_opts=9)
            print("Dataset name: " + str(self.tmpDataset.name))
            for attName in self.acqConfig.attributes[dsName]:
                # print(attName)
                # print(self.datasetsTabs.widget(i).attributesList[attName].Type)
                # print(self.datasetsTabs.widget(i).attributesList[attName].Value)
                try:
                    self.tmpDataset.attrs[attName] = \
                        ApplyAttributeType(
                                           ApplyAttributeReplacement(self.acqConfig.attributes[dsName][attName][Attribute_ValueKey],
                                                      self, self.acqConfig, dsName),
                                           self.acqConfig.attributes[dsName][attName][Attribute_TypeKey])
                except Exception as e:
                    sys.stderr.write(
                        "Error while trying to cast the parameter \"" + attName + "\" from the attribute list to type " +
                        self.acqConfig.attributes[dsName][attName][Attribute_TypeKey] + ". "
                                                                                   "Make sure that the type you chose for this variable is compatible with the its contents. The contents "
                                                                                   "are: " + ApplyAttributeReplacement(
                            str(self.acqConfig.attributes[dsName][attName][Attribute_ValueKey]), self, self.acqConfig,
                            dsName) + "\n")
                    sys.stderr.write("Exception says: " + str(e) + "\n")
                    sys.stderr.flush()

        # write built-in sensor magnetic fields
        self.tmpDataset = self.h5fObj.create_dataset(OutputMagFieldSensorDataset, data=self.auxMagFieldSensorArray,
                                                     compression="gzip", compression_opts=9)
        self.tmpDataset.attrs["Units"] = self.magFieldSenorUnit
        self.tmpDataset.attrs["Range"] = self.magFieldSenorRange

        # write built-in temperature sensor values
        self.h5fObj.create_dataset(InternalTemperaturesDataset, data=self.intTemperatureArray,
                                   compression="gzip", compression_opts=9)
        self.h5fObj.create_dataset(ExternalTemperaturesDataset, data=self.extTemperatureArray,
                                   compression="gzip", compression_opts=9)

        # write errors list to the file
        errorArray = []
        for errorElement in self.errorMsgs:
            QCoreApplication.processEvents()
            errorArray.append(
                [np.str(errorElement[ERROR_IDENTIFIER_SEVERITY]), np.str(errorElement[ERROR_IDENTIFIER_MESSAGE])])
        self.tmpErrorDataset = self.h5fObj.create_dataset("Errors", data=[0],
                                                          compression="gzip", compression_opts=9)
        for i in range(len(errorArray)):
            QCoreApplication.processEvents()
            self.tmpErrorDataset.attrs[OutputPrefix_Error + str(i)] = errorArray[i][0] + ": " + errorArray[i][1]
        self.h5fObj.close()

