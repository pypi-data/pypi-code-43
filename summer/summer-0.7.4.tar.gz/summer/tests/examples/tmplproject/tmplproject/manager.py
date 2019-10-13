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

import ldap3
import summer

from .model import Category, Item, User


#
# category #
#


class CategoryDao(summer.CodeEntityDao):
    def __init__(self, session_factory: summer.SessionFactory):
        summer.CodeEntityDao.__init__(self, session_factory, Category)

    def sample_method1(self) -> list:
        return [i for i in self.query.all()]

    def sample_method2(self) -> list:
        return [i for i in self.query.all()]


class CategoryManager(object):
    def __init__(self, category_dao: CategoryDao):
        self.category_dao = category_dao

    @summer.transactional
    def sample_method3(self) -> list:
        return self.category_dao.sample_method1() + self.category_dao.sample_method2()


#
# item #
#


class ItemDao(summer.CodeEntityDao):
    def __init__(self, session_factory: summer.SessionFactory):
        summer.CodeEntityDao.__init__(self, session_factory, Item)

    def sample_method1(self) -> list:
        return [i for i in self.query.all()]

    def sample_method2(self) -> list:
        return [i for i in self.query.all()]


class ItemManager(object):
    def __init__(self, item_dao: ItemDao):
        self.item_dao = item_dao

    @summer.transactional
    def sample_method3(self) -> list:
        return self.item_dao.sample_method1() + self.item_dao.sample_method2()


#
# user #
#


class UserDao(summer.LdapEntityDao):
    def __init__(self, ldap_session_factory: summer.LdapSessionFactory):
        summer.LdapEntityDao.__init__(self, ldap_session_factory, User)

    def find(self) -> list:
        """Gets all users."""
        session = self.session
        base = "ou=users,%s" % (self.base,)
        result = session.search(search_base=base,
                                search_filter="(cn=*)",
                                search_scope=ldap3.SUBTREE,
                                attributes=["cn", "userPassword"])
        users = list()
        if result:
            for entry in session.response:
                attrs = entry["attributes"]
                login = attrs["cn"][0]
                crypt = attrs["userPassword"][0]
                user = User(login, crypt)
                users.append(user)
        return users


class UserManager(object):
    def __init__(self, user_dao: UserDao):
        self.user_dao = user_dao

    @summer.ldapaop
    def find(self) -> list:
        return self.user_dao.find()
