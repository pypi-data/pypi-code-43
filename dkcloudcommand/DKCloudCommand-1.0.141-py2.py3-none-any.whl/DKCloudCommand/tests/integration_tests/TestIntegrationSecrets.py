import time
import unittest

from click.testing import CliRunner

from DKCloudCommand.tests.integration_tests.BaseTestCloud import (
    BaseTestCloud,
    VAULT_ADDR,
    VAULT_ROOT_TOKEN,
)
from DKCloudCommand.cli.__main__ import dk


class TestIntegrationSecrets(BaseTestCloud):

    def test_secrets(self):
        debug = False
        runner = CliRunner()

        result = runner.invoke(dk, ["secret-write", "cli-unit-tests/value='hello'", "--yes"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Secret written.' in result.output)

        result = runner.invoke(dk, ["secret-list"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        if debug:
            print(result.output)
        self.assertTrue('s3_schema/' in result.output)
        self.assertTrue('cli-unit-tests/' in result.output)

        result = runner.invoke(dk, ["secret-list"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        self.assertTrue('vault://cli-unit-tests/value' in result.output)

        result = runner.invoke(dk, ["secret-exists", "cli-unit-tests/value"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('True' in result.output)

        result = runner.invoke(dk, ["secret-delete", "cli-unit-tests/value", "--yes"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Secret deleted.' in result.output)

        result = runner.invoke(dk, ["secret-list"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        self.assertTrue('s3_schema/' in result.output)
        self.assertTrue('cli-unit-tests/' not in result.output)

        result = runner.invoke(dk, ["secret-list"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        self.assertTrue('vault://cli-unit-tests/value' not in result.output)

        result = runner.invoke(dk, ["secret-exists", "cli-unit-tests/value"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('False' in result.output)

    def test_secrets_kitchen_vault(self):
        debug = False
        runner = CliRunner()

        # Prepare test kitchen
        parent_kitchen = 'CLI-Top'
        new_kitchen = 'test_secrets_kitchen_vault-CLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])
        time.sleep(BaseTestCloud.SLEEP_TIME)

        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        runner.invoke(dk, ['vault-delete', '-k', new_kitchen, '--yes'])

        # Try to write a secret without vault config for the new kitchen, and fail
        result = runner.invoke(
            dk, ["secret-write", "-k", new_kitchen, "cli-unit-tests/value='hello'", "--yes"]
        )
        self.assertEqual(1, result.exit_code, result.output)
        self.assertTrue('No vault service configured for kitchen %s' % new_kitchen in result.output)

        # configure kitchen vault
        result = runner.invoke(dk, ["vault-info"])
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('---- global config ----')
        assertions.append(' DataKitchen default')
        self.assert_response(assertions, result.output)

        result_output = str(result.output)
        the_url_index = result_output.find(' url')
        result_output[the_url_index:].strip()

        # configure kitchen vault
        result = runner.invoke(
            dk, [
                "vault-config", "-k", new_kitchen, "--prefix", new_kitchen, "--service", "custom",
                "--url", VAULT_ADDR, "--token", VAULT_ROOT_TOKEN, "--yes"
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Setting the vault info')
        assertions.append('Done.')
        self.assert_response(assertions, result.output)

        # Try secret write once again
        result = runner.invoke(
            dk, ["secret-write", "-k", new_kitchen, "cli-unit-tests/value='hello'", "--yes"]
        )
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Writing secret')
        assertions.append('Secret written.')
        self.assert_response(assertions, result.output)

        result = runner.invoke(dk, ["secret-list", "-k", new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        if debug:
            print(result.output)
        self.assertTrue('cli-unit-tests/value' in result.output)

        # secret list kitchen and global, mixed mode
        result = runner.invoke(dk, ["secret-list", "-g", "-k", new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        if debug:
            print(result.output)
        assertions = list()
        assertions.append('Getting the list of secrets')
        assertions.append('---- global secrets ----')
        assertions.append(' vault://s3_schema/bucket')
        assertions.append('---- %s secrets ----' % new_kitchen)
        assertions.append(' vault://cli-unit-tests/value')

        self.assert_response(assertions, result.output)
        self.assertTrue('cli-unit-tests/value' in result.output)

        result = runner.invoke(dk, ["secret-exists", "-k", new_kitchen, "cli-unit-tests/value"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('True (found in kitchen vault)' in result.output)

        result = runner.invoke(
            dk, ["secret-delete", "-k", new_kitchen, "cli-unit-tests/value", "--yes"]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Deleting secret' in result.output)
        self.assertTrue('Secret deleted.' in result.output)

        result = runner.invoke(dk, ["secret-list", "-k", new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        self.assertTrue('cli-unit-tests/value' not in result.output)

        result = runner.invoke(dk, ["secret-exists", "-k", new_kitchen, "cli-unit-tests/value"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('False' in result.output)

    def test_vault_global(self):
        runner = CliRunner()
        result = runner.invoke(dk, ["vi"])
        self.assertEqual(0, result.exit_code, result.output)

        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('---- global config ----')
        assertions.append(' DataKitchen default')
        self.assert_response(assertions, result.output)

    def test_vault_kitchen(self):
        # setup, create kitchen
        parent_kitchen = 'CLI-Top'
        new_kitchen = 'test_vault_info_kitchen-CLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        runner = CliRunner()
        runner.invoke(dk, ['vault-delete', '-k', new_kitchen, '--yes'])
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        # get kitchen vault before any config
        result = runner.invoke(dk, ["vi", "-k", new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('No vault service configured for kitchen %s' % new_kitchen)
        self.assert_response(assertions, result.output)

        # configure kitchen vault
        result = runner.invoke(
            dk, [
                "vault-config", "-k", new_kitchen, "--prefix", "my-prefix", "--private", "True",
                "--service", "custom", "--token", "my-token", "--inheritable", "True", "--url",
                "my-url"
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Setting the vault info')
        assertions.append('Done.')
        self.assert_response(assertions, result.output)

        # get kitchen vault after config, with gobal as well
        result = runner.invoke(dk, ["vi", "-g", "-k", new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('---- global config ----')
        assertions.append(' DataKitchen default')
        assertions.append('---- %s config ----' % new_kitchen)
        assertions.append(' prefix\t\t\tmy-prefix')
        assertions.append(' private\t\tTrue')
        assertions.append(' service\t\tcustom')
        assertions.append(' token\t\t\t******')
        assertions.append(' url\t\t\tmy-url')
        assertions.append(' inheritable\t\tTrue')
        self.assert_response(assertions, result.output)

        # delete kitchen vault
        result = runner.invoke(dk, ['vault-delete', '-k', new_kitchen, '--yes'])
        self.assertEqual(0, result.exit_code, result.output)

        assertions = list()
        assertions.append('Deleting the vault configuration for kitchen %s' % new_kitchen)
        assertions.append('Done.')
        self.assert_response(assertions, result.output)

        # get kitchen vault after delete, with global as well
        result = runner.invoke(dk, ["vi", "-g", "-k", new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('---- global config ----')
        assertions.append(' DataKitchen default')
        assertions.append('No vault service configured for kitchen %s' % new_kitchen)
        self.assert_response(assertions, result.output)

        self.assertFalse('inheritable' in result.output)

        # cleanup
        runner.invoke(dk, ['vault-delete', '-k', new_kitchen, '--yes'])
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])


if __name__ == '__main__':
    unittest.main()
