"""
Copyright (c) 2019, Nils P. Müller <shimst3r@gmail.com>
All rights reserved.

This file is part of dodeka.

`factors.py` implements the functionality for generating the
twelve-factor app checklist.

License: MIT, see https://opensource.org/licenses/MIT
"""

import os.path
from dataclasses import dataclass
from typing import List, Tuple

import jinja2

FACTORS = (
    ("I. Codebase", "One codebase tracked in revision control, many deploys"),
    ("II. Dependencies", "Explicitly declare and isolate dependencies"),
    ("III. Config", "Store config in the environment"),
    ("IV. Backing services", "Treat backing services as attached resources"),
    ("V. Build, release, run", "Strictly separate build and run stages"),
    ("VI. Processes", "Execute the app as one or more stateless processes"),
    ("VII. Port binding", "Export services via port binding"),
    ("VIII. Concurrency", "Scale out via the process model"),
    (
        "IX. Disposability",
        "Maximize robustness with fast startup and graceful shutdown",
    ),
    (
        "X. Dev/prod parity",
        "Keep development, staging, and production as similar as possible",
    ),
    ("XI. Logs", "Treat logs as event streams"),
    ("XII. Admin processes", "Run admin/management tasks as one-off processes"),
)


@dataclass
class Factor:
    """
    Factor implements a basic interface for easier use in templates.
    """

    title: str
    short_description: str


def generate_factors() -> List[Factor]:
    """
    generate_factors returns a list of Factors containing the twelve factors.

    >>> generate_factors()[0]
    Factor(title='I. Codebase', short_description='One codebase tracked in revision control, many deploys') 
    """
    return [
        Factor(title=title, short_description=short_description)
        for title, short_description in FACTORS
    ]


def generate_checklist(factors: List[Factor]) -> str:
    """
    generate_checklist uses the Jinja2 template engine to generate a markdown
    formatted document that renders all Factor entities provided by `factors`.
    """

    template_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=os.path.abspath(".")),
        keep_trailing_newline=True,
    )
    template = template_environment.get_template("dodeka/template.md")

    checklist = template.render(factors=factors)

    return checklist
