# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""The main entry point for the :command:`getlino`  command.
"""

import click

from .configure import configure
from .startsite import startsite


@click.group()
def main():
    pass


main.add_command(configure)
main.add_command(startsite)

if __name__ == '__main__':
    main()
    # main(auto_envvar_prefix='GETLINO')
