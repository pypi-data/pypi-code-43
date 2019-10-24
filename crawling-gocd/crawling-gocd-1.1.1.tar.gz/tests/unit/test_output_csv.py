import unittest
import csv
from datetime import datetime
from crawling_gocd.outputs import OutputCsv
from crawling_gocd.calculate_domain import GlobalTimeRange
import tests.unit.test_fixture as fixture

class OutputCsvTest(unittest.TestCase):
    def setUp(self):
        self.outputCsv = OutputCsv()
        self.globalTimeRange = GlobalTimeRange(datetime(2019, 10, 15, 0), datetime(2019, 10, 17, 23, 59, 59))
        self.fileName = "crawling_output_20191015000000_20191017235959.csv"

    def test_output(self):
        self.outputCsv.output(fixture.getResults(), self.globalTimeRange)
        with open(self.fileName, newline="") as csvFile:
            reader = csv.reader(csvFile)
            self.assertEqual(str(list(reader)), "[['pipelineName', 'groupName', 'ChangeFailPercentage', 'DeploymentFrequency', 'MeanTimeToRestore'], ['account-management-normal-master', 'ci', '5.5%', '145', '56(mins)'], ['account-management-normal-master', 'qa', '4.9%', '61', '53(mins)']]")