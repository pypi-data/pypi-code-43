# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Extends :mod:`lino_xl.lib.contacts` for :ref:`avanti`.

.. autosummary::
   :toctree:

    models
    management.commands.garble_persons
    fixtures.std
    fixtures.demo

"""


from lino_xl.lib.contacts import Plugin


class Plugin(Plugin):
    pass
    # extends_models = ['Person']
