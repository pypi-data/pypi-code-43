# -*- coding: UTF-8 -*-
# Copyright 2013-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Extends :mod:`lino_xl.lib.cal` for :ref:`avanti`.

Adds a model AbsenceReason and a field Guest.absence_reason which
points to it.

.. autosummary::
   :toctree:

    fixtures.std
    fixtures.demo2
"""


from lino_xl.lib.cal import Plugin


class Plugin(Plugin):

    extends_models = ['Guest']

    def setup_config_menu(self, site, user_type, m):
        super(Plugin, self).setup_config_menu(site, user_type, m)
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('cal.AbsenceReasons')
    
