import os
from crawling_gocd.inputs_parser import InputsParser
from crawling_gocd.gocd_domain import Organization
from crawling_gocd.crawler import Crawler, CrawlingDataMapper
from crawling_gocd.calculator import Calculator
from crawling_gocd.four_key_metrics import DeploymentFrequency, ChangeFailPercentage, ChangeFailPercentage_ignoredContinuousFailed, MeanTimeToRestore

class Portal:
    def __init__(self):
        self.inputsParser = InputsParser("crawling-gocd.yaml")
        self.calculator = self.assembleCalculator()
        self.output = self.newOutputInstance()
        self.crawler = self.newCrawler()
        self.globalTimeRange = self.getGlobalTimeRange()

    def serve(self):
        inputPipelines = self.inputsParser.parsePipelineConfig()
        pipelineWithFullData = list(map(lambda pipeline: self.crawlingSinglePipeline(
            pipeline, self.crawler), inputPipelines))

        results = self.calculator.work(pipelineWithFullData, [])
        self.output.output(results)

    def crawlingSinglePipeline(self, pipeline, crawler):
        mapper = CrawlingDataMapper()
        histories = crawler.getPipelineHistories(
            pipeline.name, pipeline.calcConfig.startTime, pipeline.calcConfig.endTime)
        pipeline.histories = mapper.mapPipelineHistory(histories)
        return pipeline

    def newCrawler(self):
        orgnization = Organization(
            os.environ["GOCD_SITE"], os.environ["GOCD_USER"], os.environ["GOCD_PASSWORD"])
        return Crawler(orgnization)

    def assembleCalculator(self):
        inputMetricClasses = self.inputsParser.getMetrics()
        handlers = list(map(lambda clazz: clazz(), inputMetricClasses))
        return Calculator(handlers)

    def newOutputInstance(self):
        inputOutputClass = self.inputsParser.outputCustomizeClazz()
        return inputOutputClass()

    def getGlobalTimeRange(self):
        return self.inputsParser.getGlobalTimeRange()
