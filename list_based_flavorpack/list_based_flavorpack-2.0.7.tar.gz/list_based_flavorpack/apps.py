'''
    Copyright 2018 SerialLab, CORP

    This file is part of ListBasedFlavorpack.

    RandomFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RandomFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RandomFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''

from serialbox.flavor_packs import FlavorPackApp


class ListBasedFlavorpackConfig(FlavorPackApp):
    # The flavorpack app is a django AppConfig instance
    # with a meta-class that does some auto-registration for flavorpacks...
    # for more on AppConfigs see the Django documentation.
    name = 'list_based_flavorpack'
    verbose_name = 'List Based Number Regions'

    @property
    def pool_slug_fields(self):
        return {
            'listbasedregion_set':
            'list_based_flavorpack.api.serializers.listbasedregion_set'
        }

    # Each flavorpack must supply hyperlink fields for it's serializer fields
    @property
    def pool_hyperlink_fields(self):
        return {
            'listbasedregion_set':
            'list_based_flavorpack.api.serializers.listbasedregion_set'
        }
    # Each flavorpack must supply number generators for it's regions

    @property
    def generators(self):
        # here we define the model and generator that
        # is responsible for creating words for the API and maintaining
        # the appropriate state in the database
        return {
            'list_based_flavorpack.models.ListBasedRegion':
            'list_based_flavorpack.generators.list_based.ListBasedGenerator'
        }

    @property
    def api_urls(self):
        # this is the name of the URL config that returns word regions,
        # returning it makes it visible on the self-documenting
        # django rest framework HTML interface at the Root Api page...
        return ['list-based-region-list', 'list-based-region-create']
