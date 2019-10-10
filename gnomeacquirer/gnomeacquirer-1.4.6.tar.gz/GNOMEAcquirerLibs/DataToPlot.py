import matplotlib.dates as mdates

import datetime
import copy

#This class is a quick class that could accumulate data from DataBatch to be plotted
class DataToPlot:
    def __init__(self):
        self.dataToSave = {}
        self.MaxSizeToPlot = 10000

    def appendData(self, dataToSave, startTime, samplingRate):
        self.startTime = startTime
        self.samplingRate = samplingRate
        timeArray = []
        timestep = datetime.timedelta(microseconds=float(10 ** 6) / float(samplingRate))
        t0 = copy.deepcopy(startTime)

        # get a random element to get array size
        for self.tmpDSName in dataToSave:
            pass

        # create time array
        for i in range(len(dataToSave[self.tmpDSName])):
            timeArray.append(mdates.date2num(t0))
            t0 += timestep

        if len(dataToSave) == len(self.dataToSave):
            self.dataToPlot_timeAxis = self.dataToPlot_timeAxis + timeArray
            for self.tmpDataset in dataToSave:
                self.dataToSave[self.tmpDataset] = self.dataToSave[self.tmpDataset] + dataToSave[
                    self.tmpDataset].tolist()
            if len(self.dataToSave[self.tmpDataset]) > self.MaxSizeToPlot:
                self.dataToPlot_timeAxis = self.dataToPlot_timeAxis[-self.MaxSizeToPlot:]
                for el in self.dataToSave:
                    self.dataToSave[el] = self.dataToSave[el][-self.MaxSizeToPlot:]
        else:
            self.dataToSave = dataToSave
            for self.tmpDataset in dataToSave:
                self.dataToSave[self.tmpDataset] = dataToSave[self.tmpDataset].tolist()
            self.dataToPlot_timeAxis = timeArray
