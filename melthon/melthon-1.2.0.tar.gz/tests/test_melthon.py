from click.testing import CliRunner

from melthon.cli import main


def test_main_help():
    runner = CliRunner()
    result = runner.invoke(main, [])

    # Melthon should show help page
    assert result.exit_code == 0
    print(result.stdout)
    print(result.exception)
