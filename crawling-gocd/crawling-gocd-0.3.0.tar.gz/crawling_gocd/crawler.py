import time
import sys
import itertools
import logging
from operator import attrgetter
from datetime import datetime
from requests_html import HTMLSession
from crawling_gocd.gocd_domain import PipelineHistory, StageHistory


class Crawler:
    def __init__(self, organization):
        self.path = "./data"
        self.organization = organization
        self.session = HTMLSession()
        self.session.headers.update(
            {"Authorization": self.organization.getBasicAuth()})

    def getResource(self, url):
        return self.session.get(url=url).json()

    def generatePipelineHistoryUrl(self, pipelineName, start=0):
        url = "https://{}/go/pipelineHistory.json?pipelineName={}".format(
            self.organization.site, pipelineName)
        if start != 0:
            url = url + "&start={}".format(start)
        return url

    def getPipelineHistories(self, pipelineName, startTime, endTime):
        if startTime > endTime:
            return []
        offset, data = 0, []
        while True:
            url = self.generatePipelineHistoryUrl(pipelineName, offset)
            logging.debug("get url {}".format(url))
            try:
                ret = self.getResource(url)
                pipelineHistoriesList = list(
                    map(lambda x: x["history"], ret["groups"]))
                pipelineHistories = list(itertools.chain(*pipelineHistoriesList))

                if len(pipelineHistories) == 0:
                    break

                data = data + self.filterPipelinesPerPage(
                        pipelineHistories, startTime, endTime)

                if self.canStop(pipelineHistories, startTime):
                    break

                offset = ret["start"] + ret["perPage"]
            except:
                logging.error("failed {} \n".format(url), sys.exc_info())
                break
        return data

    def filterPipelinesPerPage(self, pipelines, startTime, endTime):
        return list(filter(lambda x: datetime.timestamp(startTime) <= (int(x["scheduled_timestamp"]) / 1000) <= datetime.timestamp(endTime), pipelines))

    def canStop(self, pipelines, startTime):
        scheduledTimestatmps = list(
            map(lambda x: int(x["scheduled_timestamp"]) / 1000, pipelines))
        return (min(scheduledTimestatmps)) < datetime.timestamp(startTime)

class CrawlingDataMapper:
    def mapPipelineHistory(self, pipelineHistories):
        return list(map(lambda history: PipelineHistory(
            history["counterOrLabel"], history["scheduled_timestamp"], self.mapPipelineHistoryStage(history["stages"])), pipelineHistories))

    def mapPipelineHistoryStage(self, stageArray):
        return list(map(lambda stage: StageHistory(stage["stageId"], stage["stageName"], stage["stageStatus"]), stageArray))
