"""
KCUForms
=======
KCUForms is a flexible forms validation and rendering library for python web
development that inherited and learned form WTForms.

:copyright: Copyright (c) 2019 by the KCUForms team.
:license: BSD, see LICENSE.rst for details.
"""
# flake8: noqa
from kcuforms import validators
from kcuforms.fields import *
from kcuforms.form import WebForm, SearchWebForm
from kcuforms.errors import FieldError

__version__ = "0.0.7dev"
