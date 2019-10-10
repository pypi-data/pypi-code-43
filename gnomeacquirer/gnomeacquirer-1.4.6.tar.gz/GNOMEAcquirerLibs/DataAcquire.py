#!/usr/bin/python3

from PyQt5 import QtCore

from math import sin,cos,pi,floor
import time
import datetime
import copy
import serial
from GNOMEAcquirerLibs.DataCollected import *
from GNOMEAcquirerLibs.DataBatch import *
from GNOMEAcquirerLibs.DataToPlot import *
import os
import sys
import glob
import ctypes as c
import multiprocessing as mp

#constants
stringDumpFolderName  = "Dumped"
stringDumpFilePadding = 6
numOfLinesInDumpFile  = 500000

acquisitionEndlineChar = "\r\n"

NoDevicesString = "Cannot find any device"

def decodeString(strIn):
    if isinstance(strIn,bytes):
        retStr = strIn.decode("ascii")
    else:
        retStr = strIn
    return retStr

def CreateDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def ListOnlyDirs(path):
    if path[-1] != "/":
        path += "/"
    if os.path.isdir(path):
        contents = os.listdir(path)
    else:
        return []
    contentsOnlyDirs = []
    for p in contents:
        if os.path.isdir(os.path.join(path, p)):
            contentsOnlyDirs.append(p)
    return contentsOnlyDirs


def ListOnlyFiles(path):
    if path[-1] != "/":
        path +=  "/"
    if os.path.isdir(path):
        contents = os.listdir(path)
    else:
        return []
    contentsOnlyFiles = []
    for p in contents:
        if os.path.isfile(os.path.join(path, p)):
            contentsOnlyFiles.append(p)
    return contentsOnlyFiles


def get_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

# fills the queue of lines self.acqBuffer
def fillQueue_process(devSpecs, acquisitionSpecs, shared_stopped, shared_return_list, shared_lock):
    def DecodeString(strIn):
        if isinstance(strIn,bytes):
            retStr = strIn.decode("ascii")
        else:
            retStr = strIn
        return retStr

    def TransferQueueToSharedMemory(bufferQueue):
        if len(bufferQueue) > acquisitionSpecs["LengthToPass"]:
            # print("locking in fill")
            try:
                shared_lock.acquire()
                # print("locked in fill")
                if len(shared_return_list) < acquisitionSpecs["AcqMaxBufferLines"]:
                    shared_return_list.extend(bufferQueue)
                    del bufferQueue[:]
                # print("unlocking in fill")
            finally:
                shared_lock.release()
                # print("unlocked in fill")

    def ReopenDevice(devObject):
        try:
            devObject.close()
            devObject.open()
            print("Instrument: " + devSpecs["DevName"] + " is open successfully in the process")

        except Exception as e:
            print("Error while trying to connect to device " + devObject.port + ". The error says:")
            print(e)
            time.sleep(2)

    try:
        devObj = serial.Serial()
        devObj.port = devSpecs["DevName"]
        devObj.baudrate = 115200
        devObj.bytesize = serial.EIGHTBITS  # number of bits per bytes
        devObj.parity = serial.PARITY_ODD  # set parity check: no parity
        devObj.stopbits = serial.STOPBITS_ONE  # number of stop bits
        devObj.timeout = 2  # block read for this amount
        devObj.xonxoff = True  # disable software flow control
        devObj.rtscts = False  # disable hardware (RTS/CTS) flow control
        devObj.dsrdtr = False  # disable hardware (DSR/DTR) flow control
        devObj.writeTimeout = 2  # timeout for write

        ReopenDevice(devObj)

    except Exception as e:
        print("Error configuring serial port: ")
        print(e)
        print("Error while trying to configure serial port for instrument instrument: " + devSpecs["DevName"])
        # shared_stopped[0] = True
        # return


    acqBufferStr = ""
    acqBuffer = []

    #the next line measures how long it has been since the last successful data pull has been made
    #this is to fix a problem with PySerial where it loses its connection to the device some times for no reason
    #the solution is to reopen the port with the function ReopenPort()
    lastAcquisitionTime = datetime.datetime.now()
    deemFailedConnectionAfter = 120 #seconds
    print(acquisitionSpecs)
    if not acquisitionSpecs["ParanoidMode"]:
        # if the local buffer (software buffer) is empty, fill it from the device
        # if len(self.acqBuffer) <= 0:
        while not shared_stopped[0]:
            print("Pulling data from device...")
            # the following variable ensures that if the buffer is empty, then wait, otherwise keep pulling until it's empty
            # keep pulling until the buffer max number of lines is reached (unless the device buffer is empty, there's "break" inside)
            TransferQueueToSharedMemory(acqBuffer)
            while len(acqBuffer) < acquisitionSpecs["AcqMaxBufferLines"] and (not shared_stopped[0]):
                try:
                    # if the user hasn't stopped the acquisition
                    if not shared_stopped[0]:
                        # read available bytes to local buffer
                        buffer = decodeString(devObj.read(8192))

                        #if the buffer is empty, it's possible that connection to the device is lost
                        #if for time that's equal to deemFailedConnectionAfter noting is received, reopen connection
                        if buffer == "":
                            if abs(datetime.datetime.now() - lastAcquisitionTime) > datetime.timedelta(
                                    seconds=deemFailedConnectionAfter):
                                print("Failed in getting data from the device for " + str(
                                    deemFailedConnectionAfter) + " second(s). Trying to reconnect to the device and resetting time counter...")
                                ReopenDevice(devObj)
                                lastAcquisitionTime = datetime.datetime.now()
                            continue

                        else:
                            lastAcquisitionTime = datetime.datetime.now()

                            acqBufferStr += buffer

                            # commented for performance
                            # print("Expected length: " + str(bytesToRead) + "; Received length: " + str(len(buffer)))

                            # find the last endline character in the accumulated string so that the rest can be combined
                            # with the next available bytes
                            lastChar = acqBufferStr.rfind(acquisitionEndlineChar)
                            acqBuffer.extend(acqBufferStr[0:lastChar + 1].split(acquisitionEndlineChar))
                            # delete empty strings from the buffer queue
                            acqBuffer = list(filter(None, acqBuffer))
                            # start the next buffer from the last available endline
                            acqBufferStr = acqBufferStr[lastChar + 1:]
                            # remove \n and \r from the strings
                            acqBuffer = list(map(lambda x: x.replace("\n", "").replace("\r", ""), acqBuffer))

                        # commented for performance
                        # print("Current buffer size (in lines): " + str(len(acqBuffer)))
                    else:
                        break
                except Exception as e:
                    print("Error was thrown while pulling data. The error says:")
                    print(e)
                    print("Trying to reconnect to the device")
                    ReopenDevice(devObj)

                TransferQueueToSharedMemory(acqBuffer)

    else:
        while not shared_stopped[0]:
            while len(acqBuffer) < acquisitionSpecs["AcqMaxBufferLines"] and (not shared_stopped[0]):
                try:
                    buffer = decodeString(devObj.readline())
                    buffer = buffer.replace(acquisitionEndlineChar, "").replace("\n", "").replace("\r", "")
                    if buffer == "":
                        continue
                    acqBuffer.append(buffer)
                    TransferQueueToSharedMemory(acqBuffer)

                except Exception as e:
                    print("Error was thrown while pulling data. The error says:")
                    print(e)
                    print("Trying to reconnect to the device")
                    ReopenDevice(devObj)

            TransferQueueToSharedMemory(acqBuffer)

    try:
        devObj.close()
        print("Device " + devSpecs["DevName"] + " closed successfully.")
    except Exception as e:
        print("Unable to close device " + devSpecs["DevName"] + ". Exception says: ")
        print(e)

    print("Data acquisition thread reached its end successfully.")


class DataAcquirer(QObject):
    postErrorMessage  = QtCore.pyqtSignal(str)
    postResultsSignal = QtCore.pyqtSignal(DataToPlot, DataCollected)
    postNumMissingBatches = QtCore.pyqtSignal(int)
    reenableStartButtonSignal = QtCore.pyqtSignal()
    finishedSignal = QtCore.pyqtSignal()

    def __init__(self,acqConfig):
        # QtCore.QThread.__init__(self)
        QtCore.QObject.__init__(self)

        self.acqConfig = acqConfig

        self.acquisitionThread = None

        self.dataStrQueue = []
        self.stopped = False
        self.openInstrumentObject = None
        self.rm = None
        self.line = None

        self.fakeReaderCounter = -1
        self.fakePhase = 0
        self.fakeCurrentTime = datetime.datetime.utcnow() - datetime.timedelta(days=2 * 36500)
        self.fakeSamplingRate = 128
        self.fakeSamplingRateCounter = 0
        self.fakeChannelOuts = []

        self.fileAcqReader = None
        self.fileAcqListOfFiles = None
        self.fileAcqLastFileRead = None
        self.fileAcqFileLines = []
        self.fileAcqSubFolderForSuccessful = "Done"
        #sleep after how many lines to avoid freezing the GUI (starts with sleeping to enable the stop button)
        self.fileSleepCounterMax = 200000
        self.fileSleepCounter = self.fileSleepCounterMax


        self.acqBuffer = []
        self.acqBufferStr = ""
        self.acqMaxBufferLines = 100000

        # self.dataCollected = {}

        #the following helps in preventing unlimited pulls in a short time
        #if some time passes without data being found, then the program pauses to breathe to prevent overloading the
        #event loop
        self.pullForHowLongBeforeBreathing = 2
        self.pullsCounterLimit = 100
        self.pullBreatheTime   = 3

        self.mpManager = mp.Manager()
        self.shared_return_list = self.mpManager.list()
        self.shared_stopped = self.mpManager.list()
        self.shared_stopped.extend([False])
        self.shared_result_lock = mp.Lock()

    def stopAcquisition(self):
        self.stopped = True
        self.shared_stopped[0] = True

    def emitError(self,message,DoStopAcquisition=True,WithLogFileEntry=True):
        if WithLogFileEntry:
            self.logFileObj.write(str(datetime.datetime.utcnow().strftime(logDateTimeFormat)) + ": " + message + "\n\n")
            self.logFileObj.flush()
            self.logFileObj.flush()
        if DoStopAcquisition:
            self.stopAcquisition()
            self.postErrorMessage.emit(message)

    def healthyWait(self,totalWait):
        _waitTime = 0
        _waitStep = 0.1
        if totalWait < _waitStep:
            time.sleep(totalWait)
        else:
            while _waitTime < totalWait:
                QCoreApplication.processEvents()
                if self.stopped:
                    break
                else:
                    time.sleep(_waitStep)
                    _waitTime += _waitStep


    #fills the queue of lines self.acqBuffer
    def readLineRealToQueue(self):
        if not self.acqConfig.paranoidMode:
            pull_startTime = time.time()

            # if the local buffer (software buffer) is empty, fill it from the device
            if len(self.acqBuffer) <= 0:
                print("Pulling data from device...")

                #the following variable ensures that if the buffer is empty, then wait, otherwise keep pulling until it's empty

                #keep pulling until the buffer max number of lines is reached (unless the device buffer is empty, there's "break" inside)
                while len(self.acqBuffer) < self.acqMaxBufferLines:
                    QCoreApplication.processEvents()
                    try:
                    # if True:

                        #if the user hasn't stopped the acquisition
                        if not self.stopped:

                            #available bytes in device buffer
                            bytesToRead = self.openInstrumentObject.inWaiting()
                            #commented for performance
                            print("Bytes available: " + str(bytesToRead))

                            #if available bytes are zero
                            # the check for zero size is important because the device takes finite amount of time to prepare
                            # the next set of data to send it
                            if bytesToRead == 0:
                                print("Available bytes are zero! Waiting...")
                                # self.healthyWait(1)
                                if abs(time.time() - pull_startTime) > self.pullForHowLongBeforeBreathing:
                                    print("There has been no data to pull from the device for " + str(self.pullForHowLongBeforeBreathing) + " second(s). Breathing...")
                                    self.healthyWait(self.pullBreatheTime)
                                    pull_startTime = time.time()
                                continue

                            else:
                                #data was found, so reset breathing time
                                pull_startTime = time.time()

                                #self.healthyWait(0.01)
                                #read available bytes to local buffer
                                tempBuffer = decodeString(self.openInstrumentObject.read(bytesToRead))
                                self.acqBufferStr += tempBuffer

                                #commented for performance
                                print("Expected length: " + str(bytesToRead) + "; Received length: " + str(len(tempBuffer)))

                                #find the last endline character in the accumulated string so that the rest can be combined
                                #with the next available bytes
                                lastChar = self.acqBufferStr.rfind(acquisitionEndlineChar)
                                self.acqBuffer.extend(self.acqBufferStr[0:lastChar+1].split(acquisitionEndlineChar))
                                #delete empty strings from the buffer queue
                                self.acqBuffer = list(filter(None, self.acqBuffer))
                                #start the next buffer from the last available endline
                                self.acqBufferStr = self.acqBufferStr[lastChar+1:]
                                #remove \n and \r from the strings
                                self.acqBuffer = list(map(lambda x: x.replace("\n", "").replace("\r", ""), self.acqBuffer))

                            #commented for performance
                            print("Current buffer size (in lines): " + str(len(self.acqBuffer)))
                        else:
                            break
                    except Exception as e:
                        print("Assuming acquisition queue is empty... waiting.")
                        print("Exception message: ",e)
                        if len(self.acqBuffer) > 0:
                            pass
                        else:
                            self.healthyWait(5)
                #these lines make acquisition slower
                #print("Received strings:")
                #for line in self.acqBuffer: print(line)
            # lineData = self.acqBuffer.pop(0)

        else:
            QCoreApplication.processEvents()
            if len(self.acqBuffer) <= 0:
                while len(self.acqBuffer) < self.acqMaxBufferLines:
                    QCoreApplication.processEvents()
                    buffer = decodeString(self.openInstrumentObject.readline())
                    buffer = buffer.replace(acquisitionEndlineChar, "")

                    self.acqBuffer.extend(buffer.split(acquisitionEndlineChar))


                # delete empty strings from the buffer queue
                self.acqBuffer = list(filter(None, self.acqBuffer))
                # remove \n and \r from the strings
                self.acqBuffer = list(map(lambda x: x.replace("\n", "").replace("\r", ""), self.acqBuffer))

            # lineData = self.acqBuffer.pop(0)
            # print(lineData)

        # return lineData

    def readLineFile(self):
        QCoreApplication.processEvents()
        self.fileSleepCounter += 1
        # if self.fileSleepCounter >= self.fileSleepCounterMax:
        #     self.fileSleepCounter = 0
        #     print("Breathing...")
        #     self.healthyWait(3)
        #     print("Done breathing.")
        if len(self.fileAcqFileLines) <= 0:
            if len(self.fileAcqListOfFiles) > 0:
                self.fileAcqLastFileRead = self.fileAcqListOfFiles.pop(0)
                with open(os.path.join(self.acqConfig.fileAcqPath,self.fileAcqLastFileRead)) as f:
                    self.fileAcqFileLines = f.readlines()
                    self.fileAcqFileLines = list(map(lambda x: x.replace("\n", "").replace("\r", ""), self.fileAcqFileLines))
                    self.fileAcqFileLines = list(filter(None, self.fileAcqFileLines))
                    f.close()

                return self.fileAcqFileLines.pop(0)
            else:
                self.emitError("All files in the directory given have been read and parsed.")

        else:
            return self.fileAcqFileLines.pop(0)

    def readLineFake(self):
        self.fakeRetVal = ""
        if self.fakeReaderCounter == -1:
            self.fakeCurrentTime += datetime.timedelta(seconds=1)
            self.fakeRetVal = "@Header"
        elif self.fakeReaderCounter == 0:
            self.fakeRetVal = "Date: " + self.fakeCurrentTime.strftime(DataBatch.f_dateFormat) + " Time: " + self.fakeCurrentTime.strftime(DataBatch.f_timeFormat)
        elif self.fakeReaderCounter == 1:
            self.fakeRetVal = ""
        elif self.fakeReaderCounter == 2:
            self.fakeRetVal = "Week: 1024 TOW: 12345"
        elif self.fakeReaderCounter == 3:
            self.fakeRetVal = ""
        elif self.fakeReaderCounter == 4:
            self.fakeRetVal = "UTC offset: 0  No UTC info!"
        elif self.fakeReaderCounter == 5:
            self.fakeRetVal = "GPS time, GPS PPS, Time from GPS"
        elif self.fakeReaderCounter == 6:
            self.fakeRetVal = "Rec. mode: 7"
        elif self.fakeReaderCounter == 7:
            self.fakeRetVal = "Self survey progress: 100%"
        elif self.fakeReaderCounter == 8:
            self.fakeRetVal = "Warnings: Antenna open, Not tracking satellites, Almanac not complete"
        elif self.fakeReaderCounter == 9:
            self.fakeRetVal = "Decod. stat.: 0x01 No GPS time"
        elif self.fakeReaderCounter == 10:
            self.fakeRetVal = "Temp. int. [C]: 12.34"
        elif self.fakeReaderCounter == 11:
            self.fakeRetVal = "Temp. ext. [C]: --"
        elif self.fakeReaderCounter == 12:
            self.fakeRetVal = "Lat. [deg]: 49.9905505 Long. [deg]: 8.2345987 Alt. [m]: 198.62"
        elif self.fakeReaderCounter == 13:
            self.fakeRetVal = ""
        elif self.fakeReaderCounter == 14:
            self.fakeRetVal = ""
        elif self.fakeReaderCounter == 15:
            self.fakeRetVal = "@Data"
        elif self.fakeReaderCounter == 16:
            self.fakeRetVal = self.fakeChannelStates
        elif self.fakeReaderCounter == 17:
            if self.fakeSamplingRateCounter < self.fakeSamplingRate:
                self.fakeSamplingRateCounter += 1
                #subtract one from counter to stay here
                self.fakeReaderCounter -= 1
                self.fakeVal = sin(self.fakePhase)
                self.fakePhase += 2*pi*0.3/self.fakeSamplingRate
                self.fakeChannelOutsVals = list(map(lambda x: x*self.fakeVal,self.fakeChannelsAmplitudes))
                self.fakeChannelOuts = []
                for i in range(len(self.fakeChannelsAmplitudes)):
                    if self.fakeChannelsAmplitudes[i] != 0:
                        self.fakeChannelOuts.append(self.fakeChannelOutsVals[i])
                self.fakeRetVal = '  '.join(str(e) for e in self.fakeChannelOuts)
                if self.fakeSamplingRateCounter == self.fakeSamplingRate:
                    self.fakeReaderCounter += 1


        elif self.fakeReaderCounter == 18:
            self.fakeRetVal = "@Magnetic"
        elif self.fakeReaderCounter == 19:
            self.fakeRetVal = "X Y Z off"
        elif self.fakeReaderCounter == 20:
            self.fakeRetVal = "@End"
            self.fakeReaderCounter = -2
            self.fakeSamplingRateCounter = 0
        else:
            self.fakeReaderCounter = -1
            print("Wrong index: " + str(self.fakeReaderCounter))
        self.fakeReaderCounter += 1
        time.sleep(0.001)
        return self.fakeRetVal

    def readLineRealFromQueue(self):
        # self.readLineRealToQueue()
        self.pullBufferFromParallelProcess()
        try:
            lineData = self.acqBuffer.pop(0)
        except Exception as e:
            print("Queue is empty...")
            lineData = ""
        return lineData

    def pullBufferFromParallelProcess(self):
        #copy list from shared buffer and empty it
        # print("locking in read")
        step_size = 10000 #length to copy per step
        if len(self.acqBuffer) < 200000:
            try:
                self.shared_result_lock.acquire()
                # print("locked in read")
                #copy data to local buffer in steps to avoid freezing GUI
                while len(self.shared_return_list) > 0:
                    QCoreApplication.processEvents()
                    if len(self.shared_return_list) < step_size:
                        self.acqBuffer.extend(self.shared_return_list)
                        del self.shared_return_list[:]
                    else:
                        self.acqBuffer.extend(self.shared_return_list[:step_size])
                        del self.shared_return_list[:step_size]
                    QCoreApplication.processEvents()

                # print("unlocking in read")
            finally:
                self.shared_result_lock.release()
                # print("unlocked in read")

        else:
            print("Internal queue is full. No more data will be pulled from the acquisition thread.")
            print("Current size of the internal local queue: " + str(len(self.acqBuffer)))
            print("Current size of the shared queue: " + str(len(self.shared_return_list)))
        QCoreApplication.processEvents()


    def readLine(self):
        QCoreApplication.processEvents()
        if self.acqConfig.isFakeAcquisition:
            line_read = self.readLineFake()
        elif self.acqConfig.isFileAcquisition:
            line_read = self.readLineFile()
        else:
            line_read = self.readLineRealFromQueue()
        return line_read

    def openDumpFile(self):
        if self.acqConfig.doDumpStringsToFile:
            try:
                dumpPath = os.path.join(self.acqConfig.dataPath, stringDumpFolderName)
                CreateDir(dumpPath)
            except Exception as e:
                self.emitError("Couldn't create the path " + dumpPath + ". Make sure you have access to that directory and enough permissions to write. Exception message: " + str(e))
                return False
            self.dumpFilenum = -1
            while True:
                self.dumpFilenum += 1
                self.dumpFilename = os.path.join(dumpPath,str(self.dumpFilenum).zfill(stringDumpFilePadding))
                if not os.path.isfile(self.dumpFilename):
                    try:
                        self.dumpFileObj = open(self.dumpFilename, 'w')
                        self.dumpFileLineCounter = 0
                        self.dumpFileOpen = True
                        return True
                    except Exception as e:
                        self.emitError("Couldn't create the file " + self.dumpFilename + ". Make sure you have access to that directory and enough permissions to write. Exception message: " + str(e))
                        return False


    def writeDumpFileLine(self,line):
        if self.acqConfig.doDumpStringsToFile:
            if not self.dumpFileOpen:
                self.openDumpFile()

            if self.dumpFileLineCounter > numOfLinesInDumpFile:
                self.dumpFileObj.close()
                self.openDumpFile()

            if self.dumpFileOpen:
                self.dumpFileObj.write(line + "\n")
                self.dumpFileObj.flush()
                self.dumpFileLineCounter += 1
                return True
            else:
                return False

    def openLogFile(self,fileName):
        self.logFileObj = open(fileName, 'w')

    def dataError_ClearCollectedData(self,strQueue):
        self.postNumMissingBatches.emit(self.dataCollected.numOfBatches + 1) #+1 for the current batch that has the problem
        self.dataCollected.dumpRemainingDataToFile(strQueue)
        self.dataCollected.clearData()
        self.dataStrQueue.clear()

    def waitForAcquisitionThread(self):
        while True:
            if self.acquisitionThread is not None:
                if not self.acquisitionThread.is_alive():
                    break

                else:
                    QCoreApplication.processEvents()
                    self.healthyWait(1)

    def run(self):
        self.logFilePath = self.acqConfig.logFilePath
        try:
            CreateDir(os.path.join(self.acqConfig.dataPath, logDirName))

            self.openLogFile(self.logFilePath)
        except Exception as e:
            self.emitError("Unable to open acquisition log file. Exception message: " + str(e), True, False)
        except:
            self.emitError("Unable to open acquisition log file. Unknown exception.", True, False)
        # amplitude of channel is channel number
        self.fakeChannelStates = "Ch1 +/-1.25 [V], Ch2  +/-2.5 [V], Ch3 +/-5 [V], Ch4 +/-10 [V], 128 S/s"
        self.fakeChannelsAmplitudes = list(
            map(lambda x: 0 if (x.count("off") > 0) else 1, self.fakeChannelStates.split(",")))
        for i in range(len(self.fakeChannelsAmplitudes)):
            self.fakeChannelsAmplitudes[i] = self.fakeChannelsAmplitudes[i] * float(i + 1)

        print("Opening dump file...")
        self.openDumpFile()
        print("Finished opening dump file.")

        if self.acqConfig.isFakeAcquisition:
            self.openInstrumentObject = ""
            self.dataCollected = DataCollected(self.acqConfig)
            self.readBatchFunction = self.readBatchLineByLine
        elif self.acqConfig.isFileAcquisition:
            self.openInstrumentObject = ""
            self.dataCollected = DataCollected(self.acqConfig)
            self.fileAcqListOfFiles = ListOnlyFiles(self.acqConfig.fileAcqPath)
            self.readBatchFunction = self.readBatchLineByLine
            # self.fileAcqListOfFiles = list(map(lambda x: os.path.join(self.acqConfig.fileAcqPath,x),self.fileAcqListOfFiles))
            try:
                CreateDir(os.path.join(self.acqConfig.fileAcqPath,self.fileAcqSubFolderForSuccessful))
            except Exception as e:
                self.emitError("Unable to create the folder for successful files. Please make sure that the folder where the files are is writable. Exception message: " + str(e))
        else:
            # self.openInstrument(dev)
            self.dataCollected = DataCollected(self.acqConfig)
            self.readBatchFunction = self.readBatchFromDevice

        self.dataToPlot = DataToPlot()

        #start process for data acquisition
        self.healthyWait(2)
        if (not self.acqConfig.isFakeAcquisition) and (not self.acqConfig.isFileAcquisition):
            devSpecs = {}
            devSpecs["DevName"] = self.acqConfig.requestedDevice
            acquisitionSpecs = {}
            acquisitionSpecs["ParanoidMode"] = self.acqConfig.paranoidMode
            acquisitionSpecs["AcqMaxBufferLines"] = self.acqMaxBufferLines
            acquisitionSpecs["LengthToPass"] = 2000
            self.acquisitionThread = mp.Process(target=fillQueue_process, args=(devSpecs, acquisitionSpecs, self.shared_stopped, self.shared_return_list, self.shared_result_lock))
            self.acquisitionThread.daemon = True
            self.acquisitionThread.start()

        self.reenableStartButtonSignal.emit()
        self.acquisitionLoop()

        if (not self.acqConfig.isFakeAcquisition) and (not self.acqConfig.isFileAcquisition):
            self.acquisitionThread.join()

        self.acquisitionThread = None

        # self.closeAllInstruments()
        if not self.logFileObj.closed:
            self.logFileObj.close()

        print("Data acquisition function ended.")
        self.finishedSignal.emit()


    def acquisitionLoop(self):
        LastErrors = []
        while not self.stopped:
            # print("Starting acquisition cycle (batch read)...")

            #read batch from the queue
            self.dataStrQueue.clear()
            pull_startTime = time.time()
            while len(self.dataStrQueue) <= 0:
                self.pullBufferFromParallelProcess()
                self.dataStrQueue = self.readBatchFunction()
                QCoreApplication.processEvents()

                if self.stopped:
                    return

                if len(self.dataStrQueue) <= 0:
                    if abs(time.time() - pull_startTime) > self.pullForHowLongBeforeBreathing:
                        print("There has been no data to pull from the queue for " + str(
                            self.pullForHowLongBeforeBreathing) + " second(s). Breathing...")
                        self.healthyWait(self.pullBreatheTime)
                        pull_startTime = time.time()

                else:
                    pull_startTime = time.time()

            if not self.stopped:
                #parse the received batch
                self.dataB = DataBatch(self.acqConfig, self.dataStrQueue)
                self.batchParseErrorCheck = self.dataB.containsSevereError()
                #deal with errors of the current batch, if they exist
                if len(self.dataB.errorMsgs) > 0:
                    if self.dataB.errorMsgs != LastErrors: #print errors only if there's anything new
                        print("List of errors produced from analyzing data batch (won't be printed again if errors don't change):")
                        [print(err[ERROR_IDENTIFIER_SEVERITY] + ": " + err[ERROR_IDENTIFIER_MESSAGE]) for err in self.dataB.errorMsgs]
                        print("")

                    #set current errors as errors from last time for the next step
                    LastErrors = self.dataB.errorMsgs
                if self.batchParseErrorCheck is None:
                    try:
                        self.dataToPlot.appendData(self.dataB.dataToSave, self.dataB.startTime, self.dataB.samplingRate)
                    except Exception as e1:
                        self.dataError_ClearCollectedData(self.dataStrQueue)
                        self.emitError("A severe error occured in the acquired data: \n\n" + \
                                       "Data failed to parse possibly due to missing chunks. Exception: " + str(e1), False, True)
                    try:
                        self.postResultsSignal.emit(self.dataToPlot, self.dataCollected)
                    except Exception as e1:
                        self.dataError_ClearCollectedData(self.dataStrQueue)
                        self.emitError("Error while posting results to be plotted. Exception says: " + str(e1), False, True)


                    #append parsed batch to DataCollected object
                    appendStatus = self.dataCollected.appendData(self.dataB)
                    if not appendStatus[DataCollected.AppendData_ReturnSuccessKey]:
                        self.dataError_ClearCollectedData(self.dataStrQueue)
                        self.emitError("A severe error occured in the acquired data: \n\n" + appendStatus[DataCollected.AppendData_ReturnErrorMsgKey], False, True)

                    self.dataStrQueue.clear()
                    if appendStatus[DataCollected.AppendData_ReturnIsLastBatchKey]:
                        # move the successful file to the success folder
                        if self.acqConfig.isFileAcquisition:
                            try:
                                successFile = os.path.join(self.acqConfig.fileAcqPath, self.fileAcqLastFileRead)
                                newSuccessFilePath = os.path.join(self.acqConfig.fileAcqPath,
                                                                  self.fileAcqSubFolderForSuccessful,
                                                                  self.fileAcqLastFileRead)
                                os.rename(successFile, newSuccessFilePath)

                            except Exception as e:
                                msg = "Unable to move the succeeded file \"" + successFile + "\" to the new path \"" + newSuccessFilePath + "\". Exception message: " + str(e)
                                print(msg)
                                self.emitError(msg,True,True)

                else:
                    self.dataError_ClearCollectedData(self.dataStrQueue)
                    self.emitError("One or more severe errors were found. "
                                 "The error message says: \n\n" + str(self.batchParseErrorCheck[ERROR_IDENTIFIER_MESSAGE]),False,True)


    def readBatchLineByLine(self):
        QCoreApplication.processEvents()
        dataStrQueue = []
        try:
            # keep reading until the first line is found (@Header)
            while not self.stopped:
                self.line = self.readLine()
                self.writeDumpFileLine(self.line)
                # print(self.line)
                if self.line == DataBatch.d_startString:
                    # print("Acquiring batch, line by line...")
                    # print(self.line)
                    dataStrQueue.append(self.line)
                    break
            # after @Header is found, read lines
            while not self.stopped:
                QCoreApplication.processEvents()
                self.line = self.readLine()
                self.writeDumpFileLine(self.line)
                dataStrQueue.append(self.line)
                if self.line == DataBatch.d_endString:
                    # print(self.line)
                    break
                    # parse data

            return dataStrQueue

        except Exception as e1:
            print("Exception while trying to read. Error: " + str(e1))

    def readBatchFromDevice(self):
        QCoreApplication.processEvents()
        try:
            dataStrQueue = []
            # find the first line of a batch (@Header)
            startIndex = next((i for i in range(len(self.acqBuffer)) if self.acqBuffer[i] == DataBatch.d_startString), None)
            if startIndex is not None:
                endIndex = next((i for i in range(startIndex+1,len(self.acqBuffer)) if self.acqBuffer[i] == DataBatch.d_endString), None)
                if endIndex is not None:
                    dataStrQueue = self.acqBuffer[startIndex:endIndex+1]
                    #delete from the beginning of the buffer to the end, as the beginning is considered corrupt data
                    del self.acqBuffer[0:endIndex+1]

                else:
                    QCoreApplication.processEvents()
            else:
                QCoreApplication.processEvents()

            return dataStrQueue

        except Exception as e1:
            print("Exception while trying to read a batch. Exception says: " + str(e1))

    def openInstrument(self,instrumentName):
        try:
            self.openInstrumentObject = serial.Serial()
            self.openInstrumentObject.port = instrumentName
            self.openInstrumentObject.baudrate = 115200
            self.openInstrumentObject.bytesize = serial.EIGHTBITS #number of bits per bytes
            self.openInstrumentObject.parity   = serial.PARITY_ODD #set parity check: no parity
            self.openInstrumentObject.stopbits = serial.STOPBITS_ONE #number of stop bits
            self.openInstrumentObject.timeout  = 15        #non-block read
            self.openInstrumentObject.xonxoff  = True      #disable software flow control
            self.openInstrumentObject.rtscts   = False     #disable hardware (RTS/CTS) flow control
            self.openInstrumentObject.dsrdtr   = False     #disable hardware (DSR/DTR) flow control
            self.openInstrumentObject.writeTimeout = 2     #timeout for write

            self.openInstrumentObject.open()

            print("Instrument: " + instrumentName + " is open successfully.")
        except Exception as e:
            print("Error open serial port: " + str(e))
            print("Error while trying to open instrument: " + instrumentName)

    def closeInstrument(self):
        if (not self.acqConfig.isFakeAcquisition) and (not self.acqConfig.isFileAcquisition):
            try:
                self.openInstrumentObject.close()

            except Exception as e:
                print("error communicating...: " + str(e))
                print("Error while trying to close instrument: " + self.acqConfig.requestedDevice)

    def closeAllInstruments(self):
        print("Closing open instruments...")
        self.closeInstrument()
        print("Done closing instruments.")

