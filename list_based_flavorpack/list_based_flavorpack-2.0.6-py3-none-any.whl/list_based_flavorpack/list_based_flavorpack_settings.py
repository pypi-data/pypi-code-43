'''
    Copyright 2018 SerialLab, CORP

    This file is part of ListBasedFlavorpack.

    ListBasedFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ListBasedFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with ListBasedFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''

from django.conf import settings


GENERATOR_PREPROCESSING_RULES = getattr(
    settings,
    'GENERATOR_PREPROCESSING_RULES',
    {
        'list_based_flavorpack.generators.list_based.ListBasedGenerator': [
            'serialbox.rules.limits.ActiveRule',
            'list_based_flavorpack.generators.list_based.ListBasedPreprocessRule',
            'serialbox.rules.limits.RequestThresholdLimitRule',
        ]
    })

GENERATOR_POSTPROCESSING_RULES = getattr(
    settings,
    'GENERATOR_POSTPROCESSING_RULES',
    {'list_based_flavorpack.generators.list_based.ListBasedGenerator': [
            'serialbox.rules.limits.ActiveRule',
            'list_based_flavorpack.generators.list_based.ListBasedPostprocessRule',
            'serialbox.rules.limits.RequestThresholdLimitRule',
        ]})
