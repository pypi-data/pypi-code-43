import unittest
import json
import datetime
import tests.unit.test_fixture as fixture
from crawling_gocd.four_key_metrics import DeploymentFrequency, ChangeFailPercentage, MeanTimeToRestore
from crawling_gocd.gocd_domain import Pipeline
from crawling_gocd.crawler import CrawlingDataMapper
from crawling_gocd.calculate_domain import InputsCalcConfig


class DeploymentFrequencyTest(unittest.TestCase):
    def setUp(self):
        self.pipeline = fixture.generatePipeline()

    def test_should_calculate_deployment_frequency_correctly(self):
        handler = DeploymentFrequency()
        results = handler.calculate([self.pipeline], [])
        self.assertEqual("".join(str(x) for x in results),
                         "{ pipelineName: go_service, metricsName: DeploymentFrequency, groupName: qa, value: 6 }")


class ChangeFailPercentageTest(unittest.TestCase):
    def setUp(self):
        self.pipeline = fixture.generatePipeline()

    def test_should_calculate_change_fail_percentage_correctly(self):
        handler = ChangeFailPercentage()
        results = handler.calculate([self.pipeline], [])
        self.assertEqual("".join(str(x) for x in results),
                         "{ pipelineName: go_service, metricsName: ChangeFailPercentage, groupName: qa, value: 16.7% }")

class MeanTimeToRestoreTest(unittest.TestCase):
    def setUp(self):
        self.pipeline = fixture.generatePipeline()

    def test_should_calculate_mean_time_to_restore_correctly(self):
        handler = MeanTimeToRestore()
        results = handler.calculate([self.pipeline], [])
        self.assertEqual("".join(str(x) for x in results),
                         "{ pipelineName: go_service, metricsName: MeanTimeToRestore, groupName: qa, value: 69(mins) }")
