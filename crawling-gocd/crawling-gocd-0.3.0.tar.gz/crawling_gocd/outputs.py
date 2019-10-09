import csv
import itertools
import logging
from crawling_gocd.calculate_domain import Result


class Output:
    def output(self, results):
        pass

class OutputCsv(Output):
    def __init__(self):
        self.fieldNames = ["pipelineName", "groupName"]
        self.fileName = "crawling_output.csv"

    def output(self, results):
        metricNames = set(list(map(lambda result: result.metricsName, results)))
        self.fieldNames += sorted(metricNames)
        formatOutputs = self.convertToFormatOutputs(results)

        with open(self.fileName, mode="w") as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=self.fieldNames, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(formatOutputs)
        logging.info("The metrics results see the crawling_output.csv file")

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
