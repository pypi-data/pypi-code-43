"""A sample CLI."""

import click
import log

from . import commands
from .utils import get_browser


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    log.init()
    log.silence("datafiles", "selenium", "urllib3")


@main.command(help="Verify browser automation is working.")
@click.option(
    "--username",
    envvar="TWITTER_USERNAME",
    prompt="Twitter username",
    help="Username of Twitter account to automate.",
)
@click.option("--browser", help="Browser to use for automation.")
@click.option("--debug", is_flag=True, help="Start debugger on exceptions.")
def check(username: str, browser: str, debug: bool):
    with get_browser(browser) as b:
        try:
            commands.check(b, username, display=click.echo)
        except Exception as e:  # pylint: disable=broad-except
            if debug:
                import ipdb  # pylint: disable=import-outside-toplevel

                log.exception(e)

                ipdb.post_mortem()
            else:
                raise e from None


@main.command(help="Crawl for bots starting from seed account.")
@click.argument("username", envvar="TWITTER_SEED_USERNAME")
@click.option("--browser", help="Browser to use for automation.")
def crawl(username: str, browser: str):
    with get_browser(browser) as b:
        commands.crawl(b, username)


@main.command(help="Verify browser automation is working.")
@click.option(
    "--username",
    envvar="TWITTER_USERNAME",
    prompt="Twitter username",
    help="Username of Twitter account to automate.",
)
@click.option(
    "--password",
    envvar="TWITTER_PASSWORD",
    prompt="Twitter password",
    hide_input=True,
    help="Password of twitter account to automate.",
)
@click.option("--browser", help="Browser to use for automation.")
def block(username: str, password: str, browser: str):
    with get_browser(browser) as b:
        commands.block(b, username, password, display=click.echo)


if __name__ == "__main__":  # pragma: no cover
    main()
