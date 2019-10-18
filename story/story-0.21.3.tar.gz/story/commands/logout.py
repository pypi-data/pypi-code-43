# -*- coding: utf-8 -*-
from .. import cli


@cli.cli.command()
def logout():
    """Logout from the Storyscript Cloud.
    This command will only remove your login credentials, and not your apps."""
    cli.reset()
