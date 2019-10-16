import unittest
import json
from freezegun import freeze_time
from datetime import datetime
from crawling_gocd.inputs_parser import InputsParser, InputTimeParser
from crawling_gocd.outputs import Output, OutputCsv


class InputsParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = InputsParser("tests/unit/resources/crawling-gocd.yaml")

    def test_should_generate_inputs_object_correctly_by_fix_time_range(self):
        result = self.parser.parsePipelineConfig()
        self.assertEqual("".join(str(x) for x in result),
                         "{ name: accounting-plus-master, calcConfig: { groupedStages: {'ci': ['code-scan', 'test-integration', 'build'], 'qa': ['flyway-qa', 'deploy-qa']}, startTime: 2019-07-01 00:00:00, endTime: 2019-08-12 23:59:59 } }")

    @freeze_time("2019-10-25 08:00:00")
    def test_should_generate_inputs_object_correctly_by_cycle_time_range(self):
        self.parser.inputs["global"].update(
            {
               "time_type": "cycle",
               "cycle_weeks": 2
            }
        )
        result = self.parser.parsePipelineConfig()
        self.assertEqual("".join(str(x) for x in result),
                         "{ name: accounting-plus-master, calcConfig: { groupedStages: {'ci': ['code-scan', 'test-integration', 'build'], 'qa': ['flyway-qa', 'deploy-qa']}, startTime: 2019-10-07 00:00:00, endTime: 2019-10-20 23:59:59 } }")

    def test_should_return_customize_type_class(self):
        self.parser.inputs.update(
            {"output_class_name": "crawling_gocd.outputs.Output"})
        clazz = self.parser.outputCustomizeClazz()
        self.assertTrue(isinstance(clazz(),  Output))

    def test_should_return_default_type_class(self):
        clazz = self.parser.outputCustomizeClazz()
        self.assertTrue(isinstance(clazz(), OutputCsv))

    def test_should_return_metrics_class(self):
        metricsClazz = self.parser.getMetrics()
        self.assertEqual(str(
            metricsClazz), "[<class 'crawling_gocd.four_key_metrics.DeploymentFrequency'>, <class 'crawling_gocd.four_key_metrics.ChangeFailPercentage'>]")


class InputTimeParserTest(unittest.TestCase):

    @freeze_time("2019-10-07 19:00:00")
    def test_should_return_correctly_cycle_start_time_end_time(self):
        globalDict = {
            "time_type": "cycle",
            "cycle_weeks": 2
        }
        parser = InputTimeParser()
        (globalStartTime, globalEndTime) = parser.parse(globalDict)
        print(globalStartTime, globalEndTime)
        self.assertEqual(str(globalStartTime), "2019-09-23 00:00:00")
        self.assertEqual(str(globalEndTime), "2019-10-06 23:59:59")

    def test_should_return_correctly_fix_start_time_end_time(self):
        globalDict = {
            "time_type": "fix",
            "start_time": "2019-09-30 01:00:00", 
            "end_time": "2019-10-13 23:59:00"
        }
        parser = InputTimeParser()
        (globalStartTime, globalEndTime) = parser.parse(globalDict)
        print(globalStartTime, globalEndTime)
        self.assertEqual(str(globalStartTime), "2019-09-30 01:00:00")
        self.assertEqual(str(globalEndTime), "2019-10-13 23:59:00")

    
