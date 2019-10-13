# Copyright (C) 2009-2019 Martin Slouf <martinslouf@users.sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
Application context definition.
"""

import summer

# do all the necessary imports, all that is imported bellow is deployed
# into the context, just as an example -- you can deploy anything you want
# of course
from .orm.tables import TableDefinitions
from .orm.mappings import ClassMappings
from .manager import (
    CategoryDao, CategoryManager,
    ItemDao, ItemManager,
    UserDao, UserManager,
)
from . import conf
# we mix traditional and declarative approach in SQLAlchemy entities -- we must share metadata and engine
from . import sessionprovider


class ApplicationContext(summer.Context):

    def __init__(self):
        session_provider = sessionprovider.session_provider
        ldap_connection_provider = summer.DefaultLdapConnectionProvider(
            conf.ldap_host,
            conf.ldap_port,
            conf.ldap_login,
            conf.ldap_password,
            conf.ldap_base)
        l10n = summer.Localization(conf.l10n_domain, conf.l10n_dir, conf.l10n_languages)
        summer.Context.__init__(self, session_provider, ldap_connection_provider, l10n)

    def orm_init(self):
        # you can do whatever setup you want, here you can see so-called
        # "classical" mapping, see *SqlAlchemy* for details

        # first let's complete database initialization with custom table
        # definitions and mappings
        self.session_factory.table_definitions = TableDefinitions()
        # class mappings must be defined _after_ table definitions
        self.session_factory.class_mappings = ClassMappings()

    def context_init(self):
        # deploy our dao objects
        self.category_dao = CategoryDao(self.session_factory)
        self.item_dao = ItemDao(self.session_factory)

        # let's deploy LDAP DAO's; treat them as analogy to SQL DAO's,
        # though the LDAP has no sense of SQL transaction
        self.user_dao = UserDao(self.ldap_session_factory)

        # let's define some higher level business level objects (managers)
        self.category_manager = CategoryManager(self.category_dao)
        self.item_manager = ItemManager(self.item_dao)
        self.user_manager = UserManager(self.user_dao)


# module level reference to (singleton) ApplicationContext
ctx = ApplicationContext()
