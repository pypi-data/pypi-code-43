"""
Simple proof of concept command

"""
from click import command, option, secho, version_option


@command()
@version_option()
@option("--test/--no-test", help="A test flag", default=False)
def main(test):
    """
    CLI commands

    """
    if test:
        secho("It works!", fg="green")


def return_true():
    """
    Returns true

    """
    return True
