import unittest

from click.testing import CliRunner

from DKCloudCommand.tests.integration_tests.BaseTestCloud import BaseTestCloud, EMAIL_SUFFIX
from DKCloudCommand.cli.__main__ import dk


class TestIntegrationBasic(BaseTestCloud):

    def test_alias(self):
        runner = CliRunner()
        result = runner.invoke(dk, ["--help"])
        rv = result.output
        self.assertTrue('kitchen-create (kc)' in rv)
        self.assertTrue('orderrun-delete (ord)' in rv)

        result = runner.invoke(dk, ["kl"])
        rv = result.output
        self.assertTrue('CLI-Top' in rv)

    def test_user_info(self):
        runner = CliRunner()
        result = runner.invoke(dk, ["user-info"])

        self.assertEqual(0, result.exit_code, result.output)
        splitted_output = result.output.split('\n')

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'Name:' in splitted_output[index] and EMAIL_SUFFIX in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'Email:' in splitted_output[index] and EMAIL_SUFFIX in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if 'Customer Name:' in splitted_output[index] and 'DataKitchen' in splitted_output[
                        index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                if 'Support Email:' in splitted_output[
                        index] and '@datakitchen.io' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 5:
                if 'Role:' in splitted_output[index] and ('ADMIN' in splitted_output[index]
                                                          or 'IT' in splitted_output[index]):
                    stage += 1
                index += 1
                continue
            index += 1

        self.assertEqual(6, stage)

    def test_config_list(self):
        runner = CliRunner()
        result = runner.invoke(dk, ["config-list"])

        self.assertEqual(0, result.exit_code, result.output)
        splitted_output = result.output.split('\n')

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'Current configuration is ...' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'Config Location:' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if 'General Config Location:' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                if 'Username:' in splitted_output[index] and EMAIL_SUFFIX in splitted_output[index]:
                    stage += 1  # skip-secret-check
                index += 1
                continue
            if stage == 5:
                if 'Password:' in splitted_output[index]:
                    stage += 1  # skip-secret-check
                index += 1
                continue
            if stage == 6:
                if 'Cloud IP:' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 7:
                if 'Cloud Port:' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 8:
                if 'Merge Tool:' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 9:
                if 'Diff Tool:' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            index += 1

        self.assertEqual(10, stage)


if __name__ == '__main__':
    unittest.main()
