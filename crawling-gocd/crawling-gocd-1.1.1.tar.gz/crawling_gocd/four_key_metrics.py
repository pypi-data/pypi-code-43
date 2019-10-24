from crawling_gocd.calculate_domain import CalculateStrategyHandler, Result

class CalculateStrategyHandlerBase(CalculateStrategyHandler):
    def calculate(self, pipelines, results):
        for pipeline in pipelines:
            self.calculateSingle(pipeline, results)
        return results

    def calculateSingle(self, pipeline, results):
        for groupedStage in pipeline.calcConfig.groupedStages.items():
            value = self.valueOfSingleGroupedStage(pipeline.histories, groupedStage[1])
            results.append(Result(pipeline.name, self.getMetricName(), groupedStage[0], value))
    
    def getMetricName(self):
        return ""

    def valueOfSingleGroupedStage(self, pipelineHistories, stageNames):
        return 0


class DeploymentFrequency(CalculateStrategyHandlerBase):
    def getMetricName(self):
        return "DeploymentFrequency"

    def valueOfSingleGroupedStage(self, pipelineHistories, stageNames):
        return len(list(filter(lambda history: history.hasStatusInStages(stageNames), pipelineHistories)))

class ChangeFailPercentage(CalculateStrategyHandlerBase):
    def getMetricName(self):
        return "ChangeFailPercentage"

    def valueOfSingleGroupedStage(self, pipelineHistories, stageNames):
        runCount = len(list(filter(lambda history: history.hasStatusInStages(stageNames), pipelineHistories)))
        failedCount = len(list(filter(lambda history: history.hasFailedInStages(stageNames), pipelineHistories)))

        if runCount == 0:
            return "N/A"

        return "{:.1%}".format(failedCount / runCount)

class ChangeFailPercentage_ignoredContinuousFailed(CalculateStrategyHandlerBase):
    def getMetricName(self):
        return "ChangeFailPercentage_2"

    def valueOfSingleGroupedStage(self, pipelineHistories, stageNames):
        runCount = len(list(filter(lambda history: history.hasStatusInStages(stageNames), pipelineHistories)))
        
        pipelineHistories.sort(key=lambda history: history.label)
        failedCount, lastIsFailed = 0, False
        for history in pipelineHistories:
            if history.hasFailedInStages(stageNames) and lastIsFailed == False:
                failedCount += 1
                lastIsFailed = True
            
            if history.allPassedInStages(stageNames) and lastIsFailed == True:
                lastIsFailed = False

        if runCount == 0:
            return "N/A"

        return "{:.1%}".format(failedCount / runCount)

class MeanTimeToRestore(CalculateStrategyHandlerBase):
    def getMetricName(self):
        return "MeanTimeToRestore"

    def valueOfSingleGroupedStage(self, pipelineHistories, stageNames):
        restoreTotalTime, failedCount, latestFailedScheduled = 0, 0, 0

        pipelineHistories.sort(key=lambda history: history.scheduledTimestamp)
        for history in pipelineHistories:
            if history.hasFailedInStages(stageNames) and latestFailedScheduled == 0:
                failedCount += 1
                latestFailedScheduled = history.scheduledTimestamp

            if history.allPassedInStages(stageNames) and latestFailedScheduled != 0:
                restoreTotalTime += history.scheduledTimestamp - latestFailedScheduled
                latestFailedScheduled = 0
        
        if latestFailedScheduled != 0 and failedCount > 0:
            failedCount -= 1

        if failedCount == 0:
            return "N/A"

        return "%s(mins)" % round(restoreTotalTime / failedCount / 1000 / 60)


    
