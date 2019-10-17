import yaml
import sys
import logging
from datetime import datetime, timedelta
from crawling_gocd.gocd_domain import Pipeline
from crawling_gocd.calculate_domain import InputsCalcConfig


class InputsParser:
    def __init__(self, filePath):
        self.inputTimeParser = InputTimeParser()
        with open(filePath, 'r') as stream:
            try:
                self.inputs = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print("yaml file read failed, {}", exc)

    def parsePipelineConfig(self):
        globalTimeRange = self.getGlobalTimeRange()
        logging.info("global_start_time: {}, global_end_time: {}".format(globalTimeRange.startTime, globalTimeRange.endTime))

        return list(map(lambda pipeline: self.mapSinglePipeline(
            pipeline, globalTimeRange.startTime, globalTimeRange.endTime), self.inputs["pipelines"]))

    def mapSinglePipeline(self, pipelineConfig, globalStartTime, globalEndTime):
        inputCalcConfig = InputsCalcConfig(pipelineConfig["calc_grouped_stages"], pipelineConfig.get(
            "startTime", globalStartTime), pipelineConfig.get("endTime", globalEndTime))
        return Pipeline(pipelineConfig["name"], inputCalcConfig)

    def outputCustomizeClazz(self):
        absoluteClassName = self.inputs.get("output_class_name", None)
        if absoluteClassName == None:
            return getattr(sys.modules["crawling_gocd.outputs"], "OutputCsv")

        partitions = absoluteClassName.rpartition(".")
        return getattr(sys.modules[partitions[0]], partitions[2])

    def getMetrics(self):
        metrics = self.inputs["metrics"]
        four_key_metrics = metrics.get("four_key_metrics", [])
        return list(map(lambda m: getattr(sys.modules["crawling_gocd.four_key_metrics"], m), four_key_metrics))
    
    def getGlobalTimeRange(self):
        return self.inputTimeParser.parse(self.inputs.get("global", {}))


class InputTimeParser:
    def parse(self, globalDict):
        type = globalDict.get("time_type", None)
        if type == "cycle":
            return self.getCycleTimeRange(globalDict)
        else:
            return self.getFixTimeRange(globalDict)

    def getFixTimeRange(self, globalDict):
        startTime = globalDict.get("start_time", datetime(1970, 1, 1))
        endTime = globalDict.get("end_time", datetime.now())
        return TimeRange(startTime, endTime)

    def getCycleTimeRange(self, globalDict):
        weekNum = globalDict.get("cycle_weeks")
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        endTime = now - timedelta(days = now.weekday())
        startTime = endTime - timedelta(days = 7 * weekNum)
        return TimeRange(startTime, endTime - timedelta(seconds = 1))

class TimeRange:
    def __init__(self, startTime, endTime):
        self.startTime = startTime
        self.endTime = endTime
