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
        "  --print  Prints the twelve factors to stdout.\n"
        "  --help   Show this message and exit.\n"
    )

    runner = click.testing.CliRunner()
    actual = runner.invoke(interface.dodeka, args=["--help"]).output

    assert actual == expected


def test_dodeka_print():
    expected = (
        "# Twelve-Factor App Checklist\n"
        "\n"
        "- [ ] I. Codebase: One codebase tracked in revision control, many deploys\n"
        "\n"
        "- [ ] II. Dependencies: Explicitly declare and isolate dependencies\n"
        "\n"
        "- [ ] III. Config: Store config in the environment\n"
        "\n"
        "- [ ] IV. Backing services: Treat backing services as attached resources\n"
        "\n"
        "- [ ] V. Build, release, run: Strictly separate build and run stages\n"
        "\n"
        "- [ ] VI. Processes: Execute the app as one or more stateless processes\n"
        "\n"
        "- [ ] VII. Port binding: Export services via port binding\n"
        "\n"
        "- [ ] VIII. Concurrency: Scale out via the process model\n"
        "\n"
        "- [ ] IX. Disposability: Maximize robustness with fast startup and graceful shutdown\n"
        "\n"
        "- [ ] X. Dev/prod parity: Keep development, staging, and production as similar as possible\n"
        "\n"
        "- [ ] XI. Logs: Treat logs as event streams\n"
        "\n"
        "- [ ] XII. Admin processes: Run admin/management tasks as one-off processes\n"
        "\n"
    )

    runner = click.testing.CliRunner()
    actual = runner.invoke(interface.dodeka, args=["--print"]).output

    assert actual == expected
