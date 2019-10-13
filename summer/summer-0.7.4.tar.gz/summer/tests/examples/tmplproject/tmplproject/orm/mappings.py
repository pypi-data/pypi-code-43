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
Contains ORM mappings.
"""

import sqlalchemy.orm
import summer

from .tables import TableDefinitions
from ..model import Category, Item


class ClassMappings(summer.AbstractClassMappings):
    def __init__(self):
        summer.AbstractClassMappings.__init__(self)
        self.category = None
        self.item = None

    def create_mappings(self, session_factory: summer.SessionFactory):
        tables = session_factory.table_definitions
        assert isinstance(tables, TableDefinitions)

        self.category = sqlalchemy.orm.mapper(
            Category, tables.category,
            # db column has different name
            properties={"order": tables.category.c.orderx}
        )

        self.item = sqlalchemy.orm.mapper(
            Item, tables.item,
            properties={
                "items":
                    sqlalchemy.orm.relation(Category, secondary=tables.category_x_item)
            }
        )
