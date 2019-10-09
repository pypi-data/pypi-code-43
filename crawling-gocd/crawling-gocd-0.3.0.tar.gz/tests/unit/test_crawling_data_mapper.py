import unittest
import json
import tests.unit.test_fixture as fixture
from crawling_gocd.crawler import CrawlingDataMapper
from crawling_gocd.gocd_domain import PipelineHistory, StageHistory

class CrawlingDataMapperTest(unittest.TestCase):
    def setUp(self):
        filePage1 = "tests/unit/resources/pipeline_history_pg_1.json"
        self.pipelineHistories = fixture.getPipelineHistories(filePage1)
        self.mapper = CrawlingDataMapper()

    def test_should_map_domain_object_correctly(self):
        result = self.mapper.mapPipelineHistory(self.pipelineHistories)
        givenData = PipelineHistory("226", "1567335377736", [
            StageHistory("217936", "code-scan", "Passed"),
            StageHistory("217937", "test-integration", "Passed"),
            StageHistory("217939", "build", "Passed"),
            StageHistory("217982", "flyway-qa", "Passed"),
            StageHistory("217983", "deploy-qa", "Passed")
        ])
        self.assertEqual(str(result[0]), str(givenData))

if __name__ == '__main__':
    unittest.main()