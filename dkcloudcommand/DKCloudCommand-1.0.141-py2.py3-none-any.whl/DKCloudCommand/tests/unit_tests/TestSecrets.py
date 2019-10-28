import requests
import shutil

from mock import patch
from click.testing import CliRunner

from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.cli.__main__ import Backend
from DKCloudCommand.modules.DKCloudAPI import DKCloudAPI
from DKCloudCommand.modules.DKCloudCommandRunner import DKCloudCommandRunner
from DKCloudCommand.modules.DKPathHelper import DKPathHelper
from DKCloudCommand.tests.DKCommonUnitTestSettings import DKCommonUnitTestSettings
from DKCloudCommand.tests.DKCommonUnitTestSettings import MockBackendResponse
from DKCommon.Constants import VAULT_GLOBAL


class TestSecrets(DKCommonUnitTestSettings):

    # ----------------------- setup and teardown --------------------------------------------------
    def setUp(self):
        self.temp_dir = None
        if DKPathHelper.is_windows_os():
            TestSecrets._TEMP_FILE_LOCATION = 'c:\\temp'
        else:
            TestSecrets._TEMP_FILE_LOCATION = '/var/tmp'

    def tearDown(self):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ----------------------- vault-info ----------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_info_global(self, backend, dkcloudapi_login):
        # Config
        runner = CliRunner()
        mock_response = {
            "config": {
                VAULT_GLOBAL: {
                    "url": None,
                    "token": None,
                    "service": "default",
                    "prefix": None,
                    "private": None
                }
            }
        }

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["vault-info"])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('---- global config ----')
        assertions.append(' DataKitchen default')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_info_global_disabled(self, backend, dkcloudapi_login):
        # Config
        runner = CliRunner()
        mock_response = {"config": {VAULT_GLOBAL: {"disabled": True}}}

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["vault-info"])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('---- global config ----')
        assertions.append(' disabled')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_info_kitchen(self, backend, dkcloudapi_login):
        # Config
        kitchen_name = 'my-kitchen'
        runner = CliRunner()
        mock_response = {
            "config": {
                VAULT_GLOBAL: {
                    "url": None,
                    "token": None,
                    "service": "default",
                    "prefix": None,
                    "private": None
                },
                kitchen_name: {
                    "url": "my-url",
                    "token": "my-token",
                    "service": "my-service",
                    "prefix": "my-prefix",
                    "private": "my-private",
                    "inheritable": True
                }
            }
        }

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["vault-info", "-k", kitchen_name])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('---- %s config ----' % kitchen_name)
        assertions.append(' prefix			my-prefix')
        assertions.append(' private		my-private')
        assertions.append(' service		my-service')
        assertions.append(' token			******')
        assertions.append(' url			my-url')
        assertions.append(' inheritable		True')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_info_mixed(self, backend, dkcloudapi_login):
        # Config
        kitchen_name = 'my-kitchen'
        runner = CliRunner()
        mock_response = {
            "config": {
                VAULT_GLOBAL: {
                    "url": None,
                    "token": None,
                    "service": "default",
                    "prefix": None,
                    "private": None
                },
                kitchen_name: {
                    "url": "my-url",
                    "token": "my-token",
                    "service": "my-service",
                    "prefix": "my-prefix",
                    "private": "my-private",
                    "inheritable": True
                }
            }
        }

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["vault-info", "-g", "-k", kitchen_name])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Getting the vault info')
        assertions.append('---- global config ----')
        assertions.append(' DataKitchen default')
        assertions.append('---- %s config ----' % kitchen_name)
        assertions.append(' prefix			my-prefix')
        assertions.append(' private		my-private')
        assertions.append(' service		my-service')
        assertions.append(' token			******')
        assertions.append(' url			my-url')
        assertions.append(' inheritable		True')
        self.assert_response(assertions, result.output)

    # ----------------------- vault-config --------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_config_kitchen(self, backend, dkcloudapi_login):
        kitchen_name = 'my-kitchen'
        runner = CliRunner()

        mock_response = {"status": "success"}

        # Test
        with patch.object(requests, 'post',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(
                dk, [
                    "vault-config", "-k", kitchen_name, "--prefix", "my-prefix", "--private",
                    "True", "--service", "custom", "--token", "my-token", "--inheritable", "True",
                    "--url", "my-url", "--yes"
                ]
            )
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Setting the vault info')
        assertions.append('Done.')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(DKCloudAPI, 'is_user_role', return_value=True)
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_config_global(self, backend, dkcloudapi_is_user_role, dkcloudapi_login):
        runner = CliRunner()

        mock_response = {"status": "success"}

        # Test
        with patch.object(requests, 'post',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(
                dk, ["vault-config", "--token", "my-token", "--url", "my-url", "--yes"]
            )
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Setting the vault info')
        assertions.append('Done.')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(DKCloudAPI, 'is_user_role', return_value=True)
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_config_global_disable_wrong(
            self, backend, dkcloudapi_is_user_role, dkcloudapi_login
    ):
        runner = CliRunner()

        mock_response = {"status": "success"}

        # Test
        with patch.object(requests, 'post',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(
                dk, ["vault-config", "--disable", "--kitchen", "my-kitchen", "--yes"]
            )
        self.assertEqual(1, result.exit_code)
        assertions = list()
        assertions.append('Kitchen vault cannot be disabled. Check vault-delete command instead.')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(DKCloudAPI, 'is_user_role', return_value=True)
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_config_global_disable_good(
            self, backend, dkcloudapi_is_user_role, dkcloudapi_login
    ):
        runner = CliRunner()

        mock_response = {"status": "success"}

        # Test
        with patch.object(requests, 'post',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["vault-config", "--disable", "--yes"])
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Setting the vault info')
        assertions.append('Done.')
        self.assert_response(assertions, result.output)

    # ----------------------- vault-delete -----------------------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_vault_delete_kitchen(self, backend, dkcloudapi_login):
        kitchen_name = 'my-kitchen'
        runner = CliRunner()

        mock_response = {"status": "success"}

        # Test
        with patch.object(requests, 'delete',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["vault-delete", "-k", kitchen_name, "--yes"])
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Deleting the vault configuration for kitchen %s' % kitchen_name)
        assertions.append('Done.')
        self.assert_response(assertions, result.output)

    # ----------------------- secret-delete ----------------------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(DKCloudCommandRunner, 'is_vault_config_writable', return_value=True)
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_delete_kitchen(
            self, backend, dkcloudcommandrunner_is_vault_config_writable, dkcloudapi_login
    ):
        kitchen_name = 'my-kitchen'
        runner = CliRunner()

        mock_response = {"result": True}

        # Test
        with patch.object(requests, 'delete',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(
                dk, ["secret-delete", "-k", kitchen_name, "cli-unit-tests/value", "--yes"]
            )
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Deleting secret')
        assertions.append('Secret deleted.')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_delete_global(self, backend, dkcloudapi_login):
        runner = CliRunner()

        mock_response = {"result": True}

        # Test
        with patch.object(requests, 'delete',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["secret-delete", "cli-unit-tests/value", "--yes"])
        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Deleting secret')
        assertions.append('Secret deleted.')
        self.assert_response(assertions, result.output)

    # ----------------------- secret-exists ----------------------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_exists_kitchen(self, backend, dkcloudapi_login):
        kitchen_name = 'my-kitchen'
        runner = CliRunner()

        # this is the mock for secret-list
        mock_response = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["vault://global1/", "vault://global2/global2a"]
            },
            "my-kitchen": {
                "error": False,
                "list": ["vault://my-kitchen1/", "vault://my-kitchen2/my-kitchen2a"]
            }
        }

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(
                dk, ["secret-exists", "-k", kitchen_name, "my-kitchen2/my-kitchen2a"]
            )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('True (found in kitchen vault)' in result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_exists_global_false(self, backend, dkcloudapi_login):
        runner = CliRunner()

        # this is the mock for secret-list
        mock_response = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["vault://global1/", "vault://global2/global2a"]
            }
        }

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["secret-exists", "my-kitchen2/my-kitchen2a"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('False' in result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_exists_global_true(self, backend, dkcloudapi_login):
        runner = CliRunner()

        # this is the mock for secret-list
        mock_response = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["vault://global1/", "vault://global2/global2a"]
            }
        }

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["secret-exists", "global2/global2a"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('True (found in global vault)' in result.output)

    # ----------------------- secret-write -----------------------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_write_global(self, backend, dkcloudapi_login):
        runner = CliRunner()

        # this is the mock for secret-list
        mock_response_get = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["vault://global1/", "vault://global2/global2a"]
            }
        }

        mock_response_post = {"status": "success", "result": True}

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response_get)):
            with patch.object(requests, 'post',
                              return_value=MockBackendResponse(status_code=200,
                                                               response_dict=mock_response_post)):
                result = runner.invoke(
                    dk, ["secret-write", "my-write/my-write-value='hello'", "--yes"]
                )

        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Writing secret')
        assertions.append('Secret written.')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_write_vault_in_key(self, backend, dkcloudapi_login):
        runner = CliRunner()

        # this is the mock for secret-list
        mock_response_get = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["vault://global1/", "vault://global2/global2a"]
            }
        }

        mock_response_post = {"status": "success", "result": True}

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response_get)):
            with patch.object(requests, 'post',
                              return_value=MockBackendResponse(status_code=200,
                                                               response_dict=mock_response_post)):
                result = runner.invoke(
                    dk, ["secret-write", "vault://path/to/key=my-write-value", "--yes"]
                )

        self.assertEqual(1, result.exit_code, result.output)
        assertions = list()
        assertions.append('Secret key should not contain "vault://"')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudCommandRunner, 'is_vault_config_writable', return_value=True)
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_write_kitchen(
            self, backend, dkcloudapi_login, dkcloudcommandrunner_is_vault_config_writable
    ):
        kitchen_name = 'my-kitchen'
        runner = CliRunner()

        # this is the mock for secret-list
        mock_response_get = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["vault://global1/", "vault://global2/global2a"]
            },
            "my-kitchen": {
                "error": False,
                "list": ["vault://my-kitchen1/", "vault://my-kitchen2/my-kitchen2a"]
            }
        }

        mock_response_post = {"status": "success", "result": True}

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response_get)):
            with patch.object(requests, 'post',
                              return_value=MockBackendResponse(status_code=200,
                                                               response_dict=mock_response_post)):
                result = runner.invoke(
                    dk, [
                        "secret-write", "-k", kitchen_name, "my-write/my-write-value='hello'",
                        "--yes"
                    ]
                )

        self.assertEqual(0, result.exit_code, result.output)
        assertions = list()
        assertions.append('Writing secret')
        assertions.append('Secret written.')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_write_kitchen_vault_in_key(self, backend, dkcloudapi_login):
        runner = CliRunner()
        kitchen_name = 'my-kitchen'

        # this is the mock for secret-list
        mock_response_get = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["vault://global1/", "vault://global2/global2a"]
            }
        }

        mock_response_post = {"status": "success", "result": True}

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response_get)):
            with patch.object(requests, 'post',
                              return_value=MockBackendResponse(status_code=200,
                                                               response_dict=mock_response_post)):
                result = runner.invoke(
                    dk, [
                        "secret-write", "-k", kitchen_name, "vault://path/to/key=my-write-value",
                        "--yes"
                    ]
                )

        self.assertEqual(1, result.exit_code, result.output)
        assertions = list()
        assertions.append('Secret key should not contain "vault://"')
        self.assert_response(assertions, result.output)

    # ----------------------- secret-list ------------------------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_list_secrets_global(self, backend, dkcloudapi_login):
        # Config

        # Test
        runner = CliRunner()

        mock_response = {
            VAULT_GLOBAL: {
                "error":
                    False,
                "list": [
                    "cli-unit-tests/", "dkcloud/", "dockerhub/", "postgresql/", "redshift/",
                    "s3_schema/", "sftp/"
                ]
            }
        }

        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["secret-list"])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        self.assertTrue('s3_schema/' in result.output)
        self.assertTrue('cli-unit-tests/' in result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_list_secrets_global_disabled(self, backend, dkcloudapi_login):
        # Config

        # Test
        runner = CliRunner()

        mock_response = {}

        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["secret-list"])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting the list of secrets' in result.output)
        self.assertTrue('(Secrets are not available)' in result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_multi_vault_list_secrets_private(self, backend, dkcloudapi_login):
        # Config
        debug = True

        # Test
        runner = CliRunner()

        mock_response = {
            VAULT_GLOBAL: {
                "error": True,
                "error-message": "Service is private"
            },
            "my-kitchen": {
                "error": True,
                "error-message": "Service is private"
            },
        }

        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["secret-list"])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        if debug:
            print(result.output)
        assertions = list()
        assertions.append('Getting the list of secrets')
        assertions.append('Service is private')

        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_multi_vault_list_secrets_private_specific_kitchen(self, backend, dkcloudapi_login):
        # Config
        debug = True
        kitchen_name = 'my-kitchen'

        # Test
        runner = CliRunner()

        mock_response = {
            VAULT_GLOBAL: {
                "error": True,
                "error-message": "Service is private"
            },
            "my-kitchen": {
                "error": True,
                "error-message": "Service is private"
            },
        }

        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["secret-list", "-k", kitchen_name])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        if debug:
            print(result.output)
        assertions = list()
        assertions.append('Getting the list of secrets')
        assertions.append('Service is private')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_multi_vault_list_secrets_specific_kitchen(self, backend, dkcloudapi_login):
        # Config
        debug = True
        kitchen_name = 'my-kitchen'

        # Test
        runner = CliRunner()

        mock_response = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["secret1", "secret2"]
            },
            "my-kitchen": {
                "error": False,
                "list": ["my-kitchen-secret1", "my-kitchen-secret2"]
            },
        }

        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response)):
            result = runner.invoke(dk, ["secret-list", "-k", kitchen_name, "-g"])

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)
        if debug:
            print(result.output)
        assertions = list()
        assertions.append('Getting the list of secrets')
        assertions.append('---- global secrets ----')
        assertions.append(' secret1')
        assertions.append(' secret2')
        assertions.append('---- %s secrets ----' % kitchen_name)
        assertions.append(' my-kitchen-secret1')
        assertions.append(' my-kitchen-secret2')
        self.assert_response(assertions, result.output)

    # -------------------------------- invalid keys --------------------------------------------------------------------
    @patch.object(DKCloudCommandRunner, 'is_vault_config_writable', return_value=True)
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_secret_check_vault_in_path(
            self, backend, dkcloudapi_login, dkcloudcommandrunner_is_vault_config_writable
    ):
        runner = CliRunner()

        # this is the mock for secret-list
        mock_response_get = {
            VAULT_GLOBAL: {
                "error": False,
                "list": ["vault://global1/", "vault://global2/global2a"]
            },
            "my-kitchen": {
                "error": False,
                "list": ["vault://my-kitchen1/", "vault://my-kitchen2/my-kitchen2a"]
            }
        }

        mock_response_post = {"status": "success", "result": True}

        # Test
        with patch.object(requests, 'get',
                          return_value=MockBackendResponse(status_code=200,
                                                           response_dict=mock_response_get)):
            with patch.object(requests, 'post',
                              return_value=MockBackendResponse(status_code=200,
                                                               response_dict=mock_response_post)):
                result1 = runner.invoke(
                    dk, ["secret-write", "vault://path/to/key=my-write-value", "--yes"]
                )
                result2 = runner.invoke(dk, ["secret-exists", "vault://path/to/key"])
                result3 = runner.invoke(dk, ["secret-delete", "vault://path/to/key", "--yes"])
                result4 = runner.invoke(dk, ["secret-list", "vault://path/to/key"])

        for item in [result1, result2, result3, result4]:
            self.assertEqual(1, item.exit_code, item.output)
            assertions = list()
            assertions.append('Secret key should not contain "vault://"')
            self.assert_response(assertions, item.output)
