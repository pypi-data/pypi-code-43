from datetime import datetime

class InputsCalcConfig:
    def __init__(self, groupedStages: dict, startTime: datetime, endTime: datetime):
        self.groupedStages = groupedStages
        self.startTime = startTime
        self.endTime = endTime

    def __str__(self):
        return "{ groupedStages: %s, startTime: %s, endTime: %s }" % (str(self.groupedStages), str(self.startTime), str(self.endTime))

class CalculateStrategyHandler:
    def calculate(self, pipelines, results):
        return []

class GlobalTimeRange:
    def __init__(self, startTime, endTime):
        self.startTime = startTime
        self.endTime = endTime

class Result:
    def __init__(self, pipelineName, metricsName, groupName, value):
        self.pipelineName = pipelineName
        self.metricsName = metricsName
        self.groupName = groupName
        self.value = value

    def __str__(self):
        return "{ pipelineName: %s, metricsName: %s, groupName: %s, value: %s }" % (self.pipelineName, self.metricsName, self.groupName, self.value) 