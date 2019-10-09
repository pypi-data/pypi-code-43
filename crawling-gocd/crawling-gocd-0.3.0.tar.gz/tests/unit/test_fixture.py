import json
import itertools
import datetime
from crawling_gocd.crawler import CrawlingDataMapper
from crawling_gocd.gocd_domain import Pipeline
from crawling_gocd.calculate_domain import InputsCalcConfig
from crawling_gocd.calculate_domain import Result

def getPipelineHistories(filePath):
    with open(filePath, 'r') as f:
        page1 = json.load(f)
    pipelineHistoriesList = list(map(lambda x: x["history"], page1["groups"]))
    return list(itertools.chain(*pipelineHistoriesList))

def generatePipeline():
    filePage1 = "tests/unit/resources/pipeline_history_pg_1.json"
    pipelineHistories = getPipelineHistories(filePage1)
    mapper = CrawlingDataMapper()

    pipeline = Pipeline("go_service", InputsCalcConfig({"qa": ["flyway-qa", "deploy-qa"]}, datetime.datetime(1970, 1, 1), datetime.datetime.now()))
    pipeline.setHistories(mapper.mapPipelineHistory(pipelineHistories))
    return pipeline

def getResults():
    return [
        Result("account-management-normal-master", "DeploymentFrequency", "ci", "145"),
        Result("account-management-normal-master", "DeploymentFrequency", "qa", "61"),
        Result("account-management-normal-master", "ChangeFailPercentage", "ci", "5.5%"),
        Result("account-management-normal-master", "ChangeFailPercentage", "qa", "4.9%"),
        Result("account-management-normal-master", "MeanTimeToRestore", "ci", "56(mins)"),
        Result("account-management-normal-master", "MeanTimeToRestore", "qa", "53(mins)"),
    ]