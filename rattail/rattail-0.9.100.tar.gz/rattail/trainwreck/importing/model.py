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
Trainwreck model importers
"""

from __future__ import unicode_literals, absolute_import

from rattail import importing
from rattail.time import make_utc
from .util import ToOrFromTrainwreck


class ToTrainwreck(ToOrFromTrainwreck, importing.ToSQLAlchemy):
    """
    Base class for all Trainwreck model importers
    """
    key = 'uuid'


class TransactionImporter(ToTrainwreck):
    """
    Transaction data importer
    """
    # NOTE: you must subclass this and define the model
    # model_class = trainwreck.Transaction

    def cache_query(self):
        query = super(TransactionImporter, self).cache_query()
        return query.filter(self.model_class.end_time >= make_utc(self.start_time))\
                    .filter(self.model_class.end_time < make_utc(self.end_time))


class TransactionItemImporter(ToTrainwreck):
    """
    Transaction item data importer
    """
    # NOTE: you must subclass this and define the model
    # model_class = trainwreck.TransactionItem

    # NOTE: subclass must also define this
    # transaction_class = trainwreck.Transaction

    def cache_query(self):
        query = super(TransactionItemImporter, self).cache_query()
        return query.join(self.transaction_class)\
                    .filter(self.transaction_class.end_time >= make_utc(self.start_time))\
                    .filter(self.transaction_class.end_time < make_utc(self.end_time))
