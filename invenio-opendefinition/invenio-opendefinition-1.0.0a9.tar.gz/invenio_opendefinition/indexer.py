# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record modification prior to indexing."""

from __future__ import absolute_import, print_function

from elasticsearch import VERSION as ES_VERSION


def indexer_receiver(sender, json=None, record=None, index=None,
                     **dummy_kwargs):
    """Connect to before_record_index signal to transform record for ES."""
    if index.startswith('licenses-'):
        if ES_VERSION[0] == 2:
            # Generate suggest field
            json['suggest'] = {
                'input': [json['id'], json['title']],
                'output': json['title'],
                'payload': {
                    'id': json['id'],
                    'title': json['title']
                },
            }
        elif ES_VERSION[0] > 2:
            json['suggest'] = {
                'input': [json['id'], json['title']]}
