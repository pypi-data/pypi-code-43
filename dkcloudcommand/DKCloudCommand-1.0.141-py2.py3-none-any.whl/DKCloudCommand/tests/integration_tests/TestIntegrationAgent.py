import unittest

from click.testing import CliRunner

from DKCloudCommand.tests.integration_tests.BaseTestCloud import BaseTestCloud
from DKCloudCommand.cli.__main__ import dk


class TestIntegrationAgent(BaseTestCloud):

    def test_agent_status(self):
        runner = CliRunner()
        result = runner.invoke(dk, ["agent-status"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Agent is Online' in result.output)
        self.assertTrue('Total available memory:' in result.output)
        self.assertTrue('Total available disk space:' in result.output)


if __name__ == '__main__':
    unittest.main()
