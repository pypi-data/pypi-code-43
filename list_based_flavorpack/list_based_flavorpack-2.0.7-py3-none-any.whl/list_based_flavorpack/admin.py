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
from django.contrib import admin
from list_based_flavorpack import models


class ProcessingParametersInline(admin.TabularInline):
    model = models.ProcessingParameters
    extra = 0


class ListBasedRegionAdmin(admin.ModelAdmin):
    list_display = (
        'readable_name',
        'machine_name',
        'pool',
        'file_id'
    )
    inlines = [
        ProcessingParametersInline
    ]
    ordering = [
        'readable_name'
    ]


def register_to_site(admin_site):
    admin_site.register(models.ListBasedRegion, ListBasedRegionAdmin)
