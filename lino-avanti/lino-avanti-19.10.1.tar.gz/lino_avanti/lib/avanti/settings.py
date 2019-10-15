# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""

.. autosummary::
   :toctree:

   doctests
   demo
   memory
   fixtures



"""

from __future__ import print_function
from __future__ import unicode_literals

from lino.projects.std.settings import *
from lino.api.ad import _


class Site(Site):

    verbose_name = "Lino Avanti!"
    # version = '2017.1.0'
    url = "http://avanti.lino-framework.org/"
    demo_fixtures = ['std',
                     'few_languages', 'compass',
                     # 'all_countries', 'all_languages',
                     'demo', 'demo2', 'checkdata']
    user_types_module = 'lino_avanti.lib.avanti.user_types'
    workflows_module = 'lino_avanti.lib.avanti.workflows'
    custom_layouts_module = 'lino_avanti.lib.avanti.layouts'
    migration_class = 'lino_avanti.lib.avanti.migrate.Migrator'

    project_model = 'avanti.Client'
    textfield_format = 'plain'
    # textfield_format = 'html'
    # use_silk_icons = False
    default_build_method = "appypdf"

    webdav_protocol = 'webdav'
    # beid_protocol = 'beid'

    auto_configure_logger_names = 'schedule atelier django lino lino_xl lino_avanti'

    def get_installed_apps(self):
        """Implements :meth:`lino.core.site.Site.get_installed_apps`.

        """
        yield super(Site, self).get_installed_apps()
        yield 'lino_avanti.lib.users'
        # yield 'lino.modlib.users'
        yield 'lino_xl.lib.countries'
        yield 'lino_avanti.lib.contacts'
        # yield 'lino_xl.lib.extensible'
        yield 'lino_avanti.lib.cal'
        yield 'lino_avanti.lib.avanti'
        yield 'lino.modlib.comments'
        yield 'lino.modlib.notify'
        yield 'lino.modlib.changes'
        yield 'lino_xl.lib.uploads'
        yield 'lino.modlib.dupable'
        # yield 'lino_xl.lib.households'
        yield 'lino_avanti.lib.households'
        # yield 'lino_welfare.modlib.households'
        # yield 'lino_xl.lib.humanlinks'
        yield 'lino_xl.lib.lists'
        # yield 'lino_xl.lib.notes'
        yield 'lino_xl.lib.beid'
        yield 'lino_xl.lib.clients'
        yield 'lino_avanti.lib.cv'
        yield 'lino_xl.lib.trends'
        yield 'lino_xl.lib.polls'

        yield 'lino_avanti.lib.courses' # pupil__gender
        # yield 'lino_xl.lib.courses'
        # yield 'lino_xl.lib.rooms'

        yield 'lino.modlib.checkdata'
        yield 'lino.modlib.export_excel'
        # yield 'lino.modlib.tinymce'
        yield 'lino.modlib.weasyprint'
        yield 'lino_xl.lib.excerpts'
        yield 'lino.modlib.dashboard'
        yield 'lino_xl.lib.appypod'
        # yield 'lino.modlib.davlink'

        # yield 'lino_xl.lib.votes'
        # yield 'lino_avanti.lib.tickets'
        # yield 'lino_xl.lib.tickets'
        # yield 'lino_xl.lib.skills'

    # def setup_plugins(self):
    #     super(Site, self).setup_plugins()
    #     self.plugins.cv.configure(
    #         person_model = 'avanti.Client')
    #     # self.plugins.humanlinks.configure(
    #     #     person_model = 'contacts.Person')
    #         # person_model = 'avanti.Client')
    #     # self.plugins.households.configure(
    #     #     person_model = 'contacts.Person')
    #         # person_model='avanti.Client')
    #     self.plugins.cal.configure(
    #         partner_model='avanti.Client')
    #     # self.plugins.skills.configure(
    #     #     end_user_model='avanti.Client')
    #     self.plugins.clients.configure(
    #         client_model='avanti.Client')
    #     self.plugins.trends.configure(
    #         subject_model='avanti.Client')
    #     # self.plugins.comments.configure(
    #     #     user_must_publish=False)

    def get_plugin_configs(self):
        for i in super(Site, self).get_plugin_configs():
            yield i
        yield ('cv', 'with_language_history', True)
        yield ('cv', 'person_model', 'avanti.Client')
        yield ('cal', 'partner_model', 'avanti.Client')
        yield ('clients', 'client_model', 'avanti.Client')
        yield ('trends', 'subject_model', 'avanti.Client')

    def setup_quicklinks(self, user, tb):
        super(Site, self).setup_quicklinks(user, tb)
        a = self.models.users.MySettings.default_action
        tb.add_instance_action(
            user, action=a, label=_("My settings"))

        # Clients = self.models.avanti.Clients
        Clients = self.models.avanti.MyClients
        tb.add_action(Clients)
        tb.add_action(
            Clients.insert_action,
            label=_("New {}").format(
                Clients.model._meta.verbose_name))
        tb.add_action(Clients, 'find_by_beid')

        # tb.add_action(self.modules.tickets.MyTickets)
        # tb.add_action(self.modules.tickets.TicketsToTriage)
        # tb.add_action(self.modules.tickets.TicketsToTalk)
        # tb.add_action(self.modules.tickets.TicketsToDo)
        # tb.add_action(self.modules.tickets.AllTickets)
        # tb.add_action(
        #     self.modules.tickets.MyTickets.insert_action,
        #     label=_("Submit a ticket"))

    def do_site_startup(self):
        super(Site, self).do_site_startup()

        from lino.utils.watch import watch_changes as wc

        wc(self.models.avanti.Client)
        # wc(self.models.contacts.Person, master_key='partner_ptr')
        # wc(self.models.contacts.Company, master_key='partner_ptr')
        # wc(self.models.pcsw.Client, master_key='partner_ptr')

        # wc(self.models.coachings.Coaching, master_key='client__partner_ptr')
        wc(self.models.cal.Guest, master_key='partner')


# the following line should not be active in a checked-in version
# DATABASES['default']['NAME'] = ':memory:'

USE_TZ = True
TIME_ZONE = 'UTC'
