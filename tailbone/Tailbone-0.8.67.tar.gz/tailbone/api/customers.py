# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tailbone Web API - Customer Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from cornice.resource import resource, view

from tailbone.api import APIMasterView


@resource(collection_path='/customers', path='/customer/{uuid}')
class CustomerView(APIMasterView):

    model_class = model.Customer

    def normalize(self, customer):
        return {
            'uuid': customer.uuid,
            '_str': six.text_type(customer),
            'id': customer.id,
            'name': customer.name,
        }

    @view(permission='customers.list')
    def collection_get(self):
        return self._collection_get()

    @view(permission='customers.create')
    def collection_post(self):
        return self._collection_post()

    @view(permission='customers.view')
    def get(self):
        return self._get()

    @view(permission='customers.edit')
    def post(self):
        return self._post()


def includeme(config):
    config.scan(__name__)
