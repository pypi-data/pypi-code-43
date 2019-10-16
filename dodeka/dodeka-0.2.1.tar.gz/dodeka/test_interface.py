"""
Copyright (c) 2019, Nils P. Müller <shimst3r@gmail.com>
All rights reserved.

This file is part of dodeka.

`test_interface.py` tests the command line interface as
implemented in `interface.py`.

License: MIT, see https://opensource.org/licenses/MIT
"""

import click.testing

from dodeka import interface


def test_dodeka_help():
    expected = (
        "Usage: dodeka [OPTIONS]\n"
        "\n"
        "  dodeka is a command line tool for tracking the degree of fulfilment of The\n"
        "  Twelve-Factor App methodology. Use it in your projects to test whether they\n"
        "  conform to the principles for developing solid web apps that originated\n"
        "  within Heroku.\n"
        "\n"
        "Options:\n"
        "  --help  Show this message and exit.\n"
    )

    runner = click.testing.CliRunner()
    actual = runner.invoke(interface.dodeka, args=["--help"]).output

    assert actual == expected
