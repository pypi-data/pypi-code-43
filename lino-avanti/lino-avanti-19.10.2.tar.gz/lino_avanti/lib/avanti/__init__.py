# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
The main plugin for Lino Avanti.

See :doc:`/specs/avanti/avanti`.

.. autosummary::
   :toctree:

    migrate
    user_types
    layouts
    choicelists

"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Master")

    needs_plugins = ['lino_xl.lib.countries']

    municipality_type = '50'

    def setup_main_menu(self, site, user_type, m):
        mg = site.plugins.contacts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('avanti.Clients')
        m.add_action('avanti.MyClients')
        # m.add_action('avanti.Translators')
        # m.add_action('courses.CourseProviders')
        # m.add_action('coachings.CoachedClients')
        # m.add_action('coachings.MyCoachings')

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.contacts
        # mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('avanti.Categories')
        m.add_action('avanti.EndingReasons')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.contacts
        # mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('avanti.AllClients')
