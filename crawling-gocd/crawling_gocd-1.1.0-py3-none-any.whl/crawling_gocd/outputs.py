import csv
import itertools
import logging
from crawling_gocd.calculate_domain import Result


class Output:
    def output(self, results, globalTimeRange):
        pass

class OutputCsv(Output):
    def __init__(self):
        self.fieldNames = ["pipelineName", "groupName"]
        self.fileNameTemplate = "crawling_output_{}_{}.csv"

    def output(self, results, globalTimeRange):
        metricNames = set(list(map(lambda result: result.metricsName, results)))
        self.fieldNames += sorted(metricNames)
        formatOutputs = self.convertToFormatOutputs(results)

        fileName = self.generateCvsFileName(globalTimeRange)
        with open(fileName, mode="w") as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=self.fieldNames, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(formatOutputs)
        logging.info("The metrics results see the {} file".format(fileName))

    def convertToFormatOutputs(self, results):
        keyFunction = lambda r: (r.pipelineName, r.groupName)
        results = sorted(results, key=keyFunction)
        
        formatOutputs = []
        for k, group in itertools.groupby(results, keyFunction):
            output = {"pipelineName": k[0], "groupName": k[1]}
            
            for t in sorted(group, key=lambda t: t.metricsName):
                output.update({t.metricsName: t.value})
            formatOutputs.append(output)
        return formatOutputs

    def generateCvsFileName(self, globalTimeRange):
        timeFormater = "%Y%m%d%H%M%S"
        start = globalTimeRange.startTime.strftime(timeFormater)
        end = globalTimeRange.endTime.strftime(timeFormater)
    
        return self.fileNameTemplate.format(start, end)
