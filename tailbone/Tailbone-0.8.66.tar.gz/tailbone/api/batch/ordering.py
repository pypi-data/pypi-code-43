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
Tailbone Web API - Ordering Batches
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model
from rattail.time import localtime

from cornice.resource import resource, view

from tailbone.api import APIMasterView


@resource(collection_path='/ordering-batches', path='/ordering-batch/{uuid}')
class OrderingBatchView(APIMasterView):

    model_class = model.PurchaseBatch

    def base_query(self):
        return self.Session.query(model.PurchaseBatch)\
                           .filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING)

    def pretty_datetime(self, dt):
        if not dt:
            return ""
        return dt.strftime('%Y-%m-%d @ %I:%M %p')

    def normalize(self, batch):

        created = batch.created
        created = localtime(self.rattail_config, created, from_utc=True)
        created = self.pretty_datetime(created)

        executed = batch.executed
        if executed:
            executed = localtime(self.rattail_config, executed, from_utc=True)
            executed = self.pretty_datetime(executed)

        return {
            'uuid': batch.uuid,
            '_str': six.text_type(batch),
            'id': batch.id,
            'id_str': batch.id_str,
            'description': batch.description,
            'vendor_uuid': batch.vendor.uuid,
            'vendor_name': batch.vendor.name,
            'po_total_calculated': batch.po_total_calculated,
            'po_total_calculated_display': "${:0.2f}".format(batch.po_total_calculated) if batch.po_total_calculated is not None else None,
            'date_ordered': six.text_type(batch.date_ordered or ''),
            'created': created,
            'created_by_uuid': batch.created_by.uuid,
            'created_by_display': six.text_type(batch.created_by),
            'executed': executed,
            'executed_by_uuid': batch.executed_by_uuid,
            'executed_by_display': six.text_type(batch.executed_by or ''),
        }

    @view(permission='ordering.list')
    def collection_get(self):
        return self._collection_get()

    # @view(permission='ordering.create')
    # def collection_post(self):
    #     return self._collection_post()

    @view(permission='ordering.view')
    def get(self):
        return self._get()

    # @view(permission='ordering.edit')
    # def post(self):
    #     return self._post()


def includeme(config):
    config.scan(__name__)
