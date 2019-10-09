import unittest
import csv
from crawling_gocd.outputs import OutputCsv
import tests.unit.test_fixture as fixture

class OutputCsvTest(unittest.TestCase):
    def setUp(self):
        self.outputCsv = OutputCsv()
        self.fileName = "crawling_output.csv"

    def test_output(self):
        self.outputCsv.output(fixture.getResults())
        with open(self.fileName, newline="") as csvFile:
            reader = csv.reader(csvFile)
            self.assertEqual(str(list(reader)), "[['pipelineName', 'groupName', 'ChangeFailPercentage', 'DeploymentFrequency', 'MeanTimeToRestore'], ['account-management-normal-master', 'ci', '5.5%', '145', '56(mins)'], ['account-management-normal-master', 'qa', '4.9%', '61', '53(mins)']]")