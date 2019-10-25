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
Tailbone Web API - Product Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from cornice.resource import resource, view

from tailbone.api import APIMasterView


@resource(collection_path='/products', path='/product/{uuid}')
class ProductView(APIMasterView):

    model_class = model.Product

    def normalize(self, product):
        cost = product.cost
        return {
            'uuid': product.uuid,
            '_str': six.text_type(product),
            'upc': six.text_type(product.upc),
            'scancode': product.scancode,
            'item_id': product.item_id,
            'item_type': product.item_type,
            'description': product.description,
            'status_code': product.status_code,
            'default_unit_cost': cost.unit_cost if cost else None,
            'default_unit_cost_display': "${:0.2f}".format(cost.unit_cost) if cost and cost.unit_cost is not None else None,
        }

    @view(permission='products.list')
    def collection_get(self):
        return self._collection_get()

    @view(permission='products.create')
    def collection_post(self):
        return self._collection_post()

    @view(permission='products.view')
    def get(self):
        return self._get()

    @view(permission='products.edit')
    def post(self):
        return self._post()


def includeme(config):
    config.scan(__name__)
