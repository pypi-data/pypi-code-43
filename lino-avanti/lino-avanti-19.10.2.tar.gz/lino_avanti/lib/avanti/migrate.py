# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Default data migrator for Lino Avanti.


"""

from django.conf import settings
from lino.api import dd, rt
from lino.utils.dpy import Migrator, override

class Migrator(Migrator):
    """The standard migrator for Lino Avanti.

    This is used because
    :class:`lino_avanti.projects.avanti.settings.Site` has
    :attr:`migration_class <lino.core.site.Site.migration_class>` set
    to ``"lino_avanti.lib.avanti.migrate.Migrator"``.

    """
    def migrate_from_0_0_1(self, globals_dict):
        # do something here
        return '0.0.2'

