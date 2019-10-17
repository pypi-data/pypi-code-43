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
Contains domain classes mapped to database & ldap.
"""

from sqlalchemy import Column, Integer, Unicode

import summer

from . import sessionprovider

Base = sessionprovider.session_provider.declarative_base_class


class Category(summer.CodeEntity):
    """Database entity."""

    def __init__(self):
        super().__init__()
        self.order = 0


class Item(summer.CodeEntity):
    """Database entity."""

    def __init__(self):
        super().__init__()
        self.value = 0


class DeclarativeFooEntity(Base):
    """Database entity mapped with declarative approach.  Mixing traditional and declarative approaches is possible,
    if there is single :py:class:`summer.sf.SessionProvider` class.
    """
    __tablename__ = 'declarative_foo_entity'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256))


class User(summer.Domain):
    """LDAP entity."""

    def __init__(self, login, crypt):
        super().__init__()
        self.login = login
        self.passwd = crypt
