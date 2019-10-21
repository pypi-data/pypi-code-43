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

import os.path
import summer

# create ConfigValue instance
config_value = summer.ConfigValue()

project_name = "tmplproject"
project_topdir = os.path.abspath(os.path.join(__file__, "..", ".."))

# allow override by setting SQLALCHEMY_URI environment variable (depends on your OS)
sqlalchemy_uri = config_value("SQLALCHEMY_URI", "sqlite:///:memory:")
sqlalchemy_autocommit = config_value("SQLALCHEMY_AUTOCOMMIT", False)

l10n_domain = project_name
l10n_dir = "%s/l10n" % (project_topdir,)
l10n_languages = ("cs", "en")

ldap_host = config_value("LDAP_HOST", "localhost")
ldap_port = config_value("LDAP_PORT", 389)
ldap_base = "dc=sample,dc=local"
ldap_login = config_value("LDAP_LOGIN", "cn=admin,dc=sample,dc=local")
ldap_password = config_value("LDAP_PASSWORD", "secret")
