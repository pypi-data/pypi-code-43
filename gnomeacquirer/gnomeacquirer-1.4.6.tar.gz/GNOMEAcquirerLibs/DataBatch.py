import datetime
import copy
import re
from GNOMEAcquirerLibs.AttributeData import *

# constants
# The following define error messages definitions, as communicated between the main thread and the acquisition thread
ERROR_SEVERITY_SEVERE  = "Severe"
ERROR_SEVERITY_WARNING = "Warning"

ERROR_IDENTIFIER_SEVERITY = "Severity"
ERROR_IDENTIFIER_MESSAGE  = "Message"

regex_datetime_str = r"^\s*Date: (?P<Date>\d{4}.\d{2}.\d{2}) Time: (?P<Time>\d{2}.\d{2}.\d{2})\s*(?P<IsNotSet>Time not set!)?\s*$"
regex_weekinfo_str = r"^\s*Week: (?P<WeekNumber>\d+) TOW: (?P<TimeOfWeek>\d+)\s*$"
regex_coords_str   = r"^\s*Lat.\s*\[deg\]:\s*(?P<Latitude>[(-|)]\d*.\d+)\s*Long.\s*\[deg\]:\s*(?P<Longitude>[(-|)]\d*.\d+)\s*Alt.\s*\[m]:\s*(?P<Altitude>[(-|)]\d*.\d+)\s*$"

regex_datetime = re.compile(regex_datetime_str)
regex_weekinfo = re.compile(regex_weekinfo_str)
regex_coords = re.compile(regex_coords_str)

def GetChannelToArrayMapping(channelOpBinary):
    """
    Channel to array mapping is necessary because if a channel is disabled, consequently a column disappears instead
    of making it empty.
    Therefore, it's important to detect what channels are enabled, and then map them in order with the available column.
    ChannelToArray means channel number in the device vs the column number in the array
    :param channelOpBinary: A list with length that is equal to the maximum number of channels (so, 4).
        It contains as boolean flags whether a every channel is enabled
    :return: Returns a dict that has for every enabled channel the corresponding column in the array. If the channel
    doesn't exist, its key doesn't exist in the dict.
    """
    #find channel to array element correspondence. In the acquisition box, if a channel is disabled, it doesn't produce output
    channelToArrayMapping = {}
    chToArrCounter = 0
    #check available channels
    for i in range(len(channelOpBinary)):
        if channelOpBinary[i]:
            channelToArrayMapping[i] = chToArrCounter
            chToArrCounter += 1
    return channelToArrayMapping


def FindDataRange(StrQueue, startStr, endStr):
    startIndex = next((i for i in range(len(StrQueue)) if StrQueue[i].replace(" ","").replace("\t","") == startStr), None)
    if startIndex is not None:
        endIndex = next(
            (i for i in range(startIndex + 1, len(StrQueue)) if StrQueue[i] == endStr), None)
        if endIndex is None:
            raise LookupError("Cannot find " + endStr)
    else:
        raise LookupError("Cannot find " + startStr)
    return startIndex, endIndex+1


# DataBatch is a class whose object contains the data received from the device in a single shot.
# DataBatch consists mainly of a string queue that is received from the device (we call batch here).
# This string queue is analyzed based on a certain order of the information.
class DataBatch:
    SamplingRatePossibilities = [1,2,4,8,16,32,64,128,256,512,1024]
    d_dataPrefix       = "@Data"
    d_magneticPrefix   = "@Magnetic"
    d_startString      = "@Header"
    d_endString        = "@End"
    d_timePrefix       = "Time:"
    d_datePrefix       = "Date:"
    d_intTempPrefix    = "Temp. int. [C]:"
    d_extTempPrefix    = "Temp. ext. [C]:"
    d_latitudePrefix   = "Lat. [deg]:"
    d_longitudePrefix  = "Long. [deg]:"
    d_altitudePrefix   = "Alt. [m]:"
    d_weekNumberPrefix = "Week:"
    d_timeNotSetStr = "Time not set!"
    f_dateFormat = "%Y.%m.%d"
    f_timeFormat = "%H.%M.%S"

    def __init__(self, acquisitionConfig, dataQueueOfStrings):
        self.deviceName       = acquisitionConfig.requestedDevice
        self.dataStringQueue  = dataQueueOfStrings
        self.requestedChannelsInDev = acquisitionConfig.requestedChannels
        self.requestedChannelsTypesInDev = acquisitionConfig.requestedChannelsTypes

        self.dataArray        = []
        #Our acquisition system has a built-in (auxiliary) sensor for magnetic fields. These are stored here.
        self.auxMagFieldSensorArray = []
        self.samplingRate     = None
        self.missingPoints    = None
        self.startTime        = None
        self.weekNumber       = None
        self.latitude         = None
        self.longitude        = None
        self.altitude         = None
        self.channelOp        = []
        self.channelOpBinary  = []
        self.receiverMode     = None
        self.intTemperature   = None
        self.extTemperature   = None
        self.magFieldSenorUnit = ""
        self.headerStringList = []
        self.errorFlag = False
        self.errorMsgs = []

        self.parseAllData()


    def containsSevereError(self):
        for err in self.errorMsgs:
            if err[ERROR_IDENTIFIER_SEVERITY] == ERROR_SEVERITY_SEVERE:
                return err
        return None

    def parseAllData(self):
        self.checkParameterInstanceSanity(DataBatch.d_datePrefix)
        self.checkParameterInstanceSanity(DataBatch.d_intTempPrefix)
        self.checkParameterInstanceSanity(DataBatch.d_extTempPrefix)
        self.checkParameterInstanceSanity(DataBatch.d_latitudePrefix)
        self.checkParameterInstanceSanity(DataBatch.d_weekNumberPrefix)
        if self.errorFlag:
            return self.errorFlag

        if not self.containsSevereError():
            self.parseStartTime()
        if not self.containsSevereError():
            self.parseDataArray()
        if not self.containsSevereError():
            self.parseAuxSensorMagneticFields()
        if not self.containsSevereError():
            self.checkChannelSelectionSanity()
        if not self.containsSevereError():
            self.castDataToCorrectTypes()
        if not self.containsSevereError():
            self.parseCoordinates()
        if not self.containsSevereError():
            self.parseTemperature()
        if not self.containsSevereError():
            self.parseWeekNumber()
        if not self.containsSevereError():
            self.calculateSamplingRate()

        if self.errorFlag:
            return self.errorFlag



    #search string data queue and find a parameter by its prefix.
    #returns a list of lines containing these instances
    def findPrefixInDataQueue(self,prefix):
        return [line for line in self.dataStringQueue if line[:len(prefix)] == prefix]

    #checks whether every parameter exists in every batch only once!
    #a parameter is defined by its prefix in a line
    def checkParameterInstanceSanity(self,prefix):
        dataInstancesCount = sum(line[:len(prefix)] == prefix for line in self.dataStringQueue)
        if dataInstancesCount > 1:
            self.setErrorFlag("Multiple instances of \"" + prefix + "\" string was found in a single data batch. " \
                                                                          "The current model of data " \
                                                                          "includes that only once",ERROR_SEVERITY_SEVERE)
        elif dataInstancesCount == 0:
            self.setErrorFlag("Could not find \"" + prefix + "\" in the current data batch. " \
                                                                   "The current model of the data contains " \
                                                                   "that once per batch.",ERROR_SEVERITY_SEVERE)

    def parseStartTime(self):
        try:
            self.dateStrList = self.findPrefixInDataQueue(self.d_datePrefix)

            self.dateStr = self.dateStrList[0]

            datetime_parsed = regex_datetime.match(self.dateStr)

            # if date string doesn't match the expected form
            if datetime_parsed is None:
                self.setErrorFlag("Date and time does not comply to the expected format. "
                                  "Unable to find date and/or time.", ERROR_SEVERITY_SEVERE)
                return

            if datetime_parsed.group("IsNotSet") is not None:
                self.setErrorFlag(
                    "Time is claimed to be not set. Antenna has to be connected for the data acquired to be meaningful")

            #remove strings prefix
            timeStrToParse = datetime_parsed.group("Time")
            dateStrToParse = datetime_parsed.group("Date")

            sep = "___"

            try:
                self.startTime = datetime.datetime.strptime(timeStrToParse + sep + dateStrToParse,
                                                            DataBatch.f_timeFormat + sep + DataBatch.f_dateFormat)
            except Exception as e:
                self.setErrorFlag("Times and Dates are supposed to contain three, two digit numbers separated by a dot, \".\", " \
                                 "This does not seem to be the case! " \
                                 "Check the syntax of the received data from the device. The string seen as time is: " +
                                 "Time: " + str(timeStrToParse) + " | " + "Date: " +str(dateStrToParse) + ". Exception message: " + str(e)
                                  , ERROR_SEVERITY_SEVERE)
                return

        except Exception as e:
            self.setErrorFlag("An exception was thrown while parsing date/time. Make sure that the device is sending correct time format." + " Exception message: " + str(e), ERROR_SEVERITY_SEVERE)
            return

    def parseCoordinates(self):
        try:
            latitudeStr  = self.findPrefixInDataQueue(self.d_latitudePrefix)[0]
            coords_parsed = regex_coords.match(latitudeStr)
            if coords_parsed is None:
                self.setErrorFlag("Unable to parse GPS coordinates from: " + latitudeStr, ERROR_SEVERITY_SEVERE)

            self.latitude = float(coords_parsed.group("Latitude"))
            self.longitude = float(coords_parsed.group("Longitude"))
            self.altitude = float(coords_parsed.group("Altitude"))

        except Exception as e:
            self.setErrorFlag("Could not find/convert coordinates (longitude,latitude,altitude)." + " Exception message: " + str(e),ERROR_SEVERITY_SEVERE)

    def parseTemperature(self):
        try:
            intTempStr = self.findPrefixInDataQueue(self.d_intTempPrefix)[0]
            extTempStr = self.findPrefixInDataQueue(self.d_extTempPrefix)[0]

            self.intTemperature = str(intTempStr[len(self.d_intTempPrefix):].replace(" ","").replace("\t",""))
            self.extTemperature = str(extTempStr[len(self.d_extTempPrefix):].replace(" ","").replace("\t",""))
            try:
                self.intTemperature = float(self.intTemperature)
            except:
                self.intTemperature = "nan"

            try:
                self.extTemperature = float(self.extTemperature)
            except:
                self.extTemperature = "nan"


        except Exception as e:
            self.setErrorFlag("Could not find/convert temperature information." + " Exception message: " + str(e))

    def parseWeekNumber(self):
        try:
            weekNumberStr = self.findPrefixInDataQueue(self.d_weekNumberPrefix)[0]
            weekNumber_parsed = regex_weekinfo.match(weekNumberStr)
            if weekNumber_parsed is None:
                self.setErrorFlag("Unable to parse week number from string: " + weekNumberStr,
                                  ERROR_SEVERITY_SEVERE)
                return
            self.weekNumber = int(weekNumber_parsed.group("WeekNumber"))

        except Exception as e:
            self.setErrorFlag("Could not find/convert week number." + " Exception message: " + str(e), ERROR_SEVERITY_SEVERE)


    def parseDataArray(self):
        try:
            range = FindDataRange(self.dataStringQueue, DataBatch.d_dataPrefix, DataBatch.d_magneticPrefix)
        except Exception as e:
            self.setErrorFlag("Error while searching for auxiliary sensor magnetic field data."
                              + " Exception message: " + str(e))


        self.parseChannelStatusString(self.dataStringQueue[range[0]+1])

        try:
            self.dataArray = list(map(str.split,self.dataStringQueue[range[0]+2:range[1]-1]))
        except Exception as e:
            self.setErrorFlag("Error while pushing acquired data points into an array." + " Exception message: " + str(e),ERROR_SEVERITY_SEVERE)
            return

        # self.getChannelStateBits = False
        # self.startCollecting = False
        # for line in self.dataStringQueue:
        #     if line.replace(" ","").replace("\t","") == DataBatch.d_dataPrefix:
        #         self.getChannelStateBits = True
        #         continue
        #
        #     if self.getChannelStateBits:
        #         self.parseChannelStatusString(line)
        #         self.getChannelStateBits = False
        #         self.startCollecting = True
        #         continue
        #
        #     if self.startCollecting:
        #         if line.replace(" ","").replace("\t","") == DataBatch.d_magneticPrefix:
        #             break
        #         else:
        #             try:
        #                 self.splitLine = line.split()
        #                 self.dataArray.append(self.splitLine)
        #             except Exception as e:
        #                 self.setErrorFlag("Error while pushing acquired data points into an array." + " Exception message: " + str(e),ERROR_SEVERITY_SEVERE)
        #                 return

    def parseAuxSensorMagneticFields(self):

        try:
            range = FindDataRange(self.dataStringQueue, DataBatch.d_magneticPrefix, DataBatch.d_endString)
        except Exception as e:
            self.setErrorFlag("Error while searching for auxiliary sensor magnetic field data."
                              + " Exception message: " + str(e))

        try:
            self.parseAuxMagneticFieldsStatus(self.dataStringQueue[range[0]+1])
            self.auxMagFieldSensorArray = list(map(lambda p: np.array(list(map(np.float32,p.split()))),self.dataStringQueue[range[0]+2:range[1]-1]))

        except Exception as e:
            self.setErrorFlag("Error while pushing auxiliary sensor magnetic field data points into an array."
                              " It is possible that the sensor is not properly connected." + " Exception message: " + str(e))
            return

        # self.getMagStateBits = False
        # self.startCollecting = False
        # for line in self.dataStringQueue:
        #     if line.replace(" ","").replace("\t","") == DataBatch.d_magneticPrefix:
        #         self.getMagStateBits = True
        #         continue
        #
        #     if self.getMagStateBits:
        #         self.parseAuxMagneticFieldsStatus(line)
        #         self.getMagStateBits = False
        #         self.startCollecting = True
        #         continue
        #
        #     if self.startCollecting:
        #         if line.replace(" ","").replace("\t","") == DataBatch.d_endString:
        #             break
        #         else:
        #             try:
        #                 self.splitLine = list(map(np.float32,line.split()))
        #                 self.auxMagFieldSensorArray.append(np.array(self.splitLine))
        #             except Exception as e:
        #                 self.setErrorFlag("Error while pushing auxiliary sensor magnetic field data points into an array."
        #                                   " It is possible that the sensor is not properly connected." + " Exception message: " + str(e))
        #                 return

    def castDataToCorrectTypes(self):
        self.dataArrayTranspose = list(map(list, list(zip(*self.dataArray))))

        self.channelToArrayMapping = GetChannelToArrayMapping(self.channelOpBinary)

        self.dataToSave = {}
        self.channelRangesPerName = {}
        for dataset in self.requestedChannelsInDev:
            try:
                dataArrayIndex = self.channelToArrayMapping[self.requestedChannelsInDev[dataset]-1]
                self.dataToSave[dataset] = self.dataArrayTranspose[dataArrayIndex]

                #save channel ranges from channel name (instead of number)
                self.channelRangesPerName[dataset] = self.channelRanges[self.requestedChannelsInDev[dataset]-1]
            except Exception as e:
                print("Error: Exception with: " + dataset + ": ",e)
                self.setErrorFlag("Error while resorting data from recorded arrays. Make sure you enabled the channels "
                                  "you requested from the acquisition box. Check the data log to find the problem in the data." + " Exception message: " + str(e),ERROR_SEVERITY_SEVERE)
                return
            try:
                if self.requestedChannelsTypesInDev[dataset] == GetTypeNameString(AttributeType.Double):
                    typeToCast = np.float64
                elif self.requestedChannelsTypesInDev[dataset] == GetTypeNameString(AttributeType.Float):
                    typeToCast = np.float32
                elif self.requestedChannelsTypesInDev[dataset] == GetTypeNameString(AttributeType.Integer32):
                    typeToCast = np.int32
                elif self.requestedChannelsTypesInDev[dataset] == GetTypeNameString(AttributeType.Integer64):
                    typeToCast = np.int64
                elif self.requestedChannelsTypesInDev[dataset] == GetTypeNameString(AttributeType.String):
                    typeToCast = np.str
                else:
                    print("Dataset received: " + str(self.dataToSave[dataset]))
                    dataSampleForException = self.dataToSave[dataset][0:4] if len(self.dataToSave[dataset]) > 4 else self.dataToSave[dataset]
                    self.setErrorFlag("No supported data type was found to cast dataset " + dataset + " to " + self.requestedChannelsTypesInDev[dataset] + ". Check the terminal log of the program to see what the full data array looks like. Part of the data is " + str(dataSampleForException) + ". Exception message: " + str(e),ERROR_SEVERITY_SEVERE)
                    print(self.dataToSave)

                # self.dataToSave[dataset] = (np.asarray(self.dataToSave[dataset],dtype=typeToCast) + typeToCast(self.chOffsets[dataset]))*typeToCast(self.conversionFactors[dataset])
                self.dataToSave[dataset] = (np.asarray(self.dataToSave[dataset],dtype=typeToCast))

            except Exception as e:
                print(self.requestedChannelsInDev)
                print(self.dataToSave)
                print("Dataset received: " + str(self.dataToSave[dataset]))
                print("Exception message: ",e)
                dataSampleForException = self.dataToSave[dataset][0:4] if len(self.dataToSave[dataset]) > 4 else self.dataToSave[dataset]
                self.setErrorFlag("Error while trying to cast data of dataset " + dataset + " to " + self.requestedChannelsTypesInDev[dataset] + ". Check the terminal log of the program to see what the full data array looks like. Part of the data is " + str(dataSampleForException) + ". Exception message: " + str(e),ERROR_SEVERITY_SEVERE)


    def parseChannelStatusString(self,chString):
        self.splitChannelStatus = chString.split(",")
        expectedNumOfEntries = 5
        if not len(self.splitChannelStatus) == expectedNumOfEntries:
            self.setErrorFlag("The line coming directly after " + DataBatch.d_dataPrefix + " is expected"
                              " to contain 5 strings separated by commas. This was not found. Unknown error!",ERROR_SEVERITY_SEVERE)
            return

        else:
            for i in range(expectedNumOfEntries):
                chStripped = self.splitChannelStatus[i].replace(" ","").replace("\t","")
                #the following removes the prefix strings of channels status, i.e., Ch1, for example.
                self.channelOp.append(chStripped[3:])
        #convert channel findings to binary values
        self.channelOpToBin()
        self.channelOpToRanges()
        # print(self.channelOpBinary)

        self.samplingRate = float(self.splitChannelStatus[4].replace(" S/s",""))

    def parseAuxMagneticFieldsStatus(self,magString):
        self.magFieldSenorStatus = magString.split()
        if len(self.magFieldSenorStatus) < 4:
            self.setErrorFlag("The header of sensor magnetic fields that comes after " + DataBatch.d_magneticPrefix + " is expected"
                              " to contain 4 or more strings separated by a space. This was not found. "
                              "The string seen is: \"" + magString + "\".", ERROR_SEVERITY_SEVERE)
            return

        else:
            #the range comes 4th
            self.magFieldSenorRange = self.magFieldSenorStatus[3]
            if len(self.magFieldSenorStatus) > 4:
                self.magFieldSenorUnit  = self.magFieldSenorStatus[4].replace("[","").replace("]","")
        # print(self.channelOpBinary)


    #write channel states as booleans
    def channelOpToBin(self):
        #self.channelOp contains whether channels are on or off as strings, it's either "off" or a range
        self.channelOpBinary = list(map(lambda channelStrStatus: True if not channelStrStatus == "off" else False, self.channelOp))

    def channelOpToRanges(self):
                #initialize an array with garbage (meaningless) values. This is because python doesn't have a resize function
        #in its default array
        self.channelRanges = self.channelOp

    def checkChannelSelectionSanity(self):
        self.channelToArrayMapping = GetChannelToArrayMapping(self.channelOpBinary)
        channelCount = 0
        for dataset in self.requestedChannelsInDev:
            binVal = self.channelOpBinary[channelCount]
            if binVal:
                if not (self.requestedChannelsInDev[dataset]-1 in self.channelToArrayMapping):
                    self.setErrorFlag("Error in channel presence. Channel " + str(self.requestedChannelsInDev[dataset]) + " in device " + str(self.deviceName) + " is not enabled and/or does not exist in the acquired data.",ERROR_SEVERITY_SEVERE)
                    print("Error in channel selection. Channel " + str(self.requestedChannelsInDev[dataset]) + " in device " + str(self.deviceName) + " is not enabled and/or does not exist in the acquired data.")

            channelCount += 1

    def calculateSamplingRate(self):
        if len(self.dataArray) < 15:
            self.setErrorFlag("The sampling rate of the data cannot be calculated before parsing the data points. "
                              "Or: You cannot choose a sampling rate that is less than 20 Hz. This is due to the algorithm "
                              "used to calculate the sampling rate and determine whether there are missing points in the data.",ERROR_SEVERITY_SEVERE)
        else:
            try:
                #the following is an algorithm that detects the existence of missing points by comparing with the possible
                #values of the sampling rate
                self.dataLength = len(self.dataArray)
                self.missingPoints = int(round(abs(self.samplingRate - self.dataLength)))
                if self.missingPoints != 0:
                    self.setErrorFlag("WARNING: There are missing data points in one of the data batches. Number of missing points is: " + str(self.missingPoints), severity=ERROR_SEVERITY_SEVERE)
            except Exception as e:
                self.setErrorFlag("An exception was thrown while trying to calculate the sampling rate. Exception message: " + str(e), ERROR_SEVERITY_SEVERE)
                print("An exception was thrown while trying to calculate the sampling rate. Exception message: " + str(e))

    def setErrorFlag(self,message,severity=ERROR_SEVERITY_WARNING):
        self.errorFlag = True
        self.errorMsgs.append({ERROR_IDENTIFIER_MESSAGE:message, ERROR_IDENTIFIER_SEVERITY:severity})
