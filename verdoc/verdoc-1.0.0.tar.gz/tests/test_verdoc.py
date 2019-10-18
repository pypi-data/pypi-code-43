from click.testing import CliRunner

import verdoc


def test_cli_version_option():
    result = CliRunner().invoke(verdoc.cli, ['--version'])
    assert result.exit_code == 0
    assert verdoc.__version__ in result.output
