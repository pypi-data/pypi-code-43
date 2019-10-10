import click
import pytest
from json import loads
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.authentication
def test_authentication_api(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, '--help'], terminal_width=78)
    assert not result.exception
    expected = ["Usage: main [OPTIONS] COMMAND [ARGS]...",
                "",
                "  DNA Center API wrapper.",
                "",
                "  DNACenterAPI wraps all of the individual DNA Center APIs and represents",
                "  them in a simple hierarchical structure.",
                "",
                "Options:",
                "  -v, --dna-version TEXT          Controls which version of DNA_CENTER to use.",
                "  -u, --username TEXT             HTTP Basic Auth username.",
                "  -p, --password TEXT             HTTP Basic Auth password.",
                "  -ea, --encoded_auth TEXT        HTTP Basic Auth base64 encoded string.",
                "  --base_url TEXT                 The base URL to be prefixed to the",
                "                                  individual API endpoint suffixes.",
                "  --single_request_timeout INTEGER",
                "                                  Timeout (in seconds) for RESTful HTTP",
                "                                  requests.",
                "  --wait_on_rate_limit BOOLEAN    Enables or disables automatic rate-limit",
                "                                  handling.",
                "  --verify BOOLEAN                Controls whether to verify the server's TLS",
                "                                  certificate.",
                "  -d, --debug BOOLEAN             Controls whether to log information about",
                "                                  DNA Center APIs' request and response",
                "                                  process.",
                "  -y / -n                         Prompt flag for username and password",
                "  --help                          Show this message and exit."]
    assert all([e in result.output for e in expected])
