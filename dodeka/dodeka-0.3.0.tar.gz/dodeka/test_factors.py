"""
Copyright (c) 2019, Nils P. Müller <shimst3r@gmail.com>
All rights reserved.

This file is part of dodeka.

`test_factors.py` tests the functionality for generating the
twelve-factor app checklist as implemented in `factors.py`.

License: MIT, see https://opensource.org/licenses/MIT
"""
from dodeka import factors


def test_generate_factors():
    expected = [
        factors.Factor(title=title, short_description=short_description)
        for title, short_description in factors.FACTORS
    ]
    actual = factors.generate_factors()

    assert actual == expected


def test_template_with_empty_list():
    expected = "# Twelve-Factor App Checklist\n\n"
    actual = factors.generate_checklist(factors=[])

    assert actual == expected


def test_template_with_one_factor():
    expected = (
        "# Twelve-Factor App Checklist\n"
        "\n"
        "- [ ] I. Codebase: One codebase tracked in revision control, many deploys\n"
        "\n"
    )

    first_factor = factors.generate_factors()[0]
    actual = factors.generate_checklist(factors=[first_factor])

    assert actual == expected


def test_template_with_all_factors():
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
    actual = factors.generate_checklist(factors=factors.generate_factors())

    assert actual == expected
